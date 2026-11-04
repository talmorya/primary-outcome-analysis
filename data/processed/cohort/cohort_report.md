# Analytic cohort statistics

**Run ID:** `cohort_simplified_v1`
**Generated:** 2026-11-04 12:52 UTC

Auto-generated from `data/processed/cohort/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 789 |
| Included | **688** |
| Excluded | 101 |
| Primary outcome rows (included studies) | 1499 |
| Studies with ≥1 primary outcome | 675 |
| Mean primary outcomes per study | 2.2 |

## Condition exclusions

- **Excluded at condition stage:** 101

### By general reason (`exclusion_reason`)

- `condition`: 95
- `acute`: 6

### By specific rule (start of `exclusion_detail`)

- `population_non_target_conditions`: 65
- `no_eligible_target_after_migraine_overlap`: 12
- `no_target_match`: 8
- `pathology_other`: 7
- `acute_pain`: 6
- `cancer_oncology`: 3

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Chronic back pain | 307 |
| Fibromyalgia | 207 |
| Migraine | 144 |
| Primary headache (non-migraine) | 39 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 315 |
| `mind_body_integrative` | 272 |
| `education_self_management` | 217 |
| `other_behavioral_treatment` | 172 |
| `psychological_cognitive` | 161 |
| `digital_health_delivery` | 67 |
| `multidisciplinary_interdisciplinary` | 32 |
| `neuroplastic_recovery_therapy` | 25 |
| `experimental_research_paradigm` | 18 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 598 |
| Multimodal | 90 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 414 |
| `pain_interference` | 362 |
| `other` | 308 |
| `feasibility_acceptability` | 226 |
| `mood` | 112 |
| `mechanistic` | 77 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 306 |
| `pain_interference` → `disability` | 258 |
| `pain_recovery` → `pain_intensity` | 216 |
| `pain_recovery` → `general_pain` | 143 |
| `feasibility_acceptability` → `feasibility_recruitment` | 134 |
| `pain_interference` → `quality_of_life` | 57 |
| `pain_recovery` → `pain_frequency` | 52 |
| `mood` → `anxiety` | 46 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 42 |
| `mood` → `depression` | 30 |
| `mood` → `distress_stress` | 28 |
| `pain_interference` → `interference` | 25 |
| `mechanistic` → `neuroimaging_neural` | 23 |
| `feasibility_acceptability` → `safety` | 22 |
| `mechanistic` → `other_mechanistic` | 21 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 20 |
| `primary_outcome_mechanistic = FALSE` | 668 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 423 |
| RECRUITING | 89 |
| UNKNOWN | 73 |
| NOT_YET_RECRUITING | 41 |
| TERMINATED | 24 |
| ACTIVE_NOT_RECRUITING | 20 |
| WITHDRAWN | 9 |
| ENROLLING_BY_INVITATION | 9 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 15 |
| 2006 | 11 |
| 2007 | 20 |
| 2008 | 11 |
| 2009 | 20 |
| 2010 | 13 |
| 2011 | 22 |
| 2012 | 15 |
| 2013 | 19 |
| 2014 | 20 |
| 2015 | 27 |
| 2016 | 22 |
| 2017 | 26 |
| 2018 | 36 |
| 2019 | 35 |
| 2020 | 30 |
| 2021 | 47 |
| 2022 | 39 |
| 2023 | 52 |
| 2024 | 43 |
| 2025 | 71 |
| 2026 | 83 |
