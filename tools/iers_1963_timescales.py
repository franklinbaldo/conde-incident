#!/usr/bin/env python3
"""Source-locked 1963 UTC/TAI/TT/UT1 ledger; not a satellite observation.

1963 UTC had a frequency offset: treating TAI-UTC as a constant adds a false
~1.1232 ms/day discrepancy to differences of UT1-UTC and length of day.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
import math
from pathlib import Path
from urllib.request import urlopen

from iers_1963_eop import DAYS, SHA256, URL, parse_archive

BIPM_TABLE = ('https://www.bipm.org/documents/20126/59466374/'
              '9_Table2_TAR20.pdf/713645fb-e266-6304-1375-d906d14785d7')
IERS_TABLE = 'https://hpiers.obspm.fr/eop-pc/index.php?index=TAI-UTC_tab'
# Official 1963-11-01 to 1964-01-01 clause (NOT a 1972-era leap-second table).
FIRST_MJD = 38334
LAST_MJD_EXCLUSIVE = 38395
REFERENCE_MJD = Decimal('37665')
REFERENCE_OFFSET_S = Decimal('1.9458580')
UTC_RATE_S_PER_DAY = Decimal('0.0011232')
TT_MINUS_TAI_S = Decimal('32.184')
DAY_S = Decimal('86400')
SOFA_ERA_DOC = 'https://juliaastro.org/SOFA/stable/api/rotations/'
OUTPUT = Path('research/constraints/iers_1963_timescales_G47.json')


def tai_minus_utc(mjd: int) -> Decimal:
    """1963 Nov-Dec UTC rate clause only. Refuse extrapolation across a step."""
    if type(mjd) is not int or not FIRST_MJD <= mjd < LAST_MJD_EXCLUSIVE:
        raise ValueError('MJD outside documented 1963-Nov UTC rate clause')
    return REFERENCE_OFFSET_S + (Decimal(mjd) - REFERENCE_MJD) * UTC_RATE_S_PER_DAY


def earth_rotation_angle_iau2000(jd1: Decimal, jd2: Decimal) -> float:
    """IAU 2000 Earth Rotation Angle component, not full ECI/ITRF frame.

    Canonical ERA = 2*pi*[0.7790572732640 + 1.00273781191135448
    * (UT1_JD - 2451545.0)] modulo one turn. Keep split-JD precision.
    """
    t = jd1 + jd2 - Decimal('2451545.0')
    phase = Decimal('0.7790572732640') + Decimal('1.00273781191135448') * t
    return 2 * math.pi * float(phase % 1) % (2 * math.pi)


def build(data: bytes) -> dict:
    import hashlib
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('IERS original 1963 SHA256 mismatch')
    archive = parse_archive(data)
    rows = []
    for day in DAYS:
        entry = archive[day]
        mjd = entry['mjd']
        tai_utc = tai_minus_utc(mjd)
        dut1 = Decimal(str(entry['ut1_minus_utc_s']))
        lod = Decimal(str(entry['lod_s']))
        jd_ut1 = Decimal(mjd) + dut1 / DAY_S
        jd_tt = Decimal(mjd) + (tai_utc + TT_MINUS_TAI_S) / DAY_S
        rows.append({
            'utc': entry['utc'], 'mjd': mjd,
            'tai_minus_utc_s': float(tai_utc),
            'tt_minus_utc_s': float(tai_utc + TT_MINUS_TAI_S),
            'ut1_minus_utc_s': float(dut1),
            'ut1_minus_tai_s': float(dut1 - tai_utc),
            'lod_s': float(lod),
            # SOFA 2-part Julian Date inputs: avoid subtracting large JD floats.
            'jd_part1': 2400000.5,
            'jd_part2_ut1': float(jd_ut1),
            'jd_part2_tt': float(jd_tt),
            'era_iau2000_rad': earth_rotation_angle_iau2000(Decimal('2400000.5'), jd_ut1),
        })
    intervals = []
    for a, b in zip(rows, rows[1:]):
        if b['mjd'] - a['mjd'] != 1:
            raise ValueError('Nonconsecutive UTC days')
        raw = Decimal(str(b['ut1_minus_utc_s'])) - Decimal(str(a['ut1_minus_utc_s']))
        tai = Decimal(str(b['tai_minus_utc_s'])) - Decimal(str(a['tai_minus_utc_s']))
        lod = (Decimal(str(a['lod_s'])) + Decimal(str(b['lod_s']))) / 2
        # Change in UT1-TAI should approximately equal -mean LOD over 1 day.
        # This is a DIAGNOSTIC, not a strict identity or calibrated sigma.
        intervals.append({
            'utc_start': a['utc'], 'utc_end': b['utc'],
            'delta_ut1_minus_utc_s': float(raw),
            'delta_tai_minus_utc_s': float(tai),
            'delta_ut1_minus_tai_s': float(raw - tai),
            'mean_lod_s': float(lod),
            'lod_residual_without_utc_rate_us': float((raw + lod) * 1_000_000),
            'lod_residual_with_utc_rate_us': float((raw - tai + lod) * 1_000_000),
        })
    return {
        'id': 'CASTOR-G47-1963-PRELEAP-UTC-RATE',
        'classification': 'RETROSPECTIVE_TIMESCALE_RECONSTRUCTION_NOT_TRACKING',
        'sources': {
            'iers_eop': {'url': URL, 'sha256': SHA256, 'original_rows': 365},
            'tai_utc_definition': {'bipm_url': BIPM_TABLE, 'iers_url': IERS_TABLE,
                                    'clause': '1963-11-01 through 1963-12-31',
                                    'basis_mjd': 37665, 'offset_s': 1.945858,
                                    'rate_s_per_day': 0.0011232},
            'era_model': {'reference': SOFA_ERA_DOC, 'model': 'IAU 2000 ERA00'},
        },
        'rows_at_00_utc': rows, 'daily_lod_diagnostics': intervals,
        'limits': {
            'utc_rate': 'valid ONLY Nov-Dec 1963; historical step on 1963-11-01',
            'daily_dut1_interpolation': 'NOT_IMPLEMENTED',
            'lod_residual': 'descriptive central differences; NOT calibrated uncertainty',
            'tt_definition': 'conventional TT=TAI+32.184 s back-extrapolation',
            'earth_rotation_angle': 'IAU2000 analytic component computed, not frame',
            'full_iau2000a_celestial_to_terrestrial_rotation': 'NOT_IMPLEMENTED',
            'dut1_x_y_source': 'retrospective IERS C04, not independent NORAD sensors',
            'historical_527_529_holdout': 'NOT_RUN',
            'impact_location_or_probability': None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source', type=Path)
    group.add_argument('--download', action='store_true')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.download:
        with urlopen(URL, timeout=35) as response:
            source = response.read(128_000)
    else:
        source = args.source.read_bytes()
    content = json.dumps(build(source), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit('FAIL: recorded G47 ledger differs from pinned sources')
        print('PASS: 365-row SHA-pinned IERS / 1963 UTC rate / daily LOD diagnostics')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
        print(f'WROTE: {args.output}')


if __name__ == '__main__':
    main()
