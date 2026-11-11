#!/usr/bin/env python3
"""Read-only custodian of the *unavailable here* original Lean archive.

Only reports a verified historical corpus when an actual ZIP, two expected
digests from its chain of custody, and the source registry are supplied.
No historical proposition text is synthesized, normalized or rewritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from zipfile import BadZipFile, ZipFile

REQUIRED = {"Evidence.lean", "evidence_registry.json"}
EXPECTED_DUPLICATED = {"C44", "C45", "C46"}


class AuditError(ValueError):
    pass


def normalize_label(raw: object) -> str:
    if not isinstance(raw, str):
        raise AuditError(f"label must be a string, got {type(raw).__name__}")
    match = re.fullmatch(r"C0*([1-9][0-9]*)", raw)
    if match is None:
        raise AuditError(f"invalid evidence label: {raw!r}")
    return f"C{int(match.group(1))}"


def audit_archive(
    path: Path, *, expected_sha1: str, expected_sha256: str, label_key: str = "id"
) -> dict:
    if not re.fullmatch(r"[a-fA-F0-9]{40}", expected_sha1):
        raise AuditError("an externally recorded 40-hex SHA-1 is required")
    if not re.fullmatch(r"[a-fA-F0-9]{64}", expected_sha256):
        raise AuditError("an externally recorded 64-hex SHA-256 is required")
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha1.update(block)
            sha256.update(block)
    if sha1.hexdigest() != expected_sha1.lower():
        raise AuditError("ZIP SHA-1 mismatch (no source material examined)")
    if sha256.hexdigest() != expected_sha256.lower():
        raise AuditError("ZIP SHA-256 mismatch (no source material examined)")

    try:
        with ZipFile(path) as zf:
            members = [zi for zi in zf.infolist() if not zi.is_dir()]
            paths = [zi.filename for zi in members]
            if len(paths) != len(set(paths)):
                raise AuditError("duplicate ZIP member path; refusing ambiguous corpus")
            for member in members:
                p = PurePosixPath(member.filename)
                if p.is_absolute() or ".." in p.parts or "\\" in member.filename:
                    raise AuditError("unsafe ZIP member path")
                if member.file_size > 64 * 1024 * 1024:
                    raise AuditError("individual ZIP member is unexpectedly large")
            located = {}
            for basename in REQUIRED:
                matches = [p for p in paths if PurePosixPath(p).name == basename]
                if len(matches) != 1:
                    raise AuditError(f"{basename}: expected exactly one member, found {len(matches)}")
                located[basename] = matches[0]
            # read() verifies CRC; there is no extraction or file writing.
            for member in members:
                zf.read(member.filename)
            registry = json.loads(zf.read(located["evidence_registry.json"]))
    except (BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise AuditError(f"invalid ZIP/registry: {e}") from e

    if isinstance(registry, dict):
        registry = registry.get("propositions")
    if not isinstance(registry, list):
        raise AuditError("registry must be a list or an object with a propositions list")
    if any(not isinstance(entry, dict) or label_key not in entry for entry in registry):
        raise AuditError(f"each registry entry must contain the explicit key {label_key!r}")
    labels = [normalize_label(entry[label_key]) for entry in registry]
    counts = Counter(labels)
    duplicated = {label for label, count in counts.items() if count > 1}
    if len(registry) != 154 or len(counts) != 151 or duplicated != EXPECTED_DUPLICATED:
        raise AuditError(
            "registry counts/collisions mismatch: "
            f"{len(registry)} entries, {len(counts)} distinct, repeated={sorted(duplicated)}; "
            "expected 154/151 and C44/C45/C46"
        )
    if any(counts[c] != 2 for c in EXPECTED_DUPLICATED):
        raise AuditError("each C44/C45/C46 collision must occur exactly twice")

    return {
        "status": "STRUCTURE_PASS_ONLY",
        "provenance_status": "NOT_VERIFIED: matching caller-supplied digests cannot prove independent custody",
        "semantic_status": "NOT_RUN: registry entries and Lean propositions are not compared",
        "zip_sha1": sha1.hexdigest(),
        "zip_sha256": sha256.hexdigest(),
        "evidence_member": located["Evidence.lean"],
        "registry_member": located["evidence_registry.json"],
        "generator_candidates": sorted(p for p in paths if p.endswith(".py")),
        "propositions": len(registry),
        "distinct_labels": len(counts),
        "duplicate_labels": sorted(duplicated),
        "warning": "Synthetic ZIPs can satisfy every structural check. Digests require independently documented custody; NOT a Lean recompilation or historical verification.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=Path, help="original bytes, not a recreated ZIP")
    ap.add_argument("--sha1", required=True, help="independently recorded original SHA-1")
    ap.add_argument("--sha256", required=True, help="independently recorded original SHA-256")
    ap.add_argument("--label-key", default="id")
    args = ap.parse_args()
    try:
        result = audit_archive(
            args.archive, expected_sha1=args.sha1, expected_sha256=args.sha256,
            label_key=args.label_key,
        )
    except (AuditError, OSError) as e:
        print(json.dumps({"status": "FAIL", "error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
