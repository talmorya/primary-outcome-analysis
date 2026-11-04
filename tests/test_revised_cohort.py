"""Tests for cohort classifiers."""

from __future__ import annotations

import unittest

from ctgov_pipeline.classify_intervention_categories import classify_intervention_categories
from ctgov_pipeline.config_loader import load_yaml
from ctgov_pipeline.outcome_category import classify_outcome_category
from ctgov_pipeline.condition_eligibility import evaluate_condition_eligibility
from ctgov_pipeline.outcome_mechanism import (
    assess_primary_outcome_mechanistic,
    is_clinical_treatment_outcome,
    is_mechanistic_outcome,
)


class RevisedCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.intervention_config = load_yaml("intervention_categories.yaml")
        cls.condition_config = load_yaml("condition_patterns_cohort.yaml")

    def test_cbt_classified_as_psychological_cognitive(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Cognitive Behavioral Therapy"}],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)

    def test_psychophysical_maps_to_experimental_category(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "psychophysical tasks"}],
            self.intervention_config,
        )
        self.assertIn("experimental_research_paradigm", result.intervention_categories)

    def test_muscle_function_primary_not_mechanistic(self) -> None:
        self.assertTrue(is_clinical_treatment_outcome("Muscle function", None, None))
        self.assertFalse(is_mechanistic_outcome("Muscle function", None, None))
        self.assertFalse(
            assess_primary_outcome_mechanistic(
                [{"measure": "Muscle function", "description": None, "time_frame": None}]
            )
        )

    def test_visual_snow_retained_with_feature(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Visual Snow Syndrome", "Migraine", "Healthy"],
            keywords=[],
            config=self.condition_config,
            brief_title="Investigating Brain Function in People With Visual Snow Syndrome",
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("visual_snow", result.condition_feature_flags)

    def test_emotional_regulation_in_arm_name_classified(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "Emotional regulation smartphone task (PBrE)",
                    "description": "Delivered via app.",
                }
            ],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)

    def test_outcome_pain_intensity(self) -> None:
        cat = classify_outcome_category("Average pain intensity (NRS)", None, "8 weeks")
        self.assertEqual(cat.outcome_category, "pain_recovery")
        self.assertEqual(cat.outcome_subcategory, "pain_intensity")

    def test_short_outcome_uses_normal_rules(self) -> None:
        cat = classify_outcome_category("Pain", None, None)
        self.assertNotEqual(cat.outcome_subcategory, "uncertain")

    def test_mechanistic_outcome_category(self) -> None:
        cat = classify_outcome_category(
            "Functional connectivity (fMRI)", "Resting-state brain networks", "12 weeks"
        )
        self.assertEqual(cat.outcome_category, "mechanistic")
        self.assertEqual(cat.outcome_subcategory, "neuroimaging_neural")

    def test_acupuncture_control_by_name_only(self) -> None:
        result = classify_intervention_categories(
            [
                {"type": "DEVICE", "name": "Verum acupuncture"},
                {"type": "DEVICE", "name": "Sham acupuncture"},
                {
                    "type": "BEHAVIORAL",
                    "name": "Usual care",
                    "description": "Health education on lifestyle and migraine self-management.",
                },
            ],
            self.intervention_config,
        )
        self.assertEqual(result.intervention_categories, ["mind_body_integrative"])
        self.assertIn("usual_care", result.control_arm_types)

    def test_cbt_with_placebo_in_name_is_control(self) -> None:
        result = classify_intervention_categories(
            [
                {"type": "BEHAVIORAL", "name": "CBT with a placebo"},
            ],
            self.intervention_config,
        )
        self.assertEqual(result.intervention_categories, [])
        self.assertTrue(result.has_control_arm)

    def test_cbt_on_other_arm_type(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "OTHER",
                    "name": "CBT and milnacipran",
                    "description": "Eight telephone CBT sessions with milnacipran.",
                },
                {"type": "DRUG", "name": "milnacipran"},
            ],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)
        self.assertTrue(result.is_multimodal)


if __name__ == "__main__":
    unittest.main()
