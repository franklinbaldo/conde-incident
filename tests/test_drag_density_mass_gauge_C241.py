"""Adversarial exact checks: a drag proxy cannot certify NORAD 528 mass."""
import copy
import json
import unittest

from tools.drag_density_mass_gauge_C241 import (
    COORDINATES, OBJECTS, EPOCHS, TARGET, anchor_row, audit, drag_design,
    drag_row, gauge_witnesses, holdout_design, observable,
)
from tools.mass_identifiability_C241 import (
    GCAT, catalog_is_not_mass_inventory, rank,
)


class DragDensityGauge(unittest.TestCase):
    def test_all_six_hypothetical_rows_and_eight_coordinates(self):
        rows = [drag_row(i, t) for i in OBJECTS for t in EPOCHS]
        self.assertEqual((len(rows), len(COORDINATES)), (6, 8))
        self.assertTrue(all(len(row) == 8 for row in rows))
        self.assertEqual(drag_row("528", "e0"), (0, -1, 0, 0, 1, 0, 1, 0))

    def test_drag_only_rank_four_nullity_four(self):
        r = drag_design()
        self.assertEqual((r["rank"], r["nullity"]), (4, 4))
        self.assertFalse(r["q528_estimable"])

    def test_two_distinct_exact_gauges_move_target(self):
        self.assertTrue(gauge_witnesses()[
            "both_change_q528_without_changing_drag"
        ])

    def test_density_anchor_alone_does_not_measure_mass(self):
        r = drag_design(anchors=("s0",))
        self.assertEqual(r["rank"], 5)
        self.assertFalse(r["q528_estimable"])

    def test_geometry_anchor_alone_does_not_measure_mass(self):
        r = drag_design(anchors=("g528",))
        self.assertEqual(r["rank"], 5)
        self.assertFalse(r["q528_estimable"])

    def test_density_and_geometry_identify_target_not_whole_system(self):
        r = drag_design(anchors=("s0", "g528"))
        self.assertEqual((r["rank"], r["nullity"]), (6, 2))
        self.assertTrue(r["q528_estimable"])

    def test_calibrated_control_without_528_geometry_is_insufficient(self):
        r = drag_design(anchors=("q527", "g527"))
        self.assertEqual((r["rank"], r["nullity"]), (6, 2))
        self.assertFalse(r["q528_estimable"])

    def test_calibrated_control_plus_528_geometry_is_conditional_solution(self):
        r = drag_design(anchors=("q527", "g527", "g528"))
        self.assertEqual((r["rank"], r["nullity"]), (7, 1))
        self.assertTrue(r["q528_estimable"])

    def test_repeated_drag_measurement_does_not_change_rank(self):
        rows = [drag_row(i, t) for i in OBJECTS for t in EPOCHS]
        self.assertEqual(rank(rows, columns=8), rank(rows + [drag_row("528", "e1")], columns=8))
        self.assertFalse(observable(rows, TARGET))

    def test_duplicate_or_unknown_calibration_rejected(self):
        for names in (("s0", "s0"), ("rho_1963",), ("GCAT_1176",)):
            with self.subTest(names=names), self.assertRaises(ValueError):
                drag_design(anchors=names)

    def test_unknown_object_and_epoch_rejected(self):
        for i, ep in (("688", "e0"), ("528", "1963-11-08"), ("", "e0")):
            with self.subTest(i=i, ep=ep), self.assertRaises(ValueError):
                drag_row(i, ep)
        with self.assertRaises(ValueError):
            anchor_row("Bstar528")

    def test_future_holdout_requires_time_matched_control(self):
        r = holdout_design()
        self.assertFalse(r["future_528_from_e0_alone"])
        self.assertTrue(r["future_528_with_527_e1_control"])
        self.assertTrue(r["future_528_with_529_e1_control"])
        self.assertFalse(r["q528_from_e0_plus_527_e1_control"])
        self.assertEqual(r["historical_holdout"], "NOT_RUN")

    def test_no_historical_posterior_or_active_geography(self):
        r = audit()
        self.assertEqual(r["historical_mass_observation_rank"], 0)
        self.assertFalse(r["historical_constraint_active"])
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")
        self.assertIsNone(r["historical_mass_posterior"])
        self.assertIsNone(r["impact_probability"])
        self.assertFalse(r["historical_domain_reduction"])

    def test_catalog_veto_cannot_promote_total_to_measured_inventory(self):
        data = json.loads(GCAT.read_text(encoding="utf-8"))
        data = copy.deepcopy(data)
        data["conclusion"]["historical_mass_constraint_active"] = True
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(data)

    def test_output_deterministic_and_provenance_hashed(self):
        a = audit()
        self.assertEqual(a, audit())
        self.assertEqual(len(a["source_sha256"]), 64)
        self.assertEqual(a["source_occurrence"], "C241-L40")


if __name__ == "__main__":
    unittest.main()
