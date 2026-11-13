"""Offline audit: a Wayback copy is the same document, not a second observation."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "research/archive/coruja_wayback_live_comparison_20261113.json").read_text())
CUSTODY = json.loads((ROOT / "research/archive/wayback_pilot_2026-11-12.json").read_text())


class CorujaArchiveComparisonTest(unittest.TestCase):
    def test_timestamped_live_audit_has_three_distinct_documents(self):
        self.assertEqual(DATA["schema"], "conde.coruja.archive-live-replay-comparison/v1")
        self.assertTrue(DATA["observed_at_utc"].startswith("2026-11-13T"))
        self.assertEqual({r["id"] for r in DATA["records"]},
                         {"WB-NORAD-1963-H2", "WB-SAO-RU301", "WB-NASA-SSR-19631115"})
        self.assertEqual(len({r["source_family"] for r in DATA["records"]}), 3)

    def test_verified_wayback_replays_equal_original_downloaded_bytes(self):
        by_id = {r["id"]: r for r in CUSTODY["records"]}
        for observed in DATA["records"]:
            recorded = by_id[observed["id"]]
            self.assertEqual(observed["original_url"], recorded["original_url"])
            self.assertEqual(observed["original"]["http_status"], 200)
            self.assertEqual(observed["original"]["content_type"], "application/pdf")
            self.assertTrue(observed["original"]["pdf_header"])
            self.assertTrue(observed["original"]["pdf_eof"])
            if recorded["status"] == "VERIFIED_REPLAY":
                self.assertTrue(observed["byte_identity_observed"])
                self.assertEqual(observed["replay_url"], recorded["archived_url"])
                self.assertEqual(observed["capture_utc"], recorded["capture_utc"])
                self.assertEqual(observed["replay"]["bytes"], recorded["replay"]["bytes"])
                self.assertEqual(observed["original"]["bytes"], recorded["replay"]["bytes"])
                self.assertEqual(observed["original"]["sha256"], recorded["replay"]["sha256"])
                self.assertEqual(observed["replay"]["sha256"], recorded["replay"]["sha256"])
            else:
                self.assertEqual(recorded["status"], "NO_EXACT_CAPTURE_IN_QUERIED_INDEX")
                self.assertIsNone(observed["replay_url"])
                self.assertIsNone(observed["replay"])
                self.assertIsNone(observed["byte_identity_observed"])
                self.assertEqual(observed["exact_wayback_lookup"], recorded["status"])

    def test_not_claimed_as_new_physical_observation(self):
        limitations = " ".join(DATA["limitations"]).lower()
        for term in ("not independent", "1963", "no tracking epoch", "not absence"):
            self.assertIn(term, limitations)


if __name__ == "__main__":
    unittest.main()
