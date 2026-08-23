"""Rule-based outcome purpose tagging (not conceptual pain-domain classification)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class OutcomePurpose:
    purpose: str
    rule: str
    review_flag: bool


def _text(measure: str | None, description: str | None, time_frame: str | None) -> str:
    return " ".join(part for part in [measure or "", description or "", time_frame or ""] if part).lower()


def classify_outcome_purpose(
    measure: str | None,
    description: str | None,
    time_frame: str | None,
) -> OutcomePurpose:
    text = _text(measure, description, time_frame)

    rules: list[tuple[str, str, list[str], bool]] = [
        (
            "safety_adverse_events",
            "PURPOSE_SAFETY",
            [r"\badverse\b", r"\bsafety\b", r"side effect", r"tolerability"],
            False,
        ),
        (
            "feasibility_recruitment",
            "PURPOSE_FEASIBILITY",
            [
                r"\bfeasibility\b",
                r"\brecruitment\b",
                r"\benrollment\b",
                r"\beligibility\b",
                r"screening rate",
                r"accrual",
            ],
            False,
        ),
        (
            "acceptability_satisfaction",
            "PURPOSE_ACCEPTABILITY",
            [
                r"\bacceptability\b",
                r"\bsatisfaction\b",
                r"\busability\b",
                r"user experience",
                r"participant experience",
            ],
            False,
        ),
        (
            "treatment_fidelity",
            "PURPOSE_FIDELITY",
            [r"\bfidelity\b", r"protocol adherence", r"therapist adherence", r"treatment integrity"],
            False,
        ),
        (
            "biological_physiological",
            "PURPOSE_BIOLOGICAL",
            [
                r"\beeg\b",
                r"\bfmri\b",
                r"\bmri\b",
                r"heart rate variability",
                r"\bhrv\b",
                r"electrophysiolog",
                r"biomarker",
                r"cortisol",
                r"neuroimaging",
                r"cortical electrical",
            ],
            False,
        ),
        (
            "functional",
            "PURPOSE_FUNCTIONAL",
            [
                r"\bfunctioning\b",
                r"\bfunctional\b",
                r"\bdisability\b",
                r"activities of daily living",
                r"\badl\b",
                r"return to work",
                r"work ability",
            ],
            False,
        ),
        (
            "psychological",
            "PURPOSE_PSYCHOLOGICAL",
            [
                r"\banxiety\b",
                r"\bdepression\b",
                r"\bdistress\b",
                r"catastroph",
                r"\bstress\b",
                r"\bmood\b",
                r"emotional distress",
                r"psychological stress",
            ],
            False,
        ),
        (
            "therapeutic_clinical",
            "PURPOSE_THERAPEUTIC",
            [
                r"\bpain\b",
                r"pain intensity",
                r"pain severity",
                r"pain relief",
                r"quality of life",
                r"\bheadache\b",
                r"\bmigraine\b",
                r"global impression",
                r"\bsymptom",
            ],
            False,
        ),
    ]

    for purpose, rule_id, patterns, review in rules:
        if any(re.search(pattern, text) for pattern in patterns):
            return OutcomePurpose(purpose=purpose, rule=rule_id, review_flag=review)

    if len(text.strip()) < 8:
        return OutcomePurpose(purpose="uncertain", rule="PURPOSE_UNCERTAIN_SHORT", review_flag=True)

    return OutcomePurpose(purpose="other", rule="PURPOSE_OTHER", review_flag=True)
