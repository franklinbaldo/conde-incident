#!/usr/bin/env python3
"""Check data coverage for a counterfactual causal 81-day solar-flux average.

The *standard* NRLMSISE F107A is centered, not this trailing alternative.
Coverage is necessary but never sufficient for historical as-of availability:
publication timestamps and released data vintages remain unverified.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

from audit_space_weather_asof import SOURCE, ROOT, audit_bytes, parsed_timestamp

CERT = ROOT / 'research/constraints/C241-P32_causal_flux_backfill.json'
WINDOW_DAYS = 81


def causal_window(epoch):
    """Last 81 *completed UTC dates*, excluding target date at noon."""
    if epoch.tzinfo != dt.timezone.utc:
        raise ValueError('UTC required')
    if epoch.hour != 12 or epoch.minute or epoch.second or epoch.microsecond:
        raise ValueError('the audited source evaluates only at 12:00 UTC')
    end = epoch.date() - dt.timedelta(days=1)
    start = end - dt.timedelta(days=WINDOW_DAYS - 1)
    return [start + dt.timedelta(days=k) for k in range(WINDOW_DAYS)]


def audit_bytes_causal(source_bytes):
    source = json.loads(source_bytes)
    previous = audit_bytes(source_bytes)  # Retain all independent P31 numerical/source checks.
    observations = source['raw_series']['F107_observed_daily']
    rows = []
    for p31_row in previous['rows']:
        epoch = parsed_timestamp(p31_row['model_evaluation_utc_not_event_time'])
        dates = causal_window(epoch)
        available = [d for d in dates if d.isoformat() in observations]
        absent = [d for d in dates if d.isoformat() not in observations]
        # Input provenance proves measured values exist in a modern archive, not
        # that anyone possessed these exact values by the historical cutoff.
        rows.append({
            'model_evaluation_utc_not_event_time': epoch.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'candidate_definition': 'counterfactual_trailing_81_completed_utc_days',
            'required_window': {'first': dates[0].isoformat(),
                                'last': dates[-1].isoformat(), 'days': WINDOW_DAYS},
            'observed_dates_in_pinned_extract': len(available),
            'missing_dates_in_pinned_extract': len(absent),
            'missing_first': absent[0].isoformat() if absent else None,
            'missing_last': absent[-1].isoformat() if absent else None,
            'all_missing_dates_before_cutoff': all(d < epoch.date() for d in absent),
            'complete_candidate_mean_computable': not absent,
            'candidate_mean_sfu': (sum(observations[d.isoformat()]['observed_sfu']
                                        for d in available) / WINDOW_DAYS if not absent else None),
            'historical_release_timestamp_audited': False,
            'prospective_driver_eligible': False,
            'standard_centered_f107a_replaced': False,
            'historical_trajectory_constraint_active': False,
        })
    if len(rows) != 3:
        raise ValueError('expected three source evaluation points')
    return {
        'schema': 'conde.c241-p32-causal-flux-backfill/v1',
        'source_snapshot': str(SOURCE.relative_to(ROOT)),
        'source_snapshot_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'parent_audit_schema': previous['schema'],
        'source_family': 'Natural Resources Canada historical observed F10.7 (single lineage)',
        'finding': 'The bounded modern extract cannot compute the counterfactual trailing 81-day mean; its historical publication vintages are also unknown.',
        'warning': 'A trailing mean is NOT the centered 81-day F107A required by standard NRLMSISE; it is a candidate for a separately calibrated causal predictor only.',
        'causal_forecast_score': 'NOT_RUN',
        'historical_orbit_inference': 'NOT_RUN',
        'physical_constraint': 'CONNECTED_PENDING_CALIBRATION',
        'rows': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    args = parser.parse_args()
    payload = json.dumps(audit_bytes_causal(SOURCE.read_bytes()), ensure_ascii=False, indent=2) + '\n'
    if args.write:
        CERT.write_text(payload)
        print('WROTE', CERT)
    elif args.check:
        if not CERT.is_file() or CERT.read_text() != payload:
            raise SystemExit('STALE_CAUSAL_FLUX_AUDIT: regenerate and review C241-P32')
        print('PASS C241-P32: causal 81-day coverage incomplete at all three cutoffs')
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
