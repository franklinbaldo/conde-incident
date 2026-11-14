#!/usr/bin/env python3
"""Retrospective IERS 1963 EOP + pre-1972 UTC -> IAU2000A GCRS/ITRS frames.

Restricted to 1963-11-07/08/09 00:00 UTC. NOT a TEME/SGP4 transform or
an observation of a NORAD object. Uses SOFA-derived ERFA c2t00a.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
import math
from pathlib import Path

from iers_1963_eop import DAYS, SHA256
from iers_1963_timescales import tai_minus_utc

ROOT = Path(__file__).resolve().parents[1]
EOP = Path('research/constraints/iers_eop_1963_11_07_09.json')
TIME = Path('research/constraints/iers_1963_timescales_G47.json')
AS2RAD = math.pi / (180 * 3600)


def validate_input(eop: dict, times: dict) -> list[tuple[dict, dict]]:
    """Reject wrong lineage, mismatched dates and invented pole offsets."""
    if eop['source']['sha256'] != SHA256 or times['sources']['iers_eop']['sha256'] != SHA256:
        raise ValueError('IERS SHA256 lineage mismatch')
    if eop['source']['original_rows'] != 365 or times['sources']['iers_eop']['original_rows'] != 365:
        raise ValueError('IERS entire-year lineage required')
    samples = eop['sample']
    rows = times['rows_at_00_utc']
    if len(samples) != 3 or len(rows) != 3:
        raise ValueError('Expected exactly three documented epochs')
    for day, a, b in zip(DAYS, samples, rows, strict=True):
        if a['utc'] != b['utc'] or a['utc'] != day + 'T00:00:00Z' or a['mjd'] != b['mjd']:
            raise ValueError('EOP/time-source epoch mismatch')
        if (a['dX_arcsec'], a['dY_arcsec']) != (None, None) or a['celestial_pole_offsets_status'] != 'UNAVAILABLE_NOT_ZERO_MEASUREMENT':
            raise ValueError('Unobserved dX/dY must not be modeled as measured zero')
        for k in ('x_arcsec', 'y_arcsec', 'ut1_minus_utc_s'):
            if type(a[k]) not in (int, float) or not math.isfinite(a[k]):
                raise ValueError('Non-finite EOP value')
        if abs(a['ut1_minus_utc_s'] - b['ut1_minus_utc_s']) > 1e-12:
            raise ValueError('G46/G47 UT1 disagreement')
        if abs(b['tai_minus_utc_s'] - float(tai_minus_utc(a['mjd']))) > 1e-10:
            raise ValueError('Historical UTC rate mismatch')
        if abs(b['tt_minus_utc_s'] - b['tai_minus_utc_s'] - 32.184) > 1e-10:
            raise ValueError('TT offset mismatch')
    return list(zip(samples, rows, strict=True))


def matrix_at_epoch(eop: dict, times: dict) -> list[list[float]]:
    """IAU 2000A GCRS->ITRS orientation at *daily* UTC 00:00 only."""
    import erfa
    # SOFA two-part JD: TT for precession/nutation, UT1 for Earth rotation.
    # SOFA 2-part JD with the integer MJD in part 1 and the offset in part
    # 2. Keeping 38,000 days in a single float needlessly quantizes UTC.
    jd1 = 2400000.5 + times['mjd']
    tt = float(Decimal(str(times['tt_minus_utc_s'])) / Decimal(86400))
    ut1 = float(Decimal(str(eop['ut1_minus_utc_s'])) / Decimal(86400))
    return erfa.c2t00a(jd1, tt, jd1, ut1,
                       eop['x_arcsec'] * AS2RAD, eop['y_arcsec'] * AS2RAD).tolist()


def mul(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(x*y for x, y in zip(row, vector, strict=True)) for row in matrix]


def orthogonality_error(m: list[list[float]]) -> float:
    return max(abs(sum(m[k][i]*m[k][j] for k in range(3)) - (i == j))
               for i in range(3) for j in range(3))


def build(eop: dict, times: dict) -> dict:
    sampled = validate_input(eop, times)
    output = []
    for a, b in sampled:
        m = matrix_at_epoch(a, b)
        err = orthogonality_error(m)
        if not math.isfinite(err) or err > 1e-12:
            raise ValueError('Non-orthogonal ERFA output')
        output.append({
            'utc': a['utc'], 'mjd': a['mjd'],
            'model': 'IAU2000A_ERFA_C2T00A_NOMINAL_NO_DX_DY',
            'gcrs_to_itrs': m,
            # Each row of the orthogonal GCRS->ITRS rotation is the corresponding
            # ITRS basis vector expressed in GCRS. NOT directly TEME or RK4 ECI.
            'itrs_x_axis_in_gcrs': m[0],
            'itrs_pole_axis_in_gcrs': m[2],
            'orthogonality_residual': err,
            'polar_motion_arcsec': [a['x_arcsec'], a['y_arcsec']],
            'ut1_minus_utc_s': a['ut1_minus_utc_s'],
            'tai_minus_utc_s': b['tai_minus_utc_s'],
            'tt_minus_utc_s': b['tt_minus_utc_s'],
        })
    return {
        'id': 'CASTOR-G48-IERS-IAU2000A-1963-DAILY',
        'classification': 'RETROSPECTIVE_GCRS_TO_ITRS_FRAME_NOT_NORAD_TRACKING',
        'sources': {'eop_1963_sha256': SHA256,
                    'eop_1963_rows': 365,
                    'erfa_package': 'pyerfa==2.0.1.5',
                    'model': 'SOFA/ERFA c2t00a IAU 2000A',
                    'timescale': 'G47 pre-1972 UTC drift, TT and UT1'},
        'daily_00_utc_only': output,
        'limitations': {
            'dX_dY': 'UNAVAILABLE_NOT_ASSUMED_MEASURED_ZERO',
            'historical_EOP': 'RETROSPECTIVE_SMOOTHED_IERS_C04_05',
            'intra_day_interpolation': 'NOT_IMPLEMENTED',
            'TEME_to_GCRS_or_ITRS': 'NOT_IMPLEMENTED',
            'NRLMSISE_solar_vector': 'NOT_IMPLEMENTED',
            'sensor_observation_527_529': 'MISSING',
            'holdout_527_529': 'NOT_RUN',
            'impact_location_or_probability': None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eop', type=Path, default=ROOT / EOP)
    parser.add_argument('--times', type=Path, default=ROOT / TIME)
    args = parser.parse_args()
    print(json.dumps(build(json.loads(args.eop.read_text()),
                           json.loads(args.times.read_text())), indent=2))


if __name__ == '__main__':
    main()
