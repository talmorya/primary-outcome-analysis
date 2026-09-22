# Condition eligibility & research-question QC report

**Date:** 2026-08-31  
**Status:** Inspection only — no cohort changes, re-fetch, or merge.

**Research question reminder:** Among **psychological/behavioral** interventions for **chronic pain**, what primary outcomes do researchers register? Condition eligibility must identify **primary/chronic pain** populations; RQ fit additionally requires a **psychological/behavioral intervention** (not exercise/diet/lab paradigm alone) and **headache/pain-relevant primary outcomes**.

---

## Part A — Final headache cohort (22 studies)

### NCT05689944 — TTH clarification → **exclude**

| Field | Detail |
|---|---|
| Title | Dance-therapy and Chronic Pain |
| Registered conditions | Chronic Pain; Complex Regional Pain Syndromes; **Tension-Type Headache** |
| **Enrollment criterion** | “Patients aged 12–20 with **chronic pain**” diagnosed in a Pain Management Center — **not** TTH-specific |
| Intervention | Dance-therapy / art-therapy / yoga for **chronic adolescent pain** |

**Conclusion:** TTH appears as a **registry tag/keyword**, not an enrollment or target condition. The study enrolls generic chronic pain adolescents (including CRPS). Per your rule, **exclude** from the headache expansion.

**Adjusted count:** 20 definite includes + 2 comorbid borderline (`NCT00267618`, `NCT03308630`) − 1 (`NCT05689944`) = **22 headache studies** (not 23).

---

### Headache RQ inspection (22 studies)

#### Clearly fit condition + RQ (17)

Psych/behavioral component identified; chronic/recurring headache; primary outcomes target headache/pain/function.

| NCT ID | Headache type | Intervention (psych/behavioral) | Primary outcome sample |
|---|---|---|---|
| NCT01213056 | Chronic headache | MBCT | Headache diary |
| NCT07240532 | TTH | Multimodal PT + guided meditation app | Headache pain intensity |
| NCT01525303 | Chronic headache | Behavioral headache program + exercise | Headache-free days |
| NCT00457496 | Primary headache + neck/shoulder | CBT + relaxation + exercise | Headache/neck/shoulder frequency |
| NCT06631222 | TTH | CBT + psychoeducation | Algometry (pain sensitivity) |
| NCT02264340 | TTH | Autogenic training + exercises | Headache frequency |
| NCT00897780 | Chronic headache | Biofeedback + VR | Headache frequency/severity |
| NCT04867967 | TTH | MBSR (+ yoga comparator) | Headache frequency |
| NCT06822673 | Primary headache | Mindfulness-based intervention | HRQoL; pediatric headaches |
| NCT00956969 | Chronic headaches | Stress management / relaxation | Headache frequency/severity |
| NCT01347684 | TTH | Behavioral therapy + psychoeducation | Headache intensity |
| NCT01488825 | Episodic TTH | Yoga therapy (classified with meditation/relaxation) | Headache frequency |
| NCT00389038 | Pediatric chronic headache | Coping skills + psychoeducation | Headache diary frequency |
| NCT02475005 | Headache (adolescent) | Pain self-management app | Headache intensity; pain coping |
| NCT01155557 | TTH | Lifestyle counseling + strength training | Headache |
| NCT06041997 | Primary headache | Smartphone restriction (behavioral) | Abortive treatment burden (headache-related) |
| NCT02460003 | Cluster headache | Physiotherapy + pain education | Pain VAS |

#### RQ borderline — condition OK, review before merge (2)

| NCT ID | Issue | Recommendation |
|---|---|---|
| NCT03166358 | Yoga-only (Hatha yoga); no psych taxonomy tag; yoga as physical activity | **Borderline** — include only if mind-body yoga trials are in scope |
| NCT06631222 | Multimodal manual therapy + CBT; primary outcome is pressure algometry not headache diary | **Borderline** — psych component present but outcome is mechanistic |

*(NCT06631222 also listed above in clear fit — flag for outcome relevance review.)*

#### Should exclude from RQ — headache-eligible but wrong intervention/outcome focus (5)

| NCT ID | Why exclude from RQ |
|---|---|
| NCT01664585 | **Exercise-only** (Walk With Ease–style training); no psych component |
| NCT00181064 | **Diet-only** (Modified Atkins); dietary intervention, not psych/behavioral |
| NCT00267618 | Family help program; **primary outcomes are psychiatric diagnosis (KSADS)**, not headache; dual headache+abdominal pain |
| NCT03308630 | Yoga/mantra for stress; **primary outcome = self-reported stress**, not headache |
| NCT05689944 | *(Excluded from headache cohort)* — chronic pain/CRPS, not headache target |

