# Cohort filtering rules (condition stage)

**Version:** `simplified_v1` (`cohort_rules_version` in `studies.csv`)

**Config:** `config/condition_patterns_cohort.yaml`
**Code:** `condition_eligibility.py`, `acute_population_screen.py`, `eligibility_text.py`

Only the **condition stage** excludes studies. Interventions and primary outcomes are **descriptive only** (no exclusion).

---

## 1. API retrieval (master pool)

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND registered Conditions field contains any of (back pain, fibromyalgia, migraine, headache)
```

- All filters are combined with AND in one `filter.advanced` expression per term: `AREA[StudyType]INTERVENTIONAL AND AREA[InterventionType]BEHAVIORAL AND AREA[Condition]"<term>"`. `AREA[Condition]` searches the registered Conditions field only. (`query.cond` is not used: it also searches titles, keywords and MeSH terms, which pulled trials whose registered condition was unrelated.)
- One search per term, deduplicated by `nct_id`. Which search(es) returned a trial is recorded in `api_retrieval_queries`.
- CT.gov matches whole words with synonym expansion, so a few pulled trials do not contain a target as a substring in their conditions (e.g. `Myofascial Pain Syndrome` returned for fibromyalgia, `Low Back Ache` for back pain). The local condition stage excludes them as `no_target_match`.
- Raw JSON: `data/raw/full/<extraction_run_id>/studies/*.json` (keep one run).
- Master table: `data/processed/studies.csv` — **every** retrieved trial, with its include/exclude status.

---

## 2. What each excluded study records

| Column | Meaning |
|---|---|
| `cohort_inclusion_status` | `included` or `excluded` |
| `exclusion_reason` | **General reason**, one of two values: `acute` or `condition` (empty if included) |
| `exclusion_detail` | **Specific explanation**. Always starts with the rule key, then why this study hit it, e.g. `acute_pain: Acute / recent-onset pain population (found in eligibility_inclusion_1). Matched text: "…"` |

| `exclusion_reason` | Rule keys (start of `exclusion_detail`) |
|---|---|
| `acute` | `acute_pain`, `acute_and_chronic_in_inclusion` |
| `condition` | `no_target_match`, `cancer_oncology`, `pathology_other`, `pregnancy_related` |

Rules are checked in the order of `exclusion_rules` in the YAML (cancer, pathology, acute), then `no_target_match`. The **first** rule that fires is the one recorded.

---

## 3. Condition rules (`exclusion_reason = condition`)

### Target conditions (must match at least one)

Patterns in `condition_patterns_cohort.yaml` set these flags:

| Flag column | Target |
|---|---|
| `eligible_migraine` | migraine |
| `eligible_chronic_back_pain` | back pain |
| `eligible_fibromyalgia` | fibromyalgia |
| `eligible_headache` | headache (non-migraine) |

**Inclusion and flags** (`eligible_*`, `condition_matched`): a trial is included only if at least one target matches its **registered conditions**; keywords and titles never qualify it. Each condition line is pattern-matched as a substring (so `Pain, Head` → headache, `Pain, Back` → back pain, `Fybromyalgia` → fibromyalgia). A trial can have several flags (e.g. migraine and headache). Every included trial has at least one flag `True`.

There is no migraine/headache overlap rule: mentions of migraine in eligibility text never remove a headache trial.

**Duplicates:** records are de-duplicated by `nct_id` before any filtering, and the build fails if `nct_id` is not unique in `studies.csv`.

### Rules

| Rule key | When it applies |
|---|---|
| `no_target_match` | No target pattern matched the registered conditions. |
| `cancer_oncology` | Oncology pattern in conditions, keywords, brief title or official title (not eligibility boilerplate). Detail shows the matched word. |
| `pathology_other` | Non-pain primary pathology pattern (same text scope). Detail shows the matched word. |
| `pregnancy_related` | Pregnancy, postpartum, childbirth, menstrual or pelvic girdle pain wording in conditions, keywords or titles (same text scope; eligibility text is not searched). A different pain population. Detail shows the matched word. |

Registered comorbid or overlapping conditions (CNS, mood/psychological symptoms, chronic overlapping pain conditions, widespread pain, nociplastic risk factors) are **not** an exclusion rule; a trial with a target pain condition stays in however many other conditions it lists. They are kept in `raw_conditions`.

Descriptive only (never exclude): `condition_feature_flags` (post-traumatic, TBI, visual snow, …) and `review_flags` (currently `provider_or_system_level`: title mentions clinicians, guidelines, implementation, decision support, referral, health system, … so you can check whether the trial targets clinicians or care systems rather than patients; some hits are patient trials in a care-model setting).

---

## 4. Acute rules (`exclusion_reason = acute`)

Goal: exclude trials whose **enrolled population** is acute pain, or recent-onset (&lt;3 months) pain / recent surgery / recent injury. Do not exclude on educational, drug-related, or laboratory uses of the word "acute".

### Text used

| Used | Not used |
|---|---|
| Eligibility **inclusion** blocks (checked first) | Detailed description |
| Registered **conditions** (each line) | Keywords / MeSH-style terms |
| Official title, brief title, brief summary | Intervention names |

### Order

1. **Inclusion blocks** — acute population, recent surgery/injury in the past 3 months / 12 weeks, or acute **and** chronic population in the same block → exclude.
2. Inclusion requires a **chronic** population and the **exclusion** section lists acute/recent pain → pass.
3. **Conditions**, then **official title → brief title → brief summary** — skipped entirely when **every** registered condition contains the word `chronic`.

Every occurrence of "acute" in a text is checked (not just the first).

### Uses of "acute" that are *not* a population (ignored)

Only the specific occurrence is ignored; other acute wording in the same text still counts.

| Pattern | Example |
|---|---|
| Laboratory stimulus | "acute noxious physical stimuli" |
| Drug / treatment wording | "acute pain relief medications", "acute migraine attacks", "acute treatment" |
| Acute flare of a chronic condition | "acute pain episode of chronic low back pain" |
| Background contrast | "chronic versus acute PTHA" |
| Negation | "not due to acute trauma", "without acute pain" |

### Pass examples

- Acute only under **exclusion** criteria.
- `Chronic Pain` + `Acute Pain` co-listed when inclusion supports a chronic cohort.
- All conditions contain `chronic` (e.g. `Chronic Low Back Pain` only).

### Reference NCTs (manual QC, enforced by `tests/test_finalize_cohort.py`)

| NCT | Expected | Why |
|---|---|---|
| NCT03537573 | exclude | acute diagnosis in inclusion |
| NCT02647658 | exclude | acute LBP in inclusion (prevention study) |
| NCT04356963 | exclude | `Pain, Acute` in conditions |
| NCT00796536 | include (rule example) | "acute" only in detailed description (stimuli). Since the Conditions-field pull, no longer retrieved: its registered condition is only `Chronic Pain` |
| NCT01794988 | include (rule example) | "acute" only in keywords / MeSH. No longer retrieved (registered condition is only `Chronic Pain`) |
| NCT03483168 | include | educational "acute vs chronic" in summary; condition is chronic only |
| NCT04636177 | include | "not due to acute trauma" |
| NCT06971809 | include | chronic in inclusion, acute only in exclusion |
| NCT04984720 | include | "acute pain relief medications" is drug wording |
| NCT02419131 | include | "chronic versus acute PTHA" is background; trial enrolls chronic PTH |
| NCT03157544 | include | chronic neck/LBP patients during an acute flare (**judgment call**) |
| NCT06114264 | include | `Pain, Chronic` must not count as a non-target condition |

### Known limit (not implemented)

Peri-operative / ambiguous surgery-injury timing (e.g. "scheduled for lumbar surgery", "within 3 months of a head injury") is **not** screened: only ~7 included trials were affected and the decision was to leave them. Auto-exclusion fires only on explicit "past/last/previous 3 months / 12 weeks / 90 days" wording.

---

## 5. Intervention & outcomes (no filtering)

- **Interventions:** `intervention_categories` (from active arms), `is_multimodal`, `control_arm_types`; raw arm text in `raw_intervention_names` and `raw_intervention_details`.
- **Outcomes:** raw text preserved in `primary_outcomes.csv`; `outcome_category` / `outcome_subcategory` are descriptive.

See [DATA_COLUMNS.md](DATA_COLUMNS.md).
