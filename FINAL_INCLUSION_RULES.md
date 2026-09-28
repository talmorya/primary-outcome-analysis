# Final inclusion rules — analytic cohort (666 studies)

**Run ID:** `final_cohort_20260922`  
**Rules document version:** September 2026 (post–active-arm / mechanistic-outcome update)

This document is the single reference for **cohort inclusion**, **intervention classification**, and **primary-outcome classification**. Pattern matching is **case-insensitive** unless noted. Intervention category patterns are defined in `config/intervention_categories.yaml`; condition patterns in `config/condition_patterns_proposed.yaml`; outcome rules in `src/ctgov_pipeline/outcome_category.py` and `src/ctgov_pipeline/outcome_mechanism.py`.

**Cohort inclusion:** `cohort_included = TRUE` when **Stage 1 (condition)** and **Stage 2 (intervention)** pass. **Outcomes do not exclude studies.** Mechanistic outcomes are classified and flagged descriptively.

---

## Master pool (696 studies)

**CT.gov API v2 retrieval:**

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND condition IN (chronic back pain, fibromyalgia, migraine, primary headache)
```

| Source | Studies |
|---|---:|
| Full extraction `full_20260823_201251` | 674 |
| Curated primary-headache expansion | 22 |
| **Master pool total** | **696** |

All 696 studies appear in `exclusion_audit.csv`. **Analytic cohort:** `cohort_included = TRUE` (**666** studies).

---

## Stage 1 — Condition eligibility

**Include** when `condition_eligibility` ∈ {`eligible`, `borderline`}.

**Logic:** `src/ctgov_pipeline/condition_eligibility.py`  
**Patterns:** `config/condition_patterns_proposed.yaml`

### Target conditions (study flags; multiple allowed)

| Flag | Label | Text patterns (regex) |
|---|---|---|
| `eligible_migraine` | Migraine | `migraine`, `chronic migraine`, `vestibular migraine` |
| `eligible_chronic_back_pain` | Chronic back pain | `chronic.*back`, `low back pain`, `clbp`, `lbp`, `non-specific low back`, `chronic low back` |
| `eligible_fibromyalgia` | Fibromyalgia | `fibromyalgia`, `fm` |
| `eligible_headache` | Primary headache (non-migraine) | `tension-type`, `tension headache`, `tth`, `cluster headache`, `trigeminal autonomic`, `hemicrania continua`, `paroxysmal hemicrania`, `sunct`, `suna`, `chronic daily headache`, `cdh`, `new daily persistent`, `ndph`, `primary headache`, `headache disorder`, `chronic headache`, `episodic headache`, `recurrent headache`, `pediatric headache`, `headache in children`, `headache in adolescent`, `^headache$`, `^headaches$` |

Matching uses conditions, keywords, titles, and intervention names per the module (see code).

### Global exclusions (`global_excludes`)

| Rule key | Patterns (summary) |
|---|---|
| `post_traumatic` | post-traumatic headache/pain, post-concuss*, persistent post-traumatic, post concussive headache |
| `tbi_concussion` | traumatic brain injury, `tbi`, brain injur*, concussion, mild traumatic brain, post-concussion syndrome |
| `cancer_oncology` | cancer (not “non-cancer”), carcinoma, oncolog*, neoplasm, malignan*, head and neck carcinoma |
| `surgical_postoperative` | disc prosthesis, total disc replacement, spinal fusion, postoperative, postsurgical, failed back surgery, post-dural / pdph, etc. |
| `secondary_pain` | secondary headache/pain, cervicogenic, pain due to malignancy |
| `pathology_other` | intracranial hypertension, pseudotumor, meningitis, multiple sclerosis, clinically isolated syndrome |
| `visual_snow` | visual snow |
| `vestibular_schwannoma` | vestibular schwannoma, acoustic neuroma |
| `acute_lbp_only` | (only when chronic LBP is the sole target match) `acute low back pain`, `acute back pain` |

### Headache-expansion exclusions (`headache_excludes`)

| Rule | Patterns |
|---|---|
| Medication-overuse | medication-overuse, `moh`, rebound headache, analgesic overuse |
| Cervicogenic | cervicogenic |
| Symptom-not-target | delirium, diagnostic error, opioid prescribing, reflexology, breastfeeding, occupational stress, anesthesia, obesity & overweight, etc. |

### Population-primary mismatch (`population_primary_excludes`)

Exclude when **first listed condition** matches off-target population **and** no target pain condition in the **first three** conditions **and** title does not name a target:

- `me/cfs`, myalgic encephalomyelitis, chronic fatigue syndrome, long covid, post-covid, postural orthostatic tachycardia, `pots`

### Borderline (included)

- **Fibromyalgia + inflammatory co-listing** (e.g. lupus) when fibromyalgia remains a focus (`borderline_rules.fibromyalgia_inflammatory`).

### Manual decision

- **NCT01118988:** KEEP (heterogeneous chronic pain / IBS listed first; pain outcomes registered).

---

## Stage 2 — Intervention eligibility

**Logic:** `classify_intervention_categories.py`, `intervention_eligibility.py`  
**Patterns:** `config/intervention_categories.yaml`

### Concepts

| Term | Meaning |
|---|---|
| **Comparator arm** | Arm whose **name** matches control patterns (below), after active-treatment name exceptions. Comparator arms are **not** used for treatment categories, multimodal, or active behavioral flags. |
| **Active treatment arm** | Any non-comparator arm. |
| **`intervention_categories`** | Sorted **union** of all category IDs matched on **any** active arm (multiple categories per arm allowed, e.g. MBSR + pain education → `mind_body_integrative` + `education_self_management`; app-based CBT → `psychological_cognitive` + `digital_health_delivery`). |
| **`has_active_behavioral_arm`** | Active arm is CT.gov `BEHAVIORAL`, behavioral-text `OTHER`, assigned a treatment category, or `other_behavioral_treatment`. |
| **`has_behavioral_arm`** | Same as `has_active_behavioral_arm` (legacy column name). |

**Text used for category matching on active arms:** arm `name` + `description` + `type` (joined).

### Inclusion decision tree

1. **No active treatment arm**  
   - If any comparator → exclude `control_arms_only`  
   - Else → exclude `no_active_treatment_arm`

2. **No `intervention_categories` on active arms**  
   - If mechanism arms on active side → `mechanism_arms_only`  
   - Else if no `has_active_behavioral_arm` → `no_active_behavioral_arm`  
   - Else → `no_treatment_behavioral_arm`

3. **≥1 intervention category on active arms** → **intervention eligible** (e.g. acupuncture on active `DEVICE` arm via `mind_body_integrative`).

**Final cohort rule:** `cohort_included` = condition OK **and** intervention eligible.

### Comparator detection (arm **name** only)

**Control name patterns:**

`placebo`, `sham`, `waitlist` / `waiting list`, `usual care`, `standard care`, `standard medical`, `no intervention`, `attention control`, `control group`, `control arm`

**Names treated as active (not comparator) despite control-like words:**

- Name matches **active-treatment heuristic** (`intervention`, `therapy`, `cbt`, `meditation`, `app-based`, `self-management`, `web`, `training`, `education`, `exercise`, `pain ed`, `tenacity`, `+`) **and** contains `usual care` or `standard care`
- `standard care and web`, `web-based`, `internet-enhanced`

### Control type labels (`control_arm_types`)

From comparator arm **name** only:

| `control_type` | Name signal |
|---|---|
| `sham_control` | sham |
| `waitlist_control` | waitlist, waiting list |
| `placebo_control` | placebo |
| `attention_control` | attention control |
| `usual_care` | usual care, standard care, standard medical |
| `no_intervention_control` | no intervention |
| `other_control` | control group, control arm, control, or default |

Raw comparator arms: **`control_arms_raw`** (JSON: `control_type`, `arm_name`, `arm_type`, `description`).

### Mechanism arms (intervention stage; active arms)

Matched on full arm text; used when **no** treatment categories assigned. **Exclude patterns** (mechanism):

`psychophysical`, experimental heat pain, cover story, nocebo, PASAT, quantitative sensory, `qst`, resting state eeg, picture viewing eeg, cognitive assessment mapping, affective touch, walk test, thermal stimuli, pressure pain threshold, pain threshold test, functional magnetic resonance, `fmri`, neuroimaging paradigm, experimental pain, pain modulation efficiency, conditioned pain modulation

**Mechanism exclude overrides** (do not tag mechanism if present):

`emotional regulation`, emotional positive/negative, `pbre`, consecutive days, administered for one hour

### Intervention categories — pattern → category

**Config version:** `2.0.0` (`config/intervention_categories.yaml`)

All patterns are case-insensitive regex substrings on **active** arm text (name + description + type). **Every** matching category is added (union across arms and within an arm).

| Category ID | Label | Rationale / examples |
|---|---|---|
| `psychological_cognitive` | Psychological & cognitive therapy | Thoughts, distortions, coping skills: CBT, ACT, MI, DBT, psychotherapy |
| `neuroplastic_recovery_therapy` | Neuroplastic recovery therapy | Unlearning neural pain loops: PRT, EAET, exposure / graded exposure |
| `mind_body_integrative` | Mind-body & integrative practice | Movement/touch + mental focus: MBSR, yoga, tai chi, acupuncture, massage |
| `education_self_management` | Education & self-management | PNE, pacing, self-management, sleep hygiene, diet, lifestyle education |
| `physical_rehabilitation` | Physical rehabilitation | Exercise, strengthening, aerobic training, structured PT / physiotherapy |
| `multidisciplinary_interdisciplinary` | Multidisciplinary / interdisciplinary program | Formal multi-provider programs (intensive pain clinics, functional restoration) |
| `digital_health_delivery` | Digital health delivery | Apps, telehealth, VR delivery (can co-tag with content categories) |
| `other_behavioral_treatment` | Other behavioral treatment | Catch-all when behavioral-like but no pattern match (review flag) |

#### `psychological_cognitive`

| Pattern |
|---|
| `cognitive behav`, `cognitive-behavioral`, `cbt` |
| `acceptance and commitment`, `act` |
| `psychotherapy`, `psychodynamic`, `interpersonal therapy` |
| `behavioral therapy`, `behavioural therapy` |
| `emdr`, `dialectical behavior`, `dbt` |
| `motivational interview`, `operant behavioral` |
| `emotional regulation`, `pbre`, `cognitive functional`, `cft` |

#### `neuroplastic_recovery_therapy`

| Pattern |
|---|
| `pain reprocess`, `pain re-processing`, `prt` |
| `emotional awareness and expression`, `eaet` |
| `exposure therapy`, `graded exposure` |

#### `mind_body_integrative`

| Pattern |
|---|
| `mindful`, `mbsr`, `mbct`, `mindfulness`, `meditation`, `hypnosis`, `hypnotherapy` |
| `relaxation`, `progressive muscle`, `yoga`, `tai chi`, `pilates` |
| `biofeedback`, `neurofeedback`, `guided imagery` |
| `acupuncture`, `massage`, `tuina`, `chiropractic`, `osteopath`, `shiatsu` |
| `music therapy`, `music listening`, `art therapy` |

#### `education_self_management`

| Pattern |
|---|
| `pain education`, `pain neuroscience education`, `pne` |
| `psychoeducation`, `psycho-education`, `patient education` |
| `self-management` / `self management`, `pacing` |
| `coping skills`, `pain coping`, `coaching`, `counsel` |
| `diet`, `nutrition`, `dietary`, `weight loss`, `fasting`, `lifestyle` |
| `sleep hygiene`, `behavioral insomnia`, `cbt-i` / `cbt i` |
| `smoking cessation`, `light exposure`, `light deprivation`, `wellness` |

#### `physical_rehabilitation`

| Pattern |
|---|
| `exercise`, `physical activity`, `aerobic`, `walking`, `walk with ease` |
| `stretching`, `workout`, `strengthening`, `resistance training` |
| `movement therapy`, `physiotherapy`, `physical therapy`, `rehabilitation`, `manual therapy` |

#### `multidisciplinary_interdisciplinary`

| Pattern |
|---|
| `multidisciplinary`, `interdisciplinary`, `back school`, `fibrowalk` |
| `functional restoration`, `work-hardening`, `headache management program` |

#### `digital_health_delivery`

| Pattern |
|---|
| `internet-delivered`, `web-based`, `mobile app`, `smartphone` |
| `telehealth`, `telemedicine`, `virtual reality`, `vr` |
| `RELAXaHEAD`, `PainGuide`, `Migraine Manager` |

#### `other_behavioral_treatment` — Catch-all

Assigned when an active arm is behavioral-like (`BEHAVIORAL` type or `OTHER` with behavioral keywords in text) but **no** category pattern matched. Sets `intervention_review_flag = TRUE`.

**Behavioral keyword check on `OTHER` arms:** `behavior`, `psych`, `mindful`, `exercise`, `education`, `therapy`, `counsel`, `acupuncture`, `diet`, `yoga`, `hypnosis`, `meditation`

### Multimodal flag

| Field | Definition |
|---|---|
| `is_multimodal` | `TRUE` when there is ≥1 intervention category **and** `has_active_behavioral_arm` **and** at least one **active** arm has CT.gov type in non-behavioral multimodal set |
| `multimodal_modalities` | Subset of `pharmacological`, `device`, `procedural` seen on **active** arms |

**CT.gov types → modality** (`multimodal_modalities` in YAML):

| Modality key | Intervention types |
|---|---|
| `pharmacological` | DRUG, BIOLOGICAL, DIETARY SUPPLEMENT |
| `device` | DEVICE |
| `procedural` | PROCEDURE, RADIATION, GENETIC |

Comparator arms do not contribute.

### Intervention exclusion reasons

| `exclusion_reason` | When |
|---|---|
| `control_arms_only` | No active arms; only comparators |
| `no_active_treatment_arm` | No active arms and no comparators |
| `mechanism_arms_only` | Active arms, no treatment categories, mechanism arms |
| `no_active_behavioral_arm` | Active arms, no categories, no active behavioral signal |
| `no_treatment_behavioral_arm` | Active behavioral signal but no category match |

---

## Outcome mechanism flags (descriptive only)

**Logic:** `outcome_mechanism.py`  
**Does not affect `cohort_included`.**

| Column | Definition |
|---|---|
| `primary_outcome_mechanistic` | Every non-empty **primary** outcome is mechanistic and none are clinical |
| `has_clinical_outcome_anywhere` | Any primary/secondary/other outcome matches clinical lexicon |
| `mechanism_study_outcomes_only` | All registered outcomes mechanistic, none clinical |

**Mechanistic vs clinical:** For each outcome, text = measure + description + time frame. If **clinical** pattern matches → not mechanistic. Else if **mechanistic** pattern matches → mechanistic.

### Clinical treatment outcome patterns (`CLINICAL_TREATMENT_PATTERNS`)

Used for mechanism flags (and to veto mechanistic classification):

`pain intensity`, `pain severity`, `current pain`, `average pain`, `worst pain`, `low back pain intensity`, `chronic.*pain`, `vas`, `nrs`, numeric rating scale, visual analog, headache/migraine day/frequency/intensity/disability, `midas`, `hit-6`, `fiq`, fibromyalgia impact, `odi`, roland-morris, `rmdq`, disability, pain interference, `bpi`, brief pain inventory, functioning, physical function, `promis`, quality of life, `qol`, `sf-36`, catastroph*, `pcs`, anxiety, depress*, `phq`, `bdi`, distress, stress, medication use/consumption, global impression, `pgic`, pain relief/reduction, body awareness, `barq`, mindfulness attention, `maas`, `ffmq`, self-efficacy, coping, pain acceptance, fatigue, sleep, insomnia, `isi`, lumbar flexion, expectation of pain/harm, tender point, photophobia, headache/medication, gait, balance, postural sway/control, muscle function/capacity/strength, exercise capacity/performance, 6-minute walk, chair stand, biceps curl, repetitions, functional scale, patient-specific functional, self-reported pain, breathing difficulty, perceived effort, back-related function, activities limitation, physical activity level, illness perception, locus of control, psychological flexibility, positive affect, dizziness handicap, dizziness, biobehavioral fibromyalgia, `sf-12`

### Mechanistic outcome patterns (`MECHANISTIC_PATTERNS`)

`fmri`, `eeg`, `mri`, functional/effective connectivity, neuroimaging, brain activity/imaging, neural activity/response, cerebral blood flow, arterial spin labeling, `asl`, MRS, resting-state, late positive potential, error related negativity, electrophysiol*, cortical map, motor cortical, TMS/rtMS, dopamine response, neurotransmitter, biomarker, inflammation, cytokine, cortisol, gene expression, neuroimmune, HRV, quantitative sensory, `qst`, pain threshold/tolerance/summation, psychophysical, conditioned pain modulation, `cpm`, pressure pain, thermal/sensory stimul*, hyperalgesia, attentional bias, contingency awareness, pain expectancy, selective learning, temporal binding, psychophysical adaptation, petco2, provocation, experimental pain, ratings of painful sensory, inducible dizziness, point of subjective simultaneity, psychophysiological, dataset of functional magnetic

---

## Primary outcome classification (annotation)

**Logic:** `outcome_category.py`  
**Does not affect inclusion.**  
**Text:** measure + description + time frame (lowercased).

### Order of rules

1. If mechanistic (clinical lexicon does **not** match; mechanistic lexicon matches) → **`mechanistic`** + subcategory (below).  
2. Else first matching row in the table below (top to bottom).  
3. If text length &lt; 8 → `other` / `uncertain` (review flag).  
4. Else → `other` / `other` (review flag).

### Mechanistic subcategories

| Subcategory | Patterns in outcome text |
|---|---|
| `neuroimaging_neural` | `fmri`, `eeg`, neuroimaging, connectivity, brain activity, neural |
| `sensory_qst` | qst, quantitative sensory, pain threshold, hyperalgesia, pressure pain |
| `biomarker_inflammatory` | biomarker, cytokine, cortisol, gene expression, neurotransmitter, inflammation |
| `psychophysiological` | `hrv`, heart rate variability, psychophysiol*, electrophysiol* |
| `other_mechanistic` | mechanistic but none of the above |

### Category rules (first match wins after mechanistic check)

| `outcome_category` | `outcome_subcategory` | Rule ID | Matching patterns |
|---|---|---|---|
| `feasibility_acceptability` | `safety` | CAT_FEAS_SAFETY | adverse, safety, side effect, tolerability, serious adverse |
| `feasibility_acceptability` | `feasibility_recruitment` | CAT_FEAS_RECRUITMENT | feasibility, recruitment, enrollment, accrual, screening rate, eligibility rate |
| `feasibility_acceptability` | `acceptability_satisfaction` | CAT_FEAS_ACCEPTABILITY | acceptability, satisfaction, usability, user experience, participant experience |
| `feasibility_acceptability` | `adherence_fidelity` | CAT_FEAS_ADHERENCE | adherence, compliance, fidelity, protocol adherence, therapist adherence, treatment integrity |
| `feasibility_acceptability` | `other_feasibility` | CAT_FEAS_OTHER | retention rate, dropout rate, completion rate |
| `mood` | `anxiety` | CAT_MOOD_ANXIETY | anxiety, panic, state-trait anxiety, `gsi`, `bai` |
| `mood` | `depression` | CAT_MOOD_DEPRESSION | depress*, `phq`, beck depression, `ces-d`, `ham-d` |
| `mood` | `catastrophizing` | CAT_MOOD_CATASTROPHIZING | catastroph*, `pcs` |
| `mood` | `distress_stress` | CAT_MOOD_DISTRESS | distress, stress, mood, emotional distress, psychological stress |
| `pain_interference` | `disability` | CAT_INTERFERE_DISABILITY | disability, functional, functioning, ADL, `fiq`, fibromyalgia impact, `pdih`, `pdii`, `odi`, roland-morris, rmdq |
| `pain_interference` | `work_participation` | CAT_INTERFERE_WORK | return to work, work ability, work productivity, sick leave, presenteeism |
| `pain_interference` | `coping_adaptation` | CAT_INTERFERE_COPING | coping, self-efficacy, pain acceptance, adaptation, resilience |
| `pain_interference` | `quality_of_life` | CAT_INTERFERE_QOL | quality of life, `qol`, `sf-36`, `sf36`, `promis`, health-related quality |
| `pain_interference` | `interference` | CAT_INTERFERE_GENERAL | interference, interfering, impact on, life impact |
| `pain_recovery` | `pain_intensity` | CAT_PAIN_INTENSITY | pain intensity/severity/score/level, average/worst/current pain, `vas`, `nrs`, numeric rating, visual analog |
| `pain_recovery` | `pain_frequency` | CAT_PAIN_FREQUENCY | headache/migraine frequency, headache/migraine days, number of headache, attack frequency, episodes per |
| `pain_recovery` | `global_impression` | CAT_PAIN_GLOBAL | global impression, `cgis`, `pgic`, patient/clinician global, overall improvement, pain relief/reduction |
| `pain_recovery` | `general_pain` | CAT_PAIN_GENERAL | pain, headache, migraine, symptom, photophobia, headache disability |
| `other` | `biological_physiological` | CAT_OTHER_BIOLOGICAL | `eeg`, `fmri`, `mri`, HRV, biomarker, cortisol, neuroimaging, pressure pain threshold, pain threshold, quantitative sensory |

*Note:* Outcomes classified as **`mechanistic`** use the mechanistic branch first; they do not fall through to `other` / `biological_physiological` unless not caught by `is_mechanistic_outcome`.

### Raw outcome fields preserved

`primary_outcome_measure`, `primary_outcome_description`, `primary_outcome_time_frame` (verbatim in `primary_outcomes.csv`).

### Feature extraction (separate from category)

Instrument acronyms and keyword features: `config/outcome_lexicon.yaml` via `extract_outcome_features.py` (columns `instruments_detected`, `keywords_matched`, etc.).

---

## Manual cohort decisions

| NCT ID | Decision |
|---|---|
| NCT00864422 | KEEP; `primary_outcome_mechanistic = TRUE`; clinical pain/function on secondary outcomes → `has_clinical_outcome_anywhere = TRUE` |
| NCT01118988 | KEEP; heterogeneous chronic pain conditions |

---

## Final cohort summary (current freeze)

| Metric | Value |
|---|---:|
| Master pool | 696 |
| **Analytic cohort** | **666** |
| Condition exclusions | 20 |
| Intervention exclusions | 10 |
| Outcome-based exclusions | **0** |
| Primary outcome rows (cohort) | 1,539 |
| `is_multimodal` (eligible) | 81 |
| `primary_outcome_mechanistic = TRUE` (eligible) | 18 |
| Primary outcomes `outcome_category = mechanistic` | 91 rows |

See `data/processed/final_cohort/cohort_report.md` for latest category counts.

### Intervention category counts (eligible cohort; taxonomy v2.0.0)

| Category | Studies (count) |
|---|---:|
| `physical_rehabilitation` | 319 |
| `mind_body_integrative` | 272 |
| `education_self_management` | 218 |
| `other_behavioral_treatment` | 159 |
| `psychological_cognitive` | 152 |
| `digital_health_delivery` | 70 |
| `multidisciplinary_interdisciplinary` | 29 |
| `neuroplastic_recovery_therapy` | 22 |

*(Studies may have multiple categories; counts overlap.)*

**v1.0.0 → v2.0.0 ID mapping (for older tables):**

| Former ID | New ID |
|---|---|
| `psychological_therapy` | `psychological_cognitive` (+ exposure/PRT → `neuroplastic_recovery_therapy`) |
| `mind_body`, `complementary_integrative` | `mind_body_integrative` |
| `pain_education_self_management`, `lifestyle_behavioral` | `education_self_management` |
| `physical_activity_exercise` | `physical_rehabilitation` |
| `multidisciplinary_program` | `multidisciplinary_interdisciplinary` |
| `digital_behavioral` | `digital_health_delivery` |

---

## Cohort outputs (key columns)

| File | Purpose |
|---|---|
| `studies.csv` | Inclusion, condition flags, `intervention_categories`, `is_multimodal`, `multimodal_modalities`, `control_arm_types`, `control_arms_raw`, mechanism flags |
| `primary_outcomes.csv` | Outcome text, `outcome_category`, `outcome_subcategory`, `outcome_is_mechanistic` |
| `exclusion_audit.csv` | Stage and reason for all 696 studies |

---

## Reproduction

With raw JSON: `PYTHONPATH=src python -m ctgov_pipeline.build_revised_cohort` then `finalize_cohort`.

Without raw JSON: `PYTHONPATH=src python scripts/refresh_revised_cohort_from_tables.py` then `finalize_cohort`.

See `COHORT_REPRODUCTION_GUIDE.md` if present in repo.

---

## Dropped from earlier pipeline versions

- `rq_eligible` / RQ eligibility layer  
- `non_psychological_behavioral_*` flags  
- `behavioral_component` taxonomy (replaced by `intervention_categories`)  
- **Outcome-based cohort exclusion** (mechanism-only studies now included; flagged descriptively)  
- `primaryPurpose`-only mechanism exclusion  
