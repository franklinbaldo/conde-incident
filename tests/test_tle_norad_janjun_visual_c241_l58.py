import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("l58", ROOT / "tools/tle_norad_janjun_visual_c241_l58.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class VisualErrataTests(unittest.TestCase):
    def setUp(self):
        self.ok = json.loads(mod.ADDENDUM.read_text(), object_pairs_hook=mod.unique)

    def corrupt(self, callback):
        record = copy.deepcopy(self.ok)
        callback(record)
        with self.assertRaises(ValueError):
            mod.audit(record)

    def test_baseline(self):
        self.assertEqual(mod.audit(self.ok)["corrected_pdf_pages"], [47, 48, 49])

    def test_wrong_zero_based(self):
        self.corrupt(lambda x: x["pages"][0].update(pdf_zero_based=47))

    def test_wrong_one_based(self):
        self.corrupt(lambda x: x["pages"][2].update(pdf_one_based=48))

    def test_missing_third_page(self):
        self.corrupt(lambda x: x["pages"].pop())

    def test_changed_fact(self):
        self.corrupt(lambda x: x["pages"][2].update(fact="NORAD 528 measured"))

    def test_false_ocr(self):
        self.corrupt(lambda x: x.update(visual_scope="OCR_CONFIRMED"))

    def test_camera_double_count(self):
        self.corrupt(lambda x: x["inventory"].update(total_in_existence=18))

    def test_fake_transfer_date(self):
        self.corrupt(lambda x: x["cold_lake"].update(effective_date="1963-05-09"))

    def test_fake_spadats_receipt(self):
        self.corrupt(lambda x: x["cold_lake"].update(**{"528_data_receipt": True}))

    def test_fake_sigma(self):
        self.corrupt(lambda x: x["cold_lake"].update(**{"528_instrument_sigma": 0.1}))

    def test_fake_sensor(self):
        self.corrupt(lambda x: x["source"].update(independent_source=True))

    def test_fake_geography(self):
        self.corrupt(lambda x: x["epistemic"].update(active_physical_constraint=True))

    def test_wrong_parent_bytes(self):
        with self.assertRaises(ValueError):
            mod.audit(self.ok, b"forgery")

    def test_duplicate_key(self):
        with self.assertRaises(ValueError):
            json.loads('{"x":1,"x":2}', object_pairs_hook=mod.unique)

    def test_invalid_pdf_bytes(self):
        with self.assertRaises(ValueError):
            mod.verify_pdf(b"%PDF fake")


if __name__ == "__main__":
    unittest.main()
