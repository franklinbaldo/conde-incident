#!/usr/bin/env python3
"""C241-P29: source-pinned GCAT time axes, without invented sensor epochs.

This checks copied TSV *rows* and full-file provenance digests from a dated
GCAT download. It does not replay the live website or certify the original
1963 sensor records. No synthetic observations and no Θ activation.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'research/tle_custody/gcat_time_axes_527_529_C241-P29.json'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError('C241-P29 GCAT time axes: ' + message)


def parse_rows(source: dict, expected: tuple[int, ...]) -> dict[int, dict[str, str]]:
    require(set(source['rows']) == set(map(str, expected)), 'missing/extra object')
    names = source['header'].lstrip('#').split('\t')
    require(len(names) == len(set(names)), 'duplicate TSV field name')
    result = {}
    for number in expected:
        entry = source['rows'][str(number)]
        raw = entry['line'].encode()
        require(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'row digest changed')
        cells = entry['line'].split('\t')
        require(len(names) == len(cells), 'row/header field count changed')
        data = {k: v.strip() for k, v in zip(names, cells)}
        require(data['JCAT'] == f'S{number:05d}', 'object identity changed')
        require(data['Piece'] == f'1963-003{chr(65+number-527)}', 'COSPAR identity changed')
        result[number] = data
    return result


def ymd(raw: str) -> tuple[int, int, int]:
    match = re.match(r'^(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:\s.*)?$', raw)
    require(match is not None, 'unresolved date')
    return (int(match[1]), datetime.strptime(match[2], '%b').month, int(match[3]))


def replay_full_tsv(ledger: dict, directory: Path) -> None:
    """Optional actual-file replay; full files are not embedded in Git."""
    for kind, source in ledger['sources'].items():
        path = directory / f'{"psatcat" if kind == "payload" else "currentcat"}.tsv'
        raw = path.read_bytes()
        require(len(raw) == source['bytes_full_tsv']
                and hashlib.sha256(raw).hexdigest() == source['sha256_full_tsv'],
                f'{kind}: full TSV digest/size mismatch')
        lines = raw.decode('utf-8').splitlines()
        require(lines[0] == source['header'], f'{kind}: TSV header mismatch')
        for number, saved in source['rows'].items():
            matches = [line for line in lines[1:]
                       if line.split('\t', 1)[0].strip() == f'S{int(number):05d}']
            require(len(matches) == 1 and matches[0] == saved['line'],
                    f'{kind} {number}: full TSV origin mismatch')


def audit(ledger: dict) -> dict:
    require(ledger.get('schema') == 'conde.gcat-time-axes/v1', 'schema changed')
    require(set(ledger['sources']) == {'payload', 'object'}, 'missing source family')
    require(ledger['gc_version'].startswith('GCAT 1.8.9'), 'release provenance changed')
    for source in ledger['sources'].values():
        require(re.fullmatch(r'[a-f0-9]{64}', source['sha256_full_tsv']) is not None
                and source['bytes_full_tsv'] > 100_000, 'full source custody lost')
    payload_source, orbital_source = ledger['sources']['payload'], ledger['sources']['object']
    require(payload_source['url'].endswith('/cat/psatcat.tsv')
            and orbital_source['url'].endswith('/derived/currentcat.tsv'), 'source namespace swapped')
    payload = parse_rows(payload_source, (527,))[527]
    orbital = parse_rows(orbital_source, (527, 528, 529))
    require({'TLast', 'TOp', 'TDate'} <= payload.keys()
            and 'DDate' not in payload, 'payload operation vs decay column confusion')
    require('DDate' in orbital[527] and 'TDate' not in orbital[527],
            'orbital decay vs payload operations column confusion')
    require(all(ymd(payload[f]) == (1963, 1, 18) for f in ('TLast', 'TOp', 'TDate')),
            '527 payload operations/transmissions changed')
    require(ymd(orbital[527]['DDate']) == (1969, 1, 9), '527 orbital decay date changed')
    require('attached to A00324' in orbital[527]['ExpandedStatus'],
            '527 attachment status changed')
    require(orbital[527]['Parent'] == 'A00324'
            and orbital[528]['Parent'] == orbital[529]['Parent'] == 'S00527',
            'parent/object genealogy changed')
    require(ymd(orbital[528]['DDate']) == (1963, 11, 8)
            and ymd(orbital[529]['DDate']) == (1963, 12, 31),
            'secondary catalog decay day changed')
    # This source prints only a day for 528/529, not an instrument hour.
    require(all(re.fullmatch(r'1963\s+(Nov|Dec)\s+\d{1,2}', orbital[n]['DDate'])
                for n in (528, 529)), 'invented precision in 528/529 catalog day')
    require(ymd(payload['TDate']) < ymd(orbital[527]['DDate']),
            'payload silence cannot be confused with orbital disappearance')
    require(ymd(orbital[527]['DDate']) > (1963, 11, 8),
            '527 cannot be excluded as a post-528-date catalog control')
    limits = ledger['interpretation']
    require(limits == {
        'end_of_transmission_is_not_reentry': True,
        'catalog_snapshot_is_not_an_instrumental_observation': True,
        'shared_gcat_lineage_not_independent': True,
        '527_remains_possible_survivor_control_on_1963_11_08': True,
        'new_instrumental_measurements': 0,
        'physical_domain_effect': 'THETA_UNCHANGED',
    }, 'unsupported sensor or physical interpretation')
    return {'schema': ledger['schema'], 'payload_end_date_527': '1963-01-18',
            'orbital_decay_dates': {str(n): '-'.join(f'{v:02d}' for v in ymd(orbital[n]['DDate']))
                                    for n in (527,528,529)},
            'observation_epoch_utc': None, 'physical_domain_effect': 'THETA_UNCHANGED'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--replay-source-dir', type=Path, help='dir containing full psatcat.tsv/currentcat.tsv')
    args = parser.parse_args()
    ledger = json.loads(LEDGER.read_text())
    if args.replay_source_dir is not None:
        replay_full_tsv(ledger, args.replay_source_dir)
    result = audit(ledger)
    if args.check:
        print('PASS: GCAT operational/decay dates separated; no instrumental activation')
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
