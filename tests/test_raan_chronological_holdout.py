"""Cervo regression: chronological holdouts only, not posterior inference."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from raan_chronological_holdout import (FIT_END, VALIDATION_END,
                                        build_manifest, split_label)


class ChronologicalSplitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "research/statistics/raan_527_528_529_1963.json").read_bytes()
        cls.manifest = build_manifest(cls.source)

    def test_membership_and_frozen_real_counts(self):
        m = self.manifest
        self.assertEqual(m["totals"], {"fit": 61, "validation": 23, "evaluation": 35})
        self.assertEqual(m["unique_total"], 119)
        self.assertEqual(m["duplicates_excluded"], {"527": 1, "528": 0, "529": 3})
        self.assertEqual([
            [len(m["memberships"][str(n)][block]) for block in ("fit", "validation", "evaluation")]
            for n in (527, 528, 529)
        ], [[15, 1, 4], [24, 13, 8], [22, 9, 23]])

    def test_exact_boundaries_are_left_closed(self):
        self.assertEqual(split_label(FIT_END), "validation")
        self.assertEqual(split_label(VALIDATION_END), "evaluation")
        from datetime import timedelta
        self.assertEqual(split_label(FIT_END - timedelta(microseconds=1)), "fit")
        self.assertEqual(split_label(VALIDATION_END - timedelta(microseconds=1)), "validation")
        with self.assertRaises(ValueError):
            split_label(datetime(1964, 1, 1, tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            split_label(datetime(1963, 3, 1))

    def test_disjoint_complete_and_ordered_per_object(self):
        m = self.manifest
        keys = []
        for norad, groups in m["memberships"].items():
            for block in ("fit", "validation", "evaluation"):
                epochs = groups[block]
                self.assertEqual(epochs, sorted(epochs))
                for epoch in epochs:
                    keys.append((norad, epoch))
                    d = datetime.fromisoformat(epoch.replace("Z", "+00:00"))
                    self.assertEqual(split_label(d), block)
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), m["unique_total"])

    def test_exact_mirror_duplicates_cannot_leak_into_another_set(self):
        doc = json.loads(self.source)
        original = self.manifest["memberships"]
        doc["records"].append(copy.deepcopy(doc["records"][0]))
        modified = build_manifest(json.dumps(doc).encode("utf-8"))
        self.assertEqual(original, modified["memberships"])
        self.assertEqual(self.manifest["totals"], modified["totals"])
        self.assertEqual(modified["duplicates_excluded"]["527"], 2)

    def test_conflicting_duplicate_is_rejected(self):
        doc = json.loads(self.source)
        row = copy.deepcopy(doc["records"][0])
        row["raan_deg"] += 1
        doc["records"].append(row)
        with self.assertRaisesRegex(ValueError, "conflicting RAAN"):
            build_manifest(json.dumps(doc).encode("utf-8"))

    def test_source_checksum_changes_when_source_bytes_change(self):
        edited = self.source + b" "
        self.assertNotEqual(
            self.manifest["source"]["sha256_of_exact_committed_json_bytes"],
            build_manifest(edited)["source"]["sha256_of_exact_committed_json_bytes"],
        )

    def test_manifest_is_byte_reproducible(self):
        m = json.loads((ROOT / "research/statistics/raan_chronological_holdout_1963.json").read_text())
        self.assertEqual(self.manifest, m)
        self.assertEqual(m["design_status"], "RETROSPECTIVE_TIME_SPLIT_NOT_BLINDED")
        self.assertEqual(m["independence_status"],
                         "SAME_SECONDARY_DOCUMENTARY_LINEAGE_NOT_INDEPENDENT")
        self.assertEqual(m["statistical_status"], "NO_FIT_NO_LIKELIHOOD_NO_POSTERIOR")
        self.assertTrue(m["no_observation_on_1963_11_08_for_528"])


if __name__ == "__main__":
    unittest.main()
