#!/usr/bin/env python3
"""Source-locked Smithsonian EAD locator replay; archival titles are NOT astrometry."""
import argparse
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'research/tle_custody/sao_archival_tracking_leads_C241-L43.json'
SOURCE = 'https://sirismm.si.edu/EADs/SIA.FARU0171-ead.xml'
EXPECTED = {
    'refIDd1e2142': ('SAO - Optical Tracking Reports, 1960-1963', 22),
    'refIDd1e2187': ('STP Monthly Report, 1961-1965', 22),
    'refIDd1e2240': ('SAO - STP Correspondence, Bk II, 1962-1963', 23),
    'refIDd1e2360': ('SAO - STP Clocks, Precision Timing System, 1961-1965', 24),
}


def check_claims(lock):
    """Reject attempts to turn archive catalogue entries into 528 orbital data."""
    if lock['id'] != 'C241-L43' or lock['collection_id'] != 'SIA.FARU0171':
        raise ValueError('wrong ledger or collection')
    if lock['source_url'] != SOURCE or lock['source_type'] != 'ARCHIVAL_FINDING_AID_METADATA_NOT_OBSERVATION':
        raise ValueError('non-source-locked finding aid')
    rows = lock['archive_entries']
    if len(rows) != len(EXPECTED) or len({r['id'] for r in rows}) != len(EXPECTED):
        raise ValueError('lost or repeated archival entry')
    for r in rows:
        if r['id'] not in EXPECTED or (r['title'], r['box']) != EXPECTED[r['id']]:
            raise ValueError('invented archive locator')
        if r['url'] != 'https://sova.si.edu/record/sia.faru0171/' + r['id']:
            raise ValueError('changed archival persistent URL')
    if lock['possible_objects'] != [527, 528, 529] or lock['object_match_verified'] is not False:
        raise ValueError('invented object crosswalk')
    if lock['original_records_inspected'] is not False or lock['instrumental_observations_recovered'] != 0:
        raise ValueError('archival metadata masquerading as an observation')
    for key in ['instrument_epoch_utc', 'sensor_or_station', 'instrument_uncertainty']:
        if lock[key] is not None:
            raise ValueError(f'invented instrument metadata: {key}')
    if (lock['domain_restrictions_activated'] != 0 or lock['conde_reentry_location'] != 'INDETERMINATE'
            or lock['contact_status'] != 'NO_ARCHIVE_CONTACT_AUTHORIZED_OR_SENT'
            or lock['evidence_status'] != 'ARCHIVE_LOCATOR_ONLY_PENDING_RETRIEVAL_AND_IDENTITY'):
        raise ValueError('unjustified scientific or contact claim')
    return rows


def replay(raw, lock):
    check_claims(lock)
    if len(raw) != lock['source_bytes'] or hashlib.sha256(raw).hexdigest() != lock['source_sha256']:
        raise ValueError('EAD version changed; preserve old SHA and re-audit before promotion')
    root = ET.fromstring(raw)
    if not root.tag.endswith('}ead'):
        raise ValueError('not an EAD document')
    records = {e.get('id'): e for e in root.iter()
               if e.tag.split('}')[-1] in ('c', 'c01', 'c02', 'c03', 'c04') and e.get('id')}
    for r in lock['archive_entries']:
        el = records.get(r['id'])
        if el is None or el.get('level') != 'file':
            raise ValueError('missing file-level archival locator ' + r['id'])
        words = ' '.join(' '.join(el.itertext()).split())
        if r['title'] not in words or f'Box {r["box"]} of 44' not in words:
            raise ValueError('archival title or box changed ' + r['id'])
    return {'id': 'C241-L43', 'status': lock['evidence_status'],
            'verified_archive_entry_ids': sorted(EXPECTED),
            'file_level_locator_count': len(EXPECTED),
            'instrumental_observations_recovered': 0,
            'domain_restrictions_activated': 0,
            'source_sha256': lock['source_sha256']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ead-file', type=Path)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    lock = json.loads(LEDGER.read_text(encoding='utf-8'))
    if args.live == bool(args.ead_file):
        parser.error('choose exactly one of --live or --ead-file')
    if args.live:
        req = urllib.request.Request(SOURCE, headers={'User-Agent': 'CondeSourceCustody/1.0'})
        with urllib.request.urlopen(req, timeout=35) as f:
            raw = f.read()
    else:
        raw = args.ead_file.read_bytes()
    print(json.dumps(replay(raw, lock), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
