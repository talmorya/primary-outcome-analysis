# Headache condition exploration report

**Date:** 2026-08-26  
**Status:** Exploration only — no changes to cohort, taxonomy, or extraction pipeline.

## Purpose

Evaluate adding **headache** as a fourth research condition alongside chronic back pain, fibromyalgia, and migraine. Target population: **chronic/recurring primary headache disorders** where headache is the primary pain condition—not secondary or symptomatic headache.

---

## 1. API retrieval

### Query (same cohort filters as current pipeline)

```
query.cond = headache
filter.advanced = AREA[StudyType]INTERVENTIONAL AND AREA[InterventionType]BEHAVIORAL
```

| Metric | Value |
|---|---:|
| API `totalCount` | **214** |
| Records retrieved | 214 |
| Comparison: migraine query (full run) | 153 API → 151 in cohort |
| Comparison: current full cohort | 674 studies |

Raw API payload saved to `reports/exploration/headache_candidates_raw.json` (not added to `data/raw/full/`).

**Note:** CT.gov API v2 study records provide `conditions` and `keywords` in `conditionsModule`; **MeSH terms are not available** in the fields returned by this endpoint. Classification below uses conditions, keywords, titles, and intervention names only.

---

## 2. What `query.cond=headache` retrieves

### Overlap with existing cohort

| Group | Count |
|---|---:|
| Total headache API candidates | 214 |
| Already in full cohort (`full_20260823_201251`) | **143** (67%) |
| — of which migraine-matched | **143** (100% of overlap) |
| — of which via back pain / fibromyalgia | 0 |
| **Net new** (not in current 674) | **71** |

**Migraine cohort vs headache query:** 151 studies in the current migraine subset; **143** appear in the headache API results; **8 migraine studies are not returned** by `query.cond=headache`:

| NCT ID | Condition (registered) | Why missed by headache query |
|---|---|---|
| NCT03979677 | Vestibular Migraine | Condition text is "Vestibular Migraine" — indexed under migraine, not generic headache |
| NCT05914207 | Vestibular Migraine | Same |
| NCT05979337 | Chronic Migraine | Same |
| NCT06417684 | Vestibular Migraine | Same |
| NCT07469748 | Vestibular Migraine | Same |
| NCT07493005 | Vestibular Migraine | Same |
| NCT07661888 | Episodic Migraine | Same |
| NCT07691164 | Chronic Migraine | Same |

These 8 are **already captured** by the existing `migraine` condition query and local `migraine` pattern. Adding a headache target should **not duplicate** them if migraine patterns remain in place.

### Breakdown by proposed headache classification (all 214)

| Classification | All | Net new |
|---|---:|---:|
| migraine | 126 | 1 |
| headache associated with other condition | 25 | 12 |
| secondary headache | 17 | 17 |
| tension-type headache | 9 | 9 |
| medication-related headache (MOH) | 8 | 4 |
| headache unspecified | 8 | 8 |
| headache as symptom (non-headache primary) | 7 | 7 |
| chronic daily headache | 7 | 7 |
| other primary headache disorder | 3 | 3 |
| postoperative/procedural headache | 2 | 2 |
| cluster headache / TAC | 2 | 1 |

### Most common registered condition strings

| Count | Condition |
|---:|---|
| 77 | Migraine |
| 36 | Headache |
| 25 | Migraine Disorders |
| 16 | Chronic Pain |
| 12 | Headache Disorders |
| 12 | Chronic Migraine |
| 7 | Tension-Type Headache |
| 7 | Post-Traumatic Headache |
| 5 | Chronic Headache |
| 5 | Tension Type Headache |

**Takeaway:** The headache query is **heavily dominated by migraine** (≈59% of candidates). Non-migraine primary headache types are a **small minority** (~25–30 studies would be candidates for inclusion under strict rules).

### Headache in keywords only

6 studies have "headache" in keywords but not in the primary `conditions` list — fragile for condition-based filtering; titles/descriptions may be needed as secondary signals.

---

## 3. QC table

Full per-study table: **`reports/exploration/headache_candidates_qc.csv`**

Columns: `nct_id`, `conditions`, `keywords`, `brief_title`, `official_title`, `intervention_names`, `behavioral_component` (from existing cohort if present), `proposed_headache_classification`, `classification_confidence`, `classification_reason`, `in_existing_cohort`, `in_migraine_cohort`, `proposed_eligibility`.

---

## 4. Representative examples by category

