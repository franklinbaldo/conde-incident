#!/usr/bin/env python3
"""Connect NASA STL printed-pair chronology to inactive Lean/simulator prerequisites.

One editorial PDF, one printed object 1963 3A, no new NORAD 528 tracking.
"""
import argparse
import hashlib
import json
from pathlib import Path

from audit_stl_space_log_r51 import audit as audit_r51
from export_stl_mile_subtype_bridge import render as render_r53

ROOT = Path(__file__).resolve().parents[1]
R51 = 'research/tle_custody/stl_space_log_nasa_r51.json'
R51_SHA = '2943e1f0a1ea6b4267f95a9ff14c022a55f7b4b0a7132cf5b37a489480bcf7e9'
CERV = 'research/statistics/C241_stl_printed_pair_coherence.json'
CERV_SHA = '50c6d92bdeee8e6f3368faa6200ecc67c03f39fcc770883a60fcfa8f05b12c48'
PARENT = 'public/data/conde-stl-mile-subtype-bridge.json'
PARENT_SHA = 'f70c8defe88497eb3790485c8ec32046c44a5a7c69e622a59d5e47c7ba148589'
OUT = ROOT / 'public/data/conde-stl-epoch-independence-bridge.json'


def require(value, reason):
    if not value:
        raise ValueError('STL-epoch bridge: ' + reason)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate key: ' + key)
        result[key] = value
    return result


def pinned(root, path, expected):
    data = (root / path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected, 'source SHA drift: ' + path)
    return json.loads(data, object_pairs_hook=unique)


def load(root=ROOT):
    r51 = pinned(root, R51, R51_SHA)
    cerv = pinned(root, CERV, CERV_SHA)
    parent = pinned(root, PARENT, PARENT_SHA)
    require(audit_r51(r51) == 'EDITORIAL_REPRODUCTION_MILES_PRINTED_SUBTYPE_PENDING_ZERO_CONSTRAINTS', 'source R51 audit')
    require((root / PARENT).read_bytes() == render_r53(), 'parent bridge regeneration')
    return r51, cerv, parent


def edge(source, target, relation):
    return {'source': source, 'target': target, 'relation': relation,
            'documentary_only': True, 'activation': False}


