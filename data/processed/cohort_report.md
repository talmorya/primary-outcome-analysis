# Analytic cohort statistics

**Run ID:** `cohort_conditions_field_v3`
**Generated:** 2026-11-18 16:21 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 936 |
| Included | **832** |
| Excluded | 104 |
| Primary outcome rows (included studies) | 1899 |
| Studies with ≥1 primary outcome | 819 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 104

### By general reason (`exclusion_reason`)

- `condition`: 82
- `acute`: 22

### By specific rule (start of `exclusion_detail`)

- `subacute_perioperative`: 49
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
| Back pain | 420 |
| Fibromyalgia | 213 |
| Migraine | 143 |
| Primary headache (non-migraine) | 110 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 398 |
| `mind_body_integrative` | 316 |
| `education_self_management` | 263 |
| `other_behavioral_treatment` | 179 |
| `psychological_cognitive` | 170 |
| `digital_health_delivery` | 78 |
| `multidisciplinary_interdisciplinary` | 34 |
| `neuroplastic_recovery_therapy` | 32 |
| `occupational_ergonomics_rtw` | 30 |
| `experimental_research_paradigm` | 18 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 729 |
| Multimodal | 103 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 509 |
| `pain_interference` | 456 |
| `other` | 413 |
| `feasibility_acceptability` | 277 |
| `mood` | 128 |
| `mechanistic` | 116 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 411 |
| `pain_interference` → `disability` | 325 |
| `pain_recovery` → `pain_intensity` | 272 |
| `pain_recovery` → `general_pain` | 176 |
| `feasibility_acceptability` → `feasibility_recruitment` | 167 |
| `pain_interference` → `quality_of_life` | 68 |
| `pain_recovery` → `pain_frequency` | 59 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 52 |
| `mood` → `anxiety` | 47 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 36 |
| `pain_interference` → `interference` | 33 |
| `mood` → `depression` | 32 |
| `mechanistic` → `neuroimaging_neural` | 29 |
| `mechanistic` → `other_mechanistic` | 28 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 25 |
| `primary_outcome_mechanistic = FALSE` | 807 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 496 |
| RECRUITING | 105 |
| UNKNOWN | 83 |
| NOT_YET_RECRUITING | 64 |
| ACTIVE_NOT_RECRUITING | 29 |
| TERMINATED | 26 |
| WITHDRAWN | 14 |
| ENROLLING_BY_INVITATION | 14 |
| SUSPENDED | 1 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 15 |
| 2006 | 13 |
| 2007 | 22 |
| 2008 | 16 |
| 2009 | 22 |
| 2010 | 19 |
| 2011 | 24 |
| 2012 | 19 |
| 2013 | 21 |
| 2014 | 23 |
| 2015 | 31 |
| 2016 | 27 |
| 2017 | 35 |
| 2018 | 42 |
| 2019 | 40 |
| 2020 | 39 |
| 2021 | 49 |
| 2022 | 49 |
| 2023 | 58 |
| 2024 | 46 |
| 2025 | 95 |
| 2026 | 116 |
