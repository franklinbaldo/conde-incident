#!/usr/bin/env python3
"""Reject >20,000-byte files; frozen pre-existing blobs are temporary exceptions.

A listed legacy blob may remain untouched. It cannot grow or change in place.
Split/migrate legacy assets in dedicated PRs, then remove each exception.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 20_000
MANIFEST = ROOT / "config/legacy-oversized-files.json"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def check():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["limit_bytes"] != LIMIT:
        raise ValueError("inconsistent size limit")
    legacy = {entry["path"]: entry["git_blob_sha"] for entry in data["exceptions"]}
    problems = []
    entries = git("ls-files", "-z").split(b"\0")
    for raw in entries:
        if not raw:
            continue
        name = raw.decode("utf-8")
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            continue
        size = path.stat().st_size
        if size <= LIMIT:
            continue
        expected = legacy.get(name)
        actual = git("hash-object", "--", name).decode().strip()
        if not expected or expected != actual:
            problems.append(f"{name}: {size} bytes > {LIMIT}; not an unchanged legacy blob")
    if problems:
        print("FILES_OVER_20KB:\n" + "\n".join(problems), file=sys.stderr)
    return bool(problems)


if __name__ == "__main__":
    sys.exit(check())
