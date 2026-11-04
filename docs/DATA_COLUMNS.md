# Data column dictionary

Canonical outputs: **`data/processed/cohort/`**

| File | Rows |
|---|---|
| `studies.csv` | One row per trial in the API master pool |
| `primary_outcomes.csv` | One row per registered primary outcome (all pool studies) |

Filter to included studies with `cohort_inclusion_status == included`.

Manifest: `manifest.json` lists extraction run id and file paths.

---

## `studies.csv`

### Inclusion / exclusion

| Column | Type | Description |
|---|---|---|
| `nct_id` | string | ClinicalTrials.gov identifier |
| `cohort_inclusion_status` | `included` \| `excluded` | Analytic cohort membership after condition stage only |
| `exclusion_reason` | `acute` \| `condition` | **General** reason for exclusion; empty when included |
| `exclusion_detail` | string | **Specific** explanation. Starts with the rule key (`acute_pain`, `no_target_match`, `population_non_target_conditions`, …), then why this study hit it (matched text / source / non-target conditions). Rules: `docs/COHORT_FILTERING_RULES.md` |

### Text for manual review (verbatim from registration)

| Column | Description |
|---|---|
| `brief_title` | Brief title |
| `official_title` | Official title |
| `brief_summary_50w` | Brief summary truncated to **50 words** (ellipsis if cut) |
| `conditions_raw` | Pipe-separated registered conditions |
| `keywords_raw` | Pipe-separated CT.gov keywords (not used for acute exclusion) |
| `eligibility_criteria` | Full eligibility criteria text |

### Condition assignment (descriptive)

| Column | Description |
|---|---|
| `condition_matched` | Pipe-separated target keys that matched (`migraine`, `chronic_back_pain`, …) |
| `condition_feature_flags` | Pipe-separated non-excluding feature tags (e.g. post-traumatic) |
| `eligible_migraine` | Boolean target flag |
| `eligible_chronic_back_pain` | Boolean target flag |
| `eligible_fibromyalgia` | Boolean target flag |
| `eligible_headache` | Boolean target flag (non-migraine headache emphasis) |

### Intervention (descriptive; no exclusion)

| Column | Description |
|---|---|
| `intervention_categories` | Pipe-separated taxonomy keys from **active** arms (e.g. `psychological_cognitive`, `education_self_management`) |
| `is_multimodal` | Active arm includes non-behavioral modality |
| `control_arm_types` | Comparator types detected from arm names (placebo, usual care, …) |
| `intervention_names` | Pipe-separated intervention names |
| `intervention_details` | Readable arm text for checking the classification: `name [TYPE]: description`, arms joined by ` \|\| ` |

Not exported (redundant): `intervention_category_labels`, `intervention_classification_rule`, raw JSON arm dumps.

### Study metadata

| Column | Description |
|---|---|
| `overall_status` | CT.gov overall status |
| `study_first_post_date` | First posted date (YYYY-MM-DD) |
| `phases` | Pipe-separated phases |
| `primary_purpose` | Design primary purpose |
| `has_results` | Whether results posted |
| `primary_outcome_mechanistic` | Study-level flag: all primaries mechanistic by lexicon |
| `api_retrieval_queries` | Which condition search(es) retrieved the trial |
| `extraction_run_id` | Raw JSON folder name under `data/raw/full/` |
| `cohort_rules_version` | Cohort rule set version string |

---

## `primary_outcomes.csv`

| Column | Description |
|---|---|
| `outcome_id` | Stable id `{nct_id}__po_{index}` |
| `nct_id` | Study link |
| `cohort_inclusion_status` | Same as study row (filter with study table) |
| `primary_outcome_index` | 1-based index among primaries |
| `n_primary_outcomes_in_study` | Count of primaries for this trial |
| `primary_outcome_measure` | Verbatim measure |
| `primary_outcome_description` | Verbatim description |
| `primary_outcome_time_frame` | Verbatim time frame |
| `outcome_category` | Descriptive top-level category |
| `outcome_subcategory` | Descriptive subcategory |
| `outcome_category_rule` | Which classifier rule assigned the category (to audit a classification) |
| `outcome_category_review_flag` | `True` when the assignment is uncertain / `other` and worth a manual look |
| `outcome_is_mechanistic` | Row-level mechanistic flag |
| `instruments_detected` | Pipe-separated instrument hits from lexicon |
| `study_first_post_date` | From study |
| `extraction_run_id` | Raw run id |

Raw outcome text must not be altered for analysis; use annotation templates separately for conceptual coding.

---

## Related files

| Path | Role |
|---|---|
| `data/raw/full/<run_id>/studies/*.json` | Immutable API source |
| `data/processed/cohort/cohort_report.md` | Counts and distributions (included only) |
| `config/condition_patterns_cohort.yaml` | Target and exclusion patterns |
| `config/intervention_categories.yaml` | Intervention taxonomy |
| `config/outcome_lexicon.yaml` | Instrument / keyword extraction |
