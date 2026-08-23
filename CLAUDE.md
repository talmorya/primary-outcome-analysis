# CLAUDE.md — AI context for primary_outcome_analysis

## Project purpose

Reproducible ClinicalTrials.gov API v2 pipeline for studying **registered primary outcomes** in **behavioral interventional** chronic pain trials.

**Research question:** Among behavioral/psychological interventions for chronic pain, what primary outcomes do researchers register, and how does this differ across intervention approaches and over time (`study_first_post_date`)?

**Motivating hypothesis (to test empirically, not assume):** CBT/ACT/acceptance-oriented approaches may emphasize interference, functioning, coping, or adaptation; PRT/pain-reprocessing/pain-education approaches may more often target pain intensity/severity.

---

## Cohort definition (do not change without explicit approval)

```
StudyType = INTERVENTIONAL
AND InterventionType = BEHAVIORAL
AND condition ∈ {chronic back pain, fibromyalgia, migraine}
```

- **IBS excluded**
- All trial statuses retained (`overall_status` is a variable, not a filter)
- Local condition validation post-API (`config/condition_patterns.yaml`)
- CT.gov `BEHAVIORAL` is broad — exercise/lifestyle trials are **flagged** via `non_psychological_behavioral_flag`, not excluded

Latest full run: `full_20260823_201251` — **674 studies**, **1,591 primary outcomes**

---

## Critical constraints

1. **Preserve raw outcome text verbatim** — `primary_outcome_measure`, `primary_outcome_description`, `primary_outcome_time_frame`
2. **Do NOT assign conceptual outcome categories at extraction** (pain intensity, interference, coping, etc.). Use the separate annotation layer (`outcome_annotations_template.csv`)
3. **`outcome_purpose` is exploratory/heuristic only** — do not use it to exclude, filter, or quantitatively classify outcomes
4. **Two-table architecture only** — `studies.csv` + `primary_outcomes.csv`. No third denormalized analysis table
5. **Raw JSON is immutable** — reprocess from `data/raw/` rather than re-querying CT.gov unless starting a new extraction run
6. **Instrument matching uses word-boundary logic** — do not revert to substring matching (caused ISI false positives). Run `tests/test_instrument_extraction.py` after lexicon changes

---

## Key paths

| Path | Contents |
|---|---|
| `data/processed/full/full_20260823_201251/studies.csv` | One row per trial |
| `data/processed/full/full_20260823_201251/primary_outcomes.csv` | One row per registered primary outcome |
| `data/raw/full/full_20260823_201251/studies/` | Per-NCT JSON (gitignored) |
| `config/condition_patterns.yaml` | Local condition matching |
| `config/intervention_taxonomy.yaml` | `behavioral_component`, multimodal, non-psych flags |
| `config/outcome_lexicon.yaml` | Instrument/keyword/phrase extraction (not categories) |
| `src/ctgov_pipeline/` | Pipeline modules |
| `reports/full/extraction_summary.md` | Run metrics |

---

## Pipeline commands

```bash
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=src python -m ctgov_pipeline.run_full    # full extraction
PYTHONPATH=src python -m ctgov_pipeline.run_pilot   # ~40 study pilot
PYTHONPATH=src python -m unittest tests.test_instrument_extraction -v
```

---

## Data model essentials

### `studies.csv`
- `behavioral_component` — pipe-joined psych approaches (cbt, act, mindfulness_mbsr_mbct, pain_education, prt, etc.)
- `is_multimodal`, `other_modality_type`, `other_modality_name` — psych component + other modality preserved separately
- `non_psychological_behavioral_flag` — exercise/lifestyle/diet typed as BEHAVIORAL on CT.gov

### `primary_outcomes.csv`
- Linked by `nct_id`; unit of analysis for outcome-selection trends
- Exploratory: `instruments_detected`, `acronyms_detected`, `keywords_matched`, `phrases_matched`, `action_verbs_matched`
- Heuristic: `outcome_purpose` (not for filtering)

---

## Known QC issues (as of full extraction)

- **232/674 studies** have missing `behavioral_component` — mostly exercise/lifestyle-only BEHAVIORAL trials (expected)
- **81 studies** in catch-all `other_psychological` — taxonomy gaps (CFT, motivational interviewing, exposure therapy)
- **279 studies** flagged `non_psychological_behavioral_flag` (41%); **136 multimodal** (20%)
- For psych-focused analysis, define an explicit subset (studies with assigned `behavioral_component`, not exercise-only)

Taxonomy gaps to address in **annotation pass**, not by re-extraction: Cognitive Functional Therapy, motivational interviewing, exposure/graded exposure, coping skills training.

---

## Code conventions

- Match existing style in `src/ctgov_pipeline/`
- Config-driven rules in YAML under `config/`
- Minimize scope — focused diffs, no over-engineering
- Do not commit secrets or large data files (`data/raw/`, `data/processed/` are gitignored)

---

## Git workflow

**Commit and push as you work** so progress is never lost. Do not leave completed changes uncommitted at the end of a session.

- **Remote:** https://github.com/talmorya/primary-outcome-analysis
- **Branch:** work on `main` (or the active feature branch if the user specifies one)
- **When to commit:** after completing a logical unit of work (pipeline change, config update, report, fix, documentation)
- **Commit messages:** short, imperative, describe *why* — e.g. `Add CLAUDE.md with project context and git workflow`, `Fix instrument boundary matching for ISI false positives`
- **Push:** after each commit (or a small batch of related commits), push to the remote branch: `git push origin HEAD`
- **Do not:** force-push, commit gitignored data blobs, or modify unrelated branches
- **Verify:** confirm push succeeded (`git status` shows up to date with remote)

Human docs: `README.md`
