# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v3`
**Generated:** 2026-11-18 16:54 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **843** |
| Excluded | 93 |
| Primary outcome rows (included studies) | 1916 |
| Studies with ≥1 primary outcome | 830 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 93

### By general reason (`exclusion_reason`)

- `condition`: 71
- `acute`: 22

### By specific rule (start of `exclusion_detail`)

- `subacute_perioperative`: 38
- `acute_pain`: 20
- `pregnancy_related`: 16
- `no_target_match`: 8
- `pathology_other`: 6
- `cancer_oncology`: 3
- `acute_bp_symptom_relief`: 2

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Back pain | 431 |
| Fibromyalgia | 213 |
| Migraine | 143 |
| Primary headache (non-migraine) | 110 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 404 |
| `mind_body_integrative` | 319 |
| `education_self_management` | 268 |
| `other_behavioral_treatment` | 179 |
| `psychological_cognitive` | 176 |
| `digital_health_delivery` | 80 |
| `multidisciplinary_interdisciplinary` | 36 |
| `neuroplastic_recovery_therapy` | 34 |
| `occupational_ergonomics_rtw` | 31 |
| `experimental_research_paradigm` | 19 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 738 |
| Multimodal | 105 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 516 |
| `pain_interference` | 459 |
| `other` | 416 |
| `feasibility_acceptability` | 277 |
| `mood` | 131 |
| `mechanistic` | 117 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 414 |
| `pain_interference` → `disability` | 328 |
| `pain_recovery` → `pain_intensity` | 278 |
| `pain_recovery` → `general_pain` | 177 |
| `feasibility_acceptability` → `feasibility_recruitment` | 167 |
| `pain_interference` → `quality_of_life` | 68 |
| `pain_recovery` → `pain_frequency` | 59 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 52 |
| `mood` → `anxiety` | 49 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 36 |
| `mood` → `depression` | 33 |
| `pain_interference` → `interference` | 33 |
| `mechanistic` → `neuroimaging_neural` | 30 |
| `mechanistic` → `other_mechanistic` | 28 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 25 |
| `primary_outcome_mechanistic = FALSE` | 818 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 503 |
| RECRUITING | 106 |
| UNKNOWN | 83 |
| NOT_YET_RECRUITING | 65 |
| ACTIVE_NOT_RECRUITING | 29 |
| TERMINATED | 27 |
| ENROLLING_BY_INVITATION | 15 |
| WITHDRAWN | 14 |
| SUSPENDED | 1 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 15 |
| 2006 | 15 |
| 2007 | 22 |
| 2008 | 16 |
| 2009 | 22 |
| 2010 | 19 |
| 2011 | 24 |
| 2012 | 20 |
| 2013 | 21 |
| 2014 | 23 |
| 2015 | 31 |
| 2016 | 27 |
| 2017 | 35 |
| 2018 | 43 |
| 2019 | 41 |
| 2020 | 40 |
| 2021 | 49 |
| 2022 | 51 |
| 2023 | 58 |
| 2024 | 46 |
| 2025 | 96 |
| 2026 | 118 |
