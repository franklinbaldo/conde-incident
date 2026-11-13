#!/usr/bin/env python3
"""Source-level likelihood gate for the 1963-003B corpus, not an orbital fit.

An archival finding aid, a fitted TLE, a compiled catalog day and a
sensor observation have different sampling mechanisms. No multiplication
of independent factors is permitted until their lineage and errors exist.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NORAD_CONTEXT = 'public/data/conde-norad-context.json'
FILMS = 'research/constraints/baker_nunn_ru301_1963_film_index.json'
SERIES = 'research/statistics/raan_527_528_529_1963.json'
SPLIT = 'research/statistics/raan_chronological_holdout_1963.json'
IDENTITY = 'research/tle_custody/catalog_identity_527_529_2026-11-12.json'
INPUTS = (NORAD_CONTEXT, FILMS, SERIES, SPLIT, IDENTITY)
OUTPUT = 'research/statistics/raan_source_likelihood_readiness_C241.json'
# Frozen UTC experiment partitions (source manifest C241-P4/G25).
# Do not trust a mutated manifest to redefine the chronological gate.
FROZEN_BOUNDARIES = {
    'fit_before_utc': '1963-08-01T00:00:00Z',
    'validation_before_utc': '1963-10-01T00:00:00Z',
    'evaluation_from_utc': '1963-10-01T00:00:00Z',
}
REQUIRED_OBSERVABLE_FIELDS = (
    'observation_epoch_utc', 'instrument_id', 'reference_frame',
    'measured_quantity', 'measured_value', 'units',
    'measurement_error_model_ref', 'observation_selection_model_ref',
    'source_document_id', 'source_page_or_record',
    'upstream_independence_assessment', 'physical_forward_operator_ref',
)


def is_utc(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith('Z'):
        return False
    try:
        result = datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError:
        return False
    return result.tzinfo == timezone.utc


def structural_gate(candidate: dict) -> dict:
    """Check requested metadata, never authenticate claimed primary evidence."""
    if type(candidate.get('norad')) is not int or candidate['norad'] != 528:
        return {'structurally_complete': False, 'blockers': ['OBJECT_NOT_528']}
    missing = [key for key in REQUIRED_OBSERVABLE_FIELDS
               if candidate.get(key) is None or candidate.get(key) == '']
    if 'observation_epoch_utc' not in missing and not is_utc(
            candidate['observation_epoch_utc']):
        missing.append('observation_epoch_utc')
    if not isinstance(candidate.get('source_document_id'), str):
        if 'source_document_id' not in missing:
            missing.append('source_document_id')
    return {'structurally_complete': not missing,
            'blockers': sorted(set(missing)),
            'historical_authenticity': 'NOT_ASSESSED',
            'independent_likelihood_factor': 'NOT_AUTHORIZED'}


def digest(data: bytes, name: str) -> dict:
    return {'path': name, 'sha256': hashlib.sha256(data).hexdigest()}


def build(norad_bytes: bytes, films_bytes: bytes, series_bytes: bytes,
          split_bytes: bytes, identity_bytes: bytes) -> dict:
    context, films, series, split, identity = [
        json.loads(b) for b in (
            norad_bytes, films_bytes, series_bytes, split_bytes, identity_bytes)]
    if context['schema'] != 'conde.norad-documentary-context/v1':
        raise ValueError('NORAD source contract drift')
    if context['epistemic_limits']['no_source_is_an_observation_of_norad_528'] is not True:
        raise ValueError('NORAD provenance reclassification requires review')
    norad_records = context['records']
    if len(norad_records) != 5 or len({r['occurrence_id'] for r in norad_records}) != 5:
        raise ValueError('NORAD crosswalk membership drift')
    by_source = {r['source_id']: r for r in norad_records}
    if len(by_source) != 5:
        raise ValueError('same NORAD document repeated with independent identity')
    for src, obj, yr in (
            ('MOR-NORAD-1961-AGREEMENT', [], '1961'),
            ('MOR-NORAD-1963-NOV12', [687, 688], '1963'),
            ('MOR-NORAD-1963-NOV14', [688], '1963'),
            ('MOR-NORAD-1964-NOV30-09', [], '1964'),
            ('MOR-NORAD-1964-NOV30-10', [943], '1964')):
        rec = by_source.get(src)
        if (rec is None or rec['object_ids_reported_in_this_document'] != obj
                or not rec['source_date'].startswith(yr + '-')
                or rec['physical_528_constraint'] is not None
                or rec['role'] != 'DOCUMENTARY_CONTEXT_NOT_528_MEASUREMENT'):
            raise ValueError(f'object/chronology drift in {src}; manual reassessment needed')
    if (by_source['MOR-NORAD-1964-NOV30-09']['catalogue_date_claim'] != '1963-11-30'
            or by_source['MOR-NORAD-1964-NOV30-10']['catalogue_date_claim'] != '1963-11-30'):
        raise ValueError('catalog date error control drift')
    groups = context['declared_documentary_groups']
    if len(groups) != 2 or [set(g['source_ids']) for g in groups] != [
            {'MOR-NORAD-1963-NOV12', 'MOR-NORAD-1963-NOV14'},
            {'MOR-NORAD-1964-NOV30-09', 'MOR-NORAD-1964-NOV30-10'}]:
        raise ValueError('NORAD lineage groups drift')
    if films['schema'] != 'conde.archival-instrument-crosswalk/v1':
        raise ValueError('film archive schema drift')
    indexed = films['film_index_entries']
    if len(indexed) != 15 or len({r['id'] for r in indexed}) != 15:
        raise ValueError('Baker-Nunn selected film membership drift')
    for film in indexed:
        if (film['station_code'] != 'SC-8' or film['object_catalog_id'] is not None
                or film['observation_epoch_utc'] is not None
                or film['angular_values'] is not None
                or film['angular_uncertainty'] is not None
                or film['film_sheet_content_inspected'] is not False
                or film['hard_physical_constraint'] is not False):
            raise ValueError('film may have new evidence: reassess likelihood manually')
    if (series['provenance']['status'] != 'SECONDARY_CATALOGUE_DERIVED_NOT_ORIGINAL_TRACK'
            or split['design_status'] != 'RETROSPECTIVE_TIME_SPLIT_NOT_BLINDED'):
        raise ValueError('mirror lineage or retrospective holdout changed')
    if split.get('schema') != 'conde.raan-chronological-split/v1' or (
            split.get('boundaries') != FROZEN_BOUNDARIES):
        raise ValueError('holdout temporal boundary contract changed')
    fit_cut = datetime.fromisoformat(FROZEN_BOUNDARIES['fit_before_utc'].replace('Z', '+00:00'))
    evaluation_cut = datetime.fromisoformat(
        FROZEN_BOUNDARIES['evaluation_from_utc'].replace('Z', '+00:00'))
    observed = {527: set(), 528: set(), 529: set()}
    for row in series['records']:
        if type(row['norad']) is not int or row['norad'] not in observed:
            raise ValueError('invalid NORAD object in secondary mirror')
        if not is_utc(row['epoch_utc']) or not row['epoch_utc'].startswith('1963-'):
            raise ValueError('invalid secondary epoch')
        observed[row['norad']].add(row['epoch_utc'])
    for k in observed:
        frozen = split['memberships'][str(k)]
        members = sum((frozen[part] for part in ('fit', 'validation', 'evaluation')), [])
        for part in ('fit', 'validation', 'evaluation'):
            for value in frozen[part]:
                if not is_utc(value):
                    raise ValueError('holdout temporal boundary contains invalid UTC epoch')
                instant = datetime.fromisoformat(value.replace('Z', '+00:00'))
                valid = (instant < fit_cut if part == 'fit' else
                         fit_cut <= instant < evaluation_cut if part == 'validation' else
                         instant >= evaluation_cut)
                if not valid:
                    raise ValueError(f'holdout leakage: temporal boundary {k} {part} {value}')
        if len(members) != len(set(members)) or set(members) != observed[k]:
            raise ValueError('frozen temporal membership changed; holdout leakage risk')
    if [len(observed[k]) for k in observed] != [20, 45, 54]:
        raise ValueError('secondary mirror epoch count drift')
    splits = {
        part: sum(len(split['memberships'][str(k)][part]) for k in observed)
        for part in ('fit', 'validation', 'evaluation')
    }
    if splits != {'fit': 61, 'validation': 23, 'evaluation': 35}:
        raise ValueError('retrospective split count drift')
    primary = identity['primary_date_only_record']
    if (primary['document_id'] != 'NASA NTRS 19640001198'
            or primary['catalog_designator_printed'] != '1963 3B'
            or primary['decay_day'] != '1963-11-08'
            or primary['printed_page'] != 8):
        raise ValueError('NASA primary documentary day-only binding drift')
    # This is a count of eligible evidence IN THESE INPUTS, not a claim
    # about the number of observations actually made in 1963.
    return {
        'schema': 'conde.raan-source-likelihood-readiness/v1',
        'classification': 'DOCUMENTARY_FACTOR_ELIGIBILITY_AUDIT_NO_HISTORICAL_POSTERIOR',
        'question': 'Which inspected records could act as calibrated physical likelihood factors for NORAD 528?',
        'input_sha256': [digest(raw, path) for raw, path in zip(
            (norad_bytes, films_bytes, series_bytes, split_bytes, identity_bytes), INPUTS)],
        'candidate_groups': [
            {
                'name': '1963_TLE_NUMERIC_MIRROR',
                'occurrences': ['C25#1', 'C179#1', 'C180#1', 'C181#1', 'C241-L3'],
                'source_path': SERIES,
                'unique_epochs_by_object': {str(k): len(observed[k]) for k in observed},
                'n_528_entries': len(observed[528]),
                'upstream_family': 'SINGLE_SECONDARY_CATALOGUE_UNVERIFIED_SENSOR_LINEAGE',
                'factor_eligibility': 'PENDING_PRIMARY_RAW_OBSERVABLE_SENSOR_FRAME_COVARIANCE',
                'blockers': ['RAW_1963_TRACKING_RECORD', 'EPOCH_SEMANTICS',
                             'SENSOR_FRAME_AND_ERROR', 'WITHIN_LINEAGE_DEPENDENCE'],
            },
            {
                'name': 'NASA_1963_003B_DAY_ONLY_STATUS',
                'occurrences': ['C197#1', 'C198#1'],
                'source_document_id': primary['document_id'],
                'printed_page': primary['printed_page'],
                'source_url': primary['url'],
                'catalog_status_day': primary['decay_day'],
                'factor_eligibility': 'NOT_AN_OBSERVED_SENSOR_EVENT_OR_TERMINAL_TIME',
                'blockers': ['OBSERVATION_EPOCH', 'TERMINAL_EVENT_SEMANTICS',
                             'STATUS_REPORT_SELECTION_PROCESS'],
            },
            {
                'name': 'NORAD_SPADATS_MOR_CONTEXT',
                'occurrences': [r['occurrence_id'] for r in norad_records],
                'document_lineages': sorted(set(r['document_lineage'] for r in norad_records)),
                'objects_named_in_documents': sorted(set(
                    k for r in norad_records for k in r['object_ids_reported_in_this_document'])),
                'n_documents': len(norad_records),
                'n_documents_about_528': 0,
                'factor_eligibility': 'NO_528_MEASUREMENT_IN_INSPECTED_DOCUMENTS',
                'blockers': ['OBJECT_ID_528', 'SENSOR_RECORD_528'],
            },
            {
                'name': 'SMITHSONIAN_RU301_SC8_FILM_INDEX',
                'occurrences': [o['id'] for o in films['document_occurrences']],
                'source_url': films['source']['original_url'],
                'n_curated_film_indices': len(indexed),
                'n_with_authenticated_target_528': 0,
                'factor_eligibility': 'INVENTORY_ONLY_TARGET_NOT_VERIFIED',
                'blockers': ['FILM_CONTENT', 'TARGET_ID', 'OBSERVATION_TIME',
                             'MEASURED_ANGLE', 'CALIBRATED_ERROR'],
            },
        ],
        'independence': {
            'lineage_count_is_not_effective_sample_size': True,
            'secondary_mirror_is_not_independent_from_its_catalog_reprints': True,
            'norad_documents_1963_sputnik46_share_reporting_family': True,
            'nasa_norad_data_exchange_possible_not_proof_of_exact_record_ancestry': True,
            'number_of_independent_528_sensor_sources_identified_in_inputs': 0,
            'number_of_independent_528_sensor_sources_in_history': None,
            'factorization_into_independent_observations': 'NOT_JUSTIFIED',
        },
        'frozen_holdout': {
            'status': split['design_status'],
            'memberships_by_partition': splits,
            'same_secondary_source_family_across_all_partitions': True,
            'prediction_score': 'NOT_RUN',
        },
        'model_contract': {
            'forward_observable': 'H_528(theta, observation_utc, frame, sensor)',
            'required_fields': list(REQUIRED_OBSERVABLE_FIELDS),
            'likelihood_scale_or_covariance': None,
            'selection_and_non_detection_model': None,
            'priors_documented_for_historical_run': None,
            'MCMC_historical': 'NOT_RUN',
            'posterior_historical': 'NOT_IDENTIFIED',
            'admissible_geographic_domain_change': 'NOT_EVALUABLE',
            'active_constraint': False,
        },
        'scope_limit': 'Zero eligible 528 instrument records IN THESE INSPECTED INPUTS, not evidence that the object was never observed.',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = build(*((ROOT / path).read_bytes() for path in INPUTS))
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    output = ROOT / OUTPUT
    if args.check:
        if not output.exists() or output.read_text(encoding='utf-8') != rendered:
            raise SystemExit('drift in source readiness: regenerate and review the audit')
        print('PASS: likelihood readiness matches source bytes and frozen holdout')
    else:
        output.write_text(rendered, encoding='utf-8')
        print(f'written {output.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
