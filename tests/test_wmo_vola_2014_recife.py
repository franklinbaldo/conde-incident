"""Adversarial controls against WMO 2014 / IGRA 1963 epoch confusion."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_wmo_vola_2014_recife as audit


class WmoVolumeA2014Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(audit.SOURCE.read_text(encoding="utf-8"))

    def reject(self, mutator):
        bad = copy.deepcopy(self.data)
        mutator(bad)
        with self.assertRaises(ValueError):
            audit.validate(bad)

    def test_source_and_station_pair(self):
        self.assertTrue(audit.validate(self.data))
        self.assertEqual({r["wmo_id"] for r in self.data["rows"]}, {82899, 82900})

    def test_wrong_epoch_rejected(self):
        self.reject(lambda d: d["source"].update(edition="1963-11"))

    def test_wrong_wmo_prefix_rejected(self):
        self.reject(lambda d: d["rows"][0].update(wmo_id=82999))

    def test_false_2014_radiowind_schedule_rejected(self):
        self.reject(lambda d: d["rows"][1]["upper_air_at_utc_2014"].__setitem__(2, "."))

    def test_backdated_sonde_site_rejected(self):
        self.reject(lambda d: d["historical_1963"].update(launch_site_wmo_id=82900))

    def test_invented_instrument_rejected(self):
        self.reject(lambda d: d["historical_1963"].update(radiosonde_model="unknown-model"))

    def test_fabricated_pdf_hash_rejected(self):
        self.reject(lambda d: d["source"].update(pdf_sha256="deadbeef"))

    def test_premature_domain_reduction_rejected(self):
        self.reject(lambda d: d.update(admissible_domain_reduction=True))

    def test_bad_extracted_row_rejected(self):
        self.reject(lambda d: d["rows"][0].update(transcribed_pdf_row=d["rows"][0]["transcribed_pdf_row"].replace("19.00", "29.00", 1)))


if __name__ == "__main__":
    unittest.main()
