"""Parse raw ClinicalTrials.gov JSON into study and outcome tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .classify_interventions import classify_interventions
from .extract_outcome_features import extract_outcome_features
from .match_conditions import match_conditions
from .outcome_purpose import classify_outcome_purpose


def _safe_get(module: dict[str, Any] | None, *keys: str, default: Any = None) -> Any:
    current: Any = module or {}
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _join(values: list[str] | None, sep: str = " | ") -> str | None:
    if not values:
        return None
    return sep.join(values)


def parse_study_record(
    record: dict[str, Any],
    *,
    condition_config: dict[str, Any],
    intervention_config: dict[str, Any],
    outcome_lexicon: dict[str, Any],
    extraction_run_id: str,
    api_version: str | None,
    data_timestamp: str | None,
    query_source: str | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ps = record.get("protocolSection", {})
    id_mod = ps.get("identificationModule", {})
    status_mod = ps.get("statusModule", {})
    conditions_mod = ps.get("conditionsModule", {})
    design_mod = ps.get("designModule", {})
    arms_mod = ps.get("armsInterventionsModule", {})
    outcomes_mod = ps.get("outcomesModule", {})

    nct_id = id_mod.get("nctId")
    conditions = conditions_mod.get("conditions", [])
    keywords = conditions_mod.get("keywords", [])
    interventions = arms_mod.get("interventions", [])

    condition_match = match_conditions(conditions, keywords, condition_config)
    intervention = classify_interventions(interventions, intervention_config)

    study_row = {
        "nct_id": nct_id,
        "brief_title": id_mod.get("briefTitle"),
        "official_title": id_mod.get("officialTitle"),
        "conditions_raw": _join(conditions),
        "keywords_raw": _join(keywords),
        "condition_matched": _join(condition_match.matched_targets),
        "condition_review_flag": condition_match.review_flag,
        "interventions_raw": json.dumps(interventions, ensure_ascii=False),
        "intervention_names": _join([item.get("name", "") for item in interventions]),
        "intervention_types": _join(sorted({item.get("type", "") for item in interventions})),
        "behavioral_component": _join(intervention.behavioral_component),
        "intervention_classification_rule": _join(intervention.classification_rules),
        "intervention_review_flag": intervention.review_flag,
        "is_multimodal": intervention.is_multimodal,
        "other_modality_present": intervention.other_modality_present,
        "other_modality_type": intervention.other_modality_type,
        "other_modality_name": intervention.other_modality_name,
        "non_psychological_behavioral_flag": intervention.non_psychological_behavioral_flag,
        "non_psychological_behavioral_type": intervention.non_psychological_behavioral_type,
        "non_psychological_behavioral_name": intervention.non_psychological_behavioral_name,
        "overall_status": status_mod.get("overallStatus"),
        "study_type": design_mod.get("studyType"),
        "phases": _join(design_mod.get("phases", [])),
        "has_results": record.get("hasResults"),
        "study_first_post_date": _safe_get(status_mod, "studyFirstPostDateStruct", "date"),
        "study_first_post_date_type": _safe_get(status_mod, "studyFirstPostDateStruct", "type"),
        "start_date": _safe_get(status_mod, "startDateStruct", "date"),
        "primary_completion_date": _safe_get(status_mod, "primaryCompletionDateStruct", "date"),
        "completion_date": _safe_get(status_mod, "completionDateStruct", "date"),
        "last_update_post_date": _safe_get(status_mod, "lastUpdatePostDateStruct", "date"),
        "status_verified_date": status_mod.get("statusVerifiedDate"),
        "query_source": query_source,
        "api_version": api_version,
        "data_timestamp": data_timestamp,
        "extraction_run_id": extraction_run_id,
        "feature_extraction_version": outcome_lexicon.get("version"),
    }

    primary_outcomes = outcomes_mod.get("primaryOutcomes", []) or []
    outcome_rows: list[dict[str, Any]] = []
    for index, outcome in enumerate(primary_outcomes, start=1):
        measure = outcome.get("measure")
        description = outcome.get("description")
        time_frame = outcome.get("timeFrame")
        features = extract_outcome_features(measure, description, time_frame, outcome_lexicon)
        purpose = classify_outcome_purpose(measure, description, time_frame)
        outcome_rows.append(
            {
                "outcome_id": f"{nct_id}__po_{index}",
                "nct_id": nct_id,
                "primary_outcome_index": index,
                "n_primary_outcomes_in_study": len(primary_outcomes),
                "primary_outcome_measure": measure,
                "primary_outcome_description": description,
                "primary_outcome_time_frame": time_frame,
                "instruments_detected": _join(features.instruments_detected),
                "acronyms_detected": _join(features.acronyms_detected),
                "keywords_matched": _join(features.keywords_matched),
                "phrases_matched": _join(features.phrases_matched),
                "action_verbs_matched": _join(features.action_verbs_matched),
                "outcome_purpose": purpose.purpose,
                "outcome_purpose_rule": purpose.rule,
                "outcome_purpose_review_flag": purpose.review_flag,
                "feature_extraction_version": outcome_lexicon.get("version"),
                "brief_title": study_row["brief_title"],
                "conditions_raw": study_row["conditions_raw"],
                "condition_matched": study_row["condition_matched"],
                "behavioral_component": study_row["behavioral_component"],
                "intervention_names": study_row["intervention_names"],
                "is_multimodal": study_row["is_multimodal"],
                "overall_status": study_row["overall_status"],
                "study_first_post_date": study_row["study_first_post_date"],
                "study_type": study_row["study_type"],
                "extraction_run_id": extraction_run_id,
            }
        )
    return study_row, outcome_rows


def load_raw_studies(raw_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("NCT*.json")):
        with path.open(encoding="utf-8") as handle:
            records.append(json.load(handle))
    return records


def build_tables(
    records: list[dict[str, Any]],
    *,
    condition_config: dict[str, Any],
    intervention_config: dict[str, Any],
    outcome_lexicon: dict[str, Any],
    extraction_run_id: str,
    api_version: str | None,
    data_timestamp: str | None,
    query_source: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    study_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    for record in records:
        study_row, outcomes = parse_study_record(
            record,
            condition_config=condition_config,
            intervention_config=intervention_config,
            outcome_lexicon=outcome_lexicon,
            extraction_run_id=extraction_run_id,
            api_version=api_version,
            data_timestamp=data_timestamp,
            query_source=query_source,
        )
        study_rows.append(study_row)
        outcome_rows.extend(outcomes)
    return pd.DataFrame(study_rows), pd.DataFrame(outcome_rows)
