"""Hierarchical outcome category classification."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class OutcomeCategory:
    outcome_category: str
    outcome_subcategory: str
    rule: str
    review_flag: bool = False


def _text(measure: str | None, description: str | None, time_frame: str | None) -> str:
    return " ".join(part for part in [measure or "", description or "", time_frame or ""] if part).lower()


def classify_outcome_category(
    measure: str | None,
    description: str | None,
    time_frame: str | None,
) -> OutcomeCategory:
    text = _text(measure, description, time_frame)

    rules: list[tuple[str, str, str, list[str]]] = [
        (
            "feasibility_acceptability",
            "safety",
            "CAT_FEAS_SAFETY",
            [r"\badverse\b", r"\bsafety\b", r"side effect", r"tolerability", r"serious adverse"],
        ),
        (
            "feasibility_acceptability",
            "feasibility_recruitment",
            "CAT_FEAS_RECRUITMENT",
            [
                r"\bfeasibility\b",
                r"\brecruitment\b",
                r"\benrollment\b",
                r"\baccrual\b",
                r"screening rate",
                r"eligibility rate",
            ],
        ),
        (
            "feasibility_acceptability",
            "acceptability_satisfaction",
            "CAT_FEAS_ACCEPTABILITY",
            [
                r"\bacceptability\b",
                r"\bsatisfaction\b",
                r"\busability\b",
                r"user experience",
                r"participant experience",
            ],
        ),
        (
            "feasibility_acceptability",
            "adherence_fidelity",
            "CAT_FEAS_ADHERENCE",
            [
                r"\badherence\b",
                r"\bcompliance\b",
                r"\bfidelity\b",
                r"protocol adherence",
                r"therapist adherence",
                r"treatment integrity",
            ],
        ),
        (
            "feasibility_acceptability",
            "other_feasibility",
            "CAT_FEAS_OTHER",
            [r"retention rate", r"drop[- ]?out rate", r"completion rate"],
        ),
        (
            "mood",
            "anxiety",
            "CAT_MOOD_ANXIETY",
            [r"\banxiety\b", r"\bpanic\b", r"state[- ]trait anxiety", r"\bgsi\b", r"\bbai\b"],
        ),
        (
            "mood",
            "depression",
            "CAT_MOOD_DEPRESSION",
            [r"\bdepress", r"\bphq", r"\bbeck depression", r"\bces-d\b", r"\bham-d\b"],
        ),
        (
            "mood",
            "catastrophizing",
            "CAT_MOOD_CATASTROPHIZING",
            [r"catastroph", r"\bpcs\b"],
        ),
        (
            "mood",
            "distress_stress",
            "CAT_MOOD_DISTRESS",
            [r"\bdistress\b", r"\bstress\b", r"\bmood\b", r"emotional distress", r"psychological stress"],
        ),
        (
            "pain_interference",
            "disability",
            "CAT_INTERFERE_DISABILITY",
            [
                r"\bdisability\b",
                r"\bfunctional\b",
                r"\bfunctioning\b",
                r"activities of daily living",
                r"\badl\b",
                r"\bfiq\b",
                r"fibromyalgia impact",
                r"\bpdih\b",
                r"\bpdii\b",
                r"\bodi\b",
                r"roland[- ]morris",
                r"rmdq",
            ],
        ),
        (
            "pain_interference",
            "work_participation",
            "CAT_INTERFERE_WORK",
            [r"return to work", r"work ability", r"work productivity", r"sick leave", r"presenteeism"],
        ),
        (
            "pain_interference",
            "coping_adaptation",
            "CAT_INTERFERE_COPING",
            [r"\bcoping\b", r"self[- ]efficacy", r"pain acceptance", r"adaptation", r"resilience"],
        ),
        (
            "pain_interference",
            "quality_of_life",
            "CAT_INTERFERE_QOL",
            [r"quality of life", r"\bqol\b", r"\bsf-36\b", r"\bsf36\b", r"\bpromis\b", r"health[- ]related quality"],
        ),
        (
            "pain_interference",
            "interference",
            "CAT_INTERFERE_GENERAL",
            [r"interference", r"interfering", r"impact on", r"life impact"],
        ),
        (
            "pain_recovery",
            "pain_intensity",
            "CAT_PAIN_INTENSITY",
            [
                r"pain intensity",
                r"pain severity",
                r"pain score",
                r"pain level",
                r"average pain",
                r"worst pain",
                r"current pain",
                r"\bvas\b",
                r"\bnrs\b",
                r"numeric rating",
                r"visual analog",
            ],
        ),
        (
            "pain_recovery",
            "pain_frequency",
            "CAT_PAIN_FREQUENCY",
            [
                r"headache frequency",
                r"migraine frequency",
                r"headache days",
                r"migraine days",
                r"number of headache",
                r"attack frequency",
                r"episodes per",
            ],
        ),
        (
            "pain_recovery",
            "global_impression",
            "CAT_PAIN_GLOBAL",
            [
                r"global impression",
                r"\bcgis\b",
                r"\bpgic\b",
                r"patient global",
                r"clinician global",
                r"overall improvement",
                r"pain relief",
                r"pain reduction",
            ],
        ),
        (
            "pain_recovery",
            "general_pain",
            "CAT_PAIN_GENERAL",
            [
                r"\bpain\b",
                r"\bheadache\b",
                r"\bmigraine\b",
                r"\bsymptom",
                r"photophobia",
                r"headache disability",
            ],
        ),
        (
            "other",
            "biological_physiological",
            "CAT_OTHER_BIOLOGICAL",
            [
                r"\beeg\b",
                r"\bfmri\b",
                r"\bmri\b",
                r"heart rate variability",
                r"\bhrv\b",
                r"biomarker",
                r"cortisol",
                r"neuroimaging",
                r"pressure pain threshold",
                r"pain threshold",
                r"quantitative sensory",
            ],
        ),
    ]

    for category, subcategory, rule_id, patterns in rules:
        if any(re.search(pattern, text) for pattern in patterns):
            return OutcomeCategory(
                outcome_category=category,
                outcome_subcategory=subcategory,
                rule=rule_id,
            )

    if len(text.strip()) < 8:
        return OutcomeCategory(
            outcome_category="other",
            outcome_subcategory="uncertain",
            rule="CAT_OTHER_UNCERTAIN",
            review_flag=True,
        )

    return OutcomeCategory(
        outcome_category="other",
        outcome_subcategory="other",
        rule="CAT_OTHER",
        review_flag=True,
    )
