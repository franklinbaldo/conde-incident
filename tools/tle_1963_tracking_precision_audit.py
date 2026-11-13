#!/usr/bin/env python3
"""Audit historical tracking-capability claims without inventing 528 covariance."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'research/tle_custody/tracking_precision_1963_C241-L26.json'
RAW_FILENAMES = {
    'NASA_SSR_1963_NOV15': 'nasa-ssr-1963-11-15.pdf',
    'PRESIDENT_US_1961_SAO': 'nasa-pres-1961.pdf',
    'NORAD_CONAD_1963_HISTORICAL': 'norad-conad-jul-dec-1963.pdf',
    'NORAD_WIR_1965_COSMOS94': 'norad-1965-cosmos94.pdf',
}
KNOWN_DIGESTS = {
    'NASA_SSR_1963_NOV15': ('0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674', 327613),
    'PRESIDENT_US_1961_SAO': ('b8c0ff027d0a20f04a07997a40cb1544c0df4d4ff2926f6542f07c68c0c127b5', 1522003),
    'NORAD_CONAD_1963_HISTORICAL': ('cb3a9c4dc8bbdae6d2f72711d4dbb50887e576975e7f0e84f2e434c90fcee52b', 1459815),
    'NORAD_WIR_1965_COSMOS94': ('c9e8e38fb9fdf0de97a209c4120d2d0a391b3624af054edeb30b01f467328e90', 7669507),
}


def validate(d, source_dir=None):
    if (d.get('id'), d.get('schema')) != ('C241-L26', 'conde.tracking-capability-custody/v1'):
        raise ValueError('invalid ledger identity/schema')
    sources = d['sources']
    if len(sources) != 4 or {s['id'] for s in sources} != set(KNOWN_DIGESTS):
        raise ValueError('source identity count')
    for source in sources:
        ident = source['id']
        digest, length = KNOWN_DIGESTS[ident]
        if (source['sha256'], source['bytes']) != (digest, length):
            raise ValueError('source hash/length changed: '+ident)
        if not source['url'].startswith('https://') or source['page_in_pdf_one_based'] < 1:
            raise ValueError('source location invalid')
        if source['observation_epoch_known'] and ident != 'NORAD_WIR_1965_COSMOS94':
            raise ValueError('historical catalog publication is not a sensor epoch')
        if source_dir is not None:
            blob = (Path(source_dir) / RAW_FILENAMES[ident]).read_bytes()
            if len(blob) != length or hashlib.sha256(blob).hexdigest() != digest:
                raise ValueError('raw PDF failed byte custody: '+ident)
    if next(s for s in sources if s['id'] == 'NORAD_CONAD_1963_HISTORICAL')['date'] is not None:
        raise ValueError('publication day for half-year summary not known')
    facts = {x['id']: x for x in d['documentary_observables']}
    if len(facts) != 4 or len(d['documentary_observables']) != len(facts):
        raise ValueError('duplicate/missing facts')
    day = facts['C241-L26:DAY_528']
    if (day['object_norad'], day['designation_printed'], day['published_calendar_day'], day['source_field']) != (528, '1963 3B', '1963-11-08', 'DECAY'):
        raise ValueError('unexpected 528 catalog entry')
    if day['date_precision'] != 'CALENDAR_DAY_ONLY' or any(day[k] is not None for k in ('time_utc', 'method', 'sensor', 'measurement_sigma')):
        raise ValueError('fabricated 528 terminal precision')
    cam = facts['C241-L26:SAO_CAMERA_CAPABILITY']
    if (cam['nominal_angular_accuracy_arcseconds'], cam['nominal_time_accuracy_milliseconds']) != (4, 2):
        raise ValueError('Baker-Nunn original stated capability changed')
    if cam['object_norad'] is not None or cam['measurement_sigma'] is not None:
        raise ValueError('network capability cannot become 528 instrumental sigma')
    for ident in ('C241-L26:SPADATS_1963_NETWORK', 'C241-L26:COMPARISON_COSMOS94'):
        fact = facts[ident]
        if fact['linked_to_528'] is not False or fact['measurement_sigma'] is not None:
            raise ValueError('other-object/network data cannot constrain 528')
    if facts['C241-L26:COMPARISON_COSMOS94']['object_norad'] != 1636:
        raise ValueError('1965 comparison target changed')
    if {x['norad'] for x in d['object_measurement_custody']} != {527, 528, 529} or len(d['object_measurement_custody']) != 3:
        raise ValueError('raw observation scope')
    for row in d['object_measurement_custody']:
        if row['status'] != 'NOT_RECOVERED' or any(v is not None for k,v in row.items() if k not in ('norad','status')):
            raise ValueError('invented instrument, station, timing, residual or frame')
    if len(d['links']) != len(facts) or {x['from'] for x in d['links']} != set(facts):
        raise ValueError('missing or orphaned variable link')
    if any(x['status'] not in ('CONNECTED_PENDING_METHOD_AND_ERROR','CONTEXT_ONLY_NOT_ACTIVATED') for x in d['links']):
        raise ValueError('unjustified hard constraint')
    if set(d['independence']) != set(KNOWN_DIGESTS) or d['domain_delta'] != 'NOT_EVALUABLE_WITHOUT_TERMINAL_METHOD_AND_ERROR':
        raise ValueError('source dependence/domain claim')
    return {'id':'C241-L26', 'verified_sources':len(sources), 'documentary_links':len(d['links']),
            'source_bytes_verified':source_dir is not None,
            'catalog_decay_day_528':day['published_calendar_day'], 'raw_instrument_observations':0,
            'physical_bounds_activated':0, 'instrument_specific_sigma_528':'NOT_RECOVERED'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = validate(json.loads(LEDGER.read_text()), args.source_dir)
    payload = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
