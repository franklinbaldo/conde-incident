#!/usr/bin/env python3
"""Export audited C179/C151 source -> derived observable -> latent-parameter links.

The output is a documentary/conditional bridge, not a new 528 track or
Conde weather measurement. It consumes the existing canonical contracts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import export_documentary_dependence as documentary
import export_contextual_scientific_bridges as scientific
import provenance_graph as pg
import export_un_1963_status_bridge as un1963
import export_soviet_raw_route_bridge as soviet
from export_pending_documentary_routes import pending_documentary_routes

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('public/data/conde-observable-dependency-links.json')
FORMAL = ROOT / 'formal/scripts'
sys.path.insert(0, str(FORMAL))
import physical_observable_bridge as physical


def encoded(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError('observable dependency contract: ' + detail)



def build_caravelas_external(report: dict, graph: dict, recife: dict,
                            parent_hashes: dict) -> dict:
    """Join one external source to the cumulative latent-wind graph, without inventing a Cnn."""
    from audit_isd_caravelas_1963 import SOURCE_SHA256, WINDOW_SHA256

    source_id = 'MET-ISD-19631107-09-CARAVELAS-01'
    latent = 'wind_field_nov_1963_with_altitude_time_and_position'
    source = report['source']
    require(report['schema'] == 'conde.isd-caravelas-hourly-1963/v1'
            and source['full_gzip_sha256'] == SOURCE_SHA256
            and source['excerpt_sha256'] == WINDOW_SHA256
            and source['excerpt_rows'] == 72
            and report['station']['usaf'] == '834970'
            and report['station']['wban'] == '99999'
            and report['station']['position_epoch_in_1963_verified'] is None
            and report['quality']['measurement_uncertainty'] is None
            and report['quality']['instrument_identity_1963'] is None
            and report['quality']['station_specific_transfer_uncertainty_to_conde'] is None
            and report['interpretation']['numeric_constraint_on_conde'] is None,
            'Caravelas archive/custody or instrumental status changed')
    require(graph['schema'] == 'conde.historical-surface-pending-bridge/v1'
            and graph['id'] == source_id
            and graph['source']['url'] == source['url']
            and graph['source']['full_gzip_sha256'] == SOURCE_SHA256
            and graph['source']['excerpt_sha256'] == WINDOW_SHA256
            and graph['source']['independence_family'] ==
                'NOAA_NCEI_ISD_DIGITIZED_SURFACE_OBSERVATIONS'
            and graph['observation']['rows'] == 72
            and graph['observation']['station_position_in_1963'] is None
            and graph['observation']['measurement_method_in_1963'] is None
            and graph['status'] == 'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION'
            and graph['active_conde_constraint'] is None
            and graph['uncertainty_m_s'] is None
            and graph['instrument_covariance'] is None,
            'Caravelas graph cannot be an activated Conde constraint')
    expected = [
        (source_id, 'Caravelas_surface_wind_at_hour_t', 'OBSERVES_DIGITIZED'),
        ('Caravelas_surface_wind_at_hour_t', 'Conde_surface_wind_at_hour_t',
         'PENDING_SPATIAL_TRANSFER'),
        ('Conde_surface_wind_at_hour_t', 'Conde_entry_drag_or_fall_location',
         'PENDING_TRAJECTORY_AND_ALTITUDE_MODEL'),
        (source_id, 'C149-C151 Recife IGRA sounding family',
         'CONTEXT_NOT_INDEPENDENCE_CERTIFIED'),
    ]
    require([(e['from'], e['to'], e['type']) for e in graph['edges']] == expected,
            'missing/reversed Caravelas edges or false spatial observation')
    require(recife['source_id'] == 'NOAA_IGRA_RECIFE_1963'
            and recife['matrix_occurrence'].endswith(':C151#1')
            and recife['activation'] is False
            and recife['simulator_value'] is None
            and recife['latent_parameter_id'] == latent,
            'Caravelas is external to matrix; Recife context must stay C151#1')
    return {
        'source_id': source_id,
        'matrix_occurrence': None,  # NOAA/ISD Caravelas is not an invented Cnn.
        'source_url': source['url'],
        'source_family': graph['source']['independence_family'],
        'full_gzip_sha256': SOURCE_SHA256,
        'excerpt_sha256': WINDOW_SHA256,
        'station_usaf': '834970',
        'station_wban': '99999',
        'digitized_station_hour_rows': 72,
        'latent_parameter_id': latent,
        'graph_edges': graph['edges'],
        'activation_requirements': graph['necessary_for_promotion'],
        'recife_context': {'matrix_occurrence': recife['matrix_occurrence'],
                           'row_sha256': recife['row_sha256'],
                           'source_id': recife['source_id'],
                           'independence_certified': False},
        'source_parent_sha256': parent_hashes,
        'station_position_1963': None,
        'instrument_covariance': None,
        'spatial_transfer_operator': None,
        'terminal_epoch_528': None,
        'simulator_value': None,
        'activation': False,
        'status': 'CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION',
        'physical_domain_effect': 'THETA_UNCHANGED',
    }



def build(root: Path = ROOT) -> dict:
    def pinned(path: str, builder) -> dict:
        raw = (root / path).read_bytes()
        require(raw == encoded(builder(root)), 'stale parent: ' + path)
        return json.loads(raw)

    dep_path = 'public/data/conde-declared-dependence.json'
    sci_path = 'public/data/conde-scientific-bridges.json'
    dep = pinned(dep_path, documentary.build)
    sci = pinned(sci_path, scientific.build)
    require(dep['matrix_git_blob_sha1'] == sci['matrix_git_blob_sha1'] ==
            pg.MATRIX_BLOB_SHA, 'matrix mismatch')
    contracts = [x for x in dep['contract_citation_crosswalk']
                 if x['contract_id'] == 'C179_C151_BRIDGE']
    require(len(contracts) == 1, 'physical contract missing or duplicated')
    contract = contracts[0]
    require(contract['contract_path'] == 'formal/scripts/physical_observable_bridge.py'
            and contract['contract_status'] == 'DERIVED_ONLY_NO_CONDE_TRANSFER',
            'conditional contract status changed')
    expected = {'C179#1': 'AFSPC_MIRROR_528',
                'C151#1': 'NOAA_IGRA_RECIFE_1963'}
    coverage = {(r['occurrence_ref'], r['source_id']): r
                for r in sci['citation_coverage']}
    require(len(contract['occurrences']) == len(expected), 'unexpected contract rows')
    matrix = (root / physical.MATRIX_PATH).read_bytes()
    physical.audit(matrix, physical.parse_rows(matrix))
    orbit = physical.orbital_observables()
    winds = physical.recife_winds(matrix)
    require(orbit['source_occurrence'] == 'C179#1'
            and orbit['source_status'] == 'SECONDARY_MIRROR_NOT_PRIMARY_TRACK'
            and orbit['observational_error_distribution'] is None
            and orbit['physical_raan_interval_deg'] is None
            and orbit['mcmc_posterior'] == 'NOT_RUN', 'TLE custody/uncertainty drift')
    source_index = {x['id']: x for x in json.loads((root / 'research/provenance/lineages.json').read_text())['sources']}
    require(source_index['AFSPC_MIRROR_528']['url'] == orbit['source_url']
            and source_index['AFSPC_MIRROR_528']['status'] == 'SECONDARY_MIRROR_ORIGINAL_TRACKING_UNVERIFIED'
            and source_index['NOAA_IGRA_RECIFE_1963']['url'] == physical.SOURCE_RECIFE
            and source_index['NOAA_IGRA_RECIFE_1963']['status'] == 'HISTORICAL_WIND_MEASUREMENT_RECIFE_NOT_CONDE',
            'citation origin or epistemic level drift')
    require(len(winds) == 5 and all(w['evidence_occurrence'] == 'C151#1'
            and w['location'] == 'Recife, Pernambuco, Brazil'
            and w['actual_release_time'] is None
            and w['source_url'] == physical.SOURCE_RECIFE for w in winds),
            'Recife profile cannot be transferred to Conde')
    source_values = {
        'C179#1': {
            'observables': ['derived_mean_angular_rate_rad_per_s',
                            'derived_kepler_proxy_semimajor_km',
                            'derived_kepler_proxy_perigee_altitude_km',
                            'derived_first_order_j2_raan_rate_deg_per_day'],
            'reference_epoch_utc': orbit['epoch_utc'],
            'input_literal_sha256': orbit['literal_pair_sha256'],
            'latent_parameter_id': 'tle_mean_elements_528_1963-10-27',
            'forward_operator': 'formal/scripts/physical_observable_bridge.py:orbital_observables',
            'required_before_physical_activation': [
                'primary_tracking_custody', 'observation_epochs_and_uncertainties',
                'calibrated_multi_epoch_forward_model'],
        },
        'C151#1': {
            'observables': ['derived_pressure_pa', 'derived_wind_to_east_m_s',
                            'derived_wind_to_north_m_s'],
            'station': winds[0]['station'],
            'nominal_date_utc': winds[0]['date_utc_nominal'],
            'pressure_levels_hpa': [r['pressure_hpa'] for r in winds],
            'latent_parameter_id': 'wind_field_nov_1963_with_altitude_time_and_position',
            'forward_operator': 'formal/scripts/physical_observable_bridge.py:recife_winds',
            'required_before_physical_activation': [
                'verified_local_Conde_wind_and_release_epoch',
                'spatial_temporal_interpolation_with_error',
                'object_ballistics_and_descent_model'],
        },
    }
    rows = []
    for item in contract['occurrences']:
        ref = item['snapshot_ref']
        occ = ref.rsplit(':', 1)[-1]
        require(occ in expected and item['citation_status'] == 'CURATED'
                and item['cited_source_ids'] == [expected[occ]]
                and item['independent_physical_observation_count'] is None,
                'source identity or independence changed: ' + occ)
        coverage_item = coverage.get((ref, expected[occ]))
        require(coverage_item is not None
                and coverage_item['matrix_line'] == item['matrix_line']
                and coverage_item['row_sha256'] == item['row_sha256']
                and coverage_item['bridge_record_id'] is None
                and coverage_item['activation'] is False,
                'matrix-joined citation not unactivated: ' + occ)
        rows.append({
            'source_id': expected[occ], 'matrix_occurrence': ref,
            'matrix_line': item['matrix_line'], 'row_sha256': item['row_sha256'],
            'status': 'DERIVED_OBSERVABLE_ONLY_NOT_528_TERMINAL_MEASUREMENT',
            'activation': False, 'lean_status': 'CANDIDATE_NOT_PROMOTED',
            'simulator_value': None,
            **source_values[occ],
        })
    require({r['matrix_occurrence'].rsplit(':', 1)[-1] for r in rows}
            == set(expected), 'partial crosswalk')
    param_ids = {p['id'] for p in json.loads((root /
        'research/constraints/ssr_1963_observable_graph.json').read_text())['parameters']}
    require(source_values['C179#1']['latent_parameter_id'] in param_ids,
            'orbital latent parameter reference lost')
    external_paths = ('research/meteorology/isd_caravelas_19631107_09.json',
                      'research/constraints/isd_caravelas_surface_1963.json')
    parents = {p: (root / p).read_bytes() for p in external_paths}
    report, graph = (json.loads(parents[p]) for p in external_paths)
    pending_paths = {
        'public/data/conde-un-1963-status-bridge.json': un1963.render,
        'public/data/conde-soviet-raw-route-bridge.json': soviet.render,
    }
    pending_raw = {path: (root / path).read_bytes() for path in pending_paths}
    for path, render in pending_paths.items():
        require(pending_raw[path] == render(), 'stale pending source bridge: ' + path)
    pending_edges = pending_documentary_routes(
        json.loads(pending_raw['public/data/conde-un-1963-status-bridge.json']),
        json.loads(pending_raw['public/data/conde-soviet-raw-route-bridge.json']))
    recife = next(x for x in rows if x['source_id'] == 'NOAA_IGRA_RECIFE_1963')
    caravelas = build_caravelas_external(
        report, graph, recife,
        {p: hashlib.sha256(raw).hexdigest() for p, raw in parents.items()})
    return {
        'schema': 'conde.observable-dependency-links/v1',
        'pending_documentary_edges': pending_edges,
        'pending_source_sha256': {path: hashlib.sha256(data).hexdigest()
                                  for path, data in pending_raw.items()},
        'external_source_edges': [caravelas],
        'matrix_git_blob_sha1': pg.MATRIX_BLOB_SHA,
        'contract_id': contract['contract_id'],
        'contract_status': contract['contract_status'],
        'parent_feed_sha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest()
                               for p in (dep_path, sci_path)},
        'edges': sorted(rows, key=lambda x: x['matrix_occurrence']),
        'epistemic_limits': {'derived_observables_not_terminal_observations': True,
                              'recife_is_not_conde': True,
                              'activated_constraints': 0,
                              'verified_528_reentry_time': None,
                              'verified_528_reentry_location': None,
                              'independent_physical_observation_count': None},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-site', action='store_true')
    group.add_argument('--check-site', action='store_true')
    args = ap.parse_args()
    content = encoded(build())
    if len(content) > 20_000:
        raise SystemExit('observable dependency links exceed 20 KB')
    target = ROOT / OUTPUT
    if args.write_site:
        target.write_bytes(content)
    elif not target.is_file() or target.read_bytes() != content:
        raise SystemExit('observable dependency export stale')
    print('OBSERVABLE_DEPENDENCY_OK', len(build()['edges']), len(content))

if __name__ == '__main__':
    main()
