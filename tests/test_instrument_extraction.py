"""Regression tests for instrument extraction."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from ctgov_pipeline.config_loader import load_yaml
from ctgov_pipeline.extract_outcome_features import extract_instruments, extract_outcome_features

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OLD_PILOT_OUTCOMES = (
    PROJECT_ROOT / "data" / "processed" / "pilot" / "pilot_20260818_141318" / "primary_outcomes.csv"
)


class InstrumentExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lexicon = load_yaml("outcome_lexicon.yaml")

    def test_hads_true_positive(self) -> None:
        text = (
            "Assessment with Hospital Anxiety and Depression Scale in caregivers (HADS): "
            "Screening instrument for the detection of affective disorders."
        )
        instruments = extract_instruments(text, self.lexicon)
        self.assertIn("Hospital Anxiety and Depression Scale", instruments)

    def test_eep10_acronym_only(self) -> None:
        text = "Assessment with EEP-10. The Spanish version of the EEP-10 used by Remor."
        acronyms = extract_outcome_features("stress", text, None, self.lexicon).acronyms_detected
        self.assertIn("EEP-10", acronyms)
        self.assertNotIn("Insomnia Severity Index", extract_instruments(text, self.lexicon))

    def test_numeric_pain_rating_scale_not_isi(self) -> None:
        text = (
            "Change is being assessed between two time points by The Numeric Pain Rating Scale. "
            "Self-report current pain rating on a 0-10 scale."
        )
        instruments = extract_instruments(text, self.lexicon)
        self.assertIn("Numeric Rating Scale", instruments)
        self.assertNotIn("Insomnia Severity Index", instruments)

    def test_visible_app_not_isi(self) -> None:
        text = "Daily symptoms will be recorded in the Visible app each evening."
        instruments = extract_instruments(text, self.lexicon)
        self.assertEqual(instruments, [])

    def test_patient_global_impression_not_isi(self) -> None:
        text = "Patient Global Impression of Improvement (PGI-I): A 7-point scale."
        instruments = extract_instruments(text, self.lexicon)
        self.assertNotIn("Insomnia Severity Index", instruments)

    def test_hrv_not_isi(self) -> None:
        text = "Heart Rate Variability. HRV will be collected each morning upon waking."
        instruments = extract_instruments(text, self.lexicon)
        self.assertNotIn("Insomnia Severity Index", instruments)

    def test_no_instrument_plain_symptoms(self) -> None:
        text = "Symptoms. Daily symptoms will be recorded."
        instruments = extract_instruments(text, self.lexicon)
        self.assertEqual(instruments, [])

    def test_fiq_true_positive(self) -> None:
        text = "Fibromyalgia Impact Questionnaire (FIQ): assessing quality of life."
        instruments = extract_instruments(text, self.lexicon)
        self.assertIn("Fibromyalgia Impact Questionnaire", instruments)
        self.assertNotIn("Insomnia Severity Index", instruments)

    def test_old_pilot_false_positive_rate_improved(self) -> None:
        if not OLD_PILOT_OUTCOMES.exists():
            self.skipTest("Old pilot outcomes file not available")

        import pandas as pd

        outcomes = pd.read_csv(OLD_PILOT_OUTCOMES)
        false_positive_cases = [
            ("NCT03819907__po_1", []),
            ("NCT07454395__po_1", []),
            ("NCT07454395__po_2", []),
            ("NCT07203339__po_2", []),
            ("NCT07203339__po_4", []),
            ("NCT07203339__po_6", []),
            ("NCT05658185__po_1", ["Hospital Anxiety and Depression Scale"]),
            ("NCT06406699__po_1", ["PEG-3"]),
        ]
        for outcome_id, expected in false_positive_cases:
            row = outcomes.loc[outcomes["outcome_id"] == outcome_id].iloc[0]
            detected = extract_instruments(
                " ".join(
                    str(row[col]) for col in [
                        "primary_outcome_measure",
                        "primary_outcome_description",
                        "primary_outcome_time_frame",
                    ]
                    if str(row[col]) != "nan"
                ),
                self.lexicon,
            )
            self.assertEqual(detected, expected, msg=outcome_id)


if __name__ == "__main__":
    unittest.main()
