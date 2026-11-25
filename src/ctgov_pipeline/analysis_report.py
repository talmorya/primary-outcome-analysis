"""Write analysis/results_summary.md: the headline results of the analysis notebook in prose, tables and figure links.

Every number is recomputed from data/processed/ on each run (nothing is typed in by hand), so the summary
always matches the current cohort. Called by `run_analysis_notebook` after the notebook has re-created the
figures; can also be run alone:
    PYTHONPATH=src python -m ctgov_pipeline.analysis_report
"""

from __future__ import annotations

import json
from collections import Counter

import pandas as pd

from . import analysis_data as ad
from .analysis_data import ANALYSIS_DIR, PERIOD_LABELS, PROCESSED_DIR, SHORT_LABELS, included
from .category_mapping_report import OUTCOME_ORDER

RESULTS_SUMMARY_MD = ANALYSIS_DIR / "results_summary.md"
FOCUS_CATEGORY = "psychological_cognitive"
FOCUS_OUTCOMES = ("pain_interference", "pain_recovery")
MIN_GROUP = 10  # groups smaller than this are not interpreted

SENSITIVITY_VERSIONS = [
    ("Full cohort", None, "fig06_intervention_x_outcome"),
    ("Behavioral arms only (no active non-behavioral arm)", "is_multimodal == False", "fig06_unimodal"),
    ("Single intervention category only (purity check)", "n_intervention_categories == 1", "fig06_single_category"),
]


