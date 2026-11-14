#!/usr/bin/env python3
"""G60: conditional finite-light-time sensitivity, not historical optical astrometry.

For a reception-epoch GCRS state (r,v), hold the station position fixed at
reception and extrapolate satellite position linearly backward by tau. Solve
c*tau=|r-v*tau-s| analytically. This is a sensitivity test, NOT a propagator:
it omits gravity over tau, station motion along photon path, relativity,
atmospheric refraction, aberration, ephemeris error, and 1963 sensor calibration.
"""
from __future__ import annotations

import math

import numpy as np

from iers_1963_optical import (
    _require_clear_wgs84_sightline, forward_optical, station_itrs_km,
)
from iers_1963_teme import _validated_vector, matrices_at, transform_state

SPEED_OF_LIGHT_KM_S = 299792.458
ARCSEC_PER_RAD = 180.0 * 3600.0 / math.pi


def constant_velocity_light_time(
    target_reception_gcrs_km: object,
    target_velocity_gcrs_km_s: object,
    station_reception_gcrs_km: object,
) -> dict:
    """Return unique positive tau and geometric-versus-retarded angular offset.

    Uses the cancellation-resistant positive-root form
    tau=range / (v_rad + sqrt(c*c - v*v + v_rad*v_rad)).
    All coordinates must be same reception epoch and GCRS. The station is
    fixed ONLY within the diagnostic and is NOT a historically surveyed site.
    """
    r = _validated_vector(target_reception_gcrs_km, "target GCRS r (km)")
    v = _validated_vector(target_velocity_gcrs_km_s, "target GCRS v (km/s)")
    s = _validated_vector(station_reception_gcrs_km, "station GCRS r (km)")
    if float(v @ v) >= SPEED_OF_LIGHT_KM_S**2:
        raise ValueError("Sub-luminal state required for diagnostic")
    rho = r - s
    rng = float(np.linalg.norm(rho))
    if not math.isfinite(rng) or rng <= 1e-6:
        raise ValueError("Degenerate topocentric range")
    rad_speed = float(rho @ v) / rng
    discriminant = SPEED_OF_LIGHT_KM_S**2 - float(v @ v) + rad_speed**2
    tau = rng / (rad_speed + math.sqrt(discriminant))
    if not math.isfinite(tau) or tau <= 0:
        raise ValueError("Invalid light-time solution")
    emission = r - v * tau
    photon = emission - s
    photon_range = float(np.linalg.norm(photon))
    # Equational residual, not calibrated astrometric uncertainty.
    equation_residual_km = photon_range - SPEED_OF_LIGHT_KM_S * tau
    unit_geo = rho / rng
    unit_ret = photon / photon_range
    cross = np.cross(unit_geo, unit_ret)
    offset_rad = math.atan2(float(np.linalg.norm(cross)),
                            float(unit_geo @ unit_ret))
    # Stable tangent basis even when the geometric direction is polar.
    index = int(np.argmin(np.abs(unit_geo)))
    seed = np.eye(3)[index]
    east = np.cross(seed, unit_geo)
    east /= np.linalg.norm(east)
    north = np.cross(unit_geo, east)
    return {
        "model": "G60_CONSTANT_GCRS_VELOCITY_RECEPTION_STATION_FIXED",
        "reception_range_km": rng,
        "light_time_s": tau,
        "emission_position_gcrs_km": emission.tolist(),
        "retarded_range_km": photon_range,
        "light_time_equation_residual_km": equation_residual_km,
        "geometric_to_retarded_angle_arcsec": offset_rad * ARCSEC_PER_RAD,
        "tangent_offset_rad": [float(unit_ret @ east), float(unit_ret @ north)],
        "geometric_line_of_sight_gcrs": unit_geo.tolist(),
        "retarded_line_of_sight_gcrs": unit_ret.tolist(),
        "evidence_class": "CONDITIONAL_NUMERICAL_SENSITIVITY_ONLY",
        "historical_holdout": "NOT_RUN",
        "historical_impact_inference": None,
    }



