"""Validate stored outcome categories against the classifier."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .outcome_category import classify_outcome_category


@dataclass
class OutcomeCategoryValidation:
    outcome_id: str
    nct_id: str
    stored_category: str
    stored_subcategory: str
    recomputed_category: str
    recomputed_subcategory: str

    @property
    def matches(self) -> bool:
        return (
            self.stored_category == self.recomputed_category
            and self.stored_subcategory == self.recomputed_subcategory
        )


def _text_field(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def recompute_outcome_category(row: pd.Series) -> tuple[str, str]:
    result = classify_outcome_category(
        _text_field(row.get("raw_primary_outcome_measure")),
        _text_field(row.get("raw_primary_outcome_description")),
        _text_field(row.get("raw_primary_outcome_time_frame")),
    )
    return result.outcome_category, result.outcome_subcategory


def validate_outcome_row(row: pd.Series) -> OutcomeCategoryValidation:
    rec_cat, rec_sub = recompute_outcome_category(row)
    return OutcomeCategoryValidation(
        outcome_id=str(row.get("outcome_id", "")),
        nct_id=str(row.get("nct_id", "")),
        stored_category=str(row.get("outcome_category", "")),
        stored_subcategory=str(row.get("outcome_subcategory", "")),
        recomputed_category=rec_cat,
        recomputed_subcategory=rec_sub,
    )
