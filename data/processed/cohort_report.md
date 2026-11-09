# Analytic cohort statistics

**Run ID:** `cohort_simplified_v1`
**Generated:** 2026-11-09 10:18 UTC

Auto-generated from `data/processed/studies.csv` on each `finalize_cohort` run.
Inclusion rules: `docs/COHORT_FILTERING_RULES.md`. Column definitions: `docs/DATA_COLUMNS.md`.

---

## Cohort size

| Metric | Count |
|---|---:|
| Master pool (API retrieval) | 789 |
| Included | **766** |
| Excluded | 23 |
| Primary outcome rows (included studies) | 1772 |
| Studies with ≥1 primary outcome | 753 |
| Mean primary outcomes per study | 2.3 |

## Condition exclusions

- **Excluded at condition stage:** 23

### By general reason (`exclusion_reason`)

- `condition`: 17
- `acute`: 6

### By specific rule (start of `exclusion_detail`)

- `no_target_match`: 7
- `pathology_other`: 7
- `acute_pain`: 6
- `cancer_oncology`: 3

## Studies by condition

Flags are non-mutually-exclusive.

| Condition flag | Studies |
|---|---:|
| Chronic back pain | 315 |
| Fibromyalgia | 214 |
| Migraine | 144 |
| Primary headache (non-migraine) | 111 |

## Intervention categories

Pipe-joined; study counts may sum to > cohort size.

| Category | Studies |
|---|---:|
| `physical_rehabilitation` | 353 |
| `mind_body_integrative` | 303 |
| `education_self_management` | 240 |
| `other_behavioral_treatment` | 191 |
| `psychological_cognitive` | 176 |
| `digital_health_delivery` | 80 |
| `multidisciplinary_interdisciplinary` | 32 |
| `neuroplastic_recovery_therapy` | 25 |
| `experimental_research_paradigm` | 18 |

### Multimodal vs not multimodal

| Type | Studies |
|---|---:|
| Not multimodal | 669 |
| Multimodal | 97 |

## Primary outcome categories

| `outcome_category` | Outcome rows |
|---|---:|
| `pain_recovery` | 472 |
| `pain_interference` | 401 |
| `other` | 386 |
| `feasibility_acceptability` | 268 |
| `mood` | 137 |
| `mechanistic` | 108 |

### Top outcome subcategories

| Category → subcategory | Outcome rows |
|---|---:|
| `other` → `other` | 384 |
| `pain_interference` → `disability` | 283 |
| `pain_recovery` → `pain_intensity` | 245 |
| `pain_recovery` → `general_pain` | 165 |
| `feasibility_acceptability` → `feasibility_recruitment` | 164 |
| `pain_interference` → `quality_of_life` | 61 |
| `pain_recovery` → `pain_frequency` | 59 |
| `mood` → `anxiety` | 55 |
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
| `primary_outcome_mechanistic = FALSE` | 743 |

## Trial status and phase

### `overall_status`

| Status | Studies |
|---|---:|
| COMPLETED | 463 |
| RECRUITING | 101 |
| UNKNOWN | 77 |
| NOT_YET_RECRUITING | 50 |
| TERMINATED | 25 |
| ACTIVE_NOT_RECRUITING | 25 |
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
| 2006 | 12 |
| 2007 | 21 |
| 2008 | 11 |
| 2009 | 20 |
| 2010 | 17 |
| 2011 | 24 |
| 2012 | 16 |
| 2013 | 22 |
| 2014 | 21 |
| 2015 | 27 |
| 2016 | 23 |
| 2017 | 31 |
| 2018 | 38 |
| 2019 | 40 |
| 2020 | 33 |
| 2021 | 51 |
| 2022 | 48 |
| 2023 | 57 |
| 2024 | 48 |
| 2025 | 86 |
| 2026 | 93 |
