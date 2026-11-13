#!/usr/bin/env python3
"""Check exact NASA NTRS legacy URL captures; network optional and bounded."""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

if __package__:
    from tools.verify_wayback_pilot import replay_errors
else:
    from verify_wayback_pilot import replay_errors

MANIFEST = Path(__file__).resolve().parents[1] / 'research/archive/nasa_ssr_19631115_legacy_wayback_20261113.json'
STAMP = re.compile(r'[0-9]{14}\Z')
SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def validate(doc: dict) -> list[str]:
    errors = []
    if doc.get('schema') != 'conde.nasa-ssr-legacy-wayback/v1':
        errors.append('schema mismatch')
    if doc.get('ntrs_id') != '19640001198' or doc.get('publication_date') != '1963-11-15':
        errors.append('source identity mismatch')
    if doc.get('source_occurrences') != ['C197#1', 'C198#1']:
        errors.append('occurrence lineage mismatch')
    path = '/archive/nasa/casi.ntrs.nasa.gov/19640001198.pdf'
    if doc.get('legacy_path') != path:
        errors.append('legacy path mismatch')
    if doc.get('current_api_url') != 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf':
        errors.append('new API path mistaken for legacy path')
    api = doc.get('current_api_replay') or {}
    if api.get('http_status') != 200 or api.get('content_type') != 'application/pdf' or api.get('pdf_magic') is not True or api.get('pdf_eof') is not True:
        errors.append('current NASA PDF not verified')
    if not isinstance(api.get('bytes'), int) or api['bytes'] < 10 or not SHA256.fullmatch(api.get('sha256', '')):
        errors.append('current PDF size/hash missing')
    flags = doc.get('interpretation') or {}
    for name in ('captured_document_is_independent_sensor', 'captures_are_independent_historical_witnesses', 'separate_cdx_lengths_mean_separate_pdf_versions', 'cdx_length_is_pdf_bytes', 'new_orbital_constraint'):
        if flags.get(name) is not False:
            errors.append('provenance false independence: ' + name)
    if flags.get('same_bytes_as_current_api_observed') is not True:
        errors.append('cross-version identity claim must be explicit')
    rows = doc.get('captures')
    if not isinstance(rows, list) or len(rows) != 3:
        return errors + ['expected 3 exact captured rows']
    stamps = set()
    digests = set()
    for row in rows:
        cdx = row.get('cdx_record') or {}
        replay = row.get('replay') or {}
        stamp = cdx.get('timestamp', '')
        if not STAMP.fullmatch(stamp):
            errors.append('invalid timestamp'); continue
        try:
            datetime.strptime(stamp, '%Y%m%d%H%M%S')
        except ValueError:
            errors.append('impossible timestamp'); continue
        if stamp in stamps:
            errors.append('duplicate timestamp')
        stamps.add(stamp)
        if cdx.get('original') not in [f'http://ntrs.nasa.gov{path}', f'https://ntrs.nasa.gov{path}']:
            errors.append('CDX record not for exact legacy PDF')
        if row.get('archived_url') != f'https://web.archive.org/web/{stamp}id_/{cdx.get("original")}':
            errors.append('archived URL does not exactly follow CDX')
        if cdx.get('statuscode') != '200' or cdx.get('mimetype') != 'application/pdf':
            errors.append('CDX not PDF 200')
        if not isinstance(cdx.get('length'), int) or cdx['length'] < 1:
            errors.append('invalid CDX WARC record length')
        if replay.get('http_status') != 200 or replay.get('content_type') != 'application/pdf' or replay.get('pdf_magic') is not True or replay.get('pdf_eof') is not True:
            errors.append('replay response not verified')
        if replay.get('bytes') != api.get('bytes') or replay.get('sha256') != api.get('sha256'):
            errors.append('NASA original/archive bytes differ from reported current source')
        if replay.get('sha1_base32') != cdx.get('digest'):
            errors.append('replay hash does not match CDX digest')
        if not re.fullmatch('[A-Z2-7]{32}', str(cdx.get('digest', ''))):
            errors.append('CDX digest invalid')
        digests.add(cdx.get('digest'))
    if len(digests) != 1:
        errors.append('claimed single payload has multiple digests')
    if stamps != {'20150217133001', '20170228144859', '20170302093149'}:
        errors.append('unexpected capture timestamp set')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--fetch', action='store_true', help='HTTP replay every archived PDF and current NASA API PDF')
    args = parser.parse_args()
    doc = json.loads(args.manifest.read_text())
    errs = validate(doc)
    if errs:
        for err in errs: print('FAIL', err)
        return 1
    print('PASS 3 exact CDX entries, one PDF payload, no independent sensor')
    if not args.fetch:
        return 0
    for row in doc['captures']:
        try:
            with urlopen(Request(row['archived_url'], headers={'User-Agent': 'CondeCustody/1.0'}), timeout=35) as r:
                data = r.read(1_000_001)
                errs = replay_errors(row, data, http_status=r.status, content_type=r.headers.get('Content-Type', ''))
        except Exception as exc:
            print('FAIL replay unavailable', type(exc).__name__)
            return 2
        if errs:
            for err in errs: print('FAIL replay', err)
            return 1
        print('PASS', row['cdx_record']['timestamp'], 'bytes and CDX SHA-1 + SHA-256')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
