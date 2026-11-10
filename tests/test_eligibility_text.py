"""Tests for eligibility-text helpers."""

from __future__ import annotations

import unittest

from ctgov_pipeline.eligibility_text import (
    extract_inclusion_blocks,
    extract_pain_duration_sentences,
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

    def test_inclusion_blocks_still_work(self) -> None:
        text = "Inclusion Criteria:\nAdults with migraine.\nExclusion Criteria:\nPregnancy."
        self.assertTrue(extract_inclusion_blocks(text))


if __name__ == "__main__":
    unittest.main()