### Proposed include — primary headache (net new)

| NCT ID | Conditions | Title (abbrev.) | Type |
|---|---|---|---|
| NCT01155557 | Tension-Type Headache | Strength-training for TTH in office workers | tension-type |
| NCT07240532 | Tension-Type Headache; Chronic Tension-type Headache | Multimodal physiotherapy + app for TTH | tension-type |
| NCT02460003 | Cluster Headache | Physiotherapy program for cluster headache | cluster/TAC |
| NCT01664585 | Headache; Physical Activity; Quality of Life | Exercise + active lifestyle to reduce headache | chronic daily / generic chronic |
| NCT01213056 | Headache; Pain | Mindfulness-based CBT for chronic headache | chronic daily |
| NCT01754571 | Medication Overuse Headache | CBT for MOH | medication-related (ICHD primary) |
| NCT06822673 | Primary Headache; Psychological Distress | MBI in children with primary headache | other primary |
| NCT06041997 | Headache Disorders | Smartphone restriction for primary headache | other primary |

### Proposed exclude — secondary / symptomatic

| NCT ID | Conditions | Why exclude |
|---|---|---|
| NCT02145117 | Post Traumatic Headache | Secondary headache (post-TBI) |
| NCT05414708 | PTSD; Post-Traumatic Headache | Headache secondary to trauma/PTSD context |
| NCT06073886 | Post-Concussion Syndrome; Headache; TBI | Concussion syndrome, not primary headache disorder |
| NCT07708701 | Postdural Puncture Headache (PDPH) | Procedural secondary headache |
| NCT04393909 | Delirium; Back Pain; …; Headache | Inpatient safety study; headache is one of many symptoms |
| NCT04043962 | Chronic Pain; Central Sensitisation; Headache | Adolescent chronic pain program; headache is comorbid |
| NCT05056571 | Occupational Stress | Nurse stress study; headache not primary condition |

### Borderline — manual review recommended

| NCT ID | Issue |
|---|---|
| NCT02908984, NCT07354776 | **Cervicogenic headache** — treated clinically as headache but ICHD-3 classifies as secondary (neck disorder). Include only if neck-source headaches are in scope. |
| NCT05689944 | Tension-Type Headache listed with **CRPS** and chronic pain — mixed primary pain condition |
| NCT00267618 | Pediatric recurrent headache **and abdominal pain** — functional pain overlap |
| NCT00457496 | Headache Disorders + neck + shoulder pain — musculoskeletal comorbidity |
| NCT02475005 | Pain; Headache — generic adolescent headache self-management |
| NCT01182051 | Pediatric; Headache; Anxiety — no "migraine" in conditions but classified as migraine in exploration (pediatric chronic headache, likely migraine spectrum) |
| NCT07425093 | Obesity; Headache — metabolic comorbidity, unclear primary focus |
| NCT02768233 | Secondary Headache Disorders; Medication-overuse Headache — MOH is primary target but "secondary" in condition label |

---

## 5. Proposed filtering rules for `condition_patterns.yaml`

### Design principles

1. **Keep `migraine` as a separate target** — do not broaden migraine patterns into a generic headache bucket; use headache target for *non-migraine* primary headache only.
2. **Require primary headache disorder signals** — named subtype or explicit primary-headache wording.
3. **Exclude secondary, procedural, and trauma-related headache** explicitly.
4. **Exclude studies where headache is one of many non-headache conditions** (symptom/comorbidity).
5. **Apply local validation post-API** (same as current pipeline) — API `query.cond=headache` is intentionally broad; YAML rules narrow the cohort.
6. **Deduplicate at merge** — studies matching both `migraine` and `primary_headache` should retain both tags or migraine only (recommend: assign `migraine` when migraine pattern matches; use `primary_headache` only for non-migraine matches).

### Proposed new target (draft — not implemented)

