#!/usr/bin/env python3
"""G50: source-bound Vallado-style TEME/ITRS/GCRS kinematics for 1963.

Model-defined, retrospective frame conversion only. The input TEME state is
synthetic or explicitly supplied; no historical NORAD measurement is inferred.
In particular, the IAU2000A GCRS->ITRS matrix is NOT a TEME->ITRS matrix.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
import math
from pathlib import Path

import erfa
import numpy as np

from iers_1963_frame import AS2RAD, EOP, TIME
from iers_1963_intraday import checked_source, fractional_mjd, interpolate_at

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STEP_SECONDS = 1.0


def _validated_vector(values: object, name: str) -> np.ndarray:
    try:
        out = np.asarray(values, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be three finite numbers") from exc
    if out.shape != (3,) or not np.isfinite(out).all():
        raise ValueError(f"{name} must be three finite numbers")
    return out


def _canonical_shift(utc: str, seconds: float) -> str:
    fractional_mjd(utc)
    # Do not round a requested derivative step or silently change the UTC scale.
    if not math.isfinite(seconds) or seconds <= 0 or seconds > 10:
        raise ValueError("Central difference step must be within (0,10] s")
    epoch = datetime.fromisoformat(utc.replace("Z", "+00:00"))
    shifted = epoch + timedelta(seconds=seconds)
    return shifted.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _rotation_z_passive(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    # Active rotation with -theta, TEME -> pseudo-Earth-fixed (PEF).
    return np.array([[c, s, 0.], [-s, c, 0.], [0., 0., 1.]])


def matrices_at(utc: str, eop: dict, times: dict) -> dict[str, np.ndarray | float]:
    """Vallado TEME->ITRS via UT1 GMST82, then compose GCRS via G49.

    The polar-motion matrix uses the SOFA s' convention, consistent with the
    IAU2000A GCRS->ITRS branch. Its historical choice remains model-dependent.
    All input EOP values come from the authenticated G46/G47 ledgers.
    """
    row = interpolate_at(utc, eop, times)
    utc_mjd = row["mjd_utc"]
    ut1_mjd = utc_mjd + row["ut1_minus_utc_s"] / 86400.
    tt_mjd = utc_mjd + row["tt_minus_utc_s"] / 86400.
    theta = float(erfa.gmst82(2400000.5, ut1_mjd))
    sp = float(erfa.sp00(2400000.5, tt_mjd))
    polar = erfa.pom00(row["x_arcsec"] * AS2RAD,
                       row["y_arcsec"] * AS2RAD, sp)
    teme_to_itrs = polar @ _rotation_z_passive(theta)
    gcrs_to_itrs = np.asarray(row["gcrs_to_itrs"])
    teme_to_gcrs = gcrs_to_itrs.T @ teme_to_itrs
    for m in (teme_to_itrs, teme_to_gcrs):
        if not np.isfinite(m).all() or np.max(np.abs(m.T @ m - np.eye(3))) > 1e-12:
            raise ValueError("Invalid frame matrix")
    return {"teme_to_itrs": teme_to_itrs, "teme_to_gcrs": teme_to_gcrs,
            "gcrs_to_itrs": gcrs_to_itrs, "gmst82_rad": theta,
            "polar_sp_rad": sp}


def frame_operator(utc: str, eop: dict, times: dict,
                   target: str = "ITRS", step_seconds: float = DEFAULT_STEP_SECONDS
                   ) -> tuple[np.ndarray, np.ndarray]:
    """Return R(t) and time derivative Rdot(t), with a real epoch derivative.

    Only strictly interior epochs are supported: the central difference
    must remain within the G49 bracket [Nov 7, Nov 9]. Units are 1/s.
    """
    if target not in ("ITRS", "GCRS"):
        raise ValueError("Target frame must be ITRS or GCRS")
    later = _canonical_shift(utc, step_seconds)
    # Validate and subtract without treating negative dt as a new tolerance.
    epoch = datetime.fromisoformat(utc[:-1] + "+00:00")
    earlier = (epoch - timedelta(seconds=step_seconds)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    fractional_mjd(earlier)
    fractional_mjd(later)
    key = "teme_to_" + target.lower()
    mid = matrices_at(utc, eop, times)[key]
    before = matrices_at(earlier, eop, times)[key]
    after = matrices_at(later, eop, times)[key]
    derivative = (after - before) / (2 * step_seconds)
    # Rotation derivatives must be tangent to SO(3).
    tangent = mid.T @ derivative
    if np.max(np.abs(tangent + tangent.T)) > 1e-7:
        raise ValueError("Non-tangential rotation derivative")
    return mid, derivative


def transform_state(source: bytes, eop: dict, times: dict, utc: str,
                    position_km: object, velocity_km_s: object,
                    target: str = "ITRS", step_seconds: float = DEFAULT_STEP_SECONDS
                    ) -> dict:
    """TEME state at UTC -> target state; fail closed on unauthenticated EOP."""
    checked_source(source, eop, times)
    pos = _validated_vector(position_km, "TEME position (km)")
    vel = _validated_vector(velocity_km_s, "TEME velocity (km/s)")
    rotation, rate = frame_operator(utc, eop, times, target, step_seconds)
    r = rotation @ pos
    v = rotation @ vel + rate @ pos
    if not np.isfinite(r).all() or not np.isfinite(v).all():
        raise ValueError("Non-finite output")
    return {"utc": utc, "source_frame": "TEME", "target_frame": target,
            "position_km": r.tolist(), "velocity_km_s": v.tolist(),
            "rotation": rotation.tolist(), "rotation_derivative_per_s": rate.tolist(),
            "jacobian_6d": jacobian_6d(rotation, rate).tolist(),
            "source_sha256_authenticated": True,
            "historical_observation_527_529": "NOT_AVAILABLE",
            "historical_holdout_527_529": "NOT_RUN",
            "impact": None}


def jacobian_6d(rotation: np.ndarray, rate: np.ndarray) -> np.ndarray:
    """6D coordinate transport: J = [[R, 0], [Rdot, R]]."""
    out = np.zeros((6, 6), dtype=float)
    out[:3, :3], out[3:, :3], out[3:, 3:] = rotation, rate, rotation
    return out


def transform_covariance(covariance: object, jacobian: object) -> list[list[float]]:
    """Propagate already specified 6x6 covariance, not a calibrated sigma."""
    try:
        cov = np.asarray(covariance, dtype=float)
        jac = np.asarray(jacobian, dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Invalid covariance or Jacobian") from exc
    if cov.shape != (6, 6) or jac.shape != (6, 6):
        raise ValueError("Covariance and Jacobian must both be 6x6")
    if not (np.isfinite(cov).all() and np.isfinite(jac).all()):
        raise ValueError("Covariance and Jacobian must be finite")
    if np.max(np.abs(cov - cov.T)) > 1e-10 * max(1, np.max(np.abs(cov))):
        raise ValueError("Covariance must be symmetric")
    # Eigenvalues checked in physically scaled units: [km, km/s * 1 s].
    if np.linalg.eigvalsh(cov).min() < -1e-11 * max(1., np.linalg.norm(cov, ord=2)):
        raise ValueError("Covariance must be positive semidefinite")
    out = jac @ cov @ jac.T
    return ((out + out.T) / 2).tolist()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="Complete, original IERS 1963 archive, not just its SHA label")
    parser.add_argument("--eop", type=Path, default=ROOT / EOP)
    parser.add_argument("--times", type=Path, default=ROOT / TIME)
    parser.add_argument("--utc", default="1963-11-08T12:00:00Z")
    parser.add_argument("--target", choices=("ITRS", "GCRS"), default="ITRS")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    eop = json.loads(args.eop.read_text())
    times = json.loads(args.times.read_text())
    out = transform_state(args.source.read_bytes(), eop, times, args.utc,
                          [7000., 0., 0.], [0., 7.5, 0.], args.target)
    if args.check:
        print("PASS: SHA-pinned EOP, TEME->" + args.target +
              " position, derivative-aware velocity and 6D Jacobian (synthetic)")
    else:
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

