"""Tests for finalized cohort freeze."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from ctgov_pipeline.config_loader import PROJECT_ROOT
from ctgov_pipeline.finalize_cohort import EXPECTED_ELIGIBLE_STUDIES, finalize_cohort


class FinalizeCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.final_dir = finalize_cohort()

    def test_final_cohort_size(self) -> None:
        studies = pd.read_csv(self.final_dir / "studies.csv")
        eligible = studies[studies["cohort_included"] == True]
        self.assertEqual(len(eligible), EXPECTED_ELIGIBLE_STUDIES)

    def test_nct00864422_manual_decision(self) -> None:
        studies = pd.read_csv(self.final_dir / "studies.csv")
        row = studies[studies["nct_id"] == "NCT00864422"].iloc[0]
        self.assertTrue(row["cohort_included"])
        self.assertTrue(row["primary_outcome_mechanistic"])
        self.assertTrue(row["has_clinical_outcome_anywhere"])

    def test_nct01118988_manual_decision(self) -> None:
        studies = pd.read_csv(self.final_dir / "studies.csv")
        row = studies[studies["nct_id"] == "NCT01118988"].iloc[0]
        self.assertTrue(row["cohort_included"])

    def test_manifest_present(self) -> None:
        manifest = self.final_dir / "cohort_manifest.json"
        self.assertTrue(manifest.is_file())

    def test_production_extraction_unchanged(self) -> None:
        production_manifest = (
            PROJECT_ROOT / "data" / "processed" / "full" / "full_20260823_201251" / "extraction_manifest.json"
        )
        self.assertTrue(production_manifest.is_file())
        studies = pd.read_csv(
            PROJECT_ROOT / "data" / "processed" / "full" / "full_20260823_201251" / "studies.csv"
        )
        self.assertEqual(len(studies), 674)


if __name__ == "__main__":
    unittest.main()
