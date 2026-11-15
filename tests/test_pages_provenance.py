"""Negative, positive and optimized-interpreter checks for Pages byte custody."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import pages_provenance as p

COMMIT = "a" * 40
RUN_ID = "12345678"


class PagesProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "public"
        for path in p.SAMPLES:
            file = self.root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(("original " + path).encode("utf-8"))
        self.sha = p.create(self.root, COMMIT, RUN_ID)

    def remote(self):
        return {
            rel: (self.root / rel).read_bytes()
            for rel in (*p.inventory(self.root), p.MANIFEST)
        }

    def test_local_good_and_complete_inventory(self):
        self.assertEqual(p.verify_local(self.root, self.sha, COMMIT), 4)
        manifest = json.loads((self.root / p.MANIFEST).read_bytes())
        self.assertEqual(manifest["run_id"], RUN_ID)
        self.assertEqual(set(manifest["files"]), set(p.SAMPLES))

    def test_live_good_bytes_and_manifest(self):
        remote = self.remote()
        self.assertEqual(p.verify_deployed(remote.__getitem__, self.sha, COMMIT), 4)

    def test_manifest_sha_must_match_build_job(self):
        remote = self.remote()
        with self.assertRaisesRegex(ValueError, "manifest SHA mismatch"):
            p.verify_deployed(remote.__getitem__, "b" * 64, COMMIT)

    def test_commit_is_not_optional(self):
        remote = self.remote()
        with self.assertRaisesRegex(ValueError, "deployment commit mismatch"):
            p.verify_deployed(remote.__getitem__, self.sha, "b" * 40)

    def test_remote_byte_mutation_rejected_even_if_manifest_stays_valid(self):
        remote = self.remote()
        remote["index.html"] += b"\n<!-- mutated -->"
        with self.assertRaisesRegex(ValueError, "served file differs"):
            p.verify_deployed(remote.__getitem__, self.sha, COMMIT)

    def test_remote_deep_page_mutation_rejected(self):
        remote = self.remote()
        remote["evidencias/arquivo/pos-matriz/index.html"] = b""
        with self.assertRaisesRegex(ValueError, "served file differs"):
            p.verify_deployed(remote.__getitem__, self.sha, COMMIT)

    def test_mutated_runtime_javascript_not_in_four_original_samples_fails(self):
        rel = "lab/assets/entry-g79.js"
        file = self.root / rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b"export const answer = 42;")
        sha = p.create(self.root, COMMIT, RUN_ID)
        remote = self.remote()
        remote[rel] = b"export const answer = 43;"
        with self.assertRaisesRegex(ValueError, "served file differs"):
            p.verify_deployed(remote.__getitem__, sha, COMMIT)

    def test_mutated_documentary_json_not_in_four_original_samples_fails(self):
        rel = "data/documentary-g79.json"
        file = self.root / rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(b'{"source":"verified"}')
        sha = p.create(self.root, COMMIT, RUN_ID)
        remote = self.remote()
        remote[rel] = b'{"source":"falsified"}'
        with self.assertRaisesRegex(ValueError, "served file differs"):
            p.verify_deployed(remote.__getitem__, sha, COMMIT)

    def test_stratified_live_probe_is_deterministic_and_bounded(self):
        for extension in ("html", "json", "xml", "txt"):
            for i in range(30):
                rel = f"extra/{extension}/file-{i:02}.{extension}"
                file = self.root / rel
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(rel.encode())
        code = self.root / "lab/assets/essential.js"
        code.parent.mkdir(parents=True, exist_ok=True)
        code.write_bytes(b"essential JS")
        sha = p.create(self.root, COMMIT, RUN_ID)
        paths = p.live_paths(p.inventory(self.root), sha)
        self.assertEqual(paths, p.live_paths(p.inventory(self.root), sha))
        self.assertEqual(len(paths), p.MAX_LIVE_FILES)
        self.assertTrue(set(p.SAMPLES).issubset(paths))
        self.assertIn("lab/assets/essential.js", paths)
        self.assertTrue(any(x.endswith(".html") and x not in p.SAMPLES for x in paths))
        self.assertTrue(any(x.endswith(".json") for x in paths))
        self.assertTrue(any(x.endswith(".xml") for x in paths))
        self.assertTrue(any(x.endswith(".txt") for x in paths))
        remote = self.remote()
        self.assertEqual(p.verify_deployed(remote.__getitem__, sha, COMMIT), p.MAX_LIVE_FILES)

    def test_excess_runtime_assets_fail_closed_instead_of_silent_skip(self):
        for i in range(p.MAX_LIVE_FILES + 1):
            file = self.root / "lab" / "assets" / f"large-{i:03}.js"
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b"x")
        sha = p.create(self.root, COMMIT, RUN_ID)
        with self.assertRaisesRegex(ValueError, "runtime assets exceed"):
            p.verify_deployed(self.remote().__getitem__, sha, COMMIT)

    def test_local_source_mutation_rejected(self):
        (self.root / "css/site.css").write_text("new css", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local Pages payload differs"):
            p.verify_local(self.root, self.sha, COMMIT)

    def test_new_unmanifested_file_rejected(self):
        (self.root / "extra.txt").write_text("untracked artifact", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local Pages payload differs"):
            p.verify_local(self.root, self.sha, COMMIT)

    def test_missing_sample_fails_closed(self):
        (self.root / "lab/index.html").unlink()
        with self.assertRaisesRegex(ValueError, "required Pages verification sample absent"):
            p.create(self.root, COMMIT, RUN_ID)

    def test_invalid_manifest_path_fails_even_with_correct_hash(self):
        manifest = json.loads((self.root / p.MANIFEST).read_text())
        manifest["files"]["../escape"] = {"bytes": 0, "sha256": "0" * 64}
        data = p.serialized(manifest)
        with self.assertRaisesRegex(ValueError, "unsafe manifest path"):
            p.parse_manifest(data, p.digest(data), COMMIT)

    def test_invalid_manifest_metadata_rejected(self):
        manifest = json.loads((self.root / p.MANIFEST).read_text())
        manifest["files"]["index.html"]["bytes"] = True
        data = p.serialized(manifest)
        with self.assertRaisesRegex(ValueError, "invalid file length"):
            p.parse_manifest(data, p.digest(data), COMMIT)

    def test_unexpected_manifest_field_rejected(self):
        manifest = json.loads((self.root / p.MANIFEST).read_text())
        manifest["claim_identity_proven"] = True
        data = p.serialized(manifest)
        with self.assertRaisesRegex(ValueError, "unexpected manifest schema"):
            p.parse_manifest(data, p.digest(data), COMMIT)

    def test_symlinks_are_rejected(self):
        target = self.root / "index.html"
        (self.root / "other.html").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            p.create(self.root, COMMIT, RUN_ID)

    def test_no_network_bypass_on_missing_file(self):
        remote = self.remote()
        remote.pop("css/site.css")
        with self.assertRaises(KeyError):
            p.verify_deployed(remote.__getitem__, self.sha, COMMIT)

    def test_noncanonical_commit_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid commit SHA"):
            p.create(self.root, "HEAD", RUN_ID)


if __name__ == "__main__":
    unittest.main()
