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
from .config_loader import PROJECT_ROOT

FINAL_RUN_ID = "final_cohort_20260922"
SOURCE_EXTRACTION_RUN_ID = "full_20260823_201251"
EXPECTED_ELIGIBLE_STUDIES = 666


def _write_cohort_report(
    studies_df: pd.DataFrame,
    outcomes_df: pd.DataFrame,
    audit_df: pd.DataFrame,
    path: Path,
) -> None:
    total = len(studies_df)
    included = studies_df[studies_df["cohort_included"] == True]
    excluded = studies_df[studies_df["cohort_included"] != True]
    inc_outcomes = outcomes_df[outcomes_df["cohort_included"] == True]

    lines = [
        "# Final cohort report",
        "",
        f"**Run ID:** `{FINAL_RUN_ID}`",
        f"**Frozen:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"- **Master pool (pre-filter):** {total} studies",
        f"- **Final analytic cohort:** {len(included)} studies",
        f"- **Excluded (total):** {len(excluded)} studies",
        "",
        "## Exclusions by stage",
        "",
        f"- **Condition stage:** {(audit_df['exclusion_stage'] == 'condition').sum()}",
        f"- **Intervention stage:** {(audit_df['exclusion_stage'] == 'intervention').sum()}",
        f"- **Mechanism / non-treatment stage:** {(audit_df['exclusion_stage'] == 'mechanism').sum()}",
        "",
        "## Intervention categories (final cohort)",
        "",
    ]

    cat_counts: dict[str, int] = {}
    for cats in included["intervention_categories"].fillna(""):
        for cat in [c.strip() for c in str(cats).split("|") if c.strip()]:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, n in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{cat}`: {n}")

    multimodal = included["is_multimodal"] == True
    lines.extend(
        [
            "",
            "## Multimodal vs purely behavioral",
            "",
            f"- **Purely behavioral:** {len(included) - int(multimodal.sum())}",
            f"- **Multimodal:** {int(multimodal.sum())}",
            "",
            "## Primary outcomes",
            "",
            f"- **Total primary outcome rows:** {len(inc_outcomes)}",
            "",
            "### Outcome category distribution",
            "",
        ]
    )
    for cat, n in inc_outcomes["outcome_category"].value_counts().items():
        lines.append(f"- `{cat}`: {n}")

    mech_flag = included["primary_outcome_mechanistic"] == True
    lines.extend(
        [
            "",
            "## Primary outcome mechanistic flag",
            "",
            f"- **TRUE:** {int(mech_flag.sum())}",
            f"- **FALSE:** {len(included) - int(mech_flag.sum())}",
            "",
            "## Condition flags (studies may match multiple)",
            "",
        ]
    )
    for col, label in [
        ("eligible_migraine", "Migraine"),
        ("eligible_chronic_back_pain", "Chronic back pain"),
        ("eligible_fibromyalgia", "Fibromyalgia"),
        ("eligible_headache", "Primary headache"),
    ]:
        lines.append(f"- **{label}:** {int((included[col] == True).sum())}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    _write_cohort_report(studies_df, outcomes_df, audit_df, out_dir / "cohort_report.md")
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
