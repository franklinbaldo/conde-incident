"""Adversarial guards for the unverified FTV 2313 secondary source."""
import copy
import json
import math
import unittest

from tools.ftv2313_secondary_geometry_C241 import LEDGER, GCAT, audit


class TestFtv2313SecondaryGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.gcat = json.loads(GCAT.read_text(encoding="utf-8"))

    def test_ideal_geometry_not_historical_528(self):
        result = audit(self.ledger, self.gcat)
        self.assertAlmostEqual(result["end_on_area_m2"], math.pi * 1.5**2 / 4)
        self.assertAlmostEqual(result["side_on_area_m2"], 1.5 * 7.99)
        self.assertGreater(result["max_orientation_area_m2"],
                           result["side_on_area_m2"])
        self.assertGreater(result["max_to_end_area_ratio"], 6)
        self.assertIsNone(result["historical_528_area_m2"])
        self.assertEqual(result["independent_mass_observations_added"], 0)

    def reject(self, field, key, value):
        altered = copy.deepcopy(self.ledger)
        altered[field][key] = value
        with self.assertRaises(ValueError):
            audit(altered, self.gcat)

    def test_norad_switch_rejected(self):
        self.reject("listing", "norad", 528)

    def test_transfer_dimensions_to_528_rejected(self):
        self.reject("interpretation", "dimensions_are_528_dimensions", True)

    def test_mass_not_independent_measurement(self):
        self.reject("interpretation", "mass_is_independent_instrumental_measurement", True)

    def test_closed_inventory_not_proven(self):
        self.reject("interpretation", "secondary_1176_is_a_closed_inventory_527_528_529", True)

    def test_cannot_invent_binary_hash(self):
        self.reject("source", "binary_sha256", "0" * 64)

    def test_mass_field_not_verified_equivalent(self):
        self.reject("gcat_comparison", "same_field_semantics_verified", True)

    def test_operational_clock_not_reentry_clock(self):
        self.reject("interpretation", "operational_lifetime_is_orbital_reentry_lifetime", True)

    def test_no_historical_posterior(self):
        self.reject("interpretation", "historical_mcmc", "RUN")

    def test_gcat_missing_mass_not_zero(self):
        altered = copy.deepcopy(self.gcat)
        altered["rows"]["S00528"]["mass_kg"] = 0
        with self.assertRaises(ValueError):
            audit(self.ledger, altered)


if __name__ == "__main__":
    unittest.main()
