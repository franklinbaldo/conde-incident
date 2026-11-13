"""Adversarial regressions for the already-custodied ON20 Wayback crosswalk."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import export_archive_documentary_links as archive


class ArchiveDocumentaryLinksTest(unittest.TestCase):
    def test_export_matches_reconstructed_source(self):
        data = archive.build()
        self.assertEqual((ROOT / archive.OUTPUT).read_bytes(), archive.encode(data))
        self.assertEqual(len(data['nodes']), 4)
        self.assertEqual(len(data['edges']), 3)
        archived = data['nodes'][1]
        self.assertEqual(archived['document_year'], 1964)
        self.assertEqual(archived['capture_utc'], '2022-01-19T07:53:33Z')
        self.assertEqual(archived['retrieved_bytes_sha256'], archive.EXPECTED_SHA256)
        self.assertIsNone(archived['cdx_digest_base32_sha1'])
        self.assertFalse(data['epistemic_limits']['site_may_claim_cdx_verified'])
        self.assertEqual(data['nodes'][3]['matrix_context_ref'].split(':')[-1], 'C151#1')
        self.assertIsNone(data['nodes'][3]['simulator_value'])
        self.assertFalse(data['nodes'][3]['activation'])

    def mutated(self, filename, mutation):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            for name in archive.SOURCES:
                destination = target / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, destination)
            path = target / filename
            obj = json.loads(path.read_text())
            mutation(obj)
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                archive.build(target)

    def test_rejects_another_pdf_even_on_success(self):
        # 200 + PDF MIME does not prove the requested historical document.
        self.mutated(archive.CUSTODY, lambda x: x['preservation'].update(
            replay_url='https://web.archive.org/web/20220119075333id_/http://example.org/wrong.pdf'))
        self.mutated(archive.CUSTODY, lambda x: x.update(original_href='http://example.org/wrong.pdf'))

    def test_rejects_error_page_and_replay_redirect(self):
        self.mutated(archive.CUSTODY, lambda x: x['preservation'].update(http_status=404))
        self.mutated(archive.CUSTODY, lambda x: x['preservation'].update(content_type='text/html'))
        self.mutated(archive.CUSTODY, lambda x: x['preservation'].update(
            replay_url=x['preservation']['replay_url'].replace('id_/', '/')))

    def test_rejects_digest_and_pdf_identity_swaps(self):
        self.mutated(archive.CUSTODY, lambda x: x['preservation'].update(sha256='0' * 64))
        self.mutated(archive.PAGE_AUDIT, lambda x: x.update(pdf_sha256='1' * 64))
        self.mutated(archive.PAGE_AUDIT, lambda x: x['page_streams'].pop())

    def test_rejects_era_confusion(self):
        self.mutated(archive.CUSTODY, lambda x: x.update(published_year=1963))
        self.mutated(archive.CUSTODY, lambda x: x['preservation'].update(
            capture_utc='1963-11-08T07:53:33Z'))
        self.mutated(archive.CUSTODY, lambda x: x.update(applicability_to_1963='ESTABLISHED'))

    def test_rejects_premature_physical_activation(self):
        self.mutated(archive.PENDING, lambda x: x.update(numeric_observations_generated=1))
        self.mutated(archive.PENDING, lambda x: x.update(physical_domain='RESTRICTED'))
        self.mutated(archive.CUSTODY, lambda x: x.update(physical_constraint='ACTIVATED'))
        self.mutated(archive.CUSTODY, lambda x: x.update(tape_decoded=True))

    def test_no_cdx_digest_imputed_from_sha256(self):
        x = archive.build()
        archived = x['nodes'][1]
        self.assertEqual(archived['cdx_digest_verification'], 'NOT_RECORDED')
        self.assertEqual(len(archived['retrieved_bytes_sha256']), 64)
        self.assertIsNone(archived['cdx_digest_base32_sha1'])
        self.assertNotEqual(archived['capture_utc'][:4], str(archived['document_year']))


if __name__ == '__main__':
    unittest.main()
