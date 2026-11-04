"""Validate outcome categories against stored primary outcome text."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from ctgov_pipeline.config_loader import PROJECT_ROOT
from ctgov_pipeline.outcome_category import classify_outcome_category
from ctgov_pipeline.validate_outcome_categories import recompute_outcome_category, validate_outcome_row

FINAL_OUTCOMES = (
    PROJECT_ROOT / "data" / "processed" / "cohort" / "primary_outcomes.csv"
)


class OutcomeCategoryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if FINAL_OUTCOMES.is_file():
            cls.outcomes = pd.read_csv(FINAL_OUTCOMES)
            cls.included = cls.outcomes[cls.outcomes["cohort_inclusion_status"] == "included"]
        else:
            cls.outcomes = None
            cls.included = None

    def test_mechanistic_beats_biological_other_bucket(self) -> None:
        cat = classify_outcome_category(
            "Functional connectivity (fMRI)",
            "Resting-state brain networks",
            "12 weeks",
        )
        self.assertEqual(cat.outcome_category, "mechanistic")
        self.assertEqual(cat.outcome_subcategory, "neuroimaging_neural")

    def test_pain_intensity_rule_order(self) -> None:
        cat = classify_outcome_category("Average pain intensity (NRS)", None, "8 weeks")
        self.assertEqual(cat.outcome_category, "pain_recovery")
        self.assertEqual(cat.outcome_subcategory, "pain_intensity")

    def test_feasibility_before_general_pain(self) -> None:
        cat = classify_outcome_category(
            "Recruitment rate",
            "Number of participants enrolled per month",
            None,
        )
        self.assertEqual(cat.outcome_category, "feasibility_acceptability")
        self.assertEqual(cat.outcome_subcategory, "feasibility_recruitment")

    @unittest.skipUnless(FINAL_OUTCOMES.is_file(), "final cohort not built")
    def test_final_cohort_reclassification_matches_stored_categories(self) -> None:
        mismatches: list[str] = []
        for _, row in self.included.iterrows():
            validation = validate_outcome_row(row)
            if not validation.matches:
                mismatches.append(
                    f"{validation.outcome_id}: stored={validation.stored_category}/"
                    f"{validation.stored_subcategory} recomputed="
                    f"{validation.recomputed_category}/{validation.recomputed_subcategory}"
                )
        self.assertEqual(mismatches, [], "\n".join(mismatches[:25]))

    @unittest.skipUnless(FINAL_OUTCOMES.is_file(), "final cohort not built")
    def test_recompute_helper_matches_classify(self) -> None:
        row = self.included.iloc[0]
        cat, sub = recompute_outcome_category(row)
        direct = classify_outcome_category(
            row.get("primary_outcome_measure"),
            row.get("primary_outcome_description"),
            row.get("primary_outcome_time_frame"),
        )
        self.assertEqual((cat, sub), (direct.outcome_category, direct.outcome_subcategory))


if __name__ == "__main__":
    unittest.main()
