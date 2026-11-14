#!/usr/bin/env python3
"""Auditoria de reapresentação pública do TLE 00688, sem promover observação nova."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path

from c241_688_terminal_holdout_readiness import (SOURCE_SHA256, extract_pinned)

# Transcrição de tabela pública secundária, inspecionada em 2026-11-14.
# Não é documento instrumental nem download preservado/hasheado da página.
PUBLIC_URL = 'https://www.sitewww.magnetic-declination.com/satellite/?s=688'
CELESTRAK_ARCHIVE = 'https://celestrak.org/NORAD/archives/'
LINE1 = '1 00688U 63044  B 63315.69103145  .00208208 +00000-0 +00000-0 0  9996'
LINE2 = '2 00688 065.0766 179.9815 0017115 312.1646 047.6913 16.29621717000071'


def checksum(line: str) -> int:
    return sum(int(ch) if ch.isdigit() else int(ch == '-') for ch in line[:68]) % 10


def parse_tle(line1: str, line2: str) -> dict:
    for expected, line in (('1', line1), ('2', line2)):
        if len(line) != 69 or line[0] != expected or not line[68].isdigit():
            raise ValueError('invalid TLE length/line identifier')
        if checksum(line) != int(line[68]):
            raise ValueError('TLE checksum mismatch')
    if line1[2:7] != '00688' or line2[2:7] != '00688':
        raise ValueError('different NORAD object')
    if line1[9:17] != '63044  B':
        raise ValueError('different international designator')
    if line1[18:20] != '63' or not line1[20:32].replace('.', '', 1).isdigit():
        raise ValueError('invalid historical TLE year/day')
    day = float(line1[20:32])
    if not (1 <= day < 366):
        raise ValueError('invalid day-of-year')
    epoch = datetime(1963, 1, 1, tzinfo=timezone.utc) + timedelta(days=day-1)
    n = float(line2[52:63])
    if not math.isfinite(n) or n <= 0:
        raise ValueError('invalid mean motion')
    return {'object_id': 688, 'international_designator': '63044  B',
            'epoch_utc': epoch, 'mean_motion_rev_day': n,
            'line1_checksum_valid': True, 'line2_checksum_valid': True}


def audit(public: dict, catalogue: dict[int, list[dict]]) -> dict:
    if set(catalogue) != {687, 688} or len(catalogue[688]) != 1:
        raise ValueError('pinned-catalogue cardinality changed: audit needs 1 epoch for 688')
    historical = catalogue[688][0]
    same_epoch = abs((public['epoch_utc']-historical['epoch']).total_seconds()) < .5
    same_n = abs(public['mean_motion_rev_day']-historical['mean_motion_rev_day']) < 1e-8
    matched = same_epoch and same_n
    return {
        'schema': 'c241-688-public-tle-duplicate/v1',
        'public_source': {'url': PUBLIC_URL, 'transcription_date': '2026-11-14',
                          'kind': 'SECONDARY_PUBLIC_TLE_TRANSCRIPTION',
                          'page_binary_sha256': None},
        'catalogue': {'sha256': SOURCE_SHA256, 'kind': 'PINNED_SECONDARY_REPLAY'},
        'object_id': public['object_id'],
        'public_epoch_utc': public['epoch_utc'].isoformat(),
        'catalogue_epoch_utc': historical['epoch'].isoformat(),
        'public_mean_motion_rev_day': public['mean_motion_rev_day'],
        'catalogue_mean_motion_rev_day': historical['mean_motion_rev_day'],
        'same_epoch_within_half_second': same_epoch,
        'same_mean_motion_within_1e_8_rev_day': same_n,
        'independent_new_epoch_found': not same_epoch,
        'independent_instrument_or_lineage_demonstrated': False,
        'duplicate_state_candidate': matched,
        'identifiability': {
            '688_unique_epoch_count_in_pinned_catalogue': 1,
            '688_secant_identifiable_from_pinned_plus_public': not same_epoch,
            'source_independence': 'NOT_DEMONSTRATED',
            'terminal_sigma_hours': None,
            'historical_mcmc': 'NOT_RUN',
            'active_constraint_528': False,
            'impact_geography_528': None,
        },
        'next_acquisition': {'archive': CELESTRAK_ARCHIVE,
                             'request': 'dated historical element sets for 688 prior to 1963-11-12T22:10Z; station, observational errors and source lineage',
                             'archive_note': 'special data request route; not evidence that additional elements exist'},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parquet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    public = parse_tle(LINE1, LINE2)
    result = audit(public, extract_pinned(args.parquet))
    if not result['duplicate_state_candidate']:
        raise SystemExit('REVIEW_REQUIRED: public TLE does not match pinned orbit, inspect manually')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('688: public TLE reproduces pinned epoch and mean motion; no second orbit; MCMC NOT_RUN')


if __name__ == '__main__':
    main()
