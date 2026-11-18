"""Tests for cohort classifiers."""

from __future__ import annotations

import unittest

from ctgov_pipeline.build_revised_cohort import dedupe_records_by_nct_id
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

    def test_amygdala_retraining_is_neuroplastic(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Amygdala Retraining Program"}],
            self.intervention_config,
        )
        self.assertIn("neuroplastic_recovery_therapy", result.intervention_categories)

    def test_ergonomics_maps_to_occupational_rtw(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Occupational ergonomic training"}],
            self.intervention_config,
        )
        self.assertIn("occupational_ergonomics_rtw", result.intervention_categories)

    def test_back_book_is_education(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "The Back Book"}],
            self.intervention_config,
        )
        self.assertIn("education_self_management", result.intervention_categories)

    def test_hyphenated_emdr_is_psychological(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Eye-Movement-Desensitization-Reprocessing"}],
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

    def test_pure_control_names_do_not_trigger_other(self) -> None:
        for name in (
            "Control",
            "Usual care",
            "Standard Care",
            "Standard of care",
            "Treatment as Usual",
            "Treatment as Usual (TAU)",
            "Typical care",
            "Business as usual",
        ):
            with self.subTest(name=name):
                result = classify_intervention_categories(
                    [{"type": "BEHAVIORAL", "name": name}],
                    self.intervention_config,
                )
                self.assertEqual(result.intervention_categories, [])
                self.assertTrue(result.has_control_arm)
                self.assertNotIn("other_behavioral_treatment", result.intervention_categories)

    def test_control_arm_ignored_while_active_arm_categorized(self) -> None:
        result = classify_intervention_categories(
            [
                {"type": "BEHAVIORAL", "name": "ABM"},
                {"type": "BEHAVIORAL", "name": "Control"},
            ],
            self.intervention_config,
        )
        self.assertEqual(result.intervention_categories, ["other_behavioral_treatment"])
        self.assertTrue(result.has_control_arm)
        self.assertIn("other_control", result.control_arm_types)

    def test_motor_control_not_treated_as_comparator(self) -> None:
        result = classify_intervention_categories(
            [{"type": "BEHAVIORAL", "name": "Motor control exercises"}],
            self.intervention_config,
        )
        self.assertFalse(result.has_control_arm)
        self.assertIn("physical_rehabilitation", result.intervention_categories)

    def test_tau_plus_active_treatment_not_comparator(self) -> None:
        result = classify_intervention_categories(
            [
                {"type": "BEHAVIORAL", "name": "TAU + FIBRO-On"},
                {"type": "OTHER", "name": "Treatment as Usual (TAU)"},
            ],
            self.intervention_config,
        )
        self.assertTrue(result.has_control_arm)
        self.assertIn("usual_care", result.control_arm_types)
        self.assertIn("other_behavioral_treatment", result.intervention_categories)

    def test_embedded_control_word_with_active_therapy_stays_active(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "OTHER",
                    "name": "Experimental and control condition: Museum therapy",
                }
            ],
            self.intervention_config,
        )
        self.assertFalse(result.has_control_arm)
        self.assertIn("other_behavioral_treatment", result.intervention_categories)

    def test_standard_of_care_arm_does_not_leak_categories(self) -> None:
        result = classify_intervention_categories(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "Standard of care treatment for Fibromyalgia",
                    "description": "Exercise, CBT, education, and occupational therapy as usual.",
                },
                {
                    "type": "BEHAVIORAL",
                    "name": "Longitudinal Behavioral Health Techniques",
                },
            ],
            self.intervention_config,
        )
        self.assertTrue(result.has_control_arm)
        self.assertEqual(result.intervention_categories, ["other_behavioral_treatment"])
        self.assertNotIn("psychological_cognitive", result.intervention_categories)
        self.assertNotIn("education_self_management", result.intervention_categories)

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

    def test_dedupe_records_by_nct_id_keeps_first(self) -> None:
        def rec(nct: str, title: str) -> dict:
            return {"protocolSection": {"identificationModule": {"nctId": nct, "briefTitle": title}}}

        records = [rec("NCT1", "a"), rec("NCT2", "b"), rec("NCT1", "dup")]
        unique, removed = dedupe_records_by_nct_id(records)
        self.assertEqual(removed, 1)
        self.assertEqual([r["protocolSection"]["identificationModule"]["nctId"] for r in unique], ["NCT1", "NCT2"])
        self.assertEqual(unique[0]["protocolSection"]["identificationModule"]["briefTitle"], "a")


if __name__ == "__main__":
    unittest.main()
