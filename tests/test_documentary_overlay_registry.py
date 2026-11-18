"""Adversarial controls for the read-only documentary overlay inspector."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools import inspect_documentary_overlay as overlay

ROOT = Path(__file__).resolve().parents[1]


class DocumentaryOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = overlay.decode((ROOT / overlay.FEED_PATH).read_bytes())

    def test_read_only_canonical_and_idempotent(self):
        paths = [ROOT / overlay.REGISTRY_PATH, ROOT / overlay.PARENT_PATH, ROOT / overlay.FEED_PATH]
        before = [p.read_bytes() for p in paths]
        one = overlay.inspect_registry(ROOT)
        two = overlay.inspect_registry(ROOT)
        self.assertEqual(one, two)
        self.assertEqual(before, [p.read_bytes() for p in paths])
        self.assertEqual((one["feed_nodes"], one["feed_edges"], one["documentary_occurrences"]), (17, 20, 4))
        self.assertEqual(one["parent_ingestion"], "NOT_IMPLEMENTED")
        self.assertEqual((one["parent_added_observations"],
                          one["parent_added_physical_bridges"], one["delta_physical_domain"]), (0, 0, 0))
        self.assertEqual(one["crosswalk"][0]["classification"], "DOCUMENTARY_ONLY")

    def test_cli_check_runs_not_only_import(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/inspect_documentary_overlay.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        report = json.loads(proc.stdout)
        self.assertEqual(report["documentary_occurrences"], 4)
        self.assertEqual(report["parent_ingestion"], "NOT_IMPLEMENTED")

    def test_git_blob_pin_detects_byte_mutation(self):
        raw = (ROOT / overlay.FEED_PATH).read_bytes()
        self.assertEqual(overlay.blob_sha1(raw), overlay.FEED_GIT_SHA1)
        self.assertNotEqual(overlay.blob_sha1(raw + b"\\n"), overlay.FEED_GIT_SHA1)

    def reject_mutation(self, change):
        changed = copy.deepcopy(self.feed)
        change(changed)
        with self.assertRaises(ValueError):
            overlay.validate_feed(changed)

    def test_duplicate_occurrence_rejected(self):
        self.reject_mutation(lambda x: x["occurrences"].append(copy.deepcopy(x["occurrences"][0])))

    def test_orphan_edge_rejected(self):
        self.reject_mutation(lambda x: x["edges"].__setitem__(0, {
            "source": "SRC:FAKE", "target": "DOC:CM21658:P8",
            "relation": "SOURCE_MANIFEST_OR_BOUNDED_AUDIT"}))

    def test_crosswalk_source_swap_rejected(self):
        self.reject_mutation(lambda x: x["occurrences"][0].__setitem__("source_id", "SRC:R86"))

    def test_fake_event_time_rejected(self):
        self.reject_mutation(lambda x: x["occurrences"][0].__setitem__("event_time_utc", "1963-11-08T23:00:00Z"))

    def test_fake_physical_activation_rejected(self):
        self.reject_mutation(lambda x: x["nodes"][-1].__setitem__("activation", True))

    def test_fake_lean_promotion_rejected(self):
        self.reject_mutation(lambda x: x["nodes"][-3].__setitem__("status", "COMPILED"))

    def test_false_editorial_independence_rejected(self):
        self.reject_mutation(lambda x: x["sources"][1].__setitem__("editorial_family", "NEW_SENSOR"))

    def test_modern_search_as_historical_publication_rejected(self):
        self.reject_mutation(lambda x: x["occurrences"][3].__setitem__("publication_date", "1963-11-16"))

    def test_denominator_not_global_negative_rejected(self):
        self.reject_mutation(lambda x: x["coverage"].__setitem__("physical_absence_proven", True))

    def test_independence_claim_rejected(self):
        self.reject_mutation(lambda x: x["independence"].__setitem__("primary_event_witnesses_identified", 1))

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):
            overlay.decode(b'{"a":1,"a":2}')


if __name__ == "__main__":
    unittest.main()