def build(r51, cerv, parent):
    require(r51['id'] == 'C241-LONTRA-R51' and cerv['pinned_source_id'] == r51['id'], 'source lineage')
    require(cerv['id'] == 'C241-CERVO-STL-PAIR-COHERENCE', 'derived audit ID')
    require(cerv['source_sha256'] == R51_SHA and cerv['source_pdf_sha256'] == r51['pdf_sha256'], 'shared PDF SHA')
    require(cerv['printed_designation'] == r51['printed_row']['international_designation_as_printed'] == '1963 3A', 'printed object')
    require(cerv['source_row_note'] == r51['printed_row']['row_note'], 'original row note')
    require(cerv['row_note_initial_data_as_of_day'] == '1963-01-31', 'editorial as-of date')
    for k in ('initial_data_column_index', 'other_column_measurement_utc',
              'columns_are_coepoch', 'period_and_altitude_element_conventions_equal'):
        require(cerv[k] is None, 'unknown remains unknown: ' + k)
    require(cerv['printed_altitude_sum'] == [620, 620], 'column-altitude checksum')
    require(cerv['period_nominal_difference_first_minus_second_seconds'] == '6', 'nominal printed delta')
    rm = cerv['conditional_rounding_model']
    require(rm['intervals_touch_at_minutes'] == '94.65' and rm['tie_handling_unknown'] is True,
            'conditional rounding envelope')
    require(rm['zero_underlying_difference_excluded'] is False and
            rm['same_input_distinct_prints_under_one_deterministic_rule'] is False and
            rm['no_published_rounding_policy_authenticated'] is True, 'not instrument chronology')
    require(cerv['original_stl_issue_retrieved'] is False and r51['stl_original_issue_retrieved'] is False,
            'unrecovered upstream original')
    design = cerv['observational_design']
    require(design['new_528_tracking_observations'] == 0 and design['new_instrumental_sensors'] == 0 and
            design['active_constraint'] is False and design['historical_mcmc'] == 'NOT_RUN',
            'unsupported observational promotion')
    require(parent['id'] == 'ABELHA-C241-LONTRA-R53-01' and
            parent['custody']['pdf_sha256'] == r51['pdf_sha256'] and
            parent['independent_from_R51'] is False and parent['activation'] is False and
            parent['physical_domain_effect'] == 'THETA_UNCHANGED', 'upstream contract')
    require(parent['lean_status'] == 'CANDIDATE_ONLY_NOT_COMPILED' and
            parent['new_independent_instrumental_observations'] == 0, 'upstream non-promotion')

    edges = [
        edge('C241-LONTRA-R51', 'DOC:NASA-TMX59315:B12', 'ONE_PRINTED_FACSIMILE'),
        edge('C241-CERVO-STL-PAIR-COHERENCE', 'C241-LONTRA-R51', 'DERIVED_FROM_SAME_PDF_NOT_INDEPENDENT'),
        edge('ABELHA-C241-LONTRA-R53-01', 'DOC:NASA-TMX59315:B12', 'SAME_PDF_NOT_NEW_SENSOR'),
        edge('DOC:NASA-TMX59315:B12', 'WORK:STL-SPACE-LOG:v3:n4', 'REPRODUCES_ORIGINAL_NOT_HELD'),
        edge('DOC:NASA-TMX59315:B12', 'DATUM:1963_3A_JAN31_PRINTED_PAIRS', 'EDITORIAL_AS_OF_NOT_MEASUREMENT_UTC'),
        edge('DATUM:1963_3A_JAN31_PRINTED_PAIRS', 'H:PRINTED_PAIR_COEPOCH', 'UNVERIFIED'),
        edge('H:PRINTED_PAIR_COEPOCH', 'LATENT:paired_column_semantics', 'UNKNOWN_ORDER_AND_EPOCH'),
        edge('C241-CERVO-STL-PAIR-COHERENCE', 'H:SAME_MEAN_ALTITUDE_DIFFERENT_PRINTED_PERIOD', 'EXACT_INTERNAL_DIAGNOSTIC'),
        edge('H:SAME_MEAN_ALTITUDE_DIFFERENT_PRINTED_PERIOD', 'LATENT:element_conventions', 'MAY_DIFFER'),
        edge('H:SAME_MEAN_ALTITUDE_DIFFERENT_PRINTED_PERIOD', 'LATENT:rounding_policy', 'COUNTERFACTUAL_ONLY'),
        edge('LATENT:paired_column_semantics', 'LEAN:candidateStlEpochAndUnitConsistency', 'MISSING_PREMISE'),
        edge('LATENT:element_conventions', 'LEAN:candidateStlEpochAndUnitConsistency', 'MISSING_PREMISE'),
        edge('LATENT:rounding_policy', 'LEAN:candidateStlEpochAndUnitConsistency', 'MISSING_PREMISE'),
        edge('LEAN:candidateStlEpochAndUnitConsistency', 'MODEL:printed_pair_epoch_translation', 'CONDITIONAL_NOT_COMPILED'),
        edge('MODEL:printed_pair_epoch_translation', 'PARAM:orbit_prior_527', 'NO_INSTRUMENT_EPOCH'),
        edge('MODEL:printed_pair_epoch_translation', 'PARAM:orbit_prior_528', 'DIFFERENT_OBJECT_NO_TRANSFER'),
    ]
    latents = [{'id': name, 'value': None, 'activation': False} for name in (
        'LATENT:paired_column_semantics', 'LATENT:element_conventions', 'LATENT:rounding_policy',
        'LATENT:first_column_instrument_utc', 'LATENT:other_column_instrument_utc',
        'LATENT:station', 'LATENT:reference_frame', 'LATENT:measurement_covariance',
        'LATENT:STL_original_issue')]
    return {
        'schema': 'conde.stl-epoch-independence/v1',
        'id': 'ABELHA-C241-STL-EPOCH-INDEPENDENCE-R53',
        'sources': [
            {'occurrence_id': 'C241-LONTRA-R51', 'path': R51, 'sha256': R51_SHA, 'role': 'original_pdf_custody_ledger'},
            {'occurrence_id': 'C241-CERVO-STL-PAIR-COHERENCE', 'path': CERV, 'sha256': CERV_SHA,
             'role': 'derived_arithmetic_same_pdf_not_independent_sensor'},
            {'occurrence_id': 'ABELHA-C241-LONTRA-R53-01', 'path': PARENT, 'sha256': PARENT_SHA,
             'role': 'existing_mile_subtype_bridge_same_pdf'}],
        'custody': {'pdf_url': r51['source_url'], 'pdf_sha256': r51['pdf_sha256'],
                    'pdf_page_one_based': 105, 'printed_page': 'B-12',
                    'original_stl_issue_observed': False},
        'printed_target': '1963 3A', 'not_a_norad_528_observation': True,
        'as_of_label': '1963-01-31', 'as_of_meaning': 'EDITORIAL_INITIAL_DATA_NOT_MEASUREMENT_UTC',
        'measurement_epoch_utc': None, 'first_column_is_initial': None,
        'other_column_measurement_utc': None, 'columns_coepoch': None,
        'period_printed_delta_seconds': '6', 'mean_altitudes_in_printed_miles': ['310', '310'],
        'underlying_period_difference_identified': False,
        'period_difference_excludes_zero': False,
        'hypotheses': ['H:PRINTED_PAIR_COEPOCH', 'H:SAME_MEAN_ALTITUDE_DIFFERENT_PRINTED_PERIOD'],
        'graph': edges,
        'lean_candidate': 'candidateStlEpochAndUnitConsistency',
        'lean_status': 'CANDIDATE_ONLY_NOT_COMPILED',
        'latents': latents,
        'simulator_parameters': [{'id': name, 'value': None, 'activation': False}
                                 for name in ('PARAM:orbit_prior_527', 'PARAM:orbit_prior_528')],
        'new_independent_instrumental_observations': 0,
        'new_activated_physical_constraints': 0,
        'activation': False, 'physical_domain_effect': 'THETA_UNCHANGED',
        'next_falsifiable_test': 'Retrieve the original STL Space Log v3 n4 caption and column definitions; recover time-tagged sensor data with station, frame, covariance and object mapping before any November 528 inference.'
    }


def render(root=ROOT):
    return (json.dumps(build(*load(root)), sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument('--write-site', action='store_true')
    mode.add_argument('--check-site', action='store_true')
    args = ap.parse_args()
    data = render()
    if args.write_site:
        OUT.write_bytes(data)
    elif args.check_site:
        require(OUT.read_bytes() == data, 'site drift')
    else:
        print(data.decode(), end='')

if __name__ == '__main__':
    main()
