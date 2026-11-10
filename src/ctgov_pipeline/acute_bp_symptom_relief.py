"""Flag (and optionally exclude) acute back-pain pharmaceutical symptom-relief trials.

Cluster-3 noise among back-pain hits: brief episode (<~2 weeks), NSAID / muscle-relaxant
arms, often with a light educational control. These treat an acute flare, not chronification
or established chronic back pain. Descriptive column: `is_acute_bp_symptom_relief`.
"""

from __future__ import annotations

import re
from typing import Any


def _compile(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def _join(*parts: str | None) -> str:
    return " | ".join(p for p in parts if p and str(p).strip())


def is_acute_bp_symptom_relief(
    *,
    eligible_back_pain: bool,
    interventions: list[dict[str, Any]] | None,
    eligibility_criteria: str | None = None,
    brief_title: str | None = None,
    brief_summary: str | None = None,
    pain_duration_inclusion: str | None = None,
    config: dict[str, Any] | None = None,
) -> bool:
    """True when a back-pain trial is short-duration pharmaceutical acute relief."""
    if not eligible_back_pain:
        return False

    spec = (config or {}).get("acute_bp_symptom_relief", {})
    drug_patterns = _compile(spec.get("drug_patterns", []))
    short_patterns = _compile(spec.get("short_duration_patterns", []))
    chronic_patterns = _compile(spec.get("chronic_keep_patterns", []))
    if not drug_patterns or not short_patterns:
        return False

    int_text = " | ".join(
        f"{(i.get('name') or '')} {(i.get('description') or '')} {(i.get('type') or '')}"
        for i in (interventions or [])
    )
    if not any(p.search(int_text) for p in drug_patterns):
        return False

    duration_blob = _join(pain_duration_inclusion, eligibility_criteria, brief_title, brief_summary)
    if any(p.search(duration_blob) for p in chronic_patterns):
        return False
    return any(p.search(duration_blob) for p in short_patterns)
