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
| `instruments_detected` | Pipe-separated instrument hits from lexicon |
| `raw_study_first_post_date` | From study |
| `extraction_run_id` | Raw run id |

### Outcome category mapping (`src/ctgov_pipeline/outcome_category.py`)

Descriptive only: never used to include or exclude, and never overwrites the raw outcome text. Counts are the 1,900 primary-outcome rows of the 811 included trials that have outcomes. Patterns are regex fragments with `\b` and escapes removed; `?` = optional.

**How a row is classified (first match wins)**

1. **Pass 1 rules**, in table order, first match wins. The `mechanistic` and `feasibility_acceptability` rules come first and read the **measure name only** (descriptions and time frames of clinical outcomes mention "pressure pain", "fMRI", "enrollment", "feasibility" or "adverse" without being those outcomes, e.g. "change from enrollment to end of treatment"); all other Pass-1 rules read measure + description + time frame. Order: mechanistic (neuroimaging, QST, biomarker, psychophysiological, other), safety, feasibility, acceptability, adherence, other feasibility, anxiety, depression, catastrophizing, distress, disability, work, coping, quality of life, interference, pain intensity, pain frequency, global impression, general pain.
2. **Pass 2 rules**, on the **measure name only**, reached only by rows that matched nothing before, so they cannot move a row out of a Pass-1 category.
3. Otherwise `other / other` with `outcome_category_review_flag = True`.

