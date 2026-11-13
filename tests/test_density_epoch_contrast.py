"""C241-P29: falsify unjustified historical or structural identification."""
import importlib.util
import math
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "tools/density_epoch_contrast.py"
SPEC = importlib.util.spec_from_file_location("density_epoch_contrast", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class DensityEpochContrast(unittest.TestCase):
    def test_archive_index_is_not_a_528_measurement(self):
        snapshot = MOD.archive_snapshot()
        self.assertEqual(snapshot["archival_film_locators"], 15)
        self.assertEqual(snapshot["locators_explicitly_attributed_to_528"], 0)
        self.assertEqual(snapshot["candidate_calibrated_528_records"], 0)

    def test_difference_of_differences_eliminates_all_nuisances(self):
        report = MOD.build_report()
        self.assertEqual(report["exact_rank_diagnostic"]["contrast_columns"],
                         [0, 0, 0, 0, 0, -30])
        self.assertEqual(report["interaction"]["delta_relative_altitude_km"], 30)

    def test_single_object_two_epochs_confounds_q_with_scale_height(self):
        rows = MOD.design((MOD.CELLS[0], MOD.CELLS[2]))
        self.assertEqual(MOD.rank_exact(rows), MOD.rank_exact([r[:-1] for r in rows]))

    def test_three_of_four_cells_do_not_identify_shape(self):
        rows = MOD.design()
        self.assertEqual(MOD.rank_exact(rows[:3]), 3)
        self.assertEqual(MOD.rank_exact([r[:-1] for r in rows[:3]]), 3)
        self.assertEqual(MOD.rank_exact(rows), 4)

    def test_no_altitude_interaction_means_no_gain(self):
        rows = MOD.design(((527, 0, 480), (529, 0, 520),
                           (527, 1, 500), (529, 1, 540)))
        self.assertEqual(MOD.rank_exact(rows), 3)

    def test_object_specific_unmeasured_time_factors_destroy_identification(self):
        rows = MOD.design(per_object_epoch_q=True)
        self.assertEqual(MOD.rank_exact(rows), 4)
        self.assertEqual(MOD.rank_exact([r[:-1] for r in rows]), 4)

    def test_528_column_remains_zero_with_only_controls(self):
        rows = MOD.design(include_528=True)
        self.assertTrue(all(r[3] == 0 for r in rows))
        self.assertEqual(MOD.rank_exact(rows), 4)

    def test_synthetic_arbitrary_q_and_b_cancel_exactly_in_contrast(self):
        log_a = 0.4
        log_b = {527: -1.8, 529: -0.9}
        log_q = {0: -2.4, 1: 1.3}
        inv_h = 1 / 60
        z = [log_a + log_b[j] + log_q[t] - (h - MOD.H0_KM) * inv_h
             for j, t, h in MOD.CELLS]
        interaction = sum(w * val for w, val in zip(MOD.WEIGHTS, z))
        self.assertTrue(math.isclose(interaction, -0.5, abs_tol=1e-13))
        self.assertTrue(math.isclose(
            -interaction / MOD.build_report()["interaction"]["delta_relative_altitude_km"],
            inv_h, abs_tol=1e-13,
        ))

    def test_report_remains_synthetic_and_source_locked(self):
        report = MOD.build_report()
        self.assertFalse(report["active_constraint"])
        self.assertEqual(report["historical_mcmc"], "NOT_RUN")
        self.assertEqual(report["historical_domain_reduction"], "NOT_EVALUABLE")
        self.assertEqual(len(report["source_inventory"]["source_sha256"]), 64)

    def test_film_locator_cannot_be_promoted_to_physical_constraint(self):
        import json
        import tempfile
        from unittest.mock import patch
        original = json.loads(MOD.SOURCE.read_text())
        original["film_index_entries"][0]["hard_physical_constraint"] = True
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "tampered.json"
            path.write_text(json.dumps(original))
            with patch.object(MOD, "SOURCE", path):
                with self.assertRaisesRegex(ValueError, "promoted"):
                    MOD.archive_snapshot()

    def test_duplicate_film_identifier_fails_closed(self):
        import json
        import tempfile
        from unittest.mock import patch
        original = json.loads(MOD.SOURCE.read_text())
        original["film_index_entries"][1]["id"] = original["film_index_entries"][0]["id"]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "duplicate.json"
            path.write_text(json.dumps(original))
            with patch.object(MOD, "SOURCE", path):
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    MOD.archive_snapshot()

    def test_committed_report_equals_recalculation(self):
        import json
        self.assertEqual(json.loads(MOD.OUTPUT.read_text()), MOD.build_report())


if __name__ == "__main__":
    unittest.main()
