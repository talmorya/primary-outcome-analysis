"""Build analytic cohort tables, report, and manifest under data/processed/cohort/."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .build_revised_cohort import COHORT_RULES_VERSION, build_revised_cohort
from .cohort_export import (
    COHORT_PROCESSED_ROOT_NAME,
    COHORT_REPORT_MD,
    MANIFEST_JSON,
    PRIMARY_OUTCOMES_CSV,
    STUDIES_CSV,
)
from .cohort_report import write_final_cohort_report
from .config_loader import PROJECT_ROOT
from .extraction_runs import latest_full_extraction_run_id

COHORT_DIR = PROJECT_ROOT / "data" / "processed" / COHORT_PROCESSED_ROOT_NAME
FINAL_RUN_ID = "cohort_simplified_v1"


def _write_manifest(
    path: Path,
    *,
    eligible: int,
    outcomes: int,
    master_pool: int,
    extraction_run_id: str,
) -> None:
    manifest: dict[str, Any] = {
        "run_id": FINAL_RUN_ID,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_extraction_run_id": extraction_run_id,
        "cohort_rules_version": COHORT_RULES_VERSION,
        "master_pool_studies": master_pool,
        "eligible_studies": eligible,
        "primary_outcome_rows_included": outcomes,
        "rules_document": "docs/COHORT_FILTERING_RULES.md",
        "column_dictionary": "docs/DATA_COLUMNS.md",
        "reproduction_guide": "docs/COHORT_REPRODUCTION_GUIDE.md",
        "output_files": {
            "studies": STUDIES_CSV,
            "primary_outcomes": PRIMARY_OUTCOMES_CSV,
            "report": COHORT_REPORT_MD,
        },
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def finalize_cohort(
    *,
    extraction_run_id: str | None = None,
) -> Path:
    run_id = extraction_run_id or latest_full_extraction_run_id()
    if not run_id:
        raise FileNotFoundError(
            "No full extraction run under data/raw/full/. Run ctgov_pipeline.run_full first."
        )

    if COHORT_DIR.exists():
        shutil.rmtree(COHORT_DIR)

    out_dir = build_revised_cohort(extraction_run_id=run_id, out_dir=COHORT_DIR)

    studies_df = pd.read_csv(out_dir / STUDIES_CSV)
    outcomes_df = pd.read_csv(out_dir / PRIMARY_OUTCOMES_CSV)

    included_mask = studies_df["cohort_inclusion_status"] == "included"
    eligible = int(included_mask.sum())
    master_pool = len(studies_df)
    inc_outcomes = outcomes_df[outcomes_df["cohort_inclusion_status"] == "included"]

    write_final_cohort_report(
        studies_df,
        inc_outcomes,
        out_dir / COHORT_REPORT_MD,
        run_id=FINAL_RUN_ID,
    )
    _write_manifest(
        out_dir / MANIFEST_JSON,
        eligible=eligible,
        outcomes=len(inc_outcomes),
        master_pool=master_pool,
        extraction_run_id=run_id,
    )

    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extraction-run-id", default=None)
    args = parser.parse_args()
    out = finalize_cohort(extraction_run_id=args.extraction_run_id)
    print(f"Final cohort written to {out}")


if __name__ == "__main__":
    main()