| Category | Subcategory | Rows (% of 1900) | Trials | Pass-1 text patterns | Pass-2 text patterns (measure name only) | Most frequent detected instruments |
|---|---|---:|---:|---|---|---|
| **pain_recovery** | | **516 (27.2%)** | **382** | | | |
| | pain_intensity | 269 (14.2%) | 230 | pain intensity, pain severity, pain score, pain level, average pain, worst pain, current pain, vas, nrs, numeric rating, visual analog | — | Visual Analog Scale (127), Numeric Rating Scale (77), Brief Pain Inventory (21), PEG-3 (2) |
| | general_pain | 176 (9.3%) | 138 | pain, headache, migraine, symptom, photophobia, headache disability | headaches, discomfort | Widespread Pain Index (6), Brief Pain Inventory (5), Numeric Rating Scale (5), McGill Pain Questionnaire (4) |
| | pain_frequency | 63 (3.3%) | 54 | headache frequency, migraine frequency, headache days, migraine days, number of headache, attack frequency, episodes per | headaches? frequency, frequency of headaches?, reduction of headaches? | — |
| | global_impression | 8 (0.4%) | 8 | global impression, cgis, pgic, patient global, clinician global, overall improvement, pain relief, pain reduction | clinical global, cgi, global perceived, proportion of responders, therapeutic changes | Patient Global Impression of Change (3) |
| **pain_interference** | | **516 (27.2%)** | **374** | | | |
| | disability | 345 (18.2%) | 292 | disability, functional, functioning, activities of daily living, adl, fiq, fibromyalgia impact, pdih, pdii, odi, roland-morris, rmdq | activit(y\|ies) limitation, back-related function, quebec | Oswestry Disability Index (91), Fibromyalgia Impact Questionnaire (65), Roland-Morris Disability Questionnaire (54), Numeric Rating Scale (14) |
| | quality_of_life | 67 (3.5%) | 51 | quality of life, qol, sf-36, sf36, promis, health-related quality | sf-?12, eq-?5d, euroqol, general health questionnaire, ghq | PROMIS (23), SF-36 (10), Visual Analog Scale (6), EQ-5D (6) |
| | coping_adaptation | 53 (2.8%) | 41 | catastroph, pcs, coping, self-efficacy, pain acceptance, adaptation, resilience | kinesiophobi, tampa, fear-avoidance, fabq, fear of (movement\|pain\|re-?injury), pain-related fear, tsk, locus of control, illness perception, ability to cope, empower, problem-solving, patient-specific goal, psychological flexibility, valued | Pain Catastrophizing Scale (10), Tampa Scale of Kinesiophobia (10), SF-12 (2), Visual Analog Scale (1) |
| | interference | 38 (2.0%) | 34 | interference, interfering, impact on, life impact | — | Brief Pain Inventory (14), Numeric Rating Scale (4), PEG-3 (2), Migraine-Specific Quality of Life Questionnaire (1) |
| | work_participation | 13 (0.7%) | 13 | return to work, work ability, work productivity, sick leave, presenteeism | employment, work status, sickness, sick-list, absence | Numeric Rating Scale (1) |
| **feasibility_acceptability** | | **298 (15.7%)** | **98** | | | |
| | feasibility_recruitment | 98 (5.2%) | 52 | feasibility, recruitment, enrollment, accrual, screening rate, eligibility rate, screened, enrolled, enrollees, refus, interested participants, eligibility criteria | eligib, consent, proportion of .{0,30}randomi[sz]ed, reach), program initiation, intervention commencement | Brief Pain Inventory (1), Numeric Rating Scale (1) |
| | acceptability_satisfaction | 81 (4.3%) | 49 | acceptability, satisfaction, usability, user experience, participant experience, ease of use, ^(participant-rated )?enjoyment, feedback, exit interview, treatment evaluation, agreed to | credibility, expectancy, perceptions? of (the )?intervention, exercise perceptions, experience with the intervention, trust score, semi-structured interview, appropriateness, continued interest, willingness to pay, adoption, confidence in carrying out, benefits and barriers, barriers and facilitators | Numeric Rating Scale (6), Patient Global Impression of Change (1) |
| | adherence_fidelity | 62 (3.3%) | 49 | adherence, compliance, fidelity, protocol adherence, therapist adherence, treatment integrity, (were\|was) delivered, duration of (use\|virtual reality sessions), (days\|minutes).{0,40}(spent\|used\|performed), sessions? (completed\|attended) | attend, usage, engagement, participation rate, treatment participation, program participation, at-home practice, (intervention\|treatment\|program) completion, completing the, utili[sz]e the, uptake, made an appointment, initiating, number of sessions, homework, successful completion, frequency of using, (days\|minutes).{0,30}practice, contamination | — |
| | other_feasibility | 41 (2.2%) | 28 | retention rate, drop-out rate, completion rate, completeness, (assessments?\|questionnaires?\|diar(y\|ies)) completed, diary completion, complet(e\|ed\|ion of) .{0,15}the intervention, definitive (rct\|trial) | drop-outs?, withdraw, retention, retain, (assessment\|questionnaires?\|outcome measures?\|tests?).{0,30}(complet\|fulfilled\|returned), complet.{0,30}(assessment\|questionnaires?\|outcome measures?\|screening), ^follow-up$, attrition | Numeric Rating Scale (1), Tampa Scale of Kinesiophobia (1), Pain Self-Efficacy Questionnaire (1) |
| | safety | 16 (0.8%) | 12 | adverse, safety, side effect, tolerability, serious adverse | — | PROMIS (3), Patient Global Impression of Change (1) |
| **mechanistic** | | **192 (10.1%)** | **76** | | | |
| | sensory_qst | 64 (3.4%) | 27 | qst, quantitative sensory, pain threshold, pain tolerance, pain summation, temporal summation, pressure pain, conditioned pain modulation, cpm, hyperalgesia, detection threshold, sensory limen, thermal stimul, sensory stimul, psychophysical, pain sensitivity, (ischemic\|evoked\|heat\|cold\|thermal) pain, cold pressor, experimental pain, ratings of painful sensory, pain modulation, painful (heat\|pressure), pressure stimul, kg/cm | — | Visual Analog Scale (8), Numeric Rating Scale (5) |
| | biological_structural | 52 (2.7%) | 22 | — | serum, plasma, blood (flow\|extraction\|oxygen), bold, gr[ae]y matter, brain, microbio, hormone, voxel, cerebr, ampk, temperature, thickness, ultrasound, fascia, muscle tone, pulsatility, endocannabinoid, inflammat, heart rate, glucos, glyc, hba1c, diabetes, noxious inhibitory, blood | — |
| | neuroimaging_neural | 38 (2.0%) | 31 | fmri, eeg, mri, connectivity, neuroimaging, brain (activity\|imaging\|function), neural, cerebral blood flow, arterial spin, asl, magnetic resonance, mrs, resting-state, late positive potential, error related negativity, evoked potential, vep, theta power, contingent negative variation, white matter, fronto-striatal, cortical (excitab\|map), motor cortical, transcranial magnetic, r?tms, transverse relaxation, ivim | — | — |
| | biomarker_inflammatory | 22 (1.2%) | 9 | biomarker, inflammat, cytokine, cortisol, gene expression, neuroimmune, tumou?r necrosis, tnf, interleukin, il-<n>, crp, c-reactive, bdnf, myo-inositol, n-acetylaspartate, choline, lactate, creatine | — | — |
| | other_mechanistic | 11 (0.6%) | 4 | dopamine response, neurotransmitter, attentional bias, contingency awareness, pain expectancy, selective learning, temporal binding, psychophysical adaptation, petco2, provocation, inducible dizziness, point of subjective simultaneity, dataset of functional magnetic | — | Numeric Rating Scale (5) |
| | psychophysiological | 5 (0.3%) | 4 | heart rate variability, ^hrv, (hrv), psychophysiol, electrophysiol, peripheral arousal | — | — |
| **mood** | | **140 (7.4%)** | **86** | | | |
| | anxiety | 50 (2.6%) | 40 | anxiety, panic, state-trait anxiety, gsi, bai | — | Fibromyalgia Impact Questionnaire (21), Hospital Anxiety and Depression Scale (10), PROMIS (3), EQ-5D (2) |
| | distress_stress | 37 (1.9%) | 30 | distress, stress, mood, emotional distress, psychological stress | bsi, brief symptom inventory | Brief Pain Inventory (4), Visual Analog Scale (2), PROMIS (1) |
| | depression | 31 (1.6%) | 21 | depress, phq, beck depression, ces-d, ham-d | — | PHQ-9 (11), Beck Depression Inventory (6), PROMIS (3) |
| | wellbeing_positive_psychology | 22 (1.2%) | 7 | — | positive affect, negative affect, optimis, well-?being, self-compassion, maas, ffmq, mindfulness, emotion regulation, life satisfaction, burnout, emotional exhaustion, personal accomplishment, body (awareness\|appreciation\|trusting\|functionality), embodiment, body connection, own body | — |
| **physical_performance** | | **143 (7.5%)** | **69** | | | |
| | mobility_balance_gait | 81 (4.3%) | 43 | — | walk, gait, timed up, get-up, chair, stair, sit to stand, posturograph, postur, proprioception, flexib, range of motion, rom, schober, sit and reach, straight leg, lumbar (spine\|flexion), segmental movement, stiffness, joint position, craniovertebral, tragus, pelvic tilt, movement control, motor control, luomajoki, ergospirometry, physical function, flexion rotation, pressure biofeedback, muscle, mobility, time up and go, 5rsts, range of movement, craniocervical flexion, limits of stability, instability, alignment | — |
| | strength_endurance | 50 (2.6%) | 31 | — | strength, muscle (capacity\|function\|endurance\|activation), muscular, grip, endurance, fitness, muscle power, biering, deadlift, repetitions, d[iy]namometry, cybex, flexor to extensor, multifidus, abdominal dynamic, emg, electromyograph, trunk muscle, conditioning, balance | — |
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
| **other** | | **34 (1.8%)** | **29** | | | |
| | other | 27 (1.4%) | 23 | — | — | Insomnia Severity Index (1) |
| | not_an_outcome_measure | 7 (0.4%) | 6 | — | trauma, ksads, diagnosis using, effect sizes?, sample size, characteri[sz]e | — |

Notes: `mechanistic` is not a separate check: it is an ordinary category whose subcategories are rules like any other (`neuroimaging_neural`: fMRI/EEG/connectivity/white matter/TMS; `sensory_qst`: QST/pain threshold/tolerance/CPM/temporal summation; `biomarker_inflammatory`: cytokines/CRP/BDNF/cortisol/MRS metabolites; `psychophysiological`: HRV/electrophysiology; `biological_structural`: Pass 2). Fear-avoidance (TSK/FABQ) and catastrophizing (PCS) sit under `pain_interference / coping_adaptation`. `not_an_outcome_measure` (under `other`) holds baseline-description items: trauma history, KSADS/diagnosis, effect sizes, sample size, "characterize". "Most frequent detected instruments" comes from the separate `instruments_detected` lexicon column, not from the category rules.

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
