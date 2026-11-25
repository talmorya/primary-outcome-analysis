"""Data preparation for the outcome analysis notebook (analysis/outcome_analysis.ipynb).

Reads the two analytic tables (data/processed/studies.csv, primary_outcomes.csv), adds a few
derived columns that are handy for plotting and for filtering, and builds the intervention x
outcome cross-tabs. Nothing here changes the analytic tables.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

from .category_mapping_report import INTERVENTION_CONFIG, OUTCOME_ORDER
from .config_loader import WORKSPACE_ROOT, load_yaml

PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
ANALYSIS_DIR = WORKSPACE_ROOT / "analysis"
FIGURES_DIR = ANALYSIS_DIR / "figures"
TABLES_DIR = ANALYSIS_DIR / "tables"

CONDITION_LABELS = {
    "back_pain": "Back pain",
    "fibromyalgia": "Fibromyalgia",
    "migraine": "Migraine",
    "headache": "Headache (other types)",
}
EXCLUSION_STRATUM = {
    "condition": "Condition eligibility",
    "acute": "Pain-character eligibility",
}
PERIOD_BINS = [0, 2009, 2014, 2019, 3000]
PERIOD_LABELS = ["up to 2009", "2010-2014", "2015-2019", "2020-2026"]
CROSSTAB_DROP_SUBCATEGORIES = ("not_an_outcome_measure",)
SHORT_LABELS = {
    "psychological_cognitive": "Psychological & cognitive",
    "neuroplastic_recovery_therapy": "Neuroplastic recovery",
    "mind_body_integrative": "Mind-body & integrative",
    "education_self_management": "Education & self-mgmt",
    "physical_rehabilitation": "Physical rehabilitation",
    "occupational_ergonomics_rtw": "Occupational / RTW",
    "multidisciplinary_interdisciplinary": "Multidisciplinary",
    "experimental_research_paradigm": "Experimental paradigm",
    "digital_health_delivery": "Digital health",
    "other_behavioral_treatment": "Other behavioral",
}


def condition_labels(columns=None) -> dict[str, str]:
    """Condition key -> label: the four main conditions plus any extra target of the active configuration."""
    labels = dict(CONDITION_LABELS)
    targets = load_yaml("condition_patterns_cohort.yaml").get("targets", {})
    for key, spec in targets.items():
        if key not in labels and (columns is None or f"eligible_{key}" in columns):
            labels[key] = spec.get("label", key)
    return labels


def _split(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def intervention_labels() -> dict[str, str]:
    config = load_yaml(INTERVENTION_CONFIG)
    labels = {key: spec.get("label", key) for key, spec in config["categories"].items()}
    labels["other_behavioral_treatment"] = "Other behavioral treatment"
    return labels


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (studies, outcomes) with derived columns added (see the notebook for the list)."""
    studies = pd.read_csv(PROCESSED_DIR / "studies.csv")
    outcomes = pd.read_csv(PROCESSED_DIR / "primary_outcomes.csv")
    return add_derived_columns(studies, outcomes), outcomes


