"""Offline regression/negative controls for historical NTRS URL variants."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
import unittest
from tools.verify_nasa_ssr_legacy_wayback import validate

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


if __name__ == '__main__':
    unittest.main()
