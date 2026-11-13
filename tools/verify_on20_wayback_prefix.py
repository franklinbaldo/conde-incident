#!/usr/bin/env python3
"""Verify historical ON20 Wayback captures, rejecting a truncated PDF-prefix."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

MANIFEST = (Path(__file__).resolve().parents[1]
            / 'research/archive/on20_wayback_prefix_20261113.json')
ORIGINAL = ('http://www.ncep.noaa.gov/officenotes/'
            'NOAA-NPM-NCEPON-0001/013FD4DB.pdf')
STAMPS = ('20080724202155', '20080920175518', '20220119075333')
EXPECTED_ASSESSMENTS = ('TRUNCATED_PREFIX_NOT_RECOMMENDED',
                        'COMPLETE_PDF_REPLAY', 'COMPLETE_PDF_REPLAY')


def validate(doc: dict) -> list[str]:
    """Check the frozen manifest only. Not a substitute for HTTP replay."""
    errors: list[str] = []
    if doc.get('schema') != 'conde.on20-wayback-prefix/v1':
        errors.append('schema mismatch')
    if doc.get('document_id') != 'MET-NMC-NCEPON-20261112-02':
        errors.append('source identifier mismatch')
    if doc.get('document_publication_year') != 1964:
        errors.append('document date mismatch')
    if doc.get('original_url') != ORIGINAL:
        errors.append('original URL mismatch')
    rows = doc.get('snapshots')
    if not isinstance(rows, list) or len(rows) != 3:
        return errors + ['exactly three snapshots required']
    flags = doc.get('comparison') or {}
    for key in ('earliest_pdf_is_complete',
                'distinct_cdx_sha1_digests_imply_distinct_historical_editions',
                'cdx_length_is_downloaded_pdf_bytes',
                'new_meteorological_observation', 'new_orbital_constraint'):
        if flags.get(key) is not False:
            errors.append(f'false provenance assertion: {key}')
    if flags.get('applicability_to_Y20175_1963') != 'NOT_ESTABLISHED':
        errors.append('1963 applicability cannot be inferred')
    if flags.get('earliest_is_exact_byte_prefix_of_complete_replay') is not True:
        errors.append('missing prefix observation')
    if flags.get('two_complete_replays_identical') is not True:
        errors.append('later replay equality unrecorded')
    if flags.get('prefix_bytes') != 130826:
        errors.append('prefix byte count mismatch')
    for index, (row, stamp, assessment) in enumerate(zip(rows, STAMPS, EXPECTED_ASSESSMENTS)):
        cdx, replay = row.get('cdx') or {}, row.get('replay') or {}
        if cdx.get('timestamp') != stamp:
            errors.append(f'{index}: unexpected CDX timestamp')
        try:
            datetime.strptime(str(cdx.get('timestamp')), '%Y%m%d%H%M%S')
        except (TypeError, ValueError):
            errors.append(f'{index}: invalid UTC timestamp')
        if cdx.get('original') != ORIGINAL:
            errors.append(f'{index}: CDX source URL mismatch')
        if row.get('archived_url') != (f'https://web.archive.org/web/{stamp}id_/{ORIGINAL}'):
            errors.append(f'{index}: archive URL not grounded in CDX')
        if cdx.get('statuscode') != '200' or cdx.get('mimetype') != 'application/pdf':
            errors.append(f'{index}: CDX did not report HTTP 200 PDF')
        if not isinstance(cdx.get('length'), int) or cdx['length'] <= 0:
            errors.append(f'{index}: invalid CDX WARC length')
        if not re.fullmatch(r'[A-Z2-7]{32}', str(cdx.get('digest', ''))):
            errors.append(f'{index}: invalid CDX SHA-1 Base32')
        if cdx.get('digest') != replay.get('sha1_base32'):
            errors.append(f'{index}: CDX/replay SHA-1 mismatch')
        if replay.get('http_status') != 200 or replay.get('content_type') != 'application/pdf':
            errors.append(f'{index}: replay not HTTP 200 PDF')
        if replay.get('pdf_header') is not True:
            errors.append(f'{index}: missing PDF header')
        if replay.get('pdf_eof') is not (index != 0):
            errors.append(f'{index}: unexpected PDF EOF state')
        if not isinstance(replay.get('bytes'), int) or replay['bytes'] < 100:
            errors.append(f'{index}: invalid payload length')
        if not re.fullmatch(r'[0-9a-f]{64}', str(replay.get('sha256', ''))):
            errors.append(f'{index}: invalid payload SHA-256')
        if row.get('assessment') != assessment:
            errors.append(f'{index}: incorrect recommended use')
    first, middle, last = [row.get('replay') or {} for row in rows]
    if first.get('bytes') != flags.get('prefix_bytes'):
        errors.append('first PDF not declared prefix-length')
    if first.get('bytes', 0) >= middle.get('bytes', 0):
        errors.append('early PDF not shorter than complete replay')
    if middle.get('bytes') != last.get('bytes') or middle.get('sha256') != last.get('sha256'):
        errors.append('complete replay payloads are not equal')
    if first.get('sha256') == middle.get('sha256'):
        errors.append('truncated replay not distinguished by SHA-256')
    if (rows[0].get('cdx') or {}).get('digest') == (rows[1].get('cdx') or {}).get('digest'):
        errors.append('early CDX digest not distinct from complete capture')
    return errors


def payload_errors(row: dict, data: bytes, *, http_status: int, content_type: str) -> list[str]:
    """Compare actual downloaded bytes with independently pinned archive metadata."""
    r, cdx = row['replay'], row['cdx']
    errors = []
    if http_status != 200:
        errors.append('response HTTP status changed')
    if content_type.split(';')[0].strip().lower() != 'application/pdf':
        errors.append('response MIME not PDF')
    if len(data) != r['bytes']:
        errors.append('payload byte count changed')
    if hashlib.sha256(data).hexdigest() != r['sha256']:
        errors.append('payload SHA-256 changed')
    sha1b32 = base64.b32encode(hashlib.sha1(data).digest()).decode('ascii').rstrip('=')
    if sha1b32 != cdx['digest'] or sha1b32 != r['sha1_base32']:
        errors.append('CDX SHA-1 Base32 differs from payload')
    if data.startswith(b'%PDF-') != r['pdf_header']:
        errors.append('PDF magic changed')
    if (b'%%EOF' in data[-1024:]) != r['pdf_eof']:
        errors.append('PDF EOF state changed')
    return errors


def relation_errors(early: bytes, later: bytes, latest: bytes) -> list[str]:
    """A unique CDX digest can be a truncated prefix, not a second edition."""
    errors = []
    if not later.startswith(early) or len(early) >= len(later):
        errors.append('2008 July capture is not a shorter exact prefix')
    if later != latest:
        errors.append('2008 September and 2022 PDF bytes differ')
    if b'%%EOF' in early[-1024:] or b'%%EOF' not in later[-1024:]:
        errors.append('invalid early/full PDF EOF comparison')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--fetch', action='store_true', help='GET and hash all three archives, including actual prefix comparison')
    args = parser.parse_args()
    doc = json.loads(args.manifest.read_text(encoding='utf-8'))
    errors = validate(doc)
    if errors:
        for e in errors: print('FAIL', e)
        return 1
    print('PASS frozen CDX metadata, incomplete earliest PDF correctly rejected (prefix replay only checked by --fetch)')
    if not args.fetch:
        return 0
    blobs = []
    for row in doc['snapshots']:
        try:
            with urlopen(Request(row['archived_url'], headers={'User-Agent': 'CondeCustody/1.0'}), timeout=50) as response:
                data = response.read(1_200_001)
                problems = payload_errors(row, data, http_status=response.status,
                                          content_type=response.headers.get('Content-Type', ''))
        except Exception as exc:
            print('NOT_RUN archive HTTP', row['cdx']['timestamp'], type(exc).__name__)
            return 2
        if problems:
            for e in problems: print('FAIL', row['cdx']['timestamp'], e)
            return 1
        blobs.append(data)
        print('PASS archive', row['cdx']['timestamp'], len(data), 'bytes SHA256+CDX-SHA1')
    for e in relation_errors(*blobs):
        print('FAIL', e)
        return 1
    print('PASS exact truncated prefix, two complete identical historical payloads')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