def quadratic_central_gravity_light_time(
    reception_position_gcrs_km: object,
    reception_velocity_gcrs_km_s: object,
    station_reception_gcrs_km: object,
    gm_km3_s2: float = 398600.4418,
) -> dict:
    """G63: second-order central-acceleration sensitivity to G60's omission.

    Local Taylor expansion r(t_rec-tau) ~= r-v*tau+a_rec*tau**2/2,
    a_rec=-GM*r/|r|**3. This is NOT an orbit propagation, measurement,
    historically calibrated error or a bound on unmodelled perturbations.
    Reception station is fixed as in G60; only short light times allowed.
    """
    r = _validated_vector(reception_position_gcrs_km, "GCRS r (km)")
    v = _validated_vector(reception_velocity_gcrs_km_s, "GCRS v (km/s)")
    s = _validated_vector(station_reception_gcrs_km, "GCRS station (km)")
    gm = float(gm_km3_s2)
    if not math.isfinite(gm) or gm < 0:
        raise ValueError("Finite nonnegative central GM required")
    radial_norm = float(np.linalg.norm(r))
    if radial_norm < 6350. or not math.isfinite(radial_norm):
        raise ValueError("Outside-Earth reception state required")
    if float(np.linalg.norm(v)) > 20.:
        raise ValueError("Near-Earth state speed must not exceed 20 km/s")
    linear = constant_velocity_light_time(r, v, s)
    tau_linear = float(linear["light_time_s"])
    if tau_linear > 0.2:
        raise ValueError("Local Taylor diagnostic requires light time <= 0.2 s")
    acceleration = -gm * r / radial_norm**3
    tau = tau_linear
    for _ in range(24):
        photon = r - v*tau + .5*acceleration*tau*tau - s
        next_tau = float(np.linalg.norm(photon)) / SPEED_OF_LIGHT_KM_S
        if not math.isfinite(next_tau) or next_tau <= 0 or next_tau > 0.2:
            raise ValueError("Invalid quadratic light-time iterate")
        if abs(next_tau - tau) <= 1e-14:
            tau = next_tau
            break
        tau = next_tau
    else:
        raise ValueError("Quadratic light-time iteration did not converge")
    photon = r - v*tau + .5*acceleration*tau*tau - s
    distance = float(np.linalg.norm(photon))
    residual = distance - SPEED_OF_LIGHT_KM_S*tau
    if abs(residual) > 1e-8:
        raise ValueError("Quadratic light-time residual exceeds 10 micrometres")
    linear_ray = np.asarray(linear["retarded_line_of_sight_gcrs"])
    quadratic_ray = photon / distance
    angle = math.atan2(float(np.linalg.norm(np.cross(linear_ray, quadratic_ray))),
                       float(linear_ray @ quadratic_ray))
    displacement_m = 500. * float(np.linalg.norm(acceleration)) * tau*tau
    return {
        "model": "G63_RECEPTION_CENTRAL_ACCELERATION_SECOND_ORDER_DIAGNOSTIC",
        "gm_km3_s2": gm,
        "reception_central_acceleration_km_s2": acceleration.tolist(),
        "constant_velocity_light_time_s": tau_linear,
        "quadratic_light_time_s": tau,
        "quadratic_light_time_equation_residual_km": residual,
        "second_order_acceleration_displacement_m": displacement_m,
        "quadratic_retarded_line_of_sight_gcrs": quadratic_ray.tolist(),
        "quadratic_vs_linear_angle_arcsec": angle * ARCSEC_PER_RAD,
        "limitations": [
            "RECEPTION_CENTRAL_ACCELERATION_ONLY", "NO_J2_OR_DRAG_OVER_LIGHT_TIME",
            "STATION_FIXED_AT_RECEPTION", "NO_RELATIVITY_OR_ABERRATION",
            "NO_1963_OBSERVATION_OR_INSTRUMENT_SIGMA",
        ],
        "evidence_class": "SYNTHETIC_LOCAL_TAYLOR_SENSITIVITY_ONLY",
        "historical_holdout": "NOT_RUN",
        "historical_impact_inference": None,
    }


def sensitivity_from_teme(
    original_iers_bytes: bytes, eop: dict, times: dict, utc: str,
    teme_position_km: object, teme_velocity_km_s: object,
    station_lon_deg: float, station_lat_deg: float, station_height_m: float,
) -> dict:
    """Bind G60 to G50/G53 frame, Earth occultation, and original IERS bytes.

    TEME 6D source is *caller-supplied scenario*, not historical tracking
    or independently authenticated NORAD measurement.
    """
    # G53 validates the original IERS source, coordinate epoch and the
    # reception-epoch solid-Earth occultation of the instantaneous ray.
    geometric = forward_optical(
        original_iers_bytes, eop, times, utc, teme_position_km,
        station_lon_deg, station_lat_deg, station_height_m,
    )
    state = transform_state(
        original_iers_bytes, eop, times, utc, teme_position_km,
        teme_velocity_km_s, target="GCRS",
    )
    m = matrices_at(utc, eop, times)
    site_itrs = station_itrs_km(station_lon_deg, station_lat_deg, station_height_m)
    site_gcrs = m["gcrs_to_itrs"].T @ site_itrs
    result = constant_velocity_light_time(
        state["position_km"], state["velocity_km_s"], site_gcrs,
    )
    # A retarded ray must also avoid the reference ellipsoid at reception.
    emitted_itrs_at_reception = m["gcrs_to_itrs"] @ np.asarray(
        result["emission_position_gcrs_km"])
    _require_clear_wgs84_sightline(site_itrs, emitted_itrs_at_reception)
    return {
        **result,
        "reception_epoch_utc": utc,
        "source_frame": "TEME",
        "output_frame": "GCRS",
        "instantaneous_geometric_range_km": geometric["range_km"],
        "earth_occultation": "CLEAR_AT_RECEPTION_AND_RETARDED_POSITION_WGS84",
        "earth_orientation": "IERS_RETROSPECTIVE_SOURCE_BYTES_AUTHENTICATED",
        "source_state_class": "CALLER_SUPPLIED_NOT_INSTRUMENTALLY_AUTHENTICATED",
        "model_omissions": [
            "ORBITAL_ACCELERATION_OVER_LIGHT_TIME", "EARTH_MOTION_ALONG_PHOTON",
            "ABERRATION", "RELATIVITY", "REFRACTION", "FK4_B1950",
            "STATION_SURVEY_1963", "CLOCK_CALIBRATION",
        ],
    }
