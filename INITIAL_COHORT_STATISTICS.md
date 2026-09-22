# Initial cohort statistics

**Run ID:** `final_cohort_20260922`  
**Analytic cohort:** 664 studies, 1,537 primary outcome rows  
**Generated:** September 2026

Filter: `cohort_included == True` in `data/processed/final_cohort/studies.csv` and `primary_outcomes.csv`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (pre-filter) | 696 |
| Final analytic cohort | **664** |
| Excluded | 32 |
| Primary outcome rows | 1,537 |
| Studies with ≥1 primary outcome | 664 |
| Mean primary outcomes per study | 2.3 |

---

## Studies by condition

Condition flags are non-mutually-exclusive (11 studies match multiple targets).

| Condition flag | Studies |
|---|---:|
| Chronic back pain | 299 |
| Fibromyalgia | 214 |
| Migraine | 140 |
| Primary headache (non-migraine) | 22 |

---

## Intervention categories

Studies may have multiple categories (pipe-joined). Counts sum to >664.

| Category | Studies |
|---|---:|
| `physical_activity_exercise` | 323 |
| `mind_body` | 248 |
| `pain_education_self_management` | 163 |
| `other_behavioral_treatment` | 160 |
| `psychological_therapy` | 158 |
| `lifestyle_behavioral` | 88 |
| `digital_behavioral` | 69 |
| `complementary_integrative` | 36 |
| `multidisciplinary_program` | 29 |

### Multimodal vs purely behavioral

| Type | Studies |
|---|---:|
| Purely behavioral | 575 |
| Multimodal (behavioral + drug/device/procedure) | 89 |

---

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 456 |
| `pain_interference` | 371 |
| `other` | 366 |
| `feasibility_acceptability` | 223 |
| `mood` | 121 |

### Top subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 341 |
| `pain_interference` → `disability` | 264 |
| `pain_recovery` → `pain_intensity` | 228 |
| `pain_recovery` → `general_pain` | 173 |
| `feasibility_acceptability` → `feasibility_recruitment` | 139 |
| `pain_interference` → `quality_of_life` | 57 |
| `pain_recovery` → `pain_frequency` | 52 |
| `mood` → `anxiety` | 48 |
| `other` → `biological_physiological` | 23 |
| `pain_interference` → `coping_adaptation` | 19 |

---

## Primary outcome mechanistic flag

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 16 |
| `primary_outcome_mechanistic = FALSE` | 648 |

### By condition (`primary_outcome_mechanistic = TRUE`)

| Condition | Studies |
|---|---:|
| Chronic back pain | 7 |
| Fibromyalgia | 7 |
| Migraine | 2 |
| Primary headache | 0 |

---

## Intervention category × outcome category

Outcome-level counts (each outcome row counted once per intervention category assigned to its study; studies with multiple categories contribute to multiple rows).

| Intervention category | pain_recovery | pain_interference | mood | feasibility | other |
|---|---:|---:|---:|---:|---:|
| `physical_activity_exercise` | 214 | 189 | 40 | 80 | 188 |
| `mind_body` | 158 | 153 | 45 | 79 | 95 |
| `pain_education_self_management` | 111 | 113 | 38 | 84 | 59 |
| `other_behavioral_treatment` | 107 | 69 | 30 | 51 | 112 |
| `psychological_therapy` | 100 | 107 | 51 | 45 | 65 |
| `digital_behavioral` | 47 | 58 | 18 | 42 | 30 |
| `lifestyle_behavioral` | 54 | 48 | 16 | 28 | 43 |
| `complementary_integrative` | 28 | 10 | 3 | 5 | 11 |
| `multidisciplinary_program` | 10 | 26 | 4 | 0 | 13 |

---

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 399 |
| RECRUITING | 89 |
| UNKNOWN | 69 |
| NOT_YET_RECRUITING | 46 |
| ACTIVE_NOT_RECRUITING | 24 |
| TERMINATED | 16 |
| ENROLLING_BY_INVITATION | 12 |
| WITHDRAWN | 9 |

### `has_results`

| Has results posted | Studies |
|---|---:|
| No | 589 |
| Yes | 75 |

### `phases` (non-empty)

| Phase | Studies |
|---|---:|
| PHASE2 | 26 |
| PHASE3 | 19 |
| PHASE4 | 13 |
| EARLY_PHASE1 | 6 |
| PHASE1 | 5 |
| Other combinations | 11 |
| Not specified | 584 |

---

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 2017 | 28 |
| 2018 | 34 |
| 2019 | 32 |
| 2020 | 26 |
| 2021 | 48 |
| 2022 | 39 |
| 2023 | 50 |
| 2024 | 42 |
| 2025 | 80 |
| 2026 | 69 |

*(Earlier years also represented; peak registration activity 2025–2026 in this cohort.)*

---

## Exclusions (master pool → analytic cohort)

| Stage | Excluded |
|---|---:|
| Condition | 20 |
| Intervention | 10 |
| Mechanism | 2 |
| **Total excluded** | **32** |

### Condition exclusion reasons

| Reason | Studies |
|---|---:|
| `surgical_postoperative` | 8 |
| `pathology_other` | 5 |
| `cancer_oncology` | 2 |
| `post_traumatic` | 1 |
| `tbi_concussion` | 1 |
| `vestibular_schwannoma` | 1 |
| `visual_snow` | 1 |
| `off_target_primary_population` | 1 |

### Mechanism exclusions

| NCT ID | Reason |
|---|---|
| NCT01857219 | `mechanism_only_outcomes` |
| NCT05773482 | `mechanism_only_outcomes` |

---

## Notes for analysis

- Use `primary_outcome_mechanistic` to stratify studies whose registered primaries are mechanistic but that remain treatment-oriented trials.
- Outcome categories are descriptive only; the large `other/other` bucket (341 rows) warrants manual annotation refinement in a later pass.
- Condition flags overlap; define primary condition for stratified analyses explicitly rather than assuming mutual exclusivity.
