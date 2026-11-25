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
    """analysis/comparison_with_main.md: the Psychological & cognitive alone-vs-combined pattern in the trials of the
    main cohort versus the trials added by the chronic-pain condition (same code as results_summary.md)."""
    import pandas as pd

    from ctgov_pipeline import analysis_data as ad

    studies, outcomes = ad.load_tables()
    main_ids = set(pd.read_csv(PROJECT / "data" / "processed" / "studies.csv").query("cohort_inclusion_status == 'included'")["nct_id"])
    focus, interf, recov = "psychological_cognitive", "pain_interference", "pain_recovery"
    parts = {
        "Main cohort trials (the original four conditions)": studies[studies["nct_id"].isin(main_ids)],
        "Trials added by the chronic-pain condition": studies[~studies["nct_id"].isin(main_ids)],
        "Whole extended cohort": studies,
    }

    def cell(k: int, n: int) -> str:
        lo, hi = ad.wilson_interval(k, n)
        return f"{100 * k / n:.0f}% ({lo:.0f}-{hi:.0f}%)"

    rows, tests = [], {}
    for title, part in parts.items():
        table = ad.companion_outcome_table(part, outcomes, focus, (interf, recov), min_n=10).set_index("group")
        for group, label in (("only_this_category", "Alone"), ("with_any_other_category", "Combined")):
            r = table.loc[group]
            rows.append([title, label, int(r["n"]), cell(int(r[interf]), int(r["n"])), cell(int(r[recov]), int(r["n"]))])
        a, c = table.loc["only_this_category"], table.loc["with_any_other_category"]
        tests[title] = tuple(
            ad.fisher_exact_two_sided(int(a[col]), int(a["n"]), int(c[col]), int(c["n"])) for col in (interf, recov)
        )
    lines = [
        "# Psychological & cognitive therapy: main cohort versus the trials added by 'chronic pain'",
        "",
        "Auto-generated by `run_scenario.py`. Share of the group's trials (with a registered primary outcome) that have at least one outcome of the type; 95% Wilson interval in brackets.",
        "",
        "| Trials | Psychological & cognitive trials | n | Pain interference | Pain recovery |",
        "|---|---|---|---|---|",
    ] + [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |" for r in rows] + [
        "",
        "Fisher exact p-value, alone vs combined (exploratory, uncorrected):",
        "",
        "| Trials | Pain interference | Pain recovery |",
        "|---|---|---|",
    ] + [f"| {title} | p = {p_i:.3f} | p = {p_r:.3f} |" for title, (p_i, p_r) in tests.items()]
    path = HERE / "analysis" / "comparison_with_main.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
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
