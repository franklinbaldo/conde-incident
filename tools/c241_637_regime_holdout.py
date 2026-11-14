#!/usr/bin/env python3
"""NORAD 637 near-decay *catalogue* holdouts, with 528/529/527 controls.

A pinned, secondary historic Parquet; no primary sensor covariance, no SGP4,
no reentry epoch or geographic localization.  Caller must pin full bytes.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA256 = 'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09'
SOURCE_URL = ('https://huggingface.co/datasets/oxzoid/space-track-tle-history/'
              'blob/4b4fb3a/data/tle_1963.parquet')
TARGET_IDS = (527, 528, 529, 637)
EXPECTED_COUNTS = {527: (21, 20), 528: (45, 45), 529: (57, 54), 637: (25, 25)}
COLUMNS = ('norad_id', 'epoch', 'inclination', 'raan', 'eccentricity',
           'mean_motion', 'mean_motion_dot', 'intl_designator')
MU_KM3_S2, EARTH_RADIUS_KM, EARTH_J2 = 398600.4418, 6378.137, 0.00108262668
WINDOWS = {'short': (2.0, 5.0, 3.0), 'twelve_day': (9.0, 15.0, 12.0)}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def parse_record(row_index: int, raw: dict) -> dict:
    dt = raw['epoch']
    if not isinstance(dt, datetime) or dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0 or dt.year != 1963:
        raise ValueError('non-1963 or non-UTC source epoch')
    sid = raw['norad_id']
    if type(sid) is not int or sid not in TARGET_IDS:
        raise ValueError('bad NORAD identity')
    if not isinstance(raw['intl_designator'], str) or not raw['intl_designator'].strip():
        raise ValueError('missing international designator')
    record = {'norad': sid, 'source_row': row_index, 'epoch': dt,
              'intl_designator': raw['intl_designator']}
    for field in ('inclination', 'raan', 'eccentricity', 'mean_motion', 'mean_motion_dot'):
        value = raw[field]
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('invalid numeric source field: ' + field)
        record[field] = float(value)
    if not (0 <= record['inclination'] <= 180 and 0 <= record['raan'] < 360
            and 0 <= record['eccentricity'] < 1 and record['mean_motion'] > 0):
        raise ValueError('invalid orbit fields')
    return record


def extract_pinned(path: Path) -> dict[int, list[dict]]:
    if digest(path) != SOURCE_SHA256:
        raise ValueError('original Parquet SHA mismatch')
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(path)
    if not set(COLUMNS).issubset(pf.schema_arrow.names):
        raise ValueError('required source columns unavailable')
    groups = defaultdict(list)
    rownum = 0
    # Streaming avoids materializing the entire Parquet in the lightweight control plane.
    for batch in pf.iter_batches(batch_size=64, columns=list(COLUMNS)):
        for raw in batch.to_pylist():
            if raw['norad_id'] in TARGET_IDS:
                groups[raw['norad_id']].append(parse_record(rownum, raw))
            rownum += 1
    if rownum != 4567:
        raise ValueError('Parquet corpus row count drift')
    distinct = {}
    for sid, counts in EXPECTED_COUNTS.items():
        records = sorted(groups[sid], key=lambda r: (r['epoch'], r['source_row']))
        by_epoch = {}
        for rec in records:
            old = by_epoch.get(rec['epoch'])
            if old:
                if any(old.get(k) != rec.get(k) for k in ('intl_designator', 'inclination',
                             'raan', 'eccentricity', 'mean_motion', 'mean_motion_dot')):
                    raise ValueError('nonidentical duplicate source epochs')
            else:
                by_epoch[rec['epoch']] = rec
        if (len(records), len(by_epoch)) != counts:
            raise ValueError(f'count drift for NORAD {sid}')
        distinct[sid] = list(by_epoch.values())
    return distinct


def days(a: datetime, b: datetime) -> float:
    return (a-b).total_seconds() / 86400.0


def wrap(value: float) -> float:
    return (value+180.0) % 360.0-180.0


def perigee_proxy_km(rec: dict) -> float:
    n = rec['mean_motion']*math.tau/86400.0
    a = (MU_KM3_S2/n**2)**(1/3)
    return a*(1-rec['eccentricity'])-EARTH_RADIUS_KM


def rate_j2_deg_day(rec: dict) -> float:
    n=rec['mean_motion']*math.tau/86400.0
    a=(MU_KM3_S2/n**2)**(1/3)
    p=a*(1-rec['eccentricity']**2)
    return math.degrees(-1.5*EARTH_J2*n*(EARTH_RADIUS_KM/p)**2*
                        math.cos(math.radians(rec['inclination']))*86400.0)


def forecast(prev: dict, origin: dict, horizon_days: float) -> dict:
    delta = days(origin['epoch'], prev['epoch'])
    if delta <= 0 or horizon_days <= 0:
        raise ValueError('invalid chronological origin or horizon')
    return {
        'raan_j2_deg': (origin['raan']+rate_j2_deg_day(origin)*horizon_days)%360,
        'raan_last_secant_deg': (origin['raan']+
              wrap(origin['raan']-prev['raan'])*horizon_days/delta)%360,
        'n_persistence_rev_day': origin['mean_motion'],
        'n_last_secant_rev_day': origin['mean_motion']+
              (origin['mean_motion']-prev['mean_motion'])*horizon_days/delta,
        'i_persistence_deg': origin['inclination'],
        'e_persistence': origin['eccentricity'],
    }


def choose_pairs(rows: list[dict], window: tuple[float,float,float],
                 start: str='1963-10-01', end: str='1963-11-05') -> list[dict]:
    minimum, maximum, target = window
    if not 0 < minimum <= target <= maximum:
        raise ValueError('invalid horizon window')
    if any(a['epoch'] >= b['epoch'] for a,b in zip(rows, rows[1:])):
        raise ValueError('unordered/duplicate source epochs')
    result=[]
    for i in range(1,len(rows)):
        prev, origin = rows[i-1], rows[i]
        day = origin['epoch'].date().isoformat()
        if not start <= day <= end:
            continue
        future=[r for r in rows[i+1:]
                if minimum <= days(r['epoch'], origin['epoch']) <= maximum]
        if not future:
            continue
        heldout = min(future, key=lambda r:(abs(days(r['epoch'],origin['epoch'])-target),r['epoch']))
        horizon = days(heldout['epoch'],origin['epoch'])
        pred = forecast(prev,origin,horizon)
        obs = {
            'raan_j2_deg':heldout['raan'], 'raan_last_secant_deg':heldout['raan'],
            'n_persistence_rev_day':heldout['mean_motion'],
            'n_last_secant_rev_day':heldout['mean_motion'],
            'i_persistence_deg':heldout['inclination'],
            'e_persistence':heldout['eccentricity'],
        }
        err={k: (wrap(obs[k]-p) if k.startswith('raan') else obs[k]-p)
             for k,p in pred.items()}
        if not all(math.isfinite(v) for v in err.values()):
            raise ValueError('nonfinite forecast errors')
        result.append({
            'origin_utc':origin['epoch'].isoformat(),
            'target_utc':heldout['epoch'].isoformat(),
            'source_rows':[prev['source_row'],origin['source_row'],heldout['source_row']],
            'horizon_days':round(horizon,6),
            'origin_perigee_kepler_proxy_km':round(perigee_proxy_km(origin),3),
            'signed_errors':{k:round(v,9) for k,v in err.items()},
        })
    return result


def summary(pairs: list[dict]) -> dict:
    out={'pairs_not_independent':len(pairs),
         'unique_future_epochs':len({p['target_utc'] for p in pairs}),
         'metrics':{}}
    if not pairs:
        return out
    for name in pairs[0]['signed_errors']:
        errors=[p['signed_errors'][name] for p in pairs]
        out['metrics'][name]={
            'rmse':round(math.sqrt(math.fsum(v*v for v in errors)/len(errors)),9),
            'mae':round(math.fsum(abs(v) for v in errors)/len(errors),9),
            'max_abs':round(max(abs(v) for v in errors),9),
        }
    return out


def report(by_sat: dict[int,list[dict]]) -> dict:
    results={}; last={}
    for sid in TARGET_IDS:
        rows=by_sat[sid]
        t=rows[-1]
        last[str(sid)]={
            'last_catalogue_epoch_utc':t['epoch'].isoformat(),
            'source_row':t['source_row'],
            'mean_motion_rev_day':round(t['mean_motion'],9),
            'kepler_perigee_proxy_km_NOT_MEASURED':round(perigee_proxy_km(t),3),
        }
        results[str(sid)]={}
        for name,window in WINDOWS.items():
            pairs=choose_pairs(rows,window)
            results[str(sid)][name]={'summary':summary(pairs),
                'pairs':pairs if sid in (528,637) else [],
                'other_pairs_omitted_only_for_report_size':sid not in (528,637)}
    return {
        'schema':'conde.secondary-low-perigee-holdout/v1',
        'status':'RETROSPECTIVE_SAME_LINEAGE_NOT_PHYSICAL_DECAY_ERROR',
        'source':{'url':SOURCE_URL,'sha256_verified':SOURCE_SHA256,
                  'lineage':'ONE_MODERN_MIRROR_OF_HISTORICAL_SPACETRACK_ELEMENTS'},
        'design':{'windows_days':{name:list(v) for name,v in WINDOWS.items()},
            'origin_filter_calendar_utc':['1963-10-01','1963-11-05'],
            'models':['RAAN J2', 'RAAN local secant','n persistence','n local secant',
                      'i persistence','e persistence'],
            'selection':'closest heldout epoch by time not value; one per origin',
            'posthoc_retrospective':True,
            'repeated_targets_not_independent':True,
            'dynamical_reentry_model':False,'sensor_sigma_calibrated':False,
            'phase_or_terminal_time_identified':False},
        'last_catalogue_states':last,
        'holdouts':results,
        'physical_gates':{'density_shared_between_object_altitudes':'NOT_ESTABLISHED',
            'ballistic_coefficients_independently_identified':False,
            'terminal_528_time_error_hours':None,
            'last_637_epoch_is_actual_reentry_time':False,
            'calibrated_geo_impact_probability':None,
            'active_fall_constraint':False},
    }


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parquet',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    content=(json.dumps(report(extract_pinned(args.parquet)),sort_keys=True,
                        separators=(',', ':'),ensure_ascii=False)+'\n').encode('utf-8')
    if args.check:
        if not args.output.is_file() or args.output.read_bytes()!=content:
            raise SystemExit('deterministic replay drift')
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(content)
    print('C241 637 secondary near-decay catalogue holdout OK')


if __name__=='__main__': main()