**Net headache expansion for RQ-aligned analysis:** **17 clear** (+ up to 2–4 borderline if accepted) ≈ **17–21 studies**, not all 22.

---

## Part B — Existing cohort condition QC

Applied shared **secondary/non-primary pain exclusion patterns** to all studies matching each condition in `condition_matched`, plus condition-specific borderline rules. Full per-study tables: `reports/exploration/cohort_qc_{migraine,chronic_back_pain,fibromyalgia}.csv`.

### Shared exclusion patterns tested

| Rule ID | Pattern intent |
|---|---|
| `exclude_post_traumatic` | Post-traumatic headache/pain, post-concussion |
| `exclude_tbi_concussion` | TBI, concussion as primary context |
| `exclude_cancer_oncology` | Cancer/oncology primary (with non-cancer guard) |
| `exclude_surgical_postop` | Surgical/disc prosthesis/spinal fusion/postoperative pain focus |
| `exclude_secondary_pain` | Secondary headache/pain, cervicogenic |
| `exclude_acute_only` | Acute low back pain without chronic designation |

### `borderline_rq` flag (separate from condition eligibility)

Studies with **no identified psychological `behavioral_component`** and only exercise/diet/lab content (`non_psychological_behavioral_flag=True`). These **pass condition filters** but may fall outside the **psych/behavioral intervention** research question. Counts:

| Condition | Include (condition) | Exclude (secondary) | Borderline (condition) | Borderline RQ (no psych tag) |
|---|---:|---:|---:|---:|
| **Migraine** | 107 | 3 | 0 | 41 |
| **Chronic back pain** | 208 | 12–16 | 0 | 88 |
| **Fibromyalgia** | 148 | 2 | 10 | 63 |

---

## Part C — Migraine (n = 151)

### Clearly fit (107)

Migraine/chronic migraine as registered condition; no secondary-pain exclusion triggered.

### Should exclude (3)

| NCT ID | Reason | Conditions (abbrev.) |
|---|---|---|
| NCT01599143 | Cancer primary context | Cancer \| Diabetes \| Hypertension \| … \| Migraine |
| NCT06098755 | TBI/concussion context | PTSD \| Migraine \| … (job stress, hyperthyroidism) |
| NCT02748174 | Post-concussive headache | Post Concussive Headache |

### Borderline / manual review (41 `borderline_rq`)

No condition-level borderline cases. **41 studies** have exercise-only, sleep hygiene, lab paradigms, or other **non-psych behavioral** interventions — e.g.:

- NCT07425964 — Sleep hygiene education (no psych component tag)
- NCT03768830 — Exercise for invisible symptoms
- NCT07328685 — Body awareness therapy (physical)

**Recommendation:** Keep in **condition cohort**; define **analysis subset** as studies with identifiable psych `behavioral_component` (same logic as README).

### Recommended migraine-specific rules

```yaml
# Keep existing migraine patterns; add excludes:
exclude:
  - "post[- ]?concuss"
  - "post concussive headache"
  - "traumatic brain injury"
  - "(?<!non[- ])(?<!non )cancer"   # when cancer listed as primary condition
```

**Note:** Vestibular migraine (8 studies not returned by `query.cond=headache`) already match `migraine` — no duplicate issue.

---

## Part D — Chronic back pain (n = 312)

### Clearly fit (208)

Chronic/low back pain as primary condition; no surgical/secondary/acute exclusion.

### Should exclude (12–16)

| NCT ID | Reason | Notes |
|---|---|---|
| NCT01599143 | Cancer context | Same multi-morbidity trial as migraine |
| NCT01704677 | Surgical comparison | Lumbar disc **prosthesis vs** multidisciplinary rehab |
| NCT00394732 | Surgical comparison | Disc prosthesis vs multidisciplinary rehab |
| NCT06027099 | Post-surgical/opioid taper | Chronic pain + back/neck; **postoperative opioid** focus |
| NCT07766824 | Post-spinal fusion | Fusion patients |
| NCT07576062 | Post-lumbar spine surgery | Failed back surgery syndrome |
| NCT04648683 | Postsurgical pain | Lumbar spine surgery population |
| NCT05698914 | Postsurgical pain | Lumbar spine surgery |
| NCT02674711 | Surgical context | Low back + opiate + neck; surgical arm |
| NCT04770480 | Surgery arm | Low back pain + surgery condition |
| NCT02647658 | Acute LBP | “Low Back Pain” without chronic designation |
| NCT03722394 | Acute LBP | Acute/chronic mixed label — review |

### Borderline / manual review (88 `borderline_rq`)

Exercise-only, yoga, psychophysical lab studies, device trials — condition OK, psych RQ unclear. Examples:

