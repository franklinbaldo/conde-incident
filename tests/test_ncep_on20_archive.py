"""Offline regression checks; no large PDF fixture or network in CI."""
import hashlib
import json
import unittest
from copy import deepcopy
from pathlib import Path
from tools.verify_ncep_on20_archived_pdf import check_manifest, verify_pdf

RECORD = json.loads((Path(__file__).resolve().parents[1] /
 "research/meteorology/ncep_on20_wayback_custody_20261112.json").read_text())


def synthetic():
    data = b"%PDF-1.4\n/Type /Page /Subtype /Image /Count 1\ntrailer /Root 1 0 R\n%%EOF\n"
    rec = deepcopy(RECORD)
    rec["preservation"].update(byte_length=len(data),
        sha256=hashlib.sha256(data).hexdigest(), page_object_count=1,
        image_object_count=1, page_tree_count_marker=1)
    return data, rec


class CustodyTest(unittest.TestCase):
    def test_link_and_unpromoted_claims(self):
        check_manifest(RECORD)
        self.assertEqual(RECORD["linked_pending_bridge"],
                         "research/constraints/nmc_y20175_pending_bridge.json")

    def test_verifier_exact_bytes(self):
        data, rec = synthetic()
        self.assertEqual(verify_pdf(data, rec)["page_objects"], 1)

    def test_tampered_bytes(self):
        data, rec = synthetic()
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            verify_pdf(data.replace(b"/Type /Page", b"/Type /Xage"), rec)

    def test_truncated_bytes(self):
        data, rec = synthetic()
        with self.assertRaisesRegex(ValueError, "byte length"):
            verify_pdf(data[:-1], rec)

    def test_forbid_1963_compatibility_promoted_without_proof(self):
        rec = deepcopy(RECORD)
        rec["applicability_to_1963"] = "PROVEN"
        with self.assertRaisesRegex(ValueError, "compatibility"):
            check_manifest(rec)

    def test_forbid_unverified_meteorology(self):
        rec = deepcopy(RECORD)
        rec["station_day_matches"] = 5
        with self.assertRaisesRegex(ValueError, "station/day"):
            check_manifest(rec)
