"""Tests for the auto-generated docs/category_mapping.md."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from ctgov_pipeline.category_mapping_report import write_category_mapping


class CategoryMappingReportTests(unittest.TestCase):
    def test_tables_contain_patterns_and_counts(self) -> None:
        studies = pd.DataFrame(
            {
                "cohort_inclusion_status": ["included", "included", "excluded"],
                "intervention_categories": ["psychological_cognitive | digital_health_delivery", "other_behavioral_treatment", "psychological_cognitive"],
                "is_multimodal": [False, True, False],
                "control_arm_types": ["usual_care", "", ""],
            }
        )
        outcomes = pd.DataFrame(
            {
                "outcome_id": ["a", "b", "c"],
                "nct_id": ["N1", "N1", "N3"],
                "cohort_inclusion_status": ["included", "included", "excluded"],
                "outcome_category": ["pain_recovery", "mechanistic", "pain_recovery"],
                "outcome_subcategory": ["pain_intensity", "sensory_qst", "pain_intensity"],
                "instruments_detected": ["Visual Analog Scale", "", "Visual Analog Scale"],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            text = write_category_mapping(studies, outcomes, Path(tmp) / "out.md").read_text(encoding="utf-8")
        self.assertIn("2 included trials, 2 primary-outcome rows", text)  # excluded trials are not counted
        self.assertIn("| | pain_intensity | 1 (50.0%) | 1 |", text)
        self.assertIn("pressure pain", text)  # mechanistic patterns listed
        self.assertIn("`psychological_cognitive` | Psychological & cognitive therapy | 1 (50.0%)", text)
        self.assertIn("`other_behavioral_treatment`", text)
        self.assertIn("Comparator arm patterns", text)


if __name__ == "__main__":
    unittest.main()