# --- formatting helpers ----------------------------------------------------------------------
def _table(header: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def _pct(k: float, n: float, digits: int = 0) -> str:
    return f"{100 * k / n:.{digits}f}%" if n else "-"


def _pretty(key: str) -> str:
    return key.replace("_", " ")


def _p_value(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def _fig(name: str, caption: str) -> str:
    return f"![{caption}](figures/{name}.png)\n\n*{caption}* (PDF: `figures/{name}.pdf`)"


def _range(values: list[float]) -> str:
    return f"{min(values):.0f}-{max(values):.0f}%"


# --- section 1: the Psychological & cognitive finding ---------------------------------------
def _focus_section(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    name = labels.get(FOCUS_CATEGORY, FOCUS_CATEGORY)
    interf, recov = FOCUS_OUTCOMES

    # 1a. the same category in the three versions of the cross-tab (trial share)
    version_rows, shares = [], {}
    for title, query, _ in SENSITIVITY_VERSIONS:
        ct = ad.outcome_by_group(studies, outcomes, labels=labels, study_query=query)
        if name not in ct.n_trials.index:
            continue
        n = int(ct.n_trials[name])
        trial_pct = ct.trial_percent().loc[name]
        shares[title] = (trial_pct.get(interf, 0.0), trial_pct.get(recov, 0.0), n)
        version_rows.append([title, n, f"{trial_pct.get(interf, 0):.0f}%", f"{trial_pct.get(recov, 0):.0f}%"])

    # 1b. alone versus combined, and by specific companion
    table = ad.companion_outcome_table(studies, outcomes, FOCUS_CATEGORY, FOCUS_OUTCOMES, min_n=MIN_GROUP)
    by_group = table.set_index("group")
    n_total, comp = ad.companions(studies, FOCUS_CATEGORY)
    n_alone_all = int(comp.iloc[0])

    def group_label(group: str) -> str:
        return {"only_this_category": "Only this category", "with_any_other_category": "Combined with any other category"}.get(
            group, "Combined with " + SHORT_LABELS.get(group, group)
        )

    def ci(k: int, n: int) -> str:
        lo, hi = ad.wilson_interval(k, n)
        return f"{_pct(k, n)} ({lo:.0f}-{hi:.0f}%)"

    group_rows = [[group_label(r.group), r.n, ci(getattr(r, interf), r.n), ci(getattr(r, recov), r.n)] for r in table.itertuples()]

    full = shares.get("Full cohort")
    single = shares.get("Single intervention category only (purity check)")
    unimodal = shares.get("Behavioral arms only (no active non-behavioral arm)")

    reversed_order = False
    if full and single:
        reversed_order = (full[0] > full[1]) and (single[0] < single[1])
    title = f"{name} flips direction depending on what it is combined with" if reversed_order else f"{name}: interference and recovery outcomes"
    out = [f"## 1. Main finding: {title}", ""]
    if full and single:
        reversed_order = (full[0] > full[1]) and (single[0] < single[1])
        lead = (
            f"In the full cohort, {name} trials register a pain-interference outcome more often than a pain-recovery outcome "
            f"({full[0]:.0f}% vs {full[1]:.0f}% of trials). "
            + (f"The same holds when trials with an active non-behavioral arm are removed ({unimodal[0]:.0f}% vs {unimodal[1]:.0f}%). " if unimodal else "")
            + f"In the single-category purity check the order **reverses**: pain recovery {single[1]:.0f}% vs pain interference {single[0]:.0f}% "
            f"(n={single[2]} trials)."
            if reversed_order
            else f"In the full cohort the shares are interference {full[0]:.0f}% and recovery {full[1]:.0f}% of the category's trials; "
            f"in the single-category purity check they are {single[0]:.0f}% and {single[1]:.0f}% (n={single[2]}). The order does not reverse in this run."
        )
        out += [lead, ""]
    out += [
        "**The same category in three versions of the intervention x outcome cross-tab** "
        "(share of the category's trials with at least one outcome of that type; a trial can have several):",
        "",
        _table(["Version", "Trials", "Pain interference", "Pain recovery"], version_rows),
        "",
        _fig("fig06_intervention_x_outcome", "Intervention category x outcome category, full cohort (left: share of outcomes; right: share of trials)"),
        "",
        _fig("fig06_single_category", "Same cross-tab restricted to trials with exactly one intervention category (purity check)"),
        "",
        "### What accompanies it",
        "",
    ]
    top_companions = [(k, v) for k, v in comp.items() if not k.startswith("(none")][:3]
    out += [
        f"{n_total} included trials carry {name}; only {n_alone_all} ({_pct(n_alone_all, n_total)}) carry it alone, so "
        f"{_pct(n_total - n_alone_all, n_total)} are combined with at least one other category. The most common companions are "
        + ", ".join(f"{SHORT_LABELS.get(k, k)} ({_pct(v, n_total)})" for k, v in top_companions)
        + ". Note that the 'behavioral arms only' version does not remove these combinations (it only removes trials that add a "
        "non-behavioral arm), which is why it looks like the full cohort.",
        "",
        _fig(f"fig15_companions_{FOCUS_CATEGORY}", f"Left: categories accompanying {name}. Right: outcomes registered by what the trial is combined with (95% CI)"),
        "",
        "### Alone versus combined",
        "",
        "Percent of the group's trials (with a registered primary outcome) that have at least one outcome of the type; 95% Wilson confidence interval in brackets. "
        "Companion groups overlap (a trial combined with two categories appears in both rows); the first two rows do not overlap.",
        "",
        _table(["Group", "Trials", "Pain interference", "Pain recovery"], group_rows),
        "",
    ]

    if {"only_this_category", "with_any_other_category"} <= set(by_group.index):
        a, c = by_group.loc["only_this_category"], by_group.loc["with_any_other_category"]
        p_rec = ad.fisher_exact_two_sided(int(a[recov]), int(a["n"]), int(c[recov]), int(c["n"]))
        p_int = ad.fisher_exact_two_sided(int(a[interf]), int(a["n"]), int(c[interf]), int(c["n"]))
        gap_rec = 100 * (a[recov] / a["n"] - c[recov] / c["n"])
        gap_int = 100 * (c[interf] / c["n"] - a[interf] / a["n"])
        lo, hi = ad.wilson_interval(int(a[recov]), int(a["n"]))
        out += [
            f"- **Pain recovery** is registered by {_pct(a[recov], a['n'])} of the {name} trials when it stands alone but {_pct(c[recov], c['n'])} "
            f"when it is combined ({gap_rec:+.0f} points alone vs combined; Fisher exact {_p_value(p_rec)}).",
            f"- **Pain interference** is {_pct(a[interf], a['n'])} alone and {_pct(c[interf], c['n'])} combined "
            f"({gap_int:+.0f} points combined vs alone; Fisher exact {_p_value(p_int)}).",
            "- The "
            + ("pain-recovery" if abs(gap_rec) >= abs(gap_int) else "pain-interference")
            + " shift is the larger of the two.",
        ]
        companion_rows = by_group.drop(index=["only_this_category", "with_any_other_category"], errors="ignore")
        if len(companion_rows):
            rec_shares = [100 * r[recov] / r["n"] for _, r in companion_rows.iterrows()]
            alone_rec = 100 * a[recov] / a["n"]
            consistent = all(s < alone_rec for s in rec_shares)
            out += [
                f"- Across the {len(companion_rows)} specific companion groups (at least {MIN_GROUP} trials) the pain-recovery share is {_range(rec_shares)}, "
                + (
                    "below the 'alone' value in every one of them: the drop goes with being combined at all, not with one particular partner."
                    if consistent
                    else "and not uniformly below the 'alone' value, so a single partner may matter."
                ),
            ]
        reading = (
            f"The opposite trends appear to stem from composition: most {name} trials are combined with other approaches, and the outcomes registered by combined trials "
            f"lean away from pain recovery. A possible reading, which these numbers only suggest, is that {name} on its own is more often aimed at recovering the patient "
            f"(pain intensity/severity), whereas inside a combined programme the outcomes follow the other components. "
            if reversed_order and gap_rec > 0
            else f"In this run the alone-versus-combined comparison does not show a clean reversal, so no composition effect is claimed. "
        )
        out += [
            "",
            "### Reading",
            "",
            reading
            + f"Limits: the 'alone' group is small (n={int(a['n'])}; its pain-recovery share has a 95% CI of {lo:.0f}-{hi:.0f}%), the comparison is exploratory "
            "(no correction for multiple comparisons), trials are not randomised to being combined or alone, and outcome categories are descriptive "
            "rule-based aids, not the researcher's manual coding.",
            "",
        ]
    out += ["", _condition_part(studies, outcomes, labels), "", _subtype_part(studies, outcomes, labels), ""]
    out += [_fig("fig13_cooccurrence_heatmap", "How intervention categories co-occur (row category: % of its trials that also carry the column category)")]
    return "\n".join(out)


def _ci_cell(k: int, n: int) -> str:
    if not n:
        return "-"
    lo, hi = ad.wilson_interval(k, n)
    return f"{100 * k / n:.0f}% ({lo:.0f}-{hi:.0f}%)"


def _condition_part(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    name = labels.get(FOCUS_CATEGORY, FOCUS_CATEGORY)
    interf, recov = FOCUS_OUTCOMES
    table = ad.condition_outcome_table(studies, outcomes, FOCUS_CATEGORY, (interf, recov, "mood"))
    group_names = {
        "all": f"{name}, all",
        "only_this_category": f"{name}, alone",
        "with_any_other_category": f"{name}, combined",
        "other_trials": "All other behavioral trials",
    }
    rows = [
        [r.condition, group_names[r.group], r.n, _ci_cell(getattr(r, interf), r.n), _ci_cell(getattr(r, recov), r.n), _pct(r.mood, r.n)]
        for r in table.itertuples()
    ]
    by = table.set_index(["condition", "group"])
    conditions = list(dict.fromkeys(table["condition"]))
    n_all = {c: int(by.loc[(c, "all"), "n"]) for c in conditions}
    out = [
        f"### {name} by registered condition",
        "",
        "Which conditions the category's trials belong to, and which outcomes they register in each (a trial with several conditions counts in each; "
        "trials with a registered primary outcome; the last group is the reference level of each condition):",
        "",
        "Trials: " + ", ".join(f"{c} {n}" for c, n in n_all.items()) + ".",
        "",
        _table(["Condition", "Group", "Trials", "Pain interference", "Pain recovery", "Mood"], rows),
        "",
    ]
    bullets = []
    for c in conditions:
        a, k = by.loc[(c, "only_this_category")], by.loc[(c, "with_any_other_category")]
        if a["n"] >= MIN_GROUP and k["n"] >= MIN_GROUP:
            p = ad.fisher_exact_two_sided(int(a[recov]), int(a["n"]), int(k[recov]), int(k["n"]))
            bullets.append(
                f"- **{c}**: pain recovery {_pct(a[recov], a['n'])} alone vs {_pct(k[recov], k['n'])} combined "
                f"({100 * (a[recov] / a['n'] - k[recov] / k['n']):+.0f} points, Fisher exact {_p_value(p)}); "
                f"pain interference {_pct(a[interf], a['n'])} vs {_pct(k[interf], k['n'])}."
            )
    small = [c for c in conditions if min(by.loc[(c, "only_this_category"), "n"], by.loc[(c, "with_any_other_category"), "n"]) < MIN_GROUP]
    if bullets:
        out += ["Alone versus combined within a condition (conditions where both groups have at least " + str(MIN_GROUP) + " trials):", ""] + bullets
    if small:
        out += ["", "Too few trials in the alone or combined group to compare: " + ", ".join(small) + "."]
    higher = []
    for c in conditions:
        a, ref = by.loc[(c, "all")], by.loc[(c, "other_trials")]
        if a["n"] >= MIN_GROUP and ref["n"] >= MIN_GROUP:
            higher.append((c, 100 * a[interf] / a["n"], 100 * ref[interf] / ref["n"], 100 * a[recov] / a["n"], 100 * ref[recov] / ref["n"]))
    if higher:
        n_up = sum(1 for _, i, ri, _, _ in higher if i > ri)
        out += [
            "",
            f"Compared with all other behavioral trials of the same condition, {name} trials register pain interference more often in {n_up} of {len(higher)} conditions ("
            + "; ".join(f"{c} {i:.0f}% vs {ri:.0f}%" for c, i, ri, _, _ in higher)
            + "); pain recovery: "
            + "; ".join(f"{c} {r:.0f}% vs {rr:.0f}%" for c, _, _, r, rr in higher)
            + ".",
        ]
    out += [
        "",
        "These are descriptive, exploratory comparisons (uncorrected p-values; small groups). Groups under "
        f"{MIN_GROUP} trials are not drawn in the figure.",
        "",
        _fig(f"fig16_condition_split_{FOCUS_CATEGORY}", f"{name}: outcomes by registered condition, alone vs combined vs all other trials"),
    ]
    return "\n".join(out)


def _subtype_part(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    name = labels.get(FOCUS_CATEGORY, FOCUS_CATEGORY)
    interf, recov = FOCUS_OUTCOMES
    sub = ad.psychological_subtypes(studies, FOCUS_CATEGORY)
    n = len(sub)
    table = ad.subtype_outcome_table(studies, outcomes, FOCUS_OUTCOMES)
    rows = [
        [r.subtype, r.trials, _pct(r.trials, n), r.n, _ci_cell(getattr(r, interf), r.n), _ci_cell(getattr(r, recov), r.n)]
        for r in table.itertuples()
    ]
    other = sub.loc[sub["other_subtype"] != "", "other_subtype"].value_counts()
    named = list(ad.PSYCH_NAMED_SUBTYPES)
    overlap = int((sub[named].sum(axis=1) > 1).sum())
    n_mbsr_total = int(ad.included(studies)["has_mind_body_integrative"].sum())
    out = [
        f"### CBT, ACT and MBSR within {name}",
        "",
        f"Of the {n} included {name} trials, " + ", ".join(f"{int(sub[k].sum())} name {k}" for k in named)
        + f" in an active arm ({overlap} name more than one); {int((sub['other_subtype'] != '').sum())} name none of the three"
        + (": " + ", ".join(f"{k.split(' (')[0].lower()} {v}" for k, v in other.items()) if len(other) else "")
        + f". MBSR belongs to the mind-body category in the taxonomy ({n_mbsr_total} mind-body trials in the cohort), so only the trials that also carry the "
        "psychological category are counted here. Matching is on the name and description of the active arms (patterns: `analysis_data.PSYCH_NAMED_SUBTYPES`); descriptive only.",
        "",
        _table(["Subtype", "Trials", f"% of {name}", "With registered outcome", "Pain interference", "Pain recovery"], rows),
        "",
        "Subtypes overlap; percentages are of the subtype's trials with a registered outcome (95% Wilson interval). Subtypes under "
        f"{MIN_GROUP} trials are unstable.",
        "",
        _fig("fig17_psychological_subtypes", f"{name}: CBT / ACT / MBSR counts and the outcomes each registers"),
    ]
    return "\n".join(out)


# --- section 2: overview of everything else --------------------------------------------------
def _overview(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    inc = included(studies)
    inc_out = outcomes[(outcomes["cohort_inclusion_status"] == "included")]
    kept = inc_out[~inc_out["outcome_subcategory"].isin(ad.CROSSTAB_DROP_SUBCATEGORIES)]
    out = ["## 2. Overview of the remaining results", ""]

    # cohort
    summary = ad.cohort_summary_table(studies, outcomes)
    out += ["### 2.1 Cohort", "", _table(list(summary.columns), summary.values.tolist()), ""]
    years = inc["first_post_year"].dropna().astype(int)
    per_year = years.value_counts().sort_index()
    complete = per_year.iloc[:-1] if len(per_year) > 1 else per_year  # the last year is partial
    out += [
        f"Included trials were first posted between {years.min()} and {years.max()}; the busiest complete year is {int(complete.idxmax())} "
        f"({int(complete.max())} trials). The latest year is partial.",
        "",
        _fig("fig01_trials_by_year", "Trials by first-post year"),
        "",
    ]

    # exclusions
    excluded = studies[studies["cohort_inclusion_status"] == "excluded"]
    strata = excluded["exclusion_stratum"].value_counts()
    top_rules = excluded["exclusion_rule"].value_counts().head(3)
    out += [
        "### 2.2 Exclusions",
        "",
        f"{len(excluded)} of {len(studies)} retrieved trials were excluded: "
        + ", ".join(f"{n} by {s.lower()}" for s, n in strata.items())
        + ". Most frequent rules: "
        + ", ".join(f"{_pretty(rule)} ({n})" for rule, n in top_rules.items())
        + ".",
        "",
        _fig("fig03_exclusion_reasons", "Exclusion reasons by stratum"),
        "",
    ]

    # conditions
    per_condition = Counter(label for lst in inc["condition_list"] for label in lst)
    multi_condition = int((inc["n_conditions"] > 1).sum())
    out += [
        "### 2.3 Conditions",
        "",
        ", ".join(f"{k}: {v} ({_pct(v, len(inc))})" for k, v in per_condition.most_common())
        + f". {multi_condition} trials ({_pct(multi_condition, len(inc))}) register more than one target condition, so these counts overlap.",
        "",
        _fig("fig04_conditions", "Trials per registered condition"),
        "",
    ]

    # interventions
    keys = ad.intervention_keys_by_size(studies)
    single_n = int((inc["n_intervention_categories"] == 1).sum())
    multi_mod = int(inc["is_multimodal"].astype(bool).sum())
    cooc = ad.cooccurrence(studies)
    comp_rows = []
    for key in keys:
        n = int(cooc.loc[key, key])
        alone = int(((inc[f"has_{key}"]) & (inc["n_intervention_categories"] == 1)).sum())
        others = cooc.loc[key].drop(key).sort_values(ascending=False)
        top = others.index[0] if len(others) and others.iloc[0] > 0 else None
        comp_rows.append(
            [labels.get(key, key), n, _pct(n, len(inc)), _pct(alone, n), f"{SHORT_LABELS.get(top, top)} ({_pct(others.iloc[0], n)})" if top else "-"]
        )
    combos = inc["intervention_list"].apply(lambda cats: " + ".join(SHORT_LABELS.get(c, c) for c in cats) or "none").value_counts().head(5)
    out += [
        "### 2.4 Intervention categories",
        "",
        f"{single_n} trials ({_pct(single_n, len(inc))}) carry exactly one category; {multi_mod} ({_pct(multi_mod, len(inc))}) also have an active non-behavioral arm. "
        f"There are {inc['intervention_list'].apply(tuple).nunique()} distinct category combinations.",
        "",
        _table(["Category", "Trials", "% of included", "Carried alone", "Most common companion"], comp_rows),
        "",
        "Most common exact combinations: " + "; ".join(f"{combo} ({n})" for combo, n in combos.items()) + ".",
        "",
        _fig("fig05_interventions", "Trials per intervention category and most common combinations"),
        "",
        _fig("fig14_upset_combinations", "Most common combinations of intervention categories (UpSet plot)"),
        "",
    ]

    # outcomes
    per_cat = kept.groupby("outcome_category").agg(rows=("outcome_id", "size"), trials=("nct_id", "nunique")).reindex(OUTCOME_ORDER).dropna().astype(int)
    n_trials_out = kept["nct_id"].nunique()
    outcome_rows = [[_pretty(cat), r.rows, _pct(r.rows, len(kept)), r.trials, _pct(r.trials, n_trials_out)] for cat, r in per_cat.iterrows()]
    n_per_trial = inc.loc[inc["n_primary_outcomes"] > 0, "n_primary_outcomes"]
    instruments = Counter(name.strip() for value in inc_out["instruments_detected"].dropna() for name in str(value).split("|") if name.strip())
    out += [
        "### 2.5 Primary outcomes",
        "",
        f"{len(kept)} primary outcomes in {n_trials_out} trials (outcomes labelled `not_an_outcome_measure` are left out, as in the cross-tab). "
        f"Trials register {n_per_trial.mean():.2f} primary outcomes on average; {_pct((n_per_trial > 1).sum(), len(n_per_trial))} register more than one.",
        "",
        _table(["Outcome category", "Outcomes", "% of outcomes", "Trials", "% of trials"], outcome_rows),
        "",
        "Most frequently detected instruments: " + ", ".join(f"{k} ({v})" for k, v in instruments.most_common(6)) + ".",
        "",
        _fig("fig07_outcome_overview", "Primary outcomes by category and most frequent subcategories"),
        "",
        _fig("fig11_top_instruments", "Most frequently detected instruments"),
        "",
        _fig("fig12_outcomes_per_trial", "Registered primary outcomes per trial"),
        "",
    ]

    # intervention x outcome (main goal)
    ct = ad.outcome_by_group(studies, outcomes, labels=labels)
    pct = ct.trial_percent()
    shown = [c for c in OUTCOME_ORDER if c in pct.columns and c != "other"]
    cross_rows = [[idx, int(ct.n_trials[idx])] + [f"{pct.loc[idx, c]:.0f}%" for c in shown] for idx in pct.index]
    leaders = []
    for idx in pct.index:
        if ct.n_trials[idx] >= MIN_GROUP:
            row = pct.loc[idx, [c for c in shown if c not in ("feasibility_acceptability", "mechanistic")]].sort_values(ascending=False)
            leaders.append(f"{idx}: {_pretty(row.index[0])} ({row.iloc[0]:.0f}%)")
    out += [
        "### 2.6 Intervention category x outcome category (the study's main question)",
        "",
        "Share of each category's trials that registered at least one outcome of the type (rows can exceed 100% because a trial can register several types).",
        "",
        _table(["Intervention category", "Trials"] + [_pretty(c) for c in shown], cross_rows),
        "",
        "Most frequent clinical outcome type per category (categories with at least "
        f"{MIN_GROUP} trials; feasibility and mechanistic outcomes set aside): " + "; ".join(leaders) + ".",
        "",
        "See the three versions of this figure in section 1; the completed-trials version is `fig06_completed`, and `fig06_custom` appears when a filter is set in the notebook.",
        "",
    ]

    # over time
    merged = kept.merge(studies[["nct_id", "period"]], on="nct_id")
    counts = pd.crosstab(merged["period"], merged["outcome_category"]).reindex(PERIOD_LABELS).fillna(0)
    share = counts.div(counts.sum(axis=1), axis=0) * 100
    time_cols = [c for c in ("pain_recovery", "pain_interference", "mood", "feasibility_acceptability", "mechanistic") if c in share.columns]
    time_rows = [[p, int(counts.loc[p].sum())] + [f"{share.loc[p, c]:.0f}%" for c in time_cols] for p in PERIOD_LABELS]
    out += [
        "### 2.7 Over time",
        "",
        "Share of the period's primary outcomes by category (period = year the trial was first posted):",
        "",
        _table(["Period", "Outcomes"] + [_pretty(c) for c in time_cols], time_rows),
        "",
        _fig("fig08_outcomes_over_time", "Primary outcome categories over time"),
        "",
        _fig("fig09_interventions_over_time", "Intervention categories over time"),
        "",
    ]

    # conditions x outcome
    ct_cond = ad.outcome_by_group(studies, outcomes, group="condition_list")
    cond_pct = ct_cond.trial_percent()
    cond_cols = [c for c in ("pain_recovery", "pain_interference", "mood") if c in cond_pct.columns]
    cond_rows = [[idx, int(ct_cond.n_trials[idx])] + [f"{cond_pct.loc[idx, c]:.0f}%" for c in cond_cols] for idx in cond_pct.index]
    out += [
        "### 2.8 Condition x outcome category",
        "",
        "Share of each condition's trials with at least one outcome of the type:",
        "",
        _table(["Condition", "Trials"] + [_pretty(c) for c in cond_cols], cond_rows),
        "",
        _fig("fig10_condition_x_outcome", "Registered condition x primary outcome category"),
        "",
    ]
    return "\n".join(out)


# --- assembly ----------------------------------------------------------------------------------
def build_results_summary() -> str:
    studies, outcomes = ad.load_tables()
    labels = ad.intervention_labels()
    manifest_path = PROCESSED_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    header = [
        "# Results summary",
        "",
        "> Auto-generated by `ctgov_pipeline.analysis_report` after every notebook run; do not edit by hand. "
        "Every number is recomputed from `data/processed/`; figures are in `analysis/figures/`, tables in `analysis/tables/`, "
        "and the full workings in `analysis/outcome_analysis.ipynb`.",
        "",
        f"Extraction run `{manifest.get('source_extraction_run_id', '?')}`, cohort rules `{manifest.get('cohort_rules_version', '?')}`; "
        f"{len(included(studies))} included trials, {int((outcomes['cohort_inclusion_status'] == 'included').sum())} primary outcome rows. "
        "Outcome categories are descriptive, rule-based aids (not the researcher's manual coding); a trial that carries several intervention "
        "or outcome categories is counted in each of them.",
        "",
    ]
    return "\n".join(header) + "\n" + _focus_section(studies, outcomes, labels) + "\n\n" + _overview(studies, outcomes, labels) + "\n"


def write_results_summary(path=RESULTS_SUMMARY_MD):
    path.write_text(build_results_summary(), encoding="utf-8")
    return path


def main() -> None:
    print(f"Wrote {write_results_summary()}")


if __name__ == "__main__":
    main()
