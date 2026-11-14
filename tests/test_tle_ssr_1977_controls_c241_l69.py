"""Adversarial NASA 1977 292/565 crosswalk checks under Python and -O."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tle_ssr_1977_controls_c241_l69 as audit

class ControlTest(unittest.TestCase):
    def setUp(self):
        self.data = audit.load()

    def mutate(self, fn):
        other = copy.deepcopy(self.data)
        fn(other)
        with self.assertRaises(ValueError):
            audit.validate(other)

    def test_positive(self):
        self.assertTrue(audit.validate(self.data))
    def test_292_id(self):
        self.mutate(lambda x: x["rows"][0].__setitem__("norad_id", 293))
    def test_565_id(self):
        self.mutate(lambda x: x["rows"][1].__setitem__("norad_id", 566))
    def test_sigma_name(self):
        self.mutate(lambda x: x["rows"][0].__setitem__("source_printed_designation", "SIGMA 2"))
    def test_565_name(self):
        self.mutate(lambda x: x["rows"][1].__setitem__("source_printed_designation", "1963 009A"))
    def test_1963_spelling(self):
        self.mutate(lambda x: x["rows"][1].__setitem__("publication_1963_designation", "1963 009B"))
    def test_page(self):
        self.mutate(lambda x: x["rows"][1].__setitem__("pdf_page_index_zero_based", 45))
    def test_date(self):
        self.mutate(lambda x: x["rows"][0].__setitem__("decay_printed", "27 NOV 63"))
    def test_hash(self):
        self.mutate(lambda x: x["source"].__setitem__("sha256", "0"*64))
    def test_not_1963_document(self):
        self.mutate(lambda x: x["source"].__setitem__("publication_date", "1963-11-30"))
    def test_pdf_not_independent(self):
        self.mutate(lambda x: x["source"].__setitem__("new_independent_tracking_source", True))
    def test_no_midnight(self):
        self.mutate(lambda x: x["rows"][0].__setitem__("terminal_utc", "1963-11-26T00:00Z"))
    def test_no_sensor(self):
        self.mutate(lambda x: x["rows"][1].__setitem__("sensor", "radar"))
    def test_no_sigma(self):
        self.mutate(lambda x: x["rows"][0].__setitem__("temporal_sigma_seconds", 86400))
    def test_no_physical_528(self):
        self.mutate(lambda x: x["limits"].__setitem__("norad_528_hard_constraints_added", 1))
    def test_no_independent_sensor(self):
        self.mutate(lambda x: x["limits"].__setitem__("independent_tracking_observations_added", 2))
    def test_no_1963_printed_norad(self):
        self.mutate(lambda x: x["limits"].__setitem__("source_norad_number_printed_in_1963", True))
    def test_no_dup_keys(self):
        with self.assertRaises(ValueError):
            audit.unique_pairs([("source", 1), ("source", 2)])
    def test_wrong_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "fake.pdf"
            file.write_bytes(b"%PDF-fake")
            with self.assertRaises(ValueError):
                audit.verify_pdf(file)

if __name__ == "__main__":
    unittest.main()
