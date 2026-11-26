"""Side analysis: add `chronic pain` as a fifth registered condition and rebuild everything end to end.

    python chronic_pain_condition_addition/run_scenario.py [--skip-fetch] [--skip-analysis]

Everything is written inside this directory (`data/raw`, `data/processed`, `analysis/`); the main results in
`data/` and `analysis/` of the project are never touched (the pipeline is pointed here with CTGOV_WORKSPACE).

Steps
1. Raw data: the raw JSON of the main run (back pain, fibromyalgia, migraine, headache) is COPIED here, so the
   four original conditions are exactly the same snapshot as the main analysis; then the chronic-pain search
   (`AREA[Condition]"chronic pain"`, same StudyType/InterventionType filters) is pulled from CT.gov and the
   records not already present are added. Search pages are kept per condition (`api_retrieval_queries`).
2. Cohort rules: identical to the main analysis; the only change is the extra target `chronic_pain`
   (config/condition_patterns_cohort.yaml here, merged over the project config).
3. `finalize_cohort` rebuilds the two tables, the reports, executes a copy of the analysis notebook and writes
   analysis/results_summary.md; analysis/comparison_with_main.md contrasts the trials added by chronic pain with the
   main cohort.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
os.environ["CTGOV_WORKSPACE"] = str(HERE)  # must be set before ctgov_pipeline is imported
sys.path.insert(0, str(PROJECT / "src"))
os.environ["PYTHONPATH"] = os.pathsep.join(filter(None, [str(PROJECT / "src"), os.environ.get("PYTHONPATH", "")]))  # for the notebook kernel

from ctgov_pipeline.config_loader import IS_SIDE_WORKSPACE  # noqa: E402

assert IS_SIDE_WORKSPACE, "workspace redirection failed; refusing to run (would overwrite the main results)"

from ctgov_pipeline.extraction_runs import latest_full_extraction_run_id  # noqa: E402
from ctgov_pipeline.fetch import get_api_version, save_json  # noqa: E402
from ctgov_pipeline.finalize_cohort import finalize_cohort  # noqa: E402
from ctgov_pipeline.run_full import ADVANCED_FILTER, _fetch_all_pages, _save_search_pages  # noqa: E402

CONDITION_KEY, CONDITION_TERM = "chronic_pain", "chronic pain"
BANNER = (
    "> **Side analysis: `chronic_pain_condition_addition`.** Same pipeline, filters and notebook as the main analysis, "
    "with **chronic pain** added as a fifth condition of the API pull (and as a target in the registered-conditions "
    "match). Data in `chronic_pain_condition_addition/data/`, outputs here; the main results are untouched.\n\n"
)


def prepare_raw_run() -> str:
    """Copy the main raw run, add the chronic-pain pull; return the new run id."""
    base_id = latest_main_run_id()
    base = PROJECT / "data" / "raw" / "full" / base_id
    run_id = "chronic_pain_addition_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw = HERE / "data" / "raw" / "full" / run_id
    shutil.copytree(base / "studies", raw / "studies")
    shutil.copytree(base / "search_pages", raw / "search_pages")
    n_base = len(list((raw / "studies").glob("NCT*.json")))

    records, total = _fetch_all_pages(CONDITION_KEY, CONDITION_TERM)
    _save_search_pages(records, raw / "search_pages", CONDITION_KEY)
    added = 0
    for record in records:
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        target = raw / "studies" / f"{nct_id}.json"
        if not target.exists():  # a trial already in the main pool keeps its main-run record
            save_json(record, target)
            added += 1

    api = get_api_version()
    save_json(
        {
            "run_id": run_id,
            "extraction_date": datetime.now(timezone.utc).isoformat(),
            "api_version": api.get("apiVersion"),
            "data_timestamp_of_chronic_pain_pull": api.get("dataTimestamp"),
            "base_run_copied_from_main_analysis": base_id,
            "retrieval_criteria": {
                "study_type": "INTERVENTIONAL",
                "intervention_type": "BEHAVIORAL",
                "conditions": ["back pain", "fibromyalgia", "migraine", "headache", CONDITION_TERM],
                "filter_advanced": ADVANCED_FILTER,
            },
            "chronic_pain_api_total_count": total,
            "base_trials": n_base,
            "chronic_pain_trials_added": added,
            "pool_trials": n_base + added,
        },
        raw / "extraction_manifest.json",
    )
    print(f"Raw run {run_id}: {n_base} copied from the main run, {added} added by the chronic-pain search ({total} hits).")
    return run_id


def latest_main_run_id() -> str:
    runs = sorted(p.name for p in (PROJECT / "data" / "raw" / "full").iterdir() if (p / "studies").is_dir())
    return runs[-1]


def prepare_notebook() -> None:
    import nbformat

    source = nbformat.read(PROJECT / "analysis" / "outcome_analysis.ipynb", as_version=4)
    first = source.cells[0]
    first.source = BANNER + first.source.replace(
        "(back pain, fibromyalgia, migraine, headache)", "(back pain, fibromyalgia, migraine, headache, chronic pain)"
    )
    (HERE / "analysis").mkdir(exist_ok=True)
    nbformat.write(source, HERE / "analysis" / "outcome_analysis.ipynb")


def write_comparison() -> Path:
    """analysis/comparison_with_main.md: the Psychological & cognitive alone-vs-combined pattern and therapy subtypes in
    the trials of the main cohort versus the trials added by the chronic-pain condition (same code as results_summary.md).
    Also puts a short 'does it reproduce?' section at the top of analysis/results_summary.md."""
    import pandas as pd

    from ctgov_pipeline import analysis_data as ad

    studies, outcomes = ad.load_tables()
    main_ids = set(pd.read_csv(PROJECT / "data" / "processed" / "studies.csv").query("cohort_inclusion_status == 'included'")["nct_id"])
    focus, interf, recov = "psychological_cognitive", "pain_interference", "pain_recovery"
    main_t, added_t, all_t = (
        "Main cohort trials (the original four conditions)",
        "Trials added by the chronic-pain condition",
        "Whole extended cohort",
    )
    parts = {main_t: studies[studies["nct_id"].isin(main_ids)], added_t: studies[~studies["nct_id"].isin(main_ids)], all_t: studies}

    def pct(k, n) -> float:
        return 100 * k / n if n else float("nan")

    def cell(k: int, n: int) -> str:
        lo, hi = ad.wilson_interval(k, n)
        return f"{pct(k, n):.0f}% ({lo:.0f}-{hi:.0f}%)"

    def short(k_i, k_r, n) -> str:
        return f"{int(n)}: {pct(k_i, n):.0f}% / {pct(k_r, n):.0f}%" if n else "-"

    rows, tests, groups = [], {}, {}
    for title, part in parts.items():
        table = ad.companion_outcome_table(part, outcomes, focus, (interf, recov), min_n=10).set_index("group")
        groups[title] = table
        for group, label in (("only_this_category", "Alone"), ("with_any_other_category", "Combined")):
            r = table.loc[group]
            rows.append([title, label, int(r["n"]), cell(int(r[interf]), int(r["n"])), cell(int(r[recov]), int(r["n"]))])
        a, c = table.loc["only_this_category"], table.loc["with_any_other_category"]
        tests[title] = tuple(
            ad.fisher_exact_two_sided(int(a[col]), int(a["n"]), int(c[col]), int(c["n"])) for col in (interf, recov)
        )

    # therapy subtypes, pure and combined, main versus added trials
    sub = {
        (title, kind): ad.subtype_outcome_table(parts[title], outcomes, (interf, recov), **{kind: True}).set_index("subtype")
        for title in (main_t, added_t)
        for kind in ("pure_only", "combined_only")
    }
    sub_rows = []
    for name in sub[(main_t, "pure_only")].index:
        if name == ad.NO_SUBTYPE:
            continue
        sub_rows.append(
            [name]
            + [short(sub[k].loc[name, interf], sub[k].loc[name, recov], sub[k].loc[name, "n"]) for k in (
                (main_t, "pure_only"), (added_t, "pure_only"), (main_t, "combined_only"), (added_t, "combined_only"))]
        )

    def row(title, group):
        r = groups[title].loc[group]
        return int(r["n"]), pct(r[interf], r["n"]), pct(r[recov], r["n"])

    (nm, im, rm), (na, ia, ra) = row(main_t, "only_this_category"), row(added_t, "only_this_category")
    (_, imc, rmc), (_, iac, rac) = row(main_t, "with_any_other_category"), row(added_t, "with_any_other_category")

    def order(i, r) -> str:
        return "more often than" if i > r + 2 else "less often than" if i < r - 2 else "about as often as"

    def pure_trials(title, name):
        return int(sub[(title, "pure_only")].loc[name, "n"])

    summary = (
        f"The main-cohort pattern does not carry over to the trials added by the chronic-pain condition. In the main cohort, "
        f"Psychological & cognitive trials used alone register recovery {order(rm, im)} interference ({rm:.0f}% vs {im:.0f}%, n={nm}) "
        f"and recovery is clearly lower when they are combined ({rmc:.0f}%). Among the added trials, those used alone register interference "
        f"{order(ia, ra)} recovery ({ia:.0f}% vs {ra:.0f}%, n={na}) and combining makes little difference to recovery ({ra:.0f}% alone vs {rac:.0f}% combined), "
        f"so the alone-versus-combined recovery difference disappears (extended cohort: p = {tests[all_t][1]:.2f}). "
        f"The therapy mix also differs: psychotherapy-type trials, which drive the recovery tilt of the main cohort's pure trials, are rare among the added "
        f"pure trials ({pure_trials(added_t, 'Psychotherapy')} vs {pure_trials(main_t, 'Psychotherapy')}), which are mostly CBT ({pure_trials(added_t, 'CBT')}) and ACT "
        f"({pure_trials(added_t, 'ACT')}), and ACT trials register interference far more than recovery. What does reproduce is the overall orientation: "
        f"in both sets, combined with other intervention categories, the category registers interference at least as often as recovery "
        f"({imc:.0f}% vs {rmc:.0f}% in the main cohort, {iac:.0f}% vs {rac:.0f}% among the added trials), "
        f"and in all five conditions it registers interference more often than other behavioral trials of the same condition. "
        f"So the interference orientation of cognitive therapies holds with chronic pain included, whereas the tilt toward recovery when used alone is "
        f"specific to the original four conditions (back pain and fibromyalgia, not the generic chronic-pain trials)."
    )
    lines = [
        "# Psychological & cognitive therapy: main cohort versus the trials added by 'chronic pain'",
        "",
        "Auto-generated by `run_scenario.py`. Share of the group's trials (with a registered primary outcome) that have at least one outcome of the type; 95% Wilson interval in brackets.",
        "",
        "## Takeaway",
        "",
        summary,
        "",
        "## Alone versus combined",
        "",
        "| Trials | Psychological & cognitive trials | n | Pain interference | Pain recovery |",
        "|---|---|---|---|---|",
    ] + [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |" for r in rows] + [
        "",
        "Fisher exact p-value, alone vs combined (exploratory, uncorrected):",
        "",
        "| Trials | Pain interference | Pain recovery |",
        "|---|---|---|",
    ] + [f"| {title} | p = {p_i:.3f} | p = {p_r:.3f} |" for title, (p_i, p_r) in tests.items()] + [
        "",
        "## Therapy subtypes",
        "",
        "Each cell: trials, then % with an interference outcome / % with a recovery outcome. Subtypes overlap; small groups (under 10) are unstable.",
        "",
        "| Subtype | Main, pure | Added, pure | Main, combined | Added, combined |",
        "|---|---|---|---|---|",
    ] + [f"| {' | '.join(r)} |" for r in sub_rows]
    path = HERE / "analysis" / "comparison_with_main.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # same takeaway at the top of this scenario's results_summary.md (replaced on every run)
    summary_path = HERE / "analysis" / "results_summary.md"
    if summary_path.exists():
        marker_start, marker_end = "<!-- reproduction:start -->", "<!-- reproduction:end -->"
        text = summary_path.read_text(encoding="utf-8")
        if marker_start in text:
            text = text[: text.index(marker_start)] + text[text.index(marker_end) + len(marker_end) :].lstrip("\n")
        block = (
            f"{marker_start}\n## Does the main-cohort pattern reproduce with 'chronic pain' added?\n\n{summary}\n\n"
            f"Tables: `comparison_with_main.md`.\n{marker_end}\n\n"
        )
        text = text.replace("## 1. ", block + "## 1. ", 1)
        summary_path.write_text(text, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-fetch", action="store_true", help="reuse the newest raw run already in this directory")
    parser.add_argument("--comparison-only", action="store_true", help="only rewrite analysis/comparison_with_main.md")
    parser.add_argument("--skip-analysis", action="store_true", help="do not execute the notebook / write the summary")
    args = parser.parse_args()

    if args.comparison_only:
        print(f"Wrote {write_comparison()}")
        return
    run_id = latest_full_extraction_run_id() if args.skip_fetch else prepare_raw_run()
    prepare_notebook()
    out = finalize_cohort(extraction_run_id=run_id, run_analysis=not args.skip_analysis)

    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scenario"] = "chronic_pain_condition_addition: main cohort rules + 'chronic pain' as a fifth condition"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if not args.skip_analysis:
        write_comparison()
    print(f"Done. Outputs: {HERE / 'analysis'}")


if __name__ == "__main__":
    main()