- NCT04280796 — Psychophysical lab paradigm (`research_paradigm`)
- NCT02552992 — Yoga for CLBP (exercise/yoga, no psych tag)

### Recommended back-pain rules

```yaml
chronic_back_pain:
  patterns: [existing]
  exclude:
    - "disc prosthesis|total disc replacement|lumbar disc prosthesis"
    - "spinal fusion"
    - "postoperative|postsurgical|after lumbar spine surgery|failed back surgery"
    - "post[- ]?traumatic"
    - "(?<!non[- ])(?<!non )cancer"
    - "\\bacute low back pain\\b"   # only when chronic not also present
```

**Open question:** Trials comparing **surgery vs behavioral rehab** (NCT01704677) — chronic CLBP population but **surgical primary comparison**. Recommend **exclude** per “pain secondary to surgery/procedure” logic.

---

## Part E — Fibromyalgia (n = 223)

### Clearly fit (148)

Fibromyalgia in conditions; no cancer/secondary exclusion.

### Should exclude (2)

| NCT ID | Reason |
|---|---|
| NCT01599143 | Cancer listed as primary condition |
| NCT05057676 | Multiple sclerosis / CIS primary with fibromyalgia secondary tag |

### Borderline — condition (10)

Flagged for **inflammatory/rheumatology comorbidity** in condition list. Several are **false positives** — e.g. NCT00526435 lists “Arthritis” as umbrella for a **Walk With Ease** trial that includes fibromyalgia arms:

| NCT ID | Issue | Recommendation |
|---|---|---|
| NCT05057676 | MS/CIS primary | **Exclude** (already above) |
| NCT06208514 | FM + systemic lupus | **Borderline** — confirm FM is enrollment target |
| NCT07282392 | Lupus + FM | **Borderline** |
| NCT00526435, NCT05289544, etc. | “Arthritis” umbrella + FM keyword | **Include** — FM is explicit arm; refine rule to avoid flagging generic “Arthritis” |

### Borderline RQ (63)

Exercise, yoga, reflexology, lab studies without psych component — same subsetting logic as migraine/back pain.

### Recommended fibromyalgia rules

```yaml
fibromyalgia:
  patterns: [existing]
  exclude:
    - "multiple sclerosis|clinically isolated syndrome"
    - "(?<!non[- ])(?<!non )cancer"
    - "systemic lupus erythematosus"   # only when SLE is primary listed condition before FM
  # Do NOT exclude on generic "arthritis" alone when fibromyalgia is co-listed
```

---

## Part F — Cross-condition findings

### Multi-condition trial appearing in all three QC exclude lists

**NCT01599143** — Mindfulness for chronic physical/mental health conditions; **Cancer** listed first. Matches migraine, back pain, and fibromyalgia via broad comorbidity. **Recommend exclude from all condition targets** when cancer is a registered condition.

### Two-layer filtering model (recommended)

| Layer | Question | Action |
|---|---|---|
| **1. Condition eligibility** | Is this a primary chronic pain disorder of interest? | YAML `condition_patterns` + secondary excludes |
| **2. RQ / analysis subset** | Is there a psych/behavioral intervention worth comparing? | Filter on `behavioral_component` not empty; exclude `research_paradigm`, exercise-only |
| **3. Outcome relevance** | Do registered primary outcomes address pain/function/psych constructs? | Manual/annotation pass (not automated yet) |

### Additional rules recommended before next extraction

1. **Headache:** Finalize at **22** (exclude NCT05689944); RQ subset ≈ **17** clear fits.
2. **Post-traumatic headache/pain:** Exclude across all conditions (already catches migraine NCT02748174).
3. **Surgical/postoperative CLBP:** Exclude disc prosthesis, fusion, postsurgical pain trials.
4. **Cancer as registered condition:** Exclude when cancer appears in `conditions` list (not “non-cancer pain” in title).
5. **Acute LBP:** Exclude when only acute label without chronic.
6. **Inflammatory comorbidity (FM):** Flag only when autoimmune disease is **primary** condition, not generic “Arthritis” umbrella.
7. **Do not conflate condition QC with psych subset:** 192 existing studies (41+88+63) are condition-valid but exercise/lab-only — retain in cohort, exclude from psych-intervention analysis.

---

## Output files

| File | Description |
|---|---|
| `reports/exploration/condition_eligibility_qc_report.md` | This report |
| `reports/exploration/headache_final22_rq_qc.csv` | 22 headache studies with RQ fit flags |
| `reports/exploration/cohort_qc_migraine.csv` | All 151 migraine-matched studies |
| `reports/exploration/cohort_qc_chronic_back_pain.csv` | All 312 CLBP-matched studies |
| `reports/exploration/cohort_qc_fibromyalgia.csv` | All 223 FM-matched studies |
