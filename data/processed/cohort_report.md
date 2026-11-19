# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v3`
**Generated:** 2026-11-19 10:41 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **797** |
| Excluded | 139 |
| Primary outcome rows (included studies) | 1838 |
| Studies with ≥1 primary outcome | 784 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 139

### By general reason (`exclusion_reason`)

- `condition`: 108
- `acute`: 31

### By specific rule (start of `exclusion_detail`)

- `subacute_perioperative`: 38
- `general_population_sample`: 25
- `acute_pain`: 20
- `pregnancy_related`: 16
- `not_about_pain`: 12
- `short_pain_window`: 11
- `no_target_match`: 8
- `pathology_other`: 6
- `cancer_oncology`: 3

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Back pain | 402 |
| Fibromyalgia | 210 |
| Migraine | 137 |
| Primary headache (non-migraine) | 99 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 378 |
| `mind_body_integrative` | 306 |
| `education_self_management` | 256 |
| `psychological_cognitive` | 175 |
| `other_behavioral_treatment` | 167 |
| `digital_health_delivery` | 76 |
| `multidisciplinary_interdisciplinary` | 36 |
| `neuroplastic_recovery_therapy` | 34 |
| `occupational_ergonomics_rtw` | 24 |
| `experimental_research_paradigm` | 18 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 696 |
| Multimodal | 101 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 491 |
| `pain_interference` | 446 |
| `other` | 397 |
| `feasibility_acceptability` | 267 |
| `mood` | 128 |
| `mechanistic` | 109 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 395 |
| `pain_interference` → `disability` | 324 |
| `pain_recovery` → `pain_intensity` | 274 |
| `feasibility_acceptability` → `feasibility_recruitment` | 159 |
| `pain_recovery` → `general_pain` | 156 |
| `pain_interference` → `quality_of_life` | 64 |
| `pain_recovery` → `pain_frequency` | 59 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 51 |
| `mood` → `anxiety` | 49 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 35 |
| `pain_interference` → `interference` | 33 |
| `mood` → `depression` | 32 |
| `mechanistic` → `other_mechanistic` | 27 |
| `feasibility_acceptability` → `adherence_fidelity` | 26 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 22 |
| `primary_outcome_mechanistic = FALSE` | 775 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 478 |
| RECRUITING | 102 |
| UNKNOWN | 79 |
| NOT_YET_RECRUITING | 57 |
| ACTIVE_NOT_RECRUITING | 28 |
| TERMINATED | 26 |
| ENROLLING_BY_INVITATION | 14 |
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
| 2006 | 14 |
| 2007 | 18 |
| 2008 | 14 |
| 2009 | 21 |
| 2010 | 18 |
| 2011 | 24 |
| 2012 | 20 |
| 2013 | 19 |
| 2014 | 23 |
| 2015 | 30 |
| 2016 | 26 |
| 2017 | 34 |
| 2018 | 41 |
| 2019 | 41 |
| 2020 | 37 |
| 2021 | 46 |
| 2022 | 47 |
| 2023 | 55 |
| 2024 | 45 |
| 2025 | 89 |
| 2026 | 111 |
