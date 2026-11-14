"""Adversarial provenance checks for the original RU478 finding aid."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_sao_ru478_finding_aid_c241_l45 import (  # noqa: E402
    CROSSWALK, LEDGER, audit, live_check, read_json,
)


class RU478Tests(unittest.TestCase):
    def setUp(self):
        self.model = read_json(LEDGER)
        self.crosswalk = read_json(CROSSWALK)

    def reject(self, change):
        corrupted = copy.deepcopy(self.model)
        change(corrupted)
        with self.assertRaises(ValueError):
            audit(corrupted, self.crosswalk)

    def test_baseline(self):
        self.assertEqual(audit(self.model, self.crosswalk)["locators"], 4)

    def test_wrong_hash(self):
        self.reject(lambda x: x["source"].update(sha256="0" * 64))

    def test_wrong_bytes(self):
        self.reject(lambda x: x["source"].update(bytes=118910))

    def test_pdf_page_offset(self):
        self.reject(lambda x: x["anchors"][2].update(pdf_page_index_zero_based=24))

    def test_wrong_finding_aid_box(self):
        self.reject(lambda x: x["anchors"][3].update(box=22))

    def test_wrong_catalogue_description(self):
        self.reject(lambda x: x["anchors"][3].update(phrase="Observation NORAD 528"))

    def test_invented_utc(self):
        self.reject(lambda x: x.update(individual_observation_utc="1963-11-08T23:30Z"))

    def test_invented_sigma(self):
        self.reject(lambda x: x.update(target_528_sensor_sigma=0.1))

    def test_invented_station(self):
        self.reject(lambda x: x.update(station_for_target_528=9008))

    def test_fabricated_detection(self):
        self.reject(lambda x: x.update(independent_instrumental_observations_recovered=1))

    def test_fabricated_nondetection(self):
        self.reject(lambda x: x.update(inference="NO_DETECTION_OF_528_EXISTED"))

    def test_fabricated_impact(self):
        self.reject(lambda x: x.update(impact_at_conde="CONFIRMED"))

    def test_unsafe_activation(self):
        self.reject(lambda x: x.update(physical_constraints_activated=1))

    def test_duplicate_unverified_independence(self):
        self.reject(lambda x: x.update(derived_from_same_sao_program=False))

    def test_upstream_crosswalk_drift(self):
        altered = copy.deepcopy(self.crosswalk)
        altered["sources"][0]["url"] = "https://example.invalid/"
        with self.assertRaises(ValueError):
            audit(self.model, altered)

    def test_invalid_pdf_rejected(self):
        with self.assertRaises(ValueError):
            live_check(b"%PDF-1.4\nfake finding aid")


if __name__ == "__main__":
    unittest.main()
