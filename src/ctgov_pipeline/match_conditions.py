"""Local condition matching against registered condition text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ConditionMatch:
    matched_targets: list[str]
    review_flag: bool


def _compile_patterns(config: dict[str, Any]) -> dict[str, list[re.Pattern[str]]]:
    compiled: dict[str, list[re.Pattern[str]]] = {}
    for target, spec in config["targets"].items():
        compiled[target] = [
            re.compile(pattern, re.IGNORECASE) for pattern in spec["patterns"]
        ]
    return compiled


def match_conditions(
    conditions: list[str] | None,
    keywords: list[str] | None,
    config: dict[str, Any],
) -> ConditionMatch:
    text = " | ".join((conditions or []) + (keywords or []))
    matched: list[str] = []
    compiled = _compile_patterns(config)
    for target, patterns in compiled.items():
        if any(pattern.search(text) for pattern in patterns):
            matched.append(target)

    review_flag = not matched and bool(text.strip())
    if matched == ["back_pain"] and re.search(r"\bchronic pain\b", text, re.I):
        review_flag = True
    return ConditionMatch(matched_targets=matched, review_flag=review_flag)
