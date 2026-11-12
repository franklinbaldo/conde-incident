"""Adversarial tests of immutable oversized-blob exemptions (synthetic inputs)."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_file_size.py"
spec = importlib.util.spec_from_file_location("file_size_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class FileSizeGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "config").mkdir()
        self.manifest = self.root / "config/legacy-oversized-files.json"

    def prepare(self, frozen):
        entries = []
        for name in frozen:
            sha = subprocess.check_output(
                ["git", "hash-object", "--", name], cwd=self.root, text=True
            ).strip()
            entries.append({"path": name, "git_blob_sha": sha})
        self.manifest.write_text(json.dumps({
            "limit_bytes": 20000, "exceptions": entries
        }))
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)

    def check(self):
        with patch.object(gate, "ROOT", self.root), patch.object(
            gate, "MANIFEST", self.manifest
        ):
            return gate.check()

    def test_new_file_over_limit_is_blocked(self):
        (self.root / "oversized.txt").write_bytes(b"x" * 20001)
        self.prepare([])
        self.assertTrue(self.check())

    def test_exact_limit_allowed(self):
        (self.root / "exact.txt").write_bytes(b"x" * 20000)
        self.prepare([])
        self.assertFalse(self.check())

    def test_original_frozen_blob_allowed(self):
        (self.root / "old.txt").write_bytes(b"x" * 20001)
        self.prepare(["old.txt"])
        self.assertFalse(self.check())

    def test_changed_oversized_legacy_blob_is_blocked(self):
        p = self.root / "old.txt"
        p.write_bytes(b"x" * 20001)
        self.prepare(["old.txt"])
        p.write_bytes(b"y" * 20001)
        self.assertTrue(self.check())


if __name__ == "__main__":
    unittest.main()
