import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("nmc_y20175", ROOT / "tools" / "verify_nmc_y20175.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestCustody(unittest.TestCase):
    def test_manifest_and_uncertainty(self):
        data = json.loads(module.MANIFEST.read_text())
        module.validate_manifest(data)
        self.assertEqual(data["binary"]["sha256"], "afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4")
        self.assertEqual(data["station_day_audit"]["wmo_codes_target"], ["83229", "83096", "82900"])
        self.assertIsNone(data["station_day_audit"]["matches"])

    def test_matching_and_tampered_file(self):
        raw = b"fixture-only-NCAR"
        fields = {"byte_count": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                  "first_64_bytes_hex": raw.hex(), "last_64_bytes_hex": raw.hex()}
        with tempfile.TemporaryDirectory() as tmp:
            name = Path(tmp) / "sample"
            name.write_bytes(raw)
            self.assertEqual(module.inspect_file(name, fields)["result"], "VERIFIED_BINARY")
            name.write_bytes(raw + b"!")
            self.assertEqual(module.inspect_file(name, fields)["result"], "MISMATCH")

if __name__ == "__main__":
    unittest.main()
