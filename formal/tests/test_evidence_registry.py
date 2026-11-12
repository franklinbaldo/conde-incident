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


    def test_sourced_raan_is_single_reference_and_free_mcmc_parameter(self):
        interface = contracts(self.rows)["unresolved_element_scenarios_interface"]
        self.assertEqual(interface["version"], 2)
        self.assertEqual(interface["kind"],
                         "SOURCED_REFERENCE_PLUS_INFERRED_ORBITAL_PARAMETERS")
        self.assertEqual(interface["active_source_lineages"], 1)
        self.assertEqual(interface["admissible_semantics"],
                         "SINGLE_SOURCED_REFERENCE_WITH_FREE_PARAMETERS")
        self.assertEqual(interface["branch_combination_allowed"],
                         "OTHER_BRANCH_ONLY_IF_NEW_DOCUMENTED_SOURCE")
        self.assertEqual(interface["current_scenario"],
                         "AFSPC_MIRROR_528_1963_10_27")
        self.assertEqual(len(interface["alternatives"]), 1)
        source = interface["alternatives"][0]
        self.assertEqual(source["id"], interface["current_scenario"])
        self.assertEqual(source["raan_degrees_reported"], "198.5261")
        self.assertEqual(source["epoch_utc"],
                         "1963-10-27T14:40:16.132512Z")
        self.assertEqual(source["literal_pair_sha256"],
                         "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd")
        self.assertEqual(source["source_authentication"], "NOT_VERIFIED_PRIMARY")
        self.assertFalse(source["admitted_as_hard_constraint"])
        self.assertTrue(source["reference_only_not_true_raan"])
        self.assertEqual(source["matrix_occurrences"], ["C25#1", "C179#1"])
        self.assertEqual(interface["original_tle_custody"], "NOT_VERIFIED")
        self.assertEqual(interface["historical_orbit_validation"], "NOT_RUN")
        self.assertEqual(interface["obsolete_legacy_input"],
                         "RETIRED_FROM_ACTIVE_INFERENCE_RETRIEVABLE_FROM_GIT")
        self.assertNotIn("SITE_RAAN_284_UNVERIFIED",
                         [x["id"] for x in interface["alternatives"]])
        theta = interface["raan_parameter"]
        self.assertEqual(theta["name"], "raan_at_reference_epoch_deg")
        self.assertEqual(theta["topology"], "CIRCLE_MOD_360")
        self.assertEqual(theta["full_search_domain_deg"], ["0", "360"])
        self.assertTrue(theta["upper_endpoint_exclusive"])
        self.assertIsNone(theta["physical_uncertainty_deg"])
        self.assertIsNone(theta["hard_admissible_interval_deg"])
        self.assertEqual(theta["prior_distribution"],
                         "UNSPECIFIED_NOT_SYNTHESIZED")
        self.assertEqual(interface["mcmc_contract"]["sampler"],
                         "NOT_IMPLEMENTED_BY_LEAN")
        self.assertTrue(interface["mcmc_contract"]
                        ["no_empirical_uncertainty_no_posterior_claim"])
        self.assertIn("FIRST_ORDER_J2_NODAL_PRECESSION",
                      [x["relation"] for x in
                       interface["physical_dependencies_to_explore"]])

    def test_sourced_raan_reference_cites_exact_original_matrix_rows(self):
        out = contracts(self.rows)
        interface = out["unresolved_element_scenarios_interface"]
        mirror = interface["alternatives"][0]
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
        self.assertIn("derive_raan_restrictions_from_j2_and_multi_epoch_observations",
                      interface["required_before_physical_use"])

    def test_joint_scenario_enclosures_require_global_coverage_not_one_branch(self):
        out = contracts(self.rows)
        bridge = out["scenario_enclosure_interface"]
        self.assertEqual(bridge["version"], 1)
        self.assertEqual(bridge["lean_module"],
                         "Conde1963/ScenarioEnclosures.lean")
        self.assertEqual(bridge["candidate_semantics"],
                         "SINGLE_SOURCED_REFERENCE_WITH_FREE_PARAMETERS")
        self.assertEqual(bridge["branch_combination"],
                         "ONE_ACTIVE_SOURCE_UNLESS_NEW_DOCUMENTED_SOURCE")
        self.assertEqual(bridge["source_matrix_sha1"],
                         out["matrix_git_blob_sha1"])
        self.assertEqual(bridge["source_branches"], [
            {"id": "AFSPC_MIRROR_528_1963_10_27",
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


    def test_finite_coverage_requires_global_proof_before_branch_elimination(self):
        out = contracts(self.rows)
        gate = out["finite_coverage_interface"]
        self.assertEqual(gate["version"], 1)
        self.assertEqual(gate["kind"],
                         "GLOBAL_COVERAGE_REQUIRED_BEFORE_EMPTY_GRID_EXCLUDES_BRANCH")
        self.assertEqual(gate["lean_module"], "Conde1963/FiniteCoverage.lean")
        self.assertEqual(gate["parameter_semantics"], "COMMON_AND_LEFT_OR_RIGHT")
        self.assertEqual(gate["source_matrix_sha1"], out["matrix_git_blob_sha1"])
        self.assertEqual(gate["source_matrix_occurrences"], ["C25#1", "C179#1"])
        self.assertEqual(gate["nasa_same_primary_source"], ["C131#1", "C197#1"])
        self.assertEqual(gate["nasa_independent_source_count"], 1)
        for key in ("current_screen", "current_global_domain_conclusion",
                    "current_geographic_verdict", "verified_numeric_enclosures"):
            self.assertIsNone(gate[key])
        for key in ("pointwise_classifier_equivalence_proven",
                    "full_domain_coverage_proven", "primary_tle_custody_proven",
                    "independent_529_holdout_passed", "ground_impact_gate_proven"):
            self.assertIs(gate[key], False)
        self.assertEqual(gate["original_zip_154_151_import"], "NOT_RUN")

    def test_finite_coverage_contract_cannot_confuse_screen_and_full_domain(self):
        obligations = contracts(self.rows)["finite_coverage_interface"]
        named = obligations["lean_obligations"]
        self.assertEqual(set(named), {
            "pointwise_iff", "surviving_witness", "no_fabrication",
            "empty_only_with_coverage", "branch_elimination",
            "left_result_only_after_branch_elimination",
            "sampled_empty_counterexample"
        })
        self.assertIn("proof_every_global_admissible_state_is_covered",
                      obligations["must_verify"])
        self.assertIn("pointwise_screen_equivalence_for_each_sample",
                      obligations["must_verify"])
        self.assertIn("no_physical_claim_from_synthetic_countermodel",
                      obligations["must_verify"])
        self.assertEqual([x["line"] for x in contracts(self.rows)["entries"]
                          if x["id"] in {"C25", "C179"}], [118, 839])


    def test_certified_cells_cover_continuous_parameters_fail_closed(self):
        output = contracts(self.rows)
        cells = output["certified_cell_interface"]
        self.assertEqual(cells["version"], 1)
        self.assertEqual(cells["kind"],
                         "CONTINUOUS_PARAMETER_CELL_COVER_NOT_POINT_GRID")
        self.assertEqual(cells["lean_module"], "Conde1963/CertifiedCells.lean")
        self.assertEqual(cells["parameter_semantics"], "COMMON_AND_LEFT_OR_RIGHT")
        self.assertEqual(cells["source_matrix_sha1"],
                         output["matrix_git_blob_sha1"])
        self.assertEqual(cells["orbital_scenario_rows"], ["C25#1", "C179#1"])
        self.assertEqual(cells["orbital_primary_tle_status"], "NOT_AUTHENTICATED")
        self.assertEqual(cells["nasa_one_document_two_occurrences"],
                         ["C131#1", "C197#1"])
        self.assertEqual(cells["nasa_independent_instrumental_sources"], 0)
        self.assertEqual(cells["original_zip_154_151_import"], "NOT_RUN")
        for key in ("current_cells", "current_event_bounds",
                    "current_geographic_verdict", "current_numeric_epoch_window_utc",
                    "current_numeric_spatial_enclosure"):
            self.assertIsNone(cells[key])
        for key in ("continuous_parameter_coverage_proven",
                    "sound_event_bounds_for_every_cell_proven",
                    "nonempty_global_domain_proven",
                    "validated_ground_impact_gate_proven",
                    "calibrated_numerical_errors_proven",
                    "independent_529_holdout_passed"):
            self.assertIs(cells[key], False)

    def test_certified_cell_obligations_do_not_equate_grid_and_cover(self):
        output = contracts(self.rows)
        cells = output["certified_cell_interface"]
        points = output["finite_coverage_interface"]
        self.assertNotEqual(cells["kind"], points["kind"])
        self.assertIsNone(cells["current_cells"])
        self.assertIsNone(points["current_screen"])
        self.assertEqual(set(cells["lean_obligations"]), {
            "event_soundness", "nonempty_requires_cell",
            "empty_cells_requires_full_cover", "exclude_conditional",
            "force_conditional", "other_window_conditional",
            "narrowed_cover", "narrowed_event_bounds"
        })
        for theorem in cells["lean_obligations"].values():
            self.assertTrue(theorem)
        obligations = set(cells["must_verify"])
        self.assertIn("independent_proof_all_admissible_parameters_lie_in_listed_cells",
                      obligations)
        self.assertIn("sound_numerical_event_bounds_for_all_parameters_in_each_cell",
                      obligations)
        self.assertIn("nonempty_surviving_domain_after_each_narrowing",
                      obligations)
        self.assertIn("ground_impact_model_not_just_catalogue_decay_or_altitude_crossing",
                      obligations)
        self.assertIn("all_surviving_RAAN_scenarios_in_union_not_intersection",
                      obligations)



    def test_paired_cell_contract_requires_two_sound_covers_and_nonempty_domain(self):
        out = contracts(self.rows)
        paired = out["paired_certified_enclosure_interface"]
        self.assertEqual(paired["version"], 1)
        self.assertEqual(paired["kind"], "PAIRED_SOUND_CELL_EVENT_INTERSECTION")
        self.assertEqual(paired["lean_module"], "Conde1963/PairedEnclosures.lean")
        self.assertEqual(paired["source_matrix_sha1"], out["matrix_git_blob_sha1"])
        self.assertEqual(paired["parameter_semantics"], "COMMON_AND_LEFT_OR_RIGHT")
        self.assertEqual(paired["unresolved_orbital_occurrences"],
                         ["C25#1", "C179#1"])
        self.assertEqual(paired["same_nasa_document_occurrences"],
                         ["C131#1", "C197#1"])
        self.assertEqual(paired["nasa_independent_instrumental_sources"], 0)
        self.assertEqual(paired["original_zip_154_151_import"], "NOT_RUN")
        for key in ("current_first_cover", "current_second_cover",
                    "current_intersection", "current_geographic_verdict",
                    "current_numeric_impact_window"):
            self.assertIsNone(paired[key])
        for key in ("primary_tle_custody_verified",
                    "both_continuous_domain_covers_verified",
                    "both_event_enclosures_proved_sound",
                    "same_physical_predictor_and_reference_frame_verified",
                    "nonempty_admissible_domain_proven",
                    "universal_ground_impact_predicted",
                    "calibrated_error_and_holdout_529_verified",
                    "ground_impact_audit_passed"):
            self.assertIs(paired[key], False)

    def test_paired_cell_contract_cannot_turn_disjoint_bounds_into_location(self):
        paired = contracts(self.rows)["paired_certified_enclosure_interface"]
        self.assertEqual(set(paired["lean_obligations"]), {
            "common_prediction_soundness", "conditional_conde_excluded",
            "conditional_conde_forced", "conditional_other_window",
            "disjoint_bounds_no_predicted_impact",
            "incompatible_bounds_vs_universal_impact",
            "narrowing_preserves_soundness"
        })
        self.assertTrue(all(paired["lean_obligations"].values()))
        required = set(paired["must_verify"])
        self.assertIn("nonempty_surviving_domain_after_each_narrowing", required)
        self.assertIn("both_event_bounds_sound_for_every_surviving_candidate",
                      required)
        self.assertIn("do_not_infer_measurement_independence_from_two_certificates",
                      required)
        self.assertIn("no_geographic_verdict_until_empirical_gates_pass", required)
        self.assertIn("ground_impact_vs_altitude_crossing_and_material_survival",
                      required)


if __name__ == "__main__":
    unittest.main()
