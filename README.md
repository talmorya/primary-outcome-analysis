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
| Status & dates | `overall_status`, `study_type`, `phases`, `has_results`, `study_first_post_date`, `study_first_post_date_type`, `start_date`, `primary_completion_date`, `completion_date`, `last_update_post_date`, `status_verified_date` |
| Provenance | `query_source`, `api_version`, `data_timestamp`, `extraction_run_id`, `feature_extraction_version` |

See [Column reference](#column-reference) below for every column.

#### `primary_outcomes.csv` — one row per registered primary outcome

| Field group | Columns |
|---|---|
| Linkage | `outcome_id`, `nct_id`, `primary_outcome_index`, `n_primary_outcomes_in_study` |
| Raw registered text | `primary_outcome_measure`, `primary_outcome_description`, `primary_outcome_time_frame` |
| Exploratory features | `instruments_detected`, `acronyms_detected`, `keywords_matched`, `phrases_matched`, `action_verbs_matched` |
| Outcome purpose (heuristic) | `outcome_purpose`, `outcome_purpose_rule`, `outcome_purpose_review_flag` |
| Denormalized study fields | `brief_title`, `conditions_raw`, `condition_matched`, `behavioral_component`, `intervention_names`, `is_multimodal`, `overall_status`, `study_first_post_date`, `study_type`, `extraction_run_id`, `feature_extraction_version` |

See [Column reference](#column-reference) below for every column.

#### `outcome_annotations_template.csv`

Empty schema for future manual, rule-based, or LLM-assisted annotation. No `outcome_category` assigned at extraction. Column definitions in [Column reference](#column-reference).

### Column reference

**Source types**

| Label | Meaning |
|---|---|
| **Raw (API)** | Copied verbatim (or as a single JSON field) from ClinicalTrials.gov API v2 study JSON |
| **Derived** | Simple aggregation or ID generation from raw fields; no classification rules |
| **Engineered** | Rule-based field produced by pipeline logic and a versioned config or module |

---

#### `studies.csv`

| Column | Source | Description |
|---|---|---|
| `nct_id` | Raw (API) | Registry identifier (`protocolSection.identificationModule.nctId`). |
| `brief_title` | Raw (API) | Short study title (`identificationModule.briefTitle`). |
| `official_title` | Raw (API) | Full official title (`identificationModule.officialTitle`). |
| `conditions_raw` | Derived | Pipe-joined list of registered conditions (`conditionsModule.conditions`). |
| `keywords_raw` | Derived | Pipe-joined condition keywords (`conditionsModule.keywords`). |
| `condition_matched` | Engineered | Local cohort condition label(s): `chronic_back_pain`, `fibromyalgia`, and/or `migraine`. Regex matching against `conditions_raw` + `keywords_raw` via `config/condition_patterns.yaml` (`match_conditions.py`). |
| `condition_review_flag` | Engineered | QC flag: `True` if no target condition matched but condition text exists, or if only `chronic_back_pain` matched when generic “chronic pain” is present (possible ambiguity). |
| `interventions_raw` | Derived | Full JSON string of all registered interventions (`armsInterventionsModule.interventions`). Preserves names, types, descriptions, arm labels. |
| `intervention_names` | Derived | Pipe-joined intervention names extracted from `interventions_raw`. |
| `intervention_types` | Derived | Pipe-joined unique CT.gov intervention types (e.g. `BEHAVIORAL`, `DRUG`). |
| `behavioral_component` | Engineered | Pipe-joined psychological/behavioral approach tags from `config/intervention_taxonomy.yaml` → `approaches`. See [classification logic](#field-definitions-and-classification-logic). |
| `intervention_classification_rule` | Engineered | Pipe-joined rule IDs that fired (e.g. `APP_CBT`, `APP_OTHER_PSYCH`). Audit trail for `behavioral_component`. |
| `intervention_review_flag` | Engineered | QC flag for intervention classification. Set when: no interventions; fallback `other_psychological`; multiple psych tags; any matched taxonomy category with `review_flag: true`; or non-psych-only with no psych tag. Does not exclude the study. |
| `is_multimodal` | Engineered | `True` if `behavioral_component` is non-empty **and** `other_modality_present` is `True` (psych plus another modality). |
| `other_modality_present` | Engineered | `True` if non-psych BEHAVIORAL arms or non-behavioral co-interventions (drug, device, etc.) are present. |
| `other_modality_type` | Engineered | Category label(s) for co-interventions (`other_modality_types` in taxonomy, or fallback to non-psych types). |
| `other_modality_name` | Engineered | Raw intervention name(s) that triggered `other_modality_type`. |
| `non_psychological_behavioral_flag` | Engineered | `True` if any BEHAVIORAL arm matched `non_psychological_behavioral` patterns (exercise, diet, research paradigm, etc.) without also matching a psych approach on the same arm. Informational—not an exclusion flag. |
| `non_psychological_behavioral_type` | Engineered | Non-psych category label(s), e.g. `physical_activity`, `research_paradigm`. |
| `non_psychological_behavioral_name` | Engineered | Raw intervention name(s) that triggered the non-psych flag. |
| `overall_status` | Raw (API) | Recruitment/completion status (`statusModule.overallStatus`). |
| `study_type` | Raw (API) | e.g. `INTERVENTIONAL` (`designModule.studyType`). |
| `phases` | Derived | Pipe-joined trial phases (`designModule.phases`). |
| `has_results` | Raw (API) | Whether posted results exist (top-level `hasResults`). |
| `study_first_post_date` | Raw (API) | First public registration date (`statusModule.studyFirstPostDateStruct.date`). Primary time axis for trend analysis. |
| `study_first_post_date_type` | Raw (API) | Date precision: `ACTUAL` or `ESTIMATED` (`studyFirstPostDateStruct.type`). |
| `start_date` | Raw (API) | Study start date (`statusModule.startDateStruct.date`). |
| `primary_completion_date` | Raw (API) | Primary completion date (`statusModule.primaryCompletionDateStruct.date`). |
| `completion_date` | Raw (API) | Study completion date (`statusModule.completionDateStruct.date`). |
| `last_update_post_date` | Raw (API) | Last registry update (`statusModule.lastUpdatePostDateStruct.date`). |
| `status_verified_date` | Raw (API) | Date status last verified (`statusModule.statusVerifiedDate`). |
| `query_source` | Derived | Human-readable description of the API retrieval query used for this run. |
| `api_version` | Derived | CT.gov API version at extraction time (from `/studies` metadata). |
| `data_timestamp` | Derived | CT.gov data snapshot timestamp at extraction time. |
| `extraction_run_id` | Derived | Pipeline run identifier (e.g. `full_20260823_201251`). |
| `feature_extraction_version` | Derived | Version string from `config/outcome_lexicon.yaml`; links study row to outcome-feature rule set. |

---

#### `primary_outcomes.csv`

| Column | Source | Description |
|---|---|---|
| `outcome_id` | Derived | Stable row ID: `{nct_id}__po_{index}`. |
| `nct_id` | Raw (API) | Parent study identifier. |
| `primary_outcome_index` | Derived | 1-based index of this outcome within the study's registered primary outcomes. |
| `n_primary_outcomes_in_study` | Derived | Total count of primary outcomes registered for the study. |
| `primary_outcome_measure` | Raw (API) | Outcome measure text, verbatim (`outcomesModule.primaryOutcomes[].measure`). |
| `primary_outcome_description` | Raw (API) | Outcome description, verbatim (`primaryOutcomes[].description`). |
| `primary_outcome_time_frame` | Raw (API) | Outcome time frame, verbatim (`primaryOutcomes[].timeFrame`). |
| `instruments_detected` | Engineered | Pipe-joined instrument names matched by word-boundary/phrase rules in `config/outcome_lexicon.yaml` → `instruments` (`extract_outcome_features.py`). Not a conceptual pain-domain category. |
| `acronyms_detected` | Engineered | Acronyms extracted from outcome text via regex (parenthetical and uppercase tokens, with stopword filtering). |
| `keywords_matched` | Engineered | Lexicon keywords found in outcome text (word-boundary match). |
| `phrases_matched` | Engineered | Lexicon phrases found as substrings in outcome text. |
| `action_verbs_matched` | Engineered | Lexicon action verbs found in outcome text (word-boundary match). |
| `outcome_purpose` | Engineered | Exploratory heuristic tag (e.g. `therapeutic_clinical`, `psychological`, `functional`, `feasibility_recruitment`). First-match rule cascade in `outcome_purpose.py`. **Not used to exclude outcomes.** |
| `outcome_purpose_rule` | Engineered | Rule ID that assigned `outcome_purpose` (e.g. `PURPOSE_THERAPEUTIC`). |
| `outcome_purpose_review_flag` | Engineered | QC flag: `True` when purpose is `uncertain` or `other` (including very short outcome text). |
| `feature_extraction_version` | Derived | Version from `config/outcome_lexicon.yaml` used for this row's feature extraction. |
| `brief_title` | Denormalized | Copied from `studies.csv` for convenience. |
| `conditions_raw` | Denormalized | Copied from `studies.csv`. |
| `condition_matched` | Denormalized | Copied from `studies.csv`. |
| `behavioral_component` | Denormalized | Copied from `studies.csv`. Updated if intervention classification is reprocessed. |
| `intervention_names` | Denormalized | Copied from `studies.csv`. |
| `is_multimodal` | Denormalized | Copied from `studies.csv`. Updated if intervention classification is reprocessed. |
| `overall_status` | Denormalized | Copied from `studies.csv`. |
| `study_first_post_date` | Denormalized | Copied from `studies.csv`. |
| `study_type` | Denormalized | Copied from `studies.csv`. |
| `extraction_run_id` | Denormalized | Copied from `studies.csv`. |

**Denormalized** columns duplicate study-level fields onto each outcome row so outcome tables can be filtered without joining. They are not re-derived from outcome text.

---

#### `outcome_annotations_template.csv`

| Column | Source | Description |
|---|---|---|
| `outcome_id` | — | Join key to `primary_outcomes.csv`. |
| `nct_id` | — | Join key to `studies.csv`. |
| `outcome_category` | Manual (future) | Planned conceptual category (pain intensity, interference, etc.). Not assigned at extraction. |
| `instrument_name` | Manual (future) | Confirmed or corrected instrument label. |
| `instrument_subscale` | Manual (future) | Subscale, if applicable. |
| `annotation_method` | Manual (future) | e.g. manual, rule-based, LLM-assisted. |
| `annotator_id` | Manual (future) | Who performed the annotation. |
| `annotation_confidence` | Manual (future) | Annotator confidence level. |
| `annotation_notes` | Manual (future) | Free-text notes. |
| `annotation_version` | Manual (future) | Annotation schema/pass version. |
| `annotated_at` | Manual (future) | Timestamp of annotation. |

### Raw data (immutable)

```
data/raw/full/<run_id>/
├── search_pages/          # Paginated API responses per condition
├── studies/               # One JSON file per cohort NCT ID
└── extraction_manifest.json
```

Raw JSON is never modified after write. Reprocessing intervention classification uses saved JSON + updated `config/intervention_taxonomy.yaml` via `PYTHONPATH=src python -m ctgov_pipeline.reprocess_interventions <run_id>`.

### Field definitions and classification logic

Intervention fields are assigned by scanning each registered intervention arm against `config/intervention_taxonomy.yaml`. Rules are applied per arm, then aggregated to the study level.

#### `behavioral_component`

Pipe-joined psychological/behavioral approach tags (e.g. `cbt | pain_education | motivational_interviewing`). Matched from the `approaches` section of the taxonomy. Empty when no psychological approach matched; falls back to `other_psychological` only when nothing else matched.

#### `non_psychological_behavioral_flag`, `non_psychological_behavioral_type`, `non_psychological_behavioral_name`

Flag and detail fields for BEHAVIORAL arms that match `non_psychological_behavioral` patterns (e.g. exercise, diet, lifestyle, research paradigms) **and did not also match a psychological approach on the same arm**.

- **`non_psychological_behavioral_flag`** — `True` if any arm matched.
- **`non_psychological_behavioral_type`** — category label(s), e.g. `physical_activity | research_paradigm`.
- **`non_psychological_behavioral_name`** — raw intervention name(s) that triggered the match.

`non_psychological_behavioral_flag = True` does **not** mean the study should be excluded. It indicates that a non-psychological behavioral component is present (often exercise-only or lab-paradigm trials typed as BEHAVIORAL on CT.gov). Define the analysis subset separately—for example, studies with an identifiable psychological `behavioral_component`, optionally excluding exercise-only trials.

#### `other_modality_present`, `other_modality_type`, `other_modality_name`

Indicate co-interventions beyond pure psychological BEHAVIORAL content:

- Non-BEHAVIORAL CT.gov types (e.g. `DRUG`, `DEVICE`, `PROCEDURE`) or pattern-matched modalities from `other_modality_types` (e.g. pharmacological, device, complementary_integrative, physical_rehabilitation).
- Also set when `non_psychological_behavioral` arms are present (exercise-only trials have no psych tag but still have another modality present).

- **`other_modality_present`** — `True` if any `other_modality_types` match **or** any non-psychological BEHAVIORAL arm matched.
- **`other_modality_type`** / **`other_modality_name`** — type label(s) and raw name(s). When both drug/device hits and non-psych BEHAVIORAL hits exist, type/name reflect the non-behavioral co-interventions; non-psych BEHAVIORAL detail stays in `non_psychological_behavioral_*`. When **only** non-psych BEHAVIORAL content exists, type/name fall back to the non-psych fields.

#### `is_multimodal`

`True` only when the trial has **both** a psychological component in `behavioral_component` **and** `other_modality_present = True` (psych plus something else: drug, device, exercise arm, etc.).

#### `other_modality_present` vs `is_multimodal`

| Situation | `behavioral_component` | `other_modality_present` | `is_multimodal` |
|---|---|---|---|
| CBT only | `cbt` | False | False |
| CBT + drug | `cbt` | True | **True** |
| CBT + exercise (separate arms) | `cbt` | True | **True** |
| Exercise only (no psych tag) | *(empty)* | True | **False** |
| Research paradigm only (e.g. QST) | *(empty)* | True | **False** |

**Important case:** A trial with a non-psychological BEHAVIORAL arm but no psychological component has `other_modality_present = True` and `is_multimodal = False`. Multimodal specifically means psych **plus** other content—not merely “not psych-only.”

**Bundled descriptions:** When exercise or other non-psych content appears only as a bullet inside a single BEHAVIORAL intervention description (not a separate registered arm), it is not split out. If psych patterns match on that same arm, non-psych patterns on that arm are suppressed. See column reference for `intervention_review_flag`, `condition_review_flag`, and outcome fields.

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
