# Analytic cohort statistics

**Run ID:** `cohort_simplified_v1`
**Generated:** 2026-11-09 10:45 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **898** |
| Excluded | 38 |
| Primary outcome rows (included studies) | 2090 |
| Studies with ≥1 primary outcome | 885 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 38

### By general reason (`exclusion_reason`)

- `acute`: 20
- `condition`: 18

### By specific rule (start of `exclusion_detail`)

- `acute_pain`: 19
- `no_target_match`: 9
- `pathology_other`: 6
- `cancer_oncology`: 3
- `acute_and_chronic_in_inclusion`: 1

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Chronic back pain | 481 |
| Fibromyalgia | 215 |
| Migraine | 144 |
| Primary headache (non-migraine) | 112 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 443 |
| `mind_body_integrative` | 315 |
| `education_self_management` | 263 |
| `other_behavioral_treatment` | 249 |
| `psychological_cognitive` | 174 |
| `digital_health_delivery` | 81 |
| `multidisciplinary_interdisciplinary` | 39 |
| `neuroplastic_recovery_therapy` | 24 |
| `experimental_research_paradigm` | 19 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 781 |
| Multimodal | 117 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 550 |
| `pain_interference` | 489 |
| `other` | 485 |
| `feasibility_acceptability` | 302 |
| `mood` | 139 |
| `mechanistic` | 125 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 483 |
| `pain_interference` → `disability` | 349 |
| `pain_recovery` → `pain_intensity` | 299 |
| `pain_recovery` → `general_pain` | 189 |
| `feasibility_acceptability` → `feasibility_recruitment` | 183 |
| `pain_interference` → `quality_of_life` | 69 |
| `pain_recovery` → `pain_frequency` | 59 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 58 |
| `mood` → `anxiety` | 51 |
| `mechanistic` → `sensory_qst` | 39 |
| `mood` → `distress_stress` | 38 |
| `mood` → `depression` | 36 |
| `pain_interference` → `interference` | 36 |
| `mechanistic` → `other_mechanistic` | 33 |
| `mechanistic` → `neuroimaging_neural` | 30 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 25 |
| `primary_outcome_mechanistic = FALSE` | 873 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 538 |
| RECRUITING | 115 |
| UNKNOWN | 87 |
| NOT_YET_RECRUITING | 66 |
| ACTIVE_NOT_RECRUITING | 33 |
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
| 2009 | 23 |
| 2010 | 20 |
| 2011 | 24 |
| 2012 | 21 |
| 2013 | 22 |
| 2014 | 24 |
| 2015 | 32 |
| 2016 | 28 |
| 2017 | 37 |
| 2018 | 45 |
| 2019 | 44 |
| 2020 | 42 |
| 2021 | 51 |
| 2022 | 53 |
| 2023 | 63 |
| 2024 | 52 |
| 2025 | 104 |
| 2026 | 129 |
