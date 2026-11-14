#!/usr/bin/env python3
"""Deterministic King-Hele-like local scale-height sensitivity, NOT a reentry predictor.

All numerical states are read from a SHA-pinned secondary Parquet via the existing
C241 importer. The NASA civil-day label is not a calibrated UTC terminal instant.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from statistics import median

from c241_637_regime_holdout import SOURCE_SHA256, SOURCE_URL, extract_pinned

MU_KM3_S2 = 398600.4418
SECONDS_PER_DAY = 86400
H_KM = (40, 50)  # retrospective, uncalibrated illustrative scale-height scenarios
CUTOFFS_637 = ('1963-10-18T00:00:00+00:00', '1963-10-23T00:00:00+00:00',
               '1963-10-27T00:00:00+00:00', '1963-10-30T00:00:00+00:00')
CUTOFF_528 = '1963-10-28T00:00:00+00:00'
NASA_DAY_637 = '1963-11-07'
NASA_DAY_528 = '1963-11-08'


def semimajor_axis_km(n_rev_day: float) -> float:
    if not math.isfinite(n_rev_day) or n_rev_day <= 0:
        raise ValueError('invalid mean motion rev/day')
    n_rad_sec = math.tau * n_rev_day / SECONDS_PER_DAY
    return (MU_KM3_S2 / (n_rad_sec * n_rad_sec)) ** (1 / 3)


def secular_dadt_km_day(n_rev_day: float, dn_rev_day2: float) -> float:
    if not math.isfinite(dn_rev_day2):
        raise ValueError('invalid mean motion derivative')
    # n is in rev/day; dn/dt is in rev/day^2. Ratio is 1/day.
    return -2 * semimajor_axis_km(n_rev_day) * dn_rev_day2 / (3 * n_rev_day)


def strict_training(rows: list[dict], cutoff: datetime) -> list[dict]:
    if cutoff.utcoffset() != timedelta(0):
        raise ValueError('cutoff must be UTC')
    if any(a['epoch'] >= b['epoch'] for a, b in zip(rows, rows[1:])):
        raise ValueError('source epochs must be ordered and unique')
    if any(r['epoch'].utcoffset() != timedelta(0) for r in rows):
        raise ValueError('epochs must be UTC')
    return [r for r in rows if r['epoch'] < cutoff]


def rate_last_two(rows: list[dict]) -> float | None:
    if len(rows) < 2:
        return None
    gap_days = (rows[-1]['epoch'] - rows[-2]['epoch']).total_seconds() / SECONDS_PER_DAY
    if gap_days <= 0:
        raise ValueError('non-positive training gap')
    return (rows[-1]['mean_motion'] - rows[-2]['mean_motion']) / gap_days


def rate_median_three(rows: list[dict]) -> float | None:
    if len(rows) < 4:
        return None
    return median(rate_last_two(rows[i:i+2]) for i in range(len(rows)-4, len(rows)-1))


def assumed_utc_day_error(prediction: datetime, label: str) -> list[float]:
    """Only conditional on NASA's unspecified date being a UTC civil day.

    Error convention predicted minus actual; real NASA timezone/censoring unknown.
    """
    if len(label) != 10 or label[4] != '-' or label[7] != '-':
        raise ValueError('NASA source offers only an un-timed civil date label')
    start = datetime.fromisoformat(label).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return [round((prediction - end).total_seconds()/SECONDS_PER_DAY, 6),
            round((prediction - start).total_seconds()/SECONDS_PER_DAY, 6)]


def method(rows: list[dict], label: str, variant: str) -> dict:
    slope = rate_last_two(rows) if variant == 'last_two' else rate_median_three(rows)
    if slope is None:
        return {'status': 'NOT_ESTIMABLE_INSUFFICIENT_PRIOR_EPOCHS', 'scenarios': []}
    origin = rows[-1]
    dadt = secular_dadt_km_day(origin['mean_motion'], slope)
    result = {'status': 'HEURISTIC_ONLY' if dadt < 0 else 'NOT_ESTIMABLE_NON_DECAYING_SECANT',
              'dn_dt_rev_day2': round(slope, 10),
              'da_dt_km_day': round(dadt, 6),
              'semimajor_axis_kepler_proxy_km': round(semimajor_axis_km(origin['mean_motion']), 5),
              'scenarios': []}
    if dadt >= 0:
        return result
    for h in H_KM:
        t_days = h / abs(dadt)
        predicted = origin['epoch'] + timedelta(days=t_days)
        result['scenarios'].append({
            'H_eff_km_ASSUMED': h, 'life_remaining_days_HEURISTIC': round(t_days, 6),
            'hypothetical_terminal_utc': predicted.isoformat(timespec='seconds'),
            'error_days_if_NASA_label_means_UTC_civil_day': assumed_utc_day_error(predicted, label),
        })
    return result


def evaluate(rows: list[dict], cutoff_text: str, label: str, norad: int) -> dict:
    cutoff = datetime.fromisoformat(cutoff_text)
    training = strict_training(rows, cutoff)
    result = {'norad': norad, 'cutoff_utc_exclusive': cutoff_text,
              'NASA_reported_calendar_day_timezone_UNVERIFIED': label,
              'prior_catalogue_epochs': len(training),
              'source_rows_used_for_last_two': [r['source_row'] for r in training[-2:]],
              'origin_catalogue_epoch_utc': training[-1]['epoch'].isoformat() if training else None,
              'last_two': method(training, label, 'last_two') if training else {'status': 'NOT_ESTIMABLE', 'scenarios': []},
              'median_three_prior_secants': method(training, label, 'median_three') if training else {'status': 'NOT_ESTIMABLE', 'scenarios': []}}
    # This flag never becomes true from a single same-lineage date-only comparison.
    result['independent_terminal_time_validation'] = False
    return result


def report(groups: dict[int, list[dict]]) -> dict:
    if 528 not in groups or 637 not in groups:
        raise ValueError('both NORAD objects required')
    return {
        'schema': 'conde.c241-king-hele-uncalibrated-day-sensitivity/v1',
        'source': {'parquet_url': SOURCE_URL, 'sha256_verified_at_ingest': SOURCE_SHA256,
                   'catalogue_lineage': 'ONE_SECONDARY_SPACETRACK_MIRROR'},
        'method': {'mean_motion_units': 'rev/day', 'dn_dt_units': 'rev/day^2',
                   'da_dt_units': 'km/day', 'H_eff_km_exploratory': list(H_KM),
                   'origin_only_strict_before_cutoff': True,
                   'predictor': 'local-exponential-scale-height sensitivity, NOT propagated orbit',
                   'robust_diagnostic': 'median of three final adjacent pre-cutoff secants; no model selection',
                   'preinspection_of_labels': True,
                   'NASA_637_day': NASA_DAY_637, 'NASA_528_day': NASA_DAY_528,
                   'NASA_date_timezone_known': False,
                   'UTC_day_error_intervals_only_counterfactual': True,
                   'source_mean_motion_dot_used': False,
                   'perigee_used_as_semimajor_axis': False},
        'comparisons': [evaluate(groups[637], cut, NASA_DAY_637, 637) for cut in CUTOFFS_637] +
                       [evaluate(groups[528], CUTOFF_528, NASA_DAY_528, 528)],
        'inference': {'active_constraint': False, 'terminal_time_sigma_hours': None,
                      'impact_geography': None, 'historical_mcmc': 'NOT_RUN',
                      'objective_validation': 'NOT_ESTABLISHED_SINGLE_CATALOGUE_LINEAGE',
                      'meaning_of_H': 'retrospectively assumed, not independently measured',
                      'physics_caveat': 'near-circular, approximately fixed Cd*A/m, local exponential density; no terminal altitude or ballistic coefficient observed'},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parquet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    payload = report(extract_pinned(args.parquet))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')
    print('C241 KING-HELE: retrospective sensitivity only; historical MCMC NOT_RUN')
    for comparison in payload['comparisons']:
        print(comparison['norad'], comparison['cutoff_utc_exclusive'],
              comparison['origin_catalogue_epoch_utc'], comparison['last_two']['status'])
        for scenario in comparison['last_two']['scenarios']:
            print('  assumed H', scenario['H_eff_km_ASSUMED'],
                  'predicted UTC', scenario['hypothetical_terminal_utc'],
                  'conditional error days', scenario['error_days_if_NASA_label_means_UTC_civil_day'])


if __name__ == '__main__':
    main()
