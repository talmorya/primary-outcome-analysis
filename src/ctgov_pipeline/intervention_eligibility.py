"""Intervention and treatment-vs-mechanism eligibility for revised cohort."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .classify_intervention_categories import InterventionCategoryResult
from .outcome_mechanism import (
    OutcomeMechanismAssessment,
    evaluate_outcome_mechanism_exclusion,
    extract_all_registered_outcomes,
)


@dataclass
class InterventionEligibility:
    intervention_eligible: bool
    exclusion_reason: str | None = None


@dataclass
class MechanismEligibility:
    mechanism_excluded: bool
    exclusion_reason: str | None = None
    primary_outcome_mechanistic: bool = False
    has_clinical_outcome_anywhere: bool = False
    all_outcomes_mechanistic: bool = False


def evaluate_intervention_eligibility(
    classification: InterventionCategoryResult,
) -> InterventionEligibility:
    if not classification.has_behavioral_arm:
        return InterventionEligibility(
            intervention_eligible=False,
            exclusion_reason="no_behavioral_arm",
        )

    if not classification.intervention_categories:
        if classification.has_mechanism_arm and not classification.has_control_arm:
            return InterventionEligibility(
                intervention_eligible=False,
                exclusion_reason="mechanism_arms_only",
            )
        if classification.has_control_arm and not classification.has_mechanism_arm:
            return InterventionEligibility(
                intervention_eligible=False,
                exclusion_reason="control_arms_only",
            )
        return InterventionEligibility(
            intervention_eligible=False,
            exclusion_reason="no_treatment_behavioral_arm",
        )

    return InterventionEligibility(intervention_eligible=True)


def evaluate_mechanism_exclusion(
    *,
    classification: InterventionCategoryResult,
    record: dict[str, Any] | None = None,
) -> MechanismEligibility:
    if classification.has_mechanism_arm and not classification.intervention_categories:
        return MechanismEligibility(
            mechanism_excluded=True,
            exclusion_reason="mechanism_arms_only",
        )

    if record is None:
        return MechanismEligibility(mechanism_excluded=False)

    outcomes_mod = record.get("protocolSection", {}).get("outcomesModule", {}) or {}
    all_outcomes = extract_all_registered_outcomes(outcomes_mod)
    assessment = evaluate_outcome_mechanism_exclusion(all_outcomes)

    return MechanismEligibility(
        mechanism_excluded=assessment.mechanism_excluded,
        exclusion_reason=assessment.exclusion_reason,
        primary_outcome_mechanistic=assessment.primary_outcome_mechanistic,
        has_clinical_outcome_anywhere=assessment.has_clinical_outcome_anywhere,
        all_outcomes_mechanistic=assessment.all_outcomes_mechanistic,
    )
