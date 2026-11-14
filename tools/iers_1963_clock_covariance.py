#!/usr/bin/env python3
"""G64: clock-only joint angular uncertainty from two correlated clocks.

Rates refer to the SAME fixed GCRS tangent plane and must come from a complete
time-varying optical forward model. Units: rad/s, s², rad². No historical data.
"""
from __future__ import annotations

import math
import numpy as np


def _vector(value, name):
    if isinstance(value, (bool, np.bool_)) or (
        isinstance(value, (list, tuple, np.ndarray)) and
        np.asarray(value).dtype.kind == "b"
    ):
        raise ValueError(f"{name}: boolean is not an angular rate")
    try:
        x = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}: expected two finite rates (rad/s)") from exc
    if x.shape != (2,) or not np.isfinite(x).all():
        raise ValueError(f"{name}: expected two finite rates (rad/s)")
    return x


def _covariance(value):
    if isinstance(value, (list, tuple, np.ndarray)) and (
        np.asarray(value).dtype.kind == "b"
    ):
        raise ValueError("Boolean is not a clock covariance")
    try:
        c = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Expected 2x2 clock covariance in s²") from exc
    if c.shape != (2, 2) or not np.isfinite(c).all():
        raise ValueError("Expected finite 2x2 clock covariance in s²")
    if c[0, 0] < 0 or c[1, 1] < 0:
        raise ValueError("Negative clock variance")
    # Compare each off-diagonal pair in its OWN scale. A huge diagonal
    # must not hide asymmetry in a tiny cross covariance (G52 regression).
    offdiag_scale = max(abs(float(c[0, 1])), abs(float(c[1, 0])))
    if (abs(float(c[0, 1] - c[1, 0])) >
            64*np.finfo(float).eps*offdiag_scale):
        raise ValueError("Asymmetric clock covariance")
    c = (c+c.T)/2
    if c[0, 0] == 0 or c[1, 1] == 0:
        if c[0, 1] != 0:
            raise ValueError("Nonzero cross term with zero clock variance")
        rho = None
    else:
        rho = float((c[0, 1] / math.sqrt(float(c[0, 0]))) /
                    math.sqrt(float(c[1, 1])))
        if not math.isfinite(rho) or abs(rho) > 1:
            raise ValueError("Clock correlation not positive semidefinite")
    return c, rho


def paired_clock_covariance(rate_a_rad_s, rate_b_rad_s,
                            clock_covariance_s2=None):
    """Transport declared 2x2 clock errors to both rays and their difference.

    The 4D angular vector is (east_A,north_A,east_B,north_B). D=[I,-I].
    This is clock-only; combining with orbit/instrument errors requires their
    cross-covariance, not an assumed independent sum.
    """
    a = _vector(rate_a_rad_s, "A")
    b = _vector(rate_b_rad_s, "B")
    out = {
        "model": "G64_PAIRED_CLOCK_LINEAR_COVARIANCE",
        "units": "rad/s; s2; rad2",
        "basis": "SAME_FIXED_GCRS_TANGENT_BASIS_REQUIRED",
        "calibration": ("MISSING" if clock_covariance_s2 is None
                        else "CALLER_DECLARED_UNAUTHENTICATED"),
        "clock_only_joint_covariance_rad2": None,
        "clock_only_difference_covariance_rad2": None,
        "combined_state_instrument_clock_covariance_rad2": None,
        "clock_correlation": None,
        "historical_holdout": "NOT_RUN",
        "historical_impact_inference": None,
        "limitations": [
            "LINEAR_TIMING_APPROXIMATION",
            "FULL_FORWARD_MODEL_ANGULAR_RATES_REQUIRED",
            "CLOCK_STATE_INSTRUMENT_CROSS_COVARIANCE_UNSPECIFIED",
            "NO_1963_INSTRUMENTAL_CALIBRATION",
        ],
    }
    if clock_covariance_s2 is None:
        return out
    c, rho = _covariance(clock_covariance_s2)
    j = np.zeros((4, 2))
    j[:2, 0] = a
    j[2:, 1] = b
    d = np.hstack((np.eye(2), -np.eye(2)))
    # G65: D @ (J C J.T) @ D.T subtracts nearly equal variances.
    # With a perfectly shared clock and rates differing by 1e-9 it can
    # falsely report *zero* uncertainty. Use a PSD factor instead.
    # For sigma_A and sigma_B, let B = rho*z0 + sqrt(1-rho²)*z1.
    # Then delta = (sigma_A*a-rho*sigma_B*b)*z0
    #              -sqrt(1-rho²)*sigma_B*b*z1.
    correlation = 0.0 if rho is None else rho
    with np.errstate(over="ignore", invalid="ignore"):
        joint = j @ c @ j.T
        scale_a = math.sqrt(float(c[0, 0]))
        scale_b = math.sqrt(float(c[1, 1]))
        scaled_b = scale_b * b
        # Avoid another subtraction of close numbers when rates nearly
        # coincide (rho=+1) or oppose each other (rho=-1).
        if correlation >= 0:
            shared = (scale_a * (a-b) +
                      ((scale_a-scale_b) + (1.0-correlation)*scale_b) * b)
        else:
            shared = (scale_a * (a+b) +
                      ((scale_b-scale_a) - (1.0+correlation)*scale_b) * b)
        residual = math.sqrt(max(0.0, (1.0-correlation)*(1.0+correlation))) * scaled_b
        difference = np.outer(shared, shared) + np.outer(residual, residual)
        symmetric_joint = 0.5 * joint + 0.5 * joint.T
    if not (np.isfinite(symmetric_joint).all() and
            np.isfinite(difference).all()):
        raise ValueError("Clock covariance propagation overflow")
    out["clock_only_joint_covariance_rad2"] = symmetric_joint.tolist()
    out["clock_only_difference_covariance_rad2"] = difference.tolist()
    out["clock_correlation"] = rho
    return out

