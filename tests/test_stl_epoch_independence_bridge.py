"""Adversarial source identity, temporal semantics and zero-promotion checks (-O safe)."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import export_stl_epoch_independence_bridge as bridge


class STLEpochIndependenceBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r51, cls.cerv, cls.parent = bridge.load()

    def test_site_exact_and_non_promoting(self):
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())
        data = bridge.build(self.r51, self.cerv, self.parent)
        self.assertEqual(16, len(data['graph']))
        self.assertFalse(data['activation'])
        self.assertEqual('THETA_UNCHANGED', data['physical_domain_effect'])
        self.assertEqual(0, data['new_independent_instrumental_observations'])
        self.assertEqual(0, data['new_activated_physical_constraints'])
        self.assertIsNone(data['measurement_epoch_utc'])
        self.assertIsNone(data['first_column_is_initial'])
        self.assertIsNone(data['columns_coepoch'])
        self.assertTrue(data['not_a_norad_528_observation'])
        self.assertFalse(data['period_difference_excludes_zero'])
        self.assertEqual('CANDIDATE_ONLY_NOT_COMPILED', data['lean_status'])
        for node in data['graph']:
            self.assertTrue(node['documentary_only'])
            self.assertFalse(node['activation'])
        for item in data['latents'] + data['simulator_parameters']:
            self.assertIsNone(item['value'])
            self.assertFalse(item['activation'])

    def reject(self, which, path, changed):
        vals = list(map(copy.deepcopy, (self.r51, self.cerv, self.parent)))
        target = vals[which]
        for name in path[:-1]:
            target = target[name]
        target[path[-1]] = changed
        with self.assertRaises(ValueError):
            bridge.build(*vals)

    def test_reject_other_day_as_measurement(self):
        self.reject(1, ['other_column_measurement_utc'], '1963-11-08T23:30:00Z')

    def test_reject_coepoch_inference(self):
        self.reject(1, ['columns_are_coepoch'], True)

    def test_reject_unsupported_column_identity(self):
        self.reject(1, ['initial_data_column_index'], 0)

    def test_reject_editing_printed_note(self):
        self.reject(0, ['printed_row', 'row_note'], 'initial orbital data as of November 8, 1963')

    def test_reject_unsupported_independence(self):
        self.reject(2, ['independent_from_R51'], True)

    def test_reject_sensors(self):
        self.reject(1, ['observational_design', 'new_528_tracking_observations'], 1)

    def test_reject_rounding_as_proof(self):
        self.reject(1, ['conditional_rounding_model', 'zero_underlying_difference_excluded'], True)

    def test_reject_pdf_identity(self):
        self.reject(1, ['source_pdf_sha256'], '0' * 64)

    def test_reject_parent_activation(self):
        self.reject(2, ['activation'], True)

    def test_reject_parent_duplicate_source(self):
        self.reject(2, ['new_independent_instrumental_observations'], 1)

    def test_reject_source_digest_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for p in (bridge.R51, bridge.CERV, bridge.PARENT):
                f = root / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((ROOT / p).read_bytes())
            corrupt = root / bridge.CERV
            corrupt.write_bytes(corrupt.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'source SHA drift'):
                bridge.load(root)


if __name__ == '__main__':
    unittest.main()
