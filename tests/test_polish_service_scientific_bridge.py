"""Adversarial tests: Polish aggregate service report is not a 528 observation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import export_polish_service_scientific_bridge as bridge


class PolishServiceBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = bridge.load()
        cls.payload = bridge.build(cls.source)

    def test_public_bytes_are_rebuilt_from_pinned_source(self):
        self.assertEqual((bridge.ROOT / bridge.OUTPUT).read_bytes(), bridge.render())

    def test_provenance_and_all_links(self):
        p = self.payload
        self.assertEqual(["C241-LONTRA-R65"], p["occurrence_ids"])
        self.assertEqual(bridge.SOURCE_SHA, p["sources"][0]["manifest_sha256"])
        self.assertEqual(bridge.PDF_SHA, p["sources"][0]["original_pdf_sha256"])
        self.assertEqual(26, p["delta_links"])
        self.assertEqual(26, len({(x["source"], x["target"], x["relation"])
                                  for x in p["graph"]}))
        self.assertTrue(all(x["documentary_only"] and not x["activation"]
                            for x in p["graph"]))

    def test_norad_and_uncertainty_stay_unknown(self):
        p = self.payload
        self.assertEqual(0, p["independent_target_measurements_newly_recovered"])
        self.assertIsNone(p["number_of_historical_independent_528_measurements"])
        self.assertIsNone(p["reported_service"]["norad_528_observations_in_report"])
        self.assertEqual("THETA_UNCHANGED", p["physical_domain_effect"])
        self.assertEqual("NOT_RUN", p["historical_mcmc"])
        self.assertEqual("NOT_PROMOTED", p["lean_candidate"]["status"])
        self.assertFalse(p["lean_candidate"]["compiled_theorem_claimed"])
        self.assertTrue(all(x["value"] is None and not x["activation"]
                            for x in p["latents"] + p["simulator_parameters"]))

    def test_aggregate_count_not_relabelled_year_or_target(self):
        for field, value in [
            ("count_scope", "NORAD_528_1963"),
            ("observations_through_year", 1964),
            ("aggregate_count_lower_bound_exclusive", 25),
            ("stations_in_1964", 10),
            ("cospar_station_id_first", 1152),
            ("measurement_methods", ["radar"]),
        ]:
            source = copy.deepcopy(self.source)
            source["reported_service"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                bridge.build(source)

    def test_missing_original_log_not_invented(self):
        changes = [
            ("observations_for_norad_527_528_529", [{"norad": 528}]),
            ("independent_measurement_rows_recovered", 1),
            ("object_specific_time_observed", "1963-11-08T18:00:00Z"),
            ("original_station_logs_recovered", True),
            ("individual_station_instrument_calibration_recovered", True),
            ("new_orbital_constraints", 1),
        ]
        for field, value in changes:
            source = copy.deepcopy(self.source)
            source["boundaries"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                bridge.build(source)

    def test_custody_page_and_year_not_forged(self):
        for field, value in [
            ("publication_year", 1963),
            ("pdf_pages_one_based", [29]),
            ("printed_pages", [190]),
            ("full_pdf_sha256", "0" * 64),
            ("full_pdf_bytes", 4882675),
        ]:
            source = copy.deepcopy(self.source)
            source["source"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                bridge.build(source)

    def test_output_mutations_rejected(self):
        for section, key, value in [
            ("simulator_parameters", 0, {"id": "polish_optical_clock_sigma_528",
                                         "value": 1.0, "activation": True}),
            ("lean_candidate", "status", "PROMOTED"),
            ("reported_service", "norad_528_observations_in_report", 25000),
            ("graph", 0, dict(self.payload["graph"][0], activation=True)),
        ]:
            payload = copy.deepcopy(self.payload)
            payload[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                bridge.validate(payload)

    def test_sha_mismatch_on_original_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / bridge.SOURCE
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(self.source, ensure_ascii=False,
                                         sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 drift"):
                bridge.load(root)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate source JSON key"):
            json.loads('{"id":"first","id":"other"}',
                       object_pairs_hook=bridge.no_duplicate_keys)


if __name__ == "__main__":
    unittest.main()
