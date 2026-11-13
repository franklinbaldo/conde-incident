#!/usr/bin/env python3
"""Audit historical space-weather input availability as of a model evaluation time.

This distinguishes retrospective driver reconstruction from prospective validation.
Never infer a release clock from a date-only archive or a physical reentry event.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/meteorology/space_weather_msise_inputs_1963_11_07_09.json'
CERT = ROOT / 'research/constraints/C241-P31_space_weather_asof.json'
UTC = dt.timezone.utc


def parsed_timestamp(value):
    t = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if t.tzinfo != UTC:
        raise ValueError('not a UTC timestamp')
    return t


def audit_bytes(source_bytes):
    doc = json.loads(source_bytes)
    if doc.get('schema') != 'conde.1963-conditional-msise-drivers/v1':
        raise ValueError('wrong source schema')
    if doc.get('physical_constraint_status') != 'CONNECTED_PENDING_CALIBRATION':
        raise ValueError('historical physical status unexpectedly promoted')
    if doc['date_grid']['f107A_window_days'] != 81:
        raise ValueError('wrong centered-window contract')
    obs = doc['raw_series']['F107_observed_daily']
    ap = doc['raw_series']['ap']
    daily = doc['raw_series']['Ap']
    rows = []
    for rec in doc['model_inputs']:
        epoch = parsed_timestamp(rec['epoch_utc'])
        day = epoch.date()
        if epoch.hour != 12 or epoch.minute or epoch.second:
            raise ValueError('this source contract only has noon evaluation points')
        first, last = day - dt.timedelta(days=40), day + dt.timedelta(days=40)
        dates = [first + dt.timedelta(days=i) for i in range(81)]
        flux = [obs[x.isoformat()]['observed_sfu'] for x in dates]
        if abs(sum(flux) / 81 - rec['F107A_81day_centered_observed_sfu']) > 0.00000051:
            raise ValueError('centered F107A mismatch')
        prev = (day - dt.timedelta(days=1)).isoformat()
        if obs[prev]['observed_sfu'] != rec['F107_previous_day_observed_sfu']:
            raise ValueError('previous-day F107 mismatch')
        midnight = epoch.replace(hour=0)
        daily_key = midnight.strftime('%Y-%m-%dT%H:%M:%SZ')
        if daily[daily_key] != rec['Ap_daily_planetary']:
            raise ValueError('daily Ap mismatch')
        bins = [midnight + dt.timedelta(hours=3*i) for i in range(8)]
        # A daily Ap index integrates the whole UTC day. At noon, four bins are not even complete.
        future_daily_bins = sum(b >= epoch for b in bins)
        if abs(sum(ap[b.strftime('%Y-%m-%dT%H:%M:%SZ')] for b in bins) / 8 - daily[daily_key]) > 0.5:
            raise ValueError('daily Ap inconsistent with 3-hour ap bins')
        current_key = epoch.strftime('%Y-%m-%dT%H:%M:%SZ')
        if ap[current_key] != rec['ap_history_planetary'][1]:
            raise ValueError('current 3-hour ap mismatch')
        if doc['raw_series']['Kp'][current_key] != rec['Kp_at_epoch']:
            raise ValueError('current 3-hour Kp mismatch')
        rows.append({
            'model_evaluation_utc_not_event_time': rec['epoch_utc'],
            'f107a_centered_window_utc_days': {'first': first.isoformat(), 'last': last.isoformat(), 'total': 81},
            'f107a_days_after_asof': sum(x > day for x in dates),
            'ap_daily_bins_at_or_after_asof': future_daily_bins,
            'ap_current_bin_utc': {'start': current_key, 'end_exclusive': (epoch + dt.timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M:%SZ')},
            'f107_previous_day_release_time': None,
            'definitive_ap_kp_release_time': None,
            'eligible_for_prospective_asof_evaluation': False,
            'eligible_for_retrospective_driver_reconstruction': True,
            'physical_constraint_active': False,
        })
    if len(rows) != 3 or len({r['model_evaluation_utc_not_event_time'] for r in rows}) != 3:
        raise ValueError('unexpected date grid')
    return {
        'schema': 'conde.c241-p31-space-weather-asof-audit/v1',
        'source_snapshot': str(SOURCE.relative_to(ROOT)),
        'source_snapshot_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'source_F107_sha256': doc['source_documents']['F107']['sha256'],
        'source_geomagnetic_family': 'GFZ Kp/ap/Ap (dependent, not three independent sensors)',
        'claim': 'Centered F107A, daily Ap and current 3-hour bins use information after the selected evaluation instant. Valid as retrospective inputs, not as-of forecasts.',
        'retrospective_driver_status': 'RETROSPECTIVE_INPUT_ONLY',
        'prospective_driver_status': 'PROSPECTIVE_SCORE_NOT_AUTHORIZED',
        'prospective_score': 'NOT_AUTHORIZED',
        'historical_density_and_reentry_posterior': 'NOT_RUN',
        'historical_constraint': 'CONNECTED_PENDING_CALIBRATION',
        'rows': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify pinned audit bytes')
    parser.add_argument('--write', action='store_true', help='regenerate audit certificate')
    args = parser.parse_args()
    if args.write and args.check:
        parser.error('choose write or check')
    value = audit_bytes(SOURCE.read_bytes())
    formatted = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if args.write:
        CERT.write_text(formatted)
        print('WROTE', CERT)
    elif args.check:
        if not CERT.is_file() or CERT.read_text() != formatted:
            raise SystemExit('STALE_ASOF_AUDIT: regenerate and review C241-P31')
        print('PASS C241-P31: 3 retrospective-only rows; prospective as-of score blocked')
    else:
        print(formatted, end='')


if __name__ == '__main__':
    main()
