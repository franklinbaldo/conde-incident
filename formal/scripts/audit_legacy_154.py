#!/usr/bin/env python3
"""Audit restored local 154-row Lean evidence snapshot against immutable C001-C238.

This *does not* authenticate the missing historic ZIP or produce physical evidence.
By design the local 2026-11-11 file and current matrix reuse C144-C151
for different propositions; detection of that aliasing is the purpose of this audit.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

# SHA-256 of exact locally preserved Conde Evidence.lean seen 2026-11-12;
# origin package ZIP/compiler log NOT available. Do not assert source authenticity.
ARCHIVE_SHA256 = "ac2c1982f2f9bc66d31f3d39cc0247dd02e8815bfef457c5d7ff5a8d6eb6f3ee"
MATRIX_GIT_BLOB_SHA1 = "a7978c3a75a153b16ab70118a92c434bba674cb7"
ARCHIVE_ROWS = 154
ARCHIVE_DISTINCT_IDS = 151
LEGACY_ALIAS_IDS = set(range(144, 152))
MATRIX_ROW = re.compile(r"^\|\s*(?:\*\*)?C(\d+)(?:\*\*)?\s*\|")
# Each EvidenceRow record occupies one line, including escaped string fields.
STRING = r'"(?:\\.|[^"\\])*"'
ENTRY = re.compile(
    r"^\s*\{ id := (?P<id>\d+), variant := (?P<variant>\d+), "
    r"uniqueId := (?P<key>" + STRING + r"), summary := (?P<summary>" + STRING
    + r"), sourceRow := (?P<source>" + STRING + r"), grade :=",
    re.MULTILINE,
)


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parse_evidence(data: bytes) -> list[dict]:
    lines = data.decode("utf-8")
    result = []
    for m in ENTRY.finditer(lines):
        result.append({
            "id": int(m["id"]),
            "variant": int(m["variant"]),
            "key": json.loads(m["key"]),
            "summary": json.loads(m["summary"]),
            "source": json.loads(m["source"]),
        })
    return result


def parse_matrix(data: bytes) -> dict[int, list[str]]:
    rows: dict[int, list[str]] = defaultdict(list)
    for line in data.decode("utf-8").splitlines():
        match = MATRIX_ROW.match(line)
        if match:
            rows[int(match[1])].append(line)
    return rows


def audit(archive: bytes, matrix: bytes) -> dict:
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Restored Evidence.lean differs from pinned local preserved bytes")
    if git_blob_sha1(matrix) != MATRIX_GIT_BLOB_SHA1:
        raise ValueError("C001-C238 matrix snapshot differs; re-audit aliases explicitly")
    rows = parse_evidence(archive)
    counts = Counter(r["id"] for r in rows)
    if len(rows) != ARCHIVE_ROWS or len(counts) != ARCHIVE_DISTINCT_IDS:
        raise ValueError(f"Old corpus count changed: {len(rows)} entries / {len(counts)} IDs")
    if set(counts) != set(range(1, ARCHIVE_DISTINCT_IDS + 1)):
        raise ValueError("Old evidence IDs are not the exact C01-C151 interval")
    if {i: c for i, c in counts.items() if c > 1} != {44: 2, 45: 2, 46: 2}:
        raise ValueError("C44-C46 collisions altered in old corpus")
    occurrences = Counter()
    matrix_rows = parse_matrix(matrix)
    if len(matrix_rows) != 238 or sum(map(len, matrix_rows.values())) != 241:
        raise ValueError("Current matrix inventory changed: expected 241 rows, 238 IDs")
    mismatches = []
    for row in rows:
        i = row["id"]
        occurrences[i] += 1
        variant = occurrences[i]
        expected_key = f"C{i:02d}" + (f".{variant}" if counts[i] > 1 else "")
        if row["variant"] != variant or row["key"] != expected_key:
            raise ValueError(f"Identity/occurrence inconsistent at legacy {row['key']}")
        if i not in matrix_rows or variant > len(matrix_rows[i]):
            raise ValueError(f"Current matrix does not include legacy {row['key']} occurrence")
        new = matrix_rows[i][variant - 1]
        if row["source"] != new:
            mismatches.append({
                "old_key": row["key"],
                "old_claim": row["summary"],
                "current_claim": new.split("|")[2].replace("**", "").strip(),
            })
    observed_alias_ids = {int(r["old_key"][1:]) for r in mismatches}
    if observed_alias_ids != LEGACY_ALIAS_IDS or len(mismatches) != 8:
        raise ValueError(f"Unexpected legacy/current claim aliases: {mismatches!r}")
    return {
        "source_status": "LOCAL_PRESERVED_FILE; ORIGINAL_ZIP_NOT_LOCATED",
        "archived_bytes_sha256": ARCHIVE_SHA256,
        "matrix_blob_sha1": MATRIX_GIT_BLOB_SHA1,
        "legacy_rows": len(rows),
        "legacy_distinct_claim_ids": len(counts),
        "legacy_duplicate_variants": [f"C{i:02d}#{variant}"
                                      for i in (44, 45, 46) for variant in (1, 2)],
        "identical_current_occurrences": len(rows) - len(mismatches),
        "claim_aliases_requiring_snapshot_qualified_ids": mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument("--evidence", type=Path, default=root / "formal/Conde1963/Evidence.lean")
    parser.add_argument("--matrix", type=Path, default=root / "research/evidence_matrix_C001-C238_2026-11-11.md")
    args = parser.parse_args()
    print(json.dumps(audit(args.evidence.read_bytes(), args.matrix.read_bytes()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
