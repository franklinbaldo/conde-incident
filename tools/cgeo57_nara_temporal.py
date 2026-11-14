#!/usr/bin/env python3
"""CGEO-57: distinguish 1942 candidate flight dates from 1956 overlay preparation."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/geo/cgeo57_nara_overlay_preparation_dates.json"
PARENT = ROOT / "research/geo/cgeo56_nara_sortie_cross_square.json"
BASE = "https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-"
EXPECTED = {
    "00247": ("11S037W", "125370", "27 SEP 42", "5 OCT 56", "1956-10-05"),
    "00432": ("12S037W", "125370", "27 SEP 42", "5 OCT 56", "1956-10-05"),
    "00248": ("11S037W", "125374", "7, 14, 18, 20 SEP 42", "6 OCT 56", "1956-10-06"),
    "00431": ("12S037W", "125374", "7, 14, 18, 20 SEP 42", "6 OCT 56", "1956-10-06"),
}
NULL_FIELDS = ("photo_capture_utc", "georeferenced_frame_footprint",
               "verified_spot_number", "film_can", "conde_1963_center", "fall_location")


def validate(d, parent=None):
    if not isinstance(d, dict) or (d.get("schema"), d.get("id"), d.get("parent")) != (
        "conde.cgeo.nara-overlay-temporal-provenance/v1", "CGEO-57", "CGEO-56"
    ):
        raise ValueError("invalid lineage")
    if d.get("record_group") != "NARA RG373 / 306062 / M1765 reel 317":
        raise ValueError("source family changed")
    if not isinstance(d.get("scans"), list) or len(d["scans"]) != 4:
        raise ValueError("expected four original index scans")
    if parent is None:
        parent = json.loads(PARENT.read_text(encoding="utf-8"))
    if parent.get("id") != "CGEO-56" or len(parent.get("scans", [])) != 4:
        raise ValueError("parent evidence absent")
    by_sheet = {v["sheet"]: v for v in parent["scans"]}
    seen = set()
    for row in d["scans"]:
        sheet = row.get("sheet")
        if sheet not in EXPECTED or sheet in seen:
            raise ValueError("unexpected or duplicate sheet")
        seen.add(sheet)
        sq, op, flight, prep, iso = EXPECTED[sheet]
        if (row.get("square"), row.get("op_file"), row.get("flight_date_reading"),
            row.get("preparation_date_reading"), row.get("preparation_date_iso")) != (
            sq, op, flight, prep, iso
        ):
            raise ValueError("header transcript or date changed")
        if row.get("prepared_by_name") is not None:
            raise ValueError("unconfirmed preparer identity")
        if date.fromisoformat(iso).year != 1956 or row.get("preparation_date_iso") < "1943":
            raise ValueError("preparation date inconsistent")
        if (row.get("bytes"), row.get("sha256")) != (
            by_sheet[sheet]["bytes"], by_sheet[sheet]["sha256"]
        ):
            raise ValueError("source bytes not inherited from CGEO-56")
        if row.get("op_file") != by_sheet[sheet]["op_file_no"]:
            raise ValueError("O.P. changed from parent")
    if seen != set(EXPECTED):
        raise ValueError("missing scans")
    if d.get("counts") != {
        "original_film_frames_acquired": 0, "original_overlay_jpegs_referenced": 4,
        "preparation_dates_visually_read": 4
    }:
        raise ValueError("unsupported evidence counts")
    limits = d.get("limits")
    if not isinstance(limits, dict) or any(limits.get(k, "MISSING") is not None for k in NULL_FIELDS):
        raise ValueError("invented geometry, spot or photo epoch")
    if limits.get("orbital_constraint_activated") is not False:
        raise ValueError("unsupported orbital constraint")
    return len(seen)


def live(d):
    for row in d["scans"]:
        url = BASE + row["sheet"] + ".jpg"
        req = Request(url, headers={"User-Agent": "CondeIncident-CGEO57/1.0"})
        with urlopen(req, timeout=50) as response:
            if response.status != 200:
                raise ValueError("HTTP failure")
            blob = response.read()
        if len(blob) != row["bytes"] or hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise ValueError("original image mismatch for " + row["sheet"])
        if not blob.startswith(bytes.fromhex("ffd8")) or not blob.endswith(bytes.fromhex("ffd9")):
            raise ValueError("invalid JPEG endpoints")
        print(f"REPLAY_OK sheet={row['sheet']} bytes={len(blob)} sha256={row['sha256']}")
    return len(d["scans"])


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--live", action="store_true")
    args = cli.parse_args()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    count = validate(data)
    print(f"CGEO57_CONTRACT_PASS scans={count} parent=CGEO-56")
    if args.live:
        print(f"CGEO57_LIVE_PASS images={live(data)}")
