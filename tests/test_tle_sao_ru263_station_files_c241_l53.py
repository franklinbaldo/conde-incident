"""Adversarial custody and inference guards for Smithsonian RU263."""
import copy
import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_sao_ru263_station_files_c241_l53 import audit, live_check, read_model  # noqa: E402

class RU263Tests(unittest.TestCase):
    def setUp(self):
        self.model = read_model()

    def reject(self, mutate):
        candidate = copy.deepcopy(self.model)
        mutate(candidate)
        with self.assertRaises(ValueError):
            audit(candidate)

    def test_verified_manifest(self):
        self.assertEqual(audit(self.model)["holdings_located"], 4)

    def test_wrong_sha(self):
        self.reject(lambda x: x["source"].update(sha256="0" * 64))

    def test_pdf_byte_size(self):
        self.reject(lambda x: x["source"].update(bytes=192143))

    def test_offset_not_same_as_printed_page(self):
        self.reject(lambda x: x["anchors"][0].update(pdf_page_index_zero_based=14))

    def test_wrong_cold_lake_box(self):
        self.reject(lambda x: x["anchors"][1].update(box=36))

    def test_wrong_archive_label(self):
        self.reject(lambda x: x["anchors"][2].update(phrase="NORAD 528 optical observations"))

    def test_fabricated_utc(self):
        self.reject(lambda x: x.update(norad_528_utc="1963-11-08T12:00:00Z"))

    def test_fabricated_station(self):
        self.reject(lambda x: x.update(norad_528_station="Cold Lake"))

    def test_fabricated_sigma(self):
        self.reject(lambda x: x.update(norad_528_sensor_sigma=0.001))

    def test_fabricated_independence(self):
        self.reject(lambda x: x.update(cross_collection_independent_observations=2))

    def test_false_transfer_receipt(self):
        self.reject(lambda x: x.update(norad_528_data_received_by_spadats="YES"))

    def test_false_detection(self):
        self.reject(lambda x: x.update(individual_observations_recovered_from_this_finding_aid=1))

    def test_false_reentry(self):
        self.reject(lambda x: x.update(impact_at_conde="CONFIRMED"))

    def test_false_activation(self):
        self.reject(lambda x: x.update(physical_constraints_activated=1))

    def test_inventory_not_a_telemetry_source(self):
        self.reject(lambda x: x["source"].update(source_class="PRIMARY_OBSERVATION"))

    def test_unexpected_manifest_field(self):
        self.reject(lambda x: x.update(fake_sensor_measurement=1))

    def test_unexpected_anchor_field(self):
        self.reject(lambda x: x["anchors"][0].update(fake_observation=True))

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"id":"C241-L53","id":"fabricated"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_model(path)

    def test_wrong_pdf_bytes(self):
        with self.assertRaises(ValueError):
            live_check(b"%PDF-1.4\nunsupported")

if __name__ == "__main__":
    unittest.main()
