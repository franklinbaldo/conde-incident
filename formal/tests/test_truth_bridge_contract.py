"""Fail-closed synthetic contract tests: forecast soundness is NOT physical truth."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from evidence_registry import contracts, parse_rows  # noqa: E402

MATRIX = ROOT / "research/evidence_matrix_C001-C238_2026-11-11.md"
THEOREMS = ROOT / "formal" / "Conde1963" / "TruthBridge.lean"
AUDIT = ROOT / "formal" / "Conde1963" / "AxiomAudit.lean"


class TruthBridgeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = contracts(parse_rows(MATRIX.read_bytes()))
        cls.bridge = cls.export["truth_bridge_interface"]

    def test_physical_claims_fail_closed_and_truth_premise_uninstantiated(self):
        out = self.bridge
        self.assertEqual(out["version"], 1)
        self.assertEqual(out["lean_module"], "Conde1963/TruthBridge.lean")
        self.assertEqual(out["source_matrix_sha1"],
                         self.export["matrix_git_blob_sha1"])
        self.assertEqual(out["historical_zip_154_151"], "NOT_RUN")
        self.assertEqual(out["source_scenarios"],
                         "UNRESOLVED_OR_UNION_NOT_INTERSECTION")
        for key in (
            "forecast_output", "hypothetical_actual_ground_impact",
            "physical_time_window", "physical_geographic_region",
            "truth_link_proof", "current_physical_outcome",
        ):
            self.assertIsNone(out[key], key)
        for key in (
            "primary_tle_custody_verified",
            "independent_physical_holdout_529_passed",
            "numerical_error_enclosure_verified",
            "full_continuous_domain_cover_verified",
            "ground_impact_and_material_survival_verified",
            "simulator_prediction_soundness_proves_physical_truth",
        ):
            self.assertIs(out[key], False, key)

    def test_documentary_lineages_and_collisions_are_not_conflated(self):
        out = self.bridge
        self.assertEqual(out["unverified_orbital_element_occurrences"],
                         ["C25#1", "C179#1"])
        self.assertEqual(out["reported_incident_occurrence"], "C01#1")
        self.assertEqual(out["single_nasa_document_occurrences"],
                         ["C131#1", "C197#1"])
        self.assertEqual(out["nasa_documentary_lineage_count"], 1)
        self.assertEqual(out["nasa_independent_terminal_measurements"], 0)
        by_key = {(x["id"], x["occurrence"]): x
                  for x in self.export["entries"]}
        self.assertEqual(len(by_key), 241)
        self.assertEqual(
            {key: by_key[key]["line"] for key in [
                ("C25", 1), ("C179", 1), ("C01", 1),
                ("C131", 1), ("C197", 1),
            ]},
            {("C25", 1): 118, ("C179", 1): 839, ("C01", 1): 19,
             ("C131", 1): 502, ("C197", 1): 905})
        self.assertEqual(
            [(x["id"], x["occurrence"]) for x in self.export["entries"]
             if x["id"] in {"C44", "C45", "C46"}],
            [("C44", 1), ("C45", 1), ("C46", 1),
             ("C44", 2), ("C45", 2), ("C46", 2)])

    def test_every_exported_lean_theorem_is_audited_for_axioms(self):
        theorem_text = THEOREMS.read_text(encoding="utf-8")
        audit_text = AUDIT.read_text(encoding="utf-8")
        self.assertEqual(len(self.bridge["lean_obligations"]), 7)
        for theorem in self.bridge["lean_obligations"].values():
            self.assertIn("theorem " + theorem, theorem_text)
            self.assertIn("#print axioms Conde1963." + theorem, audit_text)
        required = set(self.bridge["must_verify"])
        self.assertIn("predicted_event_enclosure_does_not_certify_actual_event",
                      required)
        self.assertIn("external_truth_link_for_every_admissible_physical_state",
                      required)
        self.assertIn("nonempty_surviving_domain_with_universal_ground_impact_for_forcing",
                      required)


if __name__ == "__main__":
    unittest.main()
