# Data column dictionary

Canonical outputs: **`data/processed/`**

| File | Rows |
|---|---|
| `studies.csv` | One row per trial in the API master pool |
| `primary_outcomes.csv` | One row per registered primary outcome (all pool studies) |

Filter to included studies with `cohort_inclusion_status == included`.

**`raw_` prefix:** columns copied from the CT.gov record (verbatim, or only joined / truncated for readability: `raw_brief_summary_50w`, `raw_intervention_details`). Everything without the prefix is derived by this pipeline (status, exclusion, eligibility flags, intervention/outcome classifications) or is an identifier / provenance field (`nct_id`, `extraction_run_id`, `api_retrieval_queries`).

Manifest: `manifest.json` lists extraction run id and file paths.

---

## `studies.csv`

### Inclusion / exclusion

| Column | Type | Description |
|---|---|---|
| `nct_id` | string | ClinicalTrials.gov identifier |
| `cohort_inclusion_status` | `included` \| `excluded` | Analytic cohort membership after condition stage only |
| `exclusion_reason` | `acute` \| `condition` | **General** reason for exclusion; empty when included |
| `exclusion_detail` | string | **Specific** explanation. Starts with the rule key (`acute_pain`, `no_target_match`, `cancer_oncology`, …), then why this study hit it (matched text / source). Rules: `docs/COHORT_FILTERING_RULES.md` |

### Text for manual review (verbatim from registration)

| Column | Description |
|---|---|
| `raw_brief_title` | Brief title |
| `raw_official_title` | Official title |
| `raw_brief_summary_50w` | Brief summary truncated to **50 words** (ellipsis if cut) |
| `raw_conditions` | Pipe-separated registered conditions |
| `raw_keywords` | Pipe-separated CT.gov keywords (not used for acute exclusion) |
| `raw_eligibility_criteria` | Full eligibility criteria text |

### Condition assignment (descriptive)

| Column | Description |
|---|---|
| `condition_matched` | Pipe-separated target keys matched in the **registered conditions section** (`migraine`, `chronic_back_pain`, …) |
| `condition_feature_flags` | Pipe-separated non-excluding feature tags (e.g. post-traumatic) |
| `eligible_migraine` | Target found in registered conditions (flags are not mutually exclusive) |
| `eligible_chronic_back_pain` | Target found in registered conditions |
| `eligible_fibromyalgia` | Target found in registered conditions |
| `eligible_headache` | Target found in registered conditions (headache types other than plain migraine; may co-occur with migraine) |

### Intervention (descriptive; no exclusion)

| Column | Description |
|---|---|
| `intervention_categories` | Pipe-separated taxonomy keys from **active** arms (e.g. `psychological_cognitive`, `education_self_management`) |
| `is_multimodal` | Active arm includes non-behavioral modality |
| `control_arm_types` | Comparator types detected from arm names (placebo, usual care, …) |
| `raw_intervention_names` | Pipe-separated intervention names |
| `raw_intervention_details` | Readable arm text for checking the classification: `name [TYPE]: description`, arms joined by ` \|\| ` |

Not exported (redundant): `intervention_category_labels`, `intervention_classification_rule`, raw JSON arm dumps.

### Study metadata

| Column | Description |
|---|---|
| `raw_overall_status` | CT.gov overall status |
| `raw_study_first_post_date` | First posted date (YYYY-MM-DD) |
| `raw_phases` | Pipe-separated phases |
| `raw_primary_purpose` | Design primary purpose |
| `raw_has_results` | Whether results posted |
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
| `raw_primary_outcome_measure` | Verbatim measure |
| `raw_primary_outcome_description` | Verbatim description |
| `raw_primary_outcome_time_frame` | Verbatim time frame |
| `outcome_category` | Descriptive top-level category |
| `outcome_subcategory` | Descriptive subcategory |
| `outcome_category_rule` | Which classifier rule assigned the category (to audit a classification) |
| `outcome_category_review_flag` | `True` when the assignment is uncertain / `other` and worth a manual look |
| `outcome_is_mechanistic` | Row-level mechanistic flag |
| `instruments_detected` | Pipe-separated instrument hits from lexicon |
| `raw_study_first_post_date` | From study |
| `extraction_run_id` | Raw run id |

Raw outcome text must not be altered for analysis; use annotation templates separately for conceptual coding.

---

## Related files

| Path | Role |
|---|---|
| `data/raw/full/<run_id>/studies/*.json` | Immutable API source |
| `data/processed/cohort_report.md` | Counts and distributions (included only) |
| `config/condition_patterns_cohort.yaml` | Target and exclusion patterns |
| `config/intervention_categories.yaml` | Intervention taxonomy |
| `config/outcome_lexicon.yaml` | Instrument / keyword extraction |
