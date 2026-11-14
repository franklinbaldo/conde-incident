"""Adversarial tests: operation-life metadata cannot become debris likelihood."""
import copy
import json
import unittest

from tools.nro_7153_mission_scope import SOURCE, audit


class TestNroMissionScope(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(SOURCE.read_text(encoding="utf-8"))

    def reject(self, path, value):
        changed = copy.deepcopy(self.original)
        cur = changed
        for key in path[:-1]:
            cur = cur[key]
        cur[path[-1]] = value
        with self.assertRaises(ValueError):
            audit(changed)

    def test_genuine_manifest_is_inactive(self):
        r = audit(self.original)
        self.assertEqual(r["independent_orbital_observations_added"], 0)
        self.assertIsNone(r["decay_or_breakup_time_from_battery_failure"])
        self.assertIsNone(r["mass_528_kg"])
        self.assertFalse(r["geographic_domain_reduced"])
        self.assertFalse(r["pdf_binary_verified"])
        self.assertEqual(r["historical_mcmc"], "NOT_RUN")

    def test_fail_closed_false_1963_origin(self):
        self.reject(("source", "contemporaneous_1963_record"), True)

    def test_fail_closed_false_instrumental_independence(self):
        self.reject(("source", "independent_orbital_measurement"), True)

    def test_no_invented_pdf_hash(self):
        self.reject(("source", "pdf_sha256"), "a" * 64)

    def test_no_fictional_pdf_visual_validation(self):
        self.reject(("source", "visual_verification"), "VERIFIED")

    def test_no_exact_battery_failure_utc(self):
        self.reject(("mission", "failure_timestamp_utc"), "1963-01-18T00:00:00Z")

    def test_no_exact_reentry_epoch(self):
        self.reject(("mission", "orbit_decay_timestamp_utc"), "1963-01-18T00:00:00Z")

    def test_no_breakup_inferred_from_power_loss(self):
        self.reject(("identity", "failure_means_structural_breakup"), True)

    def test_no_unverified_528_identity_assignment(self):
        self.reject(("identity", "debris_identity_verified_by_nro_history"), True)

    def test_no_528_decay_from_mission_end(self):
        self.reject(("identity", "mission_end_means_528_decay"), True)

    def test_no_invented_sensor(self):
        self.reject(("scientific_readiness", "tracking_sensor"), "SPADATS")

    def test_no_likelihood_or_historical_mcmc(self):
        self.reject(("scientific_readiness", "historical_likelihood"), {"sigma_s": 1})
        self.reject(("scientific_readiness", "historical_mcmc"), "RUN")

    def test_no_geographic_contraction(self):
        self.reject(("scientific_readiness", "conde_geographic_contraction"), True)

    def test_no_source_genealogy_mutation(self):
        self.reject(("mission", "number"), 7152)


if __name__ == "__main__":
    unittest.main()
