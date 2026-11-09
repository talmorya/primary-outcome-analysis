# CLAUDE.md — AI context for primary_outcome_analysis

## Project purpose

Reproducible ClinicalTrials.gov API v2 pipeline for studying **registered primary outcomes** in **behavioral interventional** chronic pain trials.

**Research question:** Among behavioral/psychological interventions for chronic pain, what primary outcomes do researchers register, and how does this differ across intervention approaches and over time (`raw_study_first_post_date`)?

**Motivating hypothesis (to test empirically, not assume):** CBT/ACT/acceptance-oriented approaches may emphasize interference, functioning, coping, or adaptation; PRT/pain-reprocessing/pain-education approaches may more often target pain intensity/severity.

---

## Cohort definition (do not change without explicit approval)

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND registered Conditions field contains any of (back pain, fibromyalgia, migraine, headache)
```

- **IBS excluded** at condition-matching stage
- All trial statuses retained (`raw_overall_status` is a variable, not a filter)
- Local condition validation post-API (`config/condition_patterns_cohort.yaml`)
- **Inclusion:** the registered conditions must match a target pattern (keywords/titles never qualify a trial); condition stage only (`docs/COHORT_FILTERING_RULES.md`); acute population rules in `acute_population_screen.py`

Latest extraction run: `full_20261109_104453`. Analytic tables: `data/processed/studies.csv` (see `manifest.json` for counts).

---

## Critical constraints

1. **Preserve raw outcome text verbatim** — `raw_primary_outcome_measure`, `raw_primary_outcome_description`, `raw_primary_outcome_time_frame`
2. **Outcome categories are descriptive only** — `outcome_category` / `outcome_subcategory` in `primary_outcomes.csv` are rule-based aids for review, never used to include/exclude. The researcher's conceptual coding (pain intensity, interference, coping, etc.) is a separate manual layer; do not overwrite raw outcome text with it
3. **`outcome_purpose` is exploratory/heuristic only** — do not use it to exclude, filter, or quantitatively classify outcomes
4. **Two-table architecture only** — `data/processed/studies.csv` + `primary_outcomes.csv`. One current version of raw and processed data; no third analysis table, no per-rule audit files
5. **Raw JSON is immutable** — reprocess from `data/raw/` rather than re-querying CT.gov unless starting a new extraction run
6. **Instrument matching uses word-boundary logic** — do not revert to substring matching (caused ISI false positives). Run `tests/test_instrument_extraction.py` after lexicon changes

---

## Key paths

| Path | Contents |
|---|---|
| `data/raw/full/<run_id>/studies/` | Per-NCT JSON (gitignored; keep one run) |
| `data/processed/studies.csv` | Master pool + inclusion columns |
| `data/processed/primary_outcomes.csv` | Primary outcomes |
| `docs/COHORT_FILTERING_RULES.md` | Inclusion / exclusion rules |
| `docs/DATA_COLUMNS.md` | Column dictionary |
| `config/condition_patterns_cohort.yaml` | Target conditions, exclusion patterns, acute patterns |
| `config/intervention_categories.yaml` | Intervention category taxonomy (active arms only) |
| `config/outcome_lexicon.yaml` | Instrument/keyword extraction (not categories) |
| `src/ctgov_pipeline/` | Pipeline modules |
| `data/processed/cohort_report.md` | Auto-generated statistics |

---

## Pipeline commands

```bash
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort   # rebuild cohort from raw JSON (no network)
PYTHONPATH=src python -m unittest discover -s tests -v    # all tests
PYTHONPATH=src python -m ctgov_pipeline.run_full          # NEW CT.gov pull (creates a new raw run; delete the old one)
```

---

## Data model essentials

### `studies.csv` (all retrieved trials; filter `cohort_inclusion_status == included`)
- `exclusion_reason` = `acute` | `condition`; `exclusion_detail` starts with the rule key then the specific cause
- `raw_` prefix = copied from the CT.gov record (`raw_brief_summary_50w`, `raw_eligibility_criteria`, `raw_conditions`, `raw_intervention_details`, …); unprefixed = derived by the pipeline. Raw text kept so classifications and exclusions can be audited
- `intervention_categories` (active arms), `is_multimodal`, `control_arm_types`

### `primary_outcomes.csv`
- Linked by `nct_id`; unit of analysis for outcome-selection trends
- Verbatim `raw_primary_outcome_*` text + descriptive `outcome_category`, `outcome_subcategory`, `outcome_category_rule`, `outcome_category_review_flag`
- Full definitions: `docs/DATA_COLUMNS.md`

---

## Known limits (as of the current run)

- **Conditions-field pull:** trials whose registered condition is only generic (e.g. `Chronic Pain`) are not retrieved, even if the title names a target (e.g. NCT00796536, NCT01794988, NCT01993355). Intended (AND of all filters).
- **Judgment call:** NCT03157544 (chronic neck/LBP during an acute flare) is included.
- **Relevance review (Nov 2026), suspected-irrelevant groups found among included trials:** `pregnancy_related` (15) is now an exclusion rule; `provider_or_system_level` (20) is a `review_flags` tag. Reviewed but **not** acted on: target is one of many conditions and the title is not about pain (~41, e.g. arthritis/ME-CFS/tinnitus programs), peri-operative or post-surgical course (~16), concussion/TBI as the primary population (~10), healthy or non-patient samples (~6), asymptomatic prevention/school groups (~10-15), back pain with no duration stated (~47). Revisit if the cohort needs tightening.
- **Classification QC targets:** ~20% of included outcome rows are `outcome_category = other` (many flagged by `outcome_category_review_flag`); ~25% of studies sit in `other_behavioral_treatment`.
- `run_full` still writes a legacy extraction layer to `data/processed/full/` (gitignored, unused by the cohort).

---

## Code conventions

- Match existing style in `src/ctgov_pipeline/`
- Config-driven rules in YAML under `config/`
- Minimize scope — focused diffs, no over-engineering
- Do not commit secrets or raw data (`data/raw/` is gitignored; only the four analytic files directly in `data/processed/` are tracked)

---

## Git workflow

**Commit and push as you work** so progress is never lost. Do not leave completed changes uncommitted at the end of a session.

- **Remote:** https://github.com/talmorya/primary-outcome-analysis
- **Branch:** work on `main` (or the active feature branch if the user specifies one)
- **When to commit:** after completing a logical unit of work (pipeline change, config update, report, fix, documentation)
- **Commit messages:** short, imperative, describe *why* — e.g. `Add CLAUDE.md with project context and git workflow`, `Fix instrument boundary matching for ISI false positives`
- **Push:** after each commit (or a small batch of related commits), push to the remote branch: `git push origin HEAD`
- **Do not:** force-push, commit gitignored data blobs, or modify unrelated branches
- **Verify:** confirm push succeeded (`git status` shows up to date with remote)

Human docs: `README.md`
