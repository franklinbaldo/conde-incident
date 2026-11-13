"""Offline adversarial tests for NMC ON20 historical Wayback PDF-prefix."""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from tools.verify_on20_wayback_prefix import validate, payload_errors, relation_errors

DOC = json.loads((Path(__file__).resolve().parents[1] /
                  'research/archive/on20_wayback_prefix_20261113.json').read_text())


class ON20WaybackPrefixTests(unittest.TestCase):
    def test_exact_three_records_and_status(self):
        self.assertEqual(validate(DOC), [])
        self.assertEqual([r['assessment'] for r in DOC['snapshots']],
                         ['TRUNCATED_PREFIX_NOT_RECOMMENDED', 'COMPLETE_PDF_REPLAY',
                          'COMPLETE_PDF_REPLAY'])

    def test_early_cdx_http_200_is_not_a_valid_complete_pdf(self):
        early = DOC['snapshots'][0]
        self.assertEqual(early['cdx']['statuscode'], '200')
        self.assertFalse(early['replay']['pdf_eof'])
        self.assertNotEqual(early['replay']['bytes'], early['cdx']['length'])
        bad = deepcopy(DOC)
        bad['snapshots'][0]['assessment'] = 'COMPLETE_PDF_REPLAY'
        self.assertTrue(any('recommended use' in e for e in validate(bad)))

    def test_early_snapshot_cannot_inherit_later_digest(self):
        bad = deepcopy(DOC)
        bad['snapshots'][0]['cdx']['digest'] = bad['snapshots'][1]['cdx']['digest']
        self.assertTrue(any('CDX/replay' in e for e in validate(bad)))

    def test_time_url_must_be_cdx_exact_match(self):
        bad = deepcopy(DOC)
        bad['snapshots'][1]['archived_url'] = bad['snapshots'][1]['archived_url'].replace('20080920175518', '20080920175519')
        self.assertTrue(any('archive URL' in e for e in validate(bad)))

    def test_one_source_not_new_edition_or_orbital_observation(self):
        bad = deepcopy(DOC)
        bad['comparison']['distinct_cdx_sha1_digests_imply_distinct_historical_editions'] = True
        self.assertTrue(any('false provenance' in e for e in validate(bad)))
        bad = deepcopy(DOC)
        bad['comparison']['applicability_to_Y20175_1963'] = 'CONFIRMED'
        self.assertTrue(any('1963 applicability' in e for e in validate(bad)))

    def test_two_complete_replays_must_match(self):
        bad = deepcopy(DOC)
        bad['snapshots'][2]['replay']['sha256'] = 'f' * 64
        self.assertTrue(any('complete replay' in e for e in validate(bad)))

    def test_header_without_eof_is_not_complete(self):
        bad = deepcopy(DOC)
        bad['snapshots'][0]['replay']['pdf_eof'] = True
        self.assertTrue(any('unexpected PDF EOF' in e for e in validate(bad)))

    def test_real_byte_check_fails_on_mutation(self):
        # Synthetic fixture, independent of the pinned historical checksums.
        full = b'%PDF-1.4\r\nexample trailer\n%%EOF\n'
        sha1b32 = base64.b32encode(hashlib.sha1(full).digest()).decode().rstrip('=')
        row = {'replay': {'bytes': len(full), 'sha256': hashlib.sha256(full).hexdigest(),
                          'sha1_base32': sha1b32, 'pdf_header': True, 'pdf_eof': True},
               'cdx': {'digest': sha1b32}}
        self.assertEqual(payload_errors(row, full, http_status=200, content_type='application/pdf'), [])
        altered = full.replace(b'example', b'altered')
        self.assertTrue(any('SHA-256' in e for e in
                            payload_errors(row, altered, http_status=200, content_type='application/pdf')))
        self.assertTrue(any('MIME' in e for e in
                            payload_errors(row, full, http_status=200, content_type='text/html')))

    def test_byte_prefix_relations_positive_and_negative(self):
        early = b'%PDF-1.4\npage-bytes'
        later = early + b'\nstartxref\n100\n%%EOF\n'
        self.assertEqual(relation_errors(early, later, later), [])
        self.assertTrue(any('prefix' in e for e in relation_errors(b'wrong', later, later)))
        self.assertTrue(any('differ' in e for e in relation_errors(early, later, later+b'changed')))
        self.assertTrue(any('EOF' in e for e in relation_errors(later, later, later)))


if __name__ == '__main__':
    unittest.main()
