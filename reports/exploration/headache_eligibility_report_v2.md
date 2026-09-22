# Headache eligibility report (v2 — sharpened rules)

**Date:** 2026-08-31  
**Status:** Exploration only — no changes to full cohort, taxonomy, or extraction.

**Source data:** `reports/exploration/headache_candidates_raw.json` (214 API records; unchanged).

---

## Scientific inclusion criterion applied

**Include:** Primary headache disorders constituting a chronic/recurring pain condition, where headache is the primary or co-target condition (not merely a symptom of another disease).

**Definitely include:** tension-type headache; chronic headache; chronic daily headache; generic “headache” when clearly primary/dominant; other clearly primary disorders (e.g. cluster headache).

**Potentially include:** Headache alongside another chronic pain condition (neck, shoulder, CRPS, etc.) when headache is a **named/target** condition — distinguishing comorbid chronic pain from secondary headache.

**Exclude:** Secondary headache (TBI, post-concussion, post-traumatic, procedural, cancer, pathology-driven); MOH; cervicogenic; migraine (existing cohort); headache as incidental symptom.

---

## Summary counts

| Group | n |
|---|---:|
| Total API candidates (`query.cond=headache`) | 214 |
| Excluded as **migraine** (existing cohort) | 145 |
| **Non-migraine headache pool** | **69** |
| → **Include** | **20** |
| → **Borderline** (manual review) | **5** |
| → **Exclude** (non-migraine) | **44** |

All 20 included studies are **net new** (not in current 674-study cohort). None overlap with existing migraine entries.

| Exclude reason (non-migraine) | n |
|---|---:|
| Post-traumatic / post-concussion headache | 16 |
| Headache not primary target / symptom | 11 |
| TBI / concussion context | 6 |
| Medication-overuse headache (MOH) | 4 |
| Cervicogenic headache | 2 |
| Procedural / post-dural | 2 |
| Other pathology (e.g. IIH, neurologic disease) | 2 |
| Cancer-related | 1 |

---

## Proposed eligibility labels

| Label | Meaning |
|---|---|
| `include` | Meets sharpened primary-headache criterion |
| `borderline_comorbid_pain` | Headache named but comorbid chronic pain may share focus — review title/intervention |
| `borderline_generic_headache` | Generic headache listed; target role uncertain |
| `borderline_unclear` | Headache mentioned; insufficient signal |
| `exclude_migraine` | Migraine — handled by existing cohort (not part of headache expansion) |
| `exclude_moh` | Medication-overuse headache |
| `exclude_post_traumatic` | Post-traumatic / post-concussion headache |
| `exclude_tbi` | Headache in TBI/concussion context |
| `exclude_procedural` | Post-dural / postoperative headache |
| `exclude_cancer` | Cancer/oncology context |
| `exclude_cervicogenic` | Cervicogenic headache |
| `exclude_secondary_labeled` | Explicitly labeled secondary headache |
| `exclude_pathology` | Headache attributed to another disease |
| `exclude_symptom_not_target` | Headache incidental or comorbid symptom, not target |
| `exclude_unclear` | Does not meet inclusion after exclusions |

---

## Include list (n = 20)

| NCT ID | Conditions | Brief title | Reason |
|---|---|---|---|
| NCT01155557 | Tension-Type Headache | Strength-training for TTH | Tension-type |
| NCT07240532 | Tension-Type Headache; Chronic Tension-type Headache | Multimodal physiotherapy + app for TTH | Tension-type |
| NCT06631222 | Tension Type Headache | CBT for TTH + smartphone addiction | Tension-type |
| NCT02264340 | Tension-Type Headache | Exercise and relaxation for TTH | Tension-type |
| NCT04867967 | Tension-Type Headache | Yoga and MBSR for TTH | Tension-type |
| NCT01347684 | Tension-type Headache | Two treatment strategies for TTH | Tension-type |
| NCT01488825 | Episodic Tension Type Headache | Yoga for episodic TTH | Tension-type |
| NCT03166358 | Headache | Yoga for pediatric TTH | Tension-type (pediatric) |
| NCT00181064 | Chronic Daily Headache | Atkins diet for difficult headaches (teens) | Chronic daily |
| NCT01664585 | Headache; Physical Activity; QoL | Exercise + active lifestyle for headache | Chronic headache |
| NCT01213056 | Headache; Pain | MBCT for chronic headache | Chronic headache |
| NCT01525303 | Chronic Headaches | Aerobic exercise within behavioral program | Chronic headache |
| NCT00897780 | Chronic Headache | Biofeedback + VR for chronic headache | Chronic headache |
| NCT00956969 | Headaches | Stress management for chronic headaches | Chronic headache |
| NCT00389038 | Headache | Pediatric chronic headache trial | Chronic headache (pediatric) |
| NCT02460003 | Cluster Headache | Physiotherapy for cluster headache | Cluster (primary) |
| NCT06041997 | Headache Disorders | Smartphone restriction for primary headache | Primary headache label |
| NCT06822673 | Primary Headache | MBI in children with primary headache | Primary headache label |
| NCT00457496 | Headache Disorders; Headache; Neck Pain; Shoulder Pain | CBT + exercise for headache, neck, shoulder pain | Primary headache + comorbid pain; **headache in title as target** |
| NCT02475005 | Pain; Headache | Adolescent headache self-management | Generic headache; **headache-focused title** |

---

## Borderline cases (n = 5) — manual review recommended

### `borderline_comorbid_pain` (3)

