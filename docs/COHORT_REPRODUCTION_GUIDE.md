# Cohort reproduction guide

How to rebuild **`data/processed/`** from raw ClinicalTrials.gov JSON.

**Rules:** [COHORT_FILTERING_RULES.md](COHORT_FILTERING_RULES.md)  
**Columns:** [DATA_COLUMNS.md](DATA_COLUMNS.md)

---

## Pipeline

1. **Retrieve** behavioral interventional trials for four condition searches (deduplicated by NCT ID).
2. **Include** studies that pass **condition rules only** (`config/condition_patterns_cohort.yaml`).
3. **Classify** interventions and primary outcomes descriptively (no exclusion).

---

## Commands

```bash
source .venv/bin/activate
pip install -r requirements.txt

# New API pull → data/raw/full/<run_id>/
PYTHONPATH=src python -m ctgov_pipeline.run_full

# Build cohort tables + report + manifest
PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort
# Optional: pin extraction run
# PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort --extraction-run-id full_YYYYMMDD_HHMMSS
```

---

## Outputs

| Path | Contents |
|---|---|
| `data/raw/full/<run_id>/studies/*.json` | Immutable API records (keep **one** run; delete older folders when refreshing) |
| `data/processed/studies.csv` | Full master pool + `cohort_inclusion_status`, `exclusion_reason`, `exclusion_detail`, review text columns |
| `data/processed/primary_outcomes.csv` | All primary outcomes |
| `data/processed/cohort_report.md` | Descriptive statistics (included studies) |
| `data/processed/manifest.json` | Run metadata |

Optional: `run_full` also writes legacy extraction CSVs under `data/processed/full/<run_id>/` (gitignored). The **analytic** tables are the four files directly in `data/processed/`.

---

## Code map

| Step | Module | Config |
|---|---|---|
| API retrieval | `run_full.py` | four condition terms in code |
| Condition inclusion | `condition_eligibility.py`, `acute_population_screen.py` | `condition_patterns_cohort.yaml` |
| Intervention categories | `classify_intervention_categories.py` | `intervention_categories.yaml` |
| Outcome categories | `outcome_category.py` | patterns in code |
| Build | `build_revised_cohort.py` | all of the above |
| Freeze + stats | `finalize_cohort.py`, `cohort_report.py` | — |

---

## Tests

```bash
PYTHONPATH=src python -m unittest \
  tests.test_condition_eligibility \
  tests.test_eligibility_text \
  tests.test_cohort_export \
  tests.test_revised_cohort \
  tests.test_intervention_category_validation \
  tests.test_outcome_category_validation \
  tests.test_finalize_cohort -v
```
