"""Offline semantic checks for Wayback exact-URL archive custody pilot."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from tools.verify_wayback_pilot import replay_errors, sha1_base32, validate_manifest

MANIFEST = json.loads((Path(__file__).resolve().parents[1] / 'research/archive/wayback_pilot_2026-11-12.json').read_text())


class WaybackPilotTest(unittest.TestCase):
    def test_pilot_has_two_verified_and_one_scoped_negative(self):
        self.assertEqual(validate_manifest(MANIFEST), [])
        self.assertEqual([r['status'] for r in MANIFEST['records']].count('VERIFIED_REPLAY'), 2)
        self.assertEqual([r['status'] for r in MANIFEST['records']].count('NO_EXACT_CAPTURE_IN_QUERIED_INDEX'), 1)
        self.assertTrue(all(r['source_refs'] for r in MANIFEST['records']))

    def test_negative_must_not_claim_archived_url(self):
        changed = deepcopy(MANIFEST)
        changed['records'][0]['archived_url'] = 'https://web.archive.org/web/20200101010101id_/https://ntrs.nasa.gov/test.pdf'
        self.assertTrue(any('fabricated capture' in e for e in validate_manifest(changed)))

    def test_negative_requires_actual_empty_cdx(self):
        changed = deepcopy(MANIFEST)
        changed['records'][0]['cdx_lookup']['output'] = 'NOT_QUERYED'
        self.assertTrue(any('incomplete negative CDX' in e for e in validate_manifest(changed)))

    def test_raw_replay_url_follows_real_timestamp(self):
        changed = deepcopy(MANIFEST)
        changed['records'][1]['archived_url'] = changed['records'][1]['archived_url'].replace('20230315024525', '20230315024526')
        self.assertTrue(any('exact CDX raw replay' in e for e in validate_manifest(changed)))

    def test_digest_is_not_sha256(self):
        self.assertEqual(sha1_base32(b'abc'), 'VGMT4NSHA2AWVOR6EVYXQUGCNSONBWE5')
        changed = deepcopy(MANIFEST)
        changed['records'][1]['replay']['sha1_base32'] = changed['records'][1]['replay']['sha256']
        self.assertTrue(any('SHA-1 digest disagrees' in e for e in validate_manifest(changed)))

    def test_historical_authentication_forbidden(self):
        changed = deepcopy(MANIFEST)
        changed['rules']['historical_authentication'] = True
        self.assertTrue(any('not historical authentication' in e for e in validate_manifest(changed)))

    def test_synthetic_exact_pdf_and_bad_bytes(self):
        payload = b'%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer <<>>\n%%EOF\n'
        row = deepcopy(MANIFEST['records'][1])
        row['replay'].update(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), sha1_base32=sha1_base32(payload))
        row['cdx_record']['digest'] = sha1_base32(payload)
        self.assertEqual(replay_errors(row, payload, http_status=200, content_type='application/pdf'), [])
        errors = replay_errors(row, payload + b'X', http_status=200, content_type='application/pdf')
        self.assertTrue(any('byte count mismatch' in e for e in errors))
        self.assertTrue(any('SHA-256 mismatch' in e for e in errors))

    def test_synthetic_replay_rejects_html_false_pdf(self):
        row = MANIFEST['records'][1]
        errors = replay_errors(row, b'<!doctype html>wayback error', http_status=200, content_type='text/html')
        self.assertTrue(any('MIME' in e for e in errors))
        self.assertTrue(any('PDF magic' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
