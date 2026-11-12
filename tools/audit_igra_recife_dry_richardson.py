#!/usr/bin/env python3
"""Finite-layer dry Richardson diagnostic at original IGRA wind/temperature levels.

This diagnostic is NOT the local gradient Richardson number or a turbulence
observation: vertical averages across finite/large sounding intervals are not
local gradients, and dry parcel stability is not moist atmospheric stability.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from audit_igra_recife_window import DAYS
from audit_igra_recife_dry_density import DRY_R, extract
from audit_igra_recife_shear import read_winds

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/meteorology/igra_recife_19631107_09_dry_richardson.json"
CP_DRY = 1004.0  # J / kg / K: explicit model assumption
G0 = 9.80665  # m / s^2 (geopotential height convention)
REFERENCE_HPA = 1000.0


def potential_temperature(temp_c: float, pressure_hpa: float) -> float:
    if not (-120 < temp_c < 70 and pressure_hpa > 0):
        raise ValueError("impossible source temperature or pressure")
    return (temp_c + 273.15) * (REFERENCE_HPA / pressure_hpa) ** (DRY_R / CP_DRY)


def finite_layer(lower: dict, upper: dict) -> dict:
    p0, p1 = lower["pressure_hpa"], upper["pressure_hpa"]
    z0, z1 = lower["geopotential_height_m_asl"], upper["geopotential_height_m_asl"]
    dz = z1 - z0
    if p0 <= p1 or dz <= 0:
        raise ValueError("nonmonotone pressure/geopotential endpoints")
    t0, t1 = potential_temperature(lower["temperature_deg_c"], p0), potential_temperature(upper["temperature_deg_c"], p1)
    du = upper["u_east_m_s"] - lower["u_east_m_s"]
    dv = upper["v_north_m_s"] - lower["v_north_m_s"]
    shear_squared = (du * du + dv * dv) / dz**2
    dry_n2 = G0 / ((t0 + t1) / 2) * (t1 - t0) / dz
    if not all(map(math.isfinite, (dry_n2, shear_squared))):
        raise ValueError("nonfinite diagnostic")
    # When both endpoint winds are equal, no division by zero, no inferred
    # infinite Richardson number. Missing source levels are never filled.
    ri = dry_n2 / shear_squared if shear_squared > 1e-20 else None
    return {
        "pressure_bottom_hpa": p0, "pressure_top_hpa": p1,
        "geopotential_bottom_m": z0, "geopotential_top_m": z1,
        "temperature_bottom_c": lower["temperature_deg_c"],
        "temperature_top_c": upper["temperature_deg_c"],
        "finite_layer_dry_n2_s_minus2": round(dry_n2, 9),
        "finite_layer_shear_squared_s_minus2": round(shear_squared, 15),
        "finite_layer_dry_richardson": None if ri is None else round(ri, 6),
        "calm_endpoint": lower["wind_speed_m_s"] == 0 or upper["wind_speed_m_s"] == 0,
    }


def build() -> dict:
    profiles = []
    for day in DAYS:
        original_t = extract(day)  # validates SHA, header, station, time, source
        winds = read_winds(day)  # independently parses same pinned original bytes
        if original_t["epoch"]["actual_release_utc"] is not None:
            raise ValueError("unsourced release time")
        temperatures = {(p["pressure_hpa"], p["geopotential_height_m_asl"]): p
                        for p in original_t["levels"]}
        if len(temperatures) != len(original_t["levels"]):
            raise ValueError("duplicate source p/H pairs")
        paired = []
        for w in winds:
            key = (w["pressure_hpa"], w["geopotential_height_m_asl"])
            if key not in temperatures:
                raise ValueError("wind endpoint missing co-located original p/T/H")
            t = temperatures[key]
            if w["geopotential_height_qc_flag"] != t["geopotential_height_flag"]:
                raise ValueError("source QC flag divergence")
            paired.append({**t, **w,
                           "temperature_deg_c": t["temperature_deg_c"],
                           "wind_speed_m_s": w["speed_m_s"]})
        rows = [finite_layer(a, b) for a, b in zip(paired, paired[1:])]
        if len(rows) != 14:
            raise ValueError("expected exactly 14 recorded-wind adjacent endpoint pairs")
        profiles.append({
            "nominal_utc_date": original_t["epoch"]["nominal_utc_date"],
            "nominal_utc_hour": 12, "actual_release_utc": None,
            "original_excerpt_sha256": original_t["source"]["excerpt_sha256"],
            "recorded_wind_and_temperature_levels": len(paired),
            "paired_finite_layers": len(rows),
            "negative_dry_n2_layers": sum(r["finite_layer_dry_n2_s_minus2"] < 0 for r in rows),
            "layers": rows,
        })
    return {
        "schema": "conde.igra-recife-finite-dry-richardson/v1",
        "source": {
            "station_id": "BRM00082900", "catalog_latitude_deg": -8.05,
            "catalog_longitude_deg_east": -34.9167,
            "catalog_station_elevation_m": 7, "historical_1963_station_location_verified": False,
            "source_url": original_t["source"]["archive_url"],
            "source_sha256": original_t["source"]["archive_sha256"],
            "format_url": original_t["source"]["format_url"],
            "upstream": "ncdc6301", "source_independent_families": 1,
            "same_soundings_used_for_wind_temperature_height": True,
        },
        "method": {
            "theta": "theta_K=(T_C+273.15)*(1000/p_hPa)^(287.05/1004.0)",
            "N2_finite": "(9.80665/theta_endpoint_mean)*(theta_top-theta_bottom)/(H_top-H_bottom)",
            "shear_squared_finite": "((u_top-u_bottom)^2+(v_top-v_bottom)^2)/(H_top-H_bottom)^2",
            "Ri_finite_dry": "N2_finite/shear_squared_finite where nonzero",
            "heights": "geopotential metres ASL, not geometric altitude",
            "model_assumption": "dry ideal-gas air, Cp_dry=1004, constant g0; endpoint finite differences",
            "not_observed": ["local gradient", "intermediate-layer winds", "turbulence", "moist stability",
                             "vertical-mixing coefficient", "1963 instrument uncertainty", "Conde winds"],
            "critical_local_gradient_threshold_applicable": False,
            "instrument_uncertainty": None, "height_transfer_uncertainty": None,
            "spatiotemporal_transfer_uncertainty": None,
            "physical_domain_reduction": False, "event_location_inferred": False,
            "related_evidence": ["C17", "C18", "C19", "C20", "C21", "C22", "C23",
                                 "C144", "C145", "C146", "C149", "C150", "C151", "C193"],
            "graph": [
                {"from": "C149-C151/IGRA_Recife_1963", "to": "dry_theta_finite_layers", "status": "CONDITIONAL_MODEL_DIAGNOSTIC"},
                {"from": "dry_theta_finite_layers+observed_wind_endpoints", "to": "dry_Ri_finite_Recife", "status": "CONDITIONAL_MODEL_DIAGNOSTIC"},
                {"from": "dry_Ri_finite_Recife", "to": "Conde_turbulence_or_fragment_drift", "status": "PENDING_UNCALIBRATED_TRANSFER"},
            ],
        },
        "profiles": profiles,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    fresh = build()
    if args.check:
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != fresh:
            raise SystemExit("FAIL: dry finite-layer diagnostics differ from pinned originals")
        print("PASS: 42 paired finite-layer dry diagnostics, source pins, no spatial inference")
    else:
        OUTPUT.write_text(json.dumps(fresh, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(OUTPUT)


if __name__ == "__main__":
    main()
