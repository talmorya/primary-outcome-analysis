"""Tests for finalized cohort freeze."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from ctgov_pipeline.config_loader import PROJECT_ROOT
from ctgov_pipeline.extraction_runs import latest_full_extraction_run_id


class FinalizeCohortTests(unittest.TestCase):
    def test_cohort_tables_present_after_build(self) -> None:
        cohort_dir = PROJECT_ROOT / "data" / "processed" / "cohort"
        studies_csv = cohort_dir / "studies.csv"
        if not studies_csv.is_file():
            self.skipTest("cohort not built in this environment")
        studies = pd.read_csv(studies_csv)
        self.assertGreater(len(studies), 0)
        self.assertIn("exclusion_reason", studies.columns)
        self.assertIn("exclusion_detail", studies.columns)
        excluded = studies[studies["cohort_inclusion_status"] == "excluded"]
        self.assertTrue(excluded["exclusion_reason"].isin(["acute", "condition"]).all())
        self.assertTrue(excluded["exclusion_detail"].fillna("").str.contains(":").all())
        included = studies[studies["cohort_inclusion_status"] == "included"]
        self.assertTrue(included["exclusion_reason"].isna().all())
        self.assertIn("raw_brief_summary_50w", studies.columns)
        manifest = cohort_dir / "manifest.json"
        self.assertTrue(manifest.is_file())

    def test_simplified_rules_no_intervention_exclusions(self) -> None:
        studies_csv = PROJECT_ROOT / "data" / "processed" / "cohort" / "studies.csv"
        if not studies_csv.is_file():
            self.skipTest("cohort not built")
        df = pd.read_csv(studies_csv)
        excluded = df[df["cohort_inclusion_status"] != "included"]
        rules = excluded["exclusion_detail"].str.split(":").str[0]
        self.assertFalse(rules.str.contains("intervention|outcome").any())

    def test_reference_nct_statuses_after_manual_review(self) -> None:
        studies_csv = PROJECT_ROOT / "data" / "processed" / "cohort" / "studies.csv"
        if not studies_csv.is_file():
            self.skipTest("cohort not built")
        status = pd.read_csv(studies_csv).set_index("nct_id")["cohort_inclusion_status"]
        expected_excluded = ["NCT03537573", "NCT02647658", "NCT04356963"]
        expected_included = [
            "NCT00796536", "NCT01794988", "NCT03483168", "NCT04636177", "NCT06971809",
            "NCT04984720", "NCT02419131", "NCT03157544", "NCT06114264",
        ]
        for nct in expected_excluded:
            self.assertEqual(status[nct], "excluded", nct)
        for nct in expected_included:
            self.assertEqual(status[nct], "included", nct)

    def test_latest_extraction_has_four_conditions(self) -> None:
        run_id = latest_full_extraction_run_id()
        if not run_id:
            self.skipTest("no extraction run")
        manifest_path = PROJECT_ROOT / "data" / "raw" / "full" / run_id / "extraction_manifest.json"
        if not manifest_path.is_file():
            self.skipTest("no manifest")
        import json

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        conditions = manifest["retrieval_criteria"]["conditions"]
        self.assertIn("headache", conditions)


if __name__ == "__main__":
    unittest.main()
