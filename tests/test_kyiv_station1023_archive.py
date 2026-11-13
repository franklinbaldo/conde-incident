"""Adversarial source custody tests for station 1023 archival lead."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('station1023', ROOT / 'tools/verify_kyiv_station1023_archive.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class ArchiveContract(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(M.MANIFEST.read_text())

    def reject(self, path, value):
        changed = copy.deepcopy(self.d)
        parent = changed
        for field in path[:-1]:
            parent = parent[field]
        parent[path[-1]] = value
        with self.assertRaises(ValueError):
            M.validate(changed)

    def test_manifest(self):
        self.assertTrue(M.validate(self.d))

    def test_actual_html_byte_hash_replay(self):
        paths = [Path('/workspace/lontra-r37-source/museum-research.html'),
                 Path('/workspace/lontra-r37-source/museum-funds.html')]
        if not all(path.is_file() for path in paths):
            self.skipTest('Original snapshots external to repository')
        self.assertTrue(M.validate(self.d, paths))

    def test_museum_source_integrity(self):
        self.reject(['sources', 0, 'sha256'], '0' * 64)
        self.reject(['sources', 1, 'bytes'], 0)
        self.reject(['sources', 0, 'tls_validated'], False)

    def test_retrospective_pdf_not_downloaded(self):
        self.reject(['sources', 2, 'sha256'], '0' * 64)
        self.reject(['sources', 3, 'bytes'], 100)
        self.reject(['sources', 2, 'printed_pages_checked_visually'], [116])

    def test_retrospective_counts_not_1963(self):
        self.reject(['station', 'reported_positions_measured_all_years'], 77135)
        self.reject(['station', 'counts_are_not_1963_counts'], False)
        self.reject(['station', 'regular_operational_years_reported'], [1963, 1983])

    def test_1976_report_not_1963(self):
        self.reject(['station', 'archive_1976_is_not_archive_1963'], False)
        self.reject(['station', 'museum_archive_cited_for_1976_report'], '1963 file')

    def test_no_target_detection_or_anachronistic_instrument(self):
        self.reject(['station', 'unknown_objects_are_not_identified_as_norad_targets'], False)
        self.reject(['station', 'kft_phototheodolite_not_1963_evidence'], False)
        self.reject(['limits', 'observation_for_norad_527_528_529_confirmed'], True)
        self.reject(['limits', 'orbital_constraints_activated'], 1)
        self.reject(['limits', 'outreach_sent'], True)

    def test_optimized_python_cannot_bypass_scientific_guards(self):
        baseline = (
            'import json\n'
            'from tools.verify_kyiv_station1023_archive import MANIFEST, validate\n'
            'd=json.loads(MANIFEST.read_text())\n'
        )
        for tamper in (
            '',
            "d['limits']['orbital_constraints_activated']=1\n",
            "d['station']['unknown_objects_are_not_identified_as_norad_targets']=False\n",
            "d['sources'][0]['sha256']='0'*64\n",
        ):
            result = subprocess.run(
                [sys.executable, '-O', '-c', baseline + tamper + 'validate(d)\n'],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            if not tamper:
                self.assertEqual(result.returncode, 0, result.stderr)
            else:
                self.assertNotEqual(result.returncode, 0, tamper)
                self.assertIn('ValueError', result.stderr)

    def test_no_claim_current_custody(self):
        self.reject(['limits', 'current_custody_in_2026_confirmed'], True)
        self.reject(['limits', 'original_1963_reports_retrieved'], True)
        self.reject(['sources', 2, 'direct_download_http_status_in_executor'], 200)


if __name__ == '__main__':
    unittest.main()
