"""Adversarial C241-P33 checks: exact archive coverage is not as-of eligibility."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_causal_flux_recovery import (  # noqa: E402
    EXTRACT, EXTRACT_SHA, SOURCE, audit, extract_data, verify_full_archive
)


def changed(lines):
    return ("\n".join(lines) + "\n").encode("ascii")


class RealSolarBackfillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = EXTRACT.read_bytes()
        cls.parent = SOURCE.read_bytes()

    def test_sha_and_full_window_dates(self):
        data = extract_data(self.raw)
        self.assertEqual(len(data), 40)
        self.assertEqual(str(min(data)), "1963-08-18")
        self.assertEqual(str(max(data)), "1963-09-26")
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), EXTRACT_SHA)

    def test_exact_retrospective_results(self):
        result = audit(self.raw, self.parent)
        self.assertEqual(
            [r["trailing_81_observed_sfu"] for r in result["rows"]],
            ["84.34074074074074074074074074",
             "84.29382716049382716049382716",
             "84.24444444444444444444444444"])
        self.assertEqual(
            [r["backfilled_dates_used"] for r in result["rows"]], [40, 39, 38])
        self.assertTrue(all(r["missing_after_backfill"] == 0 for r in result["rows"]))

    def test_no_asof_inference_from_retrospective_archive(self):
        result = audit(self.raw, self.parent)
        self.assertEqual(result["release_vintage"], "UNKNOWN")
        self.assertEqual(result["physical_constraint"], "CONNECTED_PENDING_CALIBRATION")
        self.assertEqual(result["causal_forecast_score"], "NOT_RUN")
        self.assertTrue(all(
            not r["prospective_eligible"] and
            not r["historical_release_timestamp_audited"] and
            not r["standard_centered_f107a_replaced"] and
            r["historical_orbit_inference"] == "NOT_RUN"
            for r in result["rows"]))

    def test_single_numeric_tamper_fails_sha(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_BYTES_HASH_MISMATCH"):
            extract_data(self.raw.replace(b"80.4", b"80.5", 1))

    def test_duplicate_date_rejected_even_with_rehashed_input(self):
        rows = self.raw.decode().splitlines()
        cols = rows[1].split(",")
        cols[4] = " 18"
        rows[1] = ",".join(cols)
        raw = changed(rows)
        with self.assertRaisesRegex(ValueError, "DUPLICATE_DATE"):
            extract_data(raw, hashlib.sha256(raw).hexdigest())

    def test_missing_date_rejected_even_with_rehashed_input(self):
        raw = changed(self.raw.decode().splitlines()[:-1])
        with self.assertRaisesRegex(ValueError, "MISSING_OR_EXTRA_DATE"):
            extract_data(raw, hashlib.sha256(raw).hexdigest())

    def test_bad_value_rejected_even_with_rehashed_input(self):
        raw = self.raw.replace(b" 80.4,", b"   .0,", 1)
        with self.assertRaisesRegex(ValueError, "NONPOSITIVE_OR_NONFINITE_FLUX"):
            extract_data(raw, hashlib.sha256(raw).hexdigest())

    def test_parent_lineage_mismatch_fails(self):
        changed_parent = json.loads(self.parent)
        changed_parent["source_documents"]["F107"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "DIFFERENT_SOURCE_LINEAGE"):
            audit(self.raw, json.dumps(changed_parent).encode())

    def test_unrelated_archive_rejected(self):
        with self.assertRaisesRegex(ValueError, "FULL_SOURCE_BYTES_HASH_MISMATCH"):
            verify_full_archive(b"not the original archive", self.raw)


if __name__ == "__main__":
    unittest.main()
