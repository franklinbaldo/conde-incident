#!/usr/bin/env python3
"""G62: conditional simultaneous differential parallax with shared state error.

Two stations view ONE reception-epoch GCRS 6D state. Its covariance is a
common latent error, so per-station angular covariance blocks are correlated.
Subtract the retarded unit directions in a FROZEN common tangent basis, and
apply (H_a - H_b) Sigma (H_a - H_b)^T. This must NOT be interpreted as a
historical likelihood: station, clock, film, atmosphere and instrument errors
are absent; no independent NORAD 528 measurement is asserted.
"""
from __future__ import annotations

import numpy as np

from iers_1963_optical_lighttime_jacobian import linearized_retarded_direction
from iers_1963_teme import _validated_vector, transform_covariance


def differential_retarded_parallax(
    position_gcrs_km: object,
    velocity_gcrs_km_s: object,
    station_a_gcrs_km: object,
    station_b_gcrs_km: object,
    shared_state_covariance_gcrs6d: object,
) -> dict:
    """Linearized sky-plane A−B difference and correlated state covariance.

    All positions and the velocity refer to the SAME GCRS reception epoch.
    The tangent basis is selected using A's nominal retarded direction and
    then held fixed under perturbations, so derivatives do not differentiate
    the arbitrary tangent basis. Covariance units follow the supplied 6D
    state: positions in km, velocities in km/s, cross units respected.
    """
    r = _validated_vector(position_gcrs_km, 'GCRS position (km)')
    v = _validated_vector(velocity_gcrs_km_s, 'GCRS velocity (km/s)')
    sa = _validated_vector(station_a_gcrs_km, 'GCRS station A (km)')
    sb = _validated_vector(station_b_gcrs_km, 'GCRS station B (km)')
    if np.array_equal(sa, sb):
        raise ValueError('Distinct receiver positions required for parallax')
    cov = np.asarray(transform_covariance(
        shared_state_covariance_gcrs6d, np.eye(6)), dtype=float)
    a = linearized_retarded_direction(r, v, sa)
    b = linearized_retarded_direction(r, v, sb)
    basis = np.asarray(a['retarded_tangent_basis_gcrs'], dtype=float)
    na = np.asarray(a['retarded_line_of_sight_gcrs'], dtype=float)
    nb = np.asarray(b['retarded_line_of_sight_gcrs'], dtype=float)
    ja = basis @ np.asarray(a['retarded_unit_jacobian_per_gcrs_state6d'])
    jb = basis @ np.asarray(b['retarded_unit_jacobian_per_gcrs_state6d'])
    jd = ja - jb
    joint = np.vstack([ja, jb]) @ cov @ np.vstack([ja, jb]).T
    cross = joint[:2, 2:]
    shared = jd @ cov @ jd.T
    # This counterfactual is intentionally provided so that double-counting
    # of the SAME orbital-state covariance can be detected in downstream code.
    false_independent = joint[:2, :2] + joint[2:, 2:]
    missing_cross = cross + cross.T
    if not all(np.isfinite(x).all() for x in
               (joint, shared, false_independent, missing_cross)):
        raise ValueError('Nonfinite joint angular state covariance')
    return {
        'model': 'G62_SAME_EPOCH_SHARED_STATE_DIFFERENTIAL_RETARDED_PARALLAX',
        'units': 'GCRS km; km/s; radians and rad^2',
        'common_tangent_basis_gcrs': basis.tolist(),
        'nominal_direction_difference_rad_linearized': (basis @ (na-nb)).tolist(),
        'differential_jacobian_rad_per_gcrs_state6d': jd.tolist(),
        'joint_marginals_and_cross_covariance_rad2': joint.tolist(),
        'shared_state_differential_covariance_rad2':
            ((shared + shared.T)/2).tolist(),
        'independent_marginals_counterfactual_covariance_rad2':
            ((false_independent + false_independent.T)/2).tolist(),
        'cross_terms_omitted_by_independence_rad2': missing_cross.tolist(),
        'light_time_a_s': a['light_time_s'],
        'light_time_b_s': b['light_time_s'],
        'covariance_scope': 'SAME_ORBITAL_STATE_ONLY_NOT_SENSOR_CLOCK_OR_STATION',
        'station_survey_1963': 'NOT_AUTHENTICATED',
        'historical_optical_measurements': 'NOT_AUTHENTICATED',
        'historical_holdout': 'NOT_RUN',
        'theta_528': 'UNCHANGED',
    }
