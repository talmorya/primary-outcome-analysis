# Primary outcome analysis — ClinicalTrials.gov extraction pipeline

Reproducible pipeline for downloading **behavioral interventional** chronic pain trials from ClinicalTrials.gov API v2 and producing structured tables of registered **primary outcomes** (verbatim text plus rule-based features).

**Canonical repository path:**

`~/Library/Mobile Documents/com~apple~CloudDocs/Documents/academic/phd/מחקר/Projects/primary_outcome_analysis`

Remote: `https://github.com/talmorya/primary-outcome-analysis.git`

---

## Research question

Among behavioral interventions for chronic pain, what primary outcomes do researchers register, and how does that vary by intervention type and over time?

**Production extraction** copies outcome text as registered and adds exploratory features (instruments, keywords, legacy intervention taxonomy). It does **not** build the paper’s analytic cohort or assign final outcome categories—that is a separate layer (see [Documentation map](#documentation-map)).

---

## Documentation map

| Document | Use when you need… |
|---|---|
| **This README** | Setup, running **API extraction** (`run_full` / `run_pilot`), layout, **production** `studies.csv` / `primary_outcomes.csv` columns |
| [`FINAL_INCLUSION_RULES.md`](FINAL_INCLUSION_RULES.md) | **Analytic cohort** (696 → 666): condition + intervention inclusion, intervention taxonomy v2, outcome categories, full regex/pattern tables, manual NCT decisions |
| [`COHORT_REPRODUCTION_GUIDE.md`](COHORT_REPRODUCTION_GUIDE.md) | Commands to **build / refresh / freeze** `data/processed/final_cohort/` and verify tests |
| [`data/processed/final_cohort/cohort_report.md`](data/processed/final_cohort/cohort_report.md) | **Only** descriptive statistics for the analytic cohort (regenerated on `finalize_cohort`) |

---

## API retrieval (production extraction)

Default query used by `run_full` (see `src/ctgov_pipeline/run_full.py` for exact parameters):

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND condition ∈ {chronic back pain, fibromyalgia, migraine}
```

Local condition matching (`config/condition_patterns.yaml`) may exclude studies that pass the API filter. Primary-headache expansion and revised condition rules apply only in the **analytic cohort** pipeline—not in the frozen full extraction run.

### Latest full extraction run

| Item | Value |
|---|---|
| Run ID | `full_20260823_201251` |
| Extraction date (UTC) | 2026-08-23T20:12:51 |
| API version | 2.0.5 |
| CT.gov data timestamp | 2026-08-21T09:00:05 |
| **Studies in processed tables** | **674** |
| **Primary outcome rows** | **1,591** |

| Output | Path |
|---|---|
| Processed tables | `data/processed/full/full_20260823_201251/` |
| Raw JSON | `data/raw/full/full_20260823_201251/` |
| Manifest | `data/processed/full/full_20260823_201251/extraction_manifest.json` |

This layer is **immutable** for analysis reproducibility; cohort logic reads from it but does not overwrite it.

---

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Full extraction (~700 API hits → 674 after local condition filter)
PYTHONPATH=src python -m ctgov_pipeline.run_full

# Pilot sample (~40 studies)
PYTHONPATH=src python -m ctgov_pipeline.run_pilot

# Extraction / feature tests
PYTHONPATH=src python -m unittest discover -s tests -v
```

**Analytic cohort** (separate from extraction):

```bash
PYTHONPATH=src python -m ctgov_pipeline.build_revised_cohort
PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort
```

Details, refresh-without-raw-JSON, and test list: [`COHORT_REPRODUCTION_GUIDE.md`](COHORT_REPRODUCTION_GUIDE.md).

---

## Production outputs (`data/processed/full/<run_id>/`)

Two main tables plus an annotation template. Column definitions below apply to this **extraction** layer only—not to `data/processed/final_cohort/` (different schema; see `FINAL_INCLUSION_RULES.md`).

### `studies.csv` — one row per trial

High-level groups: identification, conditions (`condition_matched`, `condition_review_flag`), raw interventions JSON, **legacy** `behavioral_component` taxonomy (`config/intervention_taxonomy.yaml`), multimodal / non-psych behavioral flags, status and dates, provenance (`extraction_run_id`, `feature_extraction_version`).

### `primary_outcomes.csv` — one row per registered primary outcome

Linkage (`outcome_id`, `nct_id`, indices), verbatim measure/description/time frame, lexicon-based features (`instruments_detected`, etc.), exploratory `outcome_purpose` (not exclusion), denormalized study fields.

### `outcome_annotations_template.csv`

Empty schema for future manual annotation.

### Raw data (immutable)

```
data/raw/full/<run_id>/
├── search_pages/
├── studies/              # one JSON per NCT ID
└── extraction_manifest.json
```

Re-run legacy intervention labels on a saved run:

```bash
PYTHONPATH=src python -m ctgov_pipeline.reprocess_interventions full_20260823_201251
```

---

## Column reference (production extraction only)

**Source types:** **Raw (API)** — from CT.gov JSON; **Derived** — joins/IDs; **Engineered** — config-driven rules.

### `studies.csv`

| Column | Source | Description |
|---|---|---|
| `nct_id` | Raw (API) | Registry ID (`identificationModule.nctId`). |
| `brief_title` | Raw (API) | `identificationModule.briefTitle`. |
| `official_title` | Raw (API) | `identificationModule.officialTitle`. |
| `conditions_raw` | Derived | Pipe-joined `conditionsModule.conditions`. |
| `keywords_raw` | Derived | Pipe-joined `conditionsModule.keywords`. |
| `condition_matched` | Engineered | Labels from `config/condition_patterns.yaml` (`match_conditions.py`). |
| `condition_review_flag` | Engineered | QC when matching is ambiguous or empty. |
| `interventions_raw` | Derived | JSON of `armsInterventionsModule.interventions`. |
| `intervention_names` | Derived | Pipe-joined intervention names. |
| `intervention_types` | Derived | Pipe-joined CT.gov types (e.g. `BEHAVIORAL`, `DRUG`). |
| `behavioral_component` | Engineered | Legacy psych approach tags (`intervention_taxonomy.yaml`). |
| `intervention_classification_rule` | Engineered | Rule IDs for `behavioral_component`. |
| `intervention_review_flag` | Engineered | QC for taxonomy assignment. |
| `is_multimodal` | Engineered | Psych `behavioral_component` plus `other_modality_present`. |
| `other_modality_*` | Engineered | Non-psych co-interventions (see taxonomy). |
| `non_psychological_behavioral_*` | Engineered | Exercise/diet/paradigm-style BEHAVIORAL arms (informational). |
| `overall_status`, `study_type`, `phases`, `has_results` | Raw/Derived | Design and status modules. |
| `study_first_post_date`, date fields | Raw (API) | Status module dates. |
| `query_source`, `api_version`, `data_timestamp`, `extraction_run_id`, `feature_extraction_version` | Derived | Run provenance. |

### `primary_outcomes.csv`

| Column | Source | Description |
|---|---|---|
| `outcome_id` | Derived | `{nct_id}__po_{index}`. |
| `nct_id`, `primary_outcome_index`, `n_primary_outcomes_in_study` | Derived | Linkage and ordering. |
| `primary_outcome_measure`, `description`, `time_frame` | Raw (API) | Verbatim registered text. |
| `instruments_detected`, `acronyms_detected`, `keywords_matched`, `phrases_matched`, `action_verbs_matched` | Engineered | `outcome_lexicon.yaml` / `extract_outcome_features.py`. |
| `outcome_purpose`, `outcome_purpose_rule`, `outcome_purpose_review_flag` | Engineered | Exploratory purpose tags (`outcome_purpose.py`). |
| Denormalized study columns | Denormalized | Copy of selected `studies.csv` fields for filtering without joins. |

### Legacy intervention / multimodal logic (extraction taxonomy)

Intervention fields use `config/intervention_taxonomy.yaml` (approaches + non-psych patterns). Summary:

- **`behavioral_component`** — psychological approach tags; empty if none matched.
- **`non_psychological_behavioral_flag`** — exercise/diet/paradigm BEHAVIORAL arms without psych on same arm; does not exclude studies.
- **`is_multimodal`** — requires psych in `behavioral_component` **and** `other_modality_present` (not “exercise-only” trials).

For the **analytic cohort**, intervention labels use `config/intervention_categories.yaml` v2 (`intervention_categories`, active-arm comparators, etc.)—documented in `FINAL_INCLUSION_RULES.md`.

---

## Project layout

```
config/                      # condition_patterns, intervention_taxonomy, intervention_categories, outcome_lexicon
src/ctgov_pipeline/          # fetch, parse, extract, run_full, cohort builders
tests/
data/raw/                    # API JSON (gitignored)
data/processed/full/         # Production extraction tables (gitignored)
data/processed/final_cohort/ # Frozen analytic cohort (tracked in git)
reports/                     # Exploration QC and revised_cohort review layer
FINAL_INCLUSION_RULES.md     # Cohort + classification spec
COHORT_REPRODUCTION_GUIDE.md # How to rebuild final_cohort
```

---

## Reproducibility (extraction)

Each full run writes `extraction_manifest.json` (API version, data timestamp, query, filter stats, NCT list). Config versions live under `config/`. Cohort freezes add `data/processed/final_cohort/cohort_manifest.json`.
