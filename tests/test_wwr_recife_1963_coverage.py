"""Adversarial tests for the archive-specific negative WWR finding."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('wwr_audit', ROOT / 'tools/audit_wwr_recife_1963_coverage.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class WWRRecifeCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(mod.ARTIFACT.read_text(encoding='utf-8'))
        cls.headers = mod.extract_headers(mod.HEADERS.read_bytes())

    def test_excerpt_integrity(self):
        mod.verify_snapshot(self.data)

    def test_brazil_headers_21_unique(self):
        self.assertEqual(len(self.headers), 21)
        self.assertEqual(len({r[2:7] for r in self.headers}), 21)

    def test_no_82900_or_82899_not_negative_for_igra(self):
        self.assertFalse(set(('82899', '82900')) & {r[2:7] for r in self.headers})
        self.assertFalse(self.data['independent_upper_air_observation'])
        self.assertIsNone(self.data['spatial_transfer_calibration'])
        self.assertEqual(self.data['status'], 'CONNECTED_PENDING_CALIBRATION')

    def test_real_brazilian_station_identifiers(self):
        self.assertIn('83096', {r[2:7] for r in self.headers})  # Aracaju
        self.assertIn('82397', {r[2:7] for r in self.headers})  # Fortaleza

    def test_adversarial_injected_recife_record(self):
        fake = self.headers[0][:2] + '82900' + self.headers[0][7:]
        report = mod.manifest_from_headers(self.headers + [fake])
        self.assertEqual(report['recife_wmo_candidates_present'], ['82900'])
        self.assertNotEqual(report, self.data)

    def test_duplicate_station_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicated'):
            mod.manifest_from_headers(self.headers + [self.headers[0]])

    def test_damaged_snapshot_rejected(self):
        tampered = self.headers[0][:-1] + 'X' + '\n' + '\n'.join(self.headers[1:]) + '\n'
        self.assertNotEqual(mod.manifest_from_headers(mod.extract_headers(tampered.encode('ascii'))), self.data)


if __name__ == '__main__':
    unittest.main()
