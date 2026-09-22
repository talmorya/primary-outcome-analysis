# Cohort inclusion rules (proposed — for promotion to production)

**Version:** 2026-09-08 (post QC)  
**Status:** Review artifact. Apply via `condition_patterns_proposed.yaml`, `intervention_taxonomy.yaml`, `condition_eligibility.py`, `rq_eligibility.py`, and headache expansion list in `build_proposed_cohort.py`. Does **not** yet modify `data/processed/full/`.

---

## 1. Master cohort (retrieval)

**ClinicalTrials.gov API filters (unchanged):**

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND condition ∈ {chronic back pain, fibromyalgia, migraine, primary headache (proposed 4th query)}
```

**Master cohort composition:**

| Source | Rule |
|---|---|
| Existing extraction | All studies from full run `full_20260823_201251` (674 studies) |
| Headache expansion | Add 22 net-new primary-headache studies from headache API exploration |
| Headache deduplication | One row per `nct_id`; migraine and primary headache are separate flags |
| Explicit headache exclusion | **NCT05689944** — TTH keyword only; enrollment is generic chronic adolescent pain (not TTH-specific) |

**All trial statuses retained.** Exercise-only, lab-paradigm, and research-mechanism trials stay in the master cohort; downstream layers classify them.

---

## 2. Condition eligibility layer

**Purpose:** Is the study about a target chronic pain disorder we care about, without being clearly secondary/post-traumatic/surgical?

**Config:** `config/condition_patterns_proposed.yaml`  
**Logic:** `src/ctgov_pipeline/condition_eligibility.py`

### 2.1 Target conditions (four flags)

| Flag | Target key | Notes |
|---|---|---|
| `eligible_migraine` | `migraine` | Includes chronic migraine, vestibular migraine |
| `eligible_chronic_back_pain` | `chronic_back_pain` | CLBP, non-specific LBP, LBP |
| `eligible_fibromyalgia` | `fibromyalgia` | FM |
| `eligible_headache` | `primary_headache` | Non-migraine primary headache expansion (TTH, cluster, CDH, NDPH, etc.) |

A study may match **multiple** targets. Migraine-tagged studies are **not** counted in `eligible_headache`.

### 2.2 Condition eligibility status

| Status | Meaning |
|---|---|
| `eligible` | ≥1 target matched; no exclusion rule fired |
| `borderline` | Target matched but inflammatory/comorbid context flagged for manual review |
| `excluded` | Exclusion rule fired or no target matched |

### 2.3 Global exclusion rules (all targets)

Apply to study text (conditions + keywords + titles). Global excludes fire **even when no target pattern matched** (e.g. post-concussive headache only).

| Rule ID | Exclude when |
|---|---|
| `post_traumatic` | Post-traumatic headache/pain, post-concussive headache, persistent post-traumatic pain |
| `tbi_concussion` | TBI, concussion, mild TBI, post-concussion syndrome |
| `cancer_oncology` | Cancer, carcinoma, oncology, malignancy (not "non-cancer") |
| `surgical_postoperative` | Disc prosthesis, spinal fusion, postoperative/post-surgical pain, failed back surgery, post-dural puncture headache |
| `secondary_pain` | Secondary headache/pain, cervicogenic headache, pain due to malignancy |
| `pathology_other` | MS/CIS, intracranial hypertension, meningitis, etc. |
| `acute_lbp_only` | Acute LBP only (chronic_back_pain target only; skip if "chronic" also present) |
| `no_target_match` | No target condition matched |

### 2.4 Headache-specific exclusions (`primary_headache` only)

| Rule ID | Exclude when |
|---|---|
| `headache_moh` | Medication-overuse headache, rebound headache |
| `headache_cervicogenic` | Cervicogenic headache |
| `headache_symptom_not_target` | Delirium, diagnostic error, opioid prescribing, occupational stress, etc. |
| `headache_migraine_only_or_removed` | Migraine co-listed; primary_headache flag removed |

Also remove `primary_headache` when migraine appears in study text.

### 2.5 Condition borderline rules

| Rule ID | Target | Flag when |
|---|---|---|
| `fibromyalgia_inflammatory` | fibromyalgia | Lupus/SLE co-listed (exclude if condition is exactly `arthritis` only) |

**Manual headache decisions (condition-eligible):**

| NCT ID | Decision |
|---|---|
| NCT00267618 | Include (pediatric recurrent headache + abdominal pain comorbidity) |
| NCT03308630 | Include (headache + stress + MSK pain comorbidity) |
| NCT05689944 | Exclude (not in cohort) |

---

## 3. Research-question (RQ) eligibility layer

**Purpose:** Does the study test a **psychological/behavioral treatment** relevant to our RQ (registered primary outcomes of psych/behavioral interventions for chronic pain)?

**Logic:** `src/ctgov_pipeline/rq_eligibility.py`  
**Intervention taxonomy:** `config/intervention_taxonomy.yaml`

### 3.1 RQ status

| Status | Meaning |
|---|---|
| `rq_eligible` | Condition eligible/borderline **and** identifiable psych `behavioral_component` |
| `rq_borderline` | Psych component ambiguous or catch-all classification only |
| `rq_exclude` | No psych component, condition excluded, lab paradigm, or non-psych behavioral only |

### 3.2 RQ analysis subset (primary analytic cohort)

```
condition_eligibility ∈ {eligible, borderline}
AND rq_eligibility = rq_eligible
```

Deduplicated by `nct_id` (one row per study regardless of multi-condition flags).

### 3.3 Intervention classification principles

**Psychological approaches** (`behavioral_component`): CBT, ACT, mindfulness/MBSR, pain education, PRT, exposure therapy, digital psych apps, etc. — see `approaches` in `intervention_taxonomy.yaml`.

**Non-psychological behavioral** (`non_psychological_behavioral_*`): Exercise, diet, lifestyle, **research paradigms**. Flagged per CT.gov BEHAVIORAL arm; does not remove from master cohort.

**`other_psychological` — two paths:**

| Path | Rule tag | RQ treatment |
|---|---|---|
| **Explicit match** | `APP_OTHER_PSYCHOLOGICAL` (patterns: emotional regulation, PbRE, emotional word exposure) | `rq_eligible` |
| **Catch-all fallback** | `APP_OTHER_PSYCH` (no taxonomy match on any arm) | `rq_borderline` |

### 3.4 RQ exclusion reasons (automatic)

| Condition | RQ result | Reason |
|---|---|---|
| Condition `excluded` | `rq_exclude` | Condition eligibility excluded |
| `research_paradigm` non-psych, no psych component | `rq_exclude` | Research paradigm / lab task |
| Non-psych behavioral only (exercise, diet, lifestyle) | `rq_exclude` | Non-psychological behavioral only |
| No `behavioral_component` at all | `rq_exclude` | No identifiable psychological behavioral_component |
| Catch-all `other_psychological` only | `rq_borderline` | Catch-all other_psychological classification only |
| Psych + prominent non-psych modality (exercise, yoga, diet in title) | `rq_borderline` | Multimodal trial with psych component plus prominent non-psych modality |

### 3.5 Research paradigm (`research_paradigm`)

**Keep RQ-excluded** when the registered BEHAVIORAL arm is a lab/experimental probe:

- Psychophysical tasks, experimental heat pain, QST
- EEG/fMRI paradigms, PASAT, affective touch, thermal/pressure stimuli
- Nocebo/cover-story methodology studies
- Cognitive assessment batteries (MoCA, MMSE mapping)

**Pattern refinements (QC 2026-09-08):**

| Pattern context | Treatment |
|---|---|
| `word reading task` + emotional regulation / PbRE / emotional words | **Not** research_paradigm → classify as `other_psychological` |
| Light exposure/deprivation for **multi-day treatment** (`consecutive days`, `administered for one hour`) | **Not** research_paradigm → `lifestyle_general` (non-psych behavioral) |

**QC-corrected examples:**

| NCT ID | Correction |
|---|---|
| NCT04084873 | `other_psychological` → **rq_eligible** (PbRE emotional regulation app) |
| NCT05369910 | `lifestyle_general` → **rq_exclude** (light habituation treatment, not psych) |

### 3.6 Manual RQ overrides

Hard-coded in `RQ_OVERRIDES` (`rq_eligibility.py`):

| NCT ID | RQ status | Reason |
|---|---|---|
| NCT01664585 | `rq_exclude` | Exercise-only |
| NCT00181064 | `rq_exclude` | Diet-only (Modified Atkins) |
| NCT00267618 | `rq_exclude` | Primary outcomes psychiatric (KSADS) |
| NCT03308630 | `rq_exclude` | Primary outcome is stress, not headache |
| NCT03166358 | `rq_borderline` | Yoga-only |
| NCT06631222 | `rq_borderline` | CBT present; primary outcome is algometry |
| NCT06041997 | `rq_borderline` | Smartphone restriction; other_psychological only |

---

## 4. Proposed cohort outputs (review)

| Artifact | Path |
|---|---|
| Classified study table | `reports/exploration/proposed_cohort/proposed_studies.csv` |
| QC summary | `reports/exploration/proposed_cohort/proposed_cohort_qc_report.md` |
| This rules document | `reports/exploration/proposed_cohort/cohort_inclusion_rules.md` |

**Regenerate:**

```bash
source .venv/bin/activate
PYTHONPATH=src python -m ctgov_pipeline.build_proposed_cohort
```

The builder re-applies `intervention_taxonomy.yaml` from `interventions_raw` on each run (does not read stale production classification columns).

---

## 5. Promotion checklist (when approved)

1. Merge `condition_patterns_proposed.yaml` → `condition_patterns.yaml` (add `primary_headache` + exclusion/borderline rules).
2. Re-run full extraction or condition re-match on raw JSON.
3. Run `reprocess_interventions` on production run (taxonomy already updated).
4. Integrate `condition_eligibility.py` + `rq_eligibility.py` into main pipeline / `studies.csv` columns.
5. Add headache API query to `run_full.py`.
6. Run unit tests: `tests/test_condition_eligibility.py`, `tests/test_intervention_classification.py`.

---

## 6. Current proposed counts (2026-09-08, post research-paradigm QC)

| Metric | Count |
|---|---:|
| Master proposed cohort | 696 |
| Condition-eligible | 677 |
| Condition-borderline | 2 |
| Condition-excluded | 17 |
| RQ-eligible | 375 |
| RQ-borderline | 96 |
| RQ-excluded | 225 |
| **RQ analysis subset** | **375** |
| `research_paradigm` studies | 15 |

**Change from prior proposed run:** +2 RQ-eligible (NCT04084873 PbRE correction; NCT06912971 emotional-regulation training now matches explicit `other_psychological`).
