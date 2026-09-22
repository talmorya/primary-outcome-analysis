"""Mechanistic vs clinical treatment outcome classification for cohort eligibility."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


MECHANISTIC_PATTERNS = [
    r"\bfmri\b",
    r"\beeg\b",
    r"\bmri\b",
    r"functional connectivity",
    r"effective connectivity",
    r"neuroimaging",
    r"brain activity",
    r"brain imaging",
    r"neural activity",
    r"neural response",
    r"cerebral blood flow",
    r"arterial spin labeling",
    r"\basl\b",
    r"magnetic resonance spectroscopy",
    r"\bmrs\b",
    r"resting[- ]state",
    r"late positive potential",
    r"error related negativity",
    r"electrophysiol",
    r"cortical map",
    r"motor cortical",
    r"transcranial magnetic stimulation",
    r"\btms\b",
    r"\brtms\b",
    r"dopamine response",
    r"neurotransmitter",
    r"\bbiomarker\b",
    r"inflammation",
    r"cytokine",
    r"\bcortisol\b",
    r"gene expression",
    r"neuroimmune",
    r"heart rate variability",
    r"\bhrv\b",
    r"quantitative sensory",
    r"\bqst\b",
    r"pain threshold",
    r"pain tolerance",
    r"pain summation",
    r"psychophysical",
    r"conditioned pain modulation",
    r"\bcpm\b",
    r"pressure pain",
    r"thermal stimul",
    r"sensory stimul",
    r"hyperalgesia",
    r"attentional bias",
    r"contingency awareness",
    r"pain expectancy",
    r"selective learning",
    r"temporal binding",
    r"psychophysical adaptation",
    r"petco2",
    r"provocation",
    r"experimental pain",
    r"ratings of painful sensory",
    r"inducible dizziness",
    r"point of subjective simultaneity",
    r"psychophysiological",
    r"dataset of functional magnetic",
]

CLINICAL_TREATMENT_PATTERNS = [
    r"pain intensity",
    r"pain severity",
    r"current pain",
    r"average pain",
    r"worst pain",
    r"low back pain intensity",
    r"chronic.*pain",
    r"\bvas\b",
    r"\bnrs\b",
    r"numeric rating scale",
    r"visual analog",
    r"headache day",
    r"migraine day",
    r"headache frequen",
    r"migraine frequen",
    r"attack frequen",
    r"headache intens",
    r"migraine intens",
    r"headache disability",
    r"\bmidas\b",
    r"\bhit-6\b",
    r"\bhit6\b",
    r"\bfiq\b",
    r"fibromyalgia impact",
    r"\bodi\b",
    r"roland[- ]morris",
    r"\brmdq\b",
    r"disability",
    r"pain interference",
    r"\bbpi\b",
    r"brief pain inventory",
    r"\bfunctioning\b",
    r"physical function",
    r"\bpromis\b",
    r"quality of life",
    r"\bqol\b",
    r"\bsf-36\b",
    r"\bsf36\b",
    r"catastroph",
    r"\bpcs\b",
    r"\banxiety\b",
    r"\bdepress",
    r"\bphq\b",
    r"\bbdi\b",
    r"\bdistress\b",
    r"\bstress\b",
    r"medication use",
    r"medication consumption",
    r"global impression",
    r"\bpgic\b",
    r"pain relief",
    r"pain reduction",
    r"body awareness",
    r"\bbarq\b",
    r"mindfulness attention",
    r"\bmaas\b",
    r"\bffmq\b",
    r"self[- ]efficacy",
    r"\bcoping\b",
    r"pain acceptance",
    r"\bfatigue\b",
    r"\bsleep\b",
    r"insomnia",
    r"\bisi\b",
    r"lumbar.*flexion",
    r"expectation of (pain|harm)",
    r"tender point",
    r"appreciation of body",
    r"photophobia",
    r"headache/medication",
    r"\bgait\b",
    r"balance\b",
    r"postural sway",
    r"postural control",
    r"muscle function",
    r"muscle capacity",
    r"muscle strength",
    r"exercise capacity",
    r"exercise performance",
    r"exercise[- ]related",
    r"6[- ]minute walk",
    r"six[- ]minute walk",
    r"chair stand",
    r"biceps curl",
    r"\brepetitions\b",
    r"functional scale",
    r"patient[- ]specific functional",
    r"self[- ]reported pain",
    r"\bvas scale\b",
    r"fibromyalgia impact",
    r"\bfiq\b",
    r"breathing difficulty",
    r"perceived effort",
    r"back[- ]related function",
    r"activities limitation",
    r"physical activity level",
    r"illness perception",
    r"locus of control",
    r"psychological flexibility",
    r"positive affect",
    r"dizziness handicap",
    r"\bdizziness\b",
    r"biobehavioral fibromyalgia",
    r"\bsf-12\b",
    r"\bsf12\b",
]


@dataclass
class OutcomeMechanismAssessment:
    mechanism_excluded: bool
    exclusion_reason: str | None
    primary_outcome_mechanistic: bool
    has_clinical_outcome_anywhere: bool
    all_outcomes_mechanistic: bool


def _outcome_text(
    measure: str | None,
    description: str | None,
    time_frame: str | None = None,
) -> str:
    return " ".join(part for part in [measure or "", description or "", time_frame or ""] if part).lower()


def is_mechanistic_outcome(
    measure: str | None,
    description: str | None,
    time_frame: str | None = None,
) -> bool:
    text = _outcome_text(measure, description, time_frame)
    if not text.strip():
        return False
    if is_clinical_treatment_outcome(measure, description, time_frame):
        return False
    return any(re.search(pattern, text) for pattern in MECHANISTIC_PATTERNS)


def is_clinical_treatment_outcome(
    measure: str | None,
    description: str | None,
    time_frame: str | None = None,
) -> bool:
    text = _outcome_text(measure, description, time_frame)
    if not text.strip():
        return False
    return any(re.search(pattern, text) for pattern in CLINICAL_TREATMENT_PATTERNS)


def extract_all_registered_outcomes(outcomes_mod: dict[str, Any]) -> list[dict[str, str | None]]:
    rows: list[dict[str, str | None]] = []
    for key, outcome_type in (
        ("primaryOutcomes", "primary"),
        ("secondaryOutcomes", "secondary"),
        ("otherOutcomes", "other"),
    ):
        for outcome in outcomes_mod.get(key, []) or []:
            rows.append(
                {
                    "outcome_type": outcome_type,
                    "measure": outcome.get("measure"),
                    "description": outcome.get("description"),
                    "time_frame": outcome.get("timeFrame"),
                }
            )
    return rows


def assess_primary_outcome_mechanistic(primary_outcomes: list[dict[str, str | None]]) -> bool:
    """TRUE only when every non-empty primary outcome is mechanistic and none are clinical."""
    if not primary_outcomes:
        return False
    mechanistic_flags: list[bool] = []
    for outcome in primary_outcomes:
        measure = outcome.get("measure")
        description = outcome.get("description")
        time_frame = outcome.get("time_frame")
        if not _outcome_text(measure, description, time_frame).strip():
            continue
        if is_clinical_treatment_outcome(measure, description, time_frame):
            return False
        mechanistic_flags.append(is_mechanistic_outcome(measure, description, time_frame))
    if not mechanistic_flags:
        return False
    return all(mechanistic_flags)


def evaluate_outcome_mechanism_exclusion(
    all_outcomes: list[dict[str, str | None]],
    *,
    primary_outcomes: list[dict[str, str | None]] | None = None,
) -> OutcomeMechanismAssessment:
    primary_outcomes = primary_outcomes or [
        o for o in all_outcomes if o.get("outcome_type") == "primary"
    ]

    has_clinical = any(
        is_clinical_treatment_outcome(o.get("measure"), o.get("description"), o.get("time_frame"))
        for o in all_outcomes
    )
    mechanistic_flags = [
        is_mechanistic_outcome(o.get("measure"), o.get("description"), o.get("time_frame"))
        for o in all_outcomes
        if _outcome_text(o.get("measure"), o.get("description"), o.get("time_frame")).strip()
    ]
    all_mechanistic = bool(mechanistic_flags) and all(mechanistic_flags)

    primary_outcome_mechanistic = assess_primary_outcome_mechanistic(primary_outcomes)

    if has_clinical:
        return OutcomeMechanismAssessment(
            mechanism_excluded=False,
            exclusion_reason=None,
            primary_outcome_mechanistic=primary_outcome_mechanistic,
            has_clinical_outcome_anywhere=True,
            all_outcomes_mechanistic=all_mechanistic,
        )

    if all_mechanistic:
        return OutcomeMechanismAssessment(
            mechanism_excluded=True,
            exclusion_reason="mechanism_only_outcomes",
            primary_outcome_mechanistic=primary_outcome_mechanistic,
            has_clinical_outcome_anywhere=False,
            all_outcomes_mechanistic=True,
        )

    return OutcomeMechanismAssessment(
        mechanism_excluded=False,
        exclusion_reason=None,
        primary_outcome_mechanistic=primary_outcome_mechanistic,
        has_clinical_outcome_anywhere=False,
        all_outcomes_mechanistic=all_mechanistic,
    )
