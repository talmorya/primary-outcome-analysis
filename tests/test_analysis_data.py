"""Tests for the analysis notebook's data preparation."""

from __future__ import annotations

import unittest

import pandas as pd

from ctgov_pipeline.analysis_data import add_derived_columns, cohort_summary_table, outcome_by_group


def _tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    base = {
        "eligible_back_pain": False, "eligible_fibromyalgia": False, "eligible_migraine": False, "eligible_headache": False,
        "raw_study_first_post_date": "2020-05-01", "exclusion_detail": None, "exclusion_reason": None,
    }
    rows = [
        {**base, "nct_id": "N1", "cohort_inclusion_status": "included", "intervention_categories": "psychological_cognitive | physical_rehabilitation",
         "is_multimodal": False, "eligible_back_pain": True},
        {**base, "nct_id": "N2", "cohort_inclusion_status": "included", "intervention_categories": "physical_rehabilitation",
         "is_multimodal": True, "eligible_migraine": True},
        {**base, "nct_id": "N3", "cohort_inclusion_status": "included", "intervention_categories": "", "is_multimodal": False},
        {**base, "nct_id": "N4", "cohort_inclusion_status": "excluded", "intervention_categories": "physical_rehabilitation",
         "is_multimodal": False, "exclusion_reason": "acute", "exclusion_detail": "acute_pain: found"},
    ]
    studies = pd.DataFrame(rows)
    out = pd.DataFrame(
        [
            ("N1", "included", "pain_recovery", "pain_intensity"),
            ("N1", "included", "pain_interference", "disability"),
            ("N1", "included", "other", "not_an_outcome_measure"),
            ("N2", "included", "pain_recovery", "pain_intensity"),
            ("N4", "excluded", "pain_recovery", "pain_intensity"),
        ],
        columns=["nct_id", "cohort_inclusion_status", "outcome_category", "outcome_subcategory"],
    )
    out["outcome_id"] = range(len(out))
    return add_derived_columns(studies, out), out


class AnalysisDataTests(unittest.TestCase):
    def test_summary_counts(self) -> None:
        studies, outcomes = _tables()
        summary = cohort_summary_table(studies, outcomes).set_index("Metric")["Value"]
        self.assertEqual(summary["Master pool (before filtering)"], "4")
        self.assertEqual(summary["Final analytic cohort"], "3")
        self.assertEqual(summary["Excluded"], "1")
        self.assertEqual(summary["Primary outcome rows (included trials)"], "4")
        self.assertEqual(summary["Studies with more than one primary outcome"], "1")
        self.assertEqual(summary["Mean primary outcomes per study"], "2.00")
        self.assertEqual(summary["Multimodal intervention trials"], "1")
        self.assertEqual(summary["Included trials with no registered primary outcome"], "1")

    def test_crosstab_counts_each_group_and_drops_not_an_outcome(self) -> None:
        studies, outcomes = _tables()
        ct = outcome_by_group(studies, outcomes)
        # N1 (two categories) feeds both groups; N2 only physical_rehabilitation; not_an_outcome_measure and excluded N4 dropped.
        self.assertEqual(ct.rows.loc["physical_rehabilitation", "pain_recovery"], 2)
        self.assertEqual(ct.rows.loc["psychological_cognitive", "pain_interference"], 1)
        self.assertEqual(ct.n_rows_total, 3)
        self.assertNotIn("other", ct.rows.columns)
        self.assertEqual(ct.trial_percent().loc["physical_rehabilitation", "pain_recovery"], 100.0)

    def test_study_filter(self) -> None:
        studies, outcomes = _tables()
        ct = outcome_by_group(studies, outcomes, study_query="is_multimodal == False")
        self.assertEqual(ct.rows.loc["physical_rehabilitation", "pain_recovery"], 1)
        self.assertEqual(ct.n_trials_total, 1)

    def test_condition_group(self) -> None:
        studies, outcomes = _tables()
        ct = outcome_by_group(studies, outcomes, group="condition_list")
        self.assertEqual(set(ct.rows.index), {"Back pain", "Migraine"})


if __name__ == "__main__":
    unittest.main()
