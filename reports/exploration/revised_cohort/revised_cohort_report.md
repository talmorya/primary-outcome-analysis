# Revised cohort report

**Status:** Review layer only — does not modify `data/processed/full/`.

- **Master pool (pre-filter):** 696 studies
- **Eligible cohort:** 664 studies
- **Excluded (total):** 32 studies

## Exclusions by stage

- **Condition stage:** 20
- **Intervention stage:** 10
- **Mechanism / non-treatment stage:** 2

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

- `mechanism_arms_only`: 9
- `no_treatment_behavioral_arm`: 1

### Mechanism exclusion reasons

- `mechanism_only_outcomes`: 2

## Intervention categories (eligible cohort)

- `physical_activity_exercise`: 323
- `mind_body`: 248
- `pain_education_self_management`: 163
- `other_behavioral_treatment`: 160
- `psychological_therapy`: 158
- `lifestyle_behavioral`: 88
- `digital_behavioral`: 69
- `complementary_integrative`: 36
- `multidisciplinary_program`: 29

## Multimodal vs purely behavioral (eligible cohort)

- **Purely behavioral:** 575
- **Multimodal (behavioral + drug/device/procedure):** 89

## Primary outcomes (eligible cohort)

- **Total primary outcome rows:** 1537

### Outcome category distribution

- `pain_recovery`: 456
- `pain_interference`: 371
- `other`: 366
- `feasibility_acceptability`: 223
- `mood`: 121

### Outcome subcategory distribution (top 20)

- `other` → `other`: 341
- `pain_interference` → `disability`: 264
- `pain_recovery` → `pain_intensity`: 228
- `pain_recovery` → `general_pain`: 173
- `feasibility_acceptability` → `feasibility_recruitment`: 139
- `pain_interference` → `quality_of_life`: 57
- `pain_recovery` → `pain_frequency`: 52
- `mood` → `anxiety`: 48
- `feasibility_acceptability` → `acceptability_satisfaction`: 38
- `mood` → `distress_stress`: 32
- `mood` → `depression`: 30
- `pain_interference` → `interference`: 29
- `other` → `biological_physiological`: 23
- `feasibility_acceptability` → `adherence_fidelity`: 20
- `pain_interference` → `coping_adaptation`: 19
- `feasibility_acceptability` → `safety`: 19
- `mood` → `catastrophizing`: 11
- `feasibility_acceptability` → `other_feasibility`: 7
- `pain_recovery` → `global_impression`: 3
- `pain_interference` → `work_participation`: 2

## Condition flags (eligible cohort)

- **Migraine:** 140
- **Chronic back pain:** 299
- **Fibromyalgia:** 214
- **Primary headache:** 22

## Primary outcome mechanistic flag (eligible cohort)

- **primary_outcome_mechanistic = TRUE:** 16
- **primary_outcome_mechanistic = FALSE:** 648

### By condition (primary_outcome_mechanistic = TRUE)

- **Migraine:** 2
- **Chronic back pain:** 7
- **Fibromyalgia:** 7
- **Primary headache:** 0

### By intervention category (counts; studies may overlap)

- `mind_body`: 7
- `other_behavioral_treatment`: 7
- `physical_activity_exercise`: 6
- `pain_education_self_management`: 3
- `complementary_integrative`: 2
- `psychological_therapy`: 2
- `digital_behavioral`: 1
