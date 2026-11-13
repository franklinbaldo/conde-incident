"""Offline regression/negative controls for historical NTRS URL variants."""
from __future__ import annotations
from copy import deepcopy
import contextlib
import hashlib
import io
import sys
from unittest.mock import patch
import json
from pathlib import Path
import unittest
from tools.verify_nasa_ssr_legacy_wayback import validate, current_api_errors, main

DOC = json.loads((Path(__file__).resolve().parents[1] / 'research/archive/nasa_ssr_19631115_legacy_wayback_20261113.json').read_text())


class NASAOldNTRSTest(unittest.TestCase):
    def test_exact_three_archival_snapshots_one_payload(self):
        self.assertEqual(validate(DOC), [])
        self.assertEqual(len({x['replay']['sha256'] for x in DOC['captures']}), 1)

    def test_api_url_is_not_legacy_wayback_capture(self):
        bad = deepcopy(DOC)
        bad['captures'][0]['cdx_record']['original'] = bad['current_api_url']
        self.assertTrue(any('exact legacy PDF' in x for x in validate(bad)))

    def test_archived_path_cannot_rewrite_scheme_or_timestamp(self):
        bad = deepcopy(DOC)
        bad['captures'][0]['archived_url'] = bad['captures'][0]['archived_url'].replace('20150217133001', '20150217133002')
        self.assertTrue(any('exactly follow CDX' in x for x in validate(bad)))

    def test_cdx_warc_length_is_not_pdf_bytes(self):
        self.assertNotEqual(DOC['captures'][0]['cdx_record']['length'], DOC['captures'][0]['replay']['bytes'])
        bad = deepcopy(DOC)
        bad['interpretation']['cdx_length_is_pdf_bytes'] = True
        self.assertTrue(any('false independence' in x for x in validate(bad)))

    def test_archive_not_independent_observer(self):
        bad = deepcopy(DOC)
        bad['interpretation']['captures_are_independent_historical_witnesses'] = True
        self.assertTrue(any('false independence' in x for x in validate(bad)))

    def test_digest_mismatch_is_detected(self):
        bad = deepcopy(DOC)
        bad['captures'][0]['cdx_record']['digest'] = 'A' * 32
        self.assertTrue(any('replay hash does not match' in x for x in validate(bad)))

    def test_current_api_pdf_cannot_differ_silently(self):
        bad = deepcopy(DOC)
        bad['current_api_replay']['sha256'] = '0' * 64
        self.assertTrue(any('NASA original/archive bytes differ' in x for x in validate(bad)))


    def test_current_nasa_api_bytes_are_checked_independently(self):
        sample = b'%PDF-1.4\\nindependent synthetic payload\\n%%EOF\\n'
        manifest = {'bytes': len(sample), 'sha256': hashlib.sha256(sample).hexdigest()}
        self.assertEqual(current_api_errors(manifest, sample, http_status=200,
                                            content_type='application/pdf; charset=binary'), [])
        altered = sample.replace(b'independent', b'altered____')
        self.assertTrue(any('SHA-256 mismatch' in x for x in
                            current_api_errors(manifest, altered, http_status=200,
                                               content_type='application/pdf')))

    def test_fetch_reaches_nasa_api_not_just_three_wayback_urls(self):
        visited = []

        class FakeResponse:
            status = 200
            headers = {'Content-Type': 'application/pdf'}

            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, count): return b'%PDF-1.4\\nchanged NASA API response\\n%%EOF'

        def fake_urlopen(request, timeout):
            visited.append(request.full_url)
            return FakeResponse()

        with patch('tools.verify_nasa_ssr_legacy_wayback.urlopen', side_effect=fake_urlopen), \\
             patch('tools.verify_nasa_ssr_legacy_wayback.replay_errors', return_value=[]), \\
             patch.object(sys, 'argv', ['verifier', '--fetch']), \\
             contextlib.redirect_stdout(io.StringIO()):
            result = main()
        # Wayback HTTP is faked solely to isolate the independent NASA API fetch.
        # Before G30 the script returned 0 after visiting only three archive URLs.
        self.assertEqual(result, 1)
        self.assertEqual(len(visited), 4)
        self.assertEqual(visited[-1], DOC['current_api_url'])


if __name__ == '__main__':
    unittest.main()
