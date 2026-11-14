#!/usr/bin/env python3
"""Connect C241-L46 operational NORAD messages without transferring 688 timing to 528."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = 'research/tle_custody/norad_spadats_context_C241-L46.json'
MOR = 'public/data/conde-norad-context.json'
UN = 'public/data/conde-un-1963-status-bridge.json'
OUTPUT = ROOT / 'public/data/conde-norad-1963-operational-bridge.json'
PINNED = {
    LEDGER: '2ca04b17b8dc5d2a8852de94362316c5d75825d691843af5873f49cf8e74d852',
    MOR: '78e8d88a5bcdb570d0afec854497720987f29fdfdebbe785c27418a988fb5e3b',
    UN: 'bc31cff4f2b24f88cc600cab47033c92ba5de3d60c12e2a158132563ccf1966c',
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError('C241-L46 scientific bridge: ' + message)


def build(ledger: dict, mor: dict, un: dict) -> dict:
    require(ledger['schema'] == 'c241-l46-norad-spadats-context-v1'
            and ledger['epistemic_status'] == 'CONTEXT_ONLY_NOT_ACTIVATED', 'source scope changed')
    target = ledger['target']
    require(set(target) == {'norad', 'designator', 'observation_utc', 'station', 'frame',
                            'sigma', 'decay_hour_utc', 'reentry_location', 'activation'},
            'unexpected target field, inspect manually')
    require(target['norad'] == 528 and target['designator'] == '1963-003B'
            and target['activation'] is False and all(target[k] is None for k in
            ('observation_utc', 'station', 'frame', 'sigma', 'decay_hour_utc', 'reentry_location')),
            'source falsely attributes measurement or decay timing to 528')
    require(len(ledger['sources']) == 2, 'unexpected number of messages')
    source_by_id = {s['id']: s for s in ledger['sources']}
    require(set(source_by_id) == {'C241-L46-D07', 'C241-L46-D08'}, 'source IDs changed')
    specs = (
        ('C241-L46-D07', '1963-11-12', 'AF IN 20080',
         'b1d6a37572e6c7ffa806f07f30ae714730a8d17724942638ac591c661bef97fe', 929016, 6),
        ('C241-L46-D08', '1963-11-14', 'AF IN 23784 (corrected copy of AF IN 22976)',
         '65452b827428bdbef37bf96fb915a1411c2798d5a16939d845abe561aa12e13e', 520901, 3),
    )
    for identifier, date, message, sha, size, pages in specs:
        s = source_by_id[identifier]
        require(s['document_date'] == date and s['message'] == message
                and s['sha256'] == sha and s['bytes'] == size and s['pages'] == pages,
                'custody metadata changed: ' + identifier)
        require(s['launch'] == '1963-044' and s['object_ids'] == [687, 688]
                and s['measurement_528'] is None and 528 not in s['object_ids'],
                'cross-mission observation contamination: ' + identifier)
        require(s['url'].endswith('/07.pdf' if identifier.endswith('D07') else '/08.pdf')
                and s['url'].startswith('https://nsarchive.gwu.edu/'),
                'facsimile URL not expected')
        require(all(0 <= f['page_index'] < pages and f['printed'] for f in s['findings']),
                'document locator invalid')
    require(source_by_id['C241-L46-D07']['decay_window'] is None,
            'invented decay claim in bulletin')
    window = source_by_id['C241-L46-D08']['decay_window']
    require(window == {'object_id': 688, 'date_utc': '1963-11-12',
                       'start': '2210Z', 'end': '2400Z',
                       'kind': 'REPORTED_INTERVAL_FOR_DIFFERENT_OBJECT_NOT_SIGMA'},
            '688 interval cannot be promoted or reassigned to 528')
    require(mor['schema'] == 'conde.norad-documentary-context/v1'
            and mor['epistemic_limits']['no_source_is_an_observation_of_norad_528'] is True
            and mor['epistemic_limits']['no_new_528_trajectory_or_decay_bound'] is True,
            'Morcego source scope changed')
    records = {r['source_id']: r for r in mor['records']}
    matching = (('C241-L46-D07', 'MOR-NORAD-1963-NOV12', [687, 688], '1963-11-12'),
                ('C241-L46-D08', 'MOR-NORAD-1963-NOV14', [688], '1963-11-14'))
    for _, rid, object_ids, date in matching:
        record = records[rid]
        require(record['source_date'] == date
                and record['object_ids_reported_in_this_document'] == object_ids
                and record['original_pdf_sha256'] is None,
                'Morcego report must remain an unauthenticated document crosswalk')
    require(un['schema'] == 'conde.un-1963-status-scientific-bridge/v1'
            and un['matrix_occurrence'] == 'C197#1'
            and un['activation'] is False,
            'UN status bridge no longer contextual')
    status = un['documentary_status_528']
    require(status['norad_from_c241_l32'] == 528
            and status['reported_not_in_orbit_by'] == '2400Z 15 NOVEMBER 1963'
            and status['nasa_catalogued_decay_day'] == '1963-11-08'
            and status['reporting_independence'] == 'UNKNOWN_POSSIBLY_SHARED_NASA_NORAD_UPSTREAM'
            and all(status[k] is None for k in ('actual_terminal_time_utc', 'actual_event_location',
                                                'sensor_epoch_utc', 'sensor_covariance')),
            'administrative status changed into measured event')
    require(un['independent_instrument_observations_added'] == 0,
            'UN documentary source incorrectly counted as sensor')

    graph = []
    def edge(a: str, b: str, rel: str) -> None:
        graph.append({'from': a, 'to': b, 'relation': rel,
                      'independent_physical_observation': False, 'activation': False})
    for new_id, old_id, _, _ in matching:
        edge('C241-L46', new_id, 'ORIGINAL_FACSIMILE_IDENTIFIED')
        edge(new_id, 'NORAD:1963-044:687_688', 'ORBITAL_CONTEXT_OTHER_MISSION')
        edge(new_id, old_id, 'SAME_REPORTING_TOPIC_DOCUMENT_IDENTITY_NOT_YET_PROVEN')
    edge('C241-L46-D08', 'NORAD:688:DECAY_INTERVAL_1963-11-12',
         'ORIGINAL_688_INTERVAL_NOT_TRANSFERABLE_TO_528')
    edge('C241-L46', 'C241-L33:UN-INF53',
         'CONTEXTUAL_TIMING_COMPARISON_DIFFERENT_OBJECT_UPSTREAM_UNKNOWN')
    edge('C241-L46', 'H_NORAD_528_ORIGINAL_OPERATIONAL_LOG_FOUND',
         'SEARCH_TARGET_UNPROVEN')
    edge('H_NORAD_528_ORIGINAL_OPERATIONAL_LOG_FOUND', 'LATENT:NORAD528:MEASUREMENT',
         'PENDING_PRIMARY_INSTRUMENTAL_RECORD')

    latency = ['log_document_identifier', 'station_528', 'measured_epoch_utc_528',
               'reference_frame_528', 'sigma_528', 'clock_calibration_528',
               'operational_decay_interval_528', 'reentry_position_528']
    return {
        'schema': 'conde.norad-1963-operational-scientific-bridge/v1',
        'id': 'ABELHA-C241-L46-NORAD-01',
        'source_occurrence': 'C241-L46',
        'related_matrix_occurrence': 'C197#1',
        'input_sha256': PINNED,
        'source_documents': [{
            'source_id': s['id'], 'url': s['url'], 'document_date': s['document_date'],
            'message': s['message'], 'pdf_sha256': s['sha256'], 'bytes': s['bytes'],
            'pdf_pages': s['pages'], 'findings': s['findings'],
            'observed_launch': s['launch'], 'object_ids': s['object_ids'],
            'hash_scope': 'COMPLETE_SOURCE_PDF_VERIFIED_BY_TARTARUGA',
            'physical_observation_528': None,
            'independence_family': 'USAF_NORAD_SPADATS_1963_044_REPORTING',
        } for s in ledger['sources']],
        'other_object_688_reported_decay_window': window,
        'crosswalk_identity_status': 'TOPIC_MATCH_UNVERIFIED_EXACT_DOCUMENT_IDENTITY',
        'dependency_graph': graph,
        'lean_candidate': 'Conde1963.noradOperationalReports1963Context',
        'lean_status': 'DOCUMENTARY_CANDIDATE_NOT_COMPILED_ORBITAL_CONSTRAINT',
        'hypotheses': [
            {'id': 'H_NORAD_528_ORIGINAL_OPERATIONAL_LOG_FOUND', 'state': 'OPEN_UNVERIFIED',
             'missing': 'ORIGINAL_SPADATS_528_REPORT_WITH_STATION_EPOCH_FRAME_RESIDUALS'},
            {'id': 'H_688_DECAY_INTERVAL_IS_528_SIGMA', 'state': 'REJECTED_CROSS_OBJECT_TRANSFER',
             'missing': 'NOT_APPLICABLE'},
        ],
        'simulator_latent_parameters': [{
            'id': 'NORAD528:' + name, 'value': None, 'uncertainty': 'UNKNOWN_NOT_ZERO',
            'source_occurrence': 'C241-L46', 'activation': False,
        } for name in latency],
        'observation_candidates_527_528_529': [
            {'norad': n, 'designator': f'1963-003{s}', 'source_measurement': None,
             'epoch_utc': None, 'frame': None, 'sigma': None, 'activation': False}
            for n, s in ((527, 'A'), (528, 'B'), (529, 'C'))],
        'reported_administrative_status_528_by': status['reported_not_in_orbit_by'],
        'nasa_catalogued_decay_day_528': status['nasa_catalogued_decay_day'],
        'independent_528_instrumental_observations_added': 0,
        'activation': False,
        'physical_domain_effect': 'THETA_UNCHANGED',
        'next_test': ledger['next_search'],
    }


def render(root: Path = ROOT) -> bytes:
    source = {}
    for relative, digest in PINNED.items():
        raw = (root / relative).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, 'input byte drift: ' + relative)
        source[relative] = json.loads(raw)
    return (json.dumps(build(source[LEDGER], source[MOR], source[UN]),
                       ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--write-site', action='store_true')
    p.add_argument('--check-site', action='store_true')
    args = p.parse_args()
    data = render()
    if args.write_site:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
    elif args.check_site:
        require(OUTPUT.read_bytes() == data, 'site JSON changed')
    else:
        print(data.decode(), end='')


if __name__ == '__main__':
    main()
