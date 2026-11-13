#!/usr/bin/env python3
"""Audit 1963 NOAA ISD archive filenames against retrospective Brazilian stations."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MET = ROOT / "research/meteorology/isd_bahia_coastal_1963_archive_coverage.json"
EDGES = ROOT / "research/constraints/isd_bahia_coastal_1963_archive_edges.json"
HISTORY_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"
INDEX_URL = "https://www.ncei.noaa.gov/pub/data/noaa/1963/"
HISTORY_SHA = "1994747ab4af1b97e63adb434b4d0d022f2daee76f0c144ea9ab46be2d906604"
INDEX_SHA = "93627d0e6010063fc54d6029d67499952107784f47740d895a17516e6dfb401d"
FILENAMES_SHA = "51140ef98cf946a8d885d9fb86ff4b8cefd0009708c7adae06a2e20efcf0832c"
CONDE_REF = (-11.8641854035, -37.68935144749995)  # IBGE 2022 bbox midpoint; NOT historical.
NAME_RE = re.compile(rb'href="(\d{6}-\d{5}-1963\.gz)"')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def year_range_contains_1963(row: dict) -> bool:
    return row["BEGIN"][:4] <= "1963" <= row["END"][:4]


def haversine_km(lat: float, lon: float) -> float:
    lat0, lon0 = CONDE_REF
    p1, p2 = math.radians(lat0), math.radians(lat)
    a = math.sin((p2 - p1) / 2)**2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon - lon0) / 2)**2
    return 12742 * math.asin(min(1, math.sqrt(a)))


def parse_index(raw: bytes) -> list[str]:
    found = [v.decode("ascii") for v in NAME_RE.findall(raw)]
    if not found or len(found) != len(set(found)):
        raise ValueError("Empty or duplicate NOAA annual archive filenames")
    return sorted(found)


def catalogue_candidates(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text)))
    found = []
    keys = set()
    for r in rows:
        if r["CTRY"] != "BR" or not year_range_contains_1963(r):
            continue
        try:
            lat, lon = float(r["LAT"]), float(r["LON"])
        except ValueError as e:
            raise ValueError("Malformed BR station coordinates") from e
        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            raise ValueError("Coordinates out of range")
        key = f'{r["USAF"]}-{r["WBAN"]}-1963.gz'
        if key in keys:
            raise ValueError(f"Duplicate station key: {key}")
        keys.add(key)
        found.append({"file": key, "catalogue_name": r["STATION NAME"],
                      "distance_km": round(haversine_km(lat, lon), 1),
                      "catalogue_begin": r["BEGIN"], "catalogue_end": r["END"]})
    return sorted(found, key=lambda r: (r["distance_km"], r["file"]))


def audit(history: bytes, index: bytes, *, verify_pins: bool = True) -> dict:
    if verify_pins and sha(history) != HISTORY_SHA:
        raise ValueError("ISD history changed: verify source, do not silently refresh")
    if verify_pins and sha(index) != INDEX_SHA:
        # Pin the original HTTP body, not just the extracted names.
        raise ValueError("NOAA 1963 directory listing changed: investigate before accepting")
    names = parse_index(index)
    joined = ("\n".join(names) + "\n").encode("ascii")
    if verify_pins and sha(joined) != FILENAMES_SHA:
        raise ValueError("1963 filename inventory changed")
    stations = catalogue_candidates(history)
    present = [r for r in stations if r["file"] in set(names)]
    nearest = stations[:12]
    return {
        "schema": "conde.isd-coastal-1963-archive-coverage/v1",
        "id": "MET-ISD-BAHIA-1963-ARCHIVE-COVERAGE-01",
        "source_urls": {"retrospective_station_history": HISTORY_URL, "directory_1963": INDEX_URL},
        "capture_date_utc": "2026-11-13",
        "sha256": {"station_history_full": sha(history), "directory_html_full": sha(index),
                   "directory_sorted_filenames": sha(joined)},
        "reference": {"kind": "IBGE_2022_Conde_municipality_bbox_midpoint_not_1963",
                      "lat_lon": list(CONDE_REF), "distance_method": "haversine_spherical_R6371km",
                      "historical_coordinate_uncertainty_km": None},
        "directory_gz_count": len(names),
        "catalogue_br_country_code_with_1963_in_year_bounds": len(stations),
        "matching_1963_files": len(present),
        "matched_nearest_first": present,
        "catalogue_nearest_12": [{**r, "annual_file_listed": r["file"] in set(names)} for r in nearest],
        "matched_within_500km": sum(r["distance_km"] <= 500 for r in present),
        "matched_within_800km": sum(r["distance_km"] <= 800 for r in present),
        "warning_country_code": "CTRY=BR is a literal catalog field; includes PUERTO PINASCO (860880), whose location/country assignment requires independent checking.",
        "not_proved": {
            "absence_of_1963_real_world_observations_in_unlisted_stations": None,
            "presence_of_1963_11_07_09_observations_in_listed_annual_files": None,
            "historical_station_coordinates_and_instruments": None,
            "independent_measurement_lineage": None,
            "transfer_conde_wind_or_density": None,
            "active_conde_constraint": None
        },
        "status": "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION"
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", type=Path, required=True)
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    result = audit(args.history.read_bytes(), args.index.read_bytes())
    if args.check:
        if result != json.loads(MET.read_text(encoding="utf8")):
            raise SystemExit("NOAA archive coverage manifest differs from verified sources")
        graph = json.loads(EDGES.read_text(encoding="utf8"))
        if graph["source"] != result["id"] or graph["status"] != result["status"] or graph["active_conde_constraint"] is not None:
            raise SystemExit("Cumulative graph does not preserve pending links")
        print(f'PASS: {result["matching_1963_files"]} of {result["catalogue_br_country_code_with_1963_in_year_bounds"]} catalogue stations in NOAA 1963 directory')
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
