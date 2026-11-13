"""Source and epistemic controls for modern 82899 vs 82900 catalogue labels."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('audit_wmo', ROOT / 'tools/audit_recife_wmoid_catalogues.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class SourceCatalogueCrosscheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(mod.ARTIFACT.read_text())
        cls.excerpt = mod.EXCERPT.read_bytes()

    def test_committed_evidence(self):
        mod.check(self.manifest, self.excerpt)

    def test_distinct_wmo_ids_and_sources(self):
        self.assertEqual([r['wmo_id'] for r in self.manifest['catalogue_records']], [82900,82899])
        self.assertEqual(len({r['source_key'] for r in self.manifest['catalogue_records']}), 2)

    def test_ceda_82900_exact_source_line(self):
        self.assertRegex(self.excerpt.decode(),r'CEDA\t82900\s+Recife/Curado')

    def test_adversarial_id_collision(self):
        broken = json.loads(json.dumps(self.manifest))
        broken['catalogue_records'][1]['wmo_id'] = 82900
        with self.assertRaises(ValueError): mod.check(broken, self.excerpt)

    def test_adversarial_hash_corruption(self):
        with self.assertRaises(ValueError): mod.check(self.manifest, self.excerpt+b'X')

    def test_adversarial_invented_1963_equipment(self):
        broken = json.loads(json.dumps(self.manifest))
        broken['physical_1963']['historical_1963_instrument'] = 'VAISALA'
        with self.assertRaises(ValueError): mod.check(broken, self.excerpt)

    def test_adversarial_independent_sounding(self):
        broken = json.loads(json.dumps(self.manifest))
        broken['catalogue_records'][0]['independent_igra_sounding'] = True
        with self.assertRaises(ValueError): mod.check(broken, self.excerpt)

    def test_underdetermined_transfer(self):
        self.assertIsNone(self.manifest['physical_1963']['recife_to_conde_transfer_error'])
        self.assertFalse(self.manifest['admissible_domain_reduction'])
        self.assertEqual(self.manifest['status'], 'CONNECTED_PENDING_CALIBRATION')


if __name__ == '__main__':
    unittest.main()
