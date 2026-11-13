#!/usr/bin/env python3
"""Audit catalog-day vs TLE snapshot coverage; no survival inference.

The 1963-003B NASA 'decay' day is a status-report label. A source
without observation/retention process cannot yield a missingness likelihood.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = 'research/statistics/raan_527_528_529_1963.json'
IDENTITY = 'research/tle_custody/catalog_identity_527_529_2026-11-12.json'
SPLIT = 'research/statistics/raan_chronological_holdout_1963.json'
OUTPUT = 'research/statistics/raan_catalog_day_missingness_C241.json'


def timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith('Z'):
        raise ValueError('UTC timestamp must end in Z')
    try:
        parsed = datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError as exc:
        raise ValueError('invalid UTC timestamp') from exc
    if parsed.tzinfo != timezone.utc:
        raise ValueError('timestamp not UTC')
    return parsed


def day(value: str) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError('catalog day must be ISO YYYY-MM-DD')
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError('noncanonical catalog day')
    return result


def digest(data: bytes, path: str) -> dict:
    return {'path': path, 'sha256': hashlib.sha256(data).hexdigest()}


def build(series_bytes: bytes, identity_bytes: bytes, split_bytes: bytes) -> dict:
    series = json.loads(series_bytes)
    identity = json.loads(identity_bytes)
    split = json.loads(split_bytes)
    primary = identity['primary_date_only_record']
    if (primary['catalog_designator_printed'] != '1963 3B'
            or primary['document_id'] != 'NASA NTRS 19640001198'
            or primary['decay_day'] != '1963-11-08'):
        raise ValueError('primary day-only documentary binding drift')
    if split['unique_total'] != 119:
        raise ValueError('chronological frozen membership drift')
    if (split['boundaries']['fit_before_utc'] != '1963-08-01T00:00:00Z'
            or split['boundaries']['evaluation_from_utc'] != '1963-10-01T00:00:00Z'):
        raise ValueError('frozen calendar contract drift')
    observed: dict[int, set[str]] = {527: set(), 528: set(), 529: set()}
    duplicate_counts = {k: 0 for k in observed}
    for row in series['records']:
        obj = row['norad']
        if type(obj) is not int or obj not in observed:
            raise ValueError('unexpected NORAD object')
        stamp = row['epoch_utc']
        instant = timestamp(stamp)
        if instant.year != 1963:
            raise ValueError('this source is only the 1963 excerpt')
        if type(row['raan_deg']) not in (float, int) or not (0 <= row['raan_deg'] < 360):
            raise ValueError('RAAN not within circular domain')
        if stamp in observed[obj]:
            duplicate_counts[obj] += 1
        observed[obj].add(stamp)
    unique = sum(map(len, observed.values()))
    if unique != split['unique_total']:
        raise ValueError('catalog series and frozen split disagree')
    for k, epochs in observed.items():
        members = split['memberships'][str(k)]
        all_frozen = members['fit'] + members['validation'] + members['evaluation']
        if set(all_frozen) != epochs or len(all_frozen) != len(epochs):
            raise ValueError('membership changed; do not peek/change holdouts')
    rows = {}
    for k in (527, 528, 529):
        label = identity['sources'][f'itau_{k}']
        if label['catalog'] != k or label['international_designator'] != f'1963-003{chr(k-527+65)}':
            raise ValueError('modern catalog object/designator mismatch')
        status_day = day(label['decay_day'])
        if k == 528 and label['decay_day'] != primary['decay_day']:
            raise ValueError('NASA and modern 528 catalog day mismatch')
        epochs = sorted(timestamp(t) for t in observed[k])
        label_start = datetime(status_day.year, status_day.month, status_day.day, tzinfo=timezone.utc)
        before = [t for t in epochs if t < label_start]
        on_or_after = [t for t in epochs if t >= label_start]
        # Not a verified silence period or event-time estimate. Days are exact fractions.
        delta = label_start - epochs[-1]
        microseconds = ((delta.days * 86400 + delta.seconds) * 1000000
                        + delta.microseconds)
        gap = Fraction(microseconds, 86400000000)
        rows[str(k)] = {
            'catalog_designator': label['international_designator'],
            'catalog_status_day': status_day.isoformat(),
            'catalog_status_source_kind': ('NASA_PRIMARY_DAY_ONLY_REPORT' if k == 528
                                           else 'MODERN_SECONDARY_CATALOG_DAY'),
            'source_scope': 'SECONDARY_MIRROR_ONLY_1963_EXCERPT',
            'unique_1963_epochs': len(epochs),
            'excluded_same_object_same_epoch_duplicates': duplicate_counts[k],
            'first_mirror_epoch_utc': epochs[0].isoformat().replace('+00:00', 'Z'),
            'last_mirror_epoch_utc': epochs[-1].isoformat().replace('+00:00', 'Z'),
            'mirror_epochs_on_or_after_status_day_start': len(on_or_after),
            'gap_last_mirror_epoch_to_status_day_start_days_exact': (
                f'{gap.numerator}/{gap.denominator}'
                if gap >= 0 and status_day.year == 1963 else None),
            'gap_not_computed_reason': ('SOURCE_EXCERPT_ONLY_1963'
                                        if status_day.year != 1963 else None),
            'gap_is_surveillance_interval': False,
            'status_day_is_observed_terminal_time': False,
            'status_day_is_observed_non_detection_time': False,
        }
    return {
        'schema': 'conde.catalog-day-missingness/v1',
        'classification': 'DOCUMENTARY_COVERAGE_AUDIT_NOT_EVENT_TIME_INFERENCE',
        'sources': {
            'secondary_mirror': digest(series_bytes, SERIES),
            'object_identity': digest(identity_bytes, IDENTITY),
            'frozen_retrospective_split': digest(split_bytes, SPLIT),
            'primary_528_status_report': {
                'document_id': primary['document_id'],
                'publication_date': primary['publication_date'],
                'printed_page': primary['printed_page'],
                'url': primary['url'],
                'epistemic_status': primary['kind'],
            },
        },
        'objects': rows,
        'inference_gates': {
            'historical_surveillance_schedule': None,
            'detection_probability_by_epoch': None,
            'catalog_retention_and_selection_model': None,
            'status_label_to_physical_event_model': None,
            'historical_missingness_likelihood': 'NOT_IDENTIFIED',
            'terminal_utc_time': 'NOT_IDENTIFIED',
            'geographical_exclusion': 'NOT_RUN',
            'historical_posterior': 'NOT_RUN',
            'active_constraint': False,
        },
        'interpretation': ('A gap between secondary mirror epochs and a cataloged '
                           'day is absence of retained rows, not an observed negative '
                           'sensor event. Day-only NASA 1963-003B label cannot be '
                           'converted into survival/terminal-time likelihood without '
                           'documented sampling, retention and reporting models.'),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = build(*(ROOT.joinpath(p).read_bytes() for p in (SERIES, IDENTITY, SPLIT)))
    rendered = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    dest = ROOT / OUTPUT
    if args.check:
        if dest.read_text(encoding='utf-8') != rendered:
            raise SystemExit('drift: regenerate explicit coverage report')
        print('PASS: day-only / missingness report matches pinned inputs')
    else:
        dest.write_text(rendered, encoding='utf-8')
        print(f'written {dest.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
