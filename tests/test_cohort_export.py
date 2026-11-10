"""Tests for exclusion wording and study-table schema."""

from __future__ import annotations

import unittest

from ctgov_pipeline.cohort_export import (
    STUDY_TABLE_COLUMNS,
    build_exclusion_fields,
    exclusion_rule_from_detail,
    first_n_words,
    interventions_text,
)
from ctgov_pipeline.condition_eligibility import ConditionEligibility


class CohortExportTests(unittest.TestCase):
    def test_included_study_has_empty_exclusion_fields(self) -> None:
        cond = ConditionEligibility(targets_in_conditions=["migraine"], eligibility="eligible")
        self.assertEqual(build_exclusion_fields(cond=cond, rule=""), ("", ""))

    def test_acute_rule_reports_general_reason_source_and_snippet(self) -> None:
        cond = ConditionEligibility(
            targets_in_conditions=[],
            eligibility="excluded",
            exclusion_rule="acute_pain",
            acute_population_source="eligibility_inclusion_1",
            acute_population_snippet="Receiving care for acute low back pain",
        )
        reason, detail = build_exclusion_fields(cond=cond, rule="acute_pain")
        self.assertEqual(reason, "acute")
        self.assertTrue(detail.startswith("acute_pain:"))
        self.assertIn("eligibility_inclusion_1", detail)
        self.assertIn("acute low back pain", detail)
        self.assertEqual(exclusion_rule_from_detail(detail), "acute_pain")

    def test_condition_rule_reports_condition_reason(self) -> None:
        cond = ConditionEligibility(
            targets_in_conditions=[],
            eligibility="excluded",
            exclusion_rule="no_target_match",
            exclusion_detail="No target pattern matched.",
        )
        reason, detail = build_exclusion_fields(cond=cond, rule="no_target_match")
        self.assertEqual(reason, "condition")
        self.assertEqual(detail, "no_target_match: No target pattern matched.")

    def test_brief_summary_truncated_to_50_words(self) -> None:
        text = " ".join(f"w{i}" for i in range(80))
        out = first_n_words(text, 50)
        self.assertEqual(len(out.replace(" …", "").split()), 50)
        self.assertTrue(out.endswith("…"))
        self.assertEqual(first_n_words("short text", 50), "short text")

    def test_interventions_text_is_readable(self) -> None:
        out = interventions_text(
            [
                {"name": "CBT", "type": "BEHAVIORAL", "description": "Weekly\nsessions"},
                {"name": "Usual care", "type": "OTHER"},
            ]
        )
        self.assertEqual(out, "CBT [BEHAVIORAL]: Weekly sessions || Usual care [OTHER]")

    def test_schema_has_single_general_reason_and_no_redundant_intervention_columns(self) -> None:
        self.assertIn("exclusion_reason", STUDY_TABLE_COLUMNS)
        self.assertIn("exclusion_detail", STUDY_TABLE_COLUMNS)
        self.assertNotIn("exclusion_rule", STUDY_TABLE_COLUMNS)
        for removed in ("intervention_category_labels", "intervention_classification_rule"):
            self.assertNotIn(removed, STUDY_TABLE_COLUMNS)
        self.assertEqual(len(STUDY_TABLE_COLUMNS), len(set(STUDY_TABLE_COLUMNS)))


if __name__ == "__main__":
    unittest.main()
