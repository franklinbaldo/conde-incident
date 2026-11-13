#!/usr/bin/env python3
"""Expose existing Lontra ON20 custody as typed dependencies, never as 1963 sensing.

The input records are authored/custodied separately. No Wayback lookup,
new capture, independent HTTP validation, or publication is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('public/data/conde-archive-documentary-links.json')
CATALOG = 'research/meteorology/ncep_office_notes_1963_1968_locator.json'
CUSTODY = 'research/meteorology/ncep_on20_wayback_custody_20261112.json'
PAGE_AUDIT = 'research/meteorology/ncep_on20_page_audit_20261112.json'
PENDING = 'research/constraints/nmc_y20175_pending_bridge.json'
SOURCES = (CATALOG, CUSTODY, PAGE_AUDIT, PENDING)
EXPECTED_SHA256 = '656984ac58ff1632e39b0f62ac80003785ddea0a0de32dfb19c8c612067aabbe'
ORIGINAL = 'http://www.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/013FD4DB.pdf'


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError('archive documentary contract: ' + reason)


def encode(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, ensure_ascii=False,
                       separators=(',', ':')) + '\n').encode('utf-8')


def build(root: Path = ROOT) -> dict:
    feeds, hashes = {}, {}
    for path in SOURCES:
        raw = (root / path).read_bytes()
        feeds[path] = json.loads(raw)
        hashes[path] = hashlib.sha256(raw).hexdigest()
    catalog, custody, audit, pending = (feeds[p] for p in SOURCES)
    require(catalog['id'] == 'MET-NMC-NCEPON-20261112-01'
            and custody['id'] == 'MET-NMC-NCEPON-20261112-02'
            and custody['linked_catalog_id'] == catalog['id']
            and audit['id'] == 'MET-NMC-NCEPON-20261112-03'
            and audit['related'] == custody['id'], 'catalog/custody/page identity')
    notes = [n for n in catalog['notes'] if n['number'] == 20]
    require(len(notes) == 1 and notes[0]['year_as_catalogued'] == '1964'
            and custody['published_year'] == 1964
            and notes[0]['pdf_catalog_link'] == custody['original_href'] == ORIGINAL,
            'ON20 catalog/original URI or documentary era drift')
    require(catalog['catalog']['url'] == custody['bibliographic_catalog']
            and catalog['catalog']['http_status'] == 200,
            'catalog URI or original catalog access mismatch')
    capture = custody['preservation']
    ts = datetime.fromisoformat(capture['capture_utc'].replace('Z', '+00:00'))
    require(ts.tzinfo == timezone.utc and ts.strftime('%Y%m%d%H%M%S') == '20220119075333',
            'capture timestamp not anchored')
    replay = urlsplit(capture['replay_url'])
    require(replay.scheme == 'https' and replay.netloc == 'web.archive.org'
            and replay.path == '/web/20220119075333id_/' + ORIGINAL
            and not replay.query and not replay.fragment,
            'recorded Wayback PDF replay is not exact captured original')
    require(capture['http_status'] == 200 and capture['content_type'] == 'application/pdf'
            and capture['sha256'] == EXPECTED_SHA256
            and capture['byte_length'] == audit['pdf_bytes'] == 932414
            and capture['page_tree_count_marker'] == audit['page_tree_count'] == 23
            and capture['pdf_header'] == '%PDF-1.4' and capture['pdf_eof'] is True
            and custody['checks']['wayback'] == 'HTTP_200_FULL_BYTES',
            'archived PDF custody bytes, MIME, status or page identity')
    require(audit['source_url'] == capture['replay_url']
            and audit['pdf_sha256'] == EXPECTED_SHA256
            and audit['capture_utc'] == capture['capture_utc']
            and len(audit['page_streams']) == 23
            and sorted(x['pdf_page'] for x in audit['page_streams']) == list(range(1, 24)),
            'PDF audit not anchored to this capture')
    require(custody['linked_pending_bridge'] == PENDING
            and custody['physical_constraint'] == 'NOT_ACTIVATED'
            and custody['applicability_to_1963'] == 'NOT_ESTABLISHED'
            and custody['station_day_matches'] is None
            and custody['tape_decoded'] is False
            and pending['schema'] == 'conde.pending-nmc-wind-bridge/v1'
            and pending['numeric_observations_generated'] == 0
            and pending['physical_domain'] == 'UNCHANGED_NO_ACTIVE_CONSTRAINT'
            and pending['source_independence'] == 'UNKNOWN_NO_DECODE'
            and pending['matrix_context_ref'].endswith(':C151#1'),
            'archival copy incorrectly promoted into 1963 measurement')
    # The preservation ledger does NOT supply CDX's Base32 SHA-1 digest.
    # Neither the SHA-256 of the retrieved bytes nor a capture URL supplies it.
    return {
        'schema': 'conde.archive-documentary-links/v1',
        'custodian': 'Lontra', 'source_file_sha256': hashes,
        'nodes': [
            {'id': catalog['id'], 'kind': 'BIBLIOGRAPHIC_CATALOG',
             'url': catalog['catalog']['url']},
            {'id': custody['id'], 'kind': 'RETRIEVED_PDF_COPY',
             'original_url': ORIGINAL, 'archive_url': capture['replay_url'],
             'document_year': 1964, 'capture_utc': capture['capture_utc'],
             'retrieval_date_utc': capture['retrieval_date_utc'],
             'http_status': capture['http_status'], 'mime': capture['content_type'],
             'retrieved_bytes_sha256': EXPECTED_SHA256,
             'retrieved_bytes_length': capture['byte_length'],
             'cdx_digest_base32_sha1': None, 'cdx_digest_verification': 'NOT_RECORDED',
             'custody_status': 'PREVIOUSLY_RETRIEVED_AND_HASHED_NOT_REFETCHED_BY_EXPORTER'},
            {'id': audit['id'], 'kind': 'AUDIT_OF_SAME_PDF_BYTES',
             'page_tree_count': 23, 'pdf_sha256': EXPECTED_SHA256},
            {'id': 'NMC_Y20175_PENDING_BRIDGE', 'kind': 'INACTIVE_SCIENTIFIC_BRIDGE',
             'contract_path': PENDING, 'latent_parameter_id': pending['candidate_latent_parameter'],
             'candidate_forward_operator': pending['candidate_forward_operator'],
             'matrix_context_ref': pending['matrix_context_ref'],
             'matrix_context_row_sha256': pending['matrix_context_row_sha256'],
             'lean_status': 'NOT_PROMOTED', 'activation': False,
             'simulator_value': None, 'independent_physical_observation_count': None},
        ],
        'edges': [
            {'from': custody['id'], 'to': catalog['id'], 'kind': 'LOCATED_VIA_CATALOG'},
            {'from': audit['id'], 'to': custody['id'], 'kind': 'SAME_BYTES_PAGE_AUDIT'},
            {'from': 'NMC_Y20175_PENDING_BRIDGE', 'to': custody['id'],
             'kind': 'CONDITIONAL_DOCUMENTARY_REFERENCE_NOT_1963_CALIBRATION'},
        ],
        'epistemic_limits': {
            'distinct_physical_observations_added': 0,
            'cdx_digest_retrieved': False,
            'catalog_year_is_not_capture_year': True,
            'retrieved_wayback_sha256_is_not_master_sha256': True,
            'archive_pdf_not_validated_for_1963_y20175': True,
            'site_may_claim_cdx_verified': False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-site', action='store_true')
    group.add_argument('--check-site', action='store_true')
    args = ap.parse_args()
    raw = encode(build())
    require(len(raw) <= 20_000, 'export exceeds 20,000 bytes')
    target = ROOT / OUTPUT
    if args.write_site:
        target.write_bytes(raw)
    else:
        require(target.is_file() and target.read_bytes() == raw, 'stale site export')
    print('ARCHIVE_DOCUMENTARY_LINKS_OK', len(raw))


if __name__ == '__main__':
    main()
