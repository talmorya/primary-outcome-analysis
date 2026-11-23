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

Descriptive only: never used to include or exclude, and never overwrites the raw outcome text. Counts are the 1,900 primary-outcome rows of the 811 included trials that have outcomes. Patterns are regex fragments with `\b` and escapes removed; `?` = optional.

**How a row is classified (first match wins)**

1. **Mechanistic check.** `mechanistic` if any mechanistic pattern matches *and* no clinical-treatment pattern matches (clinical patterns, in `outcome_mechanism.py`: pain intensity, VAS/NRS, headache days, disability, ODI, FIQ, RMDQ, QoL, SF-36, PROMIS, catastrophizing, anxiety, depression, sleep, coping, global impression, pain relief, gait/balance/strength tests, …). Mechanistic patterns: fmri, eeg, mri, functional connectivity, effective connectivity, neuroimaging, brain activity, brain imaging, neural activity, neural response, cerebral blood flow, arterial spin labeling, asl, magnetic resonance spectroscopy, mrs, resting-state, late positive potential, error related negativity, electrophysiol, cortical map, motor cortical, transcranial magnetic stimulation, tms, rtms, dopamine response, neurotransmitter, biomarker, inflammation, cytokine, cortisol, gene expression, neuroimmune, heart rate variability, hrv, quantitative sensory, qst, pain threshold, pain tolerance, pain summation, psychophysical, conditioned pain modulation, cpm, pressure pain, thermal stimul, sensory stimul, hyperalgesia, attentional bias, contingency awareness, pain expectancy, selective learning, temporal binding, psychophysical adaptation, petco2, provocation, experimental pain, ratings of painful sensory, inducible dizziness, point of subjective simultaneity, psychophysiological, dataset of functional magnetic.
2. **Pass 1 rules**, on measure + description + time frame. Rule order: safety, feasibility, acceptability, adherence, other feasibility, anxiety, depression, catastrophizing, distress, disability, work, coping, quality of life, interference, pain intensity, pain frequency, global impression, general pain.
3. **Pass 2 rules**, on the **measure name only**, reached only by rows that matched nothing before, so they cannot move a row out of a Pass-1 category.
4. Otherwise `other / other` with `outcome_category_review_flag = True`.

