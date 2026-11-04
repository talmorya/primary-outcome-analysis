"""Screen for acute / recent surgery / recent injury populations (condition stage)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .eligibility_text import extract_exclusion_blocks, extract_inclusion_blocks


@dataclass(frozen=True)
class AcutePopulationScreenResult:
    decision: str  # pass | exclude
    rule: str | None = None
    source: str | None = None
    detail: str | None = None
    snippet: str | None = None


# Uses of the word "acute" that do NOT describe an enrolled acute-pain population.
# A match is ignored only when its own "acute" token sits inside one of these phrases.
_NON_POPULATION_ACUTE = re.compile(
    # laboratory stimulus wording
    r"\bacute\s+(?:noxious|physical)\s+stimul"
    r"|\bresponse\s+to\s+acute\s+noxious"
    # drug / treatment wording (e.g. "acute pain relief medications", "acute migraine attacks")
    r"|\bacute\s+(?:pain\s+)?(?:relief|medications?|treatments?|therapy|therapies|drugs?|analgesics?|attacks?)\b"
    # chronic patients with an acute flare (population is still chronic)
    r"|\bacute\s+(?:pain\s+)?(?:episodes?|flares?|flare-ups?|exacerbations?)\s+of\s+(?:\w+\s+){0,2}chronic\b"
    # background contrast ("chronic versus acute"), not enrollment
    r"|\bchronic\s+(?:\w+\s+){0,2}(?:versus|vs\.?|rather\s+than|compared\s+(?:to|with))\s+(?:\w+\s+)?acute\b"
    r"|\bacute\s+(?:\w+\s+){0,2}(?:versus|vs\.?)\s+chronic\b",
    re.IGNORECASE,
)

_NEGATED_ACUTE = re.compile(
    r"\b(not|no|without|non[-\s]|exclude[d]?|excluding)\b[^.;\n]{0,50}\bacute\b"
    r"|\bacute\b[^.;\n]{0,30}\b(exclud|not eligible|not due)",
    re.IGNORECASE,
)

_CHRONIC_IN_TEXT = re.compile(
    r"\bchronic\b.{0,40}\b(?:pain|low\s+back|headache|migraine|fibromyalgia)\b"
    r"|\b(?:pain|low\s+back|headache).{0,40}\bchronic\b",
    re.IGNORECASE,
)

_CHRONIC_DURATION = re.compile(
    r"(?:pain|symptoms?|condition).{0,80}(?:≥|>=|>|more than|at least|minimum of|lasting|duration\s+of)\s*"
    r"(?:6\s*months|3\s*months|12\s*weeks|90\s*days)"
    r"|(?:≥|>=|>|more than|at least)\s*(?:3|6)\s*months",
    re.IGNORECASE,
)

_ACUTE_POPULATION_PHRASE = re.compile(
    r"\bacute\s+(?:low\s+)?back\s+pain\b"
    r"|\bacute\s+pain\b"
    r"|\bpain\s*,\s*acute\b"
    r"|\bacute\s+(?:neck|back|musculoskeletal|headache)\b"
    r"|(?:neck|back|musculoskeletal|headache)(?:\s+pain)?[\s,:(\-]{0,4}\bacute\b"
    r"|\"acute\""
    r"|acute\s+.*\s+diagnosis",
    re.IGNORECASE,
)

_RECENT_SURGERY = re.compile(
    r"(?:surgery|surgical|operation|operated|post[- ]?operative)"
    r".{0,60}(?:within|in the|during the)\s+(?:the\s+)?(?:past|previous|last)\s*"
    r"(?:3\s*months|12\s*weeks|90\s*days)"
    r"|(?:within|in the|during the)\s+(?:the\s+)?(?:past|previous|last)\s*"
    r"(?:3\s*months|12\s*weeks|90\s*days).{0,60}(?:surgery|surgical|operation|operated)",
    re.IGNORECASE,
)

_RECENT_INJURY = re.compile(
    r"(?:injury|injuries|trauma|sprain|fracture)"
    r".{0,60}(?:within|in the|during the)\s+(?:the\s+)?(?:past|previous|last)\s*"
    r"(?:3\s*months|12\s*weeks|90\s*days)"
    r"|(?:within|in the|during the)\s+(?:the\s+)?(?:past|previous|last)\s*"
    r"(?:3\s*months|12\s*weeks|90\s*days).{0,60}(?:injury|injuries|trauma)",
    re.IGNORECASE,
)


def _compile_acute_patterns(config: dict[str, Any]) -> list[re.Pattern[str]]:
    spec = config.get("exclusion_rules", {}).get("acute_pain", {})
    return [re.compile(p, re.IGNORECASE) for p in spec.get("patterns", [])]


def _snippet(text: str, match: re.Match[str]) -> str:
    start = max(0, match.start() - 40)
    end = min(len(text), match.end() + 40)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def _is_non_population_acute(text: str, match: re.Match[str]) -> bool:
    """True when this match's own word 'acute' is part of a non-population phrase."""
    token = re.search(r"\bacute\b", match.group(0), re.IGNORECASE)
    if not token:
        return False  # duration-based patterns (e.g. "pain for less than 3 months")
    pos = match.start() + token.start()
    return any(g.start() <= pos < g.end() for g in _NON_POPULATION_ACUTE.finditer(text))


