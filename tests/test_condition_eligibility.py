"""Tests for cohort condition eligibility rules."""

from __future__ import annotations

import unittest

from ctgov_pipeline.condition_eligibility import detect_review_flags, evaluate_condition_eligibility
from ctgov_pipeline.config_loader import load_yaml


class ConditionEligibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_yaml("condition_patterns_cohort.yaml")

    def test_cancer_excludes_multimorbidity_trial(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Cancer", "Migraine"],
            keywords=[],
            config=self.config,
            brief_title="Mindfulness trial",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "cancer_oncology")

    def test_post_concussive_headache_retained_with_feature_flag(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Post Concussive Headache"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("post_traumatic", result.condition_feature_flags)

    def test_tension_headache_eligible(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Tension-Type Headache"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("headache", result.targets_in_conditions)

    def test_migraine_and_headache_can_both_be_flagged(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Migraine", "Tension-Type Headache"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("migraine", result.targets_in_conditions)
        self.assertIn("headache", result.targets_in_conditions)

    def test_migraine_in_eligibility_text_does_not_drop_headache(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Tension-Type Headache"],
            keywords=[],
            config=self.config,
            eligibility_criteria="Inclusion Criteria: TTH. Exclusion Criteria: Diagnosis of migraine",
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertEqual(result.targets_in_conditions, ["headache"])

    def test_pain_comma_body_part_conditions_flag_targets(self) -> None:
        for condition, target in [
            ("Pain, Head", "headache"),
            ("Pain, Back", "chronic_back_pain"),
            ("Fybromyalgia", "fibromyalgia"),
        ]:
            result = evaluate_condition_eligibility(
                conditions=[condition], keywords=[], config=self.config
            )
            self.assertIn(target, result.targets_in_conditions, condition)

    def test_pregnancy_related_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_title="Yoga for Pregnancy-Related Low Back Pain",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "pregnancy_related")
        self.assertIn("regnan", result.exclusion_detail)

    def test_pregnancy_word_in_eligibility_text_only_does_not_exclude(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Low Back Pain"],
            keywords=[],
            config=self.config,
            eligibility_criteria="Inclusion Criteria: chronic low back pain. Exclusion Criteria: pregnancy",
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_provider_level_review_flag_does_not_exclude(self) -> None:
        flags = detect_review_flags(
            brief_title="Clinical Decision Support for Patient Migraine Management",
            official_title=None,
            config=self.config,
        )
        self.assertEqual(flags, ["provider_or_system_level"])
        result = evaluate_condition_eligibility(
            conditions=["Migraine"],
            keywords=[],
            config=self.config,
            brief_title="Clinical Decision Support for Patient Migraine Management",
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertEqual(
            detect_review_flags(brief_title="Yoga for Back Pain", official_title=None, config=self.config), []
        )

    def test_subacute_and_perioperative_feature_flags(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Subacute Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_title="Perioperative education before spine surgery",
        )
        self.assertIn("subacute", result.condition_feature_flags)
        self.assertIn("perioperative", result.condition_feature_flags)

    def test_target_only_in_title_or_keywords_is_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Pain"],
            keywords=["Fibromyalgia"],
            config=self.config,
            brief_title="Yoga for Fibromyalgia",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "no_target_match")

    def test_many_non_target_conditions_not_excluded(self) -> None:
        """Registered comorbidities / overlapping conditions are not an exclusion rule."""
        result = evaluate_condition_eligibility(
            conditions=["ME/CFS", "Long COVID", "POTS", "Fibromyalgia"],
            keywords=[],
            config=self.config,
            brief_title="Swimming for individuals with ME/CFS",
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("fibromyalgia", result.targets_in_conditions)

    def test_acute_back_pain_excluded(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Acute Low Back Pain"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "acute_pain")

    def test_chronic_back_pain_not_excluded_as_acute(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Low Back Pain"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_cancer_mention_in_eligibility_only_does_not_exclude(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Low Back Pain"],
            keywords=[],
            config=self.config,
            eligibility_criteria="Inclusion: chronic LBP. Exclusion: history of cancer or malignancy.",
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_acute_in_exclusion_criteria_does_not_exclude_fibromyalgia(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Fibromyalgia"],
            keywords=[],
            config=self.config,
            eligibility_criteria=(
                "Inclusion Criteria: FM diagnosis.\n"
                "Exclusion Criteria: Pain associated with terminal illness, acute pain, "
                "or pain associated with specific organ damage."
            ),
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_acute_pain_in_registered_conditions_excludes(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Pain, Acute", "Traumatic Brain Injury"],
            keywords=[],
            config=self.config,
            brief_title="VR Pain Management in Acute Brain Injury",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "acute_pain")

    def test_chronic_headaches_in_title_eligible(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Headaches"],
            keywords=["headaches"],
            config=self.config,
            brief_title="Stress Management for Chronic Headaches",
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertIn("headache", result.targets_in_conditions)

    def test_generic_chronic_pain_with_comorbid_conditions_eligible(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Pain", "Osteoarthritis", "Depression", "Fibromyalgia"],
            keywords=[],
            config=self.config,
            brief_title="Chronic pain rehabilitation",
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_not_due_to_acute_trauma_in_inclusion_does_not_exclude(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Pain", "Fibromyalgia"],
            keywords=[],
            config=self.config,
            brief_title="Pain Rehabilitation Virtual Reality",
            eligibility_criteria=(
                "Inclusion Criteria:\n"
                "Musculoskeletal pain not due to acute trauma (e.g. active sprain).\n"
            ),
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_nct03537573_style_inclusion_excludes(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Acute Pain", "Headache"],
            keywords=[],
            config=self.config,
            brief_title="Opioid Prescribing for Acute Pain in Primary Care",
            eligibility_criteria=(
                "Patient Participants\n"
                "Inclusion Criteria:\n"
                'acute neck, back, or other musculoskeletal and headache diagnosis '
                '("acute" defined as no similar diagnosis in past 3 months).\n'
                "Exclusion Criteria:\n"
                "Cancer diagnosis\n"
                "Providers\n"
                "Inclusion Criteria:\n"
                "Primary care provider\n"
                "Exclusion Criteria:\n"
                "None"
            ),
        )
        self.assertEqual(result.eligibility, "excluded")

    def test_acute_pain_condition_still_excludes_pragmatic_trial(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Acute Pain", "Headache"],
            keywords=[],
            config=self.config,
            brief_title="Opioid Prescribing for Acute Non-Cancer Pain in Primary Care",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "acute_pain")

    def test_keywords_with_acute_not_used_for_exclusion(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Low Back Pain"],
            keywords=["Acute Pain"],
            config=self.config,
            brief_title="Mindfulness for chronic low back pain",
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_chronic_and_acute_conditions_eligible_when_inclusion_is_chronic(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Pain", "Acute Pain", "Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_title="CBT for chronic low back pain",
            eligibility_criteria=(
                "Inclusion Criteria:\n"
                "Chronic low back pain for at least 3 months.\n"
                "Exclusion Criteria:\n"
                "Acute injury within the past month.\n"
            ),
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_acute_inclusion_excludes_before_title(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_title="Preventing chronic pain after acute low back pain",
            eligibility_criteria=(
                "Inclusion Criteria:\n"
                "Adults with acute low back pain of less than 4 weeks duration.\n"
            ),
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "acute_pain")

    def test_acute_in_brief_summary_ignored_when_all_conditions_chronic(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_title="Pain education for chronic low back pain",
            brief_summary=(
                "Sessions include explanation about differences of acute and chronic pain, "
                "purpose of acute pain, and production of acute and chronic pain."
            ),
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertEqual(result.acute_population_rule, "chronic_conditions_skip_descriptor_acute")

    def test_acute_in_brief_summary_still_excludes_when_condition_not_chronic(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_summary="Participants with acute low back pain are enrolled.",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "acute_pain")

    def test_acute_pain_relief_medication_wording_is_not_a_population(self) -> None:
        """NCT04984720: pamphlet / drug wording in summary and eligibility."""
        result = evaluate_condition_eligibility(
            conditions=["Migraine"],
            keywords=[],
            config=self.config,
            brief_summary="Clinicians provide pamphlets on triggers, acute pain relief medications, prophylaxis.",
            eligibility_criteria=(
                "Inclusion Criteria:\n* Episodic or chronic migraine.\n"
                "* No modifications to acute pain relief medications is planned over the next 3 months.\n"
            ),
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_chronic_versus_acute_background_in_inclusion_eligible(self) -> None:
        """NCT02419131: 'chronic versus acute' is background, trial enrolls chronic PTH."""
        result = evaluate_condition_eligibility(
            conditions=["Post-traumatic Headache", "PTSD"],
            keywords=[],
            config=self.config,
            eligibility_criteria=(
                "Inclusion Criteria:\n"
                "We are focusing on chronic PTHA due to the high prevalence of chronic versus "
                "acute PTHA in this Veteran population.\n"
            ),
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_acute_episode_of_chronic_pain_is_chronic_population(self) -> None:
        """NCT03157544: chronic patients during an acute flare."""
        result = evaluate_condition_eligibility(
            conditions=["Pain, Chronic", "Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_summary="Pain Relief Kit for individuals suffering from an acute pain episode of chronic low back pain.",
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_acute_far_from_back_pain_phrase_does_not_exclude(self) -> None:
        """NCT02247050 pattern: 'back ... acute' must not span unrelated clauses."""
        result = evaluate_condition_eligibility(
            conditions=["Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_summary="Imaging tests for low back pain, antibiotics for acute sinusitis, imaging for headache.",
        )
        self.assertEqual(result.eligibility, "eligible")

    def test_treatment_guard_does_not_hide_real_acute_population(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Low Back Pain"],
            keywords=[],
            config=self.config,
            brief_summary="Adults with acute low back pain receive acute treatment in primary care.",
        )
        self.assertEqual(result.eligibility, "excluded")
        self.assertEqual(result.exclusion_rule, "acute_pain")

    def test_exclusion_detail_names_the_specific_cause(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Hypertension"],
            keywords=[],
            config=self.config,
        )
        self.assertEqual(result.exclusion_rule, "no_target_match")
        self.assertTrue(result.exclusion_detail)

    def test_chronic_inclusion_acute_exclusion_eligible(self) -> None:
        result = evaluate_condition_eligibility(
            conditions=["Chronic Low Back Pain"],
            keywords=[],
            config=self.config,
            eligibility_criteria=(
                "Inclusion Criteria\n"
                "Adults experiencing chronic low back pain for a duration of at least 6 months.\n"
                "18-85 years of age Exclusion Criteria\n"
                "Experiencing acute pain related to a recent injury or pain lasting less than 6 months.\n"
            ),
        )
        self.assertEqual(result.eligibility, "eligible")
        self.assertEqual(result.acute_population_rule, "chronic_inclusion_acute_excluded")


if __name__ == "__main__":
    unittest.main()
