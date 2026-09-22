"""Re-apply intervention taxonomy to an existing extraction run without re-fetching."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .classify_interventions import classify_interventions
from .config_loader import PROJECT_ROOT, load_yaml
from .parse import load_raw_studies

INTERVENTION_COLUMNS = [
    "behavioral_component",
    "intervention_classification_rule",
    "intervention_review_flag",
    "is_multimodal",
    "other_modality_present",
    "other_modality_type",
    "other_modality_name",
    "non_psychological_behavioral_flag",
    "non_psychological_behavioral_type",
    "non_psychological_behavioral_name",
]


def _join(values: list[str] | None, sep: str = " | ") -> str | None:
    if not values:
        return None
    return sep.join(values)


def classify_record(record: dict, intervention_config: dict) -> dict:
    interventions = (
        record.get("protocolSection", {})
        .get("armsInterventionsModule", {})
        .get("interventions", [])
    )
    intervention = classify_interventions(interventions, intervention_config)
    return {
        "behavioral_component": _join(intervention.behavioral_component),
        "intervention_classification_rule": _join(intervention.classification_rules),
        "intervention_review_flag": intervention.review_flag,
        "is_multimodal": intervention.is_multimodal,
        "other_modality_present": intervention.other_modality_present,
        "other_modality_type": intervention.other_modality_type,
        "other_modality_name": intervention.other_modality_name,
        "non_psychological_behavioral_flag": intervention.non_psychological_behavioral_flag,
        "non_psychological_behavioral_type": intervention.non_psychological_behavioral_type,
        "non_psychological_behavioral_name": intervention.non_psychological_behavioral_name,
    }


def reprocess_interventions(run_id: str) -> Path:
    raw_dir = PROJECT_ROOT / "data" / "raw" / "full" / run_id / "studies"
    processed_dir = PROJECT_ROOT / "data" / "processed" / "full" / run_id
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw studies directory not found: {raw_dir}")
    if not (processed_dir / "studies.csv").is_file():
        raise FileNotFoundError(f"Processed studies.csv not found: {processed_dir / 'studies.csv'}")

    intervention_config = load_yaml("intervention_taxonomy.yaml")
    records = load_raw_studies(raw_dir)

    updates = {
        record["protocolSection"]["identificationModule"]["nctId"]: classify_record(
            record, intervention_config
        )
        for record in records
    }

    studies_df = pd.read_csv(processed_dir / "studies.csv")
    outcomes_df = pd.read_csv(processed_dir / "primary_outcomes.csv")

    for column in INTERVENTION_COLUMNS:
        studies_df[column] = studies_df["nct_id"].map(lambda nct_id: updates[nct_id][column])

    study_lookup = studies_df.set_index("nct_id")[["behavioral_component", "is_multimodal"]]
    outcomes_df["behavioral_component"] = outcomes_df["nct_id"].map(study_lookup["behavioral_component"])
    outcomes_df["is_multimodal"] = outcomes_df["nct_id"].map(study_lookup["is_multimodal"])

    studies_df.to_csv(processed_dir / "studies.csv", index=False)
    outcomes_df.to_csv(processed_dir / "primary_outcomes.csv", index=False)

    print(f"Reprocessed intervention classification: {processed_dir}")
    print(f"Studies updated: {len(studies_df)}")
    print(f"Primary outcome rows synced (behavioral_component, is_multimodal only): {len(outcomes_df)}")
    return processed_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "run_id",
        nargs="?",
        default="full_20260823_201251",
        help="Existing full extraction run ID",
    )
    args = parser.parse_args()
    reprocess_interventions(args.run_id)


if __name__ == "__main__":
    main()
