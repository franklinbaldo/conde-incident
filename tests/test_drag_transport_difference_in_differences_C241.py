"""Exact-rank, adverse transportability tests; no historical MCMC."""
import copy
import json
import unittest

from tools.drag_transport_difference_in_differences_C241 import (
    anchor, audit, contrast, coordinates, design, estimable, row,
)
from tools.mass_identifiability_C241 import GCAT, catalog_is_not_mass_inventory, rank


class TransportDifferenceInDifferences(unittest.TestCase):
    def test_model_coordinate_and_proxy_ranks(self):
        for model, n, r in (("shared", 8, 4),
                            ("static_offset", 10, 4),
                            ("epoch_offset", 12, 6)):
            with self.subTest(model=model):
                self.assertEqual(len(coordinates(model)), n)
                self.assertEqual((design(model)["six_proxy_rank"],
                                  design(model)["six_proxy_nullity"]), (r, n-r))

    def test_controls_predict_future_only_with_stable_transport(self):
        self.assertTrue(design("shared")["future_528_proxy_estimable_from_e0_and_527_e1"])
        self.assertTrue(design("static_offset")["future_528_proxy_estimable_from_e0_and_527_e1"])
        self.assertFalse(design("epoch_offset")["future_528_proxy_estimable_from_e0_and_527_e1"])

    def test_one_independent_drift_calibration_restores_proxy_prediction(self):
        r = design("epoch_offset", transport_drift_known=True)
        self.assertTrue(r["future_528_proxy_estimable_from_e0_and_527_e1"])
        self.assertFalse(r["q528_estimable_after_calibrations"])

    def test_calibrated_527_plus_528_geometry_fails_under_density_offset(self):
        a = ("q527", "g527", "g528")
        self.assertTrue(design("shared", anchors=a)["q528_estimable_after_calibrations"])
        self.assertFalse(design("static_offset", anchors=a)["q528_estimable_after_calibrations"])
        self.assertFalse(design("epoch_offset", anchors=a)["q528_estimable_after_calibrations"])

    def test_calibrating_relative_density_and_geometry_identifies_mass(self):
        a = ("q527", "g527", "g528")
        self.assertTrue(design("static_offset", anchors=a+("d528",))["q528_estimable_after_calibrations"])
        self.assertTrue(design("epoch_offset", anchors=a+("d528_e0",))["q528_estimable_after_calibrations"])

    def test_drift_alone_does_not_resolve_absolute_mass(self):
        a = ("q527", "g527", "g528")
        self.assertFalse(design("epoch_offset", anchors=a, transport_drift_known=True)["q528_estimable_after_calibrations"])

    def test_zero_contrast_only_under_shared_or_constant_relative_density(self):
        self.assertEqual(contrast("shared"), (0,)*8)
        self.assertEqual(contrast("static_offset"), (0,)*10)
        d = contrast("epoch_offset")
        self.assertEqual(sum(abs(v) for v in d), 2)
        self.assertEqual(d[coordinates("epoch_offset").index("d528_e1")], 1)
        self.assertEqual(d[coordinates("epoch_offset").index("d528_e0")], -1)

    def test_duplicate_control_and_repeated_copy_cannot_restore_prediction(self):
        model = "epoch_offset"
        train = [row(model, obj, "e0") for obj in ("527", "528", "529")]
        control = row(model, "527", "e1")
        target = row(model, "528", "e1")
        self.assertFalse(estimable(train+[control], target))
        self.assertFalse(estimable(train+[control]*20, target))
        self.assertEqual(rank(train+[control], columns=12),
                         rank(train+[control]*20, columns=12))

    def test_cannot_accidentally_promote_unvalidated_calibration(self):
        for model, channels in (("shared", ("GCAT_1176",)),
                                ("static_offset", ("d528", "d528")),
                                ("epoch_offset", ("g528", "rho528"))):
            with self.subTest(model=model), self.assertRaises(ValueError):
                design(model, anchors=channels)
        with self.assertRaises(ValueError):
            design("shared", transport_drift_known=True)
        with self.assertRaises(ValueError):
            coordinates("historical")
        with self.assertRaises(ValueError):
            anchor("epoch_offset", "density_measured_in_1963")

    def test_invalid_object_epoch_and_target_dimension_rejected(self):
        with self.assertRaises(ValueError):
            row("shared", "528", "Nov1963")
        with self.assertRaises(ValueError):
            row("static_offset", "1963-003D", "e0")
        with self.assertRaises(ValueError):
            estimable([(1, 2)], (1, 2, 3))

    def test_catalog_cannot_become_independent_mass_evidence(self):
        data = copy.deepcopy(json.loads(GCAT.read_text(encoding="utf-8")))
        data["conclusion"]["historical_mass_constraint_active"] = True
        with self.assertRaises(ValueError):
            catalog_is_not_mass_inventory(data)

    def test_no_posterior_geolocation_or_instrument_claim(self):
        a = audit()
        self.assertEqual(a, audit())
        self.assertEqual(len(a["source_sha256"]), 64)
        self.assertEqual(a["historical_calibrated_drag_observations"], 0)
        self.assertEqual(a["historical_transport_drift_calibrations"], 0)
        self.assertEqual(a["historical_mcmc"], "NOT_RUN")
        self.assertFalse(a["historical_constraint_active"])
        self.assertFalse(a["geographic_domain_reduced"])
        self.assertIsNone(a["mass_posterior_528"])
        self.assertIsNone(a["conde_impact_probability"])


if __name__ == "__main__":
    unittest.main()
