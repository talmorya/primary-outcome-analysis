# Analytic cohort statistics

**Run ID:** `final_cohort_20260922`
**Generated:** 2026-10-05 08:08 UTC

Auto-generated from `data/processed/final_cohort/*.csv` on each `finalize_cohort` run.
Inclusion rules and classification patterns: `FINAL_INCLUSION_RULES.md`.

Filter: `cohort_included == True` in `studies.csv` and `primary_outcomes.csv`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (pre-filter) | 696 |
| Final analytic cohort | **666** |
| Excluded | 30 |
| Primary outcome rows | 1539 |
| Studies with ≥1 primary outcome | 655 |
| Mean primary outcomes per study | 2.3 |

## Exclusions by stage

- **Condition:** 20
- **Intervention:** 10
- **Mechanism (historical audit label):** 0

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

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Chronic back pain | 299 |
| Fibromyalgia | 216 |
| Migraine | 140 |
| Primary headache (non-migraine) | 22 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 319 |
| `mind_body_integrative` | 272 |
| `education_self_management` | 218 |
| `other_behavioral_treatment` | 159 |
| `psychological_cognitive` | 152 |
| `digital_health_delivery` | 70 |
| `multidisciplinary_interdisciplinary` | 29 |
| `neuroplastic_recovery_therapy` | 22 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 582 |
| Multimodal | 84 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 420 |
| `pain_interference` | 364 |
| `other` | 322 |
| `feasibility_acceptability` | 221 |
| `mood` | 121 |
| `mechanistic` | 91 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 319 |
| `pain_interference` → `disability` | 257 |
| `pain_recovery` → `pain_intensity` | 228 |
| `feasibility_acceptability` → `feasibility_recruitment` | 137 |
| `pain_recovery` → `general_pain` | 137 |
| `pain_interference` → `quality_of_life` | 57 |
| `pain_recovery` → `pain_frequency` | 52 |
| `mood` → `anxiety` | 48 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 38 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 32 |
| `mood` → `depression` | 30 |
| `pain_interference` → `interference` | 29 |
| `feasibility_acceptability` → `adherence_fidelity` | 20 |
| `mechanistic` → `other_mechanistic` | 19 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 18 |
| `primary_outcome_mechanistic = FALSE` | 648 |

### By condition (`primary_outcome_mechanistic = TRUE`)

| Condition | Studies |
|---|---:|
| Chronic back pain | 7 |
| Fibromyalgia | 9 |
| Migraine | 2 |
| Primary headache | 0 |

## Intervention category × outcome category

Outcome-row counts; each study's intervention categories are applied to all its primary outcomes.

| Intervention category | `feasibility_acceptability` | `mechanistic` | `mood` | `other` | `pain_interference` | `pain_recovery` |
|---|---:|---:|---:|---:|---:|---:|
| `physical_rehabilitation` | 79 | 37 | 40 | 171 | 187 | 192 |
| `mind_body_integrative` | 80 | 30 | 46 | 87 | 154 | 163 |
| `education_self_management` | 93 | 14 | 49 | 85 | 140 | 133 |
| `other_behavioral_treatment` | 50 | 41 | 30 | 88 | 68 | 84 |
| `psychological_cognitive` | 44 | 8 | 51 | 62 | 102 | 94 |
| `digital_health_delivery` | 43 | 2 | 18 | 32 | 60 | 48 |
| `multidisciplinary_interdisciplinary` | 0 | 1 | 4 | 12 | 26 | 10 |
| `neuroplastic_recovery_therapy` | 16 | 0 | 1 | 1 | 13 | 21 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 399 |
| RECRUITING | 90 |
| UNKNOWN | 70 |
| NOT_YET_RECRUITING | 46 |
| ACTIVE_NOT_RECRUITING | 24 |
| TERMINATED | 16 |
| ENROLLING_BY_INVITATION | 12 |
| WITHDRAWN | 9 |

### `has_results`

| Posted results | Studies |
|---|---:|
| False | 591 |
| True | 75 |

### `phases` (non-empty)

| Phase | Studies |
|---|---:|
| PHASE2 | 26 |
| PHASE3 | 19 |
| PHASE4 | 13 |
| PHASE1 | PHASE2 | 6 |
| EARLY_PHASE1 | 6 |
| PHASE2 | PHASE3 | 5 |
| PHASE1 | 5 |
| (empty) | 586 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 14 |
| 2006 | 11 |
| 2007 | 20 |
| 2008 | 11 |
| 2009 | 19 |
| 2010 | 15 |
| 2011 | 20 |
| 2012 | 13 |
| 2013 | 19 |
| 2014 | 19 |
| 2015 | 26 |
| 2016 | 19 |
| 2017 | 28 |
| 2018 | 34 |
| 2019 | 32 |
| 2020 | 26 |
| 2021 | 48 |
| 2022 | 39 |
| 2023 | 51 |
| 2024 | 42 |
| 2025 | 80 |
| 2026 | 69 |

## Notes for analysis

- Outcome categories are descriptive; see `outcome_category_review_flag` and `reports/exploration/revised_cohort/outcome_other_category_review.md`.
- `primary_outcome_mechanistic` stratifies studies whose registered primaries are all mechanistic by lexicon.
- Condition flags overlap; define primary condition explicitly for stratified analyses.
