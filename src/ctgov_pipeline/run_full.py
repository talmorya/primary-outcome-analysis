"""Run full extraction for behavioral interventional chronic pain trials."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config_loader import PROJECT_ROOT, load_yaml
from .fetch import get_api_version, save_json, search_all_studies
from .parse import build_tables, parse_study_record

CONDITIONS = {
    "chronic_back_pain": "chronic back pain",
    "fibromyalgia": "fibromyalgia",
    "migraine": "migraine",
}

ADVANCED_FILTER = "AREA[StudyType]INTERVENTIONAL AND AREA[InterventionType]BEHAVIORAL"
QUERY_SOURCE = (
    "StudyType=INTERVENTIONAL AND InterventionType=BEHAVIORAL "
    "AND condition IN (chronic back pain, fibromyalgia, migraine)"
)


def _fetch_all_pages(condition_key: str, condition_term: str) -> tuple[list[dict], int]:
    params = {
        "query.cond": condition_term,
        "filter.advanced": ADVANCED_FILTER,
        "pageSize": 1000,
        "countTotal": "true",
        "format": "json",
    }
    import requests

    response = requests.get(
        "https://clinicaltrials.gov/api/v2/studies",
        params={**params, "pageSize": 1},
        timeout=60,
    )
    response.raise_for_status()
    total = response.json().get("totalCount", 0)

    records = search_all_studies(params, max_pages=None, pause_seconds=0.25)
    return records, total


def _save_search_pages(
    records: list[dict],
    output_dir: Path,
    condition_key: str,
    *,
    page_size: int = 1000,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for page_idx in range(0, len(records), page_size):
        chunk = records[page_idx : page_idx + page_size]
        page_num = page_idx // page_size + 1
        save_json({"studies": chunk}, output_dir / f"{condition_key}_page_{page_num:03d}.json")


def _save_study_records(records: list[dict], output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    nct_ids: list[str] = []
    for record in records:
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        save_json(record, output_dir / f"{nct_id}.json")
        nct_ids.append(nct_id)
    return nct_ids


def _filter_cohort(records: list[dict]) -> tuple[list[dict], dict[str, int]]:
    condition_config = load_yaml("condition_patterns.yaml")
    intervention_config = load_yaml("intervention_taxonomy.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    kept: list[dict] = []
    stats = {
        "deduplicated_api_records": len(records),
        "excluded_no_condition_match": 0,
        "excluded_non_interventional": 0,
    }

    for record in records:
        study_row, _ = parse_study_record(
            record,
            condition_config=condition_config,
            intervention_config=intervention_config,
            outcome_lexicon=outcome_lexicon,
            extraction_run_id="filter",
            api_version=None,
            data_timestamp=None,
        )
        if study_row["study_type"] != "INTERVENTIONAL":
            stats["excluded_non_interventional"] += 1
            continue
        if not study_row["condition_matched"]:
            stats["excluded_no_condition_match"] += 1
            continue
        kept.append(record)

    stats["cohort_studies"] = len(kept)
    return kept, stats


def run_full() -> Path:
    run_id = datetime.now(timezone.utc).strftime("full_%Y%m%d_%H%M%S")
    extraction_date = datetime.now(timezone.utc).isoformat()

    raw_dir = PROJECT_ROOT / "data" / "raw" / "full" / run_id
    processed_dir = PROJECT_ROOT / "data" / "processed" / "full" / run_id
    processed_dir.mkdir(parents=True, exist_ok=True)

    api_info = get_api_version()
    condition_config = load_yaml("condition_patterns.yaml")
    intervention_config = load_yaml("intervention_taxonomy.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    condition_api_counts: dict[str, int] = {}
    all_records: list[dict] = []

    for key, term in CONDITIONS.items():
        records, total = _fetch_all_pages(key, term)
        condition_api_counts[key] = total
        _save_search_pages(records, raw_dir / "search_pages", key)
        all_records.extend(records)

    deduped: dict[str, dict] = {}
    for record in all_records:
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        deduped[nct_id] = record

    deduplicated = list(deduped.values())
    cohort_records, filter_stats = _filter_cohort(deduplicated)
    nct_ids = _save_study_records(cohort_records, raw_dir / "studies")

    studies_df, outcomes_df = build_tables(
        cohort_records,
        condition_config=condition_config,
        intervention_config=intervention_config,
        outcome_lexicon=outcome_lexicon,
        extraction_run_id=run_id,
        api_version=api_info.get("apiVersion"),
        data_timestamp=api_info.get("dataTimestamp"),
        query_source=QUERY_SOURCE,
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

    manifest = {
        "run_id": run_id,
        "extraction_date": extraction_date,
        "api_version": api_info.get("apiVersion"),
        "data_timestamp": api_info.get("dataTimestamp"),
        "retrieval_criteria": {
            "study_type": "INTERVENTIONAL",
            "intervention_type": "BEHAVIORAL",
            "conditions": list(CONDITIONS.values()),
            "ibs_excluded": True,
            "filter_advanced": ADVANCED_FILTER,
        },
        "condition_api_total_counts": condition_api_counts,
        "deduplicated_unique_nct_ids": len(deduplicated),
        "filter_stats": filter_stats,
        "cohort_nct_ids": nct_ids,
        "study_count": len(studies_df),
        "primary_outcome_count": len(outcomes_df),
        "notes": {
            "outcome_purpose": (
                "Exploratory heuristic only; not used to exclude or filter outcomes."
            ),
            "local_condition_validation": (
                "Studies must match chronic back pain, fibromyalgia, or migraine via local rules."
            ),
        },
    }
    save_json(manifest, processed_dir / "extraction_manifest.json")
    save_json(manifest, raw_dir / "extraction_manifest.json")

    print(f"Full extraction complete: {processed_dir}")
    print(f"Studies: {len(studies_df)}, primary outcomes: {len(outcomes_df)}")
    return processed_dir


if __name__ == "__main__":
    run_full()
