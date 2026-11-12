"""Offline unit tests: UWM original JP2 prefix does not establish full-file fixity."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/archives/probe_uwm_jp2.py"
SPEC = importlib.util.spec_from_file_location("probe_uwm_jp2", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class FakeResponse:
    def __init__(self, status=200, content_range=None, data=None):
        self.status = status
        self.headers = {"Content-Type": "image/jp2", "Content-Range": content_range}
        self.data = data if data is not None else bytes.fromhex(
            "0000000c6a5020200d0a870a00000014667479706a703220000000006a703220"
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, count):
        return self.data[:count]


class TestJP2OriginalProbe(unittest.TestCase):
    def test_200_without_content_range_does_not_verify_range_support(self):
        with patch.object(PROBE.urllib.request, "urlopen", return_value=FakeResponse()):
            result = PROBE.probe(PROBE.DEFAULT_URL)
        self.assertEqual(result["bytes_of_body_read"], 32)
        self.assertFalse(result["range_support_observed"])
        self.assertTrue(result["partial_response_only"])
        self.assertIsNone(result["full_body_sha256"])

    def test_real_partial_range_would_be_recorded_if_server_sent_it(self):
        with patch.object(PROBE.urllib.request, "urlopen",
                          return_value=FakeResponse(206, "bytes 0-31/12345")):
            result = PROBE.probe(PROBE.DEFAULT_URL)
        self.assertTrue(result["range_support_observed"])
        self.assertEqual(result["content_range"], "bytes 0-31/12345")

    def test_wrong_header_rejected(self):
        with patch.object(PROBE.urllib.request, "urlopen",
                          return_value=FakeResponse(data=b"garbage" * 6)):
            with self.assertRaisesRegex(ValueError, "JP2 signature"):
                PROBE.probe(PROBE.DEFAULT_URL)

    def test_refuses_non_custodian_url_without_network(self):
        with self.assertRaisesRegex(ValueError, "custodial"):
            PROBE.probe("https://example.invalid/original.jp2")

    def test_invalid_prefix_size_rejected(self):
        with self.assertRaisesRegex(ValueError, "prefix_bytes"):
            PROBE.probe(PROBE.DEFAULT_URL, prefix_bytes=8)


if __name__ == "__main__":
    unittest.main()
