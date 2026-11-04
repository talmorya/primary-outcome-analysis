"""Validate intervention category assignments against raw CT.gov arm text."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .classify_intervention_categories import (
    _active_arm_text,
    _arm_name,
    _is_behavioral_item,
    _match_categories,
    classify_intervention_categories,
    is_comparator_arm,
)


@dataclass
class CategoryEvidence:
    category: str
    arm_name: str
    arm_type: str
    matched_text_snippet: str
    is_comparator_arm: bool


@dataclass
class InterventionValidationResult:
    nct_id: str
    assigned_categories: list[str]
    recomputed_categories: list[str]
    evidence: list[CategoryEvidence] = field(default_factory=list)
    categories_from_comparator_only: list[str] = field(default_factory=list)
    unsupported_categories: list[str] = field(default_factory=list)


def parse_pipe_field(value: str | None) -> list[str]:
    if not value or str(value).strip().lower() == "nan":
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def _is_comparator_arm(item: dict[str, Any], config: dict[str, Any]) -> bool:
    return is_comparator_arm(
        _arm_name(item),
        config.get("control_arm", {}).get("patterns", []),
    )


def categories_for_arm(
    item: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    """Categories a single arm contributes, mirroring classifier precedence."""
    if _is_comparator_arm(item, config):
        return []

    text = _active_arm_text(item)
    category_defs = config.get("categories", {})
    matched = _match_categories(text, category_defs)
    if matched:
        return matched

    if _is_behavioral_item(item):
        return ["other_behavioral_treatment"]

    return []


def collect_category_evidence(
    interventions: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[CategoryEvidence]:
    evidence: list[CategoryEvidence] = []
    category_defs = config.get("categories", {})

    for item in interventions:
        name = _arm_name(item)
        text = _active_arm_text(item)
        comparator = _is_comparator_arm(item, config)
        arm_type = str(item.get("type", ""))

        if comparator:
            for cat_id in _match_categories(text, category_defs):
                evidence.append(
                    CategoryEvidence(
                        category=cat_id,
                        arm_name=name,
                        arm_type=arm_type,
                        matched_text_snippet=text[:120],
                        is_comparator_arm=True,
                    )
                )
            continue

        for cat_id in categories_for_arm(item, config):
            evidence.append(
                CategoryEvidence(
                    category=cat_id,
                    arm_name=name,
                    arm_type=arm_type,
                    matched_text_snippet=text[:120],
                    is_comparator_arm=False,
                )
            )

    return evidence


def validate_intervention_categories(
    *,
    nct_id: str,
    interventions: list[dict[str, Any]],
    assigned_categories: list[str],
    config: dict[str, Any],
) -> InterventionValidationResult:
    recomputed = classify_intervention_categories(interventions, config)
    recomputed_categories = recomputed.intervention_categories
    evidence = collect_category_evidence(interventions, config)

    treatment_supported = {ev.category for ev in evidence if not ev.is_comparator_arm}
    comparator_supported = {ev.category for ev in evidence if ev.is_comparator_arm}

    unsupported = sorted(cat for cat in assigned_categories if cat not in treatment_supported)
    comparator_only = sorted(
        cat for cat in assigned_categories if cat in comparator_supported and cat not in treatment_supported
    )

    return InterventionValidationResult(
        nct_id=nct_id,
        assigned_categories=assigned_categories,
        recomputed_categories=recomputed_categories,
        evidence=evidence,
        categories_from_comparator_only=comparator_only,
        unsupported_categories=unsupported,
    )


def load_interventions_from_row(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = row.get("interventions_raw")
    if raw:
        if isinstance(raw, str):
            return json.loads(raw)
        return list(raw)
    nct_id = row.get("nct_id")
    run_id = row.get("extraction_run_id")
    if not nct_id or not run_id:
        return []
    from .config_loader import PROJECT_ROOT

    path = PROJECT_ROOT / "data" / "raw" / "full" / str(run_id) / "studies" / f"{nct_id}.json"
    if not path.is_file():
        return []
    record = json.loads(path.read_text(encoding="utf-8"))
    arms = record.get("protocolSection", {}).get("armsInterventionsModule", {}) or {}
    return list(arms.get("interventions") or [])
