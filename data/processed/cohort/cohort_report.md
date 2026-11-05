# Analytic cohort statistics

**Run ID:** `cohort_simplified_v1`
**Generated:** 2026-11-05 14:27 UTC

Auto-generated from `data/processed/cohort/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 789 |
| Included | **752** |
| Excluded | 37 |
| Primary outcome rows (included studies) | 1738 |
| Studies with ≥1 primary outcome | 739 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 37

### By general reason (`exclusion_reason`)

- `condition`: 31
- `acute`: 6

### By specific rule (start of `exclusion_detail`)

- `no_eligible_target_after_migraine_overlap`: 13
- `no_target_match`: 8
- `pathology_other`: 7
- `acute_pain`: 6
- `cancer_oncology`: 3

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Chronic back pain | 336 |
| Fibromyalgia | 227 |
| Migraine | 153 |
| Primary headache (non-migraine) | 50 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 348 |
| `mind_body_integrative` | 295 |
| `education_self_management` | 237 |
| `other_behavioral_treatment` | 189 |
| `psychological_cognitive` | 173 |
| `digital_health_delivery` | 78 |
| `multidisciplinary_interdisciplinary` | 32 |
| `neuroplastic_recovery_therapy` | 25 |
| `experimental_research_paradigm` | 18 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 659 |
| Multimodal | 93 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 452 |
| `pain_interference` | 395 |
| `other` | 379 |
| `feasibility_acceptability` | 268 |
| `mood` | 137 |
| `mechanistic` | 107 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 377 |
| `pain_interference` → `disability` | 278 |
| `pain_recovery` → `pain_intensity` | 240 |
| `feasibility_acceptability` → `feasibility_recruitment` | 164 |
| `pain_recovery` → `general_pain` | 156 |
| `pain_interference` → `quality_of_life` | 60 |
| `mood` → `anxiety` | 55 |
| `pain_recovery` → `pain_frequency` | 53 |
| `feasibility_acceptability` → `acceptability_satisfaction` | 48 |
| `mechanistic` → `sensory_qst` | 37 |
| `mood` → `distress_stress` | 37 |
| `mood` → `depression` | 34 |
| `pain_interference` → `interference` | 30 |
| `mechanistic` → `neuroimaging_neural` | 26 |
| `feasibility_acceptability` → `adherence_fidelity` | 24 |

## Primary outcome mechanistic flag (study-level)

| Flag | Studies |
|---|---:|
| `primary_outcome_mechanistic = TRUE` | 23 |
| `primary_outcome_mechanistic = FALSE` | 729 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 456 |
| RECRUITING | 100 |
| UNKNOWN | 75 |
| NOT_YET_RECRUITING | 49 |
| TERMINATED | 24 |
| ACTIVE_NOT_RECRUITING | 23 |
| WITHDRAWN | 12 |
| ENROLLING_BY_INVITATION | 12 |
| SUSPENDED | 1 |

## Registration year (`study_first_post_date`)

| Year | Studies |
|---|---:|
| 1999 | 4 |
| 2001 | 1 |
| 2003 | 3 |
| 2004 | 3 |
| 2005 | 16 |
| 2006 | 11 |
| 2007 | 21 |
| 2008 | 11 |
| 2009 | 20 |
| 2010 | 15 |
| 2011 | 23 |
| 2012 | 16 |
| 2013 | 22 |
| 2014 | 21 |
| 2015 | 27 |
| 2016 | 22 |
| 2017 | 29 |
| 2018 | 38 |
| 2019 | 40 |
| 2020 | 33 |
| 2021 | 50 |
| 2022 | 45 |
| 2023 | 57 |
| 2024 | 48 |
| 2025 | 85 |
| 2026 | 91 |
