#!/usr/bin/env python3
"""Auditable finite differences of *recorded* Recife winds, not a wind field.

All three IGRA payloads are raw, SHA-256-pinned excerpts from one NCDC family.
The finite difference is per geopotential kilometre (not geometric altitude).
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from audit_igra_recife_window import DAYS, load_original, parse_day
from audit_igra_recife_winds import ARCHIVE_SHA256, ARCHIVE_BYTES, SOURCE_URL, FORMAT_URL, number

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/meteorology/igra_recife_19631107_09_vertical_shear.json"


def read_winds(day: str) -> list[dict]:
    raw = load_original(day)  # Verify archival excerpt hash first.
    parsed = parse_day(raw, day)  # Verify station, date, time, source and levels.
    lines = raw.decode("ascii").splitlines()
    if len(lines) != parsed["source_levels"] + 1:
        raise ValueError("inconsistent IGRA profile length")
    winds: list[dict] = []
    for i, ln in enumerate(lines[1:]):
        p_pa, z, direction, speed10 = (
            number(ln, 9, 15), number(ln, 16, 21),
            number(ln, 40, 45), number(ln, 46, 51)
        )
        if (direction is None) != (speed10 is None):
            raise ValueError("partial wind observation")
        if direction is None:
            continue  # NEVER interpolate missing winds.
        if p_pa is None or p_pa <= 0 or z is None or not (0 <= direction <= 360) or speed10 < 0:
            raise ValueError("unusable pressure/height/wind combination")
        theta = math.radians(direction)
        speed = speed10 / 10
        winds.append({
            "record_level_index": i,
            "pressure_hpa": p_pa / 100,
            "geopotential_height_m_asl": z,
            "geopotential_height_qc_flag": ln[21].strip() or None,
            "wind_from_recorded_deg": direction,
            "wind_direction_defined": speed > 0,
            "speed_m_s": speed,
            "u_east_m_s": -speed * math.sin(theta),
            "v_north_m_s": -speed * math.cos(theta),
        })
    if len(winds) != 15:
        raise ValueError("wind coverage changed")
    if any(a["pressure_hpa"] <= b["pressure_hpa"] or a["geopotential_height_m_asl"] >= b["geopotential_height_m_asl"] for a, b in zip(winds, winds[1:])):
        raise ValueError("pressure/height order inconsistent")
    return winds


def build() -> dict:
    profiles = []
    for day in DAYS:
        winds = read_winds(day)
        adjacent = []
        for lower, upper in zip(winds, winds[1:]):
            dz = upper["geopotential_height_m_asl"] - lower["geopotential_height_m_asl"]
            if dz <= 0:
                raise ValueError("cannot divide by nonpositive geopotential interval")
            du = upper["u_east_m_s"] - lower["u_east_m_s"]
            dv = upper["v_north_m_s"] - lower["v_north_m_s"]
            # Derivative is an observed endpoint finite difference, not a
            # measured profile inside the layer, nor a physical uncertainty.
            adjacent.append({
                "pressure_bottom_hpa": lower["pressure_hpa"],
                "pressure_top_hpa": upper["pressure_hpa"],
                "geopotential_height_bottom_m_asl": lower["geopotential_height_m_asl"],
                "geopotential_height_top_m_asl": upper["geopotential_height_m_asl"],
                "geopotential_height_qc_flags": [lower["geopotential_height_qc_flag"], upper["geopotential_height_qc_flag"]],
                "delta_u_east_m_s": round(du, 6),
                "delta_v_north_m_s": round(dv, 6),
                "vector_difference_m_s": round(math.hypot(du, dv), 6),
                "finite_difference_m_s_per_geopotential_km": round(math.hypot(du, dv) * 1000 / dz, 6),
                "calm_endpoint_present": not (lower["wind_direction_defined"] and upper["wind_direction_defined"]),
            })
        profiles.append({
            "nominal_utc_date": "1963-11-" + day,
            "nominal_utc_hour": 12,
            "actual_release_utc": None,
            "original_excerpt_sha256": DAYS[day][0],
            "wind_observed_levels": len(winds),
            "adjacent_observed_pairs": len(adjacent),
            "vertical_layers": adjacent,
        })
    return {
        "schema": "conde.igra-recife-vertical-shear/v1",
        "source": {
            "archive_url": SOURCE_URL,
            "archive_sha256": ARCHIVE_SHA256,
            "archive_bytes": ARCHIVE_BYTES,
            "format_url": FORMAT_URL,
            "station_id": "BRM00082900",
            "catalogued_latitude_deg": -8.05,
            "catalogued_longitude_deg": -34.9167,
            "catalogued_elevation_m_asl": 7,
            "exact_1963_station_location_verified": False,
            "ncdc_upstream_code": "ncdc6301",
            "provenance_group": "IGRA/NCDC single station, three nominal soundings; not independent of recycled UADB/NCDC data",
        },
        "observables": profiles,
        "methodology": {
            "source_measurement": "recorded upper-air wind speed/direction at individual pressure/geopotential levels in Recife only",
            "derived_observable": "horizontal wind vector finite difference between consecutive observed levels per geopotential kilometre",
            "equation": "S_ij = sqrt((u_j-u_i)^2+(v_j-v_i)^2) * 1000 / (H_j-H_i) [m/s per geopotential km]",
            "wind_components": "u=-speed*sin(from_deg); v=-speed*cos(from_deg)",
            "heights_are_geopotential_not_geometric": True,
            "zero_wind_direction_not_physically_identifiable": True,
            "all_missing_wind_levels_excluded": True,
            "real_release_time_unknown_code_9999": True,
            "vertical_profile_between_levels_observed": False,
            "wind_transfer_to_conde_calibrated": False,
            "reentry_or_fragment_path_observed": False,
            "instrumental_uncertainty_m_s": None,
            "vertical_transfer_uncertainty_m_s": None,
            "regional_transfer_uncertainty_m_s": None,
            "thermospheric_drag_constraint": False,
            "physical_constraint_status": "CONNECTED_PENDING_SPATIOTEMPORAL_TRANSFER",
            "related_evidence_ids": ["C17", "C18", "C19", "C20", "C21", "C22", "C23", "C144", "C145", "C146", "C147", "C149", "C150", "C151", "C193"],
            "independent_confirmation_count_for_conde_winds": 0,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    fresh = build()
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != fresh:
            raise SystemExit("FAIL: published vertical shear differs from pinned NOAA originals")
        print("PASS: 3 IGRA source-pinned dates, 45 winds, 42 geometric-free finite differences; no transfers inferred")
    else:
        print(json.dumps(fresh, ensure_ascii=False, indent=2) + "\n", end="")


if __name__ == "__main__":
    main()
