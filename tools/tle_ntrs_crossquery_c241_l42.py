#!/usr/bin/env python3
"""C241-L42: independently check NASA NTRS report-number search blindness.

NASA's index is metadata, NEVER an epoch, station measurement or TLE.
"""
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L25 = ROOT / 'research/tle_custody/ntrs_ssr_1963_index_C241-L25.json'
L12 = ROOT / 'research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json'
L42 = ROOT / 'research/tle_custody/ntrs_ssr_crossquery_C241-L42.json'
API = 'https://ntrs.nasa.gov/api/citations/search'
QUERY = {'q': 'X-533-63-1', 'page': {'size': 200, 'from': 0}}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def is_1963(row):
    return any(str(p.get('publicationDate', '')).startswith('1963-')
               for p in row.get('publications', []))


def issue21(row):
    fields = [row.get('title', '')] + row.get('otherReportNumbers', [])
    return any(re.search(r'\bvol(?:ume)?\.?\s*3\b.{0,15}\bno\.?\s*21\b', str(s), re.I)
               for s in fields)


def audit(rows, total, l25, l12, l42, raw=None):
    require(l42['id'] == 'C241-L42' and l42['query'] == QUERY, 'query contract')
    require(l42['source_url'] == API and total == len(rows) and total <= 200,
            'incomplete or unpinned query')
    require(isinstance(total, int) and total > 0, 'empty index result')
    ids = [r['id'] for r in rows]
    require(len(ids) == len(set(ids)), 'duplicate result ID')
    anchors = {r['ntrs_id'] for r in l25['known_records']}
    require(len(anchors) == 11, 'lost base source anchor')
    oct_id = int(l12['source']['ntrs_id'])
    require(oct_id in anchors and oct_id == 19640000428, 'wrong October identity')
    require(l12['source']['report_number_printed'] == 'X-533-63-1', 'facsimile marker drift')
    require(l12['source']['ntrs_metadata_report_number'] == 'X-583-63-1',
            'metadata marker drift: re-inspect NASA original')
    require(l12['source']['report_number_disagreement'] == 'UNRESOLVED_INDEX_VS_FACSIMILE',
            'mismatch interpretation drift')
    indexed = {r['id']: r for r in rows if is_1963(r)}
    require(set(indexed) >= anchors - {oct_id}, 'previously indexed 1963 source missing')
    for ident in anchors - {oct_id}:
        locked = next(x for x in l25['known_records'] if x['ntrs_id'] == ident)
        row = indexed[ident]
        require(row['title'] == locked['title_as_indexed'], 'anchor title drift')
        require(row['otherReportNumbers'] == locked['report_numbers_as_indexed'],
                'anchor report number drift')
        require(any(str(p.get('publicationDate', '')).startswith(locked['published_on'])
                    for p in row.get('publications', [])), 'anchor publication date drift')
    require(oct_id not in indexed, 'October is newly indexed; revisit missing-match claim')
    require(l42['captured_1963_source_ids'] == sorted(anchors - {oct_id}),
            'captured independent search inventory drift')
    require(l42['captured_query_total'] == 26, 'capture total drift')
    if raw is not None:
        require(l42['captured_response_sha256'] == hashlib.sha256(raw).hexdigest()
                and l42['captured_response_bytes'] == len(raw),
                'raw response is not original snapshot')
    return {
        'id': 'C241-L42', 'source_family': 'NTRS_INDEX_METADATA_NOT_INSTRUMENTAL',
        'crossquery_report_id_count': len(anchors - {oct_id}),
        'october_id_absent_from_report_number_query': oct_id,
        'october_facs_report_number': l12['source']['report_number_printed'],
        'october_ntrs_report_number': l12['source']['ntrs_metadata_report_number'],
        'candidate_21_ids': sorted(r['id'] for r in rows if is_1963(r) and issue21(r)),
        'issue_21_not_located_in_this_query': not any(is_1963(r) and issue21(r) for r in rows),
        'no_proof_of_absence': True,
        'additional_1963_ids_pending_review': sorted(set(indexed) - anchors),
        'instrumental_528_observations': 0,
        'instrument_epoch_utc': None, 'tracking_station': None,
        'terminal_time_utc': None, 'terminal_location': None,
        'physical_constraint_activated': False, 'conde': 'INDETERMINATE',
    }


def fetch():
    request = urllib.request.Request(API, data=json.dumps(QUERY).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=40) as response:
        raw = response.read()
    payload = json.loads(raw)
    return payload['results'], payload['stats']['total'], raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--live', action='store_true')
    args = ap.parse_args()
    l25, l12, l42 = (json.loads(p.read_text(encoding='utf-8')) for p in (L25, L12, L42))
    if args.live:
        rows, total, _ = fetch()
    else:
        # Offline mode checks the preserved projection, not a simulated orbit.
        rows = [{'id': r['ntrs_id'], 'title': r['title_as_indexed'],
                 'otherReportNumbers': r['report_numbers_as_indexed'],
                 'publications': [{'publicationDate': r['published_on']}]} for r in
                l25['known_records'] if r['ntrs_id'] in l42['captured_1963_source_ids']]
        total = len(rows)
        # Full live response has additional non-1963 records. Offline audit
        # validates the anchored projection without pretending to replay raw bytes.
        rows += [{'id': -i, 'title': 'NON_1963_METADATA', 'otherReportNumbers': [],
                  'publications': [{'publicationDate': '1964-01-01'}]} for i in
                 range(1, l42['captured_query_total'] - len(rows) + 1)]
        total = len(rows)
    print(json.dumps(audit(rows, total, l25, l12, l42), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
