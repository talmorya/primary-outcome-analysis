"""Tests for eligibility-text helpers."""

from __future__ import annotations

import unittest

from ctgov_pipeline.config_loader import load_yaml
from ctgov_pipeline.eligibility_text import (
    extract_inclusion_blocks,
    extract_pain_duration_sentences,
    find_chronic_inclusion_cue,
)


class EligibilityTextTests(unittest.TestCase):
    def test_pain_duration_sentence_for_reference_trial(self) -> None:
        text = (
            "Inclusion Criteria:\n"
            "* 18-64 years old\n"
            "* Current non-specific low back pain persisting >12 weeks. "
            "Mean low back pain intensity for the previous week 4 or greater.\n"
            "Exclusion Criteria:\n"
            "* Pregnancy\n"
        )
        found = extract_pain_duration_sentences(text)
        self.assertEqual(found, ["Current non-specific low back pain persisting >12 weeks."])

    def test_duration_ignores_medication_stability_clause(self) -> None:
        text = (
            "Inclusion Criteria:\n"
            "* Patients must be on their current headache medications for the last 3 months.\n"
        )
        self.assertEqual(extract_pain_duration_sentences(text), [])

    def _cue(self, text: str) -> str:
        spec = load_yaml("condition_patterns_cohort.yaml")["flag_exclusion"][
            "keep_when_chronic_in_inclusion"
        ]
        return find_chronic_inclusion_cue(
            text,
            word_patterns=spec["word_patterns"],
            duration_patterns=spec["duration_patterns"],
        )

    def test_chronic_cue_duration_variants(self) -> None:
        for sentence in (
            "Low back pain for at least 3 months.",
            "Back pain >= 6 months",
            "Pain duration \\> 12 weeks",
            "Back pain lasting more than 1 year",
            "Back pain of at least 3 consecutive months",
            "Pain for ≥3 months or more",
            "Spine pain for 3+ months",
        ):
            with self.subTest(sentence=sentence):
                text = f"Inclusion Criteria:\n* {sentence}\nExclusion Criteria:\n* Pregnancy"
                self.assertTrue(self._cue(text))

    def test_chronic_cue_word_in_inclusion(self) -> None:
        text = "Inclusion Criteria:\n* Chronic low back pain\nExclusion Criteria:\n* None"
        self.assertTrue(self._cue(text))

    def test_chronic_cue_ignores_exclusion_section(self) -> None:
        text = (
            "Inclusion Criteria:\n* Back pain after surgery\n"
            "Exclusion Criteria:\n* Chronic opioid use\n* Pain for more than 3 months"
        )
        self.assertEqual(self._cue(text), "")

    def test_chronic_cue_needs_pain_context_for_duration(self) -> None:
        text = "Inclusion Criteria:\n* Surgery at least 3 months ago\nExclusion Criteria:\n* None"
        self.assertEqual(self._cue(text), "")

    def test_chronic_cue_rejects_short_windows(self) -> None:
        text = "Inclusion Criteria:\n* Back pain for more than 2 weeks\nExclusion Criteria:\n* None"
        self.assertEqual(self._cue(text), "")

    def test_inclusion_blocks_still_work(self) -> None:
        text = "Inclusion Criteria:\nAdults with migraine.\nExclusion Criteria:\nPregnancy."
        self.assertTrue(extract_inclusion_blocks(text))


if __name__ == "__main__":
    unittest.main()
