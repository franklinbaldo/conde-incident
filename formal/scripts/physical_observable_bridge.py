#!/usr/bin/env python3
"""Source-linked orbital and meteorological *derived observables* for Castor.

C179 (one secondary 528 TLE lineage) and C151 (NOAA Recife winds 1963-11-08)
live in the frozen cumulative research matrix. The script refuses a changed
snapshot. It never treats Recife as observed weather at Conde or a surface
wind as orbital drag; no MCMC posterior or geographic inference is made.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re

from evidence_registry import MATRIX_PATH, audit, parse_rows, j2_nodal_rate_deg_per_day

MU_KM3_S2 = 398600.4418
EARTH_EQUATORIAL_RADIUS_KM = 6378.137
EPOCH_528 = "1963-10-27T14:40:16.132512Z"
SOURCE_528 = "https://www.itau.magnetic-declination.com/satellite/?s=528"
TLE_PAIR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
SOURCE_RECIFE = "https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip"
# Matrix narrative reports approximate altitudes for THESE standard levels,
# not a full contemporaneous Conde wind sounding.
LEVEL_HEIGHT_M_APPROX = {850: 1560, 700: 3200, 500: 5900, 300: 9700, 250: 11000}
WIND_PATTERN = re.compile(r"(\d{3}) hPa\s+(\d{1,3})°/(\d+)m·s⁻¹")


def meteorological_wind_to_en(speed_m_s: float, from_degrees: float) -> tuple[float, float]:
    """u (east), v (north) from meteorological direction FROM which wind blows."""
    if not (math.isfinite(speed_m_s) and speed_m_s >= 0 and
            math.isfinite(from_degrees) and 0 <= from_degrees <= 360):
        raise ValueError("invalid meteorological wind")
    angle = math.radians(from_degrees)
    return -speed_m_s * math.sin(angle), -speed_m_s * math.cos(angle)


def orbital_observables() -> dict:
    n_rev_day = 15.74901460
    eccentricity = 0.0017147
    inclination_deg = 81.8615
    n_rad_s = 2 * math.pi * n_rev_day / 86400.0
    semimajor_km = (MU_KM3_S2 / (n_rad_s * n_rad_s)) ** (1.0 / 3.0)
    perigee_km = semimajor_km * (1 - eccentricity) - EARTH_EQUATORIAL_RADIUS_KM
    return {
        "source_occurrence": "C179#1",
        "source_url": SOURCE_528,
        "literal_pair_sha256": TLE_PAIR_SHA256,
        "source_status": "SECONDARY_MIRROR_NOT_PRIMARY_TRACK",
        "epoch_utc": EPOCH_528,
        "reported_raan_deg": 198.5261,
        "observed_mean_motion_rev_per_day": n_rev_day,
        "derived_mean_angular_rate_rad_per_s": n_rad_s,
        "derived_kepler_proxy_semimajor_km": semimajor_km,
        "derived_kepler_proxy_perigee_altitude_km": perigee_km,
        "derived_first_order_j2_raan_rate_deg_per_day":
            j2_nodal_rate_deg_per_day(inclination_deg, eccentricity, n_rev_day),
        "model_scope": "TLE_MEAN_ELEMENTS_USED_AS_KEPLER_PROXY_NOT_OSCULATING",
        "observational_error_distribution": None,
        "physical_raan_interval_deg": None,
        "mcmc_posterior": "NOT_RUN",
    }


def recife_winds(matrix_bytes: bytes) -> list[dict]:
    rows = parse_rows(matrix_bytes)
    audit(matrix_bytes, rows)  # exact Git blob SHA, all IDs including collisions
    matched = [r for r in rows if r["number"] == 151 and r["occurrence"] == 1]
    if len(matched) != 1 or matched[0]["line"] != 606:
        raise ValueError("C151 occurrence or anchor changed")
    observations = []
    for p, direction, speed in WIND_PATTERN.findall(matched[0]["row_markdown"]):
        pressure_hpa = int(p)
        if pressure_hpa not in LEVEL_HEIGHT_M_APPROX:
            raise ValueError("unknown pressure level in C151")
        u, v = meteorological_wind_to_en(int(speed), int(direction))
        observations.append({
            "evidence_occurrence": "C151#1",
            "station": "BRM00082900",
            "location": "Recife, Pernambuco, Brazil",
            "date_utc_nominal": "1963-11-08T12:00:00Z",
            "actual_release_time": None,
            "source_url": SOURCE_RECIFE,
            "source_chain": "NOAA_NCEI_IGRA_RECIFE_NCDC6301",
            "pressure_hpa": pressure_hpa,
            "derived_pressure_pa": pressure_hpa * 100,
            "approx_level_height_m": LEVEL_HEIGHT_M_APPROX[pressure_hpa],
            "measured_wind_from_degrees": int(direction),
            "measured_wind_speed_m_s": int(speed),
            "derived_wind_to_east_m_s": u,
            "derived_wind_to_north_m_s": v,
        })
    if [w["pressure_hpa"] for w in observations] != [850, 700, 500, 300, 250]:
        raise ValueError("unexpected or incomplete measured wind levels in C151")
    return observations


def conditional_drift(profile: list[dict], descent_vertical_speed_m_s: float) -> dict:
    """Hypothetical constant-speed descent between sampled approximate levels.

    Assumes same horizontal wind throughout the descent as at Recife; this
    is not an interpolation from Recife to Conde or a calibrated fall model.
    """
    if not (math.isfinite(descent_vertical_speed_m_s) and
            descent_vertical_speed_m_s > 0):
        raise ValueError("positive finite assumed downward speed required")
    ascending = sorted(profile, key=lambda row: row["approx_level_height_m"])
    total_east_m = total_north_m = duration_s = 0.0
    for lo, hi in zip(ascending, ascending[1:]):
        dz = hi["approx_level_height_m"] - lo["approx_level_height_m"]
        if dz <= 0:
            raise ValueError("non-monotonic levels")
        dt = dz / descent_vertical_speed_m_s
        total_east_m += dt * (lo["derived_wind_to_east_m_s"] +
                              hi["derived_wind_to_east_m_s"]) / 2
        total_north_m += dt * (lo["derived_wind_to_north_m_s"] +
                               hi["derived_wind_to_north_m_s"]) / 2
        duration_s += dt
    return {
        "assumed_downward_speed_m_s": descent_vertical_speed_m_s,
        "sampled_altitude_range_m_approx": [ascending[0]["approx_level_height_m"],
                                             ascending[-1]["approx_level_height_m"]],
        "derived_descent_time_s": duration_s,
        "derived_east_displacement_m": total_east_m,
        "derived_north_displacement_m": total_north_m,
        "derived_horizontal_drift_m": math.hypot(total_east_m, total_north_m),
        "scope": "CONDITIONAL_RECIFE_WINDS_ALOFT_SUBDOMAIN_ONLY",
        "not_ground_displacement": True,
        "not_conde_weather": True,
        "not_norad_528_constraint": True,
    }


def build_contract(matrix_bytes: bytes, descent_vertical_speed_m_s: float) -> dict:
    winds = recife_winds(matrix_bytes)
    return {
        "schema": "conde.physical-observable-crosswalk/v1",
        "matrix_snapshot": "a7978c3a75a153b16ab70118a92c434bba674cb7",
        "orbital": orbital_observables(),
        "atmospheric_observations": winds,
        "conditional_wind_drift": conditional_drift(winds, descent_vertical_speed_m_s),
        "related_surface_synoptic_records": [
            {
                "matrix_occurrences": ["C144#1", "C145#1", "C146#1"],
                "source": "https://idem.marinha.mil.br/geonetwork/srv/api/records/9ea5e9a4-199d-4d14-8b55-682eb4daa211/attachments/Nov_1963.pdf",
                "observation_type": "SEA_LEVEL_PRESSURE_ISOBARS_1963_11_08_12_HMG",
                "independent_from_recife_station": "SEPARATE_ARCHIVE_NOT_VALIDATED_INDEPENDENT_WIND_MEASUREMENTS",
                "geostrophic_or_actual_winds_extracted": False,
            }
        ],
        "physical_observation_operators": [
            {
                "name": "n_rev_per_day_to_n_rad_per_second",
                "equation": "n_rad_s = 2*pi*n_rev_day/86400",
                "status": "EVALUATED_C179",
            },
            {
                "name": "kepler_proxy_a_and_perigee",
                "equation": "a=(mu/n_rad_s^2)^(1/3); h_perigee=a*(1-e)-R_E",
                "status": "EVALUATED_CONDITIONALLY_C179",
            },
            {
                "name": "j2_raan_rate",
                "equation": "Omega_dot=-1.5*J2*n*(R_E/(a*(1-e^2)))^2*cos(i)",
                "status": "EVALUATED_CONDITIONALLY_C179",
            },
            {
                "name": "wind_from_to_velocity_components",
                "equation": "u_east=-speed*sin(from); v_north=-speed*cos(from)",
                "status": "EVALUATED_C151_RECIFE_ONLY",
            },
            {
                "name": "air_density_from_pressure_temperature",
                "equation": "rho=p/(R_d*T)",
                "status": "NOT_RUN_NO_COLLOCATED_TEMPERATURE_IN_THIS_EXTRACT",
            },
            {
                "name": "drag_acceleration",
                "equation": "a_drag=-0.5*rho*(Cd*A/m)*abs(v_rel)*v_rel",
                "status": "NOT_RUN_UNBOUNDED_OBJECT_AND_ATMOSPHERE",
            },
            {
                "name": "terminal_fragment_drift",
                "equation": "Delta_x=integral u(z)/v_down(z) dz",
                "status": "CONDITIONAL_RECIFE_PROXY_NOT_CONDE",
            },
        ],
        "cross_location_transfer_to_conde": "NOT_VERIFIED",
        "actual_conde_wind_profile_1963_11_08": None,
        "calibrated_atmospheric_spatial_temporal_error": None,
        "reduction_of_norad528_admissible_domain": "NOT_RUN",
        "reentry_or_ground_impact_in_conde": "INDETERMINATE",
        "next_discriminating_data": [
            "collocated_Conde_or_Salvador_atmospheric_winds_with_vertical_levels_and_UTC",
            "error_model_for_spatiotemporal_transfer_from_Recife",
            "fragment_mass_Cd_area_and_descent_vertical_speed_envelope",
            "orbital_elements_multiple_epochs_with_source_error_and_frame",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=Path(MATRIX_PATH))
    parser.add_argument("--descent-vertical-speed-mps", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_contract(args.matrix.read_bytes(), args.descent_vertical_speed_mps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "source_wind_levels": len(result["atmospheric_observations"]),
        "physical_domain_reduction": result["reduction_of_norad528_admissible_domain"],
        "weather_at_conde": result["cross_location_transfer_to_conde"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
