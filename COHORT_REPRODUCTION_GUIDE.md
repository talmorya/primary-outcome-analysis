# Cohort reproduction guide

How to reproduce the finalized analytic cohort (`final_cohort_20260922`, **664 studies**).

---

## Data sources

| Asset | Location | Notes |
|---|---|---|
| Raw CT.gov JSON (674 studies) | `data/raw/full/full_20260823_201251/studies/` | Gitignored; required for rebuild |
| Production extraction tables | `data/processed/full/full_20260823_201251/` | Gitignored; **not modified** by cohort finalization |
| Headache expansion JSON | `reports/exploration/headache_candidates_raw.json` | 22 curated primary-headache studies |
| **Final cohort output** | `data/processed/final_cohort/` | Tracked in git |

**API retrieval** (original extraction, August 2026):

- Endpoint: `https://clinicaltrials.gov/api/v2/studies`
- API version: 2.0.5
- Query: interventional + behavioral + condition filters (see `FINAL_INCLUSION_RULES.md`)
- Re-run full extraction: `PYTHONPATH=src python -m ctgov_pipeline.run_full`

---

## Pipeline steps

```bash
source .venv/bin/activate
pip install -r requirements.txt

# 1. Build/review cohort (writes reports/exploration/revised_cohort/)
PYTHONPATH=src python -m ctgov_pipeline.build_revised_cohort

# 2. Freeze final cohort (writes data/processed/final_cohort/)
PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort

# 3. Verify
PYTHONPATH=src python -m unittest tests.test_finalize_cohort tests.test_revised_cohort tests.test_condition_eligibility -v
```

`finalize_cohort` regenerates the review layer, validates 664 eligible studies, and copies outputs to `data/processed/final_cohort/`.

---

## Inclusion / exclusion logic

Three sequential stages (all must pass):

1. **Condition** — `condition_eligibility.py` + `config/condition_patterns_proposed.yaml`
2. **Intervention** — `classify_intervention_categories.py` + `intervention_eligibility.py` + `config/intervention_categories.yaml`
3. **Mechanism** — `outcome_mechanism.py` (outcome-based negative filter)

Full rule definitions: `FINAL_INCLUSION_RULES.md`

---

## Key config and code files

| File | Role |
|---|---|
| `config/condition_patterns_proposed.yaml` | Condition matching and exclusions |
| `config/intervention_categories.yaml` | Intervention taxonomy |
| `config/outcome_lexicon.yaml` | Instrument/keyword extraction (not categories) |
| `src/ctgov_pipeline/build_revised_cohort.py` | Cohort builder |
| `src/ctgov_pipeline/finalize_cohort.py` | Freeze to `data/processed/final_cohort/` |
| `src/ctgov_pipeline/condition_eligibility.py` | Condition stage |
| `src/ctgov_pipeline/outcome_mechanism.py` | Mechanism stage + flags |
| `src/ctgov_pipeline/outcome_category.py` | Outcome category annotation |

---

## Important manual decisions (frozen)

| NCT ID | Decision |
|---|---|
| **NCT00864422** | KEEP. Mechanistic primaries (TMS cortical map); clinical pain/function in secondary outcomes. `primary_outcome_mechanistic=TRUE`, `has_clinical_outcome_anywhere=TRUE`. |
| **NCT01118988** | KEEP. Heterogeneous chronic pain conditions retained; no IBS-first heterogeneity exclusion. |

Other QC decisions (e.g. excluding visual snow, vestibular schwannoma, ME/CFS-primary studies) are encoded in config rules, not manual overrides.

---

## Output files (`data/processed/final_cohort/`)

| File | Description |
|---|---|
| `studies.csv` | All 696 studies with inclusion flags and study-level metadata |
| `primary_outcomes.csv` | Primary outcome rows with category annotations |
| `exclusion_audit.csv` | Per-study audit trail |
| `cohort_manifest.json` | Run metadata and manual decisions |
| `cohort_report.md` | Auto-generated summary report |

**Analytic subset:** filter `cohort_included == True` in both tables.

---

## Limitations

1. **CT.gov `BEHAVIORAL` is broad** — includes exercise, lifestyle, and complementary trials; captured via intervention categories rather than a psych-only filter.
2. **Condition matching is text-based** — relies on registered conditions/keywords/titles; co-listed conditions may not reflect true enrollment focus.
3. **Outcome-based mechanism filter uses lexicons** — may miss uncommon clinical endpoints or misclassify ambiguous labels; `primary_outcome_mechanistic` flag supports sensitivity analyses.
4. **Outcome categories are heuristic** — large `other/other` bucket remains; not used for inclusion.
5. **Headache expansion is curated** — 22 studies added beyond API query; list in `build_revised_cohort.py` (`HEADACHE_EXPANSION_NCTS`).
6. **Raw JSON required** — cohort rebuild needs local raw files; not committed to git.
7. **Production extraction frozen** — `full_20260823_201251` tables are unchanged; final cohort is a separate derived layer.
