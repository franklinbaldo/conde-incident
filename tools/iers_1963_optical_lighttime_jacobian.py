#!/usr/bin/env python3
"""G61: implicit 6D light-time Jacobian for conditional GCRS optical geometry."""
from __future__ import annotations

import numpy as np

from iers_1963_optical import station_itrs_km
from iers_1963_optical_lighttime import (
    SPEED_OF_LIGHT_KM_S, constant_velocity_light_time, sensitivity_from_teme,
)
from iers_1963_teme import (
    _validated_vector, matrices_at, transform_covariance, transform_state,
)


def linearized_retarded_direction(
    position_gcrs_km: object,
    velocity_gcrs_km_s: object,
    station_gcrs_km: object,
    covariance_gcrs6d: object | None = None,
) -> dict:
    """Differentiate the implicit retarded ray, with no instrument covariance.

    For p=r-v*tau-s, n=p/|p|, c*tau=|p|, the exact linearization is
    dtau = n.(dr-tau*dv)/(c+n.v). Units: r km, v km/s, tau seconds.
    """
    r = _validated_vector(position_gcrs_km, "GCRS r (km)")
    v = _validated_vector(velocity_gcrs_km_s, "GCRS v (km/s)")
    s = _validated_vector(station_gcrs_km, "GCRS station (km)")
    result = constant_velocity_light_time(r, v, s)
    n = np.asarray(result["retarded_line_of_sight_gcrs"])
    tau = float(result["light_time_s"])
    rho = float(result["retarded_range_km"])
    denominator = SPEED_OF_LIGHT_KM_S + float(n @ v)
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError("Invalid light-time differentiation denominator")
    dtau = np.concatenate((n, -tau*n)) / denominator
    p_r = np.eye(3) - np.outer(v, n) / denominator
    p_v = -tau*np.eye(3) + tau*np.outer(v, n) / denominator
    direction_jac = ((np.eye(3)-np.outer(n,n)) @
                     np.hstack((p_r,p_v))) / rho
    # A nonsingular tangent basis, NOT FK4, RA/Dec or detector east/north.
    seed = np.eye(3)[int(np.argmin(np.abs(n)))]
    first = np.cross(seed, n)
    first /= np.linalg.norm(first)
    basis = np.vstack((first, np.cross(n, first)))
    h = basis @ direction_jac
    if not np.isfinite(h).all() or not np.isfinite(dtau).all():
        raise ValueError("Nonfinite retarded state derivative")
    cov2 = None
    if covariance_gcrs6d is not None:
        cov = np.asarray(transform_covariance(covariance_gcrs6d, np.eye(6)))
        cov2_raw = h @ cov @ h.T
        if not np.isfinite(cov2_raw).all():
            raise ValueError("Nonfinite retarded covariance")
        cov2 = ((cov2_raw + cov2_raw.T)/2).tolist()
    return {
        **result,
        "model": "G61_IMPLICIT_LIGHTTIME_6D_LINEARIZATION",
        "light_time_derivative_s_per_gcrs_state6d": dtau.tolist(),
        "retarded_unit_jacobian_per_gcrs_state6d": direction_jac.tolist(),
        "retarded_tangent_basis_gcrs": basis.tolist(),
        "retarded_tangent_jacobian_rad_per_gcrs_state6d": h.tolist(),
        "retarded_state_only_angular_covariance_rad2": cov2,
        "covariance_class": "CALLER_DECLARED_STATE_ONLY_NOT_INSTRUMENT_SIGMA",
        "historical_holdout": "NOT_RUN",
        "historical_impact_inference": None,
    }


def linearized_retarded_from_teme(
    original_iers_bytes: bytes, eop: dict, times: dict, utc: str,
    teme_position_km: object, teme_velocity_km_s: object,
    station_lon_deg: float, station_lat_deg: float, station_height_m: float,
    teme_covariance6d: object,
) -> dict:
    """Validate source/occultation and transport TEME covariance via full G50 J."""
    geometric = sensitivity_from_teme(
        original_iers_bytes, eop, times, utc,
        teme_position_km, teme_velocity_km_s,
        station_lon_deg, station_lat_deg, station_height_m,
    )
    state = transform_state(
        original_iers_bytes, eop, times, utc,
        teme_position_km, teme_velocity_km_s, target="GCRS",
    )
    j_frame = np.asarray(state["jacobian_6d"])
    cov_gcrs = transform_covariance(teme_covariance6d, j_frame)
    site = station_itrs_km(station_lon_deg, station_lat_deg, station_height_m)
    matrix = matrices_at(utc, eop, times)["gcrs_to_itrs"]
    observer = matrix.T @ site
    out = linearized_retarded_direction(
        state["position_km"], state["velocity_km_s"], observer, cov_gcrs,
    )
    j_gcrs = np.asarray(out["retarded_tangent_jacobian_rad_per_gcrs_state6d"])
    return {
        **geometric,
        "light_time_derivative_s_per_gcrs_state6d":
            out["light_time_derivative_s_per_gcrs_state6d"],
        "retarded_tangent_basis_gcrs": out["retarded_tangent_basis_gcrs"],
        "retarded_tangent_jacobian_rad_per_gcrs_state6d": j_gcrs.tolist(),
        "retarded_tangent_jacobian_rad_per_teme_state6d":
            (j_gcrs @ j_frame).tolist(),
        "retarded_state_only_angular_covariance_rad2":
            out["retarded_state_only_angular_covariance_rad2"],
        "covariance_class": out["covariance_class"],
        "source_state_class": "CALLER_SUPPLIED_NOT_INSTRUMENTALLY_AUTHENTICATED",
        "historical_holdout": "NOT_RUN",
        "historical_impact_inference": None,
    }
