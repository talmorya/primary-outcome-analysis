import unittest

from ctgov_pipeline.config_loader import _merge


class MergeOverlayTests(unittest.TestCase):
    def test_overlay_adds_keys_and_replaces_leaves(self) -> None:
        base = {"targets": {"migraine": {"label": "Migraine", "patterns": ["a"]}}, "version": "1"}
        overlay = {"targets": {"chronic_pain": {"label": "Chronic pain", "patterns": ["b"]}, "migraine": {"patterns": ["c"]}}}
        merged = _merge(base, overlay)
        self.assertEqual(set(merged["targets"]), {"migraine", "chronic_pain"})
        self.assertEqual(merged["targets"]["migraine"], {"label": "Migraine", "patterns": ["c"]})  # lists replaced, siblings kept
        self.assertEqual(merged["version"], "1")
        self.assertEqual(base["targets"]["migraine"]["patterns"], ["a"])  # inputs untouched


if __name__ == "__main__":
    unittest.main()
