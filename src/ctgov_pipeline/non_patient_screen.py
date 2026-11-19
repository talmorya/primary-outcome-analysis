"""Exclude samples that are not pain patients (general population, or not about pain at all)."""

from __future__ import annotations

import re
from typing import Any

from .eligibility_text import extract_inclusion_blocks


def _search(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ""


def screen_non_patient_sample(
    *,
    eligibility_criteria: str | None,
    titles: str,
    primary_outcome_text: str | None,
    config: dict[str, Any],
) -> tuple[str, str] | None:
    """(rule, detail) when the sample is not a pain-patient sample; None otherwise.

    - `general_population_sample`: the inclusion criteria name a group (all students /
      employees / staff / children ...) and never mention pain, symptoms or a diagnosis.
    - `not_about_pain`: no pain word anywhere in the titles, inclusion criteria or primary
      outcomes (the trial is about something else, e.g. concussion, tinnitus, healthy adults).
    Skipped when the inclusion criteria (or, for `not_about_pain`, the outcomes) are empty.
    """
    spec = config.get("non_patient_sample", {})
    inclusion = " ".join(extract_inclusion_blocks(eligibility_criteria)).strip()
    if not inclusion:
        return None

    general = spec.get("general_population", {})
    if general and not _search(general.get("pain_wording_patterns", []), inclusion):
        group = _search(general.get("membership_patterns", []), inclusion)
        if group:
            return (
                general.get("rule", "general_population_sample"),
                f"Inclusion criteria select a group ('{group}') with no pain, symptom or "
                "diagnosis wording; not a pain-patient sample.",
            )

    not_pain = spec.get("not_about_pain", {})
    outcomes = (primary_outcome_text or "").strip()
    if not_pain and outcomes:
        scope = f"{titles} {inclusion} {outcomes}"
        if not _search(not_pain.get("pain_wording_patterns", []), scope):
            return (
                not_pain.get("rule", "not_about_pain"),
                "No pain wording in the titles, inclusion criteria or primary outcomes.",
            )
    return None
