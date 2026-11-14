#!/usr/bin/env python3
"""Authenticated, explicitly conditional intra-day IERS/ERFA frame for Nov 1963.

The pinned annual IERS source must be supplied: a JSON SHA label alone is
not authentication. Linear interpolation is a numerical convention, not
an instrumental observation or a calibrated uncertainty.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
from pathlib import Path
import re

from iers_1963_eop import SHA256, receipt
from iers_1963_frame import EOP, TIME, AS2RAD, orthogonality_error, validate_input
from iers_1963_timescales import (REFERENCE_MJD, REFERENCE_OFFSET_S,
                                  UTC_RATE_S_PER_DAY, TT_MINUS_TAI_S, build as times_build)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("research/constraints/iers_1963_intraday_G49.json")
BASE = datetime(1963, 11, 7, tzinfo=timezone.utc)
DAY_S = Decimal("86400")
EPOCHS = (
    "1963-11-07T00:00:00Z", "1963-11-07T06:00:00Z",
    "1963-11-07T12:00:00Z", "1963-11-07T18:00:00Z",
    "1963-11-08T00:00:00Z", "1963-11-08T06:00:00Z",
    "1963-11-08T12:00:00Z", "1963-11-08T18:00:00Z",
    "1963-11-09T00:00:00Z",
)
UTC_FORMAT = re.compile(r"1963-11-(?:07|08|09)T\d\d:\d\d:\d\d(?:\.\d{1,6})?Z\Z")


def checked_source(source: bytes, eop: dict, times: dict) -> None:
    """Authenticate ALL numeric cells, not merely their advertised SHA label."""
    if receipt(source) != eop:
        raise ValueError("G46 ledger differs from SHA-pinned 365-row IERS archive")
    if times_build(source) != times:
        raise ValueError("G47 timescale ledger differs from SHA-pinned IERS archive")
    validate_input(eop, times)


def fractional_mjd(utc: str) -> Decimal:
    if not isinstance(utc, str) or not UTC_FORMAT.fullmatch(utc):
        raise ValueError("Only canonical UTC in the documented Nov 7-9 1963 span")
    try:
        instant = datetime.fromisoformat(utc[:-1] + "+00:00")
    except ValueError as error:
        raise ValueError("Invalid UTC") from error
    delta = instant - BASE
    us = (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds
    if not 0 <= us <= 172800_000000:
        raise ValueError("UTC outside bracketed IERS samples")
    return Decimal(38340) + Decimal(us) / Decimal(86_400_000_000)


def interpolate_at(utc: str, eop: dict, times: dict) -> dict:
    """Interpolate authenticated ledgers; caller MUST run checked_source first."""
    import erfa

    mjd = fractional_mjd(utc)
    offset = mjd - Decimal(38340)
    i = min(int(offset), 1)
    t = offset - Decimal(i)
    a, b = eop["sample"][i:i + 2]
    ta, tb = times["rows_at_00_utc"][i:i + 2]
    if b["mjd"] - a["mjd"] != 1:
        raise ValueError("Nonadjacent UTC bracket")

    def linear(left: float, right: float) -> float:
        return float(Decimal(str(left)) +
                     t * (Decimal(str(right)) - Decimal(str(left))))

    # Interpolate UT1-TAI (continuous atomic scale), then recover UT1-UTC
    # using the pre-1972 linear rate. Do NOT infer LOD from DUT1 alone.
    tai_utc = REFERENCE_OFFSET_S + (mjd - REFERENCE_MJD) * UTC_RATE_S_PER_DAY
    u1 = Decimal(str(a["ut1_minus_utc_s"])) - Decimal(str(ta["tai_minus_utc_s"]))
    u2 = Decimal(str(b["ut1_minus_utc_s"])) - Decimal(str(tb["tai_minus_utc_s"]))
    ut1_tai = u1 + t * (u2 - u1)
    dut1 = ut1_tai + tai_utc
    tt_utc = tai_utc + TT_MINUS_TAI_S
    xp = linear(a["x_arcsec"], b["x_arcsec"])
    yp = linear(a["y_arcsec"], b["y_arcsec"])
    lod = linear(a["lod_s"], b["lod_s"])
    # Two-part MJD Julian dates retain sub-second rotation precision.
    # Keep the fractional day in its own SOFA JD part: adding it to a
    # 38,000-day MJD float loses sub-microsecond temporal precision.  That
    # jitter is amplified when G50 differentiates the frame for velocity.
    mjd_day = int(mjd)
    fraction = mjd - Decimal(mjd_day)
    matrix = erfa.c2t00a(
        2400000.5 + mjd_day, float(fraction + tt_utc / DAY_S),
        2400000.5 + mjd_day, float(fraction + dut1 / DAY_S),
        xp * AS2RAD, yp * AS2RAD,
    ).tolist()
    residual = orthogonality_error(matrix)
    if not math.isfinite(residual) or residual > 1e-12:
        raise ValueError("Nonorthogonal Earth rotation")
    return {
        "utc": utc,
        "mjd_utc": float(mjd),
        "bracket_utc": [a["utc"], b["utc"]],
        "linear_fraction": float(t),
        "interpolation": "LINEAR_UT1_MINUS_TAI_AND_POLAR_MOTION_CONDITIONAL",
        "x_arcsec": xp, "y_arcsec": yp, "lod_s_diagnostic_only": lod,
        "ut1_minus_utc_s": float(dut1),
        "ut1_minus_tai_s": float(ut1_tai),
        "tai_minus_utc_s": float(tai_utc),
        "tt_minus_utc_s": float(tt_utc),
        "gcrs_to_itrs": matrix,
        "itrs_x_axis_in_gcrs": matrix[0],
        "itrs_pole_axis_in_gcrs": matrix[2],
        "orthogonality_residual": residual,
        "interpolation_sigma": None,
        "sensor_epoch": None,
    }


def build(source: bytes, eop: dict, times: dict,
          epochs: tuple[str, ...] = EPOCHS) -> dict:
    checked_source(source, eop, times)
    if not epochs or len(set(epochs)) != len(epochs):
        raise ValueError("Empty or repeated UTC list")
    mjds = [fractional_mjd(utc) for utc in epochs]
    if mjds != sorted(mjds):
        raise ValueError("Epochs must be strictly increasing")
    result = [interpolate_at(utc, eop, times) for utc in epochs]
    return {
        "id": "CASTOR-G49-IERS-1963-INTRADAY",
        "classification": "CONDITIONAL_RETROSPECTIVE_GCRS_ITRS_NOT_SATELLITE_TRACKING",
        "sources": {
            "iers_1963_full_archive_sha256": SHA256,
            "original_1963_days": 365,
            "g46_g47_source_cells_verified": True,
            "model": "ERFA c2t00a IAU2000A (nominal; dX/dY unavailable)",
            "utc": "BIPM pre-1972 rate valid Nov-Dec 1963",
        },
        "epochs": result,
        "limitations": {
            "interpolation": "PIECEWISE_LINEAR_CONVENTION_NOT_INSTRUMENT_CALIBRATION",
            "interpolation_uncertainty": None,
            "dX_dY": "UNAVAILABLE_NOT_MEASURED_ZERO",
            "TEME_to_GCRS": "NOT_IMPLEMENTED",
            "sensor_observations_527_529": "MISSING",
            "historical_holdout_527_529": "NOT_RUN",
            "impact_coordinates_time_probability": None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="Complete original 1963 IERS archive (SHA-pinned)")
    parser.add_argument("--eop", type=Path, default=ROOT / EOP)
    parser.add_argument("--times", type=Path, default=ROOT / TIME)
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build(args.source.read_bytes(), json.loads(args.eop.read_text()),
                   json.loads(args.times.read_text()))
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if args.output.read_text() != payload:
            raise SystemExit("FAIL: G49 ledger differs from authenticated rebuild")
        print("PASS: IERS full SHA, all G46/G47 cells, 9 interpolated frames")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
        print(f"WROTE {args.output}")


if __name__ == "__main__":
    main()

