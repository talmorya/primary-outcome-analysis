# Pilot inspection report

Run ID: `pilot_20260818_141318`  
API version: 2.0.5 | Data timestamp: 2026-08-17

## What was extracted

| Output | Location | Rows |
|---|---|---|
| Raw API JSON | `data/raw/pilot/pilot_20260818_141318/` | 40 studies + 5 search pages |
| Study table | `data/processed/pilot/pilot_20260818_141318/studies.csv` | 40 interventional trials |
| Outcome table | `data/processed/pilot/pilot_20260818_141318/primary_outcomes.csv` | 111 primary outcomes |
| Annotation template | `data/processed/pilot/pilot_20260818_141318/outcome_annotations_template.csv` | Empty (schema only) |

All 40 studies are `INTERVENTIONAL`. No conceptual outcome categories were assigned during extraction.

## Sample composition

**Intervention approaches (top):** relaxation (4), CBT (2), CBT+mindfulness (2), CBT+relaxation+self-management (2), biofeedback (2), pain education (2), counseling (2), psychotherapy (2), plus single examples of PRT, hypnosis, meditation, ACT/acceptance-based, digital psych, and multimodal combinations.

**Conditions matched:** chronic back pain (16), fibromyalgia (15), IBS (8), migraine (1).

**Status (all retained):** COMPLETED (28), UNKNOWN (4), RECRUITING (4), NOT_YET_RECRUITING (2), ACTIVE_NOT_RECRUITING (1), SUSPENDED (1).

**Multiple primary outcomes:** 14/40 studies have ≥3 registered primaries; max = 12 (NCT03986489).

**Review flags:** 31/40 intervention, 5/40 condition — expected at this stage for multimodal and broad terms.

## NCT05658185 — preserved outcome complexity

This study illustrates why raw text must be kept intact. Each primary outcome combines a timepoint-rich measure title, a detailed instrument description, and a multi-wave time frame.

| outcome_id | measure (raw) | key extracted features |
|---|---|---|
| `NCT05658185__po_1` | Change Emotional Distress Baseline T1, Baseline T2-Pre, Post-Treatment T3 and Follow-up T4. | HADS; acronyms: HADS; phrases: emotional distress; keywords: anxiety, depression, distress, caregivers |
| `NCT05658185__po_2` | Change in Perception of psychological stress. Baseline T1… | acronyms: EEP-10; phrases: psychological stress; keywords: stress |
| `NCT05658185__po_3` | Change in quality of life. Baseline T1… | MSQ / Migraine-Specific Quality of Life Questionnaire; phrases: quality of life |

The measure titles alone do not specify which subscale or domain is primary; the description carries the instrument identity and scoring interpretation. No conceptual category was assigned.

## Other illustrative outcomes

**NCT01666639** (CBT/self-management, back pain)  
- Measure: Hannover Functional Ability Questionnaire (HFAQ)  
- Raw description preserved in full; acronym HFAQ extracted; instrument not in lexicon yet

**NCT06406699** (PRT, back/neck pain)  
- Measure: PEG-3 Average Pain in last week  
- Description includes 0–10 scale anchor definitions; instrument PEG-3 detected

**NCT03319355** (multicomponent fibromyalgia, 8 primaries)  
- FIQ, Tampa Scale of Kinesiophobia, BDI, PSQI among co-primary outcomes  
- Shows need for outcome-level (not study-level) analysis

**NCT01345344** (CBT/relaxation/self-management)  
- Co-primary clinical (BPI) and neurobiological (fMRI) outcomes in same trial

## Pilot validation checklist

| Test | Result |
|---|---|
| Raw outcome text preserved | Pass — character-level match to API JSON |
| No conceptual categories assigned | Pass |
| Instruments extracted where in lexicon | Partial — HADS, BPI, FIQ, PEG-3, MSQ detected; HFAQ, EEP-10 acronym-only |
| Acronyms extracted | Pass — HADS, EEP-10, MSQ, BPI, PEG-3, HFAQ |
| Keywords/phrases/verbs | Pass — matched terms listed without category mapping |
| Multiple primaries expanded | Pass — 111 rows from 40 studies |
| Temporal date preserved | Pass — `study_first_post_date` on both tables |
| All statuses retained | Pass |
| Psych intervention breadth | Pass — 15+ distinct approach labels |
| Ambiguous/multimodal flagged | Pass — 31 review flags |

## Issues to address before full extraction

1. **Instrument lexicon gaps:** HFAQ, EEP-10, and other study-specific scales are missed or acronym-only. Expand lexicon iteratively from pilot review, not from conceptual categories.

2. **Condition balance:** Only 1 migraine study in pilot despite 500-study search pool — full extraction should use condition-stratified sampling or condition-specific search passes.

3. **High multimodal rate:** 19/40 studies classified as `multimodal` domain because physical + psychological co-interventions are common. Decide whether primary psych analysis uses `psychological_behavioral` only, or includes `multimodal` with psych approaches present.

4. **Acronym false positives:** Generic uppercase tokens (e.g. T1, T2) may appear — review acronym extraction rules.

5. **Annotation layer:** `outcome_annotations_template.csv` is ready; categories remain unassigned until manual/rule/LLM annotation.

## Suggested next step

Review `primary_outcomes.csv` and flag:
- outcomes where instrument extraction missed obvious names
- outcomes where keyword/phrase lists are too sparse or too broad
- intervention classifications that need rule refinement

After review, proceed to full condition-wide extraction with the same two-table schema.
