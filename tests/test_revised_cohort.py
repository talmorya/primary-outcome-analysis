"""Tests for revised cohort classifiers."""

from __future__ import annotations

import unittest

from ctgov_pipeline.classify_intervention_categories import classify_intervention_categories
from ctgov_pipeline.config_loader import load_yaml
from ctgov_pipeline.intervention_eligibility import (
    evaluate_intervention_eligibility,
    evaluate_mechanism_exclusion,
)
from ctgov_pipeline.outcome_category import classify_outcome_category
from ctgov_pipeline.condition_eligibility import evaluate_condition_eligibility
from ctgov_pipeline.outcome_mechanism import (
    assess_primary_outcome_mechanistic,
    evaluate_outcome_mechanism_exclusion,
    is_clinical_treatment_outcome,
    is_mechanistic_outcome,
)


class RevisedCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.intervention_config = load_yaml("intervention_categories.yaml")
        cls.condition_config = load_yaml("condition_patterns_proposed.yaml")

    def test_cbt_classified_as_psychological_cognitive(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Cognitive Behavioral Therapy"}],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)

    def test_exercise_classified_and_eligible(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Aerobic exercise program"}],
            self.intervention_config,
        )
        self.assertIn("physical_rehabilitation", result.intervention_categories)
        self.assertTrue(evaluate_intervention_eligibility(result).intervention_eligible)

    def test_psychophysical_mechanism_excluded(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "psychophysical tasks"}],
            self.intervention_config,
        )
        self.assertFalse(evaluate_intervention_eligibility(result).intervention_eligible)
        record = {
            "protocolSection": {
                "outcomesModule": {
                    "primaryOutcomes": [
                        {"measure": "Pain threshold (QST)", "description": "", "timeFrame": "baseline"},
                    ],
                    "secondaryOutcomes": [
                        {"measure": "Conditioned pain modulation", "description": "", "timeFrame": "8 weeks"},
                    ],
                },
            }
        }
        mech = evaluate_mechanism_exclusion(classification=result, record=record)
        self.assertTrue(mech.mechanism_excluded)  # descriptive flag; cohort no longer excludes on this

    def test_mechanistic_primary_with_clinical_other_included(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Mindfulness training"}],
            self.intervention_config,
        )
        record = {
            "protocolSection": {
                "outcomesModule": {
                    "primaryOutcomes": [
                        {"measure": "Brain activity (fMRI)", "description": "", "timeFrame": "12 weeks"},
                    ],
                    "otherOutcomes": [
                        {"measure": "Headache disability (MIDAS)", "description": "", "timeFrame": "12 weeks"},
                    ],
                },
            }
        }
        mech = evaluate_mechanism_exclusion(classification=result, record=record)
        self.assertFalse(mech.mechanism_excluded)
        self.assertTrue(mech.primary_outcome_mechanistic)
        self.assertTrue(mech.has_clinical_outcome_anywhere)

    def test_hrv_primary_pain_in_other_included(self) -> None:
        assessment = evaluate_outcome_mechanism_exclusion(
            [
                {"outcome_type": "primary", "measure": "Heart rate variability", "description": "", "time_frame": "8 weeks"},
                {"outcome_type": "primary", "measure": "Biceps curl repetitions", "description": "", "time_frame": "8 weeks"},
                {"outcome_type": "other", "measure": "Change in Current Pain Intensity", "description": "", "time_frame": "8 weeks"},
            ]
        )
        self.assertFalse(assessment.mechanism_excluded)
        self.assertFalse(assessment.primary_outcome_mechanistic)

    def test_muscle_function_primary_not_mechanistic(self) -> None:
        self.assertTrue(is_clinical_treatment_outcome("Muscle function", None, None))
        self.assertFalse(is_mechanistic_outcome("Muscle function", None, None))
        self.assertFalse(
            assess_primary_outcome_mechanistic(
                [{"measure": "Muscle function", "description": None, "time_frame": None}]
            )
        )

    def test_gait_primary_not_mechanistic(self) -> None:
        self.assertTrue(is_clinical_treatment_outcome("Change in rapid measure of gait", None, None))
        self.assertFalse(
            assess_primary_outcome_mechanistic(
                [
                    {"measure": "Change in rapid measure of gait", "description": None, "time_frame": None},
                    {"measure": "Change in measure of inducible dizziness", "description": None, "time_frame": None},
                ]
            )
        )

    def test_tms_primary_remains_mechanistic(self) -> None:
        self.assertTrue(
            assess_primary_outcome_mechanistic(
                [
                    {
                        "measure": "Motor cortical map and excitability from transcranial magnetic stimulation",
                        "description": None,
                        "time_frame": None,
                    }
                ]
            )
        )

    def test_visual_snow_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Visual Snow Syndrome", "Migraine", "Healthy"],
            keywords=[],
            config=self.condition_config,
            brief_title="Investigating Brain Function in People With Visual Snow Syndrome",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "visual_snow")

    def test_vestibular_schwannoma_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Migraine", "Vestibular Schwannoma", "Dizziness"],
            keywords=[],
            config=self.condition_config,
            brief_title="Vestibular compensation after schwannoma intervention",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "vestibular_schwannoma")

    def test_me_cfs_primary_without_target_in_title_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["ME/CFS", "Long COVID", "POTS", "Fibromyalgia"],
            keywords=[],
            config=self.condition_config,
            brief_title="Swimming for individuals with ME/CFS",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "off_target_primary_population")

    def test_pbre_treatment_included(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "PBrE",
                    "description": "Emotional regulation word task via smartphone app.",
                }
            ],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)
        record = {
            "protocolSection": {
                "designModule": {"designInfo": {"primaryPurpose": "TREATMENT"}},
                "descriptionModule": {},
            }
        }
        self.assertFalse(evaluate_mechanism_exclusion(classification=result, record=record).mechanism_excluded)

    def test_outcome_pain_intensity(self) -> None:
        cat = classify_outcome_category("Average pain intensity (NRS)", None, "8 weeks")
        self.assertEqual(cat.outcome_category, "pain_recovery")
        self.assertEqual(cat.outcome_subcategory, "pain_intensity")

    def test_prt_maps_to_neuroplastic_recovery(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Pain reprocessing therapy (PRT)"}],
            self.intervention_config,
        )
        self.assertIn("neuroplastic_recovery_therapy", result.intervention_categories)

    def test_eaet_maps_to_neuroplastic_recovery(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "Emotional Awareness and Expression Therapy (EAET)",
                }
            ],
            self.intervention_config,
        )
        self.assertIn("neuroplastic_recovery_therapy", result.intervention_categories)

    def test_mechanistic_outcome_category(self) -> None:
        cat = classify_outcome_category(
            "Functional connectivity (fMRI)", "Resting-state brain networks", "12 weeks"
        )
        self.assertEqual(cat.outcome_category, "mechanistic")
        self.assertEqual(cat.outcome_subcategory, "neuroimaging_neural")

    def test_acupuncture_not_multimodal_with_behavioral_control(self) -> None:
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
        # DEVICE delivery may set multimodal_modalities=device even when control is behavioral usual care
        self.assertIn("device", result.multimodal_modalities)

    def test_outcome_disability(self) -> None:
        cat = classify_outcome_category("Roland Morris Disability Questionnaire", None, None)
        self.assertEqual(cat.outcome_category, "pain_interference")
        self.assertEqual(cat.outcome_subcategory, "disability")

    def test_usual_care_comparator_skips_description_categories(self) -> None:
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

    def test_acupuncture_on_device_arm(self) -> None:
        result = classify_intervention_categories(
            [
                {"type": "DEVICE", "name": "Verum acupuncture"},
                {"type": "DEVICE", "name": "Sham acupuncture"},
                {"type": "BEHAVIORAL", "name": "Usual care"},
            ],
            self.intervention_config,
        )
        self.assertIn("mind_body_integrative", result.intervention_categories)
        self.assertTrue(evaluate_intervention_eligibility(result).intervention_eligible)

    def test_cbt_not_control_when_waitlist_in_description(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "CBT or MBSR",
                    "description": "Participants on waitlist receive CBT after follow-up.",
                }
            ],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)
        self.assertTrue(evaluate_intervention_eligibility(result).intervention_eligible)

    def test_cbt_on_other_arm_type(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "OTHER",
                    "name": "CBT and milnacipran",
                    "description": "Eight telephone CBT sessions with milnacipran.",
                },
                {"type": "DRUG", "name": "milnacipran"},
                {"type": "BEHAVIORAL", "name": "CBT with a placebo"},
            ],
            self.intervention_config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)
        self.assertTrue(result.is_multimodal)


if __name__ == "__main__":
    unittest.main()
