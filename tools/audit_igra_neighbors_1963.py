#!/usr/bin/env python3
"""Source-locked IGRA 1963 availability, not a spatial atmosphere model."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'research/meteorology/igra_nearby_1963_source_refresh.json'
BASE = 'https://www.ncei.noaa.gov/pub/data/igra/data/data-por/'
DATE = '2026-11-13'
SOURCES = {
    'BRM00082599': ('NATAL (AERO)', 19067487, 'e8ffc9be391d97674b95624eda8d57cd94ddac599404cdea775aa6e95202f7be'),
    'BRM00082900': ('RECIFE (82900-0)', 7834492, 'df4fcd10e1920723b3cf337b745301b505810ee1dc8a6c5006b84e52b2c871df'),
    'BRM00083229': ('SALVADOR (83229-0)', 6115358, 'd6bd80590ec72906726def8959df95b99f6abf9be0752b505c7c7d0c33c5e240'),
}
EXPECTED_COUNTS = {
    'BRM00082599': (20448, 0, '1943-10-18', '1946-02-28', '1967-01-18'),
    'BRM00082900': (14977, 346, '1952-07-01', '1962-12-31', '1964-01-01'),
    'BRM00083229': (7954, 0, '1970-01-02', None, '1970-01-02'),
}
OLD_RECIFE_ZIP = '0655b3ea80312abe888a5474f82233affc0a2496ee1fd8bc678162924f52ecdc'
OLD_EXCERPTS = {
    '07': 'd77a3bc79935199cc5606a21a464f2836edc1191105ea44a03e58a3fce8375c6',
    '08': '577224172e19552f5ce87081897479255596dc44debacc674dfd9d9ec418207e',
    '09': '73e963250891689bf39baf5c29963dd3e42ed13180cf72355237cf98a70d00b2',
}


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def local_excerpt(day: str) -> bytes:
    f = ROOT / f'research/meteorology/igra_recife_196311{day}_raw.txt.b64'
    result = base64.b64decode(f.read_bytes(), validate=False)
    if digest(result) != OLD_EXCERPTS[day]:
        raise ValueError('historical Recife excerpt changed: ' + day)
    return result


def header_date(line: bytes, expected_station: str) -> str:
    if not line.startswith(('#' + expected_station).encode('ascii')) or len(line) < 72:
        raise ValueError('station/header mismatch')
    date = line[13:23].decode('ascii')
    if len(date) != 10 or date[4] != ' ' or date[7] != ' ':
        raise ValueError('invalid header date')
    year, month, day = (int(s) for s in date.split())
    if not 1900 <= year <= 2100 or not 1 <= month <= 12 or not 1 <= day <= 31:
        raise ValueError('out of range date')
    return f'{year:04d}-{month:02d}-{day:02d}'


def inspect_archive(archive: Path, station: str) -> dict:
    name, expected_bytes, expected_sha = SOURCES[station]
    raw = archive.read_bytes()
    if len(raw) != expected_bytes or digest(raw) != expected_sha:
        raise ValueError('full archive integrity mismatch: ' + station)
    counts = Counter()
    year1963_window = []
    selected = {}
    first = last_before = first_after = None
    with ZipFile(archive) as zipf:
        member = f'{station}-data.txt'
        pending = None
        buf = []
        with zipf.open(member) as handle:
            for line in handle:
                if not line.startswith(b'#'):
                    if pending in OLD_EXCERPTS and station == 'BRM00082900':
                        buf.append(line)
                    continue
                if pending in OLD_EXCERPTS and station == 'BRM00082900':
                    selected[pending] = b''.join(buf)
                date = header_date(line, station)
                year = int(date[:4])
                counts[year] += 1
                if year < 1963:
                    last_before = date
                if year > 1963 and first_after is None:
                    first_after = date
                if first is None:
                    first = date
                if date in ('1963-11-07','1963-11-08','1963-11-09'):
                    year1963_window.append(date)
                pending = date[-2:] if date in ('1963-11-07','1963-11-08','1963-11-09') else None
                buf = [line] if pending is not None else []
        if pending in OLD_EXCERPTS and station == 'BRM00082900':
            selected[pending] = b''.join(buf)
    if station == 'BRM00082900':
        for day, sha in OLD_EXCERPTS.items():
            if day not in selected or digest(selected[day]) != sha or selected[day] != local_excerpt(day):
                raise ValueError('Recife 1963 historical excerpt has changed: ' + day)
    return {
        'station_id': station, 'catalogue_name': name,
        'snapshot_zip_bytes': len(raw), 'snapshot_zip_sha256': digest(raw),
        'first_report_date': first, 'last_before_1963': last_before,
        'first_after_1963': first_after,
        'total_sounding_headers': sum(counts.values()),
        'sounding_headers_1963': counts[1963],
        'dates_1963_nov_07_to_09': year1963_window,
        'nov_1963_excerpt_matches_previous_sha': (
            {d: OLD_EXCERPTS[d] for d in OLD_EXCERPTS} if station == 'BRM00082900' else None
        ),
    }


def derive(source_dir: Path) -> dict:
    by_station = [inspect_archive(source_dir / f'{id}-data.txt.zip', id) for id in SOURCES]
    if [e['sounding_headers_1963'] for e in by_station] != [0, 346, 0]:
        # Only station-specific source coverage, never an absence of historical launches.
        raise ValueError('unexpected observed year-1963 archive coverage')
    recife = by_station[1]
    if recife['dates_1963_nov_07_to_09'] != [f'1963-11-{d}' for d in OLD_EXCERPTS]:
        raise ValueError('changed window coverage')
    return {
        'schema': 'conde.igra-nearby-source-refresh/v1',
        'observation_date_utc': DATE,
        'sources': {
            'archive_pattern': BASE + '{station_id}-data.txt.zip',
            'official_station_list': 'https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt',
            'official_station_list_sha256_at_retrieval': '9515d29b0c61fcfc912028830c37f47e723ba32c14d88fb48cf6d8bf727060ab',
            'source_institution': 'NOAA/NCEI',
            'raw_zip_snapshot_is_not_committed': True,
        },
        'stations': by_station,
        'recife_archive_previously_pinned_sha256': OLD_RECIFE_ZIP,
        'recife_current_zip_sha_differs_from_older_pin': recife['snapshot_zip_sha256'] != OLD_RECIFE_ZIP,
        'recife_1963_nov_07_09_original_byte_excerpts_unchanged': True,
        'cause_of_whole_zip_change': None,
        'conclusions': {
            'nearby_Natal_and_Salvador_have_no_1963_headers_in_these_IGRA_station_archives': True,
            'no_historical_launch_in_those_cities_in_1963': None,
            'independent_regional_wind_profile_for_1963_11_08': None,
            'recife_to_conde_transfer_error_m_s': None,
            'calibrated_instrument_error': None,
            'geographic_or_orbital_constraint_activated': False,
            'status': 'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION',
            'evidence_links': ['C149','C150','C151'],
        },
    }


def validate_card(card: dict) -> None:
    if card['schema'] != 'conde.igra-nearby-source-refresh/v1':
        raise ValueError('schema mismatch')
    stations = card['stations']
    if [x['station_id'] for x in stations] != list(SOURCES):
        raise ValueError('wrong stations')
    for row in stations:
        name, size, hashvalue = SOURCES[row['station_id']]
        if row['snapshot_zip_bytes'] != size or row['snapshot_zip_sha256'] != hashvalue:
            raise ValueError('unrecognized source snapshot')
        expected = EXPECTED_COUNTS[row['station_id']]
        actual = (row['total_sounding_headers'], row['sounding_headers_1963'],
                  row['first_report_date'], row['last_before_1963'], row['first_after_1963'])
        if actual != expected:
            raise ValueError('unrecognized station/year coverage')
        if row['station_id'] != 'BRM00082900' and (row['dates_1963_nov_07_to_09'] or row['nov_1963_excerpt_matches_previous_sha'] is not None):
            raise ValueError('falsified neighbor coverage')
    for day in OLD_EXCERPTS:
        local_excerpt(day)
    if (card['recife_archive_previously_pinned_sha256'] != OLD_RECIFE_ZIP
        or not card['recife_current_zip_sha_differs_from_older_pin']
        or card['cause_of_whole_zip_change'] is not None
        or stations[1]['nov_1963_excerpt_matches_previous_sha'] != OLD_EXCERPTS
        or stations[1]['dates_1963_nov_07_to_09'] != [f'1963-11-{d}' for d in OLD_EXCERPTS]):
        raise ValueError('invalid historical-versus-current provenance')
    q = card['conclusions']
    if (q['recife_to_conde_transfer_error_m_s'] is not None
        or q['calibrated_instrument_error'] is not None
        or q['geographic_or_orbital_constraint_activated']
        or q['no_historical_launch_in_those_cities_in_1963'] is not None
        or q['independent_regional_wind_profile_for_1963_11_08'] is not None):
        raise ValueError('unwarranted promotion of archival data into physics')
    if not card['recife_1963_nov_07_09_original_byte_excerpts_unchanged']:
        raise ValueError('old excerpts unexpectedly changed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, help='directory containing all three downloaded source ZIPs')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    published = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else None
    if args.source_dir:
        observed = derive(args.source_dir)
        if args.check and observed != published:
            raise SystemExit('published source snapshot mismatch')
        if not args.check:
            OUTPUT.write_text(json.dumps(observed, indent=2, ensure_ascii=False) + '\n')
        validate_card(observed)
    else:
        if published is None:
            raise SystemExit('no published capture; provide --source-dir')
        validate_card(published)
    print('PASS: source snapshots and 1963 interpretation checks')


if __name__ == '__main__':
    main()
