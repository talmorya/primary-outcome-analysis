"""Regression tests for intervention taxonomy classification."""

from __future__ import annotations

import unittest

from ctgov_pipeline.classify_interventions import classify_interventions
from ctgov_pipeline.config_loader import load_yaml


class InterventionClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_yaml("intervention_taxonomy.yaml")

    def test_cognitive_functional_therapy(self) -> None:
        result = classify_interventions(
            [{"type": "BEHAVIORAL", "name": "Cognitive Functional Therapy (CFT)"}],
            self.config,
        )
        self.assertIn("cognitive_functional_therapy", result.behavioral_component)
        self.assertFalse(result.non_psychological_behavioral_flag)

    def test_coping_skills_training(self) -> None:
        result = classify_interventions(
            [{"type": "BEHAVIORAL", "name": "PainCOACH Pain Coping Skills Training"}],
            self.config,
        )
        self.assertIn("coping_skills_training", result.behavioral_component)
        self.assertFalse(result.non_psychological_behavioral_flag)

    def test_motivational_interviewing(self) -> None:
        result = classify_interventions(
            [{"type": "BEHAVIORAL", "name": "motivational interviewing"}],
            self.config,
        )
        self.assertIn("motivational_interviewing", result.behavioral_component)

    def test_exposure_therapy(self) -> None:
        result = classify_interventions(
            [{"type": "BEHAVIORAL", "name": "Exposure therapy"}],
            self.config,
        )
        self.assertIn("exposure_therapy", result.behavioral_component)

    def test_research_paradigm_not_psychological(self) -> None:
        result = classify_interventions(
            [{"type": "BEHAVIORAL", "name": "psychophysical tasks"}],
            self.config,
        )
        self.assertEqual(result.behavioral_component, [])
        self.assertTrue(result.non_psychological_behavioral_flag)
        self.assertIn("research_paradigm", result.non_psychological_behavioral_type or "")

    def test_operant_paradigm_excluded(self) -> None:
        result = classify_interventions(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "psychophysical tasks",
                    "description": "operant learning paradigm",
                }
            ],
            self.config,
        )
        self.assertNotIn("operant_behavioral", result.behavioral_component)
        self.assertIn("research_paradigm", result.non_psychological_behavioral_type or "")

    def test_expanded_psychoeducation(self) -> None:
        result = classify_interventions(
            [{"type": "BEHAVIORAL", "name": "Migraine education"}],
            self.config,
        )
        self.assertIn("psychoeducation", result.behavioral_component)

    def test_emotional_regulation_not_research_paradigm(self) -> None:
        result = classify_interventions(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "PBrE",
                    "description": (
                        "PbRE is a word reading task through an App. The patient will choose "
                        "emotional positive and negative words related to personal characteristics."
                    ),
                }
            ],
            self.config,
        )
        self.assertEqual(result.behavioral_component, ["other_psychological"])
        self.assertNotIn("research_paradigm", result.non_psychological_behavioral_type or "")

    def test_light_habituation_treatment_not_research_paradigm(self) -> None:
        result = classify_interventions(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "Light exposure (Flash)",
                    "description": (
                        "Light exposure (Flash) is administered for one hour on 7 consecutive days."
                    ),
                },
                {
                    "type": "BEHAVIORAL",
                    "name": "Light deprivation (Dark)",
                    "description": (
                        "Light deprivation (Dark) is administered for one hour on 7 consecutive days."
                    ),
                },
            ],
            self.config,
        )
        self.assertEqual(result.behavioral_component, [])
        self.assertIn("lifestyle_general", result.non_psychological_behavioral_type or "")
        self.assertNotIn("research_paradigm", result.non_psychological_behavioral_type or "")


if __name__ == "__main__":
    unittest.main()
