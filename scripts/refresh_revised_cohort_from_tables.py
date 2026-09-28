"""Re-apply cohort rules when raw JSON is unavailable (labels refresh only).

Reads the frozen master pool from data/processed/final_cohort/, reclassifies
interventions and outcomes, and writes reports/exploration/revised_cohort/.
Does not modify data/processed/full/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ctgov_pipeline.build_revised_cohort import (  # noqa: E402
    REVISED_RUN_ID,
    _write_outcome_other_analysis,
    _write_questionable_exclusions,
    _write_report,
)
from ctgov_pipeline.classify_intervention_categories import classify_intervention_categories
from ctgov_pipeline.config_loader import load_yaml
from ctgov_pipeline.condition_eligibility import evaluate_condition_eligibility
from ctgov_pipeline.extract_outcome_features import extract_outcome_features
from ctgov_pipeline.intervention_eligibility import (
    evaluate_intervention_eligibility,
    evaluate_mechanism_exclusion,
)
from ctgov_pipeline.outcome_category import classify_outcome_category
from ctgov_pipeline.outcome_mechanism import is_mechanistic_outcome


def _join_pipe(values: list[str] | None) -> str | None:
    if not values:
        return None
    return " | ".join(values)


def refresh() -> Path:
    source_dir = PROJECT_ROOT / "data" / "processed" / "final_cohort"
    out_dir = PROJECT_ROOT / "reports" / "exploration" / "revised_cohort"
    out_dir.mkdir(parents=True, exist_ok=True)

    intervention_config = load_yaml("intervention_categories.yaml")
    condition_config = load_yaml("condition_patterns_proposed.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    studies_df = pd.read_csv(source_dir / "studies.csv")
    outcomes_df = pd.read_csv(source_dir / "primary_outcomes.csv")
    prior_audit = pd.read_csv(source_dir / "exclusion_audit.csv")
    mechanism_only_ncts = set(
        prior_audit.loc[prior_audit["mechanism_excluded"] == True, "nct_id"].astype(str)
    )

    study_rows: list[dict] = []
    audit_rows: list[dict] = []

    for _, row in studies_df.iterrows():
        interventions = json.loads(row["interventions_raw"])
        intervention_cls = classify_intervention_categories(interventions, intervention_config)
        intervention_elig = evaluate_intervention_eligibility(intervention_cls)
        mechanism_elig = evaluate_mechanism_exclusion(classification=intervention_cls, record=None)
        mechanism_study_outcomes_only = row["nct_id"] in mechanism_only_ncts

        cond = evaluate_condition_eligibility(
            conditions=[c.strip() for c in str(row.get("conditions_raw") or "").split("|") if c.strip()],
            keywords=[k.strip() for k in str(row.get("keywords_raw") or "").split("|") if k.strip()],
            config=condition_config,
            brief_title=row.get("brief_title"),
            official_title=row.get("official_title"),
            intervention_names=row.get("intervention_names"),
            force_headache_include=row.get("cohort_source") == "headache_expansion",
        )

        cohort_included = (
            cond.eligibility in {"eligible", "borderline"}
            and intervention_elig.intervention_eligible
        )

        if cond.eligibility == "excluded":
            exclusion_stage, exclusion_reason = "condition", cond.exclusion_rule or "condition_excluded"
        elif not intervention_elig.intervention_eligible:
            exclusion_stage = "intervention"
            exclusion_reason = intervention_elig.exclusion_reason or "intervention_ineligible"
        else:
            exclusion_stage, exclusion_reason = "", ""

        study_row = row.to_dict()
        study_row.update(
            {
                "cohort_included": cohort_included,
                "exclusion_stage": exclusion_stage,
                "exclusion_reason": exclusion_reason,
                "condition_eligibility": cond.eligibility,
                "condition_exclusion_rule": cond.exclusion_rule or "",
                "condition_borderline_reason": cond.borderline_reason or "",
                "intervention_categories": _join_pipe(intervention_cls.intervention_categories),
                "intervention_category_labels": _join_pipe(intervention_cls.intervention_category_labels),
                "intervention_classification_rule": _join_pipe(intervention_cls.classification_rules),
                "intervention_review_flag": intervention_cls.review_flag,
                "is_multimodal": intervention_cls.is_multimodal,
                "multimodal_modalities": _join_pipe(intervention_cls.multimodal_modalities),
                "control_arm_types": _join_pipe(intervention_cls.control_arm_types),
                "control_arms_raw": json.dumps(intervention_cls.control_arms_raw, ensure_ascii=False),
                "mechanism_study_outcomes_only": mechanism_study_outcomes_only,
                "extraction_run_id": REVISED_RUN_ID,
            }
        )
        study_rows.append(study_row)

        audit_rows.append(
            {
                "nct_id": row["nct_id"],
                "cohort_source": row.get("cohort_source"),
                "cohort_included": cohort_included,
                "exclusion_stage": exclusion_stage,
                "exclusion_reason": exclusion_reason,
                "condition_eligibility": cond.eligibility,
                "intervention_eligible": intervention_elig.intervention_eligible,
                "mechanism_excluded": mechanism_elig.mechanism_excluded,
            }
        )

    studies_out = pd.DataFrame(study_rows)
    included_ids = set(studies_out.loc[studies_out["cohort_included"] == True, "nct_id"])

    outcome_rows: list[dict] = []
    for _, orow in outcomes_df.iterrows():
        measure = orow.get("primary_outcome_measure")
        description = orow.get("primary_outcome_description")
        time_frame = orow.get("primary_outcome_time_frame")
        if pd.isna(measure):
            measure = None
        if pd.isna(description):
            description = None
        if pd.isna(time_frame):
            time_frame = None
        category = classify_outcome_category(measure, description, time_frame)
        features = extract_outcome_features(
            measure, description, time_frame, lexicon=outcome_lexicon
        )
        nct_id = orow["nct_id"]
        srow = studies_out.loc[studies_out["nct_id"] == nct_id].iloc[0]
        cohort_included = nct_id in included_ids

        outcome_rows.append(
            {
                **orow.to_dict(),
                "cohort_included": cohort_included,
                "outcome_category": category.outcome_category,
                "outcome_subcategory": category.outcome_subcategory,
                "outcome_category_rule": category.rule,
                "outcome_category_review_flag": category.review_flag,
                "outcome_is_mechanistic": is_mechanistic_outcome(measure, description, time_frame),
                "instruments_detected": _join_pipe(features.instruments_detected),
                "acronyms_detected": _join_pipe(features.acronyms_detected),
                "keywords_matched": _join_pipe(features.keywords_matched),
                "phrases_matched": _join_pipe(features.phrases_matched),
                "action_verbs_matched": _join_pipe(features.action_verbs_matched),
                "intervention_categories": srow.get("intervention_categories"),
                "is_multimodal": srow.get("is_multimodal"),
                "extraction_run_id": REVISED_RUN_ID,
            }
        )

    outcomes_out = pd.DataFrame(outcome_rows)
    audit_df = pd.DataFrame(audit_rows)

    studies_out.to_csv(out_dir / "studies.csv", index=False)
    outcomes_out.to_csv(out_dir / "primary_outcomes.csv", index=False)
    audit_df.to_csv(out_dir / "exclusion_audit.csv", index=False)

    _write_report(studies_out, outcomes_out, audit_df, out_dir / "revised_cohort_report.md")
    _write_questionable_exclusions(studies_out, out_dir / "questionable_exclusions.md")
    _write_outcome_other_analysis(outcomes_out, out_dir / "outcome_other_category_review.md")
    return out_dir


if __name__ == "__main__":
    path = refresh()
    print(f"Refreshed revised cohort at {path}")