def _acute_population_in_text(
    text: str,
    *,
    acute_patterns: list[re.Pattern[str]],
) -> re.Match[str] | None:
    """First acute-population match in the text (every occurrence is checked)."""
    if not text.strip():
        return None
    if _NEGATED_ACUTE.search(text):
        return None
    for pattern in [*acute_patterns, _ACUTE_POPULATION_PHRASE]:
        for match in pattern.finditer(text):
            if not _is_non_population_acute(text, match):
                return match
    return None


def _chronic_population_in_text(text: str) -> bool:
    return bool(_CHRONIC_IN_TEXT.search(text) or _CHRONIC_DURATION.search(text))


def _all_registered_conditions_chronic(conditions: list[str] | None) -> bool:
    """True when every non-empty registered condition line contains the word 'chronic'."""
    lines = [str(line).strip() for line in (conditions or []) if str(line).strip()]
    if not lines:
        return False
    return all(re.search(r"\bchronic\b", line, re.IGNORECASE) for line in lines)


def _screen_inclusion_block(
    block: str,
    *,
    acute_patterns: list[re.Pattern[str]],
    source: str,
) -> AcutePopulationScreenResult | None:
    if not block.strip():
        return None

    chronic = _chronic_population_in_text(block)
    acute_match = _acute_population_in_text(block, acute_patterns=acute_patterns)

    if chronic and acute_match:
        return AcutePopulationScreenResult(
            decision="exclude",
            rule="acute_and_chronic_in_inclusion",
            source=source,
            detail="Inclusion enrolls/requires both chronic and acute pain populations.",
            snippet=_snippet(block, acute_match),
        )

    if acute_match:
        return AcutePopulationScreenResult(
            decision="exclude",
            rule="acute_pain",
            source=source,
            detail="Acute pain population in inclusion criteria.",
            snippet=_snippet(block, acute_match),
        )

    for label, recent_pat in (("recent_surgery", _RECENT_SURGERY), ("recent_injury", _RECENT_INJURY)):
        match = recent_pat.search(block)
        if match:
            return AcutePopulationScreenResult(
                decision="exclude",
                rule=label,
                source=source,
                detail=f"Inclusion indicates {label.replace('_', ' ')} within ~3 months.",
                snippet=_snippet(block, match),
            )

    return None


def _screen_metadata_line(
    text: str,
    *,
    acute_patterns: list[re.Pattern[str]],
    source: str,
    conditions: list[str] | None,
) -> AcutePopulationScreenResult | None:
    """Conditions / titles / brief summary only (no keywords, interventions, detailed description)."""
    acute_match = _acute_population_in_text(text, acute_patterns=acute_patterns)
    if not acute_match:
        return None

    has_chronic_cond = any(_chronic_population_in_text(c) for c in (conditions or []))
    has_acute_cond = any(
        re.search(r"\bacute\s+pain\b", c, re.I) or re.search(r"\bpain\s*,\s*acute\b", c, re.I)
        for c in (conditions or [])
    )
    if has_chronic_cond and has_acute_cond and source == "registered_condition":
        return None

    return AcutePopulationScreenResult(
        decision="exclude",
        rule="acute_pain",
        source=source,
        detail="Acute pain population in registered conditions or study descriptors.",
        snippet=_snippet(text, acute_match),
    )


def screen_acute_population(
    *,
    conditions: list[str] | None,
    brief_title: str | None,
    official_title: str | None,
    brief_summary: str | None,
    eligibility_criteria: str | None,
    config: dict[str, Any],
) -> AcutePopulationScreenResult:
    """
    Order: eligibility inclusion blocks → registered conditions → official title → brief title → brief summary.

    Does not use keywords, MeSH, detailed description, or intervention names.
    """
    acute_patterns = _compile_acute_patterns(config)

    inclusion_blocks = extract_inclusion_blocks(eligibility_criteria)
    exclusion_blocks = extract_exclusion_blocks(eligibility_criteria)
    any_chronic_inclusion = any(_chronic_population_in_text(b) for b in inclusion_blocks)

    for idx, block in enumerate(inclusion_blocks):
        hit = _screen_inclusion_block(
            block,
            acute_patterns=acute_patterns,
            source=f"eligibility_inclusion_{idx + 1}",
        )
        if hit:
            return hit

    if any_chronic_inclusion and exclusion_blocks:
        for block in exclusion_blocks:
            if _acute_population_in_text(block, acute_patterns=acute_patterns):
                return AcutePopulationScreenResult(
                    decision="pass",
                    rule="chronic_inclusion_acute_excluded",
                    source="eligibility_exclusion",
                    detail="Chronic population in inclusion; acute pain only listed under exclusion.",
                )

    skip_descriptor_acute = _all_registered_conditions_chronic(conditions)

    if not skip_descriptor_acute:
        for line in conditions or []:
            text = line.strip()
            if not text:
                continue
            hit = _screen_metadata_line(
                text,
                acute_patterns=acute_patterns,
                source="registered_condition",
                conditions=conditions,
            )
            if hit:
                return hit

        for source, value in (
            ("official_title", official_title),
            ("brief_title", brief_title),
            ("brief_summary", brief_summary),
        ):
            if value and str(value).strip():
                hit = _screen_metadata_line(
                    str(value).strip(),
                    acute_patterns=acute_patterns,
                    source=source,
                    conditions=conditions,
                )
                if hit:
                    return hit

    if skip_descriptor_acute:
        return AcutePopulationScreenResult(
            decision="pass",
            rule="chronic_conditions_skip_descriptor_acute",
            detail="All registered conditions name chronic pain; acute wording in titles/summary ignored.",
        )

    return AcutePopulationScreenResult(decision="pass", rule="no_acute_population_signal")
