"""Generate descriptive statistics report for the analytic cohort."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .cohort_export import exclusion_rule_from_detail


def write_final_cohort_report(
    studies_df: pd.DataFrame,
    outcomes_df: pd.DataFrame,
    path: Path,
    *,
    run_id: str,
) -> None:
    total = len(studies_df)
    included = studies_df[studies_df["cohort_inclusion_status"] == "included"]
    excluded = studies_df[studies_df["cohort_inclusion_status"] != "included"]
    inc_outcomes = outcomes_df

    nct_with_outcomes = inc_outcomes["nct_id"].nunique()
    mean_po = len(inc_outcomes) / len(included) if len(included) else 0.0

    lines = [
        "# Analytic cohort statistics",
        "",
        f"**Run ID:** `{run_id}`",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.",
        "Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.",
        "",
        "---",
        "",
        "## Cohort size",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Master pool (API retrieval) | {total} |",
        f"| Included | **{len(included)}** |",
        f"| Excluded | {len(excluded)} |",
        f"| Primary outcome rows (included studies) | {len(inc_outcomes)} |",
        f"| Studies with ≥1 primary outcome | {nct_with_outcomes} |",
        f"| Mean primary outcomes per study | {mean_po:.1f} |",
        "",
        "## Condition exclusions",
        "",
        f"- **Excluded at condition stage:** {len(excluded)}",
        "",
    ]

    if len(excluded):
        lines.extend(["### By general reason (`exclusion_reason`)", ""])
        for reason, n in excluded["exclusion_reason"].value_counts().items():
            lines.append(f"- `{reason}`: {n}")
        lines.extend(["", "### By specific rule (start of `exclusion_detail`)", ""])
        for rule, n in excluded["exclusion_detail"].map(exclusion_rule_from_detail).value_counts().items():
            lines.append(f"- `{rule or '(none)'}`: {n}")
        lines.append("")

    lines.extend(
        [
            "## Studies by condition",
            "",
            "Flags are non-mutually-exclusive.",
            "",
            "| Condition flag | Studies |",
            "|---|---:|",
        ]
    )
    for col, label in [
        ("eligible_chronic_back_pain", "Chronic back pain"),
        ("eligible_fibromyalgia", "Fibromyalgia"),
        ("eligible_migraine", "Migraine"),
        ("eligible_headache", "Primary headache (non-migraine)"),
    ]:
        lines.append(f"| {label} | {int((included[col] == True).sum())} |")
    lines.append("")

    lines.extend(["## Intervention categories", "", "Pipe-joined; study counts may sum to > cohort size.", ""])
    cat_counts: Counter[str] = Counter()
    for cats in included["intervention_categories"].fillna(""):
        for cat in [c.strip() for c in str(cats).split("|") if c.strip()]:
            cat_counts[cat] += 1
    lines.extend(["| Category | Studies |", "|---|---:|"])
    for cat, n in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| `{cat}` | {n} |")
    lines.append("")

    multimodal = included["is_multimodal"] == True
    lines.extend(
        [
            "### Multimodal vs not multimodal",
            "",
            "| Type | Studies |",
            "|---|---:|",
            f"| Not multimodal | {len(included) - int(multimodal.sum())} |",
            f"| Multimodal | {int(multimodal.sum())} |",
            "",
            "## Primary outcome categories",
            "",
            "| `outcome_category` | Outcome rows |",
            "|---|---:|",
        ]
    )
    for cat, n in inc_outcomes["outcome_category"].value_counts().items():
        lines.append(f"| `{cat}` | {n} |")
    lines.append("")

    lines.extend(["### Top outcome subcategories", "", "| Category → subcategory | Outcome rows |", "|---|---:|"])
    sub_counts = (
        inc_outcomes.groupby(["outcome_category", "outcome_subcategory"])
        .size()
        .sort_values(ascending=False)
        .head(15)
    )
    for (cat, sub), n in sub_counts.items():
        lines.append(f"| `{cat}` → `{sub}` | {n} |")
    lines.append("")

    mech_flag = included["primary_outcome_mechanistic"] == True
    lines.extend(
        [
            "## Primary outcome mechanistic flag (study-level)",
            "",
            "| Flag | Studies |",
            "|---|---:|",
            f"| `primary_outcome_mechanistic = TRUE` | {int(mech_flag.sum())} |",
            f"| `primary_outcome_mechanistic = FALSE` | {len(included) - int(mech_flag.sum())} |",
            "",
        ]
    )

    lines.extend(["## Trial status and phase", "", "### `overall_status`", "", "| Status | Studies |", "|---|---:|"])
    for status, n in included["raw_overall_status"].fillna("").value_counts().items():
        lines.append(f"| {status or '(missing)'} | {n} |")
    lines.append("")

    if "raw_study_first_post_date" in included.columns:
        years = (
            included["raw_study_first_post_date"]
            .dropna()
            .astype(str)
            .str.slice(0, 4)
            .value_counts()
            .sort_index()
        )
        lines.extend(["## Registration year (`study_first_post_date`)", "", "| Year | Studies |", "|---|---:|"])
        for year, n in years.items():
            if year.isdigit():
                lines.append(f"| {year} | {n} |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_pipe_field(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]
