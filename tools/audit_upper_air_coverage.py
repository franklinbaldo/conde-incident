#!/usr/bin/env python3
"""Check archived NCAR GDEX file listings and station-file coverage.

The records are *archive coverage*, never observed winds at Conde.
No network access is needed to verify the pinned API replies; optional
--data-dir independently streams the full downloaded UADB station files.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "research/meteorology/gdex_1963_api_snapshot_2026-11-12.json"
MANIFEST = ROOT / "research/meteorology/gdex_uadb_1963_coverage_2026-11-12.json"


def read_snapshots(snapshot: dict) -> dict[str, dict]:
    """Validate exact server-response bytes and fail on forged/truncated records."""
    if snapshot.get("schema") != "conde.gdex-http-response-custody/v1":
        raise ValueError("bad snapshot schema")
    out: dict[str, dict] = {}
    for item in snapshot["responses"]:
        url = item["url"]
        if url in out or not url.startswith("https://gdex.ucar.edu/api/datasets/"):
            raise ValueError("duplicate/invalid GDEX URL")
        raw = base64.b64decode(item["body_b64"], validate=True)
        if hashlib.sha256(raw).hexdigest() != item["sha256"] or item["http_status"] != 200:
            raise ValueError("response hash/status mismatch")
        doc = json.loads(raw)
        if doc.get("status") != "ok" or doc.get("http_response") != 200:
            raise ValueError("GDEX API reported non-success")
        out[url] = doc["data"]
    return out


def station_rows(data: dict) -> list[list[dict]]:
    """GDEX filelist rows are lists of labeled cells, not flat dictionaries."""
    return [row for group in data["groups"] for row in group["rows"]]


def file_values(rows: list[list[dict]]) -> list[dict]:
    files = []
    for row in rows:
        record = {cell["name"]: cell.get("value") for cell in row if cell.get("name")}
        source = [cell for cell in row if cell.get("is_file")]
        if source:
            if len(source) != 1 or not source[0].get("url"):
                raise ValueError("no unique download URL")
            record["url"] = source[0]["url"]
            files.append(record)
    return files


def parse_uadb_header(line: str, station_id: str) -> dt.date | None:
    """Read date fields only: the archived time token may be non-clock (e.g. 1165)."""
    if not line.startswith("H "):
        return None
    cells = line.split()
    if len(cells) < 12 or cells[0] != "H" or cells[2] != station_id:
        raise ValueError("malformed/mismatched station header")
    return dt.date(int(cells[7]), int(cells[8]), int(cells[9]))


def summarize_station_file(path: Path, station_id: str) -> dict:
    digest = hashlib.sha256()
    first = last = None
    samples = count_1963 = window_1963 = 0
    byte_count = 0
    with path.open("rb") as handle:
        for raw in handle:
            digest.update(raw)
            byte_count += len(raw)
            if not raw.startswith(b"H "):
                continue
            observed_day = parse_uadb_header(raw.decode("ascii"), station_id)
            if observed_day is None:
                raise ValueError("unparsed station header")
            samples += 1
            first = min(first, observed_day) if first else observed_day
            last = max(last, observed_day) if last else observed_day
            if observed_day.year == 1963:
                count_1963 += 1
                if dt.date(1963, 11, 7) <= observed_day <= dt.date(1963, 11, 9):
                    window_1963 += 1
    if not samples:
        raise ValueError("no UADB H records")
    return {
        "sha256": digest.hexdigest(), "bytes": byte_count, "header_count": samples,
        "first_day": first.isoformat(), "last_day": last.isoformat(),
        "headers_1963": count_1963, "headers_1963_11_07_to_09": window_1963,
    }


def validate(snapshot: dict, manifest: dict, data_dir: Path | None = None) -> dict:
    pages = read_snapshots(snapshot)
    prefix = "https://gdex.ucar.edu/api/datasets/"
    g = pages[prefix + "d394001/groups/"]
    if len(g) != 1 or g[0]["gindex"] != 101 or g[0]["grpid"] != "DSSRAOB":
        raise ValueError("FAB group inventory changed")
    if g[0]["webcnt"] != 0 or g[0]["dwebcnt"] != 0:
        raise ValueError("FAB web-count control changed")
    if pages[prefix + "d394001/groups/101/"] != {}:
        raise ValueError("unexpected nested FAB groups")
    fab_list = pages[prefix + "d394001/filelist/101/"]
    if (fab_list["dsid"] != "d394001" or len(fab_list["groups"]) != 1 or
        fab_list["groups"][0]["total_file_count"] != 0 or
        station_rows(fab_list) or fab_list["groups"][0]["gindex"] != "101"):
        raise ValueError("FAB publicly listed files changed")
    if manifest.get("schema") != "conde.gdex-uadb-1963-archive-coverage/v1":
        raise ValueError("bad coverage schema")
    if (manifest["fab_public_filelist_status"] != "ZERO_FILES_IN_CHECKED_GDEX_WEB_API" or
        manifest["physical_constraint_status"] != "NOT_ACTIVATED" or
        manifest["station_day_1963_from_fab"] is not None or
        manifest["conde_winds_1963"] is not None):
        raise ValueError("archive gap improperly promoted to physical evidence")
    occurrences = manifest.get("new_evidence_occurrences", [])
    dependencies = manifest.get("pending_dependencies", [])
    expected = {"MET-GDEX-20261112-05", "MET-UADB-20261112-06",
                "MET-UADB-20261112-07", "MET-UADB-20261112-08",
                "MET-NMC-20261112-09"}
    if (len(occurrences) != 5 or {o["id"] for o in occurrences} != expected or
        len(dependencies) != 5 or {d["from"] for d in dependencies} != expected):
        raise ValueError("missing, orphan or duplicated archive dependencies")
    if any(o["instrument_measurement"] is not False for o in occurrences):
        raise ValueError("archive metadata cannot become weather measurement")
    if any(d["physical_constraint"] != "NOT_ACTIVATED" for d in dependencies):
        raise ValueError("unjustified weather-domain activation")
    station_data = manifest["uadb_wind_station_files"]
    if set(station_data) != {"82900", "83096", "83229"}:
        raise ValueError("missing or duplicate target station")
    for station, item in station_data.items():
        u = prefix + "d370001/filelist/3/?filter_wfile=" + station
        files = file_values(station_rows(pages[u]))
        if len(files) != 1 or files[0]["File Name"] != "uadb_wind_" + station + ".txt":
            raise ValueError("unexpected UADB filelist rows")
        if (files[0]["url"] != item["url"] or files[0]["Size"] != item["bytes"] or
            item["headers_1963"] != 0 or item["headers_1963_11_07_to_09"] != 0 or
            int(item["first_day"][:4]) <= 1963 or
            item["file_sha256"] is None or
            item["data_kind"] != "CONSOLIDATED_UADB_ARCHIVE_NOT_ORIGINAL_LAUNCH"):
            raise ValueError("station metadata or archival limitation mismatch")
        if data_dir is not None:
            computed = summarize_station_file(data_dir / files[0]["File Name"], station)
            for key, value in computed.items():
                expected_key = "file_sha256" if key == "sha256" else key
                if item[expected_key] != value:
                    raise ValueError("UADB raw record differs from captured inventory: " + station + " " + key)
    candidate = file_values(station_rows(pages[prefix + "d353000/filelist/2/?filter_wfile=Y20175"]))
    if (len(candidate) != 1 or candidate[0]["File Name"] != "Y20175" or
        candidate[0]["Size"] != 117264384 or
        manifest["alternative_1963_annual_file"]["url"] != candidate[0]["url"] or
        manifest["alternative_1963_annual_file"]["station_day_verified"] is not None):
        raise ValueError("1963 alternative file not properly scoped")
    return {"fab_public_files": 0, "verified_uadb_station_files": len(station_data),
            "1963_station_headers_in_checked_uadb_files": 0,
            "physical_constraint_status": "NOT_ACTIVATED",
            "checked_raw_station_files": len(station_data) if data_dir else 0,
            "alternative_file": "d353000/Y20175 (station coverage unknown)"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--data-dir", type=Path, help="Optional directory containing downloaded full UADB-Wind station files")
    args = parser.parse_args()
    result = validate(json.loads(args.snapshot.read_text()), json.loads(args.manifest.read_text()), args.data_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
