"""Adversarial tests: USAF reports on 687/688 cannot constrain 528."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from export_norad_1963_operational_bridge import (
    build, render, PINNED, LEDGER, MOR, UN, OUTPUT,
)


class NoradContextScientificBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = tuple(json.loads((ROOT / p).read_bytes()) for p in (LEDGER, MOR, UN))

    def mutate(self, fn, index=0):
        parts = copy.deepcopy(self.parent)
        fn(parts[index])
        with self.assertRaises(ValueError):
            build(*parts)

    def test_canonical_result_is_byte_reproducible_and_inactive(self):
        self.assertEqual(render(), OUTPUT.read_bytes())
        d = json.loads(render())
        self.assertEqual(d['source_occurrence'], 'C241-L46')
        self.assertEqual(d['related_matrix_occurrence'], 'C197#1')
        self.assertEqual(len(d['dependency_graph']), 10)
        self.assertEqual([s['source_id'] for s in d['source_documents']],
                         ['C241-L46-D07', 'C241-L46-D08'])
        self.assertEqual(d['other_object_688_reported_decay_window']['object_id'], 688)
        self.assertEqual(d['nasa_catalogued_decay_day_528'], '1963-11-08')
        self.assertEqual(d['reported_administrative_status_528_by'], '2400Z 15 NOVEMBER 1963')
        self.assertEqual(d['independent_528_instrumental_observations_added'], 0)
        self.assertFalse(d['activation'])
        self.assertEqual(d['physical_domain_effect'], 'THETA_UNCHANGED')
        for p in d['simulator_latent_parameters']:
            self.assertIsNone(p['value'])
            self.assertFalse(p['activation'])
        for c in d['observation_candidates_527_528_529']:
            self.assertIsNone(c['source_measurement'])
            self.assertIsNone(c['sigma'])
            self.assertFalse(c['activation'])
        for edge in d['dependency_graph']:
            self.assertFalse(edge['independent_physical_observation'])
            self.assertFalse(edge['activation'])

    def test_reject_cross_object_decay_interval(self):
        self.mutate(lambda d: d['sources'][1]['decay_window'].update(object_id=528))
        self.mutate(lambda d: d['sources'][1]['decay_window'].update(start='0800Z'))
        self.mutate(lambda d: d['sources'][0].update(decay_window={'object_id': 528}))

    def test_reject_forged_528_measurement(self):
        self.mutate(lambda d: d['target'].update(observation_utc='1963-11-08T08:00:00Z'))
        self.mutate(lambda d: d['target'].update(sigma=0.001))
        self.mutate(lambda d: d['sources'][0].update(measurement_528={'station': 'Shemya'}))
        self.mutate(lambda d: d['sources'][0].update(object_ids=[528, 687, 688]))
        self.mutate(lambda d: d['sources'][1].update(launch='1963-003'))

    def test_reject_dependency_and_document_mutations(self):
        self.mutate(lambda d: d['sources'][1].update(sha256='0' * 64))
        self.mutate(lambda d: d['sources'][0].update(document_date='1963-11-08'))
        self.mutate(lambda d: d['sources'][1].update(message='AF IN 20080'))
        self.mutate(lambda d: d['sources'].append(copy.deepcopy(d['sources'][0])))
        self.mutate(lambda d: d['records'][1].update(original_pdf_sha256='0' * 64), index=1)
        self.mutate(lambda d: d['epistemic_limits'].update(no_source_is_an_observation_of_norad_528=False), index=1)
        self.mutate(lambda d: d['documentary_status_528'].update(actual_terminal_time_utc='1963-11-08T12:00Z'), index=2)
        self.mutate(lambda d: d['documentary_status_528'].update(reporting_independence='INDEPENDENT'), index=2)

    def test_source_file_checksum_and_site_guard(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in PINNED:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / rel).read_bytes())
            self.assertEqual(render(root), render())
            (root / LEDGER).write_bytes((root / LEDGER).read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'input byte drift'):
                render(root)
        result = subprocess.run([sys.executable,
                                 str(ROOT / 'tools/export_norad_1963_operational_bridge.py'),
                                 '--check-site'], check=False, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == '__main__':
    unittest.main()
