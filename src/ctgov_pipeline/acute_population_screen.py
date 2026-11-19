"""Find an ACUTE enrolled population: the word "acute" describing who is enrolled.

All patterns live in `config/condition_patterns_cohort.yaml` (`exclusion_rules.acute_pain`):
`patterns` (what counts), `negation` (text that denies acute enrolment) and `ignore_phrases`
(uses of "acute" that do not describe the population, e.g. "acute pain relief medication").
"""

from __future__ import annotations

import re
from typing import Any

from .eligibility_text import extract_inclusion_blocks


def _snippet(text: str, match: re.Match[str]) -> str:
    return re.sub(r"\s+", " ", text[max(0, match.start() - 40) : match.end() + 40]).strip()


def _first_acute_match(text: str, spec: dict[str, Any]) -> re.Match[str] | None:
    if not text.strip() or re.search(spec["negation"], text, re.IGNORECASE):
        return None
    ignored = [m for p in spec["ignore_phrases"] for m in re.finditer(p, text, re.IGNORECASE)]
    for pattern in spec["patterns"]:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            word = re.search(r"\bacute\b", match.group(0), re.IGNORECASE)
            position = match.start() + (word.start() if word else 0)
            if not any(g.start() <= position < g.end() for g in ignored):
                return match
    return None


def find_acute_population(
    *,
    conditions: list[str] | None,
    brief_title: str | None,
    official_title: str | None,
    brief_summary: str | None,
    eligibility_criteria: str | None,
    check_descriptors: bool,
    config: dict[str, Any],
) -> tuple[str, str] | None:
    """(source, snippet) of the first text describing an acute population, or None.

    Order: inclusion criteria → registered conditions → official title → brief title → brief summary
    (the last four only when `check_descriptors`). Keywords, detailed description and exclusion
    criteria are never searched.
    """
    spec = config["exclusion_rules"]["acute_pain"]
    sources = [
        (f"eligibility_inclusion_{i + 1}", block)
        for i, block in enumerate(extract_inclusion_blocks(eligibility_criteria))
    ]
    if check_descriptors:
        sources += [("registered_condition", c) for c in (conditions or [])]
        sources += [
            ("official_title", official_title),
            ("brief_title", brief_title),
            ("brief_summary", brief_summary),
        ]
    for source, text in sources:
        match = _first_acute_match(str(text or ""), spec)
        if match:
            return source, _snippet(str(text), match)
    return None
