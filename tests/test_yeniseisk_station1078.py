"""Adversarial tests for station 1078 provenance, transport and 1963 coverage."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lontra_station1078", ROOT / "tools/verify_yeniseisk_station1078.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class YeniseiskArchiveLead(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(mod.MANIFEST.read_text(encoding="utf-8"))

    def reject(self, path, value):
        d = copy.deepcopy(self.doc)
        cur = d
        for k in path[:-1]:
            cur = cur[k]
        cur[path[-1]] = value
        with self.assertRaises(AssertionError):
            mod.validate(d)

    def test_manifest_valid(self):
        self.assertTrue(mod.validate(self.doc))

    def test_no_unverified_present_holdings(self):
        for field in ("journal_november_1963_confirmed", "present_day_holding_confirmed",
                      "source_original_observation_facsimile", "journal_years_individually_itemized"):
            with self.subTest(field=field):
                self.reject(["institutional_history", field], True)

    def test_no_promoted_observation(self):
        for field in ("station_logs_retrieved", "station_coordinates_confirmed_for_1963",
                      "target_objects_explicitly_identified", "archive_contacted"):
            with self.subTest(field=field):
                self.reject(["route", field], True)

    def test_no_unverified_orbital_data(self):
        for field in ("independent_target_measurements", "new_numeric_observables",
                      "orbital_constraints_activated"):
            with self.subTest(field=field):
                self.reject([field], 1)

    def test_undated_history_remains_undated(self):
        self.reject(["institutional_history", "date_of_web_publication"], "1963-11-08")

    def test_insecure_transport_not_tls_authentication(self):
        self.reject(["retrieved_transport_copy", "tls_certificate_validated"], True)

    def test_station_is_not_arbitrary_identifier(self):
        self.reject(["institutional_history", "station_identifier"], "1090")

    def test_source_bytes_reject_forgery(self):
        with self.assertRaises(AssertionError):
            mod.validate(self.doc, b"СОН ИЗС № 1078")
        bad = b"A" * self.doc["retrieved_transport_copy"]["bytes"]
        with self.assertRaises(AssertionError):
            mod.validate(self.doc, bad)

    def test_target_window_not_assumed_to_be_covered(self):
        self.reject(["route", "candidate_observation_dates"], ["1963-11-08"])

if __name__ == "__main__":
    unittest.main()
