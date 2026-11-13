"""Adversarial tests: Soviet library holdings are not original NORAD observations."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_soviet_1963_cross_id import PATHS, replay_cinii, validate

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PATHS]

class SovietCrossId(unittest.TestCase):
    def reject(self, index, edit):
        inputs = copy.deepcopy(SOURCES)
        edit(inputs[index])
        with self.assertRaises((ValueError, KeyError, TypeError, StopIteration)):
            validate(*inputs)

    def test_holding_to_six_pending_pairs(self):
        r = validate(*SOURCES)
        self.assertEqual(r["candidate_pairs"], 6)
        self.assertEqual(r["original_1963_soviet_measurements"], 0)
        self.assertEqual(r["orbital_constraints_active"], 0)
        self.assertEqual(r["primary_crosswalks_confirmed"], ["1963 03A=527 (NASA only)"])

    def test_ukraine_issue_1963_year_changed(self):
        self.reject(1, lambda x: x["records"][0].update(year=1964))

    def test_ukraine_issue_range_changed(self):
        self.reject(0, lambda x: x["holdings"][0].update(issue_numbers=[32,33,34]))

    def test_fake_soviet_facsimile(self):
        self.reject(0, lambda x: x["holdings"][0].update(issue_pages_seen=True))

    def test_catalog_snapshot_promoted_to_pdf(self):
        self.reject(0, lambda x: x["bibliographic_cross_checks"][0].update(pdf_sha256="0"*64))

    def test_independent_sensors_derived_from_two_library_cards(self):
        self.reject(0, lambda x: x["bibliographic_cross_checks"][0].update(independent_observation=True))

    def test_cinii_holdings_1963_scope_overstated(self):
        self.reject(0, lambda x: x["bibliographic_cross_checks"][1].update(status="NO_1963_ISSUES_EXIST_ANYWHERE"))

    def test_cinii_capture_hash_changed(self):
        self.reject(0, lambda x: x["bibliographic_cross_checks"][0].update(capture_sha256="0"*64))

    def test_cinii_capture_size_changed(self):
        self.reject(0, lambda x: x["bibliographic_cross_checks"][1].update(capture_bytes=10))

    def test_soviet_528_primary_claim_invented(self):
        self.reject(0, lambda x: x["western_object_aliases"][1].update(western_crosswalk="CONFIRMED_PRIMARY_NASA_CATALOG_ONLY"))

    def test_nasa_527_crosswalk_lost(self):
        self.reject(2, lambda x: x["crosswalk"].update(catalog_number=528))

    def test_soviet_528_observation_invented(self):
        self.reject(0, lambda x: x["candidate_joins"][2].update(original_measurement={"range_km":600}))

    def test_soviet_instrument_sigma_invented(self):
        self.reject(0, lambda x: x["candidate_joins"][3].update(instrument_sigma=0.01))

    def test_soviet_epoch_invented(self):
        self.reject(0, lambda x: x["candidate_joins"][4].update(original_epoch_utc="1963-11-08T12:00:00Z"))

    def test_soviet_western_identifier_join_auto_confirmed(self):
        self.reject(0, lambda x: x["candidate_joins"][1].update(join_status="CONFIRMED"))

    def test_dropped_529_pair(self):
        self.reject(0, lambda x: x["candidate_joins"].pop())

    def test_soviet_two_serials_counted_as_sensors(self):
        self.reject(0, lambda x: x["result"].update(independent_measurements_added=2))

    def test_reject_orbital_constraint_promotion(self):
        self.reject(0, lambda x: x["result"].update(orbital_constraints_activated=1))

    def test_absence_in_cinii_not_global_absence(self):
        self.reject(0, lambda x: x["rejected_automatic_upgrades"].pop())

    def test_replay_requires_real_cinii_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            (directory / "AA00566856.html").write_bytes(b"1963-1971 32-59")
            (directory / "AA00826990.html").write_bytes(b"1961-1962 1-15")
            with self.assertRaisesRegex(ValueError, "exact HTML bytes changed"):
                replay_cinii(SOURCES[0], directory)

if __name__ == "__main__":
    unittest.main()
