"""Simulation ↔ Lean snapshot audit. Tests inspect source, not orbital truth."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from simulation_bridge_audit import (  # noqa: E402
    LEGACY, CHECKS, BridgeAuditError, audit_files, git_blob_sha1
)


class SimulationBridgeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {path: (ROOT / path).read_bytes() for path in LEGACY}

    def test_pinned_sources_are_actual_git_blobs(self):
        for path, sha in LEGACY.items():
            self.assertEqual(git_blob_sha1(self.sources[path]), sha)

    def test_complete_snapshot_with_negative_findings(self):
        report = audit_files(self.sources)
        self.assertEqual(report["checked_file_count"], 5)
        self.assertEqual(report["finding_count"],
                         sum(len(checks) for checks in CHECKS.values()))
        self.assertEqual(report["status"], "STATIC_SOURCE_INSPECTION_ONLY")
        self.assertEqual(report["lean"]["certifies_typescript_execution"], False)
        self.assertEqual(report["actual_1963_ground_impact"], None)
        self.assertEqual(report["calibrated_uncertainty_probability"], None)

    def test_source_change_must_not_silently_invalidate_audit(self):
        altered = dict(self.sources)
        path = "src/lib/monteCarlo.ts"
        altered[path] = altered[path] + b"\n// changed source\n"
        with self.assertRaisesRegex(BridgeAuditError, "SHA drift"):
            audit_files(altered)

    def test_missing_known_limit_requires_human_review(self):
        altered = dict(self.sources)
        path = "src/lib/astrodynamics.ts"
        altered[path] = altered[path].replace(
            b"new Date('1963-11-08T23:59:59Z')",
            b"new Date('1963-11-09T00:00:00Z')",
        )
        with self.assertRaisesRegex(BridgeAuditError, "catalogue_midnight_cutoff"):
            audit_files(altered, verify_sha=False)

    def test_missing_source_rejected(self):
        altered = dict(self.sources)
        altered.pop("norad528_reconstruction.py")
        with self.assertRaisesRegex(BridgeAuditError, "missing simulation source"):
            audit_files(altered)

    def test_no_false_historical_certificate_from_castor_status(self):
        report = audit_files(self.sources)
        castor = report["castor"]
        self.assertEqual(castor["historical_holdout"], "NOT_RUN")
        self.assertEqual(castor["lean_proof_of_typescript"], "NOT_RUN")
        self.assertIsNone(castor["terminal_location"])
        self.assertIsNone(castor["ground_impact"])
        self.assertTrue(all(x.startswith("src/lib/") for x in castor["modules"]))

    def test_source_refs_and_lineage_cannot_be_multipled(self):
        report = audit_files(self.sources)
        ids = {r["id"] for r in report["findings"]}
        self.assertIn("catalogue_midnight_cutoff", ids)
        self.assertIn("independent_terminal_phase", ids)
        self.assertIn("legacy_orbit_angle", ids)
        cutoff = next(r for r in report["findings"]
                      if r["id"] == "catalogue_midnight_cutoff")
        self.assertEqual(cutoff["evidence_occurrences"], ["C131#1", "C197#1"])
        self.assertTrue(all("/blob/" in f["url"] for f in report["findings"]))

    def test_audit_is_not_a_trajectory_calculation(self):
        report = audit_files(self.sources)
        self.assertEqual(report["lean"]["symbolic_drag_sign_only"], True)
        self.assertEqual(report["lean"]["sample_radius_counts_not_probabilities"], True)
        self.assertEqual(report["castor"]["status"],
                         "SOURCE_TEXT_READ_ONLY_NOT_EXECUTED_BY_THIS_AUDIT")


if __name__ == "__main__":
    unittest.main()
