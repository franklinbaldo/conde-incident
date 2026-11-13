#!/usr/bin/env python3
"""Audit the fixed-width Brazil station inventory in NOAA WWR series 6.

WWR is a decade-scale SURFACE monthly data series, not an upper-air profile.
Station header observations are extracted verbatim. This cannot establish the
absence of 1963 Recife observations from other archives.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / 'research/meteorology/wwr_brazil_1961_1970_recife_coverage.json'
HEADERS = ROOT / 'research/meteorology/wwr_brazil_1961_1970_station_headers.txt'
SOURCE_URL = 'https://www.ncei.noaa.gov/data/world-weather-records/series-6/access/data/WWR_v01_global_array_1961-1970.txt'
FULL_SHA256 = '5e0dfd3c64449a93bdf88f37dcf6ec81db5852c8d8fe08cb4fb2e77857577c09'
FULL_SIZE = 6840540


def extract_headers(blob: bytes) -> list[str]:
    """Read the station '1' records; preserve precisely all 89 bytes per row."""
    headers = []
    for row in blob.decode('ascii').splitlines():
        if len(row) == 89 and row[7] == '1' and row[19:25] == 'BRAZIL':
            if not row[2:7].isdigit():
                raise ValueError('non-numeric WMO identifier')
            headers.append(row)
    return headers


def manifest_from_headers(headers: list[str]) -> dict:
    ids = [row[2:7] for row in headers]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicated station id')
    data = '\n'.join(headers) + '\n'
    return {
        'schema': 'conde.noaa-wwr-1961-1970-coverage/v1',
        'evidence': 'WWR-S6-1963-BRAZIL-RECIFE-COVERAGE',
        'source': {
            'url': SOURCE_URL, 'provider': 'NOAA/NCEI World Weather Records series 6',
            'coverage': '1961-1970; surface monthly/annual summaries',
            'sha256': FULL_SHA256, 'bytes': FULL_SIZE,
            'snapshot_header_sha256': hashlib.sha256(data.encode('ascii')).hexdigest(),
            'station_header_width_bytes': 89,
        },
        'brazil_station_header_count': len(headers),
        'brazil_station_ids': ids,
        'recife_wmo_candidates': ['82899', '82900'],
        'recife_wmo_candidates_present': [x for x in ('82899', '82900') if x in ids],
        'station_names_containing_recife_or_curado': [row[40:66].strip() for row in headers
                                                   if 'RECIFE' in row[40:66] or 'CURADO' in row[40:66]],
        'independent_upper_air_observation': False,
        'reported_actual_1963_11_08_wind': False,
        'spatial_transfer_calibration': None,
        'historical_1963_station_metadata_resolved': False,
        'claim': 'Recife/Curado (82899/82900) not listed among 21 Brazilian stations in this WWR series-6 file only',
        'interpretation': 'WWR absence is archive-specific; cannot negate IGRA Recife soundings, identify 1963 radiosonde, or bound atmospheric drift in Conde',
        'links': ['C149', 'C150', 'C151', 'C193'],
        'status': 'CONNECTED_PENDING_CALIBRATION',
    }


def verify_snapshot(expected: dict) -> None:
    data = HEADERS.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected['source']['snapshot_header_sha256']:
        raise ValueError('header excerpt has changed')
    headers = extract_headers(data)
    observed = manifest_from_headers(headers)
    if observed != expected:
        raise ValueError('manifest does not match the Brazilian station header excerpt')
    if observed['brazil_station_header_count'] != 21:
        raise ValueError('Brazilian header count unexpectedly changed')
    if observed['recife_wmo_candidates_present'] or observed['station_names_containing_recife_or_curado']:
        raise ValueError('Recife appears in the station inventory')


def download_full_and_verify(expected: dict) -> None:
    with urllib.request.urlopen(SOURCE_URL, timeout=35) as r:
        raw = r.read()
    if len(raw) != FULL_SIZE or hashlib.sha256(raw).hexdigest() != FULL_SHA256:
        raise ValueError('full NOAA source changed or download truncated')
    if extract_headers(raw) != extract_headers(HEADERS.read_bytes()):
        raise ValueError('snapshot headers differ from the NOAA source')
    if manifest_from_headers(extract_headers(raw)) != expected:
        raise ValueError('full NOAA source differs from expected manifest')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='verify pinned local excerpt and manifest')
    ap.add_argument('--download', action='store_true', help='also verify live NOAA full-file SHA-256')
    args = ap.parse_args()
    expected = json.loads(ARTIFACT.read_text(encoding='utf-8'))
    verify_snapshot(expected)
    if args.download:
        download_full_and_verify(expected)
    print('PASS NOAA WWR 1961-1970: 21 Brazil headers; WMO 82899/82900 absent; no physical transfer claimed')


if __name__ == '__main__':
    main()
