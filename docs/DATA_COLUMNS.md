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
| `exclusion_reason` | `acute` \| `condition` | **General** reason for exclusion; empty when included. Rules `acute_pain`, `short_pain_window` → `acute`; all others (incl. `not_about_pain`) → `condition` |
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
| `pain_duration_inclusion` | Verbatim inclusion-criteria sentence(s) that state how long the pain/condition lasts (heuristic; empty if none found). Never used to include/exclude. |

### Condition assignment (descriptive)

| Column | Description |
|---|---|
| `condition_matched` | Pipe-separated target keys matched in the **registered conditions section** (`migraine`, `back_pain`, …) |
| `review_flags` | Pipe-separated descriptive review tags from the titles, never used to exclude. Currently `provider_or_system_level` (clinician / guideline / implementation / decision-support / care-model wording); expect some false positives. Patterns: `review_flags` in `config/condition_patterns_cohort.yaml` |
| `condition_feature_flags` | Pipe-separated feature tags (`post_traumatic`, `tbi_concussion`, `subacute`, `perioperative`, `surgical_postoperative`, …). `subacute`, `perioperative` and `surgical_postoperative` exclude the trial (`subacute_perioperative`); the rest are descriptive. |
| `eligible_migraine` | Target found in registered conditions (flags are not mutually exclusive) |
| `eligible_back_pain` | Target found in registered conditions |
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
| `api_retrieval_queries` | Which condition search(es) retrieved the trial: `back_pain`, `fibromyalgia`, `migraine`, `headache` |
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

### Outcome category mapping (`src/ctgov_pipeline/outcome_category.py`)

Descriptive only (never used to include or exclude). Rules run top to bottom on the lower-cased text, and the first match wins. **Pass 1** reads measure + description + time frame; **Pass 2** reads the **measure name only** and is reached only by outcomes that matched nothing in Pass 1, so it cannot move an outcome out of a Pass-1 category. Counts are for the 1,900 primary-outcome rows of included trials.

| Category / subcategory (n) | Text patterns (abridged) |
|---|---|
| **mechanistic** (162): `neuroimaging_neural` 25, `sensory_qst` 37, `biomarker_inflammatory` 15, `psychophysiological` 6, `other_mechanistic` 31 | Checked first (`MECHANISTIC_PATTERNS`): fMRI, EEG, MRI, connectivity, brain activity, HRV, cortisol, cytokine/biomarker, QST, pain threshold/tolerance, pressure pain, CPM, hyperalgesia, experimental pain, psychophysical … |
| mechanistic / `biological_structural` (48) *(Pass 2)* | serum, plasma, blood, hormone, CRP, interleukin, BDNF, microbiome, cortisol, gray matter, brain, cerebral, BOLD, heart rate, glucose/HbA1c/diabetes, temperature, muscle tone, tissue thickness/ultrasound/fascia, noxious inhibitory control |
| **feasibility_acceptability** (356): `safety` 23 | adverse, safety, side effect, tolerability |
| `feasibility_recruitment` (182) | feasibility, recruitment, enrollment, accrual, screening/eligibility rate; *Pass 2:* eligible, consent, proportion randomized, program initiation, intervention commencement |
| `acceptability_satisfaction` (70) | acceptability, satisfaction, usability, user/participant experience; *Pass 2:* credibility, expectancy, perceptions of intervention, trust score, appropriateness, continued interest, willingness to pay, adoption, barriers and facilitators |
| `adherence_fidelity` (54) | adherence, compliance, fidelity, treatment integrity; *Pass 2:* attend-, usage, engagement, participation rate, at-home practice, intervention/treatment completion, uptake, homework, contamination |
| `other_feasibility` (27) | retention/completion/drop-out rate; *Pass 2:* retention, drop-out, withdrawal, attrition, assessment/questionnaire completion |
| **mood** (161): `anxiety` 49 | anxiety, panic, STAI, BAI, GSI |
| `depression` 31 · `catastrophizing` 12 · `distress_stress` 37 | depress-, PHQ, Beck, CES-D, HAM-D · catastroph-, PCS · distress, stress, mood; *Pass 2:* BSI / Brief Symptom Inventory |
| `fear_avoidance` 10 *(Pass 2)* | kinesiophobia, Tampa, fear-avoidance, FABQ, fear of movement/pain, TSK |
| `wellbeing_positive_psychology` 22 *(Pass 2)* | positive/negative affect, optimism, well-being, self-compassion, MAAS, FFMQ, mindfulness, emotion regulation, life satisfaction, burnout, body awareness/appreciation/embodiment |
| **pain_interference** (471): `disability` 330 | disability, functional/functioning, ADL, FIQ, ODI, PDI, Roland-Morris, RMDQ; *Pass 2:* activity limitation, back-related function, Quebec |
| `work_participation` 13 | return to work, work ability/productivity, sick leave, presenteeism; *Pass 2:* employment, work status, sickness absence/listing |
| `coping_adaptation` 29 | coping, self-efficacy, acceptance, adaptation, resilience; *Pass 2:* locus of control, illness perception, ability to cope, empowerment, problem solving, psychological flexibility, valued living |
| `quality_of_life` 66 | quality of life, QoL, SF-36, PROMIS; *Pass 2:* SF-12, EQ-5D/EuroQol, GHQ |
| `interference` 33 | interference, impact on, life impact |
| **pain_recovery** (523): `pain_intensity` 279 | pain intensity/severity/score/level, average/worst/current pain, VAS, NRS, numeric rating, visual analog |
| `pain_frequency` 61 | headache/migraine frequency or days, attack frequency, episodes per; *Pass 2:* frequency of headaches |
| `global_impression` 8 | global impression, CGI-S, PGIC, patient/clinician global, overall improvement, pain relief/reduction; *Pass 2:* clinical global, global perceived effect, proportion of responders |
| `general_pain` 175 | pain, headache, migraine, symptom-, photophobia; *Pass 2:* headaches, discomfort |
| **physical_performance** (140) *(new, Pass 2)*: `strength_endurance` 49 | strength, muscle capacity/function/endurance, dynamometry, grip, endurance, fitness, Biering-Sørensen, EMG, trunk muscle, balance tests, deadlift, repetitions |
| `mobility_balance_gait` 79 | walk tests, gait, Timed Up and Go, chair stand, stairs, sit-to-stand, posturography, posture, proprioception, flexibility, range of motion, Schober, straight leg raise, motor control tests, stability, alignment |
| `physical_activity_behavior` 12 | steps, accelerometer, sedentary/sitting, physical activity, activity level, cycling |
| **associated_symptoms** (38) *(new, Pass 2)*: `sleep` 28 | sleep, insomnia, PSQI, wake time, naps, circadian, light exposure, bedtime |
| `fatigue` 3 · `dizziness_vestibular` 4 · `cognition` 3 | fatigue, MFI · dizziness, vertigo · cognitive, neuropsychological, memory, executive function |
| **healthcare_use_cost** (23) *(new, Pass 2)*: `cost_economic` 8 | cost(s), economic, budget impact, QALY, cost-effectiveness/utility |
| `service_use` 9 · `medication_use` 6 | utilization, physician/doctor visits, consultations, referral, specialist care, imaging orders/requests, diagnostic error, hospital, emergency · medication, opioid, analgesic use, prescri- |
| **other** (26, 1.4%): `not_an_outcome_measure` 7 | trauma history, KSADS/diagnosis, effect sizes, sample size, "characterize" (baseline description, not an outcome) |
| `other` 19 | nothing matched (flagged `outcome_category_review_flag`) |

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
