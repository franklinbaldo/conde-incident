#!/usr/bin/env python3
"""Verify the full Y20175 binary by SHA-256 without claiming to parse observations."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

MANIFEST = Path(__file__).resolve().parents[1] / "research" / "meteorology" / "nmc_y20175_1963_custody.json"

def validate_manifest(data):
    assert data["schema"] == "conde.nmc-y20175-binary-custody/v1"
    audit = data["station_day_audit"]
    assert audit["status"] == "NOT_DECODED"
    assert audit["records_parsed"] is None and audit["matches"] is None
    assert audit["negative_station_claim"] is False
    assert audit["physical_constraint_status"] == "NOT_ACTIVATED"
    assert data["binary"]["byte_count"] == 117264384
    assert len(data["binary"]["sha256"]) == 64

def inspect_file(file, expected):
    h = hashlib.sha256()
    total = 0
    head = b""
    tail = b""
    with Path(file).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            if total == 0:
                head = chunk[:64]
            total += len(chunk)
            h.update(chunk)
            tail = (tail + chunk)[-64:]
    observed = {"byte_count": total, "sha256": h.hexdigest(),
                "first_64_bytes_hex": head.hex(), "last_64_bytes_hex": tail.hex()}
    failures = [field for field in observed if observed[field] != expected[field]]
    return {"result": "VERIFIED_BINARY" if not failures else "MISMATCH",
            "failures": failures, "observed": observed,
            "station_day_status": "NOT_DECODED"}

def download_file(url, target):
    partial = Path(str(target) + ".incomplete")
    if partial.exists():
        raise FileExistsError(str(partial))
    try:
        with urlopen(Request(url, headers={"User-Agent": "Lontra-Conde-Archive-Research"}), timeout=90) as response:
            if response.status != 200:
                raise ValueError("Expected full HTTP 200")
            with partial.open("wb") as dest:
                for chunk in iter(lambda: response.read(1024*1024), b""):
                    dest.write(chunk)
        partial.replace(target)
    except Exception:
        partial.unlink(missing_ok=True)
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--file", type=Path)
    group.add_argument("--download", type=Path)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf8"))
    validate_manifest(manifest)
    if args.download:
        if args.download.exists():
            parser.error("Download target exists; use --file")
        download_file(manifest["binary"]["public_url"], args.download)
    outcome = {"manifest": "VALID", "station_day_status": "NOT_DECODED"}
    if args.file or args.download:
        outcome.update(inspect_file(args.file or args.download, manifest["binary"]))
    print(json.dumps(outcome, sort_keys=True))
    if outcome.get("result") == "MISMATCH":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
