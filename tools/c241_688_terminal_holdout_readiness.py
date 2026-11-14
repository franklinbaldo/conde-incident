#!/usr/bin/env python3
"""Audit whether 1963-044B/688 can calibrate terminal-time prediction.

No orbital prediction is fitted; the terminal report and catalog orbit are distinct
sources.  The secondary source is SHA pinned and cannot calibrate 528 by analogy.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA256 = 'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09'
SOURCE_URL = ('https://huggingface.co/datasets/oxzoid/space-track-tle-history/'
              'blob/4b4fb3a/data/tle_1963.parquet')
LEDGER = Path('research/tle_custody/norad_spadats_context_C241-L46.json')
REPORT_ID = 'AF IN 23784 (corrected copy of AF IN 22976)'
REPORT_SHA256 = '65452b827428bdbef37bf96fb915a1411c2798d5a16939d845abe561aa12e13e'
DECAY_START = datetime(1963, 11, 12, 22, 10, tzinfo=timezone.utc)
DECAY_END = datetime(1963, 11, 13, 0, 0, tzinfo=timezone.utc)  # 2400Z on Nov 12
IDENTITIES = {687: '63044  A', 688: '63044  B'}
EXPECTED_ROWS = {687: 2, 688: 1}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify_ledger(data: dict) -> None:
    sources = [s for s in data['sources'] if s['id'] == 'C241-L46-D08']
    if len(sources) != 1:
        raise ValueError('missing or duplicated custody record')
    s = sources[0]
    if (s['sha256'] != REPORT_SHA256 or s['message'] != REPORT_ID
            or s['document_date'] != '1963-11-14'
            or s['object_ids'] != [687, 688] or s['launch'] != '1963-044'):
        raise ValueError('documentary identity/custody mismatch')
    w = s['decay_window']
    if (w['object_id'] != 688 or w['date_utc'] != '1963-11-12'
            or w['start'] != '2210Z' or w['end'] != '2400Z'
            or w['kind'] != 'REPORTED_INTERVAL_FOR_DIFFERENT_OBJECT_NOT_SIGMA'):
        raise ValueError('terminal window not sourced to 688')
    if data['target']['norad'] != 528 or data['target']['activation'] is not False:
        raise ValueError('528 source boundary changed')


def normalize_row(index: int, raw: dict) -> dict:
    sid = raw['norad_id']
    if type(sid) is not int or sid not in IDENTITIES:
        raise ValueError('unexpected object')
    t = raw['epoch']
    if (not isinstance(t, datetime) or t.utcoffset() != timedelta(0)
            or t.year != 1963):
        raise ValueError('invalid UTC epoch')
    n = raw['mean_motion']
    if not isinstance(n, (int, float)) or not math.isfinite(n) or n <= 0:
        raise ValueError('invalid mean motion')
    if raw['intl_designator'] != IDENTITIES[sid]:
        raise ValueError('catalog designator mismatch')
    return {'source_row': index, 'epoch': t, 'mean_motion_rev_day': float(n)}


def extract_pinned(path: Path) -> dict[int, list[dict]]:
    if digest(path) != SOURCE_SHA256:
        raise ValueError('historical Parquet SHA mismatch')
    import pyarrow.parquet as pq  # only required for replay, not for unit tests
    pf = pq.ParquetFile(path)
    columns = ['norad_id', 'epoch', 'mean_motion', 'intl_designator']
    if not set(columns).issubset(pf.schema_arrow.names):
        raise ValueError('missing source fields')
    groups = {sid: [] for sid in IDENTITIES}
    total = 0
    for batch in pf.iter_batches(batch_size=64, columns=columns):
        for raw in batch.to_pylist():
            if raw['norad_id'] in groups:
                groups[raw['norad_id']].append(normalize_row(total, raw))
            total += 1
    if total != 4567:
        raise ValueError('historical Parquet row count changed')
    return groups


def analyze(groups: dict[int, list[dict]], ledger: dict) -> dict:
    verify_ledger(ledger)
    if set(groups) != set(IDENTITIES):
        raise ValueError('required control object missing or extra group')
    out = {}
    for sid in sorted(IDENTITIES):
        rows = groups[sid]
        if len(rows) != EXPECTED_ROWS[sid]:
            raise ValueError('historical object epoch count changed')
        times = [r['epoch'] for r in rows]
        if times != sorted(set(times)) or any(t >= DECAY_START for t in times):
            raise ValueError('duplicate, unordered or post-outcome source epoch')
        out[str(sid)] = {
            'international_designator': IDENTITIES[sid],
            'secondary_catalogue_epoch_count': len(rows),
            'source_rows': [r['source_row'] for r in rows],
            'epochs_utc': [t.isoformat() for t in times],
            'mean_motion_rev_day': [r['mean_motion_rev_day'] for r in rows],
            'within_object_secant_estimable': len(rows) >= 2,
            'terminal_time_holdout_ready': False,
        }
    latest_688 = groups[688][-1]['epoch']
    gap_start = (DECAY_START - latest_688).total_seconds() / 3600
    gap_end = (DECAY_END - latest_688).total_seconds() / 3600
    return {
        'schema': 'c241-688-1963-terminal-holdout-readiness/v1',
        'catalogue': {'url': SOURCE_URL, 'sha256': SOURCE_SHA256,
                      'lineage': 'ONE_SECONDARY_CATALOGUE_NOT_INDEPENDENT_TRACKING'},
        'terminal_report': {'source_id': 'C241-L46-D08', 'message': REPORT_ID,
                            'pdf_sha256_from_prior_custody': REPORT_SHA256,
                            'object_id': 688, 'launch': '1963-044',
                            'status': 'REPORTED_TERMINAL_INTERVAL_NOT_SENSOR_TIMESTAMPS',
                            'utc_start': DECAY_START.isoformat(),
                            'utc_end_exclusive': DECAY_END.isoformat(),
                            'duration_minutes': 110},
        'objects': out,
        '688_gap_from_last_catalogue_epoch_to_reported_interval_hours':
            [round(gap_start, 6), round(gap_end, 6)],
        'discriminant_observations': [
            'second pre-terminal independently dated orbital state of NORAD 688',
            'measurement errors, station and orbit-element convention for 688',
            'specified dynamics and terminal-condition model frozen before external holdout',
            'other reentries with independent terminal intervals and prespecified selection',
        ],
        'inference': {
            '688_secant_status': 'NOT_ESTIMABLE_ONE_PRE_TERMINAL_EPOCH',
            '687_to_688_transfer': 'NOT_JUSTIFIED_DISTINCT_PHYSICAL_OBJECT',
            'independent_terminal_time_error_calibration': False,
            'terminal_time_sigma_hours': None, 'mass_528_posterior': None,
            'active_constraint_528': False, 'impact_geography_528': None,
            'historical_mcmc': 'NOT_RUN',
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parquet', type=Path, required=True)
    p.add_argument('--ledger', type=Path, default=LEDGER)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    catalogue = extract_pinned(args.parquet)
    result = analyze(catalogue, json.loads(args.ledger.read_text(encoding='utf-8')))
    # O workflow de replay existente executa esta entrada: uma página pública
    # que repete a mesma época não deve ser promovida a segunda observação.
    from c241_688_public_tle_duplicate import LINE1, LINE2, audit, parse_tle
    duplicate = audit(parse_tle(LINE1, LINE2), catalogue)
    if not duplicate['duplicate_state_candidate']:
        raise ValueError('public 688 TLE mismatch: independent manual review required')
    result['external_tle_duplicate_audit'] = duplicate
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"688: {result['objects']['688']['secondary_catalogue_epoch_count']} prior epoch; "
          f"interval {result['terminal_report']['duration_minutes']} min; historical MCMC NOT_RUN")


if __name__ == '__main__':
    main()
