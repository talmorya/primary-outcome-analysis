"""Freeze the finalized analytic cohort into data/processed/final_cohort/."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .build_revised_cohort import build_revised_cohort
from .cohort_report import write_final_cohort_report
from .config_loader import PROJECT_ROOT

FINAL_RUN_ID = "final_cohort_20260922"
SOURCE_EXTRACTION_RUN_ID = "full_20260823_201251"
EXPECTED_ELIGIBLE_STUDIES = 666


def _write_manifest(path: Path, *, eligible: int, outcomes: int) -> None:
    manifest: dict[str, Any] = {
        "run_id": FINAL_RUN_ID,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_extraction_run_id": SOURCE_EXTRACTION_RUN_ID,
        "master_pool_studies": 696,
        "eligible_studies": eligible,
        "primary_outcome_rows": outcomes,
        "manual_decisions": {
            "NCT00864422": "KEEP; primary_outcome_mechanistic=TRUE, has_clinical_outcome_anywhere=TRUE",
            "NCT01118988": "KEEP; heterogeneous chronic pain conditions retained (no heterogeneity exclusion)",
        },
        "rules_document": "FINAL_INCLUSION_RULES.md",
        "reproduction_guide": "COHORT_REPRODUCTION_GUIDE.md",
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def finalize_cohort(*, review_dir: Path | None = None) -> Path:
    if review_dir is None:
        raw_studies = (
            PROJECT_ROOT
            / "data"
            / "raw"
            / "full"
            / SOURCE_EXTRACTION_RUN_ID
            / "studies"
        )
        if raw_studies.is_dir() and any(raw_studies.glob("*.json")):
            review_dir = build_revised_cohort()
        else:
            review_dir = PROJECT_ROOT / "reports" / "exploration" / "revised_cohort"
            if not (review_dir / "studies.csv").is_file():
                raise FileNotFoundError(
                    "No raw JSON and no reports/exploration/revised_cohort/studies.csv; "
                    "run build_revised_cohort or scripts/refresh_revised_cohort_from_tables.py"
                )
    studies_df = pd.read_csv(review_dir / "studies.csv")
    outcomes_df = pd.read_csv(review_dir / "primary_outcomes.csv")
    audit_df = pd.read_csv(review_dir / "exclusion_audit.csv")

    eligible = int((studies_df["cohort_included"] == True).sum())
    if eligible != EXPECTED_ELIGIBLE_STUDIES:
        raise ValueError(
            f"Expected {EXPECTED_ELIGIBLE_STUDIES} eligible studies, got {eligible}"
        )

    out_dir = PROJECT_ROOT / "data" / "processed" / "final_cohort"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    for name in ("studies.csv", "primary_outcomes.csv", "exclusion_audit.csv"):
        shutil.copy2(review_dir / name, out_dir / name)

    write_final_cohort_report(
        studies_df,
        outcomes_df,
        audit_df,
        out_dir / "cohort_report.md",
        run_id=FINAL_RUN_ID,
    )
    inc_outcomes = outcomes_df[outcomes_df["cohort_included"] == True]
    _write_manifest(
        out_dir / "cohort_manifest.json",
        eligible=eligible,
        outcomes=len(inc_outcomes),
    )

    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    out = finalize_cohort()
    print(f"Final cohort written to {out}")


if __name__ == "__main__":
    main()
