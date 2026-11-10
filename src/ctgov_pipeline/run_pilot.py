"""Run revised pilot extraction for behavioral interventional chronic pain trials."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config_loader import PROJECT_ROOT, load_yaml
from .extract_outcome_features import extract_instruments
from .fetch import fetch_and_save_studies, get_api_version, save_json
from .parse import build_tables, parse_study_record

CONDITIONS = {
    "back_pain": "back pain",
    "fibromyalgia": "fibromyalgia",
    "migraine": "migraine",
}

ADVANCED_FILTER = "AREA[StudyType]INTERVENTIONAL AND AREA[InterventionType]BEHAVIORAL"

PILOT_ANCHORS = [
    "NCT05658185",
    "NCT01666639",
    "NCT06406699",
    "NCT03319355",
    "NCT01345344",
]


def _fetch_condition_pool(condition_key: str, condition_term: str) -> tuple[list[dict], int]:
    params = {
        "query.cond": condition_term,
        "filter.advanced": ADVANCED_FILTER,
        "pageSize": 100,
        "countTotal": "true",
        "format": "json",
    }
    import requests

    response = requests.get(
        "https://clinicaltrials.gov/api/v2/studies",
        params=params,
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    records = payload.get("studies", [])
    total = payload.get("totalCount", len(records))
    return records, total


def _select_pilot_ids(records: list[dict], target_n: int = 40) -> list[str]:
    condition_config = load_yaml("condition_patterns.yaml")
    intervention_config = load_yaml("intervention_taxonomy.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    parsed: list[dict] = []
    for record in records:
        study_row, outcomes = parse_study_record(
            record,
            condition_config=condition_config,
            intervention_config=intervention_config,
            outcome_lexicon=outcome_lexicon,
            extraction_run_id="selection",
            api_version=None,
            data_timestamp=None,
        )
        if study_row["study_type"] != "INTERVENTIONAL":
            continue
        if not study_row["condition_matched"]:
            continue
        parsed.append(
            {
                "nct_id": study_row["nct_id"],
                "condition": (study_row["condition_matched"] or "").split(" | ")[0],
                "component": (study_row["behavioral_component"] or "none").split(" | ")[0],
                "n_outcomes": len(outcomes),
                "is_multimodal": study_row["is_multimodal"],
                "non_psych": study_row["non_psychological_behavioral_flag"],
                "review_flag": study_row["intervention_review_flag"],
            }
        )

    selected: list[str] = []
    seen: set[str] = set()
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    multimodal: list[str] = []
    non_psych: list[str] = []
    multi_primary: list[str] = []

    for item in parsed:
        buckets[(item["condition"], item["component"])].append(item["nct_id"])
        if item["is_multimodal"]:
            multimodal.append(item["nct_id"])
        if item["non_psych"]:
            non_psych.append(item["nct_id"])
        if item["n_outcomes"] >= 3:
            multi_primary.append(item["nct_id"])

    for nct_id in PILOT_ANCHORS:
        if nct_id not in seen:
            selected.append(nct_id)
            seen.add(nct_id)

    for key in sorted(buckets):
        for nct_id in buckets[key][:2]:
            if nct_id not in seen and len(selected) < target_n:
                selected.append(nct_id)
                seen.add(nct_id)

    for pool in (multimodal, non_psych, multi_primary):
        for nct_id in pool:
            if nct_id not in seen and len(selected) < target_n:
                selected.append(nct_id)
                seen.add(nct_id)

    for item in parsed:
        if item["nct_id"] not in seen and len(selected) < target_n:
            selected.append(item["nct_id"])
            seen.add(item["nct_id"])

    return selected


def _count_old_false_positives(lexicon: dict) -> tuple[int, list[str]]:
    old_path = PROJECT_ROOT / "data" / "processed" / "pilot" / "pilot_20260818_141318" / "primary_outcomes.csv"
    if not old_path.exists():
        return 0, []
    outcomes = pd.read_csv(old_path)
    cases: list[str] = []
    for _, row in outcomes.iterrows():
        text = " ".join(
            str(row[col])
            for col in [
                "primary_outcome_measure",
                "primary_outcome_description",
                "primary_outcome_time_frame",
            ]
            if pd.notna(row[col]) and str(row[col]) != "nan"
        )
        old_detected = str(row.get("instruments_detected", ""))
        new_detected = extract_instruments(text, lexicon)
        if "Insomnia Severity Index" in old_detected and "Insomnia Severity Index" not in new_detected:
            if "insomnia" not in text.lower() and not __import__("re").search(r"\bisi\b", text, __import__("re").I):
                cases.append(str(row["outcome_id"]))
    return len(cases), cases


def run_pilot(target_n: int = 40) -> Path:
    run_id = datetime.now(timezone.utc).strftime("pilot_%Y%m%d_%H%M%S")
    raw_dir = PROJECT_ROOT / "data" / "raw" / "pilot" / run_id
    processed_dir = PROJECT_ROOT / "data" / "processed" / "pilot" / run_id
    reports_dir = PROJECT_ROOT / "reports" / "pilot" / run_id
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    api_info = get_api_version()
    condition_config = load_yaml("condition_patterns.yaml")
    intervention_config = load_yaml("intervention_taxonomy.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    pool_records: list[dict] = []
    condition_counts: dict[str, int] = {}
    for key, term in CONDITIONS.items():
        records, total = _fetch_condition_pool(key, term)
        condition_counts[key] = total
        save_json(records, raw_dir / "search_pages" / f"{key}.json")
        pool_records.extend(records)

    deduped: dict[str, dict] = {}
    for record in pool_records:
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        deduped[nct_id] = record
    pool = list(deduped.values())

    selected = _select_pilot_ids(pool, target_n=target_n)
    manifest = fetch_and_save_studies(selected, raw_dir / "studies")

    records = []
    for nct_id in manifest["saved"]:
        with (raw_dir / "studies" / f"{nct_id}.json").open(encoding="utf-8") as handle:
            records.append(json.load(handle))

    studies_df, outcomes_df = build_tables(
        records,
        condition_config=condition_config,
        intervention_config=intervention_config,
        outcome_lexicon=outcome_lexicon,
        extraction_run_id=run_id,
        api_version=api_info.get("apiVersion"),
        data_timestamp=api_info.get("dataTimestamp"),
        query_source="INTERVENTIONAL AND BEHAVIORAL AND target condition",
    )

    studies_df.to_csv(processed_dir / "studies.csv", index=False)
    outcomes_df.to_csv(processed_dir / "primary_outcomes.csv", index=False)

    pd.DataFrame(
        columns=[
            "outcome_id",
            "nct_id",
            "outcome_category",
            "instrument_name",
            "instrument_subscale",
            "annotation_method",
            "annotator_id",
            "annotation_confidence",
            "annotation_notes",
            "annotation_version",
            "annotated_at",
        ]
    ).to_csv(processed_dir / "outcome_annotations_template.csv", index=False)

    old_fp_count, old_fp_cases = _count_old_false_positives(outcome_lexicon)
    new_fp_cases: list[str] = []
    for _, row in outcomes_df.iterrows():
        text = " ".join(
            str(row[col])
            for col in [
                "primary_outcome_measure",
                "primary_outcome_description",
                "primary_outcome_time_frame",
            ]
            if pd.notna(row[col])
        )
        detected = extract_instruments(text, outcome_lexicon)
        if "Insomnia Severity Index" in detected and "insomnia" not in text.lower():
            import re

            if not re.search(r"\bisi\b", text, re.I):
                new_fp_cases.append(str(row["outcome_id"]))

    multimodal = studies_df[studies_df["is_multimodal"] == True]
    non_psych = studies_df[studies_df["non_psychological_behavioral_flag"] == True]

    lines = [
        f"# Revised pilot report ({run_id})",
        "",
        "## Retrieval criteria",
        "- StudyType = INTERVENTIONAL",
        "- InterventionType = BEHAVIORAL",
        "- Conditions: chronic back pain, fibromyalgia, migraine (IBS excluded)",
        "",
        "## Studies retrieved by condition (API totalCount, deduplicated pool may overlap)",
        "",
    ]
    for key, total in condition_counts.items():
        lines.append(f"- {key}: {total}")
    lines.extend(
        [
            f"- Unique studies in 1-page pool per condition: {len(pool)}",
            f"- Pilot sample extracted: {len(studies_df)}",
            f"- Primary outcome rows: {len(outcomes_df)}",
            "",
            "## Behavioral intervention counts",
            f"- Studies with psychological component identified: {(studies_df['behavioral_component'].notna() & (studies_df['behavioral_component'] != '')).sum()}",
            f"- Flagged potentially non-psychological behavioral: {len(non_psych)} ({len(non_psych)/len(studies_df)*100:.1f}%)",
            "",
            "## Multimodal studies",
            f"- Count: {len(multimodal)} ({len(multimodal)/len(studies_df)*100:.1f}%)",
            "",
        ]
    )
    if not multimodal.empty:
        lines.append("### Examples")
        lines.append("")
        for _, row in multimodal.head(8).iterrows():
            lines.append(
                f"- **{row['nct_id']}**: component={row['behavioral_component']}; "
                f"other_type={row['other_modality_type']}; other_name={row['other_modality_name']}"
            )

    lines.extend(
        [
            "",
            "## Instrument false positives (ISI substring issue)",
            f"- Known false-positive cases in old pilot fixed: {old_fp_count}",
            "",
            "Old false-positive outcome_ids:",
            "",
        ]
    )
    lines.extend(f"- {case}" for case in old_fp_cases)
    lines.extend(
        [
            "",
            f"- Remaining ISI false positives in revised pilot: {len(new_fp_cases)}",
            "",
            "## outcome_purpose distribution",
            "",
            outcomes_df["outcome_purpose"].value_counts().to_string(),
            "",
            "## Multiple-primary-outcome examples",
            "",
        ]
    )
    multi = outcomes_df.groupby("nct_id").agg(
        n=("outcome_id", "count"),
        title=("brief_title", "first"),
        purposes=("outcome_purpose", lambda s: ", ".join(sorted(set(s)))),
    )
    multi = multi[multi["n"] >= 3].sort_values("n", ascending=False).head(5)
    for nct_id, row in multi.iterrows():
        lines.append(f"### {nct_id} ({row['n']} primaries)")
        lines.append(f"- {row['title']}")
        lines.append(f"- Purposes: {row['purposes']}")
        sub = outcomes_df[outcomes_df["nct_id"] == nct_id][
            ["primary_outcome_index", "primary_outcome_measure", "outcome_purpose", "instruments_detected"]
        ]
        for _, po in sub.iterrows():
            lines.append(
                f"  - PO{po['primary_outcome_index']}: {po['primary_outcome_measure'][:100]} "
                f"[{po['outcome_purpose']}] instruments={po['instruments_detected']}"
            )
        lines.append("")

    lines.extend(["", "## NCT05658185 preserved outcomes", ""])
    anchor = outcomes_df[outcomes_df["nct_id"] == "NCT05658185"]
    for _, row in anchor.iterrows():
        lines.extend(
            [
                f"### {row['outcome_id']}",
                f"- Measure: {row['primary_outcome_measure']}",
                f"- Description: {row['primary_outcome_description']}",
                f"- Time frame: {row['primary_outcome_time_frame']}",
                f"- Instruments: {row['instruments_detected']}",
                f"- Acronyms: {row['acronyms_detected']}",
                f"- Purpose: {row['outcome_purpose']}",
                "",
            ]
        )

    (reports_dir / "revised_pilot_report.md").write_text("\n".join(lines), encoding="utf-8")
    save_json(
        {
            "run_id": run_id,
            "condition_counts": condition_counts,
            "selected_nct_ids": selected,
            "old_isi_false_positives_fixed": old_fp_count,
            "new_isi_false_positives": new_fp_cases,
        },
        processed_dir / "run_metadata.json",
    )
    print(f"Revised pilot complete: {processed_dir}")
    return processed_dir


if __name__ == "__main__":
    run_pilot()
