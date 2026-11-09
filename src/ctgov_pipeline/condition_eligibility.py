"""Cohort condition eligibility: chronic pain targets and minimal exclusions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .acute_population_screen import AcutePopulationScreenResult, screen_acute_population


@dataclass
class ConditionEligibility:
    targets_in_conditions: list[str]  # target pain conditions found in the registered conditions
    eligibility: str  # eligible | excluded
    exclusion_rule: str | None = None
    exclusion_detail: str | None = None  # why this specific study hit a non-acute rule
    condition_feature_flags: list[str] = field(default_factory=list)
    acute_population_decision: str | None = None
    acute_population_rule: str | None = None
    acute_population_detail: str | None = None
    acute_population_source: str | None = None
    acute_population_snippet: str | None = None


def _compile(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def _matches_any(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(text) for p in patterns)


def _clean(value: str | float | None) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        import math

        if math.isnan(value):
            return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _study_text(
    *,
    conditions: list[str] | None,
    keywords: list[str] | None,
    brief_title: str | None = None,
    official_title: str | None = None,
    intervention_names: str | None = None,
    eligibility_criteria: str | None = None,
) -> str:
    parts = list(conditions or []) + list(keywords or [])
    for item in (brief_title, official_title, intervention_names, eligibility_criteria):
        cleaned = _clean(item)
        if cleaned:
            parts.append(cleaned)
    return " | ".join(parts)


def _detect_targets_in_conditions(
    conditions: list[str] | None, config: dict[str, Any]
) -> list[str]:
    """Targets matched by the registered conditions section alone (each line separately)."""
    lines = [c.strip() for c in (conditions or []) if c and str(c).strip()]
    matched: list[str] = []
    for target, spec in config.get("targets", {}).items():
        patterns = _compile(spec.get("patterns", []))
        if any(_matches_any(line, patterns) for line in lines):
            matched.append(target)
    return matched


def detect_review_flags(
    *,
    brief_title: str | None,
    official_title: str | None,
    config: dict[str, Any],
) -> list[str]:
    """Descriptive review flags from the titles (never used to exclude)."""
    text = " | ".join(t for t in (_clean(brief_title), _clean(official_title)) if t)
    flags: list[str] = []
    for flag_id, spec in config.get("review_flags", {}).items():
        if _matches_any(text, _compile(spec.get("patterns", []))):
            flags.append(flag_id)
    return sorted(flags)


def _first_pattern_hit(text: str, patterns: list[re.Pattern[str]]) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


def _detect_feature_flags(text_lower: str, config: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    for feature_id, spec in config.get("condition_features", {}).items():
        patterns = _compile(spec.get("patterns", []))
        if _matches_any(text_lower, patterns):
            flags.append(feature_id)
    return sorted(flags)


def _attach_acute_fields(result: ConditionEligibility, acute: AcutePopulationScreenResult) -> ConditionEligibility:
    result.acute_population_decision = acute.decision
    result.acute_population_rule = acute.rule
    result.acute_population_detail = acute.detail
    result.acute_population_source = acute.source
    result.acute_population_snippet = acute.snippet
    return result


def evaluate_condition_eligibility(
    *,
    conditions: list[str] | None,
    keywords: list[str] | None,
    config: dict[str, Any],
    brief_title: str | None = None,
    official_title: str | None = None,
    brief_summary: str | None = None,
    eligibility_criteria: str | None = None,
) -> ConditionEligibility:
    text_core = _study_text(
        conditions=conditions,
        keywords=keywords,
        brief_title=brief_title,
        official_title=official_title,
    )
    text_full = _study_text(
        conditions=conditions,
        keywords=keywords,
        brief_title=brief_title,
        official_title=official_title,
        eligibility_criteria=eligibility_criteria,
    )
    text_core_lower = text_core.lower()
    text_full_lower = text_full.lower()

    targets_in_conditions = _detect_targets_in_conditions(conditions, config)

    feature_flags = _detect_feature_flags(text_full_lower, config)

    acute_screen = screen_acute_population(
        conditions=conditions,
        brief_title=brief_title,
        official_title=official_title,
        brief_summary=brief_summary,
        eligibility_criteria=eligibility_criteria,
        config=config,
    )

    for rule_id, spec in config.get("exclusion_rules", {}).items():
        if rule_id == "acute_pain":
            if acute_screen.decision == "exclude":
                return _attach_acute_fields(
                    ConditionEligibility(
                        targets_in_conditions=targets_in_conditions,
                        eligibility="excluded",
                        exclusion_rule=acute_screen.rule or "acute_pain",
                        condition_feature_flags=feature_flags,
                    ),
                    acute_screen,
                )
            continue
        rule_text = text_core_lower if rule_id in {"cancer_oncology", "pathology_other", "pregnancy_related"} else text_full_lower
        hit = _first_pattern_hit(rule_text, _compile(spec.get("patterns", [])))
        if hit:
            return _attach_acute_fields(
                ConditionEligibility(
                    targets_in_conditions=targets_in_conditions,
                    eligibility="excluded",
                    exclusion_rule=rule_id,
                    exclusion_detail=(
                        f"Matched '{hit}' in registered conditions, keywords or titles."
                    ),
                    condition_feature_flags=feature_flags,
                ),
                acute_screen,
            )

    if not targets_in_conditions:
        return _attach_acute_fields(
            ConditionEligibility(
                targets_in_conditions=[],
                eligibility="excluded",
                exclusion_rule="no_target_match",
                exclusion_detail=(
                    "No target pattern (migraine, back pain, fibromyalgia, headache) "
                    "matched the registered conditions."
                ),
                condition_feature_flags=feature_flags,
            ),
            acute_screen,
        )

    return _attach_acute_fields(
        ConditionEligibility(
            targets_in_conditions=targets_in_conditions,
            eligibility="eligible",
            condition_feature_flags=feature_flags,
        ),
        acute_screen,
    )
