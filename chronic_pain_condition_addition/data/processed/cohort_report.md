# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v3`
**Generated:** 2026-11-26 09:16 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 1470 |
| Included | **1307** |
| Excluded | 163 |
| Primary outcome rows (included studies) | 3282 |
| Studies with ≥1 primary outcome | 1294 |
| Mean primary outcomes per study | 2.5 |

## Condition exclusions

- **Excluded at condition stage:** 163

### By general reason (`exclusion_reason`)

- `condition`: 111
- `acute`: 52

### By specific rule (start of `exclusion_detail`)

- `acute_pain`: 31
- `subacute_perioperative`: 27
- `not_about_pain`: 24
- `cancer_oncology`: 23
- `short_pain_window`: 21
- `pregnancy_related`: 19
- `pathology_other`: 10
- `no_target_match`: 8

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Back pain | 425 |
| Fibromyalgia | 212 |
| Migraine | 139 |
| Primary headache (non-migraine) | 103 |
| Chronic pain | 546 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 535 |
| `mind_body_integrative` | 513 |
| `education_self_management` | 447 |
| `psychological_cognitive` | 328 |
| `other_behavioral_treatment` | 310 |
| `digital_health_delivery` | 139 |
| `neuroplastic_recovery_therapy` | 49 |
| `multidisciplinary_interdisciplinary` | 43 |
| `occupational_ergonomics_rtw` | 31 |
| `experimental_research_paradigm` | 26 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 1182 |
| Multimodal | 125 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_interference` | 821 |
| `pain_recovery` | 772 |
| `feasibility_acceptability` | 625 |
| `mood` | 298 |
| `mechanistic` | 237 |
| `other` | 225 |
| `physical_performance` | 158 |
| `associated_symptoms` | 73 |
| `healthcare_use_cost` | 73 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `pain_interference` → `disability` | 432 |
| `pain_recovery` → `pain_intensity` | 394 |
| `pain_recovery` → `general_pain` | 295 |
| `feasibility_acceptability` → `feasibility_recruitment` | 221 |
| `other` → `other` | 218 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 183 |
| `pain_interference` → `quality_of_life` | 140 |
| `pain_interference` → `coping_adaptation` | 124 |
| `feasibility_acceptability` → `adherence_fidelity` | 122 |
| `mood` → `distress_stress` | 102 |
| `pain_interference` → `interference` | 101 |
| `mood` → `anxiety` | 95 |
| `physical_performance` → `mobility_balance_gait` | 87 |
| `mechanistic` → `sensory_qst` | 80 |
| `feasibility_acceptability` → `other_feasibility` | 74 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 779 |
| RECRUITING | 181 |
| UNKNOWN | 132 |
| NOT_YET_RECRUITING | 86 |
| ACTIVE_NOT_RECRUITING | 47 |
| TERMINATED | 37 |
| WITHDRAWN | 22 |
| ENROLLING_BY_INVITATION | 21 |
| SUSPENDED | 2 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 15 |
| 2006 | 17 |
| 2007 | 20 |
| 2008 | 21 |
| 2009 | 24 |
| 2010 | 21 |
| 2011 | 30 |
| 2012 | 28 |
| 2013 | 29 |
| 2014 | 38 |
| 2015 | 40 |
| 2016 | 48 |
| 2017 | 62 |
| 2018 | 76 |
| 2019 | 89 |
| 2020 | 81 |
| 2021 | 90 |
| 2022 | 85 |
| 2023 | 90 |
| 2024 | 89 |
| 2025 | 138 |
| 2026 | 165 |
