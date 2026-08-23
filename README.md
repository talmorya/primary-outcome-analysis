# Primary outcome analysis — ClinicalTrials.gov extraction pipeline

Reproducible pipeline for extracting registered primary outcomes from **behavioral interventional** chronic pain trials on ClinicalTrials.gov API v2.

## Research scope

Among behavioral/psychological interventions for chronic pain, what kinds of primary outcomes do researchers register, and how does this differ across intervention approaches and over time?

The pipeline preserves all registered primary outcomes verbatim. Conceptual categories (pain intensity vs interference vs coping) are **not** assigned at extraction time.

## Cohort definition

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND condition ∈ {chronic back pain, fibromyalgia, migraine}
```

- **IBS excluded**
- CT.gov `BEHAVIORAL` is broad (CBT, mindfulness, exercise, lifestyle, etc.); non-psychological behavioral trials are **flagged**, not excluded
- Local condition validation applied after API retrieval (33 studies excluded in full run for no target-condition match)

## Full extraction (latest run)

| Item | Value |
|---|---|
| Run ID | `full_20260823_201251` |
| Extraction date (UTC) | 2026-08-23T20:12:51 |
| API version | 2.0.5 |
| CT.gov data timestamp | 2026-08-21T09:00:05 |
| API counts by condition | chronic back pain: 330; fibromyalgia: 233; migraine: 153 |
| Deduplicated unique NCT IDs (API) | 707 |
| **Cohort studies (after local filter)** | **674** |
| **Primary outcome rows** | **1,591** |

Processed files: `data/processed/full/full_20260823_201251/`  
Raw JSON: `data/raw/full/full_20260823_201251/`  
Manifest: `data/processed/full/full_20260823_201251/extraction_manifest.json`

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Full extraction (~700 studies)
PYTHONPATH=src python -m ctgov_pipeline.run_full

# Pilot sample (~40 studies)
PYTHONPATH=src python -m ctgov_pipeline.run_pilot

# Tests
PYTHONPATH=src python -m unittest tests.test_instrument_extraction -v
```

## What the pipeline creates

### Two structured tables (no third analysis table)

#### `studies.csv` — one row per interventional trial

| Field group | Columns |
|---|---|
| Identification | `nct_id`, `brief_title`, `official_title` |
| Conditions | `conditions_raw`, `keywords_raw`, `condition_matched`, `condition_review_flag` |
| Interventions (raw) | `interventions_raw`, `intervention_names`, `intervention_types` |
| Behavioral classification | `behavioral_component`, `intervention_classification_rule`, `intervention_review_flag` |
| Multimodal | `is_multimodal`, `other_modality_present`, `other_modality_type`, `other_modality_name` |
| Non-psych behavioral flag | `non_psychological_behavioral_flag`, `non_psychological_behavioral_type`, `non_psychological_behavioral_name` |
| Status & dates | `overall_status`, `study_type`, `phases`, `has_results`, `study_first_post_date` (+ other dates) |
| Provenance | `query_source`, `api_version`, `data_timestamp`, `extraction_run_id` |

#### `primary_outcomes.csv` — one row per registered primary outcome

| Field group | Columns |
|---|---|
| Linkage | `outcome_id`, `nct_id`, `primary_outcome_index`, `n_primary_outcomes_in_study` |
| Raw registered text | `primary_outcome_measure`, `primary_outcome_description`, `primary_outcome_time_frame` |
| Exploratory features | `instruments_detected`, `acronyms_detected`, `keywords_matched`, `phrases_matched`, `action_verbs_matched` |
| Outcome purpose (heuristic) | `outcome_purpose`, `outcome_purpose_rule`, `outcome_purpose_review_flag` |
| Denormalized study fields | `brief_title`, `condition_matched`, `behavioral_component`, `is_multimodal`, `study_first_post_date`, etc. |

#### `outcome_annotations_template.csv`

Empty schema for future manual, rule-based, or LLM-assisted annotation. No `outcome_category` assigned at extraction.

### Raw data (immutable)

```
data/raw/full/<run_id>/
├── search_pages/          # Paginated API responses per condition
├── studies/               # One JSON file per cohort NCT ID
└── extraction_manifest.json
```

Raw JSON is never modified after write. Reprocessing uses saved JSON + config files.

### Exploratory fields (not conceptual categories)

- **instruments_detected** — controlled phrase/acronym matching (word-boundary fix prevents substring false positives)
- **acronyms_detected**, **keywords_matched**, **phrases_matched**, **action_verbs_matched** — matched text only

### Multimodal representation

When a trial combines a psychological/behavioral component with another modality:

- `behavioral_component` — e.g. `cbt | pain_education`
- `is_multimodal = True`
- `other_modality_type` — e.g. `physical_rehabilitation | device`
- `other_modality_name` — raw intervention name(s)

Trials with only behavioral/psychological interventions: `is_multimodal = False`.

### `outcome_purpose` (exploratory heuristic only)

Rule-based tags such as `therapeutic_clinical`, `psychological`, `functional`, `feasibility_recruitment`, `acceptability_satisfaction`, `biological_physiological`, `safety_adverse_events`, `other`, `uncertain`.

**Not used to exclude, filter, or quantitatively classify outcomes.** All registered primary outcomes are retained regardless of `outcome_purpose`. Final categorization will use the separate annotation layer.

## Project layout

```
config/                   # Condition patterns, intervention taxonomy, outcome lexicon
src/ctgov_pipeline/       # fetch, parse, classify, feature extraction, run_full, run_pilot
tests/                    # Instrument extraction regression tests
data/raw/                 # Immutable API JSON (gitignored)
data/processed/           # studies.csv, primary_outcomes.csv (gitignored)
reports/                  # Pilot and extraction summaries
```

## Reproducibility

Each run writes `extraction_manifest.json` with API version, data timestamp, query criteria, filter stats, and cohort NCT IDs. Config files are versioned in `config/`.
