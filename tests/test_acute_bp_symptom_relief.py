"""Tests for acute back-pain pharmaceutical symptom-relief detection."""

from __future__ import annotations

import unittest

from ctgov_pipeline.acute_bp_symptom_relief import is_acute_bp_symptom_relief
from ctgov_pipeline.config_loader import load_yaml


class AcuteBpSymptomReliefTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_yaml("condition_patterns_cohort.yaml")

    def test_friedman_style_short_duration_nsaid_trial_flagged(self) -> None:
        self.assertTrue(
            is_acute_bp_symptom_relief(
                eligible_back_pain=True,
                interventions=[
                    {"type": "DRUG", "name": "Ibuprofen 600 mg"},
                    {"type": "DRUG", "name": "Metaxalone"},
                    {"type": "BEHAVIORAL", "name": "Educational intervention"},
                ],
                eligibility_criteria=(
                    "Inclusion Criteria:\n"
                    "* Pain duration <2 weeks (336 hours).\n"
                    "* Patients with more than two weeks of pain are excluded.\n"
                ),
                pain_duration_inclusion="Pain duration <2 weeks (336 hours).",
                config=self.config,
            )
        )

    def test_chronic_back_pain_with_nsaid_not_flagged(self) -> None:
        self.assertFalse(
            is_acute_bp_symptom_relief(
                eligible_back_pain=True,
                interventions=[
                    {"type": "DRUG", "name": "Oral NSAIDs"},
                    {"type": "BEHAVIORAL", "name": "Multidimensional exercise"},
                ],
                eligibility_criteria="Chronic low-back pain for > 3 months",
                pain_duration_inclusion="Chronic low-back pain for > 3 months",
                config=self.config,
            )
        )

    def test_non_back_pain_trial_not_flagged(self) -> None:
        self.assertFalse(
            is_acute_bp_symptom_relief(
                eligible_back_pain=False,
                interventions=[{"type": "DRUG", "name": "Ibuprofen"}],
                eligibility_criteria="Pain duration <2 weeks",
                config=self.config,
            )
        )


if __name__ == "__main__":
    unittest.main()
