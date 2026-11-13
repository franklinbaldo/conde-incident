"""Adversarial ISD provenance tests for Caravelas November 1963."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('caravelas_flags', ROOT / 'tools/audit_isd_caravelas_source_flags_1963.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SourceProvenanceTests(unittest.TestCase):
    def test_exact_window(self):
        self.assertEqual(mod.verify_snapshot()['source_flags'], {'N': 72})

    def test_source_changed(self):
        snapshot = mod.raw_window()
        edited = snapshot.replace(b'196311070000N', b'1963110700005', 1)
        self.assertNotEqual(mod.fields(edited)['source_flags'], {'N': 72})

    def test_report_changed(self):
        snapshot = mod.raw_window()
        edited = snapshot.replace(b'BRAZ ', b'FM-12', 1)
        self.assertNotEqual(mod.fields(edited)['report_type_codes'], {'BRAZ': 72})

    def test_station_changed(self):
        snapshot = mod.raw_window()
        with self.assertRaises(ValueError):
            mod.fields(snapshot.replace(b'83497099999', b'83229099999', 1))

    def test_date_changed(self):
        snapshot = mod.raw_window()
        with self.assertRaises(ValueError):
            mod.fields(snapshot.replace(b'19631107', b'19631007', 1))

    def test_duplicate_hour(self):
        snapshot = mod.raw_window()
        with self.assertRaises(ValueError):
            mod.fields(snapshot + snapshot.splitlines(keepends=True)[0])

    def test_missing_hour(self):
        snapshot = mod.raw_window()
        with self.assertRaises(ValueError):
            mod.fields(b''.join(snapshot.splitlines(keepends=True)[:-1]))

    def test_changed_annual_pin(self):
        with self.assertRaises(ValueError):
            mod.verify_gzip(b'fake archive')

    def test_no_calibrated_transfer_claim(self):
        out = mod.audit()
        for k in ('original_station_instrument_1963', 'historical_geographic_transfer_to_conde',
                  'independence_from_other_noaa_products', 'active_conde_constraint'):
            self.assertIsNone(out[k])


if __name__ == '__main__':
    unittest.main()
