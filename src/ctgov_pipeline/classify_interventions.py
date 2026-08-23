"""Classify behavioral interventions and multimodal trial components."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InterventionClassification:
    behavioral_component: list[str]
    classification_rules: list[str] = field(default_factory=list)
    is_multimodal: bool = False
    other_modality_present: bool = False
    other_modality_type: str | None = None
    other_modality_name: str | None = None
    non_psychological_behavioral_flag: bool = False
    non_psychological_behavioral_type: str | None = None
    non_psychological_behavioral_name: str | None = None
    review_flag: bool = False


def _match_patterns(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _intervention_text(item: dict[str, Any]) -> str:
    return " ".join(
        str(item.get(key, "")) for key in ("name", "description", "type")
    )


def _match_approaches(text: str, config: dict[str, Any]) -> tuple[list[str], list[str], bool]:
    approaches: list[str] = []
    rules: list[str] = []
    review = False
    for approach, spec in config.get("approaches", {}).items():
        if any(re.search(ex, text, re.IGNORECASE) for ex in spec.get("exclude", [])):
            continue
        if _match_patterns(text, spec.get("patterns", [])):
            approaches.append(approach)
            rules.append(f"APP_{approach.upper()}")
            if spec.get("review_flag"):
                review = True
    return approaches, rules, review


def _match_non_psych_behavioral(text: str, config: dict[str, Any]) -> tuple[str | None, str | None, bool]:
    for modality, spec in config.get("non_psychological_behavioral", {}).items():
        if _match_patterns(text, spec.get("patterns", [])):
            return modality, spec.get("patterns", [""])[0], bool(spec.get("review_flag"))
    return None, None, False


def _classify_other_modality(item: dict[str, Any], config: dict[str, Any]) -> tuple[str | None, str | None]:
    text = _intervention_text(item)
    item_type = str(item.get("type", "")).upper()
    for modality, spec in config.get("other_modality_types", {}).items():
        types = set(spec.get("intervention_types", []))
        if item_type in types:
            return modality, str(item.get("name", ""))
        if _match_patterns(text, spec.get("patterns", [])):
            return modality, str(item.get("name", ""))
    return None, None


def classify_interventions(
    interventions: list[dict[str, Any]],
    config: dict[str, Any],
) -> InterventionClassification:
    if not interventions:
        return InterventionClassification(
            behavioral_component=[],
            review_flag=True,
        )

    all_approaches: list[str] = []
    all_rules: list[str] = []
    review_flag = False

    non_psych_hits: list[tuple[str, str]] = []
    other_modality_hits: list[tuple[str, str]] = []

    for item in interventions:
        text = _intervention_text(item)
        approaches, rules, review = _match_approaches(text, config)
        all_approaches.extend(approaches)
        all_rules.extend(rules)
        review_flag = review_flag or review

        non_psych_type, _, non_psych_review = _match_non_psych_behavioral(text, config)
        if non_psych_type and not approaches:
            non_psych_hits.append((non_psych_type, str(item.get("name", ""))))
            if non_psych_review:
                review_flag = True

        other_type, other_name = _classify_other_modality(item, config)
        if other_type:
            other_modality_hits.append((other_type, other_name))

    behavioral_component = sorted(set(all_approaches))
    if not behavioral_component and not non_psych_hits and not other_modality_hits:
        behavioral_component = ["other_psychological"]
        all_rules.append("APP_OTHER_PSYCH")
        review_flag = True
    elif len(behavioral_component) > 1:
        review_flag = True

    non_psychological_behavioral_flag = bool(non_psych_hits)
    non_psychological_behavioral_type = (
        " | ".join(sorted({hit[0] for hit in non_psych_hits})) if non_psych_hits else None
    )
    non_psychological_behavioral_name = (
        " | ".join(name for _, name in non_psych_hits) if non_psych_hits else None
    )

    other_modality_present = bool(other_modality_hits or non_psych_hits)
    other_modality_type = None
    other_modality_name = None
    if other_modality_hits:
        other_modality_type = " | ".join(sorted({hit[0] for hit in other_modality_hits}))
        other_modality_name = " | ".join(hit[1] for hit in other_modality_hits)
    elif non_psych_hits:
        other_modality_type = non_psychological_behavioral_type
        other_modality_name = non_psychological_behavioral_name

    has_psych_component = bool(behavioral_component)
    is_multimodal = has_psych_component and other_modality_present
    if non_psychological_behavioral_flag and not has_psych_component:
        review_flag = True

    return InterventionClassification(
        behavioral_component=behavioral_component,
        classification_rules=sorted(set(all_rules)),
        is_multimodal=is_multimodal,
        other_modality_present=other_modality_present,
        other_modality_type=other_modality_type,
        other_modality_name=other_modality_name,
        non_psychological_behavioral_flag=non_psychological_behavioral_flag,
        non_psychological_behavioral_type=non_psychological_behavioral_type,
        non_psychological_behavioral_name=non_psychological_behavioral_name,
        review_flag=review_flag,
    )
