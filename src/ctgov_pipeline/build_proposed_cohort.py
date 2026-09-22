"""Build proposed cohort classification layer for QC review (does not modify full extraction)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .classify_interventions import classify_interventions
from .condition_eligibility import evaluate_condition_eligibility
from .config_loader import PROJECT_ROOT, load_yaml
from .parse import parse_study_record
from .rq_eligibility import evaluate_rq_eligibility

EXISTING_RUN_ID = "full_20260823_201251"

# Finalized headache expansion (22 studies; NCT05689944 excluded per QC).
HEADACHE_EXPANSION_NCTS = [
    "NCT01664585",
    "NCT01155557",
    "NCT01213056",
    "NCT07240532",
    "NCT01525303",
    "NCT06041997",
    "NCT00181064",
    "NCT00457496",
    "NCT06631222",
    "NCT02264340",
    "NCT02460003",
    "NCT00897780",
    "NCT04867967",
    "NCT06822673",
    "NCT00956969",
    "NCT01347684",
    "NCT01488825",
    "NCT03166358",
    "NCT00389038",
    "NCT02475005",
    "NCT00267618",
    "NCT03308630",
]

QUERY_SOURCE = (
    "StudyType=INTERVENTIONAL AND InterventionType=BEHAVIORAL "
    "AND condition IN (chronic back pain, fibromyalgia, migraine, headache-proposed)"
)


def _split_pipe(value: str | None) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split("|") if part.strip()]


def _join_pipe(values: list[str] | None) -> str | None:
    if not values:
        return None
    return " | ".join(values)


def _refresh_intervention_fields(study: dict) -> dict:
    """Re-apply intervention taxonomy without modifying the production studies.csv."""
    raw = study.get("interventions_raw")
    if not raw or (isinstance(raw, float) and pd.isna(raw)):
        return study

    interventions = json.loads(raw) if isinstance(raw, str) else raw
    intervention = classify_interventions(interventions, load_yaml("intervention_taxonomy.yaml"))
    refreshed = dict(study)
    refreshed["behavioral_component"] = _join_pipe(intervention.behavioral_component)
    refreshed["intervention_classification_rule"] = _join_pipe(intervention.classification_rules)
    refreshed["intervention_review_flag"] = intervention.review_flag
    refreshed["is_multimodal"] = intervention.is_multimodal
    refreshed["other_modality_present"] = intervention.other_modality_present
    refreshed["other_modality_type"] = intervention.other_modality_type
    refreshed["other_modality_name"] = intervention.other_modality_name
    refreshed["non_psychological_behavioral_flag"] = intervention.non_psychological_behavioral_flag
    refreshed["non_psychological_behavioral_type"] = intervention.non_psychological_behavioral_type
    refreshed["non_psychological_behavioral_name"] = intervention.non_psychological_behavioral_name
    return refreshed


def _row_from_study_dict(study: dict, *, source: str) -> dict:
    study = _refresh_intervention_fields(study)
    cond = evaluate_condition_eligibility(
        conditions=_split_pipe(study.get("conditions_raw")),
        keywords=_split_pipe(study.get("keywords_raw")),
        config=load_yaml("condition_patterns_proposed.yaml"),
        brief_title=study.get("brief_title"),
        official_title=study.get("official_title"),
        intervention_names=study.get("intervention_names"),
        force_headache_include=source == "headache_expansion",
    )
    rq = evaluate_rq_eligibility(
        nct_id=study["nct_id"],
        behavioral_component=study.get("behavioral_component"),
        non_psychological_behavioral_flag=bool(
            study.get("non_psychological_behavioral_flag") is True
            or str(study.get("non_psychological_behavioral_flag")).lower() == "true"
        ),
        non_psychological_behavioral_type=study.get("non_psychological_behavioral_type"),
        condition_eligibility=cond.eligibility,
        brief_title=study.get("brief_title"),
        intervention_names=study.get("intervention_names"),
        intervention_classification_rule=study.get("intervention_classification_rule"),
    )
    eligible = cond.targets_eligible
    return {
        "nct_id": study["nct_id"],
        "cohort_source": source,
        "brief_title": study.get("brief_title"),
        "official_title": study.get("official_title"),
        "conditions_raw": study.get("conditions_raw"),
        "keywords_raw": study.get("keywords_raw"),
        "intervention_names": study.get("intervention_names"),
        "behavioral_component": study.get("behavioral_component"),
        "intervention_classification_rule": study.get("intervention_classification_rule"),
        "non_psychological_behavioral_flag": study.get("non_psychological_behavioral_flag"),
        "non_psychological_behavioral_type": study.get("non_psychological_behavioral_type"),
        "is_multimodal": study.get("is_multimodal"),
        "condition_targets_detected": " | ".join(cond.targets_detected),
        "condition_matched_proposed": " | ".join(eligible),
        "condition_eligibility": cond.eligibility,
        "condition_exclusion_rule": cond.exclusion_rule or "",
        "condition_borderline_reason": cond.borderline_reason or "",
        "eligible_migraine": "migraine" in eligible,
        "eligible_chronic_back_pain": "chronic_back_pain" in eligible,
        "eligible_fibromyalgia": "fibromyalgia" in eligible,
        "eligible_headache": "primary_headache" in eligible,
        "rq_eligibility": rq.rq_eligibility,
        "rq_reason": rq.rq_reason,
        "extraction_run_id": study.get("extraction_run_id", EXISTING_RUN_ID),
    }


def _load_headache_expansion_records() -> list[dict]:
    raw_path = PROJECT_ROOT / "reports/exploration/headache_candidates_raw.json"
    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    by_nct = {
        item["protocolSection"]["identificationModule"]["nctId"]: item
        for item in payload["studies"]
    }

    condition_config = load_yaml("condition_patterns.yaml")
    intervention_config = load_yaml("intervention_taxonomy.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")
    manifest_path = (
        PROJECT_ROOT / "data/processed/full" / EXISTING_RUN_ID / "extraction_manifest.json"
    )
    api_version = None
    data_timestamp = None
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        api_version = manifest.get("api_version")
        data_timestamp = manifest.get("data_timestamp")

    studies: list[dict] = []
    for nct_id in HEADACHE_EXPANSION_NCTS:
        record = by_nct[nct_id]
        study_row, _ = parse_study_record(
            record,
            condition_config=condition_config,
            intervention_config=intervention_config,
            outcome_lexicon=outcome_lexicon,
            extraction_run_id=f"{EXISTING_RUN_ID}_proposed_headache",
            api_version=api_version,
            data_timestamp=data_timestamp,
            query_source=QUERY_SOURCE,
        )
        studies.append(study_row)
    return studies


def build_proposed_cohort() -> Path:
    proposed_config_path = PROJECT_ROOT / "config" / "condition_patterns_proposed.yaml"
    if not proposed_config_path.is_file():
        raise FileNotFoundError(proposed_config_path)

    existing_path = (
        PROJECT_ROOT / "data/processed/full" / EXISTING_RUN_ID / "studies.csv"
    )
    if not existing_path.is_file():
        raise FileNotFoundError(existing_path)

    existing_df = pd.read_csv(existing_path)
    existing_ids = set(existing_df["nct_id"])

    rows: list[dict] = []
    for _, study in existing_df.iterrows():
        rows.append(_row_from_study_dict(study.to_dict(), source="existing_cohort"))

    headache_added = 0
    for study in _load_headache_expansion_records():
        if study["nct_id"] in existing_ids:
            continue
        rows.append(_row_from_study_dict(study, source="headache_expansion"))
        headache_added += 1

    out_dir = PROJECT_ROOT / "reports/exploration/proposed_cohort"
    out_dir.mkdir(parents=True, exist_ok=True)
    proposed_df = pd.DataFrame(rows)
    proposed_df.to_csv(out_dir / "proposed_studies.csv", index=False)

    _write_qc_report(proposed_df, out_dir / "proposed_cohort_qc_report.md", headache_added)
    return out_dir


def _write_qc_report(df: pd.DataFrame, path: Path, headache_added: int) -> None:
    total = len(df)
    cond_eligible = df[df["condition_eligibility"] == "eligible"]
    cond_border = df[df["condition_eligibility"] == "borderline"]
    cond_excluded = df[df["condition_eligibility"] == "excluded"]

    rq_eligible = df[df["rq_eligibility"] == "rq_eligible"]
    rq_border = df[df["rq_eligibility"] == "rq_borderline"]
    rq_excluded = df[df["rq_eligibility"] == "rq_exclude"]

    rq_analysis = rq_eligible[rq_eligible["condition_eligibility"].isin(["eligible", "borderline"])]

    lines = [
        "# Proposed cohort QC report",
        "",
        "**Status:** Review layer only — does not modify `data/processed/full/`.",
        "",
        f"- **Master proposed cohort:** {total} studies ({len(df[df.cohort_source=='existing_cohort'])} existing + {headache_added} headache expansion)",
        f"- **Condition-eligible:** {len(cond_eligible)}",
        f"- **Condition-borderline:** {len(cond_border)}",
        f"- **Condition-excluded:** {len(cond_excluded)}",
        f"- **RQ-eligible:** {len(rq_eligible)}",
        f"- **RQ-borderline:** {len(rq_border)}",
        f"- **RQ-excluded:** {len(rq_excluded)}",
        f"- **Proposed RQ analysis subset** (condition eligible/borderline AND rq_eligible): **{len(rq_analysis)}**",
        "",
        "## Studies by condition (eligible flags)",
        "",
    ]

    for col, label in [
        ("eligible_migraine", "Migraine"),
        ("eligible_chronic_back_pain", "Chronic back pain"),
        ("eligible_fibromyalgia", "Fibromyalgia"),
        ("eligible_headache", "Primary headache (non-migraine)"),
    ]:
        sub = df[df[col] == True]
        ce = sub[sub["condition_eligibility"] == "eligible"]
        lines.append(f"- **{label}:** {len(ce)} condition-eligible ({len(sub)} total flagged)")

    lines.extend(["", "## Condition eligibility breakdown", ""])
    for status in ["eligible", "borderline", "excluded"]:
        n = len(df[df["condition_eligibility"] == status])
        lines.append(f"- `{status}`: {n}")

    lines.extend(["", "## RQ eligibility breakdown", ""])
    for status in ["rq_eligible", "rq_borderline", "rq_exclude"]:
        n = len(df[df["rq_eligibility"] == status])
        lines.append(f"- `{status}`: {n}")

    lines.extend(["", "## Condition exclusion rules (top)", ""])
    excl = cond_excluded[cond_excluded["condition_exclusion_rule"].astype(bool)]
    for rule, n in excl["condition_exclusion_rule"].value_counts().head(15).items():
        lines.append(f"- `{rule}`: {n}")

    lines.extend(["", "## Multi-condition overlap (condition-eligible only)", ""])
    ce = cond_eligible.copy()
    multi = ce["condition_matched_proposed"].fillna("").apply(
        lambda s: len([p for p in s.split("|") if p.strip()]) if s else 0
    )
    for n_conds in [1, 2, 3, 4]:
        count = int((multi == n_conds).sum())
        lines.append(f"- {n_conds} condition(s): {count}")

    lines.extend(["", "## Borderline cases (condition)", ""])
    for _, r in cond_border.sort_values("nct_id").iterrows():
        lines.append(
            f"- **{r['nct_id']}** — {r['condition_borderline_reason'] or 'borderline'} | "
            f"{(r['brief_title'] or '')[:70]}"
        )

    lines.extend(["", "## Borderline cases (RQ)", ""])
    for _, r in rq_border.sort_values("nct_id").iterrows():
        lines.append(f"- **{r['nct_id']}** — {r['rq_reason']} | {(r['brief_title'] or '')[:70]}")

    lines.extend(["", "## Surprising cases for manual review", ""])
    surprises = [
        ("NCT01599143", "Cancer listed; excluded across migraine/back pain/FM"),
        ("NCT05689944", "Not in cohort — excluded (TTH tag only, chronic pain enrollment)"),
        ("NCT01704677", "Surgical disc prosthesis vs rehab — excluded surgical_postoperative"),
        ("NCT05057676", "MS/CIS primary with FM tag; also lists Cancer in Remission — excluded cancer_oncology"),
    ]
    for nct, note in surprises:
        hit = df[df["nct_id"] == nct]
        if len(hit):
            r = hit.iloc[0]
            lines.append(
                f"- **{nct}** — {note} | condition=`{r['condition_eligibility']}` "
                f"rule=`{r['condition_exclusion_rule']}` rq=`{r['rq_eligibility']}`"
            )
        else:
            lines.append(f"- **{nct}** — {note} | not in proposed master cohort")

    lines.extend(["", "## Headache expansion (22 studies)", ""])
    he = df[df["cohort_source"] == "headache_expansion"].sort_values("nct_id")
    for _, r in he.iterrows():
        lines.append(
            f"- **{r['nct_id']}** | condition=`{r['condition_eligibility']}` | "
            f"rq=`{r['rq_eligibility']}` | {r['rq_reason']}"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    out = build_proposed_cohort()
    print(f"Proposed cohort written to {out}")


if __name__ == "__main__":
    main()
