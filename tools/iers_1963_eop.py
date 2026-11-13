#!/usr/bin/env python3
"""Verify an IERS 1963 EOP archive and freeze a small, source-backed input slice.

This is a *retrospective* geophysical series, not a 1963 tracking observation.
It does not itself define a TEME/GCRS/ITRF rotation or an impact constraint.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
from urllib.request import urlopen

URL = 'https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63'
SHA256 = '66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264'
OUTPUT = Path('research/constraints/iers_eop_1963_11_07_09.json')
DAYS = ('1963-11-07', '1963-11-08', '1963-11-09')
FIELDS = ('x_arcsec', 'y_arcsec', 'ut1_minus_utc_s', 'lod_s',
          'dX_arcsec', 'dY_arcsec', 'sigma_x_arcsec', 'sigma_y_arcsec',
          'sigma_ut1_minus_utc_s', 'sigma_lod_s', 'sigma_dX_arcsec',
          'sigma_dY_arcsec')


def parse_archive(data: bytes, *, expected_days: int = 365) -> dict[str, dict]:
    """Strict, unit-preserving parse; rejects duplicate, gapped, or mixed epochs."""
    try:
        lines = data.decode('ascii').splitlines()
    except UnicodeDecodeError as error:
        raise ValueError('EOP source is not ASCII') from error
    records: dict[str, dict] = {}
    for line in lines:
        fields = line.split()
        if not fields or fields[0] != '1963':
            continue
        if len(fields) != 16:
            raise ValueError('EOP year row must have 16 columns')
        try:
            y, m, d, mjd = (int(x) for x in fields[:4])
            calendar = date(y, m, d)
            numeric = [float(x) for x in fields[4:]]
        except (ValueError, OverflowError) as error:
            raise ValueError('Invalid IERS EOP row') from error
        if not all(math.isfinite(v) for v in numeric):
            raise ValueError('Non-finite EOP value')
        # MJD 38030 at midnight 1963-01-01; no leap day in 1963.
        if mjd != 38030 + (calendar - date(1963, 1, 1)).days:
            raise ValueError('MJD/calendar mismatch')
        if calendar.year != 1963:
            raise ValueError('Unexpected IERS year')
        if any(v < 0 for v in numeric[6:]):
            raise ValueError('Negative formal uncertainty')
        key = calendar.isoformat()
        if key in records:
            raise ValueError('Duplicate EOP UTC day')
        records[key] = {'utc': key + 'T00:00:00Z', 'mjd': mjd,
                        **dict(zip(FIELDS, numeric, strict=True))}
    if len(records) != expected_days:
        raise ValueError(f'EOP days: got {len(records)}, expected {expected_days}')
    first = date.fromisoformat(min(records))
    for offset in range(expected_days):
        if (first + timedelta(days=offset)).isoformat() not in records:
            raise ValueError('Missing daily EOP epoch')
    if expected_days == 365 and first != date(1963, 1, 1):
        raise ValueError('Incomplete 1963 archive')
    return records


def receipt(data: bytes) -> dict:
    actual = hashlib.sha256(data).hexdigest()
    if actual != SHA256:
        raise ValueError(f'IERS source SHA256 mismatch: {actual}')
    rows = parse_archive(data)
    selected = []
    for day in DAYS:
        row = rows[day].copy()
        # The 1963 series has dX/dY exactly zero for the whole year.
        # They are unavailable offsets, NOT measured zero corrections.
        if row['dX_arcsec'] != 0 or row['dY_arcsec'] != 0:
            raise ValueError('Unexpected 1963 dX/dY values: review epistemic flag')
        row['dX_arcsec'] = None
        row['dY_arcsec'] = None
        row['celestial_pole_offsets_status'] = 'UNAVAILABLE_NOT_ZERO_MEASUREMENT'
        selected.append(row)
    return {
        'id': 'CASTOR-G46-IERS-EOP-1963',
        'classification': 'RETROSPECTIVE_EOP_ESTIMATE_NOT_ORBITAL_OBSERVATION',
        'source': {
            'url': URL, 'sha256': SHA256, 'bytes': len(data),
            'series': 'IERS 05 C04 IAU2000A, ITRF2005 (2011 edition)',
            'description_url': 'https://datacenter.iers.org/discontinued/www.iers.org/SharedDocs/Metadaten/EN/179_EOP_05_C04_2000/14334_EOP_C04_05_XX_IAU2000Af1a8.html?nn=12932',
            'original_rows': len(rows), 'epoch_definition': 'daily 00:00 UTC',
            'lineage': 'retrospective IERS solution, not primary 1963 NORAD tracking',
        },
        'units': {'x_y_dX_dY_sigma': 'arcseconds',
                  'UT1_minus_UTC_sigma': 'seconds', 'LOD_sigma': 'seconds'},
        'sample': selected,
        'limitations': {
            'fractional_day_interpolation': 'NOT_IMPLEMENTED',
            'precession_nutation_model_transform': 'NOT_IMPLEMENTED',
            'teme_to_itrf_or_gcrs_operator': 'NOT_IMPLEMENTED',
            'historical_station_coordinates': None,
            'independent_norad_527_529_instrumental_holdout': 'NOT_RUN',
            'measured_1963_003B_position': None,
            'impact_location_or_probability': None,
            'can_constrain_historical_reentry': False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Previously downloaded 1963 IERS source bytes')
    parser.add_argument('--download', action='store_true', help='Fetch official archived source')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--check', action='store_true', help='Compare report with tracked version')
    args = parser.parse_args()
    if args.download == bool(args.source):
        parser.error('Select exactly one of --download or --source')
    if args.download:
        with urlopen(URL, timeout=35) as response:
            source = response.read(128_000)
    else:
        source = args.source.read_bytes()
    data = json.dumps(receipt(source), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if not args.output.exists() or args.output.read_text() != data:
            raise SystemExit('FAIL: tracked IERS report differs from pinned source')
        print('PASS: IERS archive SHA, 365 UTC days, fixed 3-day receipt')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
        print(f'WROTE: {args.output}')


if __name__ == '__main__':
    main()
