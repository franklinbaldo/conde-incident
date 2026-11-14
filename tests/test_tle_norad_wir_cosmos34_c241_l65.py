"""C241-L65 adverse proof that a 1964 estimated de-orbit cannot calibrate 528."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tle_norad_wir_cosmos34_c241_l65 as subject


class NORAD1964(unittest.TestCase):
    def setUp(self):
        self.record = subject.load()

    def falsify(self, section, field, val):
        changed = copy.deepcopy(self.record)
        changed[section][field] = val
        with self.assertRaises(ValueError):
            subject.verify_record(changed)

    def test_canonical(self):
        self.assertEqual(subject.verify_record(self.record)["observations_528"], 0)

    def test_do_not_forge_utc_for_528(self):
        self.falsify("interpretation", "permits_utc_terminal_point_for_528", True)

    def test_do_not_infer_sigma(self):
        self.falsify("interpretation", "permits_five_minute_sigma_for_528", True)

    def test_no_sigma_document(self):
        self.falsify("report", "time_uncertainty_sigma_seconds", 300)

    def test_no_sensor(self):
        self.falsify("report", "sensor", "NORAD radar")

    def test_no_station(self):
        self.falsify("report", "instrument_observation_id", "imaginary")

    def test_not_norad528(self):
        self.falsify("interpretation", "same_event_as_1963_norad_528", True)

    def test_not_norad308(self):
        self.falsify("interpretation", "same_event_as_1963_norad_308", True)

    def test_no_activated_constraints(self):
        self.falsify("interpretation", "activated_orbital_constraints_528", 1)

    def test_date_1964(self):
        self.falsify("report", "event_date", "1963-11-08")

    def test_original_qualifier(self):
        self.falsify("report", "qualifier", "confirmed")

    def test_interval_literal(self):
        self.falsify("report", "event_printed", "reentered at 0933Z")

    def test_no_independent_sensor(self):
        self.falsify("interpretation", "original_independent_measurements_528", 1)

    def test_sha256(self):
        self.falsify("source", "pdf_sha256", "0" * 64)

    def test_source_date(self):
        self.falsify("source", "published_on", "1963-07-17")

    def test_no_extra_field(self):
        changed = copy.deepcopy(self.record)
        changed["interpretation"]["observed_reentry_latitude"] = -7.2
        with self.assertRaises(ValueError):
            subject.verify_record(changed)

    def test_type_guard_bool_int(self):
        self.falsify("source", "pdf_bytes", True)

    def test_duplicate_key_rejected(self):
        with self.assertRaises(ValueError):
            subject.no_duplicates([("a", 1), ("a", 2)])

    def test_wrong_pdf_rejected(self):
        with self.assertRaises(ValueError):
            subject.verify_pdf(ROOT / "AGENTS.md")

    def test_missing_pdf_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            pdf = Path(td) / "missing.pdf"
            with self.assertRaises(FileNotFoundError):
                subject.verify_pdf(pdf)


if __name__ == "__main__":
    unittest.main()
