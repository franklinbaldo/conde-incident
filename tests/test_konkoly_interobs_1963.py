"""Adversarial tests: contemporary INTEROBS data on Sputnik 4 are not NORAD 527–529."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('konkoly', ROOT / 'tools/verify_konkoly_interobs_1963.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(MODULE.MANIFEST.read_text(encoding='utf-8'))

    def rejects(self, keys, value):
        mutated = copy.deepcopy(self.data)
        parent = mutated
        for key in keys[:-1]:
            parent = parent[key]
        parent[keys[-1]] = value
        with self.assertRaises(ValueError):
            MODULE.validate(mutated)

    def test_manifest_passes(self):
        self.assertTrue(MODULE.validate(self.data))

    def test_optimized_python_rejects_three_falsifications(self):
        # Run in a REAL optimized interpreter; changing __debug__ in a mock is insufficient.
        script = r"""
import copy, importlib.util, json
from pathlib import Path
p = Path('tools/verify_konkoly_interobs_1963.py')
spec = importlib.util.spec_from_file_location('konkoly_opt', p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
base = json.loads(module.MANIFEST.read_text(encoding='utf-8'))
if module.validate(base) is not True:
    raise RuntimeError("clean source failed in optimized Python")
for kind in ['source_hash', 'wrong_target', 'invented_orbit']:
    sample = copy.deepcopy(base)
    if kind == 'source_hash': sample['source']['sha256'] = '0' * 64
    if kind == 'wrong_target': sample['study']['object_is_1963_003_abc'] = True
    if kind == 'invented_orbit': sample['limits']['orbital_constraints_activated'] = 1
    try:
        module.validate(sample)
    except ValueError:
        continue
    raise RuntimeError(f'optimized Python accepted falsified {kind}')
"""
        for argv in ([sys.executable, '-O'], [sys.executable]):
            with self.subTest(interpreter=argv):
                completed = subprocess.run([*argv, '-c', script], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_fake_html_bytes_rejected(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            fake = Path(tmp) / 'source.html'
            fake.write_text('Kiev U.S.S.R. 1023 29', encoding='utf-8')
            with self.assertRaises(ValueError):
                MODULE.validate(self.data, fake)

    def test_exact_html_replay_when_available(self):
        snapshot = Path('/workspace/lontra-r38-konkoly59.html')
        if not snapshot.is_file():
            self.skipTest('Original snapshot not stored in Git checkout')
        self.assertTrue(MODULE.validate(self.data, snapshot))

    def test_source_integrity(self):
        self.rejects(['source', 'sha256'], '0' * 64)
        self.rejects(['source', 'bytes'], 0)
        self.rejects(['source', 'tls_validated'], False)
        self.rejects(['source', 'original_print_facsimile_retrieved'], True)
        self.rejects(['source', 'original_station_logs_retrieved'], True)

    def test_wrong_satellite_not_target(self):
        self.rejects(['study', 'object_is_1963_003_abc'], True)
        self.rejects(['study', 'object_designation'], '1963-003B')
        self.rejects(['limits', 'target_observations_identified'], True)
        self.rejects(['limits', 'new_target_orbital_measurements'], 1)
        self.rejects(['limits', 'orbital_constraints_activated'], 1)

    def test_cant_attribute_station_fixes_to_november(self):
        self.rejects(['study', 'campaign_includes_1963_nov_07_to_09'], True)
        self.rejects(['study', 'station_counts_cover_all_study_windows_not_only_august_1963'], False)
        self.rejects(['study', 'fixes_by_station_from_table_2', 0, 'fixes'], 30)
        self.rejects(['study', 'simultaneous_positions_used_in_study'], 793)

    def test_original_cited_campaign_volumes_not_retrieved(self):
        self.rejects(['original_campaign_volumes_cited_by_paper', 'full_text_of_volumes_retrieved'], True)
        self.rejects(['original_campaign_volumes_cited_by_paper', 'whether_november_1963_is_covered'], True)
        self.rejects(['original_campaign_volumes_cited_by_paper', 'whether_norad_527_528_529_appear'], False)
        self.rejects(['original_campaign_volumes_cited_by_paper', 'citation_number_in_paper'], 1)

    def test_no_external_contact_or_november_claim(self):
        self.rejects(['limits', 'outreach_sent'], True)
        self.rejects(['limits', 'november_1963_campaign_confirmed'], True)
        self.rejects(['limits', 'raw_station_observations_accessed'], True)


if __name__ == '__main__':
    unittest.main()
