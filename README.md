# Primary outcome analysis — ClinicalTrials.gov pipeline

Reproducible pipeline for studying **registered primary outcomes** in **behavioral interventional** chronic pain trials (ClinicalTrials.gov API v2).

Repository: `https://github.com/talmorya/primary-outcome-analysis`

## Research question

Among behavioral interventions for chronic pain, what primary outcomes do researchers register, and how does that vary by intervention approach and over time (`raw_study_first_post_date`)?

---

## Where things are

| Need | Go to |
|---|---|
| **Inclusion / exclusion rules** (all of them, including acute) | [`docs/COHORT_FILTERING_RULES.md`](docs/COHORT_FILTERING_RULES.md) |
| **What every column means** | [`docs/DATA_COLUMNS.md`](docs/DATA_COLUMNS.md) |
| How to rebuild from raw data | [`docs/COHORT_REPRODUCTION_GUIDE.md`](docs/COHORT_REPRODUCTION_GUIDE.md) |
| Cohort statistics (auto-generated) | [`data/processed/cohort_report.md`](data/processed/cohort_report.md) |
| Index of docs | [`docs/README.md`](docs/README.md) |

## Data (one current version of each)

| Path | Contents |
|---|---|
| `data/raw/full/<run_id>/studies/*.json` | Immutable CT.gov records (gitignored; keep only the latest run) |
| `data/processed/studies.csv` | **Every retrieved trial**, with `cohort_inclusion_status`, `exclusion_reason` (`acute` / `condition`) and `exclusion_detail`, plus raw text columns for manual review |
| `data/processed/primary_outcomes.csv` | One row per registered primary outcome (verbatim text + descriptive categories) |
| `data/processed/manifest.json` | Source run id and counts |

Analysis subset: `studies.csv` where `cohort_inclusion_status == "included"`, joined to `primary_outcomes.csv` on `nct_id`.

Current run `full_20261109_104453`: 936 trials retrieved → **882 included**, 54 excluded (20 `acute`, 34 `condition`).

---

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Rebuild the cohort from the raw JSON already on disk (no network)
PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort

# Tests
PYTHONPATH=src python -m unittest discover -s tests -v

# Only when you want fresh CT.gov data (creates a NEW raw run; then delete the old one)
PYTHONPATH=src python -m ctgov_pipeline.run_full
PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort
```

`run_full` also writes a legacy extraction layer to `data/processed/full/<run_id>/` (gitignored, not used by the cohort). It is not needed for analysis and can be deleted after a run.

---

## Project layout

```
config/                  condition_patterns_cohort.yaml, intervention_categories.yaml, outcome_lexicon.yaml
docs/                    filtering rules, column dictionary, reproduction guide
src/ctgov_pipeline/      run_full (fetch) · build_revised_cohort / finalize_cohort (cohort) · classifiers
tests/
data/raw/                raw JSON (gitignored)
data/processed/   the four analytic files (tracked in git; legacy full/ is ignored)
```
