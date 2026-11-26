"""Tests for the analysis notebook's data preparation."""

from __future__ import annotations

import unittest

import pandas as pd

from ctgov_pipeline.analysis_data import (
    add_derived_columns,
    cohort_summary_table,
    companion_outcome_table,
    companions,
    condition_outcome_table,
    cooccurrence,
    fisher_exact_two_sided,
    outcome_by_group,
    psychological_subtypes,
    subtype_outcome_table,
    wilson_interval,
)


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

    def test_cooccurrence_and_companions(self) -> None:
        studies, outcomes = _tables()
        counts = cooccurrence(studies)
        self.assertEqual(counts.loc["physical_rehabilitation", "physical_rehabilitation"], 2)  # excluded N4 not counted
        self.assertEqual(counts.loc["physical_rehabilitation", "psychological_cognitive"], 1)
        self.assertEqual(counts.loc["psychological_cognitive", "physical_rehabilitation"], 1)
        n_total, comp = companions(studies, "physical_rehabilitation")
        self.assertEqual(n_total, 2)
        self.assertEqual(comp["(none: only this category)"], 1)  # N2 alone
        self.assertEqual(comp["psychological_cognitive"], 1)

    def test_companion_outcome_table(self) -> None:
        studies, outcomes = _tables()
        table = companion_outcome_table(studies, outcomes, "psychological_cognitive", min_n=1).set_index("group")
        self.assertNotIn("only_this_category", table.index)  # the only psychological trial also has physical rehab
        self.assertEqual(table.loc["with_any_other_category", "n"], 1)
        self.assertEqual(table.loc["with_any_other_category", "pain_interference"], 1)
        self.assertEqual(table.loc["physical_rehabilitation", "pain_recovery"], 1)

    def test_fisher_and_wilson(self) -> None:
        self.assertAlmostEqual(fisher_exact_two_sided(3, 10, 7, 10), 0.1789, places=3)
        self.assertAlmostEqual(fisher_exact_two_sided(5, 10, 5, 10), 1.0)
        lo, hi = wilson_interval(23, 39)
        self.assertTrue(43 < lo < 44 and 72 < hi < 74)

    def test_condition_outcome_table(self) -> None:
        studies, outcomes = _tables()
        table = condition_outcome_table(studies, outcomes, "psychological_cognitive").set_index(["condition", "group"])
        self.assertEqual(table.loc[("Back pain", "with_any_other_category"), "n"], 1)  # N1: psychological + physical rehab
        self.assertEqual(table.loc[("Back pain", "with_any_other_category"), "pain_interference"], 1)
        self.assertEqual(table.loc[("Back pain", "only_this_category"), "n"], 0)
        self.assertEqual(table.loc[("Migraine", "other_trials"), "n"], 1)  # N2
        self.assertEqual(table.loc[("Migraine", "other_trials"), "pain_recovery"], 1)

    def test_psychological_subtypes(self) -> None:
        details = {
            "A": "Cognitive-behavioral therapy [BEHAVIORAL]: weekly sessions",
            "B": "ACT group [BEHAVIORAL]: acceptance work || Waitlist control [OTHER]: CBT after the study",  # CBT only in a control arm
            "C": "Mindfulness-Based Stress Reduction [BEHAVIORAL]: 8 weeks",
            "D": "Pain education [BEHAVIORAL]: we act on beliefs; psychotherapy sessions",  # the word "act" is not ACT
        }
        studies = pd.DataFrame(
            {
                "nct_id": list(details),
                "cohort_inclusion_status": "included",
                "has_psychological_cognitive": True,
                "n_intervention_categories": [1, 2, 2, 1],
                "raw_intervention_details": list(details.values()),
            }
        ).set_index("nct_id", drop=False)
        result = psychological_subtypes(studies).set_index("nct_id")
        self.assertEqual(result.loc["A", ["CBT", "ACT", "MBSR"]].tolist(), [True, False, False])
        self.assertTrue(result.loc["D", "Psychotherapy"])  # the word "act" is not ACT, but psychotherapy is named
        self.assertFalse(result.loc["A", "Behavioral activation / therapy"])  # "cognitive-behavioral therapy" is CBT only
        self.assertEqual(result.loc["B", ["CBT", "ACT", "MBSR"]].tolist(), [False, True, False])
        self.assertEqual(result.loc["C", ["CBT", "ACT", "MBSR"]].tolist(), [False, False, True])
        self.assertEqual(result.loc["D", ["CBT", "ACT", "MBSR"]].tolist(), [False, False, False])
        self.assertTrue(result.loc["D", "Psychotherapy"])
        self.assertFalse(result.loc["D", "No named subtype"])

        outcomes = pd.DataFrame(
            {
                "nct_id": ["A", "B", "C", "D"],
                "cohort_inclusion_status": "included",
                "outcome_category": ["pain_recovery", "pain_interference", "pain_interference", "pain_recovery"],
                "outcome_subcategory": "x",
            }
        )
        everything = subtype_outcome_table(studies, outcomes).set_index("subtype")
        pure = subtype_outcome_table(studies, outcomes, pure_only=True).set_index("subtype")
        self.assertEqual(everything.loc["CBT", "trials"], 1)
        self.assertEqual(pure.loc["ACT", "trials"], 0)  # B also carries another category
        self.assertEqual(pure.loc["Psychotherapy", "trials"], 1)  # D
        self.assertEqual(pure.loc["Psychotherapy", "pain_recovery"], 1)


if __name__ == "__main__":
    unittest.main()
