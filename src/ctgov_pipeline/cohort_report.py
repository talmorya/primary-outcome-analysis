"""Generate descriptive statistics report for the frozen analytic cohort."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def write_final_cohort_report(
    studies_df: pd.DataFrame,
    outcomes_df: pd.DataFrame,
    audit_df: pd.DataFrame,
    path: Path,
    *,
    run_id: str,
) -> None:
    total = len(studies_df)
    included = studies_df[studies_df["cohort_included"] == True]
    excluded = studies_df[studies_df["cohort_included"] != True]
    inc_outcomes = outcomes_df[outcomes_df["cohort_included"] == True]

    nct_with_outcomes = inc_outcomes["nct_id"].nunique()
    mean_po = len(inc_outcomes) / len(included) if len(included) else 0.0

    lines = [
        "# Analytic cohort statistics",
        "",
        f"**Run ID:** `{run_id}`",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Auto-generated from `data/processed/final_cohort/*.csv` on each `finalize_cohort` run.",
        "Inclusion rules and classification patterns: `FINAL_INCLUSION_RULES.md`.",
        "",
        "Filter: `cohort_included == True` in `studies.csv` and `primary_outcomes.csv`.",
        "",
        "---",
        "",
        "## Cohort size",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Master pool (pre-filter) | {total} |",
        f"| Final analytic cohort | **{len(included)}** |",
        f"| Excluded | {len(excluded)} |",
        f"| Primary outcome rows | {len(inc_outcomes)} |",
        f"| Studies with ≥1 primary outcome | {nct_with_outcomes} |",
        f"| Mean primary outcomes per study | {mean_po:.1f} |",
        "",
        "## Exclusions by stage",
        "",
        f"- **Condition:** {(audit_df['exclusion_stage'] == 'condition').sum()}",
        f"- **Intervention:** {(audit_df['exclusion_stage'] == 'intervention').sum()}",
        f"- **Mechanism (historical audit label):** {(audit_df['exclusion_stage'] == 'mechanism').sum()}",
        "",
    ]

    cond_excl = audit_df[audit_df["exclusion_stage"] == "condition"]
    if len(cond_excl):
        lines.extend(["### Condition exclusion reasons", ""])
        for reason, n in cond_excl["exclusion_reason"].value_counts().items():
            lines.append(f"- `{reason}`: {n}")
        lines.append("")

    int_excl = audit_df[audit_df["exclusion_stage"] == "intervention"]
    if len(int_excl):
        lines.extend(["### Intervention exclusion reasons", ""])
        for reason, n in int_excl["exclusion_reason"].value_counts().items():
            lines.append(f"- `{reason}`: {n}")
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
            "### By condition (`primary_outcome_mechanistic = TRUE`)",
            "",
            "| Condition | Studies |",
            "|---|---:|",
        ]
    )
    for col, label in [
        ("eligible_chronic_back_pain", "Chronic back pain"),
        ("eligible_fibromyalgia", "Fibromyalgia"),
        ("eligible_migraine", "Migraine"),
        ("eligible_headache", "Primary headache"),
    ]:
        lines.append(f"| {label} | {len(included[(included[col] == True) & mech_flag])} |")
    lines.append("")

    lines.extend(
        [
            "## Intervention category × outcome category",
            "",
            "Outcome-row counts; each study's intervention categories are applied to all its primary outcomes.",
            "",
        ]
    )
    outcome_cats = sorted(inc_outcomes["outcome_category"].dropna().unique())
    header = "| Intervention category | " + " | ".join(f"`{c}`" for c in outcome_cats) + " |"
    sep = "|---|" + "|".join(["---:"] * len(outcome_cats)) + "|"
    lines.extend([header, sep])
    cross: dict[str, Counter[str]] = {cat: Counter() for cat in cat_counts}
    study_cats = {
        row["nct_id"]: parse_pipe_field(row.get("intervention_categories"))
        for _, row in included.iterrows()
    }
    for _, orow in inc_outcomes.iterrows():
        ocat = orow.get("outcome_category")
        for icat in study_cats.get(orow["nct_id"], []):
            if icat in cross and pd.notna(ocat):
                cross[icat][str(ocat)] += 1
    for icat in sorted(cat_counts.keys(), key=lambda c: (-cat_counts[c], c)):
        row_cells = [str(cross[icat].get(c, 0)) for c in outcome_cats]
        lines.append(f"| `{icat}` | " + " | ".join(row_cells) + " |")
    lines.append("")

    lines.extend(["## Trial status and phase", "", "### `overall_status`", "", "| Status | Studies |", "|---|---:|"])
    for status, n in included["overall_status"].fillna("").value_counts().items():
        lines.append(f"| {status or '(missing)'} | {n} |")
    lines.append("")

    lines.extend(["### `has_results`", "", "| Posted results | Studies |", "|---|---:|"])
    for val, n in included["has_results"].value_counts().items():
        lines.append(f"| {val} | {n} |")
    lines.append("")

    if "phases" in included.columns:
        lines.extend(["### `phases` (non-empty)", "", "| Phase | Studies |", "|---|---:|"])
        phase_nonempty = included[included["phases"].fillna("").astype(str).str.len() > 0]
        for phase, n in phase_nonempty["phases"].value_counts().head(12).items():
            lines.append(f"| {phase} | {n} |")
        lines.append(f"| (empty) | {len(included) - len(phase_nonempty)} |")
        lines.append("")

    if "study_first_post_date" in included.columns:
        years = (
            included["study_first_post_date"]
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

    lines.extend(
        [
            "## Notes for analysis",
            "",
            "- Outcome categories are descriptive; see `outcome_category_review_flag` and `reports/exploration/revised_cohort/outcome_other_category_review.md`.",
            "- `primary_outcome_mechanistic` stratifies studies whose registered primaries are all mechanistic by lexicon.",
            "- Condition flags overlap; define primary condition explicitly for stratified analyses.",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_pipe_field(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]
