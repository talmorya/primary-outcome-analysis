"""Figures for the outcome analysis notebook. Each function returns a matplotlib Figure."""

from __future__ import annotations

from collections import Counter

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch

from .analysis_data import (
    CONDITION_LABELS,
    CROSSTAB_DROP_SUBCATEGORIES,
    FIGURES_DIR,
    PERIOD_LABELS,
    SHORT_LABELS,
    TABLES_DIR,
    CrossTab,
    companion_outcome_table,
    companions,
    cooccurrence,
    included,
    intervention_keys_by_size,
)
from .category_mapping_report import OUTCOME_ORDER

INCLUDED_COLOR = "#2b6cb0"
EXCLUDED_COLOR = "#cfd4da"
STRATUM_COLORS = {"Condition eligibility": "#2b6cb0", "Pain-character eligibility": "#dd8452"}
OUTCOME_COLORS = dict(zip(OUTCOME_ORDER, sns.color_palette("tab10", len(OUTCOME_ORDER))))
RULE_LABELS = {
    "cancer_oncology": "Cancer / oncology",
    "pathology_other": "Other pathology (e.g. fracture, infection)",
    "pregnancy_related": "Pregnancy-related pain",
    "no_target_match": "No target condition registered",
    "not_about_pain": "Not about pain (no pain wording)",
    "acute_pain": "Acute pain population",
    "short_pain_window": "Pain duration of 11 weeks or less",
    "subacute_perioperative": "Subacute / perioperative population",
}


def set_style() -> None:
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.0)
    plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 300, "axes.spines.top": False, "axes.spines.right": False})


