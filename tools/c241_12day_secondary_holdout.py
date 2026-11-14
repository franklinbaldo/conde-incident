#!/usr/bin/env python3
"""Retrospective ~12-day same-catalogue control forecast; NOT sensor sigma.

One time-ordered historical ledger, not independent instruments. Models are
minimal baselines, not SGP4, atmospheric reentry, or phase forecasts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CSV_SHA256 = '3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231'
PARQUET_SHA256 = 'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09'
SOURCE = 'https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet'
SATELLITES = (527, 529)
MIN_HORIZON, MAX_HORIZON, TARGET_HORIZON = 9.0, 15.0, 12.0
MU, R, J2 = 398600.4418, 6378.137, 0.00108262668


def days(a: datetime, b: datetime) -> float:
    return (a - b).total_seconds() / 86400.0


def wrap(x: float) -> float:
    return (x + 180) % 360 - 180


def rate_j2(origin: dict) -> float:
    n = origin['mean_motion'] * 2 * math.pi / 86400.0
    ecc, inc = origin['eccentricity'], math.radians(origin['inclination'])
    if n <= 0 or not (0 <= ecc < 1) or not (0 <= origin['inclination'] <= 180):
        raise ValueError('invalid J2 parameters')
    a = (MU / n**2)**(1/3)
    return math.degrees(-1.5 * J2 * n * (R / (a * (1-ecc**2)))**2 * math.cos(inc) * 86400)


def read_secondary_csv(path: Path) -> list[dict]:
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != CSV_SHA256:
        raise ValueError('SHA mismatch: secondary CSV was not pinned')
    rows = []
    for raw in csv.DictReader(payload.decode('utf-8').splitlines()):
        sid = int(raw['norad_id'])
        if sid not in SATELLITES:
            continue
        epoch = datetime.fromisoformat(raw['epoch'].replace('Z', '+00:00'))
        if epoch.tzinfo != timezone.utc or epoch.year != 1963:
            raise ValueError('invalid UTC epoch')
        record = {'norad': sid, 'epoch': epoch, 'source_row': int(raw['source_row'])}
        for field in ('mean_motion', 'raan', 'inclination', 'eccentricity'):
            record[field] = float(raw[field])
            if not math.isfinite(record[field]):
                raise ValueError('nonfinite orbit field')
        rows.append(record)
    if len(rows) != 78:  # secondary: 527=21, 529=57, four identical repeats
        raise ValueError('historical row count changed')
    groups = defaultdict(list)
    for row in rows:
        groups[row['norad']].append(row)
    distinct = []
    for sid, records in groups.items():
        seen = {}
        for row in sorted(records, key=lambda x: (x['epoch'], x['source_row'])):
            epoch = row['epoch']
            if epoch in seen:
                fields = ('raan', 'mean_motion', 'inclination', 'eccentricity')
                if any(row[f] != seen[epoch][f] for f in fields):
                    raise ValueError('conflicting repeated epoch')
            else:
                seen[epoch] = row
        if len(seen) != {527: 20, 529: 54}[sid]:
            raise ValueError('historical unique epoch count changed')
        distinct += list(seen.values())
    return sorted(distinct, key=lambda x: (x['norad'], x['epoch']))


def forecast(previous: dict, origin: dict, horizon: float) -> dict[str, float]:
    step = days(origin['epoch'], previous['epoch'])
    if step <= 0 or not MIN_HORIZON <= horizon <= MAX_HORIZON:
        raise ValueError('invalid forward horizon')
    return {
        'raan_j2_deg': (origin['raan'] + rate_j2(origin) * horizon) % 360,
        'raan_two_point_deg': (origin['raan'] +
            wrap(origin['raan'] - previous['raan']) * horizon / step) % 360,
        'mean_motion_persistence_rev_day': origin['mean_motion'],
        'mean_motion_two_point_rev_day': origin['mean_motion'] +
            (origin['mean_motion'] - previous['mean_motion']) * horizon / step,
        'inclination_persistence_deg': origin['inclination'],
        'eccentricity_persistence': origin['eccentricity'],
    }


def make_pairs(records: list[dict], *, start: str | None = None,
               end: str | None = None) -> list[dict]:
    pairs = []
    for sid in SATELLITES:
        rows = sorted((row for row in records if row['norad'] == sid),
                      key=lambda x: x['epoch'])
        if any(a['epoch'] >= b['epoch'] for a, b in zip(rows, rows[1:])):
            raise ValueError('non-distinct or non-monotone epochs')
        for ix in range(1, len(rows)):
            prev, origin = rows[ix - 1], rows[ix]
            origin_iso = origin['epoch'].date().isoformat()
            if start and origin_iso < start or end and origin_iso > end:
                continue
            options = [(abs(days(t['epoch'], origin['epoch'])-TARGET_HORIZON), t)
                       for t in rows[ix+1:]
                       if MIN_HORIZON <= days(t['epoch'], origin['epoch']) <= MAX_HORIZON]
            if not options:
                continue
            # Deterministic nearest-to-12d target, without fitting to target values.
            target = min(options, key=lambda x: (x[0], x[1]['epoch']))[1]
            horizon = days(target['epoch'], origin['epoch'])
            pred = forecast(prev, origin, horizon)
            values = {
                'raan_j2_deg': target['raan'],
                'raan_two_point_deg': target['raan'],
                'mean_motion_persistence_rev_day': target['mean_motion'],
                'mean_motion_two_point_rev_day': target['mean_motion'],
                'inclination_persistence_deg': target['inclination'],
                'eccentricity_persistence': target['eccentricity'],
            }
            errors = {k: wrap(values[k]-v) if k.startswith('raan') else values[k]-v
                      for k, v in pred.items()}
            if any(not math.isfinite(v) for v in errors.values()):
                raise ValueError('non-finite error')
            pairs.append({'norad': sid, 'previous_epoch_utc': prev['epoch'].isoformat(),
                          'origin_epoch_utc': origin['epoch'].isoformat(),
                          'target_epoch_utc': target['epoch'].isoformat(),
                          'previous_source_row': prev['source_row'],
                          'origin_source_row': origin['source_row'],
                          'target_source_row': target['source_row'],
                          'horizon_days': round(horizon, 6),
                          'signed_errors': {k: round(v, 10) for k, v in errors.items()}})
    return pairs


def summarize(pairs: list[dict]) -> dict:
    metrics = {}
    if pairs:
        names = pairs[0]['signed_errors']
        for key in names:
            es = [p['signed_errors'][key] for p in pairs]
            metrics[key] = {
                'mae': round(math.fsum(abs(e) for e in es)/len(es), 10),
                'rmse': round(math.sqrt(math.fsum(e*e for e in es)/len(es)), 10),
                'max_abs': round(max(abs(e) for e in es), 10),
                'mean_signed': round(math.fsum(es)/len(es), 10),
            }
    return {'pair_count_not_independent': len(pairs),
            'unique_targets': len({(p['norad'], p['target_epoch_utc']) for p in pairs}),
            'metrics': metrics}


def report(rows: list[dict]) -> dict:
    full = make_pairs(rows)
    oct_pairs = make_pairs(rows, start='1963-10-01', end='1963-10-27')
    return {
        'schema': 'conde.secondary-12day-controls/v1',
        'status': 'RETROSPECTIVE_SECONDARY_CATALOGUE_RESIDUALS_NOT_INSTRUMENT_SIGMA',
        'source': {'uri': SOURCE, 'parquet_sha256_documented': PARQUET_SHA256,
                   'extracted_csv_sha256_checked': CSV_SHA256,
                   'lineage': 'ONE_HISTORICAL_SPACETRACK_MIRROR_NOT_SENSOR_INDEPENDENCE'},
        'design': {'horizon_days': [MIN_HORIZON, MAX_HORIZON], 'target_days': TARGET_HORIZON,
                   'pair_rule': 'each origin chooses nearest future epoch within 9-15 days',
                   'training': 'one origin and preceding sample of same object only',
                   'pre_registration': 'RETROSPECTIVE_POST_INSPECTION_2026-11-14',
                   'future_values_used_in_forecast': False,
                   'overlapping_pairs_are_independent': False,
                   'not_sgp4_or_decay_prediction': True},
        'all_1963': {str(s): summarize([p for p in full if p['norad']==s]) for s in SATELLITES},
        'october_origins_through_oct27': {
            str(s): summarize([p for p in oct_pairs if p['norad']==s]) for s in SATELLITES},
        'october_pairs': oct_pairs,
        'decay_time_error_hours': None,
        'terminal_position_or_phase_error': None,
        'limitations': ['Not external measurements, no source sensor covariance/frame verified',
                        'RAAN catalogue frame and mean-element conventions unverified',
                        'Time-to-reentry calibration cannot be inferred from these field residuals',
                        'Data-dependent nearest 12-day target timestamps; overlapping forecasts',
                        '527 October-to-November next interval is > 30 days, not a 12-day control'],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = (json.dumps(report(read_secondary_csv(args.csv)), ensure_ascii=False,
                          indent=2, sort_keys=True) + '\n').encode()
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != content:
            raise SystemExit('report drift')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print('secondary 12-day controls: replay OK')


if __name__ == '__main__':
    main()
