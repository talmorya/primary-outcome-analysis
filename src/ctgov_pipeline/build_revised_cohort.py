"""Build revised cohort with hard inclusion criteria (review layer; not production)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .classify_intervention_categories import classify_intervention_categories
from .condition_eligibility import evaluate_condition_eligibility
from .config_loader import PROJECT_ROOT, load_yaml
from .extract_outcome_features import extract_outcome_features
from .intervention_eligibility import (
    evaluate_intervention_eligibility,
    evaluate_mechanism_exclusion,
)
from .outcome_category import classify_outcome_category
from .outcome_mechanism import is_mechanistic_outcome
from .parse import load_raw_studies

SOURCE_RUN_ID = "full_20260823_201251"
REVISED_RUN_ID = "revised_20260910_review"

HEADACHE_EXPANSION_NCTS = [
    "NCT01664585",
    "NCT01155557",
    "NCT01213056",
    "NCT07240532",
    "NCT01525303",
    "NCT06041997",
    "NCT00181064",
    "NCT00457496",
    "NCT06631222",
    "NCT02264340",
    "NCT02460003",
    "NCT00897780",
    "NCT04867967",
    "NCT06822673",
    "NCT00956969",
    "NCT01347684",
    "NCT01488825",
    "NCT03166358",
    "NCT00389038",
    "NCT02475005",
    "NCT00267618",
    "NCT03308630",
]

QUERY_SOURCE = (
    "StudyType=INTERVENTIONAL AND InterventionType=BEHAVIORAL "
    "AND condition IN (chronic back pain, fibromyalgia, migraine, primary headache)"
)


def _join(values: list[str] | None, sep: str = " | ") -> str | None:
    if not values:
        return None
    return sep.join(values)


def _load_all_records() -> list[tuple[dict[str, Any], str]]:
    raw_dir = PROJECT_ROOT / "data" / "raw" / "full" / SOURCE_RUN_ID / "studies"
    records: list[tuple[dict[str, Any], str]] = [
        (record, "existing_extraction") for record in load_raw_studies(raw_dir)
    ]

    headache_path = PROJECT_ROOT / "reports/exploration/headache_candidates_raw.json"
    if headache_path.is_file():
        payload = json.loads(headache_path.read_text(encoding="utf-8"))
        by_nct = {
            item["protocolSection"]["identificationModule"]["nctId"]: item
            for item in payload["studies"]
        }
        existing_ids = {r[0]["protocolSection"]["identificationModule"]["nctId"] for r in records}
        for nct_id in HEADACHE_EXPANSION_NCTS:
            if nct_id in by_nct and nct_id not in existing_ids:
                records.append((by_nct[nct_id], "headache_expansion"))

    return records


def _parse_record(
    record: dict[str, Any],
    *,
    cohort_source: str,
    condition_config: dict[str, Any],
    intervention_config: dict[str, Any],
    outcome_lexicon: dict[str, Any],
    force_headache_include: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    ps = record.get("protocolSection", {})
    id_mod = ps.get("identificationModule", {})
    status_mod = ps.get("statusModule", {})
    conditions_mod = ps.get("conditionsModule", {})
    design_mod = ps.get("designModule", {})
    arms_mod = ps.get("armsInterventionsModule", {})
    outcomes_mod = ps.get("outcomesModule", {})

    nct_id = id_mod.get("nctId")
    conditions = conditions_mod.get("conditions", []) or []
    keywords = conditions_mod.get("keywords", []) or []
    interventions = arms_mod.get("interventions", []) or []

    cond = evaluate_condition_eligibility(
        conditions=conditions,
        keywords=keywords,
        config=condition_config,
        brief_title=id_mod.get("briefTitle"),
        official_title=id_mod.get("officialTitle"),
        intervention_names=_join([item.get("name", "") for item in interventions]),
        force_headache_include=force_headache_include,
    )

    intervention_cls = classify_intervention_categories(interventions, intervention_config)
    intervention_elig = evaluate_intervention_eligibility(intervention_cls)
    mechanism_elig = evaluate_mechanism_exclusion(
        classification=intervention_cls,
        record=record,
    )

    cohort_included = (
        cond.eligibility in {"eligible", "borderline"}
        and intervention_elig.intervention_eligible
        and not mechanism_elig.mechanism_excluded
    )

    if cond.eligibility == "excluded":
        exclusion_stage = "condition"
        exclusion_reason = cond.exclusion_rule or "condition_excluded"
    elif not intervention_elig.intervention_eligible:
        exclusion_stage = "intervention"
        exclusion_reason = intervention_elig.exclusion_reason or "intervention_ineligible"
    elif mechanism_elig.mechanism_excluded:
        exclusion_stage = "mechanism"
        exclusion_reason = mechanism_elig.exclusion_reason or "mechanism_study"
    else:
        exclusion_stage = ""
        exclusion_reason = ""

    eligible_targets = cond.targets_eligible
    study_row = {
        "nct_id": nct_id,
        "cohort_source": cohort_source,
        "cohort_included": cohort_included,
        "exclusion_stage": exclusion_stage,
        "exclusion_reason": exclusion_reason,
        "brief_title": id_mod.get("briefTitle"),
        "official_title": id_mod.get("officialTitle"),
        "conditions_raw": _join(conditions),
        "keywords_raw": _join(keywords),
        "condition_eligibility": cond.eligibility,
        "condition_exclusion_rule": cond.exclusion_rule or "",
        "condition_borderline_reason": cond.borderline_reason or "",
        "condition_matched": _join(eligible_targets),
        "eligible_migraine": "migraine" in eligible_targets,
        "eligible_chronic_back_pain": "chronic_back_pain" in eligible_targets,
        "eligible_fibromyalgia": "fibromyalgia" in eligible_targets,
        "eligible_headache": "primary_headache" in eligible_targets,
        "intervention_categories": _join(intervention_cls.intervention_categories),
        "intervention_category_labels": _join(intervention_cls.intervention_category_labels),
        "intervention_classification_rule": _join(intervention_cls.classification_rules),
        "intervention_review_flag": intervention_cls.review_flag,
        "is_multimodal": intervention_cls.is_multimodal,
        "multimodal_modalities": _join(intervention_cls.multimodal_modalities),
        "interventions_raw": json.dumps(interventions, ensure_ascii=False),
        "intervention_names": _join([item.get("name", "") for item in interventions]),
        "intervention_types": _join(sorted({item.get("type", "") for item in interventions})),
        "overall_status": status_mod.get("overallStatus"),
        "study_type": design_mod.get("studyType"),
        "primary_purpose": design_mod.get("designInfo", {}).get("primaryPurpose"),
        "primary_outcome_mechanistic": mechanism_elig.primary_outcome_mechanistic,
        "has_clinical_outcome_anywhere": mechanism_elig.has_clinical_outcome_anywhere,
        "phases": _join(design_mod.get("phases", [])),
        "has_results": record.get("hasResults"),
        "study_first_post_date": status_mod.get("studyFirstPostDateStruct", {}).get("date"),
        "query_source": QUERY_SOURCE,
        "extraction_run_id": REVISED_RUN_ID,
        "source_extraction_run_id": SOURCE_RUN_ID,
        "feature_extraction_version": outcome_lexicon.get("version"),
    }

    primary_outcomes = outcomes_mod.get("primaryOutcomes", []) or []
    outcome_rows: list[dict[str, Any]] = []
    for index, outcome in enumerate(primary_outcomes, start=1):
        measure = outcome.get("measure")
        description = outcome.get("description")
        time_frame = outcome.get("timeFrame")
        features = extract_outcome_features(measure, description, time_frame, outcome_lexicon)
        category = classify_outcome_category(measure, description, time_frame)
        outcome_rows.append(
            {
                "outcome_id": f"{nct_id}__po_{index}",
                "nct_id": nct_id,
                "cohort_included": cohort_included,
                "primary_outcome_index": index,
                "n_primary_outcomes_in_study": len(primary_outcomes),
                "primary_outcome_measure": measure,
                "primary_outcome_description": description,
                "primary_outcome_time_frame": time_frame,
                "outcome_category": category.outcome_category,
                "outcome_subcategory": category.outcome_subcategory,
                "outcome_category_rule": category.rule,
                "outcome_category_review_flag": category.review_flag,
                "outcome_is_mechanistic": is_mechanistic_outcome(measure, description, time_frame),
                "instruments_detected": _join(features.instruments_detected),
                "acronyms_detected": _join(features.acronyms_detected),
                "keywords_matched": _join(features.keywords_matched),
                "phrases_matched": _join(features.phrases_matched),
                "action_verbs_matched": _join(features.action_verbs_matched),
                "brief_title": study_row["brief_title"],
                "condition_matched": study_row["condition_matched"],
                "intervention_categories": study_row["intervention_categories"],
                "is_multimodal": study_row["is_multimodal"],
                "overall_status": study_row["overall_status"],
                "study_first_post_date": study_row["study_first_post_date"],
                "extraction_run_id": REVISED_RUN_ID,
            }
        )

    audit = {
        "nct_id": nct_id,
        "cohort_source": cohort_source,
        "cohort_included": cohort_included,
        "exclusion_stage": exclusion_stage,
        "exclusion_reason": exclusion_reason,
        "condition_eligibility": cond.eligibility,
        "intervention_eligible": intervention_elig.intervention_eligible,
        "mechanism_excluded": mechanism_elig.mechanism_excluded,
    }
    return study_row, outcome_rows, audit


def build_revised_cohort() -> Path:
    out_dir = PROJECT_ROOT / "reports" / "exploration" / "revised_cohort"
    out_dir.mkdir(parents=True, exist_ok=True)

    condition_config = load_yaml("condition_patterns_proposed.yaml")
    intervention_config = load_yaml("intervention_categories.yaml")
    outcome_lexicon = load_yaml("outcome_lexicon.yaml")

    study_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []

    for record, source in _load_all_records():
        nct_id = record["protocolSection"]["identificationModule"]["nctId"]
        study_row, outcomes, audit = _parse_record(
            record,
            cohort_source=source,
            condition_config=condition_config,
            intervention_config=intervention_config,
            outcome_lexicon=outcome_lexicon,
            force_headache_include=source == "headache_expansion",
        )
        study_rows.append(study_row)
        outcome_rows.extend(outcomes)
        audit_rows.append(audit)

    studies_df = pd.DataFrame(study_rows)
    outcomes_df = pd.DataFrame(outcome_rows)
    audit_df = pd.DataFrame(audit_rows)

    studies_df.to_csv(out_dir / "studies.csv", index=False)
    outcomes_df.to_csv(out_dir / "primary_outcomes.csv", index=False)
    audit_df.to_csv(out_dir / "exclusion_audit.csv", index=False)

    _write_report(studies_df, outcomes_df, audit_df, out_dir / "revised_cohort_report.md")
    _write_questionable_exclusions(studies_df, out_dir / "questionable_exclusions.md")
    _write_outcome_other_analysis(outcomes_df, out_dir / "outcome_other_category_review.md")
    return out_dir


def _write_report(
    studies_df: pd.DataFrame,
    outcomes_df: pd.DataFrame,
    audit_df: pd.DataFrame,
    path: Path,
) -> None:
    total = len(studies_df)
    included = studies_df[studies_df["cohort_included"] == True]
    excluded = studies_df[studies_df["cohort_included"] != True]

    cond_excl = audit_df[audit_df["exclusion_stage"] == "condition"]
    int_excl = audit_df[audit_df["exclusion_stage"] == "intervention"]
    mech_excl = audit_df[audit_df["exclusion_stage"] == "mechanism"]

    inc_outcomes = outcomes_df[outcomes_df["cohort_included"] == True]

    lines = [
        "# Revised cohort report",
        "",
        "**Status:** Review layer only — does not modify `data/processed/full/`.",
        "",
        f"- **Master pool (pre-filter):** {total} studies",
        f"- **Eligible cohort:** {len(included)} studies",
        f"- **Excluded (total):** {len(excluded)} studies",
        "",
        "## Exclusions by stage",
        "",
        f"- **Condition stage:** {len(cond_excl)}",
        f"- **Intervention stage:** {len(int_excl)}",
        f"- **Mechanism / non-treatment stage:** {len(mech_excl)}",
        "",
        "### Condition exclusion reasons",
        "",
    ]
    for reason, n in cond_excl["exclusion_reason"].value_counts().items():
        lines.append(f"- `{reason}`: {n}")

    lines.extend(["", "### Intervention exclusion reasons", ""])
    for reason, n in int_excl["exclusion_reason"].value_counts().items():
        lines.append(f"- `{reason}`: {n}")

    lines.extend(["", "### Mechanism exclusion reasons", ""])
    for reason, n in mech_excl["exclusion_reason"].value_counts().items():
        lines.append(f"- `{reason}`: {n}")

    lines.extend(["", "## Intervention categories (eligible cohort)", ""])
    cat_counts: dict[str, int] = {}
    for cats in included["intervention_categories"].fillna(""):
        for cat in [c.strip() for c in str(cats).split("|") if c.strip()]:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, n in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{cat}`: {n}")

    multimodal = included["is_multimodal"] == True
    lines.extend(
        [
            "",
            "## Multimodal vs purely behavioral (eligible cohort)",
            "",
            f"- **Purely behavioral:** {len(included) - int(multimodal.sum())}",
            f"- **Multimodal (behavioral + drug/device/procedure):** {int(multimodal.sum())}",
            "",
            "## Primary outcomes (eligible cohort)",
            "",
            f"- **Total primary outcome rows:** {len(inc_outcomes)}",
            "",
            "### Outcome category distribution",
            "",
        ]
    )
    for cat, n in inc_outcomes["outcome_category"].value_counts().items():
        lines.append(f"- `{cat}`: {n}")

    lines.extend(["", "### Outcome subcategory distribution (top 20)", ""])
    for (cat, sub), n in (
        inc_outcomes.groupby(["outcome_category", "outcome_subcategory"])
        .size()
        .sort_values(ascending=False)
        .head(20)
        .items()
    ):
        lines.append(f"- `{cat}` → `{sub}`: {n}")

    lines.extend(["", "## Condition flags (eligible cohort)", ""])
    for col, label in [
        ("eligible_migraine", "Migraine"),
        ("eligible_chronic_back_pain", "Chronic back pain"),
        ("eligible_fibromyalgia", "Fibromyalgia"),
        ("eligible_headache", "Primary headache"),
    ]:
        lines.append(f"- **{label}:** {int((included[col] == True).sum())}")

    mech_flag = included["primary_outcome_mechanistic"] == True
    lines.extend(
        [
            "",
            "## Primary outcome mechanistic flag (eligible cohort)",
            "",
            f"- **primary_outcome_mechanistic = TRUE:** {int(mech_flag.sum())}",
            f"- **primary_outcome_mechanistic = FALSE:** {len(included) - int(mech_flag.sum())}",
            "",
            "### By condition (primary_outcome_mechanistic = TRUE)",
            "",
        ]
    )
    for col, label in [
        ("eligible_migraine", "Migraine"),
        ("eligible_chronic_back_pain", "Chronic back pain"),
        ("eligible_fibromyalgia", "Fibromyalgia"),
        ("eligible_headache", "Primary headache"),
    ]:
        sub = included[(included[col] == True) & mech_flag]
        lines.append(f"- **{label}:** {len(sub)}")

    lines.extend(["", "### By intervention category (counts; studies may overlap)", ""])
    cat_mech: dict[str, int] = {}
    for _, row in included[mech_flag].iterrows():
        for cat in [c.strip() for c in str(row["intervention_categories"]).split("|") if c.strip()]:
            cat_mech[cat] = cat_mech.get(cat, 0) + 1
    for cat, n in sorted(cat_mech.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{cat}`: {n}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_questionable_exclusions(studies_df: pd.DataFrame, path: Path) -> None:
    excluded = studies_df[studies_df["cohort_included"] != True]
    included = studies_df[studies_df["cohort_included"] == True]

    lines = [
        "# Questionable exclusions and review flags",
        "",
        "Cases that may warrant manual review after classifier fix.",
        "",
    ]

    mech_excl = excluded[excluded["exclusion_stage"] == "mechanism"]
    lines.extend(
        [
            "## Mechanism-stage exclusions (outcome-based)",
            "",
            f"**{len(mech_excl)} studies** — all registered outcomes mechanistic with no "
            "clinical/treatment-relevant outcome among primary, secondary, or other outcomes.",
            "",
        ]
    )
    for _, r in mech_excl.sort_values("nct_id").iterrows():
        lines.append(
            f"- **{r['nct_id']}** — `{r['exclusion_reason']}` | "
            f"{(r['brief_title'] or '')[:70]}"
        )

    mech_prim = included[included["primary_outcome_mechanistic"] == True]
    lines.extend(
        [
            "",
            "## Included with mechanistic primary outcomes",
            "",
            f"**{len(mech_prim)} studies** — treatment-oriented cohort members whose registered "
            "primary outcomes are mechanistic (clinical outcomes may appear in secondary/other).",
            "",
        ]
    )
    for _, r in mech_prim.sort_values("nct_id").head(30).iterrows():
        lines.append(f"- **{r['nct_id']}** | {(r['brief_title'] or '')[:70]}")
    if len(mech_prim) > 30:
        lines.append(f"- … and {len(mech_prim) - 30} more")

    int_excl = excluded[excluded["exclusion_stage"] == "intervention"]
    lines.extend(["", "## Remaining intervention-stage exclusions", "", f"**{len(int_excl)} studies**", ""])
    for _, r in int_excl.sort_values("nct_id").iterrows():
        lines.append(
            f"- **{r['nct_id']}** — `{r['exclusion_reason']}` | {(r['brief_title'] or '')[:70]}"
        )

    cond_border = included[included["condition_eligibility"] == "borderline"]
    lines.extend(["", "## Included condition-borderline cases", "", f"**{len(cond_border)} studies**", ""])
    for _, r in cond_border.sort_values("nct_id").iterrows():
        lines.append(
            f"- **{r['nct_id']}** — `{r['condition_borderline_reason']}` | {(r['brief_title'] or '')[:70]}"
        )

    other_only = included[
        included["intervention_categories"].fillna("").str.fullmatch(r"other_behavioral_treatment")
    ]
    lines.extend(
        [
            "",
            "## Included: other_behavioral_treatment only (catch-all)",
            "",
            f"**{len(other_only)} studies**",
            "",
        ]
    )
    for _, r in other_only.sort_values("nct_id").head(25).iterrows():
        lines.append(f"- **{r['nct_id']}** | {(r['brief_title'] or '')[:70]}")
    if len(other_only) > 25:
        lines.append(f"- … and {len(other_only) - 25} more")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_outcome_other_analysis(outcomes_df: pd.DataFrame, path: Path) -> None:
    inc = outcomes_df[outcomes_df["cohort_included"] == True]
    other = inc[
        (inc["outcome_category"] == "other")
        & (inc["outcome_subcategory"].isin(["other", "uncertain"]))
    ].copy()

    lines = [
        "# Outcome `other` category review",
        "",
        f"Eligible cohort primary outcomes classified as `other` / `other` or `uncertain`: **{len(other)}**",
        "",
        "## Likely misclassification themes",
        "",
    ]

    theme_patterns = {
        "fatigue": r"fatigue|\bfss\b|\bfatigue severity",
        "sleep": r"sleep|insomnia|\bisi\b|psqi",
        "headache_instrument": r"\bhit-6\b|\bhit6\b|\bmidas\b|\bpedmidas\b",
        "medication_use": r"medication|analgesic|rescue med",
        "catastrophizing_missed": r"catastroph|\bpcs\b",
        "anxiety_depression_scale": r"\bphq\b|\bbdi\b|\bhads\b|\bgsi\b|\banxiety|\bdepress",
        "self_efficacy_coping": r"self[- ]efficacy|coping|acceptance|resilience",
        "instrument_name_only": r"^[A-Z]{2,8}[- ]?\d*$|questionnaire|scale score",
        "neuro_mechanistic_missed": r"\beeg\b|\bfmri\b|connectivity|threshold|hrv",
    }
    theme_counts: dict[str, int] = {}
    for theme, pattern in theme_patterns.items():
        mask = other["primary_outcome_measure"].fillna("").str.contains(pattern, case=False, regex=True)
        theme_counts[theme] = int(mask.sum())

    for theme, n in sorted(theme_counts.items(), key=lambda x: (-x[1], x[0])):
        if n:
            lines.append(f"- **{theme}:** {n}")

    lines.extend(["", "## Sample `other` primary outcome measures (top 40 by frequency)", ""])
    for measure, n in other["primary_outcome_measure"].value_counts().head(40).items():
        lines.append(f"- ({n}) {measure}")

    lines.extend(
        [
            "",
            "## Recommended fixes before finalization",
            "",
            "- Expand outcome lexicon for fatigue, sleep, HIT-6/MIDAS, medication-use outcomes.",
            "- Map common instrument-only labels (e.g. BDI, PCS, FSS) via outcome_lexicon instruments.",
            "- Separate mechanistic outcomes into `other/biological_physiological` consistently.",
            "- Review instrument names with no pain/function keyword (e.g. 'Change from baseline').",
            "",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    out = build_revised_cohort()
    print(f"Revised cohort written to {out}")


if __name__ == "__main__":
    main()
