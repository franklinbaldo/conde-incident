"""Synthetic tests for frozen legacy and exact editable exceptions."""
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
        self.exemptions = self.root / "config/file-size-exemptions.json"

    def prepare(self, frozen=(), editable=()):
        entries = []
        for name in frozen:
            sha = subprocess.check_output(
                ["git", "hash-object", "--", name], cwd=self.root, text=True
            ).strip()
            entries.append({"path": name, "git_blob_sha": sha})
        self.manifest.write_text(json.dumps({
            "limit_bytes": 20000, "exceptions": entries
        }))
        self.exemptions.write_text(json.dumps({"exceptions": [
            {"path": name, "reason": "Generated file"} for name in editable
        ]}))
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)

    def check(self):
        with patch.object(gate, "ROOT", self.root), patch.object(
            gate, "MANIFEST", self.manifest
        ), patch.object(gate, "EXEMPTIONS", self.exemptions):
            return gate.check()

    def test_new_file_over_limit_is_blocked(self):
        (self.root / "oversized.txt").write_bytes(b"x" * 20001)
        self.prepare()
        self.assertTrue(self.check())

    def test_exact_limit_allowed(self):
        (self.root / "exact.txt").write_bytes(b"x" * 20000)
        self.prepare()
        self.assertFalse(self.check())

    def test_original_frozen_blob_allowed(self):
        (self.root / "old.txt").write_bytes(b"x" * 20001)
        self.prepare(frozen=["old.txt"])
        self.assertFalse(self.check())

    def test_changed_oversized_legacy_blob_is_blocked(self):
        p = self.root / "old.txt"
        p.write_bytes(b"x" * 20001)
        self.prepare(frozen=["old.txt"])
        p.write_bytes(b"y" * 20001)
        self.assertTrue(self.check())

    def test_mutable_lockfile_may_change_above_limit(self):
        p = self.root / "bun.lock"
        p.write_bytes(b"x" * 20001)
        self.prepare(editable=["bun.lock"])
        p.write_bytes(b"y" * 35000)
        self.assertFalse(self.check())

    def test_unlisted_lockfile_is_blocked(self):
        (self.root / "other.lock").write_bytes(b"x" * 20001)
        self.prepare(editable=["bun.lock"])
        self.assertTrue(self.check())

    def test_arbitrary_non_lockfile_exemption_is_rejected(self):
        """An edited manifest must not exempt scientific evidence or executable code."""
        (self.root / "scientific-proof.json").write_bytes(b"x" * 20001)
        self.prepare(editable=["scientific-proof.json"])
        with self.assertRaises(ValueError):
            self.check()

    def test_unapproved_lockfile_exemption_is_rejected(self):
        """New oversized lockfiles need code review, not just a JSON exception."""
        (self.root / "third-party.lock").write_bytes(b"x" * 20001)
        self.prepare(editable=["third-party.lock"])
        with self.assertRaises(ValueError):
            self.check()

    def test_wildcards_are_rejected(self):
        self.prepare()
        self.exemptions.write_text(json.dumps({"exceptions": [
            {"path": "*.lock", "reason": "Too broad"}
        ]}))
        with self.assertRaises(ValueError):
            self.check()

    def test_missing_reason_is_rejected(self):
        self.prepare()
        self.exemptions.write_text(json.dumps({"exceptions": [
            {"path": "bun.lock", "reason": ""}
        ]}))
        with self.assertRaises(ValueError):
            self.check()


if __name__ == "__main__":
    unittest.main()
