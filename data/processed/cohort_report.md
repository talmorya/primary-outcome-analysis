# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v2`
**Generated:** 2026-11-10 13:08 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **880** |
| Excluded | 56 |
| Primary outcome rows (included studies) | 2003 |
| Studies with ≥1 primary outcome | 867 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 56

### By general reason (`exclusion_reason`)

- `condition`: 34
- `acute`: 22

### By specific rule (start of `exclusion_detail`)

- `acute_pain`: 20
- `pregnancy_related`: 16
- `no_target_match`: 9
- `pathology_other`: 6
- `cancer_oncology`: 3
- `acute_bp_symptom_relief`: 2

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Back pain | 465 |
| Fibromyalgia | 214 |
| Migraine | 144 |
| Primary headache (non-migraine) | 111 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 432 |
| `mind_body_integrative` | 310 |
| `education_self_management` | 258 |
| `other_behavioral_treatment` | 240 |
| `psychological_cognitive` | 174 |
| `digital_health_delivery` | 80 |
| `multidisciplinary_interdisciplinary` | 39 |
| `neuroplastic_recovery_therapy` | 24 |
| `experimental_research_paradigm` | 19 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 766 |
| Multimodal | 114 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 533 |
| `pain_interference` | 479 |
| `other` | 437 |
| `feasibility_acceptability` | 301 |
| `mood` | 131 |
| `mechanistic` | 122 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 435 |
| `pain_interference` → `disability` | 343 |
| `pain_recovery` → `pain_intensity` | 290 |
| `feasibility_acceptability` → `feasibility_recruitment` | 182 |
| `pain_recovery` → `general_pain` | 181 |
| `pain_interference` → `quality_of_life` | 68 |
| `pain_recovery` → `pain_frequency` | 59 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 58 |
| `mood` → `anxiety` | 49 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 36 |
| `pain_interference` → `interference` | 34 |
| `mood` → `depression` | 33 |
| `mechanistic` → `other_mechanistic` | 33 |
| `mechanistic` → `neuroimaging_neural` | 30 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 25 |
| `primary_outcome_mechanistic = FALSE` | 855 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 526 |
| RECRUITING | 111 |
| UNKNOWN | 87 |
| NOT_YET_RECRUITING | 66 |
| ACTIVE_NOT_RECRUITING | 31 |
| TERMINATED | 27 |
| ENROLLING_BY_INVITATION | 16 |
| WITHDRAWN | 15 |
| SUSPENDED | 1 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 18 |
| 2006 | 15 |
| 2007 | 23 |
| 2008 | 17 |
| 2009 | 22 |
| 2010 | 20 |
| 2011 | 24 |
| 2012 | 20 |
| 2013 | 21 |
| 2014 | 24 |
| 2015 | 31 |
| 2016 | 28 |
| 2017 | 36 |
| 2018 | 45 |
| 2019 | 44 |
| 2020 | 41 |
| 2021 | 50 |
| 2022 | 53 |
| 2023 | 61 |
| 2024 | 51 |
| 2025 | 101 |
| 2026 | 124 |
