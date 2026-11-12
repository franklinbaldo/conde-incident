"""Matrix-to-Lean contracts: deterministic coverage, no evidence promotion."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from evidence_registry import (  # noqa: E402
    InventoryError, audit, contracts, parse_rows, render_lean
)

MATRIX = ROOT / "research" / "evidence_matrix_C001-C238_2026-11-11.md"
LEAN = ROOT / "formal" / "Conde1963" / "MatrixEvidence.lean"


class MatrixEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = MATRIX.read_bytes()
        cls.rows = parse_rows(cls.raw)

    def test_full_documentary_inventory(self):
        report = audit(self.raw, self.rows)
        self.assertEqual(report["occurrences"], 241)
        self.assertEqual(report["unique_labels"], 238)
        self.assertEqual(report["collision_labels"], ["C44", "C45", "C46"])

    def test_collisions_not_overwritten(self):
        for number, expected_lines in {
            44: [164, 175], 45: [165, 176], 46: [166, 177]
        }.items():
            records = [r for r in self.rows if r["number"] == number]
            self.assertEqual([r["occurrence"] for r in records], [1, 2])
            self.assertEqual([r["line"] for r in records], expected_lines)

    def test_generated_lean_in_repository_matches_matrix_exactly(self):
        self.assertEqual(LEAN.read_text(encoding="utf-8"), render_lean(self.rows))

    def test_mutated_source_blob_is_rejected(self):
        tampered = self.raw.replace(b"| C01 |", b"| C99 |", 1)
        self.assertNotEqual(tampered, self.raw)
        with self.assertRaisesRegex(InventoryError, "blob changed"):
            audit(tampered, parse_rows(tampered))

    def test_missing_row_rejected_even_without_blob_guard(self):
        fewer = [r for r in self.rows if r["number"] != 238]
        with self.assertRaisesRegex(InventoryError, "241 rows"):
            audit(self.raw, fewer, strict_hash=False)

    def test_duplicate_occurrence_rejected(self):
        corrupted = [dict(row) for row in self.rows]
        second = next(r for r in corrupted if r["number"] == 44 and r["occurrence"] == 2)
        second["occurrence"] = 1
        with self.assertRaisesRegex(InventoryError, "occurrence"):
            audit(self.raw, corrupted, strict_hash=False)

    def test_unjustified_filter_promotion_rejected(self):
        corrupted = [dict(row) for row in self.rows]
        corrupted[0]["role"] = "nasaReportedDecayDay"
        with self.assertRaisesRegex(InventoryError, "unreviewed physical promotion"):
            audit(self.raw, corrupted, strict_hash=False)


    def test_uncertainty_is_explicit_for_every_record(self):
        out = contracts(self.rows)
        self.assertEqual(out["schema_version"], 2)
        self.assertEqual(len(out["entries"]), 241)
        self.assertEqual(
            sum(x["epistemic_uncertainty"] == "requiresIndividualAssessment"
                for x in out["entries"]), 238
        )
        self.assertTrue(all(x["epistemic_uncertainty"] and x["uncertainty_basis"]
                            for x in out["entries"]))
        self.assertTrue(all(x["numeric_error_bounds"] is None
                            for x in out["entries"]))
        self.assertEqual([x["id"] for x in out["entries"]
                          if x["epistemic_uncertainty"] ==
                          "reportedCatalogueDayActualDayUnknown"], ["C131", "C197"])

    def test_promoting_uncertainty_without_review_is_rejected(self):
        altered = [dict(row) for row in self.rows]
        altered[0]["uncertainty"] = "reportedCatalogueDayActualDayUnknown"
        with self.assertRaisesRegex(InventoryError, "uncertainty promotion"):
            audit(self.raw, altered, strict_hash=False)


    def test_outcome_handoff_cannot_claim_a_physical_prediction(self):
        out = contracts(self.rows)
        interface = out["outcome_interface"]
        self.assertEqual(interface["version"], 1)
        self.assertEqual(interface["kind"],
                         "CONDITIONAL_OUTCOME_PROOF_OBLIGATIONS_NOT_OBSERVATIONS")
        self.assertIsNone(interface["current_result"])
        self.assertIsNone(interface["calibrated_model"])
        self.assertIsNone(interface["numerical_impact_window"])
        self.assertEqual(
            {v["code"] for v in interface["conditional_outcomes"]},
            {"CONTRADICTORY_PREMISES", "CONDE_FORCED", "CONDE_EXCLUDED",
             "OTHER_WINDOW", "INDETERMINATE"}
        )
        for v in interface["conditional_outcomes"]:
            self.assertTrue(v["lean"])
            self.assertTrue(v["scope"])
            self.assertTrue(v["warning"])
        self.assertIn("global_coverage_proof_or_explicit_finite_grid_scope",
                      interface["required_inputs"])
        self.assertIn("ground_impact_model_distinct_from_orbital_decay",
                      interface["required_inputs"])
        self.assertEqual(sum(
            e["physical_encoding"] ==
            "NASA_CATALOGUED_DATE_HYPOTHESIS_NOT_HARD_FILTER"
            for e in out["entries"]), 2)

    def test_enclosure_handoff_is_fail_closed_and_source_aware(self):
        out = contracts(self.rows)
        env = out["enclosure_interface"]
        self.assertEqual(env["version"], 1)
        self.assertEqual(env["kind"],
                         "MODEL_ENCLOSURE_OBLIGATIONS_NOT_NUMERICAL_RESULTS")
        self.assertEqual(env["lean_module"], "Conde1963/Enclosures.lean")
        self.assertEqual(env["ground_impact_gate"], "GroundImpactAdmissible")
        self.assertEqual(env["enclosure_soundness"],
                         "ImpactEnvelope.soundForPredictions")
        self.assertIsNone(env["current_result"])
        self.assertIsNone(env["event_type"])
        self.assertIsNone(env["numerical_epoch_window_utc"])
        self.assertIsNone(env["numerical_spatial_enclosure"])
        for key in (
            "global_parameter_domain_verified",
            "ground_impact_audit_verified",
            "historical_input_custody_verified",
            "independent_holdout_verified",
            "numerical_error_coverage_verified",
        ):
            self.assertIs(env[key], False)
        self.assertEqual(env["original_154_151_corpus_import"], "NOT_RUN")
        self.assertEqual({c["code"] for c in env["conditional_certificates"]},
                         {"CONDE_EXCLUDED", "CONDE_FORCED", "OTHER_WINDOW"})
        self.assertEqual(env["conditional_certificates"][0]
                         ["impact_elsewhere_implied"], False)
        self.assertEqual(env["conditional_certificates"][2]
                         ["impact_elsewhere_implied"], True)
        self.assertIn("nonempty_full_admissible_parameter_domain",
                      env["mandatory_proof_obligations"])
        self.assertIn("proof_actual_predicted_event_is_inside_its_enclosure",
                      env["mandatory_proof_obligations"])
        self.assertEqual(env["source_lineage"][0]["matrix_occurrences"], ["C01#1"])
        self.assertEqual(env["source_lineage"][1]["matrix_occurrences"],
                         ["C131#1", "C197#1"])
        self.assertEqual(env["source_lineage"][1]["independent_sources"], 1)
        self.assertIs(env["source_lineage"][1]["physical_day_admitted"], False)
        self.assertEqual(len(out["entries"]), 241)
        self.assertTrue(all(x["numeric_error_bounds"] is None
                            for x in out["entries"]))


    def test_unresolved_raan_branches_are_fail_closed_and_disjunctive(self):
        interface = contracts(self.rows)["unresolved_element_scenarios_interface"]
        self.assertEqual(interface["version"], 1)
        self.assertEqual(interface["admissible_semantics"],
                         "COMMON_AND_LEFT_OR_RIGHT")
        self.assertEqual(interface["branch_combination_allowed"],
                         "DISJUNCTION_ONLY_UNTIL_SOURCE_ADJUDICATION")
        self.assertIsNone(interface["current_scenario"])
        self.assertIsNone(interface["chosen_physical_constraints"])
        self.assertIsNone(interface["numerically_supported_bounds"])
        self.assertEqual(interface["historical_orbit_validation"], "NOT_RUN")
        self.assertEqual(interface["original_tle_custody"], "NOT_VERIFIED")
        self.assertEqual(interface["independent_source_lineages"],
                         "NOT_ESTABLISHED")
        self.assertFalse(interface["physical_reference_frame_reconciled"])
        self.assertFalse(interface["holdout_529_passed"])
        self.assertFalse(interface["all_branch_error_enclosures_verified"])
        self.assertEqual({x["id"] for x in interface["alternatives"]}, {
            "SITE_RAAN_284_UNVERIFIED", "AFSPC_MIRROR_RAAN_198_UNVERIFIED"
        })
        self.assertEqual([x["raan_degrees_reported"]
                          for x in interface["alternatives"]],
                         ["284.1520", "198.5261"])
        self.assertTrue(all(not x["admitted_as_hard_constraint"]
                            for x in interface["alternatives"]))
        self.assertEqual(interface["alternatives"][0]["matrix_occurrences"], [])
        self.assertEqual(interface["alternatives"][1]["matrix_occurrences"],
                         ["C25#1", "C179#1"])

    def test_unresolved_raan_sources_cite_exact_original_matrix_rows(self):
        out = contracts(self.rows)
        interface = out["unresolved_element_scenarios_interface"]
        mirror = interface["alternatives"][1]
        for key, line in [("C25#1", 118), ("C179#1", 839)]:
            n, occurrence = key.split("#")
            found = [x for x in out["entries"]
                     if x["id"] == n and x["occurrence"] == int(occurrence)]
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["line"], line)
            self.assertIn(found[0]["citation"], mirror["matrix_citations"])
            self.assertIsNone(found[0]["numeric_error_bounds"])
            self.assertEqual(
                found[0]["physical_encoding"],
                "NOT_ADMITTED_AS_TERMINAL_STATE_CONSTRAINT")
        self.assertTrue(all(x["source_authentication"].startswith("NOT_VERIFIED")
                            for x in interface["alternatives"]))
        self.assertIn(
            "prove_all_surviving_scenarios_agree_before_global_geographic_verdict",
            interface["required_before_physical_use"],
        )


    def test_joint_scenario_enclosures_require_global_coverage_not_one_branch(self):
        out = contracts(self.rows)
        bridge = out["scenario_enclosure_interface"]
        self.assertEqual(bridge["version"], 1)
        self.assertEqual(bridge["lean_module"],
                         "Conde1963/ScenarioEnclosures.lean")
        self.assertEqual(bridge["candidate_semantics"],
                         "COMMON_AND_LEFT_OR_RIGHT")
        self.assertEqual(bridge["branch_combination"],
                         "UNION_UNTIL_VERIFIED_SOURCE_ADJUDICATION")
        self.assertEqual(bridge["source_matrix_sha1"],
                         out["matrix_git_blob_sha1"])
        self.assertEqual(bridge["source_branches"], [
            {"id": "SITE_RAAN_284_UNVERIFIED", "original_custody": "NOT_VERIFIED",
             "matrix_occurrences": [], "is_hard_physical_constraint": False},
            {"id": "AFSPC_MIRROR_RAAN_198_UNVERIFIED",
             "original_custody": "NOT_VERIFIED_PRIMARY",
             "matrix_occurrences": ["C25#1", "C179#1"],
             "is_hard_physical_constraint": False},
        ])
        self.assertEqual(bridge["nasa_lineage"]["matrix_occurrences"],
                         ["C131#1", "C197#1"])
        self.assertEqual(bridge["nasa_lineage"]["source_count"], 1)
        self.assertEqual(bridge["nasa_lineage"]
                         ["instrumental_trajectory_measurements"], 0)
        self.assertFalse(bridge["nasa_lineage"]
                         ["physical_decay_time_or_location_established"])
        self.assertEqual(set(bridge["lean_obligations"]), {
            "exclusion", "forcing", "other_window",
            "consistent_refinement_exclusion", "consistent_refinement_forcing",
            "consistent_refinement_other", "one_branch_only_if_other_empty",
            "opposed_branch_witnesses", "missing_gate_blocks_all",
        })
        self.assertIn("one_branch_only_if_other_is_proven_empty",
                      bridge["mandatory_checks"])
        self.assertIn("no_geographic_claim_while_surviving_branches_disagree",
                      bridge["mandatory_checks"])

    def test_joint_scenario_enclosure_contract_fails_closed(self):
        bridge = contracts(self.rows)["scenario_enclosure_interface"]
        self.assertIsNone(bridge["current_geographic_verdict"])
        self.assertIsNone(bridge["predicted_ground_impact"])
        self.assertIsNone(bridge["validated_error_enclosures"])
        for gate in ("global_parameter_domain_certified",
                     "source_branch_authenticity_certified",
                     "independent_529_holdout_passed",
                     "ground_impact_gate_verified"):
            self.assertIs(bridge[gate], False)
        self.assertEqual(bridge["historical_zip_154_propositions_151_labels"],
                         "NOT_RUN")

    def test_export_preserves_all_rows_and_lineage_limits(self):
        out = contracts(self.rows)
        self.assertEqual(len(out["entries"]), 241)
        same_source = [x for x in out["entries"] if x["source_chain"]]
        self.assertEqual([x["id"] for x in same_source], ["C131", "C197"])
        self.assertEqual(len({(x["id"], x["occurrence"]) for x in out["entries"]}), 241)
        self.assertTrue(all(x["citation"].endswith(f'#L{x["line"]}')
                            for x in out["entries"]))
        self.assertTrue(all(x["source_status"] == "MATRIX_ONLY_NOT_REINSPECTED_THIS_RUN"
                            for x in out["entries"]))
        self.assertEqual(sum(x["physical_encoding"] ==
            "NASA_CATALOGUED_DATE_HYPOTHESIS_NOT_HARD_FILTER" for x in out["entries"]), 2)


if __name__ == "__main__":
    unittest.main()
