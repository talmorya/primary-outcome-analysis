# Final inclusion rules — analytic cohort (664 studies)

**Run ID:** `final_cohort_20260922`  
**Frozen:** September 2026 (manual QC complete)

This document defines the finalized rules used to construct the analytic cohort. The cohort is **not** the raw CT.gov extraction cohort (674 studies); it applies additional condition, intervention, and outcome-based filters to a master pool of 696 studies.

---

## Master pool (696 studies)

**Retrieval query (CT.gov API v2):**

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND condition IN (chronic back pain, fibromyalgia, migraine, primary headache)
```

**Sources:**

| Source | Studies |
|---|---:|
| Existing full extraction (`full_20260823_201251`) | 674 |
| Net-new primary-headache expansion (curated) | 22 |
| **Master pool total** | **696** |

All 696 studies are retained in `exclusion_audit.csv` with inclusion/exclusion flags. The analytic cohort is the subset with `cohort_included = True` (664 studies).

---

## Stage 1 — Condition eligibility

**Include** when `condition_eligibility` ∈ {`eligible`, `borderline`}.

**Target conditions** (boolean flags; studies may match multiple):

| Flag | Condition |
|---|---|
| `eligible_migraine` | Migraine (including chronic/vestibular migraine) |
| `eligible_chronic_back_pain` | Chronic low back pain |
| `eligible_fibromyalgia` | Fibromyalgia |
| `eligible_headache` | Primary headache (non-migraine expansion) |

**Hard exclusions** (`global_excludes` in `config/condition_patterns_proposed.yaml`):

- Post-traumatic / post-concussive headache
- TBI / concussion
- Cancer / oncology
- Surgical / postoperative pain
- Secondary pain (cervicogenic, malignancy-related)
- MS / clinically isolated syndrome
- Acute-only low back pain (when chronic LBP is the only target match)
- Visual snow syndrome
- Vestibular schwannoma / acoustic neuroma

**Headache-expansion exclusions** (when `primary_headache` is in play):

- Medication-overuse headache
- Cervicogenic headache

**Population-primary mismatch** (`off_target_primary_population`):

Exclude when the **first listed condition** is ME/CFS, long COVID, POTS, or similar off-target population **and** no target pain condition appears in the first three listed conditions **and** the study title does not name a target condition.

**Borderline** (included, flagged for sensitivity analyses):

- Fibromyalgia + inflammatory/autoimmune co-listing (e.g. lupus) when fibromyalgia remains a study focus

**Manual decision — retained:**

- **NCT01118988:** KEEP despite IBS being listed first. Heterogeneous chronic pain conditions (IBS, fibromyalgia, CRPS, etc.) are all relevant; study registers pain outcomes. No heterogeneity exclusion rule was introduced.

Config: `config/condition_patterns_proposed.yaml`  
Logic: `src/ctgov_pipeline/condition_eligibility.py`

---

## Stage 2 — Intervention eligibility

**Include** when ≥1 treatment-oriented behavioral arm is classified into an intervention category.

**Intervention categories** (pipe-joined; studies may have multiple):

| Category | Examples |
|---|---|
| `psychological_therapy` | CBT, ACT, exposure, MI |
| `mind_body` | Mindfulness, MBSR, yoga, tai chi |
| `pain_education_self_management` | Pain neuroscience education, self-management |
| `physical_activity_exercise` | Aerobic exercise, strengthening, PT programs |
| `lifestyle_behavioral` | Sleep hygiene, diet, pacing |
| `complementary_integrative` | Acupuncture, massage |
| `multidisciplinary_program` | Combined structured programs |
| `digital_behavioral` | App-based / telehealth behavioral delivery |
| `other_behavioral_treatment` | Catch-all treatment-oriented behavioral |

**Exclude:**

| Reason | Description |
|---|---|
| `no_behavioral_arm` | No BEHAVIORAL-type arm |
| `control_arms_only` | Only comparator arms (sham, waitlist, usual care) |
| `mechanism_arms_only` | Only lab/psychophysical mechanism arms |
| `no_treatment_behavioral_arm` | Behavioral arms present but none classify as treatment |

**Multimodal flag:** `is_multimodal = True` when behavioral treatment is combined with drug, device, or procedure co-interventions. Multimodal trials **remain eligible**.

Treatment categories are matched on **all arm types** (not only `BEHAVIORAL`). Control detection uses arm **name** only (not description) to avoid false positives.

Config: `config/intervention_categories.yaml`  
Logic: `src/ctgov_pipeline/classify_intervention_categories.py`, `src/ctgov_pipeline/intervention_eligibility.py`

---

## Stage 3 — Treatment vs mechanism (outcome-based)

**Core principle:** Exclude only when registered outcomes as a whole indicate a mechanistic/experimental study, not a treatment evaluation.

**Exclude** (`mechanism_only_outcomes`) when:

- **All** registered outcomes (primary + secondary + other) are mechanistic/experimental, **and**
- There is **no** clinical/treatment-relevant outcome anywhere among them

**Do not exclude** merely because all **primary** outcomes are mechanistic if any secondary/other outcome is clinical.

**Mechanistic endpoints** include (non-exhaustive): fMRI/EEG/connectivity, biomarkers, QST/pain thresholds, dopamine response, attentional bias (experimental), HRV when used as mechanism endpoint, etc.

**Clinical/treatment endpoints** include (non-exhaustive): pain intensity/severity/frequency, headache days, disability/function, QoL, mood/anxiety/depression scales, fatigue, sleep, gait, exercise capacity/performance, medication use, global impression.

**Study-level flags (included studies):**

| Column | Definition |
|---|---|
| `primary_outcome_mechanistic` | TRUE only when **every** non-empty primary outcome is mechanistic and **none** are clinical |
| `has_clinical_outcome_anywhere` | TRUE when any registered outcome matches the clinical lexicon |

**Manual decision — retained:**

- **NCT00864422:** KEEP. Primary outcomes are TMS cortical mapping (mechanistic → `primary_outcome_mechanistic = TRUE`). Secondary outcomes include self-reported pain (VAS) and patient-specific functional scale → `has_clinical_outcome_anywhere = TRUE`.

Logic: `src/ctgov_pipeline/outcome_mechanism.py`

---

## Outcome classification (annotation layer)

Primary outcomes are classified into hierarchical categories for descriptive analysis. **Outcome categories do not determine inclusion.**

| `outcome_category` | Examples of `outcome_subcategory` |
|---|---|
| `pain_recovery` | `pain_intensity`, `pain_frequency`, `general_pain` |
| `pain_interference` | `disability`, `interference`, `quality_of_life`, `coping_adaptation` |
| `mood` | `anxiety`, `depression`, `catastrophizing`, `distress_stress` |
| `feasibility_acceptability` | `feasibility_recruitment`, `adherence_fidelity`, `safety` |
| `other` | `biological_physiological`, `other`, `uncertain` |

Raw outcome text (`primary_outcome_measure`, `primary_outcome_description`, `primary_outcome_time_frame`) is preserved verbatim.

Logic: `src/ctgov_pipeline/outcome_category.py`

---

## Final cohort summary

| Metric | Value |
|---|---:|
| Master pool | 696 |
| **Analytic cohort** | **664** |
| Condition exclusions | 20 |
| Intervention exclusions | 10 |
| Mechanism exclusions | 2 |
| Primary outcome rows (cohort) | 1,537 |
| `primary_outcome_mechanistic = TRUE` | 16 |

---

## What was dropped from earlier pipeline versions

- `rq_eligible` / RQ eligibility layer
- `non_psychological_behavioral_*` flags
- `behavioral_component` taxonomy (replaced by `intervention_categories`)
- `primaryPurpose`-based mechanism exclusion (replaced by outcome-based rule)