```yaml
  primary_headache:
    label: "Primary headache (non-migraine)"
    patterns:
      # Named primary subtypes
      - "tension[- ]?type"
      - "tension headache"
      - "\\btth\\b"
      - "cluster headache"
      - "trigeminal autonomic"
      - "hemicrania continua"
      - "paroxysmal hemicrania"
      - "\\bsunct\\b"
      - "\\bsuna\\b"
      - "chronic daily headache"
      - "\\bcdh\\b"
      - "new daily persistent"
      - "\\bndph\\b"
      - "medication[- ]?overuse headache"
      - "medication overuse headache"
      - "primary headache"
      - "headache disorder"
      - "chronic headache"
      - "episodic headache"
      - "recurrent headache"
      - "pediatric headache"
      - "headache in children"
      - "headache in adolescent"
    exclude:
      # Secondary / trauma / procedural
      - "post[- ]?traumatic"
      - "posttraumatic"
      - "post[- ]?concuss"
      - "post[- ]?dural"
      - "postdural"
      - "postoperative"
      - "secondary headache"
      - "brain injur"
      - "\\btbi\\b"
      - "concussion"
      - "\\bptsd\\b"
      - "intracranial hypertension"
      - "pseudotumor"
      # Non-headache primary conditions (headache as symptom)
      - "head and neck carcinoma"
      - "delirium"
      - "occupational stress"
      # Already covered by migraine target
      - "migraine"
      - "vestibular migraine"
```

### Optional borderline patterns (decide before implementation)

| Pattern | Recommendation |
|---|---|
| `cervicogenic headache` | **Exclude** if strict ICHD primary-only; **include** if clinical headache-population definition |
| Generic `^headache$` alone | **Include only** when headache is the sole or dominant condition (≤2 conditions, no chronic pain / CRPS / obesity primary) |
| `medication[- ]?overuse` | **Include** — MOH is an ICHD-3 primary headache disorder |
| `vestibular migraine` | **Keep under `migraine`** — already matched by existing pattern |

### Simulated impact of draft rules (on 214 API candidates)

| Outcome | Count |
|---|---:|
| Would match `primary_headache` (non-migraine) | **25** |
| Already in current 674 cohort | 0 (all 25 are net new) |
| Excluded as migraine (handled separately) | 143 |
| Excluded by secondary/trauma/symptom rules | ~30 |
| No match / manual review | ~16 |

**Estimated cohort expansion:** **+25 studies** (+3.7% over current 674), almost entirely tension-type, chronic/daily headache, cluster, and MOH trials.

---

## 6. Duplicate prevention strategy

When adding headache to a future full extraction:

1. Run four condition API queries: `chronic back pain`, `fibromyalgia`, `migraine`, `headache`.
2. Deduplicate by `nct_id` (same as current pipeline).
3. Apply local `condition_patterns.yaml` validation — study must match **at least one** target.
4. For `condition_matched`, allow multiple tags (e.g. `migraine | primary_headache` is unlikely; `migraine` alone suffices).
5. **Do not double-count** in analysis — migraine studies returned by both queries appear once in `studies.csv`.

---

## 7. Recommendations

### Proceed with headache as fourth condition?

**Yes, with a narrow `primary_headache` target** — but expect a **modest yield** (~25 net new studies). The headache API query is useful for discovery but **not sufficient alone**; local exclusion rules are essential.

### Priority subtypes aligned with research goals

| Include | Rationale |
|---|---|
| Tension-type headache (chronic/episodic) | Core primary headache; clear chronic pain relevance |
| Chronic daily headache / chronic headache | Recurring primary pain condition |
| Cluster headache / TAC | Primary headache disorder, distinct biology |
| Medication-overuse headache | ICHD primary category; behavioral relevance |
| Primary headache (explicit label) | When condition clearly states primary |

| Exclude | Rationale |
|---|---|
| Post-traumatic / post-concussion headache | Secondary to injury |
| Post-dural / postoperative headache | Procedural secondary |
| Headache with TBI / PTSD / cancer as co-primary | Headache not the primary pain condition of interest |
| Headache as one item in long comorbidity lists | Symptom, not primary condition |
| Cervicogenic headache | ICHD secondary — decide explicitly |

### Before full extraction

- [ ] Decide on **cervicogenic headache** (include vs exclude)
- [ ] Decide on **generic "Headache"** rule (strict sole-condition vs permissive)
- [ ] Decide on **MOH** when condition also says "Secondary Headache Disorders"
- [ ] Confirm **vestibular migraine** stays under migraine only (no change needed)
- [ ] Review 8 borderline studies in QC table (`proposed_eligibility = proposed_borderline`)

---

## Files produced (exploration only)

| File | Description |
|---|---|
| `reports/exploration/headache_candidates_raw.json` | 214 API study records |
| `reports/exploration/headache_candidates_qc.csv` | Per-study classification QC table |
| `reports/exploration/headache_exploration_report.md` | This report |

No changes to `data/processed/`, `config/condition_patterns.yaml`, or pipeline code.
