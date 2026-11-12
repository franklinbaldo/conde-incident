#!/usr/bin/env python3
"""Dry-air ideal-gas density proxy from source-pinned IGRA p/T in Recife only."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from audit_igra_recife_window import DAYS, load_original, parse_day
from audit_igra_recife_winds import ARCHIVE_SHA256, ARCHIVE_BYTES, SOURCE_URL, FORMAT_URL, number

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research/meteorology"
DRY_R = 287.05   # J / (kg K), assumed ideal dry air, not a measured constant of 1963 air
COMMON_HPA = (1000, 850, 700, 500, 300, 100)

def density_proxy(p_pa: int, temp10: int) -> float:
    k = 273.15 + temp10 / 10
    if p_pa <= 0 or k <= 0 or not math.isfinite(k):
        raise ValueError("impossible pressure or absolute temperature")
    return p_pa / (DRY_R * k)

def extract(day: str, raw: bytes | None = None) -> dict:
    if day not in DAYS:
        raise ValueError("unrecognized sounding date")
    if raw is None:
        raw = load_original(day)  # verify pinned NOAA SHA
    hdr = parse_day(raw, day)  # epoch, station, provenance, level count
    lines = raw.decode("ascii").splitlines()[1:]
    rows = []
    last_p, last_h = float("inf"), -float("inf")
    for idx, ln in enumerate(lines):
        if len(ln) < 51 or ln[0] not in "123" or ln[1] not in "012":
            raise ValueError("malformed IGRA record")
        p, h, t10, rh10 = (number(ln, 9, 15), number(ln, 16, 21),
                          number(ln, 22, 27), number(ln, 28, 33))
        if None in (p, h, t10):
            continue   # no invented temperature or altitude
        if p >= last_p or h <= last_h:
            raise ValueError("nonmonotone source p/height")
        if not -1200 <= t10 <= 700:
            raise ValueError("outside source thermometer plausibility interval")
        if rh10 is not None and not (0 <= rh10 <= 1000):
            raise ValueError("RH out of range")
        last_p, last_h = p, h
        rows.append({
            "source_level_index": idx,
            "pressure_hpa": p / 100,
            "geopotential_height_m_asl": h,
            "geopotential_height_flag": ln[21].strip() or None,
            "temperature_deg_c": t10 / 10,
            "temperature_flag": ln[27].strip() or None,
            "reported_rh_percent": None if rh10 is None else rh10 / 10,
            "dry_density_proxy_kg_m3": round(density_proxy(p, t10), 9),
        })
    if len(rows) != len(lines):
        raise ValueError("published source expects all original p/T/height levels")
    by_p = {row["pressure_hpa"]: row for row in rows}
    if len(by_p) != len(rows) or any(p not in by_p for p in COMMON_HPA):
        raise ValueError("duplicate or absent common isobaric pressure")
    return {
        "schema": "conde.igra-recife-conditional-dry-density/v1",
        "source": {
            "station_id": "BRM00082900", "latitude_catalog_deg": -8.05,
            "longitude_catalog_deg_east": -34.9167, "station_elevation_catalog_m": 7,
            "historical_location_verified": False, "archive_url": SOURCE_URL,
            "archive_sha256": ARCHIVE_SHA256, "archive_bytes": ARCHIVE_BYTES,
            "excerpt_sha256": DAYS[day][0], "format_url": FORMAT_URL,
            "upstream": "ncdc6301",
            "dependence": "one station and one NCDC upstream; repeated days not independent source archives"
        },
        "epoch": {"nominal_utc_date": hdr["nominal_utc_date"],
                  "nominal_hour_utc": 12, "actual_release_utc": None, "missing_time_code": 9999},
        "physical_link": {
            "assumption_R_dry_J_kgK": DRY_R,
            "equation": "rho_proxy=p_Pa/(287.05*(273.15+T_C))",
            "quantities_observed": ["p", "T", "geopotential height", "RH where present", "QC flags"],
            "quantity_derived": "dry ideal gas density proxy, not a measured actual moist-air density",
            "geopotential_height_is_not_geometric": True,
            "uncertainties": {"instrumental_kg_m3": None, "humidity_correction_kg_m3": None,
                              "regional_transfer_kg_m3": None, "time_transfer_kg_m3": None},
            "conde_air_density_estimated": False, "norad528_thermosphere_estimated": False,
            "fragment_drift_estimated": False, "uncertainty_is_not_numeric_zero": True,
            "status": "RECIFE_PT_OBSERVED_DRY_PROXY_CONDITIONAL_NO_TRANSFER",
            "evidence_ids": ["C17", "C18", "C19", "C20", "C21", "C22", "C23",
                             "C144", "C145", "C146", "C149", "C150", "C151", "C193"]
        },
        "source_levels": len(lines),
        "rh_levels": sum(r["reported_rh_percent"] is not None for r in rows),
        "common_isobaric_hpa": list(COMMON_HPA),
        "levels": rows,
    }

def check():
    for day in DAYS:
        expected = extract(day)
        target = OUTDIR / f"igra_recife_196311{day}_dry_density_proxy.json"
        if json.loads(target.read_text(encoding="utf-8")) != expected:
            raise ValueError("pinned source does not reproduce " + target.name)
    print("PASS 81 original p/T/height levels in 3 source-pinned Recife dry-proxy profiles")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--day", choices=DAYS)
    args = ap.parse_args()
    if args.check: check()
    elif args.day: print(json.dumps(extract(args.day), indent=2, ensure_ascii=False))
    else: ap.error("--check or --day required")

if __name__ == "__main__":
    main()