def save_figure(fig: plt.Figure, name: str) -> None:
    """Write the figure as PNG (300 dpi) and PDF (vector) into analysis/figures/."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.png", bbox_inches="tight")
    fig.savefig(FIGURES_DIR / f"{name}.pdf", bbox_inches="tight")


def save_table(table: pd.DataFrame, name: str, *, index: bool = True) -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / f"{name}.csv", index=index)


def _share(fraction: float) -> str:
    return "<1%" if 0 < fraction < 0.005 else f"{fraction:.0%}"


def _bar_labels(ax: plt.Axes, values, total: float | None = None, *, pad: float = 0.01) -> None:
    """Write the count (and share of `total`) at the end of horizontal bars."""
    xmax = ax.get_xlim()[1]
    for y, value in enumerate(values):
        text = f"{value}" if total is None else f"{value}  ({_share(value / total)})"
        ax.text(value + xmax * pad, y, text, va="center", fontsize=9)
    ax.set_xlim(0, xmax * 1.18)


# 1 -----------------------------------------------------------------------------------------
def plot_trials_by_year(studies: pd.DataFrame) -> plt.Figure:
    counts = studies.groupby(["first_post_year", "cohort_inclusion_status"]).size().unstack(fill_value=0)
    counts = counts.reindex(range(int(counts.index.min()), int(counts.index.max()) + 1), fill_value=0)
    counts = counts.reindex(columns=["included", "excluded"], fill_value=0)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(counts.index, counts["included"], color=INCLUDED_COLOR, label=f"Included (n={counts['included'].sum()})")
    ax.bar(
        counts.index, counts["excluded"], bottom=counts["included"], color=EXCLUDED_COLOR,
        label=f"Excluded (n={counts['excluded'].sum()})",
    )
    for year, row in counts.iterrows():
        if row["included"]:
            ax.text(year, row["included"] + row["excluded"] + 1, int(row["included"]), ha="center", fontsize=8, color=INCLUDED_COLOR)
    ax.set_xticks(counts.index)
    ax.set_xticklabels(counts.index, rotation=90)
    ax.set_xlabel(
        "Year the trial was first posted on ClinicalTrials.gov\n"
        "(numbers above bars = included trials; the latest year is partial, up to the extraction date)"
    )
    ax.set_ylabel("Number of trials")
    ax.set_title("Behavioral chronic-pain trials by first-post year")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="x", visible=False)
    return fig


# 3 -----------------------------------------------------------------------------------------
def plot_exclusion_reasons(studies: pd.DataFrame) -> plt.Figure:
    excluded = studies[studies["cohort_inclusion_status"] == "excluded"]
    counts = excluded.groupby(["exclusion_stratum", "exclusion_rule"]).size().reset_index(name="n")
    total = int(counts["n"].sum())

    labels, values, colors, positions, y = [], [], [], [], 0.0
    for stratum in STRATUM_COLORS:
        part = counts[counts["exclusion_stratum"] == stratum].sort_values("n", ascending=False)
        if part.empty:
            continue
        for row in part.itertuples():
            labels.append(RULE_LABELS.get(row.exclusion_rule, row.exclusion_rule))
            values.append(row.n)
            colors.append(STRATUM_COLORS[stratum])
            positions.append(y)
            y += 1
        y += 0.6  # gap between the two strata

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.barh(positions, values, color=colors)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    xmax = max(values)
    for pos, value in zip(positions, values):
        ax.text(value + xmax * 0.01, pos, f"{value}  ({_share(value / total)})", va="center", fontsize=9)
    ax.set_xlim(0, xmax * 1.2)
    ax.set_xlabel("Excluded trials (first matching rule)")
    ax.set_title(f"Why trials were excluded (n={total})")
    ax.legend(handles=[Patch(color=c, label=s) for s, c in STRATUM_COLORS.items()], frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    return fig


# 4 -----------------------------------------------------------------------------------------
def plot_conditions(studies: pd.DataFrame) -> plt.Figure:
    inc = included(studies)
    per_condition = Counter(label for labels in inc["condition_list"] for label in labels)
    per_condition = pd.Series(per_condition).reindex(list(CONDITION_LABELS.values())).fillna(0).astype(int).sort_values()
    combos = inc["condition_list"].apply(lambda labels: " + ".join(labels) if labels else "None").value_counts().sort_values()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
    ax1.barh(per_condition.index, per_condition.values, color=INCLUDED_COLOR)
    _bar_labels(ax1, per_condition.values, len(inc))
    ax1.set_title("Trials per registered condition\n(a trial listing several conditions counts in each)")
    ax1.set_xlabel(f"Trials (of {len(inc)} included)")
    ax2.barh(combos.index, combos.values, color="#6b8fb5")
    _bar_labels(ax2, combos.values, len(inc))
    ax2.set_title("Trials by exact combination of conditions\n(each trial counted once)")
    ax2.set_xlabel("Trials")
    for ax in (ax1, ax2):
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


# 5 -----------------------------------------------------------------------------------------
def plot_interventions(studies: pd.DataFrame, labels: dict[str, str], *, top_combinations: int = 15) -> plt.Figure:
    inc = included(studies)
    exploded = inc[["nct_id", "intervention_list", "is_multimodal"]].explode("intervention_list").dropna(subset=["intervention_list"])
    exploded["category"] = exploded["intervention_list"].map(labels)
    table = exploded.groupby(["category", "is_multimodal"]).size().unstack(fill_value=0).reindex(columns=[False, True], fill_value=0)
    table = table.loc[table.sum(axis=1).sort_values().index]
    combos = (
        inc["intervention_list"]
        .apply(lambda cats: " + ".join(labels.get(c, c) for c in cats) if cats else "No category")
        .value_counts()
        .head(top_combinations)
        .sort_values()
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.2), gridspec_kw={"width_ratios": [1, 1.35]})
    ax1.barh(table.index, table[False], color=INCLUDED_COLOR, label="Behavioral arms only")
    ax1.barh(table.index, table[True], left=table[False], color="#e0a458", label="Plus an active non-behavioral arm")
    totals = table.sum(axis=1)
    xmax = totals.max()
    for y, total in enumerate(totals):
        ax1.text(total + xmax * 0.01, y, f"{total}  ({_share(total / len(inc))})", va="center", fontsize=9)
    ax1.set_xlim(0, xmax * 1.2)
    ax1.set_title("Trials per intervention category\n(a trial can carry several categories)")
    ax1.set_xlabel(f"Trials (of {len(inc)} included)")
    ax1.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=9)  # below the axes: never covers a bar
    ax2.barh(combos.index, combos.values, color="#6b8fb5")
    _bar_labels(ax2, combos.values, len(inc))
    ax2.set_title(f"Most common exact combinations (top {top_combinations}; each trial counted once)")
    ax2.set_xlabel("Trials")
    for ax in (ax1, ax2):
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


# 6 -----------------------------------------------------------------------------------------
def plot_crosstab(ct: CrossTab, *, group_name: str = "Intervention category", title: str = "", min_n_warn: int = 10) -> plt.Figure:
    """Two heatmaps: where each group's outcome rows go (left) and how many of its trials register each outcome (right)."""
    row_pct, trial_pct = ct.row_percent(), ct.trial_percent()
    height = max(3.5, 0.62 * len(row_pct) + 2.2)
    fig, axes = plt.subplots(1, 2, figsize=(17, height), sharey=True)
    y_labels = [
        f"{name}  (n={ct.n_trials[name]} trials, {ct.n_rows[name]} outcomes)" + ("  *" if ct.n_trials[name] < min_n_warn else "")
        for name in row_pct.index
    ]
    panels = [
        (axes[0], row_pct, "Share of the group's primary outcomes (%)\nrows sum to 100%", "Blues"),
        (axes[1], trial_pct, "Share of the group's trials with at least one\noutcome of that category (%); columns do not sum to 100%", "Oranges"),
    ]
    for ax, data, subtitle, cmap in panels:
        sns.heatmap(data, annot=True, fmt=".0f", cmap=cmap, vmin=0, vmax=max(float(data.max().max()), 1), cbar=False,
                    linewidths=0.5, linecolor="white", ax=ax, annot_kws={"fontsize": 9})
        ax.set_title(subtitle, fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_xticklabels([c.replace("_", " ") for c in data.columns], rotation=35, ha="right")
    axes[0].set_yticklabels(y_labels, rotation=0)
    suptitle = title or f"{group_name} x primary outcome category"
    fig.suptitle(f"{suptitle}\n{ct.n_trials_total} trials, {ct.n_rows_total} primary outcomes", fontsize=12, y=1.02)
    if (ct.n_trials < min_n_warn).any():
        fig.text(0.01, -0.02, f"* fewer than {min_n_warn} trials: percentages are unstable.", fontsize=8, color="gray")
    fig.tight_layout()
    return fig


# Additional ---------------------------------------------------------------------------------
def plot_outcome_overview(outcomes: pd.DataFrame, *, top_sub: int = 18) -> plt.Figure:
    inc = outcomes[outcomes["cohort_inclusion_status"] == "included"]
    inc = inc[~inc["outcome_subcategory"].isin(CROSSTAB_DROP_SUBCATEGORIES)]
    cat = inc.groupby("outcome_category").size().reindex(OUTCOME_ORDER).dropna().astype(int).sort_values()
    sub = inc.groupby(["outcome_category", "outcome_subcategory"]).size().reset_index(name="n").sort_values("n", ascending=False).head(top_sub)
    sub = sub.sort_values("n")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1, 1.2]})
    ax1.barh([c.replace("_", " ") for c in cat.index], cat.values, color=[OUTCOME_COLORS[c] for c in cat.index])
    _bar_labels(ax1, cat.values, len(inc))
    ax1.set_title(f"Primary outcomes by category (n={len(inc)} rows)")
    ax2.barh(sub["outcome_subcategory"].str.replace("_", " "), sub["n"], color=[OUTCOME_COLORS[c] for c in sub["outcome_category"]])
    _bar_labels(ax2, sub["n"].values)
    ax2.set_title(f"Most frequent subcategories (top {top_sub}; colour = category)")
    for ax in (ax1, ax2):
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def plot_outcomes_over_time(studies: pd.DataFrame, outcomes: pd.DataFrame) -> plt.Figure:
    inc = outcomes[(outcomes["cohort_inclusion_status"] == "included") & ~outcomes["outcome_subcategory"].isin(CROSSTAB_DROP_SUBCATEGORIES)]
    merged = inc.merge(studies[["nct_id", "period"]], on="nct_id")
    counts = pd.crosstab(merged["period"], merged["outcome_category"]).reindex(PERIOD_LABELS).reindex(columns=OUTCOME_ORDER, fill_value=0)
    share = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 4.8))
    bottom = pd.Series(0.0, index=share.index)
    for cat in share.columns:
        ax.bar(share.index, share[cat], bottom=bottom, color=OUTCOME_COLORS[cat], label=cat.replace("_", " "), width=0.7)
        for x, (v, b) in enumerate(zip(share[cat], bottom)):
            if v >= 5:
                ax.text(x, b + v / 2, f"{v:.0f}", ha="center", va="center", fontsize=8, color="white")
        bottom += share[cat]
    ax.set_xticks(range(len(share.index)))
    ax.set_xticklabels([f"{p}\n(n={int(counts.loc[p].sum())})" for p in share.index])
    ax.set_ylabel("% of primary outcomes registered")
    ax.set_xlabel("Period the trial was first posted")
    ax.set_title("Primary outcome categories over time")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", frameon=False)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def plot_interventions_over_time(studies: pd.DataFrame, labels: dict[str, str]) -> plt.Figure:
    inc = included(studies).dropna(subset=["period"])
    n = inc.groupby("period").size().reindex(PERIOD_LABELS)
    exploded = inc[["nct_id", "period", "intervention_list"]].explode("intervention_list").dropna(subset=["intervention_list"])
    share = pd.crosstab(exploded["intervention_list"], exploded["period"]).reindex(columns=PERIOD_LABELS, fill_value=0)
    share = share.div(n, axis=1) * 100
    share = share.loc[share.mean(axis=1).sort_values(ascending=False).index]
    share.index = [labels.get(i, i) for i in share.index]

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(share, annot=True, fmt=".0f", cmap="Blues", cbar=False, linewidths=0.5, linecolor="white", ax=ax)
    ax.set_xticklabels([f"{p}\n(n={int(n[p])} trials)" for p in PERIOD_LABELS], rotation=0)
    ax.set_xlabel("Period the trial was first posted")
    ax.set_ylabel("")
    ax.set_title("Intervention categories over time\n(% of the period's included trials; a trial can carry several categories)")
    fig.tight_layout()
    return fig


