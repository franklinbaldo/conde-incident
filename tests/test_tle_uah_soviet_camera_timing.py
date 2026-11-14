"""Contraprovas de proveniencia e de transferencia orbital indevida: C241-L47."""
import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import tle_uah_soviet_camera_timing_audit as auditor


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.d = auditor.load()

    def invalid(self, change):
        altered = copy.deepcopy(self.d)
        change(altered)
        with self.assertRaises(ValueError):
            auditor.audit(altered)

    def test_original(self):
        self.assertTrue(auditor.audit(self.d))

    def test_no_orbital_528(self):
        self.invalid(lambda d: d["target"].update(observation_utc="1963-11-08T23:30:00Z"))

    def test_no_sensor_identity_transfer(self):
        self.invalid(lambda d: d["target"].update(sensor_identity_for_528="NAFA-3S/25-S"))

    def test_no_error_transfer(self):
        self.invalid(lambda d: d["target"].update(instrument_sigma_for_528=0.0002))

    def test_no_reentry_location(self):
        self.invalid(lambda d: d["target"].update(reentry_location="Conde, Bahia"))

    def test_no_activation(self):
        self.invalid(lambda d: d.update(orbital_constraint_active=True))

    def test_source_not_primary(self):
        self.invalid(lambda d: d.update(epistemic_status="PRIMARY_ORBITAL_OBSERVATION"))

    def test_source_sha(self):
        self.invalid(lambda d: d["source_copies"][1].update(sha256="0" * 64))

    def test_source_swapped(self):
        self.invalid(lambda d: d["source_copies"].reverse())

    def test_page_shift(self):
        self.invalid(lambda d: d["inspected_context"].update(page_pdf_index_zero_based=24))

    def test_camera_data_mutation(self):
        self.invalid(lambda d: d["inspected_context"].update(chronograph_delay_at_230_volts_seconds_printed="0.0268"))

    def test_uncertainty_mutation(self):
        self.invalid(lambda d: d["inspected_context"].update(opening_shutter_plusminus_seconds_printed="0.002"))

    def test_unretrieved_russian_original(self):
        self.invalid(lambda d: d["inspected_context"].update(original_russian_page_recovered=True))

    def test_independence(self):
        self.invalid(lambda d: d.update(family_count=3))

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=auditor.reject_duplicate_keys)

    def test_pdf_integrity(self):
        mock = self.d["source_copies"][1]
        with self.assertRaises(ValueError):
            auditor.verify_pdf(mock, b"%PDF-fake%%EOF")

    def test_no_hidden_alternative(self):
        self.invalid(lambda d: d["target"].update(impact_proved=True))


if __name__ == "__main__":
    unittest.main()
