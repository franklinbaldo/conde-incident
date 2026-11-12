#!/usr/bin/env python3
"""Audit frozen matrix citations; this does not authenticate historical sources."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

MATRIX_PATH = "research/evidence_matrix_C001-C238_2026-11-11.md"
MATRIX_COMMIT = "38ee0f01134f6a1ee07c9346945d058d2ad3ce0b"
MATRIX_BLOB_SHA1 = "a7978c3a75a153b16ab70118a92c434bba674cb7"
PINS = {
    "C01": (19,),
    "C131": (502,),
    "C197": (905,),
    "C44": (164, 175),
    "C45": (165, 176),
    "C46": (166, 177),
}
ROW = re.compile(r"^\|\s*(?:\*\*)?(C[0-9]+)(?:\*\*)?\s*\|")


class MatrixAuditError(ValueError):
    pass


def git_blob_sha1(data: bytes) -> str:
    """Check Git blob bytes, rather than raw-file SHA-1."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def audit_rows(data: bytes, *, pins: dict[str, tuple[int, ...]] = PINS,
               expected_blob: str = MATRIX_BLOB_SHA1) -> dict:
    actual_blob = git_blob_sha1(data)
    if actual_blob != expected_blob:
        raise MatrixAuditError(
            f"matrix Git blob mismatch: expected {expected_blob}, got {actual_blob}; "
            "new source revision requires human review, not automatic pin updates"
        )
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise MatrixAuditError("matrix is not UTF-8") from exc
    found: dict[str, list[int]] = {id_: [] for id_ in pins}
    for line_no, line in enumerate(lines, 1):
        match = ROW.match(line)
        if match and match[1] in found:
            found[match[1]].append(line_no)
    for id_, expected in pins.items():
        if found[id_] != list(expected):
            raise MatrixAuditError(
                f"{id_} rows {found[id_]!r} != pinned {list(expected)!r}; "
                "do not merge distinct occurrences or cite an adjacent row"
            )
    return {
        "status": "PINNED_MATRIX_ROWS_PASS_ONLY",
        "historical_source_status": "NOT_VERIFIED: matrix snapshot is not primary-source authentication",
        "original_lean_registry": "NOT_RUN: original 154 propositions / 151 labels ZIP absent",
        "matrix_git_blob_sha1": actual_blob,
        "matrix_commit": MATRIX_COMMIT,
        "references": [
            {"id": id_, "line": line_no,
             "url": ("https://github.com/franklinbaldo/conde-incident/blob/"
                     f"{MATRIX_COMMIT}/{MATRIX_PATH}#L{line_no}")}
            for id_, lines_ in pins.items() for line_no in lines_
        ],
        "ambiguous_ids": sorted(id_ for id_, rows in pins.items() if len(rows) > 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("matrix", type=Path)
    args = ap.parse_args()
    try:
        result = audit_rows(args.matrix.read_bytes())
    except (MatrixAuditError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
