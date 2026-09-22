"""Proposed condition eligibility with QC exclusion rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .match_conditions import match_conditions


@dataclass
class ConditionEligibility:
    targets_detected: list[str]
    targets_eligible: list[str]
    eligibility: str  # eligible | excluded | borderline
    exclusion_rule: str | None = None
    borderline_reason: str | None = None
    review_flag: bool = False


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
) -> str:
    parts = list(conditions or []) + list(keywords or [])
    for item in (brief_title, official_title, intervention_names):
        cleaned = _clean(item)
        if cleaned:
            parts.append(cleaned)
    return " | ".join(parts)


def _population_primary_mismatch(
    *,
    conditions: list[str] | None,
    brief_title: str | None = None,
    official_title: str | None = None,
    config: dict[str, Any],
) -> str | None:
    """Exclude when an off-target disorder is the primary population, not a co-listed target."""
    cond_list = [c.strip() for c in (conditions or []) if c and str(c).strip()]
    if not cond_list:
        return None

    first_lower = cond_list[0].lower()
    title_text = " ".join(
        part for part in (_clean(brief_title), _clean(official_title)) if part
    ).lower()
    title_has_target = bool(
        re.search(
            r"fibromyalgia|migraine|chronic (low )?back pain|low back pain|\bclbp\b|\blbp\b|headache",
            title_text,
        )
    )
    target_in_top3 = any(
        re.search(
            r"fibromyalgia|migraine|chronic (low )?back|low back pain|\bclbp\b|\blbp\b",
            cond_list[i].lower(),
        )
        for i in range(min(3, len(cond_list)))
    )

    off_target_first_patterns = _compile(
        config.get("population_primary_excludes", {}).get("off_target_first_condition", {}).get(
            "patterns",
            [
                r"me/cfs",
                r"myalgic encephalomyelitis",
                r"chronic fatigue syndrome",
                r"long covid",
                r"post[- ]covid",
                r"postural orthostatic tachycardia",
                r"\bpots\b",
            ],
        )
    )
    if _matches_any(first_lower, off_target_first_patterns) and not target_in_top3 and not title_has_target:
        return "off_target_primary_population"

    return None


def evaluate_condition_eligibility(
    *,
    conditions: list[str] | None,
    keywords: list[str] | None,
    config: dict[str, Any],
    brief_title: str | None = None,
    official_title: str | None = None,
    intervention_names: str | None = None,
    force_headache_include: bool = False,
) -> ConditionEligibility:
    text = _study_text(
        conditions=conditions,
        keywords=keywords,
        brief_title=brief_title,
        official_title=official_title,
        intervention_names=intervention_names,
    )
    text_lower = text.lower()

    match = match_conditions(conditions, keywords, config)
    targets_detected = list(match.matched_targets)

    if force_headache_include and "primary_headache" not in targets_detected:
        targets_detected.append("primary_headache")

    # Global exclusions apply even when no target matched (e.g. post-concussive headache only).
    for rule_id, spec in config.get("global_excludes", {}).items():
        target_scope = spec.get("target")
        patterns = _compile(spec.get("patterns", []))
        if not _matches_any(text_lower, patterns):
            continue
        if target_scope and target_scope not in targets_detected:
            continue
        if rule_id == "acute_lbp_only" and re.search(r"chronic", text_lower):
            continue
        return ConditionEligibility(
            targets_detected=targets_detected,
            targets_eligible=[],
            eligibility="excluded",
            exclusion_rule=rule_id,
            review_flag=True,
        )

    if not targets_detected and not force_headache_include:
        return ConditionEligibility(
            targets_detected=[],
            targets_eligible=[],
            eligibility="excluded",
            exclusion_rule="no_target_match",
            review_flag=match.review_flag,
        )

    population_exclude = _population_primary_mismatch(
        conditions=conditions,
        brief_title=brief_title,
        official_title=official_title,
        config=config,
    )
    if population_exclude:
        return ConditionEligibility(
            targets_detected=targets_detected,
            targets_eligible=[],
            eligibility="excluded",
            exclusion_rule=population_exclude,
            review_flag=True,
        )

    # Headache-specific exclusions (only when primary_headache is in play)
    if "primary_headache" in targets_detected or force_headache_include:
        if re.search(r"migraine", text_lower):
            targets_detected = [t for t in targets_detected if t != "primary_headache"]
        else:
            for rule_id, spec in config.get("headache_excludes", {}).items():
                patterns = _compile(spec.get("patterns", []))
                if _matches_any(text_lower, patterns):
                    return ConditionEligibility(
                        targets_detected=targets_detected,
                        targets_eligible=[],
                        eligibility="excluded",
                        exclusion_rule=f"headache_{rule_id}",
                        review_flag=True,
                    )

    eligible = list(targets_detected)
    if "primary_headache" in eligible and re.search(r"migraine", text_lower):
        eligible = [t for t in eligible if t != "primary_headache"]

    borderline_reason = None
    for rule_id, spec in config.get("borderline_rules", {}).items():
        target = spec.get("target")
        if target not in eligible:
            continue
        patterns = _compile(spec.get("patterns", []))
        if not _matches_any(text_lower, patterns):
            continue
        skip = False
        for ex in spec.get("exclude_if", []):
            conds = [c.strip().lower() for c in (conditions or [])]
            if any(re.fullmatch(ex, c, re.I) for c in conds):
                skip = True
                break
        if not skip:
            borderline_reason = rule_id

    if not eligible:
        return ConditionEligibility(
            targets_detected=targets_detected,
            targets_eligible=[],
            eligibility="excluded",
            exclusion_rule="headache_migraine_only_or_removed",
            review_flag=True,
        )

    if borderline_reason:
        return ConditionEligibility(
            targets_detected=targets_detected,
            targets_eligible=eligible,
            eligibility="borderline",
            borderline_reason=borderline_reason,
            review_flag=True,
        )

    return ConditionEligibility(
        targets_detected=targets_detected,
        targets_eligible=eligible,
        eligibility="eligible",
        review_flag=match.review_flag,
    )
