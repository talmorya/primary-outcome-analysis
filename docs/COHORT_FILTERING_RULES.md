# Cohort filtering rules

How the study cohort is built, step by step, and why a trial is kept or dropped.
Written so that someone who has not seen the code can follow it.

**Rules version:** `conditions_field_v2` (column `cohort_rules_version` in `studies.csv`)
**Configuration:** `config/condition_patterns_cohort.yaml` (all patterns live here)
**Code:** `src/ctgov_pipeline/condition_eligibility.py`, `acute_population_screen.py`, `eligibility_text.py`
**Column meanings:** [DATA_COLUMNS.md](DATA_COLUMNS.md) · **How to rebuild:** [COHORT_REPRODUCTION_GUIDE.md](COHORT_REPRODUCTION_GUIDE.md)

---

## 1. Purpose and big picture

The project studies which **primary outcomes** researchers register for **behavioral interventions in chronic pain**. The data source is the public [ClinicalTrials.gov](https://clinicaltrials.gov) registry (API v2).

Building the cohort has three stages:

```
 1. PULL         ask the registry for trials that satisfy ALL of:
                 interventional  AND  behavioral intervention  AND  a target condition
                         │
 2. DE-DUPLICATE one row per NCT id (a trial can be returned by more than one search)
                         │
 3. FILTER       local rules remove trials that are not the intended population
                 (wrong condition, cancer, pregnancy-related, acute pain, ...)
                         │
                 studies.csv  ── every pulled trial, marked included / excluded, with the reason
```

Two principles run through everything:

- **Nothing is silently dropped.** Every pulled trial stays in `studies.csv`; excluded ones carry the reason.
- **Only the condition/population stage excludes.** The intervention type and the primary outcomes are described and categorised, but never used to include or exclude a trial.

### Current result (extraction run `full_20261109_104453`)

| Step | Trials |
|---|---:|
| Pulled from the registry (unique NCT ids) | 936 |
| Excluded by the rules below | 54 |
| **Included in the cohort** | **882** |
| Registered primary outcomes of included trials | 2,005 |

Exclusions by rule (the first rule that fires is the one recorded):

| Rule key | Reason group | Trials |
|---|---|---:|
| `acute_pain` | acute | 20 |
| `pregnancy_related` | condition | 16 |
| `no_target_match` | condition | 9 |
| `pathology_other` | condition | 6 |
| `cancer_oncology` | condition | 3 |

---

## 2. Stage 1 – Pulling the pool from the registry

### What is requested

```
StudyType            = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND the registered Conditions field contains any of:
    back pain | fibromyalgia | migraine | headache
```

One request is sent per condition term, with all filters joined by AND in a single expression:

```
AREA[StudyType]INTERVENTIONAL AND AREA[InterventionType]BEHAVIORAL AND AREA[Condition]"<term>"
```

### Why `AREA[Condition]` and not `query.cond`

ClinicalTrials.gov offers two different ways to search by condition. They do **not** look at the same parts of the record:

| Parameter | What it searches | Used here? |
|---|---|---|
| `AREA[Condition]"…"` | **Only** the registered Conditions field | **Yes** |
| `query.cond=…` | A broader "ConditionSearch" area: Conditions, brief title, official title, condition MeSH terms, MeSH ancestors, keywords, and the NCT id, with synonym expansion | **No** |

`query.cond` was tried earlier and pulled trials whose registered condition was unrelated (Arthritis, Insomnia, Anesthesia, …) because the target word appeared only in a title or keyword. Restricting to `AREA[Condition]` keeps the pull aligned with "the trial lists this as a condition".

### Other pull details

- "Behavioral" is the registry's own intervention-type label (exercise, physiotherapy, education, mind-body practices, …). It is used as labelled and is not re-judged.
- Results of the four searches are merged and **de-duplicated by `nct_id`**. The de-duplication **does** remove overlapping hits: the four searches returned 994 records in total, of which 58 were the same trial returned by more than one search, leaving **936 unique NCT ids**. `api_retrieval_queries` records which search(es) found each trial (keys: `back_pain`, `fibromyalgia`, `migraine`, `headache`).
- Raw JSON, one file per trial, is saved unchanged under `data/raw/full/<extraction_run_id>/studies/`. Only one run is kept. Everything below is recomputed from these files with no network access.
- The registry matches **whole words and expands synonyms**, so a few pulled trials do not contain a target as a substring in their conditions (e.g. `Myofascial Pain Syndrome` returned for fibromyalgia, `Low Back Ache` for back pain). The local filter removes them as `no_target_match`.
- The build stops with an error if `nct_id` (or `outcome_id`) is not unique in the output tables.

### Why the back-pain term is `back pain` (not `chronic back pain`)

The pull originally used the phrase `chronic back pain`, which returned only about 11 trials. Widening it to `back pain` brought the back-pain search to 503 trials and added roughly **180–190 trials** that were not in the earlier pool (mostly registered as plain `Low Back Pain`).

Among the 468 included trials that currently carry the back-pain flag, about **340** also have a chronicity cue in their conditions, title or the `pain_duration_inclusion` column, and about **128** have no such cue. Clearly acute ones are still removed by the acute-word screen (section 4). Whether the broader term makes the cohort too noisy is an open judgment call; the known-limits section records it.

### What a `chronic pain` pull would add

A separate check (behavioral + interventional + `AREA[Condition]"chronic pain"`) returns **594** trials, of which only **60** are already in the current pool. That would add about **534 new NCT ids**, most registering only the generic label `Chronic Pain` (or similar) without naming back pain, fibromyalgia, migraine or headache. They are **not** in the current cohort. Adding them would be a deliberate broadening of the cohort definition.

---

## 3. Stage 2 – Filtering rules

Each pulled trial is checked against the rules **in this order**. The first rule that fires decides, and its key is recorded at the start of `exclusion_detail`.

| Order | Rule key | `exclusion_reason` | Excludes a trial when… | Text searched |
|---:|---|---|---|---|
| 1 | `cancer_oncology` | condition | an oncology word appears (cancer, carcinoma, oncolog-, neoplasm, malignan-, …) | conditions, keywords, brief title, official title |
| 2 | `pathology_other` | condition | a non-pain primary disease appears (e.g. intracranial hypertension, pseudotumor, meningitis, multiple sclerosis) | same as above |
| 3 | `pregnancy_related` | condition | pregnancy, postpartum, childbirth, menstrual/dysmenorrhea or pelvic girdle pain wording appears | same as above |
| 4 | `acute_pain` | acute | the enrolled population is described with the word **acute** (details in section 4) | eligibility inclusion criteria, conditions, titles, brief summary |
| 5 | `no_target_match` | condition | none of the four target conditions matches the registered conditions | registered conditions |

If no rule fires, the trial is **included**.

### Why rules 1–3 ignore the eligibility criteria

Eligibility text is full of boilerplate such as "excluded: pregnancy, cancer", "must not be pregnant", "non-oncological pain". Searching it for those words would exclude almost every trial.

A check of the current included set found hundreds of eligibility-only hits for pregnancy/cancer wording, almost all of them under the **exclusion** criteria or as a negation in the inclusion criteria ("not pregnant", "non-pregnant", "chronic non-oncological pain"). The few inclusion-only hits that looked real were either negations or already covered once the postpartum pattern allowed a spaced hyphen (`Post -Partum`). So the current scope (conditions + keywords + titles) is kept; eligibility text is **not** used for rules 1–3.

### 3.1 The target condition check (rule 5, and the condition flags)

A trial must have at least one target condition **in its registered conditions**. Keywords and titles alone never qualify a trial.

Each registered condition line is tested separately as a substring against the patterns in the YAML. This sets four independent flags in `studies.csv`:

| Flag column | Target | Examples of what matches |
|---|---|---|
| `eligible_back_pain` | back pain | `Low Back Pain`, `Chronic Low Back Pain`, `Back Pain`, `Pain, Back`, `CLBP`, `LBP` |
| `eligible_fibromyalgia` | fibromyalgia | `Fibromyalgia`, `Fybromyalgia`, `FM` |
| `eligible_migraine` | migraine | `Migraine`, `Chronic Migraine`, `Vestibular Migraine` |
| `eligible_headache` | headache (non-migraine) | `Tension-Type Headache`, `Cluster Headache`, `Headache`, `Pain, Head`, `Head Pain` |

- A trial can carry **several flags** (about 50 included trials have more than one). There is no rule that removes a headache label because migraine is also present, and migraine wording in the eligibility text never affects the flags.
- Every included trial therefore has at least one flag `True`. `condition_matched` lists the matched targets as text (`back_pain`, not "chronic back pain", even when the registered wording includes "chronic").

### 3.2 Comorbid or additional conditions are not a rule

A trial that lists a target plus many other conditions (mood, other pain conditions, CNS conditions, widespread pain, …) stays in however many it lists. An earlier rule excluding trials with three or more non-target conditions was removed after manual review showed most of them were relevant. All listed conditions remain visible in `raw_conditions`.

### 3.3 Descriptive tags and the pain-duration column (never exclude)

| Column | What it shows |
|---|---|
| `condition_feature_flags` | Tags found in the trial text, for filtering at analysis time. Includes `post_traumatic`, `tbi_concussion`, `subacute`, `perioperative`, `surgical_postoperative`, `medication_overuse_headache`, `secondary_pain`, `visual_snow`, `vestibular_schwannoma`. Use `subacute` / `perioperative` / `surgical_postoperative` when you want to set aside recent-onset or surgical cases without an automatic exclusion rule. |
| `review_flags` | Currently `provider_or_system_level`: the title mentions clinicians, guidelines, implementation, decision support, referral, a care model or a health system. Meant to help check whether a trial targets clinicians or care systems rather than patients. Some hits are ordinary patient trials delivered in such a setting. |
| `pain_duration_inclusion` | Verbatim sentence(s) from the **inclusion** criteria that state how long the pain/condition lasts (e.g. for NCT01761617: `Current non-specific low back pain persisting >12 weeks.`). Empty when no such sentence is found. Heuristic; never used to include or exclude. |

---

## 4. The acute-pain screen (rule 4)

**Goal:** exclude trials whose *enrolled population* is described as **acute** pain.

This screen looks for the word **acute** (and a small set of close phrases such as `Pain, Acute`) in the places listed below. It does **not** try to parse free-text duration windows such as "pain for less than 3 months", "within the past 12 weeks", or "recent surgery/injury". Those phrasings vary too much (inclusion vs exclusion, negation, different time windows), so they are left for analysis via `pain_duration_inclusion` and the `subacute` / `perioperative` / `surgical_postoperative` feature flags.

### Text used

| Used | Not used |
|---|---|
| Eligibility **inclusion** criteria (checked first) | Detailed description |
| Registered **conditions** (each line) | Keywords / MeSH-style terms |
| Official title, brief title, brief summary | Intervention names |

### Order of checks

1. **Inclusion criteria** – acute population wording → exclude.
2. If the inclusion criteria describe a **chronic** population and acute pain is only mentioned under the **exclusion** criteria → pass (acute pain is what the trial excludes).
3. **Conditions**, then **official title → brief title → brief summary** – skipped entirely when **every** registered condition contains the word `chronic`.

Every occurrence of "acute" in a text is checked, not just the first.

### Uses of "acute" that are not a population (ignored)

Only that specific occurrence is ignored; other acute wording in the same text still counts.

| Pattern | Example |
|---|---|
| Laboratory stimulus | "acute noxious physical stimuli" |
| Drug / treatment wording | "acute pain relief medications", "acute migraine attacks", "acute treatment" |
| Acute flare of a chronic condition | "acute pain episode of chronic low back pain" |
| Background contrast | "chronic versus acute PTHA" |
| Negation | "not due to acute trauma", "without acute pain" |

### Pass examples

- "Acute" only under the **exclusion** criteria.
- `Chronic Pain` and `Acute Pain` both listed, with inclusion criteria supporting a chronic cohort.
- All registered conditions contain `chronic` (e.g. only `Chronic Low Back Pain`).

### Rule key written by this screen

| Key | Meaning |
|---|---|
| `acute_pain` | Acute pain population (word "acute" describing who is enrolled) |

An earlier special case that excluded trials whose inclusion criteria mentioned both acute and chronic populations (`acute_and_chronic_in_inclusion`) was removed: only one trial hit it, which is not enough to justify a separate rule. That trial is still excluded when the ordinary acute-population check fires.

---

## 5. What gets recorded for an excluded trial

| Column | Meaning |
|---|---|
| `cohort_inclusion_status` | `included` or `excluded` |
| `exclusion_reason` | **General reason**, one of two values: `acute` or `condition` (empty if included) |
| `exclusion_detail` | **Specific explanation**. Always starts with the rule key, then the matched text and where it was found, e.g. `acute_pain: Acute pain population (found in eligibility_inclusion_1). Matched text: "…"` |

| `exclusion_reason` | Rule keys |
|---|---|
| `acute` | `acute_pain` |
| `condition` | `cancer_oncology`, `pathology_other`, `pregnancy_related`, `no_target_match` |

For manual review, the registered text is kept verbatim in the `raw_*` columns (titles, a 50-word summary, conditions, keywords, eligibility criteria), so any decision can be checked against the source.

---

## 6. What is deliberately not filtered

- **Interventions.** `intervention_categories` (from the active arms), `is_multimodal` and `control_arm_types` describe the intervention but never exclude. Arm text is kept in `raw_intervention_names` and `raw_intervention_details`.
- **Primary outcomes.** Raw text is preserved in `primary_outcomes.csv`. `outcome_category` / `outcome_subcategory` are rule-based aids for review, not a coding of the outcomes and not used to filter.
- **Trial status and date.** `raw_overall_status` and `raw_study_first_post_date` are variables to analyse, not filters.
- **Age group, trial size, design, comorbidities.** Not used.
- **Pain-duration windows, recent surgery/injury, peri-operative timing.** Not automatic exclusions (see section 4 and the feature flags / `pain_duration_inclusion` column).

---

## 7. Known limits and judgment calls

- **Back pain is not restricted to chronic back pain.** The pull uses the term `back pain`. Clearly acute ones are removed by the acute-word screen; trials with no duration information stay in. See section 2 for the count of trials added by the broader term.
- **Generic registered conditions are not retrieved.** A trial whose only registered condition is generic (e.g. `Chronic Pain`) is not pulled, even if its title names a target (e.g. NCT00796536, NCT01794988, NCT01993355). A dedicated `chronic pain` pull would add ~534 new NCT ids (section 2); that is a separate cohort-definition choice.
- **Other suspected-irrelevant groups reviewed but kept** (November 2026): trials where the target is one of many listed conditions and the title is not about pain (~41, e.g. arthritis, ME/CFS, tinnitus programs); concussion/TBI as the primary population (~10); healthy or non-patient samples (~6); asymptomatic prevention/school groups (~10–15). They remain included; they can be filtered at analysis time using `raw_conditions`, `condition_feature_flags`, `review_flags` and `pain_duration_inclusion`.
- **Judgment call:** NCT03157544 (chronic neck/low back pain patients during an acute flare) is included.
- **Registry synonym matching** can return trials with no target substring in their conditions; these are excluded as `no_target_match` (see section 2).

---

## 8. Manual QC reference trials

These trials were reviewed by hand and their expected status is enforced by `tests/test_finalize_cohort.py`.

| NCT | Expected | Why |
|---|---|---|
| NCT03537573 | exclude | acute diagnosis in inclusion criteria |
| NCT02647658 | exclude | acute low back pain in inclusion criteria (prevention study) |
| NCT04356963 | exclude | `Pain, Acute` in registered conditions |
| NCT00937365 | exclude | pregnancy-related low back pain (`pregnancy_related`) |
| NCT03483168 | include | educational "acute vs chronic" in the summary; registered condition is chronic only |
| NCT04636177 | include | "not due to acute trauma" |
| NCT06971809 | include | chronic in inclusion criteria, acute only under exclusion |
| NCT04984720 | include | "acute pain relief medications" is drug wording |
| NCT02419131 | include | "chronic versus acute PTHA" is background; the trial enrolls chronic post-traumatic headache |
| NCT03157544 | include | chronic neck/low back pain during an acute flare (**judgment call**) |
| NCT06114264 | include | `Pain, Chronic` is the generic chronic-pain label, not a reason to exclude |

NCT00796536 and NCT01794988 were used earlier as examples of acute-screen behavior ("acute" appearing only in the detailed description / keywords). They are no longer retrieved because their only registered condition is `Chronic Pain`.

---

## 9. Reproducing the cohort

```bash
source .venv/bin/activate
PYTHONPATH=src python -m ctgov_pipeline.finalize_cohort   # rebuild tables from raw JSON (no network)
PYTHONPATH=src python -m ctgov_pipeline.run_full          # NEW registry pull (creates a new raw run)
PYTHONPATH=src python -m unittest discover -s tests -v    # all tests
```

Outputs are written to `data/processed/`: `studies.csv`, `primary_outcomes.csv`, `cohort_report.md` (auto-generated statistics) and `manifest.json`.
