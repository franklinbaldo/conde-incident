#!/usr/bin/env python3
"""Offline, source-pinned comparison of three *nominal*-date Recife soundings.

This is a same-station temporal contrast, not a spatial transfer, a confidence
interval, a fitted met model, or an observed reentry epoch.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
from pathlib import Path

from audit_igra_recife_winds import number, ARCHIVE_SHA256, ARCHIVE_BYTES, SOURCE_URL

ROOT = Path(__file__).resolve().parents[1]
DAYS = {
    "07": ("d77a3bc79935199cc5606a21a464f2836edc1191105ea44a03e58a3fce8375c6", 29),
    "08": ("577224172e19552f5ce87081897479255596dc44debacc674dfd9d9ec418207e", 26),
    "09": ("73e963250891689bf39baf5c29963dd3e42ed13180cf72355237cf98a70d00b2", 26),
}
PRESSURES = (850, 700, 500, 300, 250)
OUTPUT = ROOT / "research/meteorology/igra_recife_19631107_09_temporal_contrast.json"


def load_original(day: str) -> bytes:
    if day not in DAYS:
        raise ValueError("unlisted comparison day")
    raw = base64.b64decode(
        (ROOT / f"research/meteorology/igra_recife_196311{day}_raw.txt.b64").read_bytes().replace(b"\n", b"").replace(b"\r", b""),
        validate=True,
    )
    if hashlib.sha256(raw).hexdigest() != DAYS[day][0]:
        raise ValueError("original IGRA sounding excerpt checksum mismatch")
    return raw


def parse_day(raw: bytes, day: str) -> dict:
    lines = raw.decode("ascii").splitlines()
    if not lines:
        raise ValueError("empty sounding")
    h = lines[0]
    if (h[1:12], h[13:17], h[18:20], h[21:23]) != ("BRM00082900", "1963", "11", day):
        raise ValueError("wrong station / date")
    if h[24:26] != "12" or h[27:31] != "9999":
        raise ValueError("nominal hour or missing real launch time changed")
    if h[37:45].strip() != "ncdc6301":
        raise ValueError("changed upstream source")
    n = int(h[32:36])
    if n != DAYS[day][1] or len(lines) != n + 1:
        raise ValueError("sounding level count mismatch")
    if (int(h[55:62]) / 10000, int(h[63:71]) / 10000) != (-8.05, -34.9167):
        raise ValueError("station catalog coordinate mismatch")
    winds = []
    by_pressure = {}
    for index, ln in enumerate(lines[1:]):
        if len(ln) < 51 or ln[0] not in "123" or ln[1] not in "012":
            raise ValueError("malformed level record")
        p = number(ln, 9, 15)
        height = number(ln, 16, 21)
        deg = number(ln, 40, 45)
        speed10 = number(ln, 46, 51)
        if (deg is None) != (speed10 is None):
            raise ValueError("one wind component missing")
        if deg is None:
            continue
        if p is None or p <= 0 or not 0 <= deg <= 360 or speed10 < 0:
            raise ValueError("invalid pressure/wind")
        winds.append(index)
        if p % 100 != 0:  # pressure in Pa; target standard levels
            continue
        hpa = p // 100
        if hpa in PRESSURES:
            if hpa in by_pressure or height is None:
                raise ValueError("duplicate or no-altitude standard wind level")
            speed = speed10 / 10
            angle = math.radians(deg)
            by_pressure[hpa] = {
                "pressure_hpa": hpa,
                "geopotential_height_m_asl": height,
                "gph_quality_flag": ln[21].strip() or None,
                "wind_from_deg": deg,
                "speed_m_s": speed,
                "u_east_m_s": round(-speed * math.sin(angle), 6),
                "v_north_m_s": round(-speed * math.cos(angle), 6),
            }
    if len(winds) != 15 or set(by_pressure) != set(PRESSURES):
        raise ValueError("unreproducible level/wind coverage")
    return {
        "nominal_utc_date": f"1963-11-{day}",
        "nominal_utc_hour": 12,
        "release_time_utc": None,
        "release_time_missing_code": 9999,
        "record_sha256": hashlib.sha256(raw).hexdigest(),
        "source_levels": n,
        "complete_wind_levels": len(winds),
        "standard_pressure_levels": [by_pressure[p] for p in PRESSURES],
    }


def build():
    soundings = [parse_day(load_original(day), day) for day in DAYS]
    lookup = {s["nominal_utc_date"][-2:]: {r["pressure_hpa"]: r for r in s["standard_pressure_levels"]} for s in soundings}
    contrasts = []
    for p in PRESSURES:
        center = lookup["08"][p]
        comparisons = {}
        for day in ("07", "09"):
            other = lookup[day][p]
            du = round(other["u_east_m_s"] - center["u_east_m_s"], 6)
            dv = round(other["v_north_m_s"] - center["v_north_m_s"], 6)
            comparisons[f"day_{day}_minus_08"] = {
                "delta_u_m_s": du,
                "delta_v_m_s": dv,
                "vector_difference_m_s": round(math.hypot(du, dv), 6),
            }
        contrasts.append({"pressure_hpa": p, **comparisons})
    return {
        "schema": "conde.igra-recife-nominal-date-contrast/v1",
        "source": {
            "archive_url": SOURCE_URL,
            "archive_bytes": ARCHIVE_BYTES,
            "archive_sha256": ARCHIVE_SHA256,
            "instrument_station": "BRM00082900",
            "coordinates_catalogued": {"lat_deg": -8.05, "lon_deg_east": -34.9167, "elevation_m": 7},
            "original_archive_upstream_code": "ncdc6301",
            "same_instrumental_family": True,
            "exact_1963_station_location_verified": False,
            "instrument_error_m_s": None,
            "temporal_transfer_error_m_s": None,
            "recife_to_conde_transfer_error_m_s": None,
            "station_period": "three separate nominal-date soundings, not independent stations",
        },
        "soundings": soundings,
        "inter_day_at_recife_nominal_date_contrasts": contrasts,
        "methodology": {
            "days": ["1963-11-07", "1963-11-08", "1963-11-09"],
            "time_differences_are_nominal": True,
            "real_release_times_all_unknown": True,
            "comparisons_are_not_calibrated_uncertainty_bounds": True,
            "sampling_is_not_spatially_transferable_to_conde": True,
            "pressure_level_isobaric_comparison": True,
            "gph_is_geopotential_altitude_not_exact_geometric_altitude": True,
            "balloon_drift_or_impact_location_estimated": False,
            "satellite_thermospheric_density_estimated": False,
            "physical_constraint_status": "OBSERVATION_ONLY_PENDING_SPATIOTEMPORAL_TRANSFER",
            "related_matrix_ids": ["C149", "C150", "C151", "C144", "C145", "C146", "C17", "C18", "C19", "C20", "C21", "C23", "C193"],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    calculated = build()
    if args.check:
        published = json.loads(OUTPUT.read_text())
        if calculated != published:
            raise SystemExit("FAIL: pinned NOAA IGRA excerpts do not reproduce published comparison")
        print("PASS three original Recife soundings, pinned hashes, pressure-level contrasts, uncertainty left unknown")
    else:
        print(json.dumps(calculated, ensure_ascii=False, indent=2) + "\n", end="")


if __name__ == "__main__":
    main()
