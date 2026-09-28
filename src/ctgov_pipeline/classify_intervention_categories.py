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
    has_active_treatment_arm: bool = False
    has_active_behavioral_arm: bool = False
    review_flag: bool = False
    control_arm_types: list[str] = field(default_factory=list)
    control_arms_raw: list[dict[str, str]] = field(default_factory=list)


# Arm names that deliver active treatment despite mentioning usual/standard care.
_ACTIVE_TREATMENT_NAME = re.compile(
    r"intervention|therapy|\bcbt\b|meditation|app[- ]based|self[- ]management|"
    r"web|training|education|exercise|pain ed|tenacity|\+",
    re.IGNORECASE,
)


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


def classify_control_type(arm_name: str) -> str:
    """Simple control taxonomy from arm name (not description)."""
    name = arm_name.lower()
    if re.search(r"\bsham\b", name):
        return "sham_control"
    if re.search(r"wait[- ]?list|waiting list", name):
        return "waitlist_control"
    if re.search(r"\bplacebo\b", name):
        return "placebo_control"
    if re.search(r"attention control", name):
        return "attention_control"
    if re.search(r"usual care|standard care|standard medical", name):
        return "usual_care"
    if re.search(r"no intervention", name):
        return "no_intervention_control"
    if re.search(r"control group|control arm|\bcontrol\b", name):
        return "other_control"
    return "other_control"


def is_comparator_arm(arm_name: str, control_patterns: list[str]) -> bool:
    """Comparator detection on arm name; active arms may mention usual care adjunctively."""
    name = arm_name.strip()
    if not name:
        return False
    lower = name.lower()
    if _ACTIVE_TREATMENT_NAME.search(name) and re.search(
        r"usual care|standard care", lower
    ):
        return False
    if re.search(r"standard care and web|web[- ]based|internet[- ]enhanced", lower):
        return False
    return _matches(name, control_patterns)


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
    treatment_multimodal_modalities: set[str] = set()
    active_arm_types: set[str] = set()
    has_control = False
    has_mechanism = False
    has_active_treatment = False
    has_active_behavioral = False
    review = False
    control_types: set[str] = set()
    control_raw: list[dict[str, str]] = []

    category_defs = config.get("categories", {})
    label_map = {key: spec.get("label", key) for key, spec in category_defs.items()}
    non_behavioral_types = set()
    for spec in config.get("multimodal_modalities", {}).values():
        non_behavioral_types.update(spec.get("intervention_types", []))

    for item in interventions:
        name = _arm_name(item)
        text = _arm_text(item)
        item_type = str(item.get("type", "")).upper()

        if is_comparator_arm(name, control_patterns):
            has_control = True
            rules.append("ARM_CONTROL")
            ctrl_type = classify_control_type(name)
            control_types.add(ctrl_type)
            control_raw.append(
                {
                    "control_type": ctrl_type,
                    "arm_name": name,
                    "arm_type": item_type,
                    "description": str(item.get("description") or "").strip(),
                }
            )
            continue

        has_active_treatment = True
        if item_type == "BEHAVIORAL" or _is_behavioral_item(item):
            has_active_behavioral = True

        active_arm_types.add(item_type)
        for modality, spec in config.get("multimodal_modalities", {}).items():
            types = set(spec.get("intervention_types", []))
            if item_type in types:
                treatment_multimodal_modalities.add(modality)

        arm_categories = _match_categories(text, category_defs)
        if arm_categories:
            categories.update(arm_categories)
            has_active_behavioral = True
            for cat_id in arm_categories:
                rules.append(f"CAT_{cat_id.upper()}")
            continue

        if _matches(text, mechanism_patterns) and not _matches(text, mechanism_excludes):
            has_mechanism = True
            rules.append("ARM_MECHANISM")
            continue

        if _is_behavioral_item(item):
            categories.add("other_behavioral_treatment")
            rules.append("CAT_OTHER_BEHAVIORAL_TREATMENT")
            review = True

    ordered = sorted(categories)
    labels = [label_map.get(cat_id, cat_id) for cat_id in ordered]
    if "other_behavioral_treatment" in ordered:
        review = True

    has_active_non_behavioral = bool(active_arm_types & non_behavioral_types)
    is_multimodal = bool(categories) and has_active_behavioral and has_active_non_behavioral

    return InterventionCategoryResult(
        intervention_categories=ordered,
        intervention_category_labels=labels,
        classification_rules=sorted(set(rules)),
        is_multimodal=is_multimodal,
        multimodal_modalities=sorted(treatment_multimodal_modalities),
        has_control_arm=has_control,
        has_mechanism_arm=has_mechanism,
        has_behavioral_arm=has_active_behavioral,
        has_active_treatment_arm=has_active_treatment,
        has_active_behavioral_arm=has_active_behavioral,
        review_flag=review,
        control_arm_types=sorted(control_types),
        control_arms_raw=control_raw,
    )
