#!/usr/bin/env python3
"""Bind a GitHub Pages build to its deployed manifest and bounded HTTPS probes.

All runtime JS/CSS plus a reproducible, stratified cross-section of documentary
pages/assets are checked (max 64 files). The remainder are INVENTORIED but not
read via HTTPS. This is not a signed attestation or complete CDN audit.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import time
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

SCHEMA = "conde.pages-build-provenance/v1"
MANIFEST = "data/conde-deployment-provenance.json"
SAMPLES = (
    "index.html",
    "lab/index.html",
    "css/site.css",
    "evidencias/arquivo/pos-matriz/index.html",
)
MAX_LIVE_FILES = 64
RUNTIME_SUFFIXES = (".js", ".mjs", ".css")
HEX = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def path_ok(name: str) -> bool:
    p = PurePosixPath(name)
    return (
        isinstance(name, str) and bool(name) and
        not name.startswith("/") and "\\" not in name and
        all(x not in ("", ".", "..") for x in name.split("/")) and
        not p.is_absolute()
    )


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serialized(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def inventory(root: Path) -> dict:
    require(root.is_dir(), "Pages output directory is absent")
    result = {}
    for file in sorted(root.rglob("*")):
        require(not file.is_symlink(), "symlink in Pages output")
        if not file.is_file():
            continue
        name = file.relative_to(root).as_posix()
        require(path_ok(name), "unsafe Pages output path")
        if name == MANIFEST:
            continue
        raw = file.read_bytes()
        result[name] = {"sha256": digest(raw), "bytes": len(raw)}
    require(all(name in result for name in SAMPLES),
            "required Pages verification sample absent")
    return result


def create(root: Path, commit: str, run_id: str) -> str:
    require(bool(COMMIT.fullmatch(commit)), "invalid commit SHA")
    require(run_id.isdecimal() and int(run_id) > 0, "invalid run id")
    payload = {"schema": SCHEMA, "commit_sha": commit, "run_id": run_id,
               "files": inventory(root)}
    output = root / MANIFEST
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = serialized(payload)
    output.write_bytes(raw)
    return digest(raw)


def parse_manifest(raw: bytes, expected_sha: str, commit: str) -> dict:
    require(bool(HEX.fullmatch(expected_sha)), "invalid expected manifest SHA")
    require(digest(raw) == expected_sha, "manifest SHA mismatch")
    payload = json.loads(raw)
    require(isinstance(payload, dict) and
            set(payload) == {"schema", "commit_sha", "run_id", "files"},
            "unexpected manifest schema")
    require(payload["schema"] == SCHEMA, "wrong manifest schema")
    require(payload["commit_sha"] == commit and
            bool(COMMIT.fullmatch(payload["commit_sha"])),
            "deployment commit mismatch")
    require(isinstance(payload["run_id"], str) and
            payload["run_id"].isdecimal() and int(payload["run_id"]) > 0,
            "invalid manifest run id")
    files = payload["files"]
    require(isinstance(files, dict) and files, "empty Pages manifest")
    for path, meta in files.items():
        require(path_ok(path) and path != MANIFEST, "unsafe manifest path")
        require(isinstance(meta, dict) and set(meta) == {"sha256", "bytes"},
                "invalid file entry")
        require(isinstance(meta["sha256"], str) and
                bool(HEX.fullmatch(meta["sha256"])), "invalid file SHA")
        require(type(meta["bytes"]) is int and meta["bytes"] >= 0,
                "invalid file length")
    require(all(s in files for s in SAMPLES), "required sample not indexed")
    return files


def compare_bytes(raw: bytes, meta: dict, name: str) -> None:
    require(len(raw) == meta["bytes"] and digest(raw) == meta["sha256"],
            "served file differs from built artifact: " + name)


def verify_local(root: Path, expected_sha: str, commit: str) -> int:
    files = parse_manifest((root / MANIFEST).read_bytes(), expected_sha, commit)
    current = inventory(root)
    require(current == files, "local Pages payload differs from manifest")
    return len(files)


def live_paths(files: dict, manifest_sha: str) -> tuple[str, ...]:
    """Select mandatory runtime code and a SHA-seeded mix of other file types.

    This is a sampling policy, NOT verification of all CDN bytes. Sampling
    stays deterministic for the exact build; runtime assets are never skipped.
    Exceeding the budget fails closed so the policy must be consciously revised.
    """
    require(bool(HEX.fullmatch(manifest_sha)), "invalid sampling seed")
    required = set(SAMPLES) | {
        name for name in files if name.endswith(RUNTIME_SUFFIXES)
    }
    require(required.issubset(files), "missing mandatory Pages file")
    require(len(required) <= MAX_LIVE_FILES,
            "runtime assets exceed Pages HTTPS verification budget")
    buckets = {"html": [], "json": [], "xml": [], "other": []}
    for name in files:
        if name in required:
            continue
        extension = name.rsplit(".", 1)[-1] if "." in name else ""
        bucket = extension if extension in ("html", "json", "xml") else "other"
        buckets[bucket].append(name)
    for entries in buckets.values():
        entries.sort(key=lambda name: (
            digest((manifest_sha + ":" + name).encode("utf-8")), name))
    selected = set(required)
    target = min(MAX_LIVE_FILES, len(files))
    while len(selected) < target:
        progress = False
        for entries in buckets.values():
            if entries and len(selected) < target:
                selected.add(entries.pop())
                progress = True
        if not progress:
            break
    require(len(selected) == target, "incomplete Pages verification selection")
    return tuple(sorted(selected))


def verify_deployed(fetcher, expected_sha: str, commit: str) -> int:
    files = parse_manifest(fetcher(MANIFEST), expected_sha, commit)
    paths = live_paths(files, expected_sha)

    def verify_one(path: str) -> None:
        compare_bytes(fetcher(path), files[path], path)

    # Restrict concurrency and request count for predictable public CDN load.
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(verify_one, paths))
    return len(paths)


def fetch_live(base_url: str, rel: str) -> bytes:
    require(path_ok(rel), "unsafe download path")
    url = base_url + "/".join(quote(part) for part in rel.split("/"))
    request = Request(url, headers={"Accept-Encoding": "identity",
                                   "User-Agent": "conde-pages-audit/1"})
    with urlopen(request, timeout=20) as response:
        require(response.status == 200, "Pages HTTP status not 200")
        return response.read()


def verify_live(url: str, expected_sha: str, commit: str) -> int:
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and bool(parsed.hostname) and
            not parsed.query and not parsed.fragment and url.endswith("/"),
            "invalid Pages deployment URL")
    last_error = None
    for attempt in range(1, 7):
        try:
            count = verify_deployed(
                lambda rel: fetch_live(url, rel), expected_sha, commit)
            return count
        except (ValueError, OSError) as error:
            last_error = error
            print(f"Pages probe {attempt}/6: {error}", file=sys.stderr)
            if attempt < 6:
                time.sleep(5)
    raise ValueError(f"Pages did not serve this build: {last_error}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("build", "verify-local", "verify-live"))
    ap.add_argument("--root", type=Path, default=Path("public"))
    ap.add_argument("--commit", required=True)
    ap.add_argument("--run-id", default="")
    ap.add_argument("--sha256", default="")
    ap.add_argument("--url", default="")
    args = ap.parse_args()
    if args.mode == "build":
        print(create(args.root, args.commit, args.run_id))
    elif args.mode == "verify-local":
        print("LOCAL_PAGES_BYTES_VERIFIED", verify_local(
            args.root, args.sha256, args.commit))
    else:
        print("LIVE_PAGES_BYTES_VERIFIED", verify_live(
            args.url, args.sha256, args.commit))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Pages provenance: FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
