"""Synthetic falsification of page-tree and content-stream custody."""
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/audit_ncep_on20_page_streams.py'
spec = importlib.util.spec_from_file_location('audit_ncep_on20_page_streams', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(payload=b'abcdef', length=6):
    nodes = [
        (3, b'<< /Type /Pages /Count 1 /Kids [25 0 R] >>'),
        (25, b'<< /Type /Page /Parent 3 0 R /Resources << /XObject 27 0 R >> >>'),
        (27, b'<< /Im0 22 0 R >>'),
        (23, str(length).encode()),
        (22, b'<< /Subtype /Image /Name /Im0 /Filter /CCITTFaxDecode /DecodeParms << /K -1 >> /Width 10 /Height 20 /Length 23 0 R >>\rstream\r\n' + payload + b'\rendstream'),
    ]
    return b'%PDF-1.4\r' + b''.join(str(n).encode()+b' 0 obj\r'+v+b'\rendobj\r' for n,v in nodes)


class TestPageStreams(unittest.TestCase):
    def test_real_manifest_has_23_distinct_ccitt_hashes(self):
        path = Path(__file__).resolve().parents[1] / 'research/meteorology/ncep_on20_page_audit_20261112.json'
        obj = json.loads(path.read_text())
        self.assertEqual(len(obj['page_streams']), 23)
        self.assertEqual([p['pdf_page'] for p in obj['page_streams']], list(range(1,24)))
        self.assertEqual(len({p['ccitt_sha256'] for p in obj['page_streams']}), 23)
        self.assertEqual(obj['pdf_sha256'], '656984ac58ff1632e39b0f62ac80003785ddea0a0de32dfb19c8c612067aabbe')
        self.assertEqual(obj['revision']['date_seen_on_pdf_pages'], '1964-11-27')
        self.assertEqual(obj['applicability_to_1963'], 'NOT_ESTABLISHED')

    def test_synthetic_valid_page(self):
        rows=module.extract_pages(fixture(), expected_pages=1)
        self.assertEqual(rows[0]['ccitt_bytes'],6)

    def test_rejects_broken_page_tree(self):
        with self.assertRaises(module.AuditError):
            module.extract_pages(fixture().replace(b'/Count 1',b'/Count 2'), expected_pages=1)

    def test_rejects_wrong_stream_length(self):
        with self.assertRaises(module.AuditError):
            module.extract_pages(fixture(length=5), expected_pages=1)

    def test_rejects_wrong_image_index(self):
        with self.assertRaises(module.AuditError):
            module.extract_pages(fixture().replace(b'/Im0 22',b'/Im1 22'), expected_pages=1)

    def test_rejects_unsupported_compression(self):
        with self.assertRaises(module.AuditError):
            module.extract_pages(fixture().replace(b'/CCITTFaxDecode',b'/DCTDecode'), expected_pages=1)


if __name__ == '__main__':
    unittest.main()