def add_derived_columns(studies: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    studies = studies.copy()
    studies["first_post_year"] = pd.to_datetime(studies["raw_study_first_post_date"], errors="coerce").dt.year
    studies["period"] = pd.cut(studies["first_post_year"], bins=PERIOD_BINS, labels=PERIOD_LABELS).astype(object)

    studies["intervention_list"] = studies["intervention_categories"].apply(_split)
    studies["n_intervention_categories"] = studies["intervention_list"].str.len()
    for cat in intervention_labels():
        studies[f"has_{cat}"] = studies["intervention_list"].apply(lambda cats, c=cat: c in cats)

    cond_labels = condition_labels(studies.columns)
    studies["condition_list"] = studies.apply(
        lambda row: [label for key, label in cond_labels.items() if row[f"eligible_{key}"]], axis=1
    )
    studies["n_conditions"] = studies["condition_list"].str.len()

    studies["exclusion_rule"] = studies["exclusion_detail"].str.split(":").str[0]
    studies["exclusion_stratum"] = studies["exclusion_reason"].map(EXCLUSION_STRATUM)

    counts = outcomes.groupby("nct_id").size()
    studies["n_primary_outcomes"] = studies["nct_id"].map(counts).fillna(0).astype(int)
    return studies


def included(studies: pd.DataFrame) -> pd.DataFrame:
    return studies[studies["cohort_inclusion_status"] == "included"]


def cohort_summary_table(studies: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    inc = included(studies)
    inc_outcomes = outcomes[outcomes["cohort_inclusion_status"] == "included"]
    with_outcomes = inc[inc["n_primary_outcomes"] > 0]
    n_inc = len(inc)
    multi = int((with_outcomes["n_primary_outcomes"] > 1).sum())
    multimodal = int(inc["is_multimodal"].astype(bool).sum())
    rows = [
        ("Master pool (before filtering)", f"{len(studies):,}", "all trials retrieved from CT.gov"),
        ("Final analytic cohort", f"{n_inc:,}", f"{n_inc / len(studies):.1%} of the pool"),
        ("Excluded", f"{len(studies) - n_inc:,}", f"{(len(studies) - n_inc) / len(studies):.1%} of the pool"),
        ("Primary outcome rows (included trials)", f"{len(inc_outcomes):,}", "one row per registered primary outcome"),
        (
            "Studies with more than one primary outcome",
            f"{multi:,}",
            f"{multi / len(with_outcomes):.1%} of the {len(with_outcomes)} included trials with a registered primary outcome",
        ),
        (
            "Mean primary outcomes per study",
            f"{len(inc_outcomes) / len(with_outcomes):.2f}",
            f"over the {len(with_outcomes)} included trials with a registered primary outcome",
        ),
        ("Multimodal intervention trials", f"{multimodal:,}", f"{multimodal / n_inc:.1%} of included (behavioral + an active non-behavioral arm)"),
        (
            "Included trials with no registered primary outcome",
            f"{n_inc - len(with_outcomes):,}",
            "no row in primary_outcomes.csv",
        ),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value", "Note"])


@dataclass
class CrossTab:
    rows: pd.DataFrame  # group x outcome category: number of outcome rows
    trials: pd.DataFrame  # group x outcome category: number of trials with >= 1 such outcome
    n_trials: pd.Series  # trials per group (with >= 1 outcome after filtering)
    n_rows: pd.Series  # outcome rows per group
    n_trials_total: int
    n_rows_total: int

    def row_percent(self) -> pd.DataFrame:
        """Share of each group's outcome rows that fall in each outcome category (rows sum to 100)."""
        return self.rows.div(self.rows.sum(axis=1), axis=0) * 100

    def trial_percent(self) -> pd.DataFrame:
        """Share of each group's trials that registered at least one outcome of the category."""
        return self.trials.div(self.n_trials, axis=0) * 100


def outcome_by_group(
    studies: pd.DataFrame,
    outcomes: pd.DataFrame,
    *,
    group: str = "intervention_list",
    labels: dict[str, str] | None = None,
    study_query: str | None = None,
    outcome_query: str | None = None,
    drop_subcategories: tuple[str, ...] = CROSSTAB_DROP_SUBCATEGORIES,
) -> CrossTab:
    """Cross-tab of a list-valued study column (intervention categories, conditions) by outcome category.

    Included trials only. A trial with several groups contributes its outcomes to each group.
    `study_query` filters trials (pandas query on `studies` columns, e.g. "is_multimodal == False");
    `outcome_query` filters outcome rows (pandas query on `outcomes` columns).
    """
    inc = included(studies)
    if study_query:
        inc = inc.query(study_query)
    sub = outcomes[outcomes["cohort_inclusion_status"] == "included"]
    sub = sub[sub["nct_id"].isin(inc["nct_id"]) & ~sub["outcome_subcategory"].isin(drop_subcategories)]
    if outcome_query:
        sub = sub.query(outcome_query)

    merged = sub.merge(inc[["nct_id", group]], on="nct_id").explode(group).dropna(subset=[group])
    columns = [c for c in OUTCOME_ORDER if c in set(merged["outcome_category"])]
    rows = pd.crosstab(merged[group], merged["outcome_category"]).reindex(columns=columns, fill_value=0)
    per_trial = merged.drop_duplicates(["nct_id", group, "outcome_category"])
    trials = pd.crosstab(per_trial[group], per_trial["outcome_category"]).reindex(columns=columns, fill_value=0)
    n_trials = merged.drop_duplicates(["nct_id", group]).groupby(group).size()

    order = n_trials.sort_values(ascending=False).index
    rows, trials, n_trials = rows.reindex(order), trials.reindex(order), n_trials.reindex(order)
    n_rows = rows.sum(axis=1)
    if labels:
        rename = lambda idx: [labels.get(key, key) for key in idx]  # noqa: E731
        rows.index, trials.index, n_trials.index, n_rows.index = (rename(x.index) for x in (rows, trials, n_trials, n_rows))
    return CrossTab(rows, trials, n_trials, n_rows, int(merged["nct_id"].nunique()), len(sub))


def intervention_keys_by_size(studies: pd.DataFrame) -> list[str]:
    """Intervention category keys present among included trials, most frequent first."""
    inc = included(studies)
    sizes = {key: int(inc[f"has_{key}"].sum()) for key in intervention_labels()}
    return [key for key, n in sorted(sizes.items(), key=lambda kv: -kv[1]) if n > 0]


def cooccurrence(studies: pd.DataFrame) -> pd.DataFrame:
    """Matrix [A, B] = number of included trials carrying both category A and category B (diagonal = trials with A)."""
    inc = included(studies)
    keys = intervention_keys_by_size(studies)
    data = {b: {a: int((inc[f"has_{a}"] & inc[f"has_{b}"]).sum()) for a in keys} for b in keys}
    return pd.DataFrame(data).loc[keys, keys]


def companions(studies: pd.DataFrame, category: str) -> tuple[int, pd.Series]:
    """Trials carrying `category`, and how many of them also carry each other category.

    The first entry of the series, "(none: only this category)", counts trials with no other category.
    """
    inc = included(studies)
    inc = inc[inc[f"has_{category}"]]
    counts = {"(none: only this category)": int((inc["n_intervention_categories"] == 1).sum())}
    for key in intervention_keys_by_size(studies):
        if key != category:
            counts[key] = int(inc[f"has_{key}"].sum())
    series = pd.Series(counts)
    return len(inc), pd.concat([series.iloc[:1], series.iloc[1:].sort_values(ascending=False)])


def companion_outcome_table(
    studies: pd.DataFrame,
    outcomes: pd.DataFrame,
    category: str,
    outcome_categories: tuple[str, ...] = ("pain_interference", "pain_recovery"),
    *,
    min_n: int = 10,
) -> pd.DataFrame:
    """For trials carrying `category`: how many register at least one outcome of each given outcome category,
    overall by companion group (only this category / with any other / with each other category; groups overlap).
    Only trials with at least one primary outcome (excluding `not_an_outcome_measure`) are counted.
    """
    inc = included(studies)
    inc = inc[inc[f"has_{category}"]]
    sub = outcomes[(outcomes["cohort_inclusion_status"] == "included") & ~outcomes["outcome_subcategory"].isin(CROSSTAB_DROP_SUBCATEGORIES)]
    registered = sub.groupby("nct_id")["outcome_category"].agg(set)
    inc = inc[inc["nct_id"].isin(registered.index)].copy()
    for oc in outcome_categories:
        inc[oc] = inc["nct_id"].map(lambda nct, c=oc: c in registered[nct])
    groups = [
        ("only_this_category", inc["n_intervention_categories"] == 1),
        ("with_any_other_category", inc["n_intervention_categories"] > 1),
    ]
    groups += [(key, inc[f"has_{key}"]) for key in intervention_keys_by_size(studies) if key != category and inc[f"has_{key}"].sum() >= min_n]
    rows = [{"group": name, "n": int(mask.sum()), **{oc: int(inc.loc[mask, oc].sum()) for oc in outcome_categories}} for name, mask in groups if mask.sum() > 0]
    return pd.DataFrame(rows)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson confidence interval (in %) for k successes out of n."""
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return 100 * (centre - half), 100 * (centre + half)


def fisher_exact_two_sided(k1: int, n1: int, k2: int, n2: int) -> float:
    """Two-sided Fisher exact p-value for k1/n1 versus k2/n2 (no scipy needed)."""
    total, successes = n1 + n2, k1 + k2
    denom = math.comb(total, n1)

    def prob(x: int) -> float:
        return math.comb(successes, x) * math.comb(total - successes, n1 - x) / denom

    observed = prob(k1)
    low, high = max(0, n1 - (total - successes)), min(n1, successes)
    return min(1.0, sum(p for x in range(low, high + 1) if (p := prob(x)) <= observed * (1 + 1e-9)))
