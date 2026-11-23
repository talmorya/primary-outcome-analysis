# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v3`
**Generated:** 2026-11-23 14:03 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **824** |
| Excluded | 112 |
| Primary outcome rows (included studies) | 1900 |
| Studies with ≥1 primary outcome | 811 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 112

### By general reason (`exclusion_reason`)

- `condition`: 74
- `acute`: 38

### By specific rule (start of `exclusion_detail`)

- `subacute_perioperative`: 26
- `acute_pain`: 21
- `short_pain_window`: 17
- `pregnancy_related`: 16
- `not_about_pain`: 15
- `no_target_match`: 8
- `pathology_other`: 6
- `cancer_oncology`: 3

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Back pain | 423 |
| Fibromyalgia | 212 |
| Migraine | 139 |
| Primary headache (non-migraine) | 103 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 394 |
| `mind_body_integrative` | 316 |
| `education_self_management` | 261 |
| `psychological_cognitive` | 175 |
| `other_behavioral_treatment` | 174 |
| `digital_health_delivery` | 79 |
| `neuroplastic_recovery_therapy` | 36 |
| `multidisciplinary_interdisciplinary` | 35 |
| `occupational_ergonomics_rtw` | 27 |
| `experimental_research_paradigm` | 17 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 723 |
| Multimodal | 101 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_interference` | 516 |
| `pain_recovery` | 516 |
| `feasibility_acceptability` | 298 |
| `mechanistic` | 192 |
| `physical_performance` | 143 |
| `mood` | 140 |
| `associated_symptoms` | 38 |
| `other` | 34 |
| `healthcare_use_cost` | 23 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `pain_interference` → `disability` | 345 |
| `pain_recovery` → `pain_intensity` | 269 |
| `pain_recovery` → `general_pain` | 176 |
| `feasibility_acceptability` → `feasibility_recruitment` | 98 |
| `physical_performance` → `mobility_balance_gait` | 81 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 81 |
| `pain_interference` → `quality_of_life` | 67 |
| `mechanistic` → `sensory_qst` | 64 |
| `pain_recovery` → `pain_frequency` | 63 |
| `feasibility_acceptability` → `adherence_fidelity` | 62 |
| `pain_interference` → `coping_adaptation` | 53 |
| `mechanistic` → `biological_structural` | 52 |
| `mood` → `anxiety` | 50 |
| `physical_performance` → `strength_endurance` | 50 |
| `feasibility_acceptability` → `other_feasibility` | 41 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 492 |
| RECRUITING | 107 |
| UNKNOWN | 82 |
| NOT_YET_RECRUITING | 61 |
| ACTIVE_NOT_RECRUITING | 28 |
| TERMINATED | 25 |
| ENROLLING_BY_INVITATION | 16 |
| WITHDRAWN | 12 |
| SUSPENDED | 1 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 13 |
| 2006 | 15 |
| 2007 | 19 |
| 2008 | 16 |
| 2009 | 21 |
| 2010 | 18 |
| 2011 | 24 |
| 2012 | 20 |
| 2013 | 20 |
| 2014 | 23 |
| 2015 | 29 |
| 2016 | 26 |
| 2017 | 35 |
| 2018 | 41 |
| 2019 | 43 |
| 2020 | 37 |
| 2021 | 47 |
| 2022 | 49 |
| 2023 | 56 |
| 2024 | 47 |
| 2025 | 97 |
| 2026 | 117 |
