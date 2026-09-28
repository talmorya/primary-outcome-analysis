"""Recompute intervention category columns from interventions_raw (no API/raw JSON needed)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from ctgov_pipeline.classify_intervention_categories import classify_intervention_categories
from ctgov_pipeline.config_loader import PROJECT_ROOT, load_yaml


def recompute(studies_path: Path, outcomes_path: Path | None) -> None:
    config = load_yaml("intervention_categories.yaml")
    studies = pd.read_csv(studies_path)

    for idx, row in studies.iterrows():
        raw = row.get("interventions_raw")
        if not raw or str(raw).strip().lower() == "nan":
            continue
        interventions = json.loads(raw)
        result = classify_intervention_categories(interventions, config)
        studies.at[idx, "intervention_categories"] = "|".join(result.intervention_categories)
        studies.at[idx, "intervention_category_labels"] = "|".join(
            result.intervention_category_labels
        )
        studies.at[idx, "intervention_classification_rule"] = "|".join(
            result.classification_rules
        )
        studies.at[idx, "intervention_review_flag"] = result.review_flag
        studies.at[idx, "is_multimodal"] = result.is_multimodal
        studies.at[idx, "multimodal_modalities"] = "|".join(result.multimodal_modalities)
        studies.at[idx, "control_arm_types"] = "|".join(result.control_arm_types)
        studies.at[idx, "control_arms_raw"] = json.dumps(result.control_arms_raw, ensure_ascii=False)

    studies.to_csv(studies_path, index=False)

    if outcomes_path and outcomes_path.is_file():
        outcomes = pd.read_csv(outcomes_path)
        for col in ("intervention_categories", "is_multimodal"):
            outcomes[col] = outcomes["nct_id"].map(studies.set_index("nct_id")[col])
        outcomes.to_csv(outcomes_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--studies",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "final_cohort" / "studies.csv",
    )
    parser.add_argument(
        "--outcomes",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "final_cohort" / "primary_outcomes.csv",
    )
    args = parser.parse_args()
    recompute(args.studies, args.outcomes)
    print(f"Updated {args.studies}")


if __name__ == "__main__":
    main()
