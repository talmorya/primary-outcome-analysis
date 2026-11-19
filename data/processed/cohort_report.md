# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v3`
**Generated:** 2026-11-19 11:45 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **812** |
| Excluded | 124 |
| Primary outcome rows (included studies) | 1861 |
| Studies with ≥1 primary outcome | 799 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 124

### By general reason (`exclusion_reason`)

- `condition`: 86
- `acute`: 38

### By specific rule (start of `exclusion_detail`)

- `subacute_perioperative`: 38
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
| Back pain | 412 |
| Fibromyalgia | 211 |
| Migraine | 139 |
| Primary headache (non-migraine) | 103 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 386 |
| `mind_body_integrative` | 310 |
| `education_self_management` | 258 |
| `psychological_cognitive` | 174 |
| `other_behavioral_treatment` | 171 |
| `digital_health_delivery` | 77 |
| `multidisciplinary_interdisciplinary` | 34 |
| `neuroplastic_recovery_therapy` | 34 |
| `occupational_ergonomics_rtw` | 27 |
| `experimental_research_paradigm` | 17 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 713 |
| Multimodal | 99 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 506 |
| `pain_interference` | 443 |
| `other` | 401 |
| `feasibility_acceptability` | 273 |
| `mood` | 128 |
| `mechanistic` | 110 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 399 |
| `pain_interference` → `disability` | 321 |
| `pain_recovery` → `pain_intensity` | 274 |
| `pain_recovery` → `general_pain` | 171 |
| `feasibility_acceptability` → `feasibility_recruitment` | 166 |
| `pain_interference` → `quality_of_life` | 63 |
| `pain_recovery` → `pain_frequency` | 59 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 51 |
| `mood` → `anxiety` | 49 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 36 |
| `pain_interference` → `interference` | 33 |
| `mood` → `depression` | 31 |
| `mechanistic` → `other_mechanistic` | 27 |
| `mechanistic` → `neuroimaging_neural` | 25 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 23 |
| `primary_outcome_mechanistic = FALSE` | 789 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 487 |
| RECRUITING | 103 |
| UNKNOWN | 80 |
| NOT_YET_RECRUITING | 61 |
| ACTIVE_NOT_RECRUITING | 28 |
| TERMINATED | 25 |
| ENROLLING_BY_INVITATION | 15 |
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
| 2017 | 34 |
| 2018 | 41 |
| 2019 | 41 |
| 2020 | 37 |
| 2021 | 47 |
| 2022 | 49 |
| 2023 | 55 |
| 2024 | 45 |
| 2025 | 93 |
| 2026 | 115 |
