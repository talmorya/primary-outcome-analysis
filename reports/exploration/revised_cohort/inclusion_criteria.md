# Revised cohort inclusion criteria (review)

## Master pool

- CT.gov: `INTERVENTIONAL` + `BEHAVIORAL` intervention filter
- Conditions: chronic back pain, fibromyalgia, migraine + 22 curated primary-headache studies
- **696 studies** before hard filters (`exclusion_audit.csv` retains all)

## Hard inclusion (eligible cohort)

A study is **`cohort_included = True`** only if it passes all three stages:

### 1. Condition eligibility

- **Include:** `condition_eligibility` ∈ {`eligible`, `borderline`}
- **Exclude:** post-traumatic/TBI, cancer, surgical/postoperative, secondary pain, MS/CIS, acute-only LBP, headache-specific exclusions (MOH, cervicogenic, etc.)

### 2. Intervention eligibility

- **Include:** ≥1 treatment-oriented behavioral arm classified into an intervention category
- **Exclude:** no behavioral arm, control/sham-only behavioral arms, mechanism/lab arms only
- **Categories:** `psychological_therapy`, `mind_body`, `pain_education_self_management`, `physical_activity_exercise`, `lifestyle_behavioral`, `complementary_integrative`, `multidisciplinary_program`, `digital_behavioral`, `other_behavioral_treatment`
- **Multimodal flag:** `is_multimodal` = behavioral treatment + drug/device/procedure co-intervention (trial still eligible)

### 3. Treatment vs mechanism (outcome-based)

- **Exclude** only when **all** registered outcomes (primary + secondary + other) are mechanistic/experimental **and** there is **no** clinical/treatment-relevant outcome anywhere among them (`mechanism_only_outcomes`)
- **Population excludes:** visual snow syndrome, vestibular schwannoma; ME/CFS/long COVID/POTS as lead population when target conditions are only incidentally co-listed (`off_target_primary_population`)
- **Do not exclude** merely because all **primary** outcomes are mechanistic — if any secondary/other outcome is clinical (pain, disability, headache days, mood, etc.), the study remains eligible
- **Exclude:** mechanism/lab arms only at intervention stage (unchanged)
- **Flag (included studies):** `primary_outcome_mechanistic` = TRUE when all registered primary outcomes are mechanistic and none are clinical

## Study-level columns

| Column | Use |
|---|---|
| `cohort_included` | Final inclusion flag |
| `exclusion_stage` | `condition` / `intervention` / `mechanism` / empty |
| `exclusion_reason` | Rule ID |
| `intervention_categories` | Pipe-joined category tags |
| `is_multimodal` | Behavioral + non-behavioral modality |
| `eligible_*` | Condition flags |
| `primary_outcome_mechanistic` | TRUE if all primary outcomes mechanistic (for later stratification) |
| `has_clinical_outcome_anywhere` | TRUE if any registered outcome matches clinical/treatment lexicon |

## Outcome columns

| Column | Values |
|---|---|
| `outcome_category` | `pain_recovery`, `pain_interference`, `mood`, `feasibility_acceptability`, `other` |
| `outcome_subcategory` | e.g. `pain_intensity`, `disability`, `anxiety`, `feasibility_recruitment` |

Outcomes are classified for all studies; filter `cohort_included == True` for the analytic cohort.

## Dropped from previous version

- `rq_eligible` / `rq_borderline` / `rq_exclude`
- `non_psychological_behavioral_*` flags
- `behavioral_component` (replaced by `intervention_categories`)
