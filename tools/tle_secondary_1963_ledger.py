#!/usr/bin/env python3
"""Ledger for a SHA-pinned SECONDARY 1963 Parquet, not original NORAD TLEs.

No TLE line1/line2 reconstruction, physical-frame assumption or impact model.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

SOURCE_URL = ('https://huggingface.co/datasets/oxzoid/space-track-tle-history/'
              'resolve/4b4fb3a/data/tle_1963.parquet')
SOURCE_SHA256 = 'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09'
SOURCE_KIND = 'SECONDARY_NUMERIC_PARQUET_NOT_ORIGINAL_1963_TLE'
IDS = (527, 528, 529)
COLUMNS = ('norad_id', 'epoch', 'inclination', 'raan', 'eccentricity',
           'arg_perigee', 'mean_anomaly', 'mean_motion', 'mean_motion_dot',
           'bstar', 'intl_designator', 'altitude_km')
FLOAT_COLUMNS = tuple(x for x in COLUMNS if x not in ('norad_id','epoch','intl_designator'))
FIELDS = ('inclination','raan','eccentricity','arg_perigee','mean_anomaly','mean_motion')
TOLERANCES = {'inclination': 0.00006, 'raan': 0.00006, 'eccentricity': 0.00000008,
              'arg_perigee': 0.00006, 'mean_anomaly': 0.00006, 'mean_motion': 0.00000005}


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def checked_source_bytes(payload):
    if sha256(payload) != SOURCE_SHA256:
        raise ValueError('Parquet SHA-256 diverges from pinned source')
    if not (payload.startswith(b'PAR1') and payload.endswith(b'PAR1')):
        raise ValueError('Invalid Parquet magic bytes')
    return payload


def utc_epoch(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError('Epoch must have explicit UTC timezone')
    if value.year != 1963:
        raise ValueError('Epoch outside 1963')
    midnight = value.replace(hour=0, minute=0, second=0, microsecond=0)
    microseconds = (value - midnight) // timedelta(microseconds=1)
    if microseconds % 864:  # 8 decimals of TLE day -> 864 microseconds
        raise ValueError('Epoch does not fall on 864-us numeric TLE grid')
    return value.isoformat(timespec='microseconds').replace('+00:00', 'Z')


def extract(source_rows):
    """Keep original Parquet row numbers even when non-target rows interleave."""
    entries = []
    for index, raw in enumerate(source_rows):
        sat = raw.get('norad_id')
        if sat not in IDS:
            continue
        if not isinstance(sat, int) or isinstance(sat, bool):
            raise ValueError('NORAD field is not an integer')
        item = {'source_row': index, 'norad_id': sat, 'epoch': utc_epoch(raw.get('epoch'))}
        if not isinstance(raw.get('intl_designator'), str) or not raw['intl_designator'].strip():
            raise ValueError(f'No international designator at source_row={index}')
        item['intl_designator'] = raw['intl_designator']
        for name in FLOAT_COLUMNS:
            val = raw.get(name)
            if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(val):
                raise ValueError(f'Non-finite/non-numeric {name} at source_row={index}')
            item[name] = val
        for name, minimum, maximum, inclusive_upper in (
            ('inclination', 0, 180, True), ('raan', 0, 360, False),
            ('eccentricity', 0, 1, False), ('arg_perigee', 0, 360, False),
            ('mean_anomaly', 0, 360, False)):
            val = item[name]
            if not (minimum <= val <= maximum if inclusive_upper else minimum <= val < maximum):
                raise ValueError(f'Out-of-range {name} at source_row={index}')
        if item['mean_motion'] <= 0:
            raise ValueError(f'Non-positive mean motion at source_row={index}')
        entries.append(item)
    entries.sort(key=lambda r: (r['norad_id'], r['epoch'], r['source_row']))
    return entries


def summarize(entries):
    counts = Counter(row['norad_id'] for row in entries)
    groups = {}
    for row in entries:
        groups.setdefault((row['norad_id'], row['epoch']), []).append(row)
    collisions = []
    for (sat, epoch), group in sorted(groups.items()):
        if len(group) > 1 and any(
            tuple(row.get(k) for k in COLUMNS) != tuple(group[0].get(k) for k in COLUMNS)
            for row in group[1:]):
            collisions.append({'norad_id': sat, 'epoch_utc': epoch,
                               'source_rows': [row['source_row'] for row in group]})
    return {
        'per_object': {str(sat): {'rows': counts[sat],
                                 'unique_epochs': len({r['epoch'] for r in entries if r['norad_id'] == sat}),
                                 'duplicate_epoch_rows': counts[sat] - len({r['epoch'] for r in entries if r['norad_id'] == sat})}
                       for sat in IDS},
        'conflicting_duplicate_epochs': collisions,
        'field_units_and_cautions': {
            'epoch': 'UTC microseconds; numeric-mirror timestamp, not original 1963 measurement',
            'inclination': 'degrees',
            'raan': 'degrees; historical reference frame NOT_VERIFIED',
            'eccentricity': 'dimensionless',
            'arg_perigee': 'degrees',
            'mean_anomaly': 'degrees',
            'mean_motion': 'revolutions/day',
            'mean_motion_dot': 'mirror value in rev/day^2; matches TLE n-dot/2 field in the 528 secondary literal; NOT measured continuous acceleration',
            'bstar': 'SGP4 inverse-Earth-radii convention unverified for historic source; zero does NOT mean drag absent',
            'altitude_km': 'km; possibly derived perigee approximation, NOT an independent altitude observation',
            'intl_designator': 'catalog identifier, not physical-component identity',
        },
        'original_tle_line1_line2_present': False,
        'original_tle_checksums_verified': False,
        'historical_sensor_frame_error_verified': False,
        'physical_identity_528_verified': False,
        'legacy_raan_284_1520_active_observation': False,
        'physical_orbital_constraint': 'NOT_PROMOTED',
        'conde_impact': 'INDETERMINATE',
    }


def compare_literal(entries, literal_report):
    """Secondary-to-secondary representation comparison, not independent tracking."""
    target = literal_report['epoch_utc']
    matches = [r for r in entries if r['norad_id'] == 528 and r['epoch'] == target]
    result = {'origin': 'TWO_MODERN_MIRRORS_POSSIBLY_SHARED_TRACKING',
              'same_epoch_utc': target, 'matched_source_rows': [r['source_row'] for r in matches],
              'independent_primary_observations': 0,
              'unproven_site_raan_284_1520_active': False,
              'original_1963_line_pair_verified': False}
    if len(matches) != 1:
        result['status'] = 'NO_MATCH' if not matches else 'AMBIGUOUS_EPOCH'
        return result
    row = matches[0]
    differences = {field: abs(float(literal_report['values'][field]['decimal']) - row[field])
                   for field in FIELDS}
    result['differences'] = differences
    result['status'] = ('AGREES_WITHIN_NUMERIC_ROUNDING' if all(
        differences[field] <= TOLERANCES[field] for field in FIELDS) else 'FIELD_CONFLICT')
    return result


def csv_bytes(rows):
    from io import StringIO
    buffer = StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=('source_row',) + COLUMNS, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row[key] for key in ('source_row',) + COLUMNS})
    return buffer.getvalue().encode('utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parquet', required=True, type=Path)
    p.add_argument('--download', action='store_true')
    p.add_argument('--literal', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    if args.download:
        with urlopen(SOURCE_URL, timeout=60) as response:
            payload = response.read()
        checked_source_bytes(payload)
        args.parquet.parent.mkdir(parents=True, exist_ok=True)
        args.parquet.write_bytes(payload)
    checked_source_bytes(args.parquet.read_bytes())
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(args.parquet)
    schema = set(pf.schema_arrow.names)
    missing = set(COLUMNS) - schema
    if missing:
        raise ValueError('Missing source columns: ' + ', '.join(sorted(missing)))
    # Empty strings/line-pairs absent in source are not silently fabricated.
    if {'line1', 'line2'} & schema:
        raise ValueError('Unexpected literal line columns: revisit original-line claim')
    entries = extract(pf.read(columns=list(COLUMNS)).to_pylist())
    summary = summarize(entries)
    from tle_literal_layout import audit_literal_file
    literal = audit_literal_file(args.literal)
    summary['secondary_literal_same_epoch'] = compare_literal(entries, literal)
    summary['source'] = {'url': SOURCE_URL, 'sha256': SOURCE_SHA256,
                         'kind': SOURCE_KIND,
                         'original_tracking_record_retrieved': False,
                         'raw_rows_indexed_before_filter': pf.metadata.num_rows}
    args.output.mkdir(parents=True, exist_ok=True)
    files = {'norad_527_528_529_numeric_1963.csv': csv_bytes(entries),
             'norad_528_45_epochs_numeric_1963.csv': csv_bytes([r for r in entries if r['norad_id'] == 528])}
    for name, payload in files.items():
        (args.output / name).write_bytes(payload)
    summary['derived_csv_sha256'] = {name: sha256(payload) for name, payload in files.items()}
    (args.output / 'ledger.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'per_object': summary['per_object'],
                      'mirror': summary['secondary_literal_same_epoch']['status'],
                      'derived_sha256': summary['derived_csv_sha256']}, sort_keys=True))
    expected = {'527': (21, 20), '528': (45, 45), '529': (57, 54)}
    for sat, (rows, unique) in expected.items():
        if (summary['per_object'][sat]['rows'], summary['per_object'][sat]['unique_epochs']) != (rows, unique):
            raise SystemExit(f'Pinned corpus unexpectedly changed count for NORAD {sat}')
    if summary['conflicting_duplicate_epochs']:
        raise SystemExit('Conflicting duplicate epochs in pinned corpus')
    if summary['secondary_literal_same_epoch']['status'] != 'AGREES_WITHIN_NUMERIC_ROUNDING':
        raise SystemExit('Secondary literal and numeric Parquet diverged; not independently verified')


if __name__ == '__main__':
    main()
