"""Tests for eligibility criteria inclusion/exclusion parsing."""

from __future__ import annotations

import unittest

from ctgov_pipeline.eligibility_text import (
    extract_exclusion_blocks,
    extract_inclusion_blocks,
    split_inclusion_exclusion_eligibility,
)


class EligibilityTextTests(unittest.TestCase):
    def test_multiple_inclusion_blocks(self) -> None:
        text = (
            "Patient Participants\n"
            "Inclusion Criteria:\n"
            "Age 18+; acute neck pain.\n"
            "Exclusion Criteria:\n"
            "Cancer.\n"
            "Providers\n"
            "Inclusion Criteria:\n"
            "Primary care provider.\n"
            "Exclusion Criteria:\n"
            "None\n"
        )
        blocks = extract_inclusion_blocks(text)
        self.assertEqual(len(blocks), 2)
        self.assertIn("acute neck", blocks[0].lower())
        self.assertIn("primary care", blocks[1].lower())

    def test_inline_exclusion_header_truncates_inclusion_block(self) -> None:
        text = (
            "Inclusion Criteria\n"
            "Chronic low back pain at least 6 months.\n"
            "18-85 years of age Exclusion Criteria\n"
            "Acute pain lasting less than 6 months.\n"
        )
        blocks = extract_inclusion_blocks(text)
        self.assertEqual(len(blocks), 1)
        self.assertIn("chronic", blocks[0].lower())
        self.assertNotIn("acute pain", blocks[0].lower())
        excl = extract_exclusion_blocks(text)
        self.assertEqual(len(excl), 1)
        self.assertIn("acute", excl[0].lower())

    def test_splits_general_exclusion_block(self) -> None:
        text = (
            "General Inclusion Criteria:\n"
            "Verified diagnosis of FMS.\n"
            "General Exclusion Criteria:\n"
            "Acute pain not related to the FMS.\n"
        )
        incl, excl = split_inclusion_exclusion_eligibility(text)
        self.assertIn("FMS", incl)
        self.assertIn("Acute pain", excl)
        self.assertNotIn("Acute pain", incl)


if __name__ == "__main__":
    unittest.main()
