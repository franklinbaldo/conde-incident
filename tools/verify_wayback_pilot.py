#!/usr/bin/env python3
"""Validate an exact-URL Wayback pilot without inventing captures or hashes.

Default: offline structural validation. --fetch: verify archival replay bytes
against both SHA-256 and the CDX Base32 SHA-1 digest, with a size budget.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

DEFAULT_MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/wayback_pilot_2026-11-12.json"
)
SHA256_RE = re.compile(r"[a-f0-9]{64}\Z")
CDX_SHA1_RE = re.compile(r"[A-Z2-7]{32}\Z")
TIMESTAMP_RE = re.compile(r"[0-9]{14}\Z")


def sha1_base32(data: bytes) -> str:
    """CDX payload digest, not a SHA-256 digest."""
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def replay_errors(row: dict, data: bytes, *, http_status: int, content_type: str) -> list[str]:
    expected = row["replay"]
    cdx = row["cdx_record"]
    errors = []
    if http_status != 200:
        errors.append("replay status is not HTTP 200")
    if content_type.split(";", 1)[0].lower() != "application/pdf":
        errors.append("replay MIME is not application/pdf")
    if len(data) != expected["bytes"]:
        errors.append("replay byte count mismatch")
    if hashlib.sha256(data).hexdigest() != expected["sha256"]:
        errors.append("replay SHA-256 mismatch")
    digest = sha1_base32(data)
    if digest != expected["sha1_base32"] or digest != cdx["digest"]:
        errors.append("replay CDX SHA-1 Base32 mismatch")
    if not data.startswith(b"%PDF-"):
        errors.append("missing PDF magic")
    if b"%%EOF" not in data[-1024:]:
        errors.append("missing PDF EOF marker")
    return errors


def validate_manifest(manifest: dict) -> list[str]:
    errors = []
    if manifest.get("schema") != "conde.wayback-capture-pilot/v1":
        errors.append("unknown manifest schema")
    if manifest.get("rules", {}).get("historical_authentication") is not False:
        errors.append("archive replay is not historical authentication")
    records = manifest.get("records", [])
    if not isinstance(records, list) or not records:
        return errors + ["records required"]
    seen_ids: set[str] = set()
    for row in records:
        key = row.get("id", "missing-id")
        if key in seen_ids:
            errors.append(f"{key}: duplicate id")
        seen_ids.add(key)
        original = row.get("original_url", "")
        if not original.startswith("https://") or "#" in original:
            errors.append(f"{key}: invalid original HTTPS URL")
        if not row.get("source_refs") or not row.get("source_family"):
            errors.append(f"{key}: provenance or occurrence missing")
        lookup = row.get("cdx_lookup") or {}
        if lookup.get("http_status") != 200:
            errors.append(f"{key}: CDX query did not return 200")
        state = row.get("status")
        if state == "NO_EXACT_CAPTURE_IN_QUERIED_INDEX":
            if lookup.get("exact_results") != 0 or lookup.get("output") != "[]":
                errors.append(f"{key}: incomplete negative CDX query")
            available = row.get("availability_lookup") or {}
            if available.get("http_status") != 200 or available.get("archived_snapshots") != {}:
                errors.append(f"{key}: negative Availability evidence missing")
            if any(row.get(field) is not None for field in ("capture_utc", "archived_url", "cdx_record", "replay")):
                errors.append(f"{key}: fabricated capture data for a negative result")
        elif state == "VERIFIED_REPLAY":
            cdx = row.get("cdx_record") or {}
            replay = row.get("replay") or {}
            stamp = cdx.get("timestamp", "")
            if not TIMESTAMP_RE.fullmatch(stamp):
                errors.append(f"{key}: invalid CDX timestamp")
                continue
            try:
                captured = datetime.strptime(stamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            except ValueError:
                errors.append(f"{key}: impossible CDX timestamp")
                continue
            if row.get("capture_utc") != captured.strftime("%Y-%m-%dT%H:%M:%SZ"):
                errors.append(f"{key}: capture date does not match CDX timestamp")
            if cdx.get("original") != original:
                errors.append(f"{key}: CDX original differs from cited source")
            expected_url = f"https://web.archive.org/web/{stamp}id_/{original}"
            if row.get("archived_url") != expected_url:
                errors.append(f"{key}: archive URL is not exact CDX raw replay")
            if cdx.get("statuscode") != "200" or cdx.get("mimetype") != "application/pdf":
                errors.append(f"{key}: CDX entry is not a successful PDF")
            if not isinstance(cdx.get("length"), int) or cdx["length"] < 1:
                errors.append(f"{key}: invalid CDX record length")
            if not CDX_SHA1_RE.fullmatch(cdx.get("digest", "")):
                errors.append(f"{key}: invalid CDX digest")
            if replay.get("http_status") != 200 or replay.get("content_type") != "application/pdf":
                errors.append(f"{key}: replay HTTP status or MIME invalid")
            if not isinstance(replay.get("bytes"), int) or replay["bytes"] < 10:
                errors.append(f"{key}: invalid replay byte count")
            if not SHA256_RE.fullmatch(replay.get("sha256", "")):
                errors.append(f"{key}: missing SHA-256 of PDF")
            if replay.get("sha1_base32") != cdx.get("digest"):
                errors.append(f"{key}: SHA-1 digest disagrees with CDX")
            if replay.get("pdf_magic") is not True or replay.get("pdf_eof") is not True:
                errors.append(f"{key}: PDF structural verification missing")
        else:
            errors.append(f"{key}: unknown verification state {state}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--fetch", action="store_true", help="verify Wayback bytes live (network)")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print("FAIL", error)
        return 1
    print("PASS", len(manifest["records"]), "manifest rows; no network")
    if args.fetch:
        for row in manifest["records"]:
            if row["status"] != "VERIFIED_REPLAY":
                print("SKIP", row["id"], "no verified exact capture")
                continue
            request = Request(row["archived_url"], headers={"User-Agent": "Conde-archive-audit/1.0"})
            try:
                with urlopen(request, timeout=45) as response:
                    data = response.read(20_000_001)
                    if len(data) > 20_000_000:
                        raise ValueError("PDF exceeds configured replay budget")
                    found = replay_errors(
                        row, data, http_status=response.status,
                        content_type=response.headers.get("Content-Type", ""),
                    )
            except Exception as exc:
                print("FAIL", row["id"], "replay unavailable", type(exc).__name__)
                return 2
            if found:
                print("FAIL", row["id"], "; ".join(found))
                return 1
            print("PASS", row["id"], "exact replay byte and two-digest check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