def plot_top_instruments(outcomes: pd.DataFrame, *, top: int = 15) -> plt.Figure:
    inc = outcomes[outcomes["cohort_inclusion_status"] == "included"]
    names = Counter(
        name.strip()
        for value in inc["instruments_detected"].dropna()
        for name in str(value).split("|")
        if name.strip()
    )
    series = pd.Series(names).sort_values(ascending=False).head(top).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(series.index, series.values, color=INCLUDED_COLOR)
    _bar_labels(ax, series.values)
    ax.set_title(f"Most frequently detected instruments in primary outcomes (top {top})")
    ax.set_xlabel("Primary outcome rows mentioning the instrument")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def plot_outcomes_per_trial(studies: pd.DataFrame, *, cap: int = 8) -> plt.Figure:
    inc = included(studies)
    n = inc.loc[inc["n_primary_outcomes"] > 0, "n_primary_outcomes"].clip(upper=cap)
    counts = n.value_counts().reindex(range(1, cap + 1), fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(counts.index, counts.values, color=INCLUDED_COLOR)
    for x, v in zip(counts.index, counts.values):
        ax.text(x, v + counts.max() * 0.01, int(v), ha="center", fontsize=9)
    ax.set_xticks(counts.index)
    ax.set_xticklabels([str(i) if i < cap else f"{cap}+" for i in counts.index])
    ax.set_xlabel("Registered primary outcomes per trial")
    ax.set_ylabel("Trials")
    ax.set_title("How many primary outcomes do trials register?")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


# Which intervention categories appear together ------------------------------------------------
def plot_cooccurrence(studies: pd.DataFrame) -> plt.Figure:
    """Heatmap: of the trials with the ROW category, the % that also carry the COLUMN category (n in brackets)."""
    counts = cooccurrence(studies)
    sizes = pd.Series(np.diag(counts.values), index=counts.index)
    pct = counts.div(sizes, axis=0) * 100
    annot = pct.round(0).astype(int).astype(str) + "%\n(" + counts.astype(str) + ")"
    mask = np.eye(len(counts), dtype=bool)
    names = [SHORT_LABELS.get(k, k) for k in counts.index]
    fig, ax = plt.subplots(figsize=(10.5, 7.2))
    sns.heatmap(pct, mask=mask, annot=annot, fmt="", cmap="Purples", vmin=0, vmax=60, cbar=False,
                linewidths=0.5, linecolor="white", ax=ax, annot_kws={"fontsize": 8.5})
    ax.grid(False)
    ax.set_xticklabels(names, rotation=40, ha="right")
    ax.set_yticklabels([f"{name}  (n={sizes[k]})" for name, k in zip(names, counts.index)], rotation=0)
    ax.set_xlabel("... also carry this category")
    ax.set_ylabel("Of the trials with this category ...")
    ax.set_title("How intervention categories co-occur\n(% of the row category's trials that also carry the column category; read along rows)")
    fig.tight_layout()
    return fig


def plot_upset(studies: pd.DataFrame, *, top: int = 16) -> plt.Figure:
    """UpSet-style plot: bars = trials with exactly that combination; dots = the categories in it."""
    inc = included(studies)
    keys = intervention_keys_by_size(studies)
    combos = pd.Series(
        [tuple(k for k in keys if row[f"has_{k}"]) for _, row in inc.iterrows()]
    ).value_counts()
    combos = combos[[len(c) > 0 for c in combos.index]].head(top)
    n_sets, n_combos = len(keys), len(combos)

    fig = plt.figure(figsize=(0.6 * n_combos + 3.2, 7.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.3, 1.5], hspace=0.03)
    ax_bar = fig.add_subplot(gs[0])
    ax_mat = fig.add_subplot(gs[1], sharex=ax_bar)

    x = np.arange(n_combos)
    ax_bar.bar(x, combos.values, color=INCLUDED_COLOR, width=0.62)
    for xi, value in zip(x, combos.values):
        ax_bar.text(xi, value + combos.max() * 0.01, int(value), ha="center", fontsize=9)
    ax_bar.set_ylabel("Trials with exactly\nthis combination")
    ax_bar.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_bar.grid(axis="x", visible=False)
    ax_bar.set_title(f"Most common combinations of intervention categories (top {n_combos} of {inc['intervention_list'].apply(tuple).nunique()}; each trial counted once)")

    for y in range(n_sets):
        if y % 2 == 0:
            ax_mat.axhspan(y - 0.5, y + 0.5, color="#f1f3f5", zorder=0)
    for xi, combo in zip(x, combos.index):
        members = [keys.index(k) for k in combo]
        ax_mat.scatter([xi] * n_sets, range(n_sets), s=55, color="#d0d4d9", zorder=1)
        ax_mat.scatter([xi] * len(members), members, s=75, color=INCLUDED_COLOR, zorder=3)
        if len(members) > 1:
            ax_mat.plot([xi, xi], [min(members), max(members)], color=INCLUDED_COLOR, linewidth=2.2, zorder=2)
    sizes = [int(inc[f"has_{k}"].sum()) for k in keys]
    ax_mat.set_yticks(range(n_sets))
    ax_mat.set_yticklabels([f"{SHORT_LABELS.get(k, k)}  (n={n})" for k, n in zip(keys, sizes)])
    ax_mat.set_ylim(n_sets - 0.5, -0.5)
    ax_mat.set_xlim(-0.6, n_combos - 0.4)
    ax_mat.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_mat.grid(False)
    for side in ("left", "bottom"):
        ax_mat.spines[side].set_visible(False)
    return fig


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return 100 * (centre - half), 100 * (centre + half)


def plot_companions(
    studies: pd.DataFrame,
    outcomes: pd.DataFrame,
    category: str,
    labels: dict[str, str],
    *,
    outcome_categories: tuple[str, ...] = ("pain_interference", "pain_recovery"),
    min_n: int = 10,
) -> plt.Figure:
    """Left: which other categories accompany `category`. Right: do the outcomes it registers depend on the companion?"""
    n_total, comp = companions(studies, category)
    table = companion_outcome_table(studies, outcomes, category, outcome_categories, min_n=min_n)
    name = labels.get(category, category)

    def pretty_group(group: str) -> str:
        if group == "only_this_category":
            return "Only this category"
        if group == "with_any_other_category":
            return "With any other category"
        return "With " + SHORT_LABELS.get(group, group)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.4), gridspec_kw={"width_ratios": [1, 1.25]})
    ordered = comp.iloc[::-1]
    names = ["None (only this category)" if k.startswith("(none") else SHORT_LABELS.get(k, k) for k in ordered.index]
    colors = ["#e0a458" if k.startswith("(none") else INCLUDED_COLOR for k in ordered.index]
    ax1.barh(names, ordered.values, color=colors)
    _bar_labels(ax1, ordered.values, n_total)
    ax1.set_title(f"What else do {name} trials carry? (n={n_total} trials)\n(a trial can carry several; orange = this category alone)")
    ax1.set_xlabel("Trials")
    ax1.grid(axis="y", visible=False)

    rows = table.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(rows))
    height = 0.8 / len(outcome_categories)
    for i, oc in enumerate(outcome_categories):
        pct = 100 * rows[oc] / rows["n"]
        ci = np.array([_wilson(k, n) for k, n in zip(rows[oc], rows["n"])])
        pos = y + (i - (len(outcome_categories) - 1) / 2) * height
        ax2.barh(pos, pct, height=height * 0.92, color=OUTCOME_COLORS[oc], label=f"at least one {oc.replace('_', ' ')} outcome")
        ax2.errorbar(pct, pos, xerr=[pct - ci[:, 0], ci[:, 1] - pct], fmt="none", ecolor="#333333", elinewidth=1, capsize=2)
    ax2.set_yticks(y)
    ax2.set_yticklabels([f"{pretty_group(g)}  (n={n})" for g, n in zip(rows["group"], rows["n"])])
    ax2.set_xlim(0, 105)
    ax2.set_xlabel("% of the group's trials (whiskers: 95% confidence interval)")
    ax2.set_title("Outcomes registered, by what the trial is combined with\n(groups overlap; groups under %d trials not shown)" % min_n)
    ax2.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=9)
    ax2.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig
