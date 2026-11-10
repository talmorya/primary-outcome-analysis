"""Build analytic cohort: API pool → condition filter → descriptive classifications."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from .api_query_hits import load_api_query_hits
from .classify_intervention_categories import classify_intervention_categories
from .cohort_export import (
    PRIMARY_OUTCOMES_CSV,
    STUDIES_CSV,
    build_exclusion_fields,
    first_n_words,
    interventions_text,
    project_study_row,
)
from .condition_eligibility import detect_review_flags, evaluate_condition_eligibility
from .config_loader import PROJECT_ROOT, load_yaml
from .eligibility_text import extract_pain_duration_sentences
from .extract_outcome_features import extract_outcome_features
from .extraction_runs import latest_full_extraction_run_id
from .outcome_category import classify_outcome_category
from .outcome_mechanism import assess_primary_outcome_mechanistic, is_mechanistic_outcome
from .parse import load_raw_studies

COHORT_RULES_VERSION = "conditions_field_v2"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

QUERY_SOURCE = (
    "StudyType=INTERVENTIONAL AND InterventionType=BEHAVIORAL "
    "AND registered Condition field contains (back pain, fibromyalgia, migraine, headache)"
)


def _join(values: list[str] | None, sep: str = " | ") -> str | None:
    if not values:
        return None
    return sep.join(values)


def _eligibility_criteria(record: dict[str, Any]) -> str | None:
    ps = record.get("protocolSection", {})
    elig = ps.get("eligibilityModule", {}) or {}
    return elig.get("eligibilityCriteria")


def dedupe_records_by_nct_id(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Keep the first record per NCT id (a trial can be returned by several API queries)."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for record in records:
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        if nct_id in seen:
            continue
        seen.add(nct_id)
        unique.append(record)
    return unique, len(records) - len(unique)


def _load_records(run_id: str) -> list[dict[str, Any]]:
    raw_dir = PROJECT_ROOT / "data" / "raw" / "full" / run_id / "studies"
    records, n_duplicates = dedupe_records_by_nct_id(load_raw_studies(raw_dir))
    if n_duplicates:
        print(f"Removed {n_duplicates} duplicate NCT id record(s) before filtering.")
    return records


def _parse_record(
    record: dict[str, Any],
    *,
    extraction_run_id: str,
    condition_config: dict[str, Any],
    intervention_config: dict[str, Any],
    outcome_lexicon: dict[str, Any],
    api_retrieval_queries: str | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ps = record.get("protocolSection", {})
    id_mod = ps.get("identificationModule", {})
    status_mod = ps.get("statusModule", {})
    conditions_mod = ps.get("conditionsModule", {})
    design_mod = ps.get("designModule", {})
    arms_mod = ps.get("armsInterventionsModule", {})
    outcomes_mod = ps.get("outcomesModule", {})

    nct_id = id_mod.get("nctId")
    conditions = conditions_mod.get("conditions", []) or []
    keywords = conditions_mod.get("keywords", []) or []
    interventions = arms_mod.get("interventions", []) or []
    eligibility_criteria = _eligibility_criteria(record)
    brief_summary = (ps.get("descriptionModule", {}) or {}).get("briefSummary")

    cond = evaluate_condition_eligibility(
        conditions=conditions,
        keywords=keywords,
        config=condition_config,
        brief_title=id_mod.get("briefTitle"),
        official_title=id_mod.get("officialTitle"),
        brief_summary=brief_summary,
        eligibility_criteria=eligibility_criteria,
    )

    intervention_cls = classify_intervention_categories(interventions, intervention_config)

    included = cond.eligibility == "eligible"
    cohort_inclusion_status = "included" if included else "excluded"
    exclusion_reason, exclusion_detail = build_exclusion_fields(
        cond=cond, rule=cond.exclusion_rule or ""
    )
    # Flags reflect the registered conditions section only (several can be true).
    eligible_targets = cond.targets_in_conditions

    study_row = project_study_row(
        {
            "nct_id": nct_id,
            "cohort_inclusion_status": cohort_inclusion_status,
            "exclusion_reason": exclusion_reason,
            "exclusion_detail": exclusion_detail,
            "raw_brief_title": id_mod.get("briefTitle"),
            "raw_official_title": id_mod.get("officialTitle"),
            "raw_brief_summary_50w": first_n_words(brief_summary, 50),
            "raw_conditions": _join(conditions),
            "raw_keywords": _join(keywords),
            "raw_eligibility_criteria": eligibility_criteria,
            "pain_duration_inclusion": _join(extract_pain_duration_sentences(eligibility_criteria)),
            "condition_matched": _join(eligible_targets),
            "condition_feature_flags": _join(cond.condition_feature_flags),
            "review_flags": _join(
                detect_review_flags(
                    brief_title=id_mod.get("briefTitle"),
                    official_title=id_mod.get("officialTitle"),
                    config=condition_config,
                )
            ),
            "eligible_migraine": "migraine" in eligible_targets,
            "eligible_chronic_back_pain": "chronic_back_pain" in eligible_targets,
            "eligible_fibromyalgia": "fibromyalgia" in eligible_targets,
            "eligible_headache": "headache" in eligible_targets,
            "intervention_categories": _join(intervention_cls.intervention_categories),
            "is_multimodal": intervention_cls.is_multimodal,
            "control_arm_types": _join(intervention_cls.control_arm_types),
            "raw_intervention_names": _join([item.get("name", "") for item in interventions]),
            "raw_intervention_details": interventions_text(interventions),
            "raw_overall_status": status_mod.get("overallStatus"),
            "raw_study_first_post_date": status_mod.get("studyFirstPostDateStruct", {}).get("date"),
            "raw_phases": _join(design_mod.get("phases", [])),
            "raw_primary_purpose": design_mod.get("designInfo", {}).get("primaryPurpose"),
            "raw_has_results": record.get("hasResults"),
            "primary_outcome_mechanistic": assess_primary_outcome_mechanistic(
                [
                    {
                        "measure": o.get("measure"),
                        "description": o.get("description"),
                        "time_frame": o.get("timeFrame"),
                    }
                    for o in (outcomes_mod.get("primaryOutcomes", []) or [])
                ]
            ),
            "api_retrieval_queries": api_retrieval_queries,
            "extraction_run_id": extraction_run_id,
            "cohort_rules_version": COHORT_RULES_VERSION,
        }
    )

    primary_outcomes = outcomes_mod.get("primaryOutcomes", []) or []
    outcome_rows: list[dict[str, Any]] = []
    for index, outcome in enumerate(primary_outcomes, start=1):
        measure = outcome.get("measure")
        description = outcome.get("description")
        time_frame = outcome.get("timeFrame")
        features = extract_outcome_features(measure, description, time_frame, outcome_lexicon)
        category = classify_outcome_category(measure, description, time_frame)
        outcome_rows.append(
            {
                "outcome_id": f"{nct_id}__po_{index}",
                "nct_id": nct_id,
                "cohort_inclusion_status": cohort_inclusion_status,
                "primary_outcome_index": index,
                "n_primary_outcomes_in_study": len(primary_outcomes),
                "raw_primary_outcome_measure": measure,
                "raw_primary_outcome_description": description,
                "raw_primary_outcome_time_frame": time_frame,
                "outcome_category": category.outcome_category,
                "outcome_subcategory": category.outcome_subcategory,
                "outcome_category_rule": category.rule,
                "outcome_category_review_flag": category.review_flag,
                "outcome_is_mechanistic": is_mechanistic_outcome(measure, description, time_frame),
                "instruments_detected": _join(features.instruments_detected),
                "raw_study_first_post_date": study_row["raw_study_first_post_date"],
                "extraction_run_id": extraction_run_id,
            }
        )

    return study_row, outcome_rows


def build_revised_cohort(
    *,
    extraction_run_id: str | None = None,
    out_dir: Path | None = None,
) -> Path:
    run_id = extraction_run_id or latest_full_extraction_run_id()
    if not run_id:
        raise FileNotFoundError(
            "No full extraction run found under data/raw/full/. Run ctgov_pipeline.run_full first."
        )

    if out_dir is None:
        out_dir = PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    condition_config = load_yaml("condition_patterns_cohort.yaml")
    intervention_config = load_yaml("intervention_categories.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    query_hits = load_api_query_hits(run_id)

    study_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []

    for record in _load_records(run_id):
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        study_row, outcomes = _parse_record(
            record,
            extraction_run_id=run_id,
            condition_config=condition_config,
            intervention_config=intervention_config,
            outcome_lexicon=outcome_lexicon,
            api_retrieval_queries=_join(query_hits.get(nct_id, [])),
        )
        study_rows.append(study_row)
        outcome_rows.extend(outcomes)

    studies_df = pd.DataFrame(study_rows)
    outcomes_df = pd.DataFrame(outcome_rows)

    if studies_df["nct_id"].duplicated().any():
        dupes = studies_df.loc[studies_df["nct_id"].duplicated(), "nct_id"].tolist()
        raise ValueError(f"Duplicate nct_id in studies table: {dupes}")
    if outcomes_df["outcome_id"].duplicated().any():
        raise ValueError("Duplicate outcome_id in primary_outcomes table")

    studies_df.to_csv(out_dir / STUDIES_CSV, index=False)
    outcomes_df.to_csv(out_dir / PRIMARY_OUTCOMES_CSV, index=False)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extraction-run-id",
        default=None,
        help="Raw JSON run under data/raw/full/ (default: latest)",
    )
    args = parser.parse_args()
    out = build_revised_cohort(extraction_run_id=args.extraction_run_id)
    print(f"Cohort tables written to {out}")


if __name__ == "__main__":
    main()
