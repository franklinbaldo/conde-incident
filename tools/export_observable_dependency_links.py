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
    return {
        'schema': 'conde.observable-dependency-links/v1',
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
