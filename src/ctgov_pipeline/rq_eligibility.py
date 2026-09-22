"""Research-question eligibility layer (psych/behavioral intervention focus)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

# Manual overrides from QC review (headache expansion + flagged cohort studies).
RQ_OVERRIDES: dict[str, tuple[str, str]] = {
    "NCT01664585": ("rq_exclude", "Exercise-only intervention; no psych behavioral component"),
    "NCT00181064": ("rq_exclude", "Diet-only intervention (Modified Atkins)"),
    "NCT00267618": ("rq_exclude", "Primary outcomes psychiatric (KSADS); dual headache/abdominal focus"),
    "NCT03308630": ("rq_exclude", "Primary outcome is stress, not headache"),
    "NCT03166358": ("rq_borderline", "Yoga-only; no psych taxonomy tag"),
    "NCT06631222": ("rq_borderline", "CBT present but primary outcome is pressure algometry"),
    "NCT06041997": ("rq_borderline", "Smartphone restriction; other_psychological only"),
}


@dataclass
class RqEligibility:
    rq_eligibility: str  # rq_eligible | rq_borderline | rq_exclude
    rq_reason: str


def _as_str(value: str | float | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def evaluate_rq_eligibility(
    *,
    nct_id: str,
    behavioral_component: str | None,
    non_psychological_behavioral_flag: bool,
    non_psychological_behavioral_type: str | None,
    condition_eligibility: str,
    brief_title: str | None = None,
    intervention_names: str | None = None,
    intervention_classification_rule: str | None = None,
) -> RqEligibility:
    if nct_id in RQ_OVERRIDES:
        status, reason = RQ_OVERRIDES[nct_id]
        return RqEligibility(rq_eligibility=status, rq_reason=reason)

    if condition_eligibility == "excluded":
        return RqEligibility(
            rq_eligibility="rq_exclude",
            rq_reason="Condition eligibility excluded",
        )

    bc = _as_str(behavioral_component)
    bc_parts = [p.strip() for p in bc.split("|") if p.strip()] if bc else []
    non_psych_type = _as_str(non_psychological_behavioral_type)

    if "research_paradigm" in non_psych_type and not bc_parts:
        return RqEligibility(
            rq_eligibility="rq_exclude",
            rq_reason="Research paradigm / lab task (non_psychological_behavioral)",
        )

    if not bc_parts:
        if non_psychological_behavioral_flag:
            return RqEligibility(
                rq_eligibility="rq_exclude",
                rq_reason="Non-psychological behavioral only (e.g. exercise/diet/lifestyle)",
            )
        return RqEligibility(
            rq_eligibility="rq_exclude",
            rq_reason="No identifiable psychological behavioral_component",
        )

    if bc_parts == ["other_psychological"]:
        rules = _as_str(intervention_classification_rule)
        if "APP_OTHER_PSYCHOLOGICAL" in rules:
            return RqEligibility(
                rq_eligibility="rq_eligible",
                rq_reason="Identifiable psychological/behavioral behavioral_component",
            )
        return RqEligibility(
            rq_eligibility="rq_borderline",
            rq_reason="Catch-all other_psychological classification only",
        )

    if non_psychological_behavioral_flag and bc_parts:
        text = f"{_as_str(brief_title)} {_as_str(intervention_names)}".lower()
        if re.search(r"exercise|walk with ease|yoga|diet|atkins|physiotherapy", text):
            return RqEligibility(
                rq_eligibility="rq_borderline",
                rq_reason="Multimodal trial with psych component plus prominent non-psych modality",
            )

    return RqEligibility(
        rq_eligibility="rq_eligible",
        rq_reason="Identifiable psychological/behavioral behavioral_component",
    )
