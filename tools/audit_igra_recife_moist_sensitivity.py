#!/usr/bin/env python3
"""Conditional moist-air density sensitivity from pinned IGRA Recife source profiles.

No regional/temporal transfer, observed moist density or 1963 radiosonde RH calibration.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from audit_igra_recife_dry_density import DAYS, DRY_R, OUTDIR, density_proxy, extract

VAPOR_R = 461.5  # J/(kg K), ideal water vapor assumption
SAT_HPA = 6.1094
MAGNUS_A = 17.625
MAGNUS_B_C = 243.04
FILE = OUTDIR / "igra_recife_19631107_09_moist_sensitivity.json"


def scenario(pressure_hpa: float, temperature_c: float, rh_percent: float) -> dict:
    """Model sensitivity only, over liquid water at nonnegative Celsius temperatures."""
    for value in (pressure_hpa, temperature_c, rh_percent):
        if not math.isfinite(value):
            raise ValueError("nonfinite input")
    if not (0 <= temperature_c <= 50) or not (0 <= rh_percent <= 100) or pressure_hpa <= 0:
        raise ValueError("outside explicit warm-water pressure/temperature/RH assumptions")
    es_hpa = SAT_HPA * math.exp(MAGNUS_A * temperature_c / (MAGNUS_B_C + temperature_c))
    e_hpa = (rh_percent / 100) * es_hpa
    if e_hpa >= pressure_hpa:
        raise ValueError("water vapor partial pressure exceeds total pressure")
    t_kelvin = temperature_c + 273.15
    dry = density_proxy(round(pressure_hpa * 100), round(temperature_c * 10))
    moist = ((pressure_hpa - e_hpa) * 100 / DRY_R + e_hpa * 100 / VAPOR_R) / t_kelvin
    if rh_percent == 0:
        moist = dry  # avoid machine-rounding difference for zero partial pressure
    if not 0 < moist <= dry + 1e-12:
        raise ValueError("nonphysical density ordering")
    return {
        "saturation_vapor_pressure_hpa_model": round(es_hpa, 6),
        "partial_vapor_pressure_hpa_model": round(e_hpa, 6),
        "dry_density_proxy_kg_m3": round(dry, 9),
        "conditional_moist_density_kg_m3": round(moist, 9),
        "conditional_delta_moist_minus_dry_kg_m3": round(moist - dry, 9),
        "conditional_fractional_decrease_pct": round(100 * (dry - moist) / dry, 6),
    }


def build() -> dict:
    profiles = []
    for day in DAYS:
        original = extract(day)  # recreates and checks original hashes, station, epoch
        selected = []
        rejected_cold = 0
        rejected_missing = 0
        for level in original["levels"]:
            rh = level["reported_rh_percent"]
            tc = level["temperature_deg_c"]
            if rh is None:
                rejected_missing += 1
            elif tc < 0:
                rejected_cold += 1  # unknown RH reference phase: no water/ice guess
            else:
                values = scenario(level["pressure_hpa"], tc, rh)
                selected.append({
                    "source_level_index": level["source_level_index"],
                    "pressure_hpa": level["pressure_hpa"],
                    "geopotential_height_m_asl": level["geopotential_height_m_asl"],
                    "temperature_deg_c": tc,
                    "reported_rh_percent": rh,
                    "temperature_flag": level["temperature_flag"],
                    "geopotential_height_flag": level["geopotential_height_flag"],
                    **values,
                })
        if len(selected) + rejected_cold + rejected_missing != len(original["levels"]):
            raise ValueError("source-level eligibility partition inconsistent")
        profiles.append({
            "nominal_date_utc": original["epoch"]["nominal_utc_date"],
            "nominal_hour_utc": 12,
            "actual_launch_time_utc": None,
            "source_excerpt_sha256": original["source"]["excerpt_sha256"],
            "total_pt_levels": len(original["levels"]),
            "rh_present_levels": original["rh_levels"],
            "warm_rh_eligible_levels": len(selected),
            "missing_rh_levels_excluded": rejected_missing,
            "subzero_rh_levels_excluded": rejected_cold,
            "conditional_levels": selected,
        })
    return {
        "schema": "conde.recife-rh-moist-ideal-gas-sensitivity/v1",
        "identity": {
            "station_id": "BRM00082900", "station_name": "Recife (catalogue)",
            "station_latitude_catalog_deg": -8.05,
            "station_longitude_catalog_deg_east": -34.9167,
            "station_elevation_catalog_m": 7,
            "1963_station_geolocation_reconstructed": False,
            "archive_url": profiles and extract("08")["source"]["archive_url"],
            "archive_sha256": extract("08")["source"]["archive_sha256"],
            "upstream": "ncdc6301",
            "dependence": "one NOAA/IGRA station/source lineage across three days; no new independent instrument",
        },
        "model": {
            "water_vapor_pressure_equation": "e=RH/100*(6.1094*exp(17.625*T_C/(243.04+T_C))) hPa",
            "water_vapor_formula_reference": "Alduchov & Eskridge 1996 J Appl Meteorol 35 601-609; modern modelling equation not asserted as 1963 instrument reduction",
            "density_equation": "rho=((p-e)*100)/(287.05*T_K)+(e*100)/(461.5*T_K)",
            "pressure_unit": "hPa", "temperature_unit": "degC", "height_unit": "geopotential m ASL",
            "validity": "RH present, 0<=T_C<=50, over liquid water, gas mixture ideal; no hydrometeors",
            "rh_reference_phase_1963_verified": False,
            "instrumental_rh_accuracy_percent": None,
            "instrumental_temperature_accuracy_deg_c": None,
            "surface_to_altitude_transfer_error": None,
            "recife_to_conde_transfer_error": None,
            "temporal_transfer_error": None,
            "source_values_are_observations": ["pressure", "temperature", "RH where reported", "geopotential height", "QC flags"],
            "density_values_are_observed": False,
            "estimated_fragment_drift": False,
            "estimated_thermospheric_density": False,
            "estimated_conde_air_density": False,
            "theta_constraint_activated": False,
            "status": "CONNECTED_PENDING_CALIBRATION",
            "evidence_links": ["C17-C23", "C144-C146", "C149-C151", "C193"],
        },
        "totals": {
            "pt_levels": sum(x["total_pt_levels"] for x in profiles),
            "rh_present": sum(x["rh_present_levels"] for x in profiles),
            "warm_rh_eligible": sum(x["warm_rh_eligible_levels"] for x in profiles),
            "rh_missing": sum(x["missing_rh_levels_excluded"] for x in profiles),
            "subzero_rh_excluded": sum(x["subzero_rh_levels_excluded"] for x in profiles),
        },
        "graph_links": [
            {
                "from": "C149-C151#IGRA-Recife-1963-11-07_09",
                "to": "rho_recife_warm_levels_conditional",
                "relation": "observed p/T/RH + explicit modern saturation law and ideal mixture",
                "status": "CONNECTED_CONDITIONAL_NOT_OBSERVED",
            },
            {
                "from": "rho_recife_warm_levels_conditional",
                "to": "rho_conde_fragment_height_time",
                "relation": "needs verified 1963 station position, regional and temporal transfer, calibration errors",
                "status": "PENDING_NO_TRANSFER",
            },
            {
                "from": "rho_conde_fragment_height_time",
                "to": "drag_and_conditional_fragment_drift",
                "relation": "needs trajectory/time, fragment physics, vertical velocity and error model from Castor",
                "status": "PENDING_NO_PHYSICAL_CONSTRAINT",
            },
            {
                "from": "C17-C23#space-weather;C193#Explorer-XVII;C144-C146#CHM",
                "to": "rho_recife_warm_levels_conditional",
                "relation": "distinct contexts and regimes; no observational substitution or replicate evidence",
                "status": "CONTEXT_NOT_CALIBRATION",
            },
        ],
        "profiles": profiles,
    }


def check():
    expected = build()
    got = json.loads(FILE.read_text(encoding="utf-8"))
    if got != expected:
        raise ValueError("pinned source reconstruction does not match published moist sensitivity")
    print("PASS conditional moist sensitivity; 22 warm RH levels; no synthetic missing RH")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        check()
    else:
        print(json.dumps(build(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
