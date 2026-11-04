"""Cohort condition eligibility: chronic pain targets and minimal exclusions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .acute_population_screen import AcutePopulationScreenResult, screen_acute_population
from .match_conditions import match_conditions


@dataclass
class ConditionEligibility:
    targets_detected: list[str]
    targets_eligible: list[str]
    eligibility: str  # eligible | excluded
    exclusion_rule: str | None = None
    exclusion_detail: str | None = None  # why this specific study hit a non-acute rule
    condition_feature_flags: list[str] = field(default_factory=list)
    review_flag: bool = False
    acute_population_decision: str | None = None
    acute_population_rule: str | None = None
    acute_population_detail: str | None = None
    acute_population_source: str | None = None
    acute_population_snippet: str | None = None


# "Chronic Pain" and the MeSH-style inversion "Pain, Chronic".
_GENERIC_CHRONIC_PAIN = re.compile(r"^(?:chronic\s+pain|pain\s*,\s*chronic)$", re.IGNORECASE)


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


def _target_match_text(
    *,
    conditions: list[str] | None,
    keywords: list[str] | None,
    brief_title: str | None = None,
    official_title: str | None = None,
) -> str:
    parts = list(conditions or []) + list(keywords or [])
    for item in (brief_title, official_title):
        cleaned = _clean(item)
        if cleaned:
            parts.append(cleaned)
    return " | ".join(parts)


def _detect_targets(
    *,
    conditions: list[str] | None,
    keywords: list[str] | None,
    config: dict[str, Any],
    brief_title: str | None = None,
    official_title: str | None = None,
) -> list[str]:
    text = _target_match_text(
        conditions=conditions,
        keywords=keywords,
        brief_title=brief_title,
        official_title=official_title,
    )
    if not text.strip():
        return []
    compiled = {
        target: _compile(spec.get("patterns", []))
        for target, spec in config.get("targets", {}).items()
    }
    matched: list[str] = []
    for target, patterns in compiled.items():
        if any(p.search(text) for p in patterns):
            matched.append(target)
    return matched


def _condition_line_is_target(line: str, config: dict[str, Any]) -> bool:
    text = line.strip()
    if not text:
        return False
    compiled = {
        target: _compile(spec.get("patterns", []))
        for target, spec in config.get("targets", {}).items()
    }
    for patterns in compiled.values():
        if _matches_any(text, patterns):
            return True
    return False


def _is_ignored_non_target_condition(line: str) -> bool:
    return bool(_GENERIC_CHRONIC_PAIN.match(line.strip()))


def _population_non_target_conditions(
    *,
    conditions: list[str] | None,
    config: dict[str, Any],
) -> list[str]:
    """Non-target registered conditions when they reach the exclusion threshold, else []."""
    cond_list = [c.strip() for c in (conditions or []) if c and str(c).strip()]
    if not cond_list:
        return []
    non_target = [
        c
        for c in cond_list
        if not _condition_line_is_target(c, config) and not _is_ignored_non_target_condition(c)
    ]
    threshold = int(
        config.get("population_mismatch", {}).get("min_non_target_conditions", 3)
    )
    return non_target if len(non_target) >= threshold else []


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

    targets_detected = _detect_targets(
        conditions=conditions,
        keywords=keywords,
        config=config,
        brief_title=brief_title,
        official_title=official_title,
    )
    match = match_conditions(conditions, keywords, config)
    review_flag = match.review_flag
    if not targets_detected and (brief_title or official_title):
        review_flag = True
    elif targets_detected and match.review_flag:
        review_flag = True

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
                        targets_detected=targets_detected,
                        targets_eligible=[],
                        eligibility="excluded",
                        exclusion_rule=acute_screen.rule or "acute_pain",
                        condition_feature_flags=feature_flags,
                        review_flag=True,
                    ),
                    acute_screen,
                )
            continue
        rule_text = text_core_lower if rule_id in {"cancer_oncology", "pathology_other"} else text_full_lower
        hit = _first_pattern_hit(rule_text, _compile(spec.get("patterns", [])))
        if hit:
            return _attach_acute_fields(
                ConditionEligibility(
                    targets_detected=targets_detected,
                    targets_eligible=[],
                    eligibility="excluded",
                    exclusion_rule=rule_id,
                    exclusion_detail=(
                        f"Matched '{hit}' in registered conditions, keywords, titles or "
                        "intervention names."
                    ),
                    condition_feature_flags=feature_flags,
                    review_flag=True,
                ),
                acute_screen,
            )

    if not targets_detected:
        return _attach_acute_fields(
            ConditionEligibility(
                targets_detected=[],
                targets_eligible=[],
                eligibility="excluded",
                exclusion_rule="no_target_match",
                exclusion_detail=(
                    "No target pattern (migraine, chronic back pain, fibromyalgia, headache) "
                    "matched conditions, keywords or titles."
                ),
                condition_feature_flags=feature_flags,
                review_flag=review_flag,
            ),
            acute_screen,
        )

    non_target = _population_non_target_conditions(conditions=conditions, config=config)
    if non_target:
        return _attach_acute_fields(
            ConditionEligibility(
                targets_detected=targets_detected,
                targets_eligible=[],
                eligibility="excluded",
                exclusion_rule="population_non_target_conditions",
                exclusion_detail=(
                    f"{len(non_target)} registered conditions are not target pain conditions: "
                    + "; ".join(non_target)
                ),
                condition_feature_flags=feature_flags,
                review_flag=True,
            ),
            acute_screen,
        )

    eligible = list(targets_detected)
    if "headache" in eligible and re.search(r"migraine", text_full_lower):
        eligible = [t for t in eligible if t != "headache"]

    if not eligible:
        return _attach_acute_fields(
            ConditionEligibility(
                targets_detected=targets_detected,
                targets_eligible=[],
                eligibility="excluded",
                exclusion_rule="no_eligible_target_after_migraine_overlap",
                exclusion_detail=(
                    "Only the generic headache target matched and the text mentions migraine, "
                    "so the headache label was dropped and no target remained."
                ),
                condition_feature_flags=feature_flags,
                review_flag=True,
            ),
            acute_screen,
        )

    return _attach_acute_fields(
        ConditionEligibility(
            targets_detected=targets_detected,
            targets_eligible=eligible,
            eligibility="eligible",
            condition_feature_flags=feature_flags,
            review_flag=review_flag,
        ),
        acute_screen,
    )