| Category | Subcategory | Rows (% of 1900) | Trials | Pass-1 text patterns (measure + description + time frame) | Pass-2 text patterns (measure name only) | Most frequent detected instruments |
|---|---|---:|---:|---|---|---|
| **pain_recovery** | | **523 (27.5%)** | **381** | | | |
| | pain_intensity | 279 (14.7%) | 229 | pain intensity, pain severity, pain score, pain level, average pain, worst pain, current pain, vas, nrs, numeric rating, visual analog | — | Visual Analog Scale (128), Numeric Rating Scale (84), Brief Pain Inventory (21), PEG-3 (2) |
| | general_pain | 175 (9.2%) | 139 | pain, headache, migraine, symptom, photophobia, headache disability | headaches, discomfort | Brief Pain Inventory (5), Widespread Pain Index (5), Numeric Rating Scale (5), McGill Pain Questionnaire (3) |
| | pain_frequency | 61 (3.2%) | 52 | headache frequency, migraine frequency, headache days, migraine days, number of headache, attack frequency, episodes per | headaches? frequency, frequency of headaches?, reduction of headaches? | — |
| | global_impression | 8 (0.4%) | 8 | global impression, cgis, pgic, patient global, clinician global, overall improvement, pain relief, pain reduction | clinical global, cgi, global perceived, proportion of responders, therapeutic changes | Patient Global Impression of Change (3) |
| **pain_interference** | | **493 (25.9%)** | **356** | | | |
| | disability | 330 (17.4%) | 279 | disability, functional, functioning, activities of daily living, adl, fiq, fibromyalgia impact, pdih, pdii, odi, roland-morris, rmdq | activit(y\|ies) limitation, back-related function, quebec | Oswestry Disability Index (87), Fibromyalgia Impact Questionnaire (60), Roland-Morris Disability Questionnaire (53), Numeric Rating Scale (13) |
| | quality_of_life | 66 (3.5%) | 50 | quality of life, qol, sf-36, sf36, promis, health-related quality | sf-?12, eq-?5d, euroqol, general health questionnaire, ghq | PROMIS (23), SF-36 (10), Visual Analog Scale (6), EQ-5D (6) |
| | coping_adaptation | 51 (2.7%) | 39 | catastroph, pcs, coping, self-efficacy, pain acceptance, adaptation, resilience | kinesiophobi, tampa, fear-avoidance, fabq, fear of (movement\|pain\|re-?injury), pain-related fear, tsk, locus of control, illness perception, ability to cope, empower, problem-solving, patient-specific goal, psychological flexibility, valued | Pain Catastrophizing Scale (10), Tampa Scale of Kinesiophobia (10), SF-12 (2), Visual Analog Scale (1) |
| | interference | 33 (1.7%) | 29 | interference, interfering, impact on, life impact | — | Brief Pain Inventory (13), Numeric Rating Scale (3), PEG-3 (2), Migraine-Specific Quality of Life Questionnaire (1) |
| | work_participation | 13 (0.7%) | 13 | return to work, work ability, work productivity, sick leave, presenteeism | employment, work status, sickness, sick-list, absence | Numeric Rating Scale (1) |
| **feasibility_acceptability** | | **356 (18.7%)** | **129** | | | |
| | feasibility_recruitment | 182 (9.6%) | 91 | feasibility, recruitment, enrollment, accrual, screening rate, eligibility rate | eligib, consent, proportion of .{0,30}randomi[sz]ed, reach), program initiation, intervention commencement | Numeric Rating Scale (9), Visual Analog Scale (8), Fibromyalgia Impact Questionnaire (5), Oswestry Disability Index (4) |
| | acceptability_satisfaction | 70 (3.7%) | 47 | acceptability, satisfaction, usability, user experience, participant experience | credibility, expectancy, perceptions? of (the )?intervention, exercise perceptions, experience with the intervention, trust score, semi-structured interview, appropriateness, continued interest, willingness to pay, adoption, confidence in carrying out, benefits and barriers, barriers and facilitators | Numeric Rating Scale (2), Patient Global Impression of Change (1), Tampa Scale of Kinesiophobia (1), Pain Self-Efficacy Questionnaire (1) |
| | adherence_fidelity | 54 (2.8%) | 42 | adherence, compliance, fidelity, protocol adherence, therapist adherence, treatment integrity | attend, usage, engagement, participation rate, treatment participation, program participation, at-home practice, (intervention\|treatment\|program) completion, completing the, utili[sz]e the, uptake, made an appointment, initiating, number of sessions, homework, successful completion, frequency of using, (days\|minutes).{0,30}practice, contamination | — |
| | other_feasibility | 27 (1.4%) | 18 | retention rate, drop-out rate, completion rate | drop-outs?, withdraw, retention, retain, (assessment\|questionnaires?\|outcome measures?\|tests?).{0,30}(complet\|fulfilled\|returned), complet.{0,30}(assessment\|questionnaires?\|outcome measures?\|screening), ^follow-up$, attrition | — |
| | safety | 23 (1.2%) | 14 | adverse, safety, side effect, tolerability, serious adverse | — | PROMIS (3), Patient Global Impression of Change (1) |
| **mechanistic** | | **162 (8.5%)** | **70** | | | |
| | biological_structural | 48 (2.5%) | 24 | — | serum, plasma, blood (flow\|extraction\|oxygen), bold, gr[ae]y matter, brain, microbio, hormone, crp, c-reactive, interleukin, il-d, cortisol, voxel, cerebr, ampk, temperature, thickness, ultrasound, fascia, muscle tone, pulsatility, endocannabinoid, inflammat, heart rate, glucos, glyc, hba1c, diabetes, noxious inhibitory, bdnf, blood | — |
| | sensory_qst | 37 (1.9%) | 15 | (see mechanistic rule below) | — | Numeric Rating Scale (2) |
| | other_mechanistic | 31 (1.6%) | 19 | (see mechanistic rule below) | — | — |
| | neuroimaging_neural | 25 (1.3%) | 21 | (see mechanistic rule below) | — | — |
| | biomarker_inflammatory | 15 (0.8%) | 5 | (see mechanistic rule below) | — | — |
| | psychophysiological | 6 (0.3%) | 5 | (see mechanistic rule below) | — | — |
| **mood** | | **139 (7.3%)** | **85** | | | |
| | anxiety | 49 (2.6%) | 39 | anxiety, panic, state-trait anxiety, gsi, bai | — | Fibromyalgia Impact Questionnaire (21), Hospital Anxiety and Depression Scale (10), PROMIS (3), EQ-5D (2) |
| | distress_stress | 37 (1.9%) | 30 | distress, stress, mood, emotional distress, psychological stress | bsi, brief symptom inventory | Brief Pain Inventory (4), Visual Analog Scale (2), PROMIS (1) |
| | depression | 31 (1.6%) | 21 | depress, phq, beck depression, ces-d, ham-d | — | PHQ-9 (11), Beck Depression Inventory (6), PROMIS (3) |
| | wellbeing_positive_psychology | 22 (1.2%) | 7 | — | positive affect, negative affect, optimis, well-?being, self-compassion, maas, ffmq, mindfulness, emotion regulation, life satisfaction, burnout, emotional exhaustion, personal accomplishment, body (awareness\|appreciation\|trusting\|functionality), embodiment, body connection, own body | — |
| **physical_performance** | | **140 (7.4%)** | **67** | | | |
| | mobility_balance_gait | 79 (4.2%) | 41 | — | walk, gait, timed up, get-up, chair, stair, sit to stand, posturograph, postur, proprioception, flexib, range of motion, rom, schober, sit and reach, straight leg, lumbar (spine\|flexion), segmental movement, stiffness, joint position, craniovertebral, tragus, pelvic tilt, movement control, motor control, luomajoki, ergospirometry, physical function, flexion rotation, pressure biofeedback, muscle, mobility, time up and go, 5rsts, range of movement, craniocervical flexion, limits of stability, instability, alignment | — |
| | strength_endurance | 49 (2.6%) | 30 | — | strength, muscle (capacity\|function\|endurance\|activation), muscular, grip, endurance, fitness, muscle power, biering, deadlift, repetitions, d[iy]namometry, cybex, flexor to extensor, multifidus, abdominal dynamic, emg, electromyograph, trunk muscle, conditioning, balance | — |
| | physical_activity_behavior | 12 (0.6%) | 10 | — | steps?, step counts?, accelerometer, sedentary, sitting, physical activity, activity level, cycling | — |
| **associated_symptoms** | | **38 (2.0%)** | **25** | | | |
| | sleep | 28 (1.5%) | 16 | — | sleep, insomnia, psqi, total wake time, naps?, circadian, light exposure, bedtime, awake during the night | Insomnia Severity Index (2) |
| | dizziness_vestibular | 4 (0.2%) | 3 | — | dizz, vertigo | — |
| | cognition | 3 (0.2%) | 3 | — | cogniti, neuropsycholog, memory, executive function | — |
| | fatigue | 3 (0.2%) | 3 | — | fatigue, mfi | — |
| **healthcare_use_cost** | | **23 (1.2%)** | **17** | | | |
| | service_use | 9 (0.5%) | 7 | — | utili[sz]ation, (number of\|physicians?\|doctors?\|gp) visits?, visits? (of\|to) (physicians?\|doctors?\|gps?), consultations?, referral, specialist care, imaging (orders\|requests), diagnostic error, safe diagnosis, hospital, emergency | — |
| | cost_economic | 8 (0.4%) | 5 | — | costs?, economic, budget impact, qaly, cost-effective, cost-utility | EQ-5D (1) |
| | medication_use | 6 (0.3%) | 6 | — | medication, opioid, analgesic (use\|consumption), dependence on medicine, prescri | — |
| **other** | | **26 (1.4%)** | **23** | | | |
| | other | 19 (1.0%) | 17 | — | — | Insomnia Severity Index (1) |
| | not_an_outcome_measure | 7 (0.4%) | 6 | — | trauma, ksads, diagnosis using, effect sizes?, sample size, characteri[sz]e | — |

Notes: `mechanistic` subcategories other than `biological_structural` come from the mechanistic check (`neuroimaging_neural`: fMRI/EEG/connectivity/brain activity; `sensory_qst`: QST/pain threshold/hyperalgesia/pressure pain; `biomarker_inflammatory`: biomarker/cytokine/cortisol/inflammation; `psychophysiological`: HRV/electrophysiology; `other_mechanistic`: the rest). Fear-avoidance (TSK/FABQ) and catastrophizing (PCS) sit under `pain_interference / coping_adaptation`. `not_an_outcome_measure` (under `other`) holds baseline-description items: trauma history, KSADS/diagnosis, effect sizes, sample size, "characterize". "Most frequent detected instruments" comes from the separate `instruments_detected` lexicon column, not from the category rules.

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
