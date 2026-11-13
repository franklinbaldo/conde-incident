#!/usr/bin/env python3
"""Enforce 20 KB with narrowly reviewed lockfiles and frozen legacy blobs.

A listed legacy blob may remain untouched. It cannot grow or change in place.
No exemption can be granted merely by editing a JSON manifest.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 20_000
MANIFEST = ROOT / "config/legacy-oversized-files.json"
EXEMPTIONS = ROOT / "config/file-size-exemptions.json"
# Adding a new mutable exception requires changing reviewed code and tests, not
# just a JSON reason. Only the actually required generated lockfile is allowed.
APPROVED_EDITABLE_LOCKFILES = frozenset({"bun.lock"})


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def editable_exemptions():
    """Allow only exact named files with explanations, never globs/directories."""
    entries = json.loads(EXEMPTIONS.read_text(encoding="utf-8"))["exceptions"]
    paths = set()
    for entry in entries:
        name = entry.get("path") if isinstance(entry, dict) else None
        reason = entry.get("reason") if isinstance(entry, dict) else None
        if (
            not isinstance(name, str) or not name
            or not isinstance(reason, str) or not reason.strip()
            or name.startswith("/") or "\\" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
            or any(ch in name for ch in "*?[]")
            or name in paths
        ):
            raise ValueError(f"invalid or duplicate size exemption: {name!r}")
        if name not in APPROVED_EDITABLE_LOCKFILES:
            raise ValueError(f"unapproved mutable lockfile exemption: {name!r}")
        paths.add(name)
    return paths


def check():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data["limit_bytes"] != LIMIT:
        raise ValueError("inconsistent size limit")
    legacy = {entry["path"]: entry["git_blob_sha"] for entry in data["exceptions"]}
    editable = editable_exemptions()
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
        if size <= LIMIT or name in editable:
            continue
        expected = legacy.get(name)
        actual = git("hash-object", "--", name).decode().strip()
        if not expected or expected != actual:
            problems.append(f"{name}: {size} bytes > {LIMIT}; not exempt or an unchanged legacy blob")
    if problems:
        print("FILES_OVER_20KB:\n" + "\n".join(problems), file=sys.stderr)
    return bool(problems)


if __name__ == "__main__":
    sys.exit(check())
