# Revised cohort report

**Status:** Review layer only — does not modify `data/processed/full/`.

- **Master pool (pre-filter):** 696 studies
- **Eligible cohort:** 666 studies
- **Excluded (total):** 30 studies

## Exclusions by stage

- **Condition stage:** 20
- **Intervention stage:** 10
- **Mechanism / non-treatment stage:** 0

### Condition exclusion reasons

- `surgical_postoperative`: 8
- `pathology_other`: 5
- `cancer_oncology`: 2
- `post_traumatic`: 1
- `vestibular_schwannoma`: 1
- `tbi_concussion`: 1
- `visual_snow`: 1
- `off_target_primary_population`: 1

### Intervention exclusion reasons

- `mechanism_arms_only`: 10

### Mechanism-only outcome flag (not an exclusion stage)

- **Studies with all registered outcomes mechanistic (historical flag):** 2

## Intervention categories (eligible cohort)

- `physical_rehabilitation`: 319
- `mind_body_integrative`: 272
- `education_self_management`: 218
- `other_behavioral_treatment`: 159
- `psychological_cognitive`: 152
- `digital_health_delivery`: 70
- `multidisciplinary_interdisciplinary`: 29
- `neuroplastic_recovery_therapy`: 22

## Multimodal vs purely behavioral (eligible cohort)

- **Purely behavioral:** 582
- **Multimodal (behavioral + drug/device/procedure):** 84

## Primary outcomes (eligible cohort)

- **Total primary outcome rows:** 1539

### Outcome category distribution

- `pain_recovery`: 420
- `pain_interference`: 364
- `other`: 322
- `feasibility_acceptability`: 221
- `mood`: 121
- `mechanistic`: 91

### Outcome subcategory distribution (top 20)

- `other` → `other`: 319
- `pain_interference` → `disability`: 257
- `pain_recovery` → `pain_intensity`: 228
- `feasibility_acceptability` → `feasibility_recruitment`: 137
- `pain_recovery` → `general_pain`: 137
- `pain_interference` → `quality_of_life`: 57
- `pain_recovery` → `pain_frequency`: 52
- `mood` → `anxiety`: 48
- `feasibility_acceptability` → `acceptability_satisfaction`: 38
- `mechanistic` → `sensory_qst`: 37
- `mood` → `distress_stress`: 32
- `mood` → `depression`: 30
- `pain_interference` → `interference`: 29
- `feasibility_acceptability` → `adherence_fidelity`: 20
- `mechanistic` → `other_mechanistic`: 19
- `feasibility_acceptability` → `safety`: 19
- `pain_interference` → `coping_adaptation`: 19
- `mechanistic` → `neuroimaging_neural`: 17
- `mechanistic` → `biomarker_inflammatory`: 14
- `mood` → `catastrophizing`: 11

## Condition flags (eligible cohort)

- **Migraine:** 140
- **Chronic back pain:** 299
- **Fibromyalgia:** 216
- **Primary headache:** 22

## Primary outcome mechanistic flag (eligible cohort)

- **primary_outcome_mechanistic = TRUE:** 18
- **primary_outcome_mechanistic = FALSE:** 648

### By condition (primary_outcome_mechanistic = TRUE)

- **Migraine:** 2
- **Chronic back pain:** 7
- **Fibromyalgia:** 9
- **Primary headache:** 0

### By intervention category (counts; studies may overlap)

- `mind_body_integrative`: 11
- `other_behavioral_treatment`: 8
- `physical_rehabilitation`: 6
- `education_self_management`: 3
- `psychological_cognitive`: 2
- `digital_health_delivery`: 1
