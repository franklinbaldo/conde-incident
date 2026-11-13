"""C241-L17 adversarial regression: NASA August is publication, not epoch."""
import copy
import json
import unittest
from pathlib import Path

from tools.tle_nasa_ssr_aug15_audit import audit, validate

ROOT = Path(__file__).resolve().parents[1] / "research" / "tle_custody"
AUG = json.loads((ROOT / "nasa_ssr_aug15_1963_C241-L17.json").read_text())
APR = json.loads((ROOT / "nasa_ssr_apr_oct_1963_C241-L16.json").read_text())
OCT = json.loads((ROOT / "nasa_ssr_1963_oct15_C241-L12.json").read_text())


class TestAugustProvenance(unittest.TestCase):
    def reject(self, change):
        a, e, o = copy.deepcopy(AUG), copy.deepcopy(APR), copy.deepcopy(OCT)
        change(a, e, o)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate(a, e, o)

    def test_three_sequences_not_rates(self):
        rows = validate(AUG, APR, OCT)
        self.assertEqual([r["printed_period_min"] for r in rows],
                         [["94.6", "94.6", "94.6"], ["94.1", "93.3", "92.4"],
                          ["94.3", "93.8", "93.3"]])
        self.assertEqual([r["publication_step_delta_min_not_physical_rate"] for r in rows],
                         [["0.0", "0.0"], ["-0.8", "-0.9"], ["-0.5", "-0.5"]])
        self.assertTrue(all(r["epoch_of_elements"] is None for r in rows))
        self.assertTrue(all(r["independent_sensor_observation"] is False for r in rows))

    def test_apogee_and_perigee_sequences(self):
        rows = validate(AUG, APR, OCT)
        self.assertEqual([r["printed_apogee_km"] for r in rows],
                         [[537, 537, 531], [505, 455, 401], [531, 493, 458]])
        self.assertEqual([r["printed_perigee_km"] for r in rows],
                         [[460, 458, 462], [435, 412, 376], [437, 422, 408]])

    def test_wrong_document_number(self):
        self.reject(lambda a,e,o: a["source"].update(ntrs_id="19630012290"))

    def test_wrong_date_or_number(self):
        self.reject(lambda a,e,o: a["source"].update(number=15))

    def test_wrong_as_of_time(self):
        self.reject(lambda a,e,o: a["source"].update(data_as_of="SENSOR EPOCH"))

    def test_wrong_pdf_page(self):
        self.reject(lambda a,e,o: a["source"].update(pdf_page_index_zero_based=5))

    def test_wrong_checksum(self):
        self.reject(lambda a,e,o: a["source"].update(sha256="f"*64))

    def test_wrong_transcription(self):
        self.reject(lambda a,e,o: a["rows"][1].update(nodal_period_min="93.4"))

    def test_forged_precision(self):
        self.reject(lambda a,e,o: a["rows"][1].update(nodal_period_min="93.30"))

    def test_wrong_inclination(self):
        self.reject(lambda a,e,o: a["rows"][0].update(inclination_deg="81.87"))

    def test_wrong_perigee(self):
        self.reject(lambda a,e,o: a["rows"][2].update(perigee_km=423))

    def test_cross_object_swap(self):
        self.reject(lambda a,e,o: a["rows"][0].update(designator="1963-003B"))

    def test_duplicate_entry(self):
        self.reject(lambda a,e,o: a["rows"].append(a["rows"][0]))

    def test_modified_april_corpus(self):
        self.reject(lambda a,e,o: e["april_rows"][1].update(nodal_period_min="94.0"))

    def test_modified_october_corpus(self):
        self.reject(lambda a,e,o: o["catalog_rows"][1].update(nodal_period_min_printed="92.3"))

    def test_invented_sensor_epoch(self):
        self.reject(lambda a,e,o: a["limits"].update(publication_date_is_element_epoch=True))

    def test_invented_instrumental_independence(self):
        self.reject(lambda a,e,o: a["limits"].update(independent_sensor_observation=True))

    def test_invented_frame(self):
        self.reject(lambda a,e,o: a["limits"].update(physical_frame="TEME"))

    def test_invented_sensor(self):
        self.reject(lambda a,e,o: a["limits"].update(observing_station="XYZ"))

    def test_invented_terminal_time(self):
        self.reject(lambda a,e,o: a["limits"].update(terminal_time="1963-11-08T23:59Z"))

    def test_invented_raan(self):
        self.reject(lambda a,e,o: a["limits"].update(raan_deg=284.1520))

    def test_invented_report_21(self):
        self.reject(lambda a,e,o: a["limits"].update(issue_21="RECOVERED"))

    def test_wrong_dependency(self):
        self.reject(lambda a,e,o: a["dependencies"].update(object_id_crosswalk="C241-L9"))

    def test_rejects_non_pdf(self):
        with self.assertRaisesRegex(ValueError, "not a PDF"):
            audit(AUG, APR, OCT, b"fake")

    def test_rejects_forged_pdf(self):
        with self.assertRaisesRegex(ValueError, "PDF bytes/hash mismatch"):
            audit(AUG, APR, OCT, b"%PDF-1.4\nFAKE\n%%EOF")


if __name__ == "__main__":
    unittest.main()