| NCT ID | Conditions | Why borderline | Recommendation |
|---|---|---|---|
| **NCT05689944** | Chronic Pain; CRPS; Tension-Type Headache | TTH listed but title is “Dance-therapy and **Chronic Pain**” — CRPS/chronic pain may be primary focus | **Lean exclude** unless protocol confirms TTH as enrolled population |
| **NCT00267618** | Pediatric Recurrent Headache & Abdominal Pain | Dual functional pain program (headache **and** abdominal pain equally named) | **Lean include** if headache arm is separable; otherwise treat as mixed functional pain — may fall outside headache-specific analysis |
| **NCT03308630** | Stress Related Disorder; Musculoskeletal Pain; Headache | Title lists headache as one of three targets alongside stress and MSK pain | **Lean include** if headache outcomes registered separately; comorbid multi-target study |

### `borderline_unclear` (2)

| NCT ID | Conditions | Why borderline | Recommendation |
|---|---|---|---|
| **NCT01808664** | Unnecessary Procedures; Low Back Pain; Osteoporosis; Headache; MRI; Primary Care | Headache appears in condition list but study is about reducing inappropriate imaging in primary care | **Exclude** — headache incidental to QI study |
| **NCT02247050** | Health Services Misuse; Physician Practice Patterns | “Choosing Wisely” primary-care intervention; headache not a patient population | **Exclude** — headache not the studied condition |

**Resolved from v1:** NCT00457496 moved from borderline to **include** because title explicitly targets headache alongside neck/shoulder pain (fits “potentially include” comorbid rule).

**Resolved from v1:** NCT04043962, NCT01974791 moved to **exclude_symptom_not_target** — adolescent chronic pain programs where headache is comorbid, not the intervention target.

---

## Representative excludes (non-migraine)

| Category | Example NCT | Conditions | Why excluded |
|---|---|---|---|
| MOH | NCT01754571 | Medication Overuse Headache | Explicit MOH exclusion per criterion |
| Post-traumatic | NCT02145117 | Post Traumatic Headache | Secondary to trauma |
| TBI | NCT01552473 | Traumatic Brain Injury | Headache secondary to injury |
| Procedural | NCT07708701 | Postdural Puncture Headache (PDPH) | Procedural secondary |
| Cervicogenic | NCT02908984 | Cervicogenic Headache | Explicit exclusion |
| Cancer | NCT05077072 | Head and Neck Carcinoma | Oncology context |
| Pathology | NCT01003639 | Idiopathic Intracranial Hypertension | Secondary to disease |
| Symptom not target | NCT04393909 | Delirium; Back Pain; …; Headache (30+ conditions) | Inpatient safety study |
| Symptom not target | NCT01316471 | Chronic Pain; Abdominal Pain; Headache | Adolescent chronic pain program |
| Symptom not target | NCT07425093 | Obesity; Headache; brain imaging | Obesity/neuroimaging study |
| Symptom not target | NCT03537573 | Acute Pain; Headache; Musculoskeletal Pain | Opioid prescribing in primary care |

---

## Recommended rule updates for `condition_patterns.yaml` (draft)

```yaml
  primary_headache:
    label: "Primary headache (non-migraine)"
    patterns:
      - "tension[- ]?type"
      - "tension headache"
      - "\\btth\\b"
      - "chronic daily headache"
      - "\\bcdh\\b"
      - "new daily persistent"
      - "chronic headache"
      - "cluster headache"
      - "trigeminal autonomic"
      - "primary headache"
      - "headache disorder"
      - "recurrent headache"
      - "pediatric headache"
    exclude:
      - "migraine"
      - "vestibular migraine"
      - "medication[- ]?overuse"
      - "medication overuse"
      - "post[- ]?traumatic"
      - "posttraumatic"
      - "post[- ]?concuss"
      - "post[- ]?dural"
      - "postdural"
      - "cervicogenic"
      - "secondary headache"
      - "brain injur"
      - "\\btbi\\b"
      - "concussion"
      - "(?<!non[- ])(?<!non )cancer"
      - "carcinoma"
      - "oncolog"
      - "intracranial hypertension"
```

### Additional implementation rules (not just patterns)

1. **Generic `headache` include gate:** Require headache in `brief_title` or `official_title`, OR ≤2 non-headache conditions in the conditions list.
2. **Comorbid chronic pain gate:** If `chronic pain`, `neck pain`, `CRPS`, etc. co-listed, require headache in title OR a named headache subtype in conditions.
3. **Adolescent chronic pain programs:** Exclude when conditions are `chronic pain + abdominal pain + headache` unless title/intervention explicitly targets headache.
4. **MOH:** Exclude even when labeled under “Secondary Headache Disorders” on CT.gov.
5. **Non-cancer guard:** Use negative lookbehind on `cancer` to avoid excluding “non-cancer pain” studies (fixed false positive on NCT03537573).
6. **Migraine dedup:** Studies matching `migraine` patterns stay under `migraine` target only; do not also assign `primary_headache`.

---

## Projected cohort impact

| Scenario | Studies added |
|---|---:|
| Include only (`proposed_eligibility = include`) | **+20** |
| Include + borderline_comorbid_pain (if all accepted) | **+23** |
| Include + all borderline (if all accepted) | **+25** |

Compared to current 674-study cohort: **+3.0% to +3.7%**.

---

## Output files

| File | Description |
|---|---|
| `reports/exploration/headache_candidates_qc_v2.csv` | All 214 candidates with v2 eligibility |
| `reports/exploration/headache_eligible_candidates_qc_v2.csv` | Non-migraine pool only (69 rows) |
| `reports/exploration/headache_eligibility_report_v2.md` | This report |

**QC table columns:** `nct_id`, `conditions`, `keywords`, `brief_title`, `official_title`, `intervention_names`, `behavioral_component`, `in_existing_cohort`, `proposed_eligibility`, `eligibility_confidence`, `eligibility_reason`.

(Migraine-specific classification columns from v1 removed.)
