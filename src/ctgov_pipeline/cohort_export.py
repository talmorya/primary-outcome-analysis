"""Canonical study-table columns and exclusion wording for the analytic cohort."""

from __future__ import annotations

from typing import Any

from .condition_eligibility import ConditionEligibility

STUDIES_CSV = "studies.csv"
PRIMARY_OUTCOMES_CSV = "primary_outcomes.csv"
MANIFEST_JSON = "manifest.json"
COHORT_REPORT_MD = "cohort_report.md"

# General reason shown in `exclusion_reason`; the specific rule key leads `exclusion_detail`.
EXCLUSION_REASON_ACUTE = "acute"
EXCLUSION_REASON_CONDITION = "condition"

ACUTE_RULES = frozenset({"acute_pain", "short_pain_window"})

STUDY_TABLE_COLUMNS: list[str] = [
    "nct_id",
    "cohort_inclusion_status",
    "exclusion_reason",
    "exclusion_detail",
    "raw_brief_title",
    "raw_official_title",
    "raw_brief_summary_50w",
    "raw_conditions",
    "raw_keywords",
    "raw_eligibility_criteria",
    "pain_duration_inclusion",
    "condition_matched",
    "condition_feature_flags",
    "review_flags",
    "eligible_migraine",
    "eligible_back_pain",
    "eligible_fibromyalgia",
    "eligible_headache",
    "intervention_categories",
    "is_multimodal",
    "control_arm_types",
    "raw_intervention_names",
    "raw_intervention_details",
    "raw_overall_status",
    "raw_study_first_post_date",
    "raw_phases",
    "raw_primary_purpose",
    "raw_has_results",
    "api_retrieval_queries",
    "extraction_run_id",
    "cohort_rules_version",
]


def first_n_words(text: str | None, n: int = 50) -> str:
    if not text:
        return ""
    words = str(text).split()
    if len(words) <= n:
        return " ".join(words)
    return " ".join(words[:n]) + " …"


def interventions_text(interventions: list[dict[str, Any]]) -> str:
    """Readable arm text for manual review: 'name [TYPE]: description' joined by ' || '."""
    parts: list[str] = []
    for item in interventions:
        name = (item.get("name") or "").strip()
        kind = (item.get("type") or "").strip()
        desc = " ".join((item.get("description") or "").split())
        head = f"{name} [{kind}]" if kind else name
        parts.append(f"{head}: {desc}" if desc else head)
    return " || ".join(parts)


def build_exclusion_fields(*, cond: ConditionEligibility, rule: str) -> tuple[str, str]:
    """(exclusion_reason, exclusion_detail); both empty strings for included studies."""
    if cond.eligibility == "eligible":
        return "", ""
    reason = EXCLUSION_REASON_ACUTE if rule in ACUTE_RULES else EXCLUSION_REASON_CONDITION
    explanation = cond.exclusion_detail or "Condition-stage rule applied."
    if cond.exclusion_snippet:
        explanation += f" (found in {cond.exclusion_source}). Matched text: \"{cond.exclusion_snippet}\""
    return reason, f"{rule}: {explanation}"


def exclusion_rule_from_detail(detail: object) -> str:
    """Rule key = text before the first ':' in `exclusion_detail` (used by the report)."""
    text = "" if detail is None else str(detail)
    return text.split(":", 1)[0].strip() if ":" in text else ""


def project_study_row(row: dict[str, Any]) -> dict[str, Any]:
    """Keep only the canonical study schema (plus `eligible_<target>` flags of extra targets in the config)."""
    extra = [key for key in row if key.startswith("eligible_") and key not in STUDY_TABLE_COLUMNS]
    return {key: row.get(key) for key in STUDY_TABLE_COLUMNS + extra}
