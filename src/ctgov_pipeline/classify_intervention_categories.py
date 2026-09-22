"""Classify treatment-oriented behavioral intervention categories."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InterventionCategoryResult:
    intervention_categories: list[str]
    intervention_category_labels: list[str]
    classification_rules: list[str] = field(default_factory=list)
    is_multimodal: bool = False
    multimodal_modalities: list[str] = field(default_factory=list)
    has_control_arm: bool = False
    has_mechanism_arm: bool = False
    has_behavioral_arm: bool = False
    review_flag: bool = False


def _compile(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def _matches(text: str, patterns: list[str]) -> bool:
    if not text.strip():
        return False
    compiled = _compile(patterns)
    return any(p.search(text) for p in compiled)


def _arm_name(item: dict[str, Any]) -> str:
    return str(item.get("name", "")).strip()


def _arm_text(item: dict[str, Any]) -> str:
    return " ".join(str(item.get(key, "")) for key in ("name", "description", "type"))


def _is_behavioral_item(item: dict[str, Any]) -> bool:
    item_type = str(item.get("type", "")).upper()
    if item_type == "BEHAVIORAL":
        return True
    if item_type == "OTHER":
        text = _arm_text(item).lower()
        return bool(
            re.search(
                r"behavior|psych|mindful|exercise|education|therapy|counsel|acupuncture|diet|yoga|hypnosis|meditation",
                text,
            )
        )
    return False


def _match_categories(text: str, category_defs: dict[str, Any]) -> list[str]:
    return [
        cat_id
        for cat_id, spec in category_defs.items()
        if _matches(text, spec.get("patterns", []))
    ]


def classify_intervention_categories(
    interventions: list[dict[str, Any]],
    config: dict[str, Any],
) -> InterventionCategoryResult:
    if not interventions:
        return InterventionCategoryResult(
            intervention_categories=[],
            intervention_category_labels=[],
            review_flag=True,
        )

    control_patterns = config.get("control_arm", {}).get("patterns", [])
    mechanism_spec = config.get("mechanism_arm", {})
    mechanism_patterns = mechanism_spec.get("patterns", [])
    mechanism_excludes = mechanism_spec.get("exclude", [])

    categories: set[str] = set()
    rules: list[str] = []
    multimodal: set[str] = set()
    has_control = False
    has_mechanism = False
    has_behavioral = False
    review = False

    category_defs = config.get("categories", {})
    label_map = {key: spec.get("label", key) for key, spec in category_defs.items()}

    for item in interventions:
        name = _arm_name(item)
        text = _arm_text(item)
        item_type = str(item.get("type", "")).upper()

        for modality, spec in config.get("multimodal_modalities", {}).items():
            types = set(spec.get("intervention_types", []))
            if item_type in types:
                multimodal.add(modality)

        if item_type == "BEHAVIORAL":
            has_behavioral = True

        arm_categories = _match_categories(text, category_defs)
        if arm_categories:
            categories.update(arm_categories)
            for cat_id in arm_categories:
                rules.append(f"CAT_{cat_id.upper()}")
            continue

        if _matches(text, mechanism_patterns) and not _matches(text, mechanism_excludes):
            has_mechanism = True
            rules.append("ARM_MECHANISM")
            continue

        # Control comparators: match arm name only (not description) to avoid
        # false positives when waitlist/sham/usual care appear in arm text.
        if _matches(name, control_patterns):
            has_control = True
            rules.append("ARM_CONTROL")
            continue

        if _is_behavioral_item(item):
            categories.add("other_behavioral_treatment")
            rules.append("CAT_OTHER_BEHAVIORAL_TREATMENT")
            review = True

    ordered = sorted(categories)
    labels = [label_map.get(cat_id, cat_id) for cat_id in ordered]
    if "other_behavioral_treatment" in ordered:
        review = True

    is_multimodal = bool(multimodal) and bool(categories)

    return InterventionCategoryResult(
        intervention_categories=ordered,
        intervention_category_labels=labels,
        classification_rules=sorted(set(rules)),
        is_multimodal=is_multimodal,
        multimodal_modalities=sorted(multimodal),
        has_control_arm=has_control,
        has_mechanism_arm=has_mechanism,
        has_behavioral_arm=has_behavioral,
        review_flag=review,
    )
