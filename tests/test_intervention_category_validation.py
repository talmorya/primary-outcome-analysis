"""Validate intervention categories against raw CT.gov intervention descriptions."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from ctgov_pipeline.classify_intervention_categories import classify_intervention_categories
from ctgov_pipeline.config_loader import PROJECT_ROOT, load_yaml
from ctgov_pipeline.validate_intervention_categories import (
    categories_for_arm,
    load_interventions_from_row,
    parse_pipe_field,
    validate_intervention_categories,
)

FINAL_COHORT_STUDIES = (
    PROJECT_ROOT / "data" / "processed" / "studies.csv"
)

ACUPUNCTURE_USUAL_CARE_ARMS = [
    {"type": "DEVICE", "name": "Verum acupuncture"},
    {"type": "DEVICE", "name": "Sham acupuncture"},
    {
        "type": "BEHAVIORAL",
        "name": "Usual care",
        "description": (
            "Health education on lifestyle changes, behavioral therapies, "
            "and migraine self-management."
        ),
    },
]


class InterventionCategoryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_yaml("intervention_categories.yaml")
        if FINAL_COHORT_STUDIES.is_file():
            cls.included = pd.read_csv(FINAL_COHORT_STUDIES)
            cls.included = cls.included[cls.included["cohort_inclusion_status"] == "included"]
        else:
            cls.included = None

    def test_comparator_checked_before_category_patterns(self) -> None:
        """Usual-care arm text must not assign lifestyle/CBT categories (NCT02765581 pattern)."""
        result = classify_intervention_categories(ACUPUNCTURE_USUAL_CARE_ARMS, self.config)
        self.assertEqual(result.intervention_categories, ["mind_body_integrative"])
        self.assertTrue(result.has_control_arm)

        usual_care = ACUPUNCTURE_USUAL_CARE_ARMS[2]
        self.assertEqual(categories_for_arm(usual_care, self.config), [])

    def test_cbt_in_description_not_control_when_arm_is_active_treatment(self) -> None:
        """Waitlist in description must not demote an active CBT arm to comparator."""
        result = classify_intervention_categories(
            [
                {
                    "type": "BEHAVIORAL",
                    "name": "CBT or MBSR",
                    "description": "Participants on waitlist receive CBT after follow-up.",
                }
            ],
            self.config,
        )
        self.assertIn("psychological_cognitive", result.intervention_categories)
        self.assertFalse(result.has_control_arm)

    @unittest.skipUnless(FINAL_COHORT_STUDIES.is_file(), "final cohort not built")
    def test_final_cohort_reclassification_matches_stored_categories(self) -> None:
        mismatches: list[str] = []
        for _, row in self.included.iterrows():
            interventions = load_interventions_from_row(row)
            assigned = parse_pipe_field(row["intervention_categories"])
            recomputed = classify_intervention_categories(interventions, self.config)
            if recomputed.intervention_categories != assigned:
                mismatches.append(
                    f"{row['nct_id']}: stored={assigned} recomputed={recomputed.intervention_categories}"
                )
        self.assertEqual(mismatches, [], "\n".join(mismatches[:30]))

    @unittest.skipUnless(FINAL_COHORT_STUDIES.is_file(), "final cohort not built")
    def test_all_categories_supported_by_treatment_arm_text(self) -> None:
        unsupported: dict[str, list[str]] = {}
        for _, row in self.included.iterrows():
            interventions = load_interventions_from_row(row)
            assigned = parse_pipe_field(row["intervention_categories"])
            validation = validate_intervention_categories(
                nct_id=row["nct_id"],
                interventions=interventions,
                assigned_categories=assigned,
                config=self.config,
            )
            if validation.unsupported_categories:
                unsupported[row["nct_id"]] = validation.unsupported_categories
        self.assertEqual(
            unsupported,
            {},
            "Re-run build_revised_cohort and finalize_cohort after classifier fix:\n"
            + "\n".join(f"{k}: {v}" for k, v in list(unsupported.items())[:15]),
        )


if __name__ == "__main__":
    unittest.main()
