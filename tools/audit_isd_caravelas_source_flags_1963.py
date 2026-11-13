#!/usr/bin/env python3
"""Custody check of source/report codes in Caravelas 1963 ISD observations."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'research/meteorology/isd_caravelas_19631107_09.zlib.b64'
MANIFEST = ROOT / 'research/meteorology/isd_caravelas_source_flags_1963.json'
GRAPH = ROOT / 'research/constraints/isd_caravelas_source_flags_edges_1963.json'
GZIP_SHA = 'c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05'
WINDOW_SHA = 'c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000'
DAYS = ('19631107', '19631108', '19631109')
EXPECTED_CODES = {'N': 72}
EXPECTED_REPORTS = {'BRAZ': 72}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def raw_window() -> bytes:
    value = zlib.decompress(base64.b64decode(SNAPSHOT.read_bytes().strip(), validate=True))
    if digest(value) != WINDOW_SHA:
        raise ValueError('Snapshot original changed')
    return value


def fields(lines: bytes, *, days: tuple[str, ...] | None = DAYS) -> dict:
    rows = lines.splitlines(keepends=True)
    sources, types, qcs, hours = Counter(), Counter(), Counter(), Counter()
    if not rows:
        raise ValueError('Empty source')
    for row in rows:
        if len(row) < 105 or not row.endswith(b'\n'):
            raise ValueError('Incomplete fixed-width ISD observation')
        if row[4:15] != b'83497099999':
            raise ValueError('Unexpected station identifier')
        day = row[15:23].decode('ascii')
        hhmm = row[23:27].decode('ascii')
        if days is not None and day not in days:
            raise ValueError('Unexpected observation date')
        if len(hhmm) != 4 or not hhmm.isdigit() or not (0 <= int(hhmm[:2]) < 24 and 0 <= int(hhmm[2:]) < 60):
            raise ValueError('Malformed UTC time')
        source = row[27:28].decode('ascii')
        report = row[41:46].decode('ascii').strip()
        qc = row[56:60].decode('ascii')
        if not source or not report or not qc:
            raise ValueError('Missing mandatory provenance field')
        sources[source] += 1
        types[report] += 1
        qcs[qc] += 1
        key = f'{day}T{hhmm}'
        hours[key] += 1
        if hours[key] != 1:
            raise ValueError('Duplicate observation timestamp')
    if days is not None and (len(rows) != 72 or
        any(sum(key.startswith(day) for key in hours) != 24 for day in DAYS) or
        any(f'{day}T{h:02d}00' not in hours for day in DAYS for h in range(24))):
        raise ValueError('Missing, off-hour, or incomplete three-day archive')
    return {'records': len(rows), 'source_flags': dict(sorted(sources.items())),
            'report_type_codes': dict(sorted(types.items())),
            'quality_process_raw': dict(sorted(qcs.items()))}


def verify_snapshot() -> dict:
    parsed = fields(raw_window())
    if parsed != {'records': 72, 'source_flags': EXPECTED_CODES,
                  'report_type_codes': EXPECTED_REPORTS, 'quality_process_raw': {'V020': 72}}:
        raise ValueError('Unexpected source-code composition in original window')
    return parsed


def verify_gzip(blob: bytes) -> dict:
    if digest(blob) != GZIP_SHA:
        raise ValueError('Annual NOAA gzip hash changed; investigate, do not silently update')
    raw = gzip.decompress(blob)
    result = fields(raw, days=None)
    if result != {'records': 8532, 'source_flags': {'N': 8532},
                  'report_type_codes': {'BRAZ': 8532}, 'quality_process_raw': {'V020': 8532}}:
        raise ValueError('Annual NOAA provenance distribution changed')
    excerpt = b''.join(row for row in raw.splitlines(keepends=True) if row[15:23].decode('ascii') in DAYS)
    if excerpt != raw_window():
        raise ValueError('Snapshot does not match original annual NOAA file')
    return result


def audit(annual: bytes | None = None) -> dict:
    window = verify_snapshot()
    if annual is not None:
        verify_gzip(annual)
    return {
        'schema': 'conde.meteorological-source-lineage/v1',
        'id': 'MET-ISD-CARAVELAS-SOURCE-FLAGS-1963-01',
        'source_url': 'https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz',
        'format_url': 'https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf',
        'format_edition': '2018-01-12 (retrospective decoding, not a 1963 instrument log)',
        'annual_gzip_sha256': GZIP_SHA,
        'window_sha256': WINDOW_SHA,
        'window_utc_days': list(DAYS),
        'window': window,
        'annual_count_verified_when_archive_supplied': 8532,
        'annual_source_flags_from_verified_gzip': {'N': 8532},
        'annual_report_type_codes_from_verified_gzip': {'BRAZ': 8532},
        'interpretation': {'N': 'NCAR / NCEI cooperative effort (various national datasets)',
                           'BRAZ': 'Dataset from Brazil'},
        'upstream_archive_or_originating_operator_1963': None,
        'original_station_instrument_1963': None,
        'independence_from_other_noaa_products': None,
        'historical_geographic_transfer_to_conde': None,
        'active_conde_constraint': None,
        'status': 'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION'
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--verify-full-gz', type=Path)
    args = parser.parse_args()
    result = audit(args.verify_full_gz.read_bytes() if args.verify_full_gz else None)
    if args.check:
        if result != json.loads(MANIFEST.read_text(encoding='utf-8')):
            raise SystemExit('Source flag manifest differs from original archive')
        graph = json.loads(GRAPH.read_text(encoding='utf-8'))
        if graph.get('source') != result['id'] or graph.get('active_conde_constraint') is not None or graph.get('status') != result['status']:
            raise SystemExit('Provenance graph improperly promotes a pending source')
        print('PASS: source-flag provenance matches snapshot, manifest and graph')
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
