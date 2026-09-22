"""Tests for proposed condition eligibility rules."""

from __future__ import annotations

import unittest

from ctgov_pipeline.condition_eligibility import evaluate_condition_eligibility
from ctgov_pipeline.config_loader import load_yaml


class ConditionEligibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_yaml("condition_patterns_proposed.yaml")

    def test_cancer_excludes_multimorbidity_trial(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Cancer", "Migraine"],
            keywords=[],
            config=self.config,
            brief_title="Mindfulness trial",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "cancer_oncology")

    def test_post_concussive_headache_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Post Concussive Headache"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "post_traumatic")

    def test_tension_headache_eligible(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Tension-Type Headache"],
            keywords=[],
            config=self.config,
            force_headache_include=True,
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("primary_headache", result.targets_eligible)

    def test_migraine_not_counted_as_headache_expansion(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Migraine"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("migraine", result.targets_eligible)
        self.assertNotIn("primary_headache", result.targets_eligible)


if __name__ == "__main__":
    unittest.main()
