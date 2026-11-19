"""Cohort condition eligibility: one ordered list of simple exclusion rules.

Each rule is a small function returning a `_Hit` (rule key + reason) or None. The first rule
that fires decides; see `evaluate_condition_eligibility` for the order and
`docs/COHORT_FILTERING_RULES.md` for the rationale of each rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from .acute_population_screen import find_acute_population
from .eligibility_text import extract_inclusion_blocks, find_chronic_inclusion_cue, find_short_pain_window


@dataclass
class ConditionEligibility:
    targets_in_conditions: list[str]  # target pain conditions found in the registered conditions
    eligibility: str  # eligible | excluded
    exclusion_rule: str | None = None
    exclusion_detail: str | None = None  # why this specific study hit the rule
    condition_feature_flags: list[str] = field(default_factory=list)
    exclusion_source: str | None = None  # where the matched text was found (text-based rules)
    exclusion_snippet: str | None = None  # the matched text


class _Hit(NamedTuple):
    rule: str
    detail: str
    source: str | None = None
    snippet: str | None = None


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


def _all_conditions_chronic(conditions: list[str] | None) -> bool:
    """True when every registered condition line contains the word 'chronic'."""
    lines = [str(c).strip() for c in (conditions or []) if str(c).strip()]
    return bool(lines) and all(re.search(r"\bchronic\b", line, re.IGNORECASE) for line in lines)


# --- Rules (each returns a _Hit or None) ---------------------------------------------------------


def _keyword_rule(rule_id: str, text_lower: str, config: dict[str, Any]) -> _Hit | None:
    """cancer_oncology / pathology_other / pregnancy_related: pattern in conditions, keywords, titles."""
    patterns = _compile(config["exclusion_rules"][rule_id]["patterns"])
    hit = _first_pattern_hit(text_lower, patterns)
    if hit:
        return _Hit(rule_id, f"Matched '{hit}' in registered conditions, keywords or titles.")
    return None


def _acute_pain_rule(*, conditions, brief_title, official_title, brief_summary, eligibility_criteria, config) -> _Hit | None:
    """The word 'acute' describes the enrolled population (details: acute_population_screen)."""
    found = find_acute_population(
        conditions=conditions,
        brief_title=brief_title,
        official_title=official_title,
        brief_summary=brief_summary,
        eligibility_criteria=eligibility_criteria,
        # Titles/summary/conditions are ignored when every registered condition says "chronic".
        check_descriptors=not _all_conditions_chronic(conditions),
        config=config,
    )
    if found:
        source, snippet = found
        return _Hit("acute_pain", "Acute pain population", source, snippet)
    return None


def _subacute_perioperative_rule(
    *, feature_flags: list[str], eligibility_criteria: str | None, config: dict[str, Any]
) -> _Hit | None:
    """Subacute / perioperative / postoperative feature flag.

    Only `surgical_postoperative` can be overridden: it is kept when the inclusion criteria show
    established chronic pain, unless they also say "acute"/"subacute".
    """
    spec = config["flag_exclusion"]
    flags = [f for f in spec["flags"] if f in feature_flags]
    if not flags:
        return None
    keep = spec["keep_when_chronic_in_inclusion"]
    blocking = [f for f in flags if f not in keep["flags"]]  # flags that can never be overridden
    note = ""
    if not blocking:
        chronic_cue = find_chronic_inclusion_cue(
            eligibility_criteria,
            word_patterns=keep["word_patterns"],
            duration_patterns=keep["duration_patterns"],
        )
        acute_wording = _first_pattern_hit(
            " ".join(extract_inclusion_blocks(eligibility_criteria)),
            _compile(keep["unless_inclusion_mentions"]),
        )
        if chronic_cue and not acute_wording:
            return None
        if chronic_cue:
            note = f" Chronic cue ignored: the inclusion criteria also say '{acute_wording}'."
    blocking = blocking or flags
    return _Hit(
        spec["rule"],
        "Subacute or peri/pre/post-operative population "
        f"(condition_feature_flags: {', '.join(blocking)}); chronification prevention is out of scope." + note,
    )


def _short_pain_window_rule(
    *, conditions: list[str] | None, eligibility_criteria: str | None, config: dict[str, Any]
) -> _Hit | None:
    """An inclusion sentence about pain/symptoms states a window under 12 weeks."""
    spec = config["short_pain_window"]
    sentence = find_short_pain_window(eligibility_criteria, spec)
    if not sentence or _all_conditions_chronic(conditions):
        return None
    return _Hit(
        spec["rule"],
        "Explicit pain/symptom window under 12 weeks in the inclusion criteria",
        "inclusion criteria",
        sentence[:300],
    )


def _no_target_rule(targets_in_conditions: list[str]) -> _Hit | None:
    if targets_in_conditions:
        return None
    return _Hit(
        "no_target_match",
        "No target pattern (migraine, back pain, fibromyalgia, headache) matched the registered conditions.",
    )


def _not_about_pain_rule(
    *,
    titles: str,
    eligibility_criteria: str | None,
    primary_outcome_text: str | None,
    config: dict[str, Any],
) -> _Hit | None:
    """No pain word anywhere in titles + inclusion criteria + primary outcomes.

    Skipped when the inclusion criteria or primary outcomes are empty.
    """
    inclusion = " ".join(extract_inclusion_blocks(eligibility_criteria)).strip()
    outcomes = (primary_outcome_text or "").strip()
    if not inclusion or not outcomes:
        return None
    scope = f"{titles} {inclusion} {outcomes}"
    if _first_pattern_hit(scope, _compile(config["not_about_pain"]["pain_wording_patterns"])):
        return None
    return _Hit(
        config["not_about_pain"]["rule"],
        "No pain wording in the titles, inclusion criteria or primary outcomes.",
    )


def evaluate_condition_eligibility(
    *,
    conditions: list[str] | None,
    keywords: list[str] | None,
    config: dict[str, Any],
    brief_title: str | None = None,
    official_title: str | None = None,
    brief_summary: str | None = None,
    eligibility_criteria: str | None = None,
    primary_outcome_text: str | None = None,
) -> ConditionEligibility:
    text_core = _study_text(
        conditions=conditions, keywords=keywords, brief_title=brief_title, official_title=official_title
    ).lower()
    # Feature flags (subacute / perioperative / ...) are searched in conditions, keywords, titles
    # and the INCLUSION criteria only: exclusion criteria describe who is kept out, not who is enrolled.
    text_flags = _study_text(
        conditions=conditions,
        keywords=keywords,
        brief_title=brief_title,
        official_title=official_title,
        eligibility_criteria=" ".join(extract_inclusion_blocks(eligibility_criteria)),
    ).lower()
    targets = _detect_targets_in_conditions(conditions, config)
    flags = _detect_feature_flags(text_flags, config)
    titles = " ".join(x for x in (_clean(brief_title), _clean(official_title)) if x)

    # The first rule that fires decides. This list IS the rule order.
    hit = (
        _keyword_rule("cancer_oncology", text_core, config)
        or _keyword_rule("pathology_other", text_core, config)
        or _keyword_rule("pregnancy_related", text_core, config)
        or _acute_pain_rule(
            conditions=conditions,
            brief_title=brief_title,
            official_title=official_title,
            brief_summary=brief_summary,
            eligibility_criteria=eligibility_criteria,
            config=config,
        )
        or _subacute_perioperative_rule(
            feature_flags=flags, eligibility_criteria=eligibility_criteria, config=config
        )
        or _short_pain_window_rule(
            conditions=conditions, eligibility_criteria=eligibility_criteria, config=config
        )
        or _no_target_rule(targets)
        or _not_about_pain_rule(
            titles=titles,
            eligibility_criteria=eligibility_criteria,
            primary_outcome_text=primary_outcome_text,
            config=config,
        )
    )
    if hit is None:
        return ConditionEligibility(
            targets_in_conditions=targets, eligibility="eligible", condition_feature_flags=flags
        )
    return ConditionEligibility(
        targets_in_conditions=targets,
        eligibility="excluded",
        exclusion_rule=hit.rule,
        exclusion_detail=hit.detail,
        condition_feature_flags=flags,
        exclusion_source=hit.source,
        exclusion_snippet=hit.snippet,
    )
