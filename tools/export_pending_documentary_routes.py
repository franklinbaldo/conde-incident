#!/usr/bin/env python3
"""Source-locked pending publication routes for UN 1963 and Soviet search leads.

Only connects documentary candidates; never creates observational epochs or sigma.
"""
from __future__ import annotations


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError('observable dependency contract: ' + detail)


def pending_documentary_routes(un: dict, raw: dict) -> list[dict]:
    """Project existing source routes; neither replay nor count an observation twice."""
    require(un['schema'] == 'conde.un-1963-status-scientific-bridge/v1'
            and un['custodial_occurrence'] == 'C241-L33'
            and un['matrix_occurrence'] == 'C197#1'
            and len(un['source_dependency_graph']) == 10
            and un['control_absence_is_negative_observation'] is False
            and un['activation'] is False
            and un['independent_instrument_observations_added'] == 0
            and un['physical_domain_effect'] == 'THETA_UNCHANGED'
            and un['documentary_status_528']['actual_terminal_time_utc'] is None
            and un['documentary_status_528']['sensor_epoch_utc'] is None
            and un['documentary_status_528']['sensor_covariance'] is None
            and all(p['value'] is None and p['active'] is False
                    for p in un['simulator_latent_parameters']),
            'UN cutoff falsely promoted to instrumental event')
    docs = {d['id']: d for d in un['source_documents']}
    require(set(docs) == {'UN-INF30', 'UN-INF53', 'UN-INF54', 'UN-INF55'}
            and docs['UN-INF30']['report_cutoff_printed'] == '2400Z 31 JANUARY 1963'
            and docs['UN-INF53']['report_cutoff_printed'] == '2400Z 15 NOVEMBER 1963'
            and docs['UN-INF53']['publication_day'] == '1963-12-31'
            and un['documentary_status_528']['reporting_independence'].startswith('UNKNOWN'),
            'UN publication/cutoff/source family changed')
    expected_un = {
        ('UN-INF30-JAN31', 'latent_1963_528_state_epoch',
         'COMPILED_ORBITAL_ELEMENTS_REQUIRE_EPOCH_AND_FIT'),
        ('UN-INF53-NOV15', 'latent_528_true_terminal_time',
         'REPORTED_STATUS_REQUIRES_CATALOG_REPORTING_MODEL'),
    }
    un_links = [e for e in un['source_dependency_graph']
                if e['to'] in {x[1] for x in expected_un}]
    # C197 and forward-model links also target time; keep only source-to-latent links.
    un_links = [e for e in un_links if (e['from'], e['to'], e['type']) in expected_un]
    require({(e['from'], e['to'], e['type']) for e in un_links} == expected_un
            and len(un_links) == 2 and all(e['activation'] is False for e in un_links),
            'UN latent reporting/epoch edges changed')

    require(raw['schema'] == 'conde.soviet-raw-route-scientific-bridge/v1'
            and raw['source_occurrence'] == 'C241-L37'
            and raw['activation'] is False
            and raw['physical_domain_effect'] == 'THETA_UNCHANGED'
            and raw['new_independent_instrument_observations'] == 0
            and raw['new_numeric_orbital_constraints'] == 0
            and raw['existing_soviet_candidate_joins'] == 6
            and raw['new_retrieval_paths'] == 3
            and raw['two_serials']['identity_equivalent'] is False
            and raw['two_serials']['raw_target_measurements_read'] is False
            and raw['source']['editorial_year'] == 2007
            and len(raw['source_dependency_graph']) == 11
            and all(e['active'] is False for e in raw['source_dependency_graph']),
            'Soviet bibliographic candidate falsely promoted')
    require(len(raw['catalogue_leads']) == 2
            and raw['catalogue_leads'][0]['publication_year'] == 1964
            and raw['catalogue_leads'][0]['described_observation_month'] == 'June 1963'
            and all(not lead['target_identified'] and lead['facsimile_sha256'] is None
                    for lead in raw['catalogue_leads']),
            'Soviet catalogue mistaken for a November 1963 target measurement')
    tracks = raw['simulator_latent_parameters']
    require({p['norad'] for p in tracks} == {527, 528, 529}
            and len(tracks) == 3
            and all(p['value'] is None and p['activation'] is False
                    and p['original_observation'] is None and p['time_utc'] is None
                    and p['station'] is None and p['frame'] is None
                    and p['sigma'] is None and not p['source_identity_confirmed']
                    for p in tracks), 'Soviet target parameters cannot yet restrict orbit')
    sov_links = raw['source_dependency_graph']
    require({e['to'] for e in sov_links if e['to'].startswith('NORAD_')}
            == {'NORAD_527_latent_track', 'NORAD_528_latent_track',
                'NORAD_529_latent_track'}
            and {e['to'] for e in sov_links if e['from'] == 'C241-L37'}
            == {'SOVIET_METHODS_SERIAL', 'SOVIET_RAW_RESULTS_SERIAL',
                'C241-L29', 'C241-L31', 'C241-L34', 'C241-L35'},
            'Soviet serial identity or target retrieval routes lost')
    result = []
    for source_id, links in (('C241-L33', un_links), ('C241-L37', sov_links)):
        for edge in links:
            result.append({'source_occurrence': source_id,
                           'from': edge['from'], 'to': edge['to'],
                           'relation': edge.get('type', edge.get('relation')),
                           'status': 'CONNECTED_PENDING_CALIBRATION',
                           'matrix_context': 'C197#1' if source_id == 'C241-L33' else None,
                           'independence_certified': False,
                           'activation': False, 'observed_value': None})
    keys = {(e['from'], e['to'], e['relation']) for e in result}
    require(len(result) == 13 and len(keys) == 13,
            'cross-source graph routes duplicated or omitted')
    return result
