"""C241 fail-closed tests for assumed priors versus identified masses."""
import copy
import json
import unittest
from fractions import Fraction

from tools.mass_prior_sensitivity_C241 import (
    GCAT, audit_sources, dirichlet_moments, report,
)


class TestPriorSensitivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(GCAT.read_text(encoding="utf-8"))

    def test_exchangeable_scenario_is_not_observation(self):
        output = report()
        self.assertEqual(output["profiles"]["exchangeable"]["prior_means_kg_exact"],
                         dict.fromkeys(("527", "528", "529", "X"), "294"))
        self.assertEqual(output["source_family_independent_mass_measurements"], 0)
        self.assertIsNone(output["historical_likelihood"])
        self.assertIsNone(output["historical_mass_posterior"])
        self.assertIsNone(output["preferred_allocation"])
        self.assertEqual(output["historical_mcmc"], "NOT_RUN")
        self.assertFalse(output["physical_domain_reduction"])
        self.assertFalse(output["historical_constraint_active"])

    def test_prior_changes_estimates_without_new_measurement(self):
        result = report()
        xmeans = [Fraction(v["prior_means_kg_exact"]["X"])
                  for v in result["profiles"].values()]
        self.assertEqual(xmeans, [Fraction(294), Fraction(1176,13), Fraction(1176,25)])
        self.assertTrue(all(sum(map(Fraction, v["prior_means_kg_exact"].values())) == 1176
                            for v in result["profiles"].values()))
        self.assertEqual(result["concentration_stress"]["new_observations"], 0)

    def test_concentration_changes_variance_not_mean(self):
        a, v1 = dirichlet_moments((1,1,1,1), 1176)
        b, v2 = dirichlet_moments((10,10,10,10), 1176)
        self.assertEqual(a, b)
        self.assertTrue(all(x > y > 0 for x,y in zip(v1,v2)))

    def test_fractional_exactness_and_total_scale(self):
        m, v = dirichlet_moments(("4", "1", "1", "1/4"), 1176)
        self.assertEqual(m[0], Fraction(18816,25))
        self.assertEqual(m[-1], Fraction(1176,25))
        self.assertEqual(sum(m), 1176)
        self.assertTrue(all(x > 0 for x in v))

    def test_invalid_parameters_rejected(self):
        for alpha, total in [((0,1,1,1),1176),((1,1,1),1176),
                             ((1,1,1,False),1176),((1,1,1,1),0),
                             ((1,1,1,1.5),1176),(("nan",1,1,1),1176),
                             (("1/0",1,1,1),1176)]:
            with self.subTest(alpha=alpha,total=total), self.assertRaises(ValueError):
                dirichlet_moments(alpha, total)

    def test_528_catalog_zero_is_not_mass_measurement(self):
        bad = copy.deepcopy(self.catalog)
        bad["rows"]["S00528"]["mass_kg"] = 0
        with self.assertRaises(ValueError):
            audit_sources(bad)

    def test_fake_inventory_equation_rejected(self):
        bad = copy.deepcopy(self.catalog)
        bad["derived_checks"]["three_norad_objects_mass_sum_kg"] = 1176
        with self.assertRaises(ValueError):
            audit_sources(bad)

    def test_fake_historical_activation_rejected(self):
        bad = copy.deepcopy(self.catalog)
        bad["conclusion"]["historical_mass_constraint_active"] = True
        with self.assertRaises(ValueError):
            audit_sources(bad)


if __name__ == "__main__":
    unittest.main()
