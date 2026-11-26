"""Write analysis/results_summary.md: a short, figure-led summary of the analysis notebook.

Every number is recomputed from data/processed/ on each run (nothing is typed in by hand), so the summary
always matches the current cohort. Long tables are left to the figures and to analysis/tables/*.csv.
Called by `run_analysis_notebook` after the notebook has re-created the figures; can also be run alone:
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
    ("Full cohort", None),
    ("Behavioral arms only (no active non-behavioral arm)", "is_multimodal == False"),
    ("Single intervention category only (purity check)", "n_intervention_categories == 1"),
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
    return f"![{caption}](figures/{name}.png)"


def _ci_cell(k: int, n: int) -> str:
    if not n:
        return "-"
    lo, hi = ad.wilson_interval(k, n)
    return f"{100 * k / n:.0f}% ({lo:.0f}-{hi:.0f}%)"


# --- section 1: Psychological & cognitive therapy ---------------------------------------------
def _focus_section(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    name = labels.get(FOCUS_CATEGORY, FOCUS_CATEGORY)
    interf, recov = FOCUS_OUTCOMES

    # the same category in three versions of the cross-tab (share of the category's trials)
    version_rows, shares = [], {}
    for title, query in SENSITIVITY_VERSIONS:
        ct = ad.outcome_by_group(studies, outcomes, labels=labels, study_query=query)
        if name not in ct.n_trials.index:
            continue
        pct = ct.trial_percent().loc[name]
        shares[title] = (pct.get(interf, 0.0), pct.get(recov, 0.0), int(ct.n_trials[name]))
        version_rows.append([title, shares[title][2], f"{pct.get(interf, 0):.0f}%", f"{pct.get(recov, 0):.0f}%"])
    full, single = shares.get("Full cohort"), shares.get("Single intervention category only (purity check)")
    reversed_order = bool(full and single and full[0] > full[1] and single[0] < single[1])

    table = ad.companion_outcome_table(studies, outcomes, FOCUS_CATEGORY, FOCUS_OUTCOMES, min_n=MIN_GROUP).set_index("group")
    n_total, comp = ad.companions(studies, FOCUS_CATEGORY)
    n_alone_all = int(comp.iloc[0])
    top = [(k, v) for k, v in comp.items() if not k.startswith("(none")][:3]

    out = [f"## 1. {name}: interference or recovery?", ""]
    if full and single:
        out.append(
            f"In the full cohort the category's trials register pain interference more often than pain recovery ({full[0]:.0f}% vs {full[1]:.0f}% of trials), "
            + (
                f"but in the single-category check the order **reverses** (recovery {single[1]:.0f}% vs interference {single[0]:.0f}%, n={single[2]})."
                if reversed_order
                else f"and the single-category check gives {single[0]:.0f}% vs {single[1]:.0f}% (n={single[2]}); the order does not reverse."
            )
        )
    out += [
        "",
        _table(["Version (share of the category's trials)", "Trials", "Interference", "Recovery"], version_rows),
        "",
        _fig("fig06_intervention_x_outcome", "Intervention category x outcome category, full cohort"),
        "",
        _fig("fig06_single_category", "Same, single-category trials only"),
        "",
        "### Alone or combined",
        "",
        f"{n_total} trials carry the category, only {n_alone_all} ({_pct(n_alone_all, n_total)}) alone. Most common companions: "
        + ", ".join(f"{SHORT_LABELS.get(k, k)} ({_pct(v, n_total)})" for k, v in top)
        + ".",
        "",
    ]
    gap_rec = 0.0
    if {"only_this_category", "with_any_other_category"} <= set(table.index):
        a, c = table.loc["only_this_category"], table.loc["with_any_other_category"]
        p_rec = ad.fisher_exact_two_sided(int(a[recov]), int(a["n"]), int(c[recov]), int(c["n"]))
        p_int = ad.fisher_exact_two_sided(int(a[interf]), int(a["n"]), int(c[interf]), int(c["n"]))
        gap_rec = 100 * (a[recov] / a["n"] - c[recov] / c["n"])
        out += [
            _table(
                ["Group", "Trials", "Interference (95% CI)", "Recovery (95% CI)"],
                [
                    ["Alone", int(a["n"]), _ci_cell(int(a[interf]), int(a["n"])), _ci_cell(int(a[recov]), int(a["n"]))],
                    ["Combined", int(c["n"]), _ci_cell(int(c[interf]), int(c["n"])), _ci_cell(int(c[recov]), int(c["n"]))],
                ],
            ),
            "",
            f"Alone vs combined: recovery {_p_value(p_rec)}, interference {_p_value(p_int)} (Fisher exact, exploratory).",
        ]
        companion_rows = table.drop(index=["only_this_category", "with_any_other_category"], errors="ignore")
        if len(companion_rows):
            shares_rec = [100 * r[recov] / r["n"] for _, r in companion_rows.iterrows()]
            alone_rec = 100 * a[recov] / a["n"]
            out.append(
                f" Recovery is {min(shares_rec):.0f}-{max(shares_rec):.0f}% in each of the {len(companion_rows)} companion groups"
                + (", below the 'alone' value in all of them (no single partner stands out)." if all(s < alone_rec for s in shares_rec) else ", not uniformly below the 'alone' value.")
            )
        reading = (
            f"Most {name} trials are combined, and combined trials register recovery less often; the category may be aimed at recovery when used alone, "
            "but this is only suggested by these numbers. "
            if reversed_order and gap_rec > 0
            else "No clean alone-versus-combined reversal in this run. "
        )
        out += [
            "",
            _fig(f"fig15_companions_{FOCUS_CATEGORY}", f"Companions of {name} and outcomes by what it is combined with"),
            "",
            f"**Reading.** {reading}Caution: the 'alone' group is small (n={int(a['n'])}), tests are uncorrected, and outcome categories are rule-based aids.",
        ]
    out += ["", _condition_part(studies, outcomes, labels), "", _subtype_part(studies, outcomes, labels), ""]
    out += [_fig("fig13_cooccurrence_heatmap", "Co-occurrence of intervention categories (row: % of its trials that also carry the column)")]
    return "\n".join(out)


def _condition_part(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    name = labels.get(FOCUS_CATEGORY, FOCUS_CATEGORY)
    interf, recov = FOCUS_OUTCOMES
    table = ad.condition_outcome_table(studies, outcomes, FOCUS_CATEGORY, (interf, recov, "mood"))
    by = table.set_index(["condition", "group"])
    conditions = list(dict.fromkeys(table["condition"]))
    n_all = {c: int(by.loc[(c, "all"), "n"]) for c in conditions}
    out = [
        "### By registered condition",
        "",
        f"*all* = alone + combined (e.g. {conditions[0]}: {n_all[conditions[0]]} = {int(by.loc[(conditions[0], 'only_this_category'), 'n'])} alone + "
        f"{int(by.loc[(conditions[0], 'with_any_other_category'), 'n'])} combined); *other* = behavioral trials of the condition without the category. "
        "Trials per condition: " + ", ".join(f"{c} {n}" for c, n in n_all.items()) + f". Full table: `tables/tab16_condition_split_{FOCUS_CATEGORY}.csv`.",
        "",
        _fig(f"fig16_condition_split_{FOCUS_CATEGORY}", f"{name} by registered condition (faded bars: fewer than {MIN_GROUP} trials)"),
        "",
    ]
    lines = []
    for c in conditions:
        a, k = by.loc[(c, "only_this_category")], by.loc[(c, "with_any_other_category")]
        if a["n"] >= MIN_GROUP and k["n"] >= MIN_GROUP:
            p = ad.fisher_exact_two_sided(int(a[recov]), int(a["n"]), int(k[recov]), int(k["n"]))
            lines.append(
                f"- {c}: recovery {_pct(a[recov], a['n'])} alone vs {_pct(k[recov], k['n'])} combined ({_p_value(p)}); "
                f"interference {_pct(a[interf], a['n'])} vs {_pct(k[interf], k['n'])}."
            )
    if lines:
        out += ["Alone vs combined within a condition (both groups at least " + str(MIN_GROUP) + " trials):", ""] + lines + [""]
    rows = [
        (c, 100 * by.loc[(c, "all"), interf] / by.loc[(c, "all"), "n"], 100 * by.loc[(c, "other_trials"), interf] / by.loc[(c, "other_trials"), "n"])
        for c in conditions
        if by.loc[(c, "all"), "n"] >= MIN_GROUP and by.loc[(c, "other_trials"), "n"] >= MIN_GROUP
    ]
    if rows:
        out.append(
            f"Interference, all {name} trials vs other behavioral trials: "
            + "; ".join(f"{c} {i:.0f}% vs {o:.0f}%" for c, i, o in rows)
            + f" (higher in {sum(1 for _, i, o in rows if i > o)} of {len(rows)})."
        )
    return "\n".join(out)


def _subtype_part(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    name = labels.get(FOCUS_CATEGORY, FOCUS_CATEGORY)
    interf, recov = FOCUS_OUTCOMES
    sub = ad.psychological_subtypes(studies, FOCUS_CATEGORY)
    n = len(sub)
    named = list(ad.PSYCH_NAMED_SUBTYPES)
    n_none = int((sub["other_subtype"] != "").sum())
    n_pure = int((sub["n_intervention_categories"] == 1).sum())
    pure = ad.subtype_outcome_table(studies, outcomes, FOCUS_OUTCOMES, pure_only=True).set_index("subtype")
    comb = ad.subtype_outcome_table(studies, outcomes, FOCUS_OUTCOMES, combined_only=True).set_index("subtype")
    rows = []
    for subtype in pure.index:
        p, c = pure.loc[subtype], comb.loc[subtype]
        test = "-"
        if p["n"] and c["n"]:
            test = _p_value(ad.fisher_exact_two_sided(int(p[recov]), int(p["n"]), int(c[recov]), int(c["n"])))
        rows.append(
            [subtype, int(p["n"]), f"{_pct(p[interf], p['n'])} / {_pct(p[recov], p['n'])}", int(c["n"]), f"{_pct(c[interf], c['n'])} / {_pct(c[recov], c['n'])}", test]
        )
    out = [
        f"### CBT, ACT and MBSR within {name}",
        "",
        f"Of {n} trials: " + ", ".join(f"{int(sub[k].sum())} name {k}" for k in named)
        + f", {n_none} none of the three (active-arm text; MBSR is filed under mind-body, so few appear here). {n_pure} trials are pure (no other category).",
        "",
        _fig("fig17_psychological_subtypes", f"{name}: CBT / ACT / MBSR, alone or combined"),
        "",
        _fig("fig18_psychological_subtypes_pure", f"{name}: CBT / ACT / MBSR, pure trials only"),
        "",
        _table(["Subtype", "Pure n", "Pure: interf. / recov.", "Combined n", "Combined: interf. / recov.", "Recovery, pure vs combined"], rows),
    ]
    psych_pure = sub[sub["n_intervention_categories"] == 1]
    if len(psych_pure) and int((psych_pure[named].sum(axis=1) > 1).sum()) == 0:
        total_i, total_r = int(pure[interf].sum()), int(pure[recov].sum())
        out += [
            "",
            f"Pure trials: {total_r} register recovery, {total_i} interference (net {total_r - total_i:+d} for recovery); net by subtype (recovery minus interference): "
            + ", ".join(f"{k} {int(pure.loc[k, recov] - pure.loc[k, interf]):+d}" for k in pure.index if pure.loc[k, "n"])
            + ".",
        ]
    return "\n".join(out)


# --- section 2: overview of everything else --------------------------------------------------
def _overview(studies: pd.DataFrame, outcomes: pd.DataFrame, labels: dict[str, str]) -> str:
    inc = included(studies)
    inc_out = outcomes[outcomes["cohort_inclusion_status"] == "included"]
    kept = inc_out[~inc_out["outcome_subcategory"].isin(ad.CROSSTAB_DROP_SUBCATEGORIES)]
    out = ["## 2. Overview of the other results", "", "Tables behind every figure: `analysis/tables/`.", ""]

    summary = ad.cohort_summary_table(studies, outcomes)
    out += ["### Cohort", "", _table(["Metric", "Value"], summary[["Metric", "Value"]].values.tolist()), ""]
    years = inc["first_post_year"].dropna().astype(int)
    per_year = years.value_counts().sort_index()
    complete = per_year.iloc[:-1] if len(per_year) > 1 else per_year  # the last year is partial
    out += [f"First posted {years.min()}-{years.max()}; busiest complete year {int(complete.idxmax())} ({int(complete.max())} trials).", "", _fig("fig01_trials_by_year", "Trials by first-post year"), ""]

    excluded = studies[studies["cohort_inclusion_status"] == "excluded"]
    strata = excluded["exclusion_stratum"].value_counts()
    top_rules = excluded["exclusion_rule"].value_counts().head(3)
    out += [
        "### Exclusions",
        "",
        f"{len(excluded)} of {len(studies)} excluded: " + ", ".join(f"{v} {k.lower()}" for k, v in strata.items())
        + "; most frequent rules: " + ", ".join(f"{_pretty(k)} ({v})" for k, v in top_rules.items()) + ".",
        "",
        _fig("fig03_exclusion_reasons", "Exclusion reasons by stratum"),
        "",
    ]

    per_condition = Counter(label for lst in inc["condition_list"] for label in lst)
    multi = int((inc["n_conditions"] > 1).sum())
    out += [
        "### Conditions",
        "",
        ", ".join(f"{k} {v} ({_pct(v, len(inc))})" for k, v in per_condition.most_common()) + f"; {multi} trials list more than one condition.",
        "",
        _fig("fig04_conditions", "Trials per registered condition"),
        "",
    ]

    keys = ad.intervention_keys_by_size(studies)
    cooc = ad.cooccurrence(studies)
    single_n = int((inc["n_intervention_categories"] == 1).sum())
    multimodal = int(inc["is_multimodal"].astype(bool).sum())
    hubs = []
    for key in keys:
        others = cooc.loc[key].drop(key).sort_values(ascending=False)
        if cooc.loc[key, key] >= MIN_GROUP and len(others) and others.iloc[0] > 0:
            hubs.append((SHORT_LABELS.get(key, key), SHORT_LABELS.get(others.index[0], others.index[0]), 100 * others.iloc[0] / cooc.loc[key, key]))
    out += [
        "### Intervention categories",
        "",
        f"{single_n} trials ({_pct(single_n, len(inc))}) carry one category, {multimodal} ({_pct(multimodal, len(inc))}) add a non-behavioral arm. "
        "Most common companion of each category: " + "; ".join(f"{a} with {b} ({p:.0f}%)" for a, b, p in hubs) + ".",
        "",
        _fig("fig05_interventions", "Trials per intervention category and combinations"),
        "",
        _fig("fig14_upset_combinations", "Most common category combinations"),
        "",
    ]

    per_cat = kept.groupby("outcome_category").agg(rows=("outcome_id", "size"), trials=("nct_id", "nunique")).reindex(OUTCOME_ORDER).dropna().astype(int)
    n_trials_out = kept["nct_id"].nunique()
    n_per_trial = inc.loc[inc["n_primary_outcomes"] > 0, "n_primary_outcomes"]
    instruments = Counter(x.strip() for v in inc_out["instruments_detected"].dropna() for x in str(v).split("|") if x.strip())
    out += [
        "### Primary outcomes",
        "",
        f"{len(kept)} outcomes in {n_trials_out} trials ({n_per_trial.mean():.2f} per trial; {_pct((n_per_trial > 1).sum(), len(n_per_trial))} of trials register more than one). "
        "Share of trials registering each type: "
        + ", ".join(f"{_pretty(c)} {_pct(r.trials, n_trials_out)}" for c, r in per_cat.iterrows() if c != "other")
        + ". Top instruments: " + ", ".join(f"{k} ({v})" for k, v in instruments.most_common(5)) + ".",
        "",
        _fig("fig07_outcome_overview", "Primary outcomes by category and subcategory"),
        "",
    ]

    ct = ad.outcome_by_group(studies, outcomes, labels=labels)
    pct = ct.trial_percent()
    clinical = [c for c in pct.columns if c not in ("other", "feasibility_acceptability", "mechanistic")]
    leaders = []
    for idx in pct.index:
        if ct.n_trials[idx] >= MIN_GROUP:
            row = pct.loc[idx, clinical].sort_values(ascending=False)
            leaders.append(f"{SHORT_LABELS.get(idx, idx)} {_pretty(row.index[0])} ({row.iloc[0]:.0f}%)")
    out += [
        "### Intervention category x outcome category",
        "",
        "Most frequent clinical outcome type per category (share of its trials; feasibility and mechanistic set aside): " + "; ".join(leaders) + ". Figures in section 1.",
        "",
    ]

    merged = kept.merge(studies[["nct_id", "period"]], on="nct_id")
    counts = pd.crosstab(merged["period"], merged["outcome_category"]).reindex(PERIOD_LABELS).fillna(0)
    share = counts.div(counts.sum(axis=1), axis=0) * 100
    first, last = PERIOD_LABELS[0], PERIOD_LABELS[-1]
    moves = [f"{_pretty(c)} {share.loc[first, c]:.0f}% to {share.loc[last, c]:.0f}%" for c in ("pain_recovery", "pain_interference", "feasibility_acceptability", "mechanistic") if c in share.columns]
    out += ["### Over time", "", f"Share of outcomes, {first} to {last}: " + "; ".join(moves) + ".", "", _fig("fig08_outcomes_over_time", "Outcome categories over time"), "", _fig("fig09_interventions_over_time", "Intervention categories over time"), ""]

    ct_cond = ad.outcome_by_group(studies, outcomes, group="condition_list")
    cp = ct_cond.trial_percent()
    cols = [c for c in ("pain_recovery", "pain_interference") if c in cp.columns]
    out += [
        "### Condition x outcome category",
        "",
        "Recovery / interference share of each condition's trials: " + "; ".join(f"{i} " + " / ".join(f"{cp.loc[i, c]:.0f}%" for c in cols) for i in cp.index) + ".",
        "",
        _fig("fig10_condition_x_outcome", "Condition x outcome category"),
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
        "> Auto-generated after every notebook run; do not edit by hand. Numbers are recomputed from `data/processed/`; PDFs of the figures sit next to the PNGs; "
        "workings in `analysis/outcome_analysis.ipynb`.",
        "",
        f"Run `{manifest.get('source_extraction_run_id', '?')}`, rules `{manifest.get('cohort_rules_version', '?')}`: "
        f"{len(included(studies))} included trials, {int((outcomes['cohort_inclusion_status'] == 'included').sum())} primary outcomes. "
        "Outcome categories are rule-based aids, not manual coding; a trial with several categories counts in each. "
        "Percentages are shares of trials with at least one outcome of the type.",
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
