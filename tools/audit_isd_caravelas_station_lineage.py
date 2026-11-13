#!/usr/bin/env python3
"""Compare NOAA 1963 ISD row coordinates with a pinned retrospective station listing."""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

from audit_isd_caravelas_1963 import load_snapshot, SOURCE_SHA256

ROOT = Path(__file__).resolve().parents[1]
HISTORY_ROW = ROOT / "research/meteorology/isd_caravelas_history_row_20261113.csv"
REPORT = ROOT / "research/meteorology/isd_caravelas_station_lineage_1963.json"
GRAPH = ROOT / "research/constraints/isd_caravelas_position_genealogy_1963.json"
HISTORY_SHA256 = "1994747ab4af1b97e63adb434b4d0d022f2daee76f0c144ea9ab46be2d906604"
STATION_ROW_SHA256 = "b24514a2be25cf2fe2e59dce58f78f577e27878b69435b6db8098df74a4a7a7e"
STATION_KEY = ("834970", "99999")
YEAR = 1963


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_station_history(full_csv: bytes) -> bytes:
    if digest(full_csv) != HISTORY_SHA256:
        raise ValueError("NOAA history CSV full SHA-256 mismatch")
    lines = full_csv.splitlines(keepends=True)
    selected = [line for line in lines[1:] if line.startswith(b'"834970","99999",')]
    if len(selected) != 1:
        raise ValueError("NOAA history station row missing or ambiguous")
    if digest(selected[0]) != STATION_ROW_SHA256:
        raise ValueError("NOAA history station row changed")
    return lines[0] + selected[0]


def parse_station_row(raw: bytes) -> dict:
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    if len(rows) != 1:
        raise ValueError("must contain exactly one station history row")
    row = rows[0]
    if (row["USAF"], row["WBAN"]) != STATION_KEY or row["STATION NAME"] != "CARAVELAS":
        raise ValueError("station history identity not CARAVELAS 834970/99999")
    if row["BEGIN"] != "19610101" or row["END"] != "19971231":
        raise ValueError("retrospective metadata period changed")
    return {"lat_deg": float(row["LAT"]), "lon_deg": float(row["LON"]),
            "elevation_m": float(row["ELEV(M)"]), "icao": row["ICAO"],
            "archive_period": [row["BEGIN"], row["END"]]}


def parse_original_rows(raw: bytes, expected_rows: int | None = 72) -> dict:
    lines = raw.splitlines(keepends=True)
    if expected_rows is not None and len(lines) != expected_rows:
        raise ValueError("ISD row count differs from expected source")
    values = set()
    dates = set()
    for line in lines:
        if len(line) < 70 or line[4:15] != b"83497099999":
            raise ValueError("record truncated or station identity changed")
        try:
            lat = int(line[28:34]) / 1000
            lon = int(line[34:41]) / 1000
            elev = int(line[46:51])
            observation_date = line[15:23].decode("ascii")
        except (ValueError, UnicodeError) as exc:
            raise ValueError("invalid fixed-width station metadata") from exc
        if not observation_date.startswith(str(YEAR)):
            raise ValueError("record is not from 1963")
        dates.add(observation_date)
        values.add((lat, lon, elev))
    if len(values) != 1 or not values:
        raise ValueError("multiple or missing position/elevation encodings")
    lat, lon, elev = next(iter(values))
    return {"lat_deg": lat, "lon_deg": lon, "elevation_m": elev,
            "rows": len(lines), "distinct_dates": len(dates)}


def great_circle_km(p: dict, q: dict) -> float:
    lat1, lat2 = math.radians(p["lat_deg"]), math.radians(q["lat_deg"])
    delta_lon = math.radians(q["lon_deg"] - p["lon_deg"])
    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(delta_lon/2)**2
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def build_report(snapshot: bytes | None = None, row_csv: bytes | None = None) -> dict:
    snapshot = load_snapshot() if snapshot is None else snapshot
    row_csv = HISTORY_ROW.read_bytes() if row_csv is None else row_csv
    if digest(row_csv.splitlines(keepends=True)[-1]) != STATION_ROW_SHA256:
        raise ValueError("station CSV excerpt SHA mismatch")
    origin = parse_original_rows(snapshot)
    listing = parse_station_row(row_csv)
    return {
        "schema": "conde.isd-caravelas-station-lineage/v1",
        "station_key": {"usaf": STATION_KEY[0], "wban": STATION_KEY[1]},
        "original_records": {
            "source_url": "https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz",
            "full_source_sha256": SOURCE_SHA256,
            "coordinate_encoding": "ISD row positions 28:34, 34:41 at 0.001 degree; elevation 46:51 in metres",
            "reported_position": origin,
            "historical_site_survey_verified": None
        },
        "retrospective_catalog": {
            "source_url": "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv",
            "full_source_sha256": HISTORY_SHA256,
            "station_row_sha256": STATION_ROW_SHA256,
            "reported_position": listing,
            "position_epoch_verified": None
        },
        "comparison": {
            "horizontal_geodesic_separation_km": round(great_circle_km(origin, listing), 6),
            "elevation_catalog_minus_record_m": listing["elevation_m"]-origin["elevation_m"],
            "difference_is_geolocation_error_bound": False,
            "station_relocation_proven": False
        },
        "scientific_status": {
            "classification": "CONFLICTING_RETROSPECTIVE_POSITION_FIELDS",
            "relation_to_conde": "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION",
            "instrument_position_in_1963": None,
            "measurement_covariance": None,
            "active_location_or_drag_constraint": None,
            "need": "original 1963 station survey / original field log and position lineage"
        }
    }


def check(full_gzip: Path | None = None, history_csv: Path | None = None) -> dict:
    if history_csv is not None:
        if extract_station_history(history_csv.read_bytes()) != HISTORY_ROW.read_bytes():
            raise ValueError("NOAA history CSV source/excerpt mismatch")
    if full_gzip is not None:
        original_gz = full_gzip.read_bytes()
        if digest(original_gz) != SOURCE_SHA256:
            raise ValueError("ISD full archive SHA mismatch")
        full = parse_original_rows(gzip.decompress(original_gz), 8532)
        if full["rows"] != 8532 or full["distinct_dates"] != 365:
            raise ValueError("year-wide ISD coverage unexpectedly changed")
    report = build_report()
    if json.loads(REPORT.read_text()) != report:
        raise ValueError("station lineage published report differs from source")
    graph = json.loads(GRAPH.read_text())
    if (graph["status"] != report["scientific_status"]["relation_to_conde"] or
            graph["active_conde_constraint"] is not None or
            graph["station_site_1963"] is not None or
            graph["instrument_covariance"] is not None or
            graph["evidence"]["history_row_sha256"] != STATION_ROW_SHA256):
        raise ValueError("pending station genealogy incorrectly promoted")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--verify-full-gz", type=Path)
    p.add_argument("--verify-history-csv", type=Path)
    args = p.parse_args()
    report = check(args.verify_full_gz, args.verify_history_csv) if args.check else build_report()
    print(json.dumps(report if not args.check else {
        "checked": True, "separation_km": report["comparison"]["horizontal_geodesic_separation_km"]
    }, ensure_ascii=False, indent=2))
