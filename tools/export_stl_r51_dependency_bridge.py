#!/usr/bin/env python3
"""C241-LONTRA-R51: NASA reprint -> source genealogy -> *inactive* orbital prerequisites."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_stl_space_log_r51 import audit as audit_stl
from export_soviet_nasa_dependency_bridge import render as render_r49

ROOT = Path(__file__).resolve().parents[1]
R51_PATH = 'research/tle_custody/stl_space_log_nasa_r51.json'
R51_SHA = '2943e1f0a1ea6b4267f95a9ff14c022a55f7b4b0a7132cf5b37a489480bcf7e9'
R49_PATH = 'public/data/conde-soviet-nasa-dependency-bridge.json'
R49_SHA = 'e68cedb94fcff2e88db2ef81214ef2d5d279616bef24f7d9a05bcab90552782d'
OUT = ROOT / 'public/data/conde-stl-space-log-dependency-bridge.json'


def require(ok, message):
    if not ok:
        raise ValueError('R51 dependency: ' + message)


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, 'duplicate JSON key ' + key)
        obj[key] = value
    return obj


def read_pinned(root, path, sha):
    raw = (root / path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == sha, 'source SHA drift ' + path)
    return json.loads(raw, object_pairs_hook=no_duplicate_keys)


def load(root=ROOT):
    r51 = read_pinned(root, R51_PATH, R51_SHA)
    r49 = read_pinned(root, R49_PATH, R49_SHA)
    require(audit_stl(r51) == 'EDITORIAL_REPRODUCTION_MILES_PRINTED_SUBTYPE_PENDING_ZERO_CONSTRAINTS', 'R51 audit')
    require((root / R49_PATH).read_bytes() == render_r49(), 'upstream R49 regeneration drift')
    return r51, r49


def edge(source, target, relation):
    return {'source': source, 'target': target, 'relation': relation,
            'documentary_only': True, 'activation': False}


def build(r51, r49):
    require(r51['id'] == 'C241-LONTRA-R51', 'ledger identity')
    require(r49['id'] == 'ABELHA-C241-LONTRA-R49-01', 'parent bridge identity')
    require(r49['activation'] is False and r49['physical_domain_effect'] == 'THETA_UNCHANGED', 'parent inactive')
    require(r49['nasa_print_row'] == '1963-003A' and r49['soviet_row_explicit_norad_id'] is None,
            'prior 1963A/Soviet crosswalk')
    row = r51['printed_row']
    interpretation = r51['scientific_interpretation']
    require(row['international_designation_as_printed'] == '1963 3A', 'R51 print target')
    require(row['perigee_apogee_unit_on_b12'] == 'miles' and row['mile_variant_as_printed'] is None, 'documented miles, unresolved subtype')
    require(row['individual_measurement_utc'] is None and row['station_or_instrument'] is None
            and row['observational_uncertainty'] is None, 'no raw observation')
    require(interpretation['candidate_upstream_proven'] is False
            and interpretation['original_stl_pages_or_date_verified'] is False, 'hypothesis not proof')
    require(interpretation['independent_instrumental_sensors_added'] == 0
            and interpretation['new_physical_constraints_activated'] == 0, 'no physical promotion')
    graph = [
        edge('C241-LONTRA-R51', 'DOC:NASA-TMX59315:B12', 'PDF_FACSIMILE_PAGE_105'),
        edge('DOC:NASA-TMX59315:B12', 'WORK:STL-SPACE-LOG:v3:n4', 'EXPLICIT_REPRODUCTION_CREDIT'),
        edge('WORK:STL-SPACE-LOG:v3:n4', 'LATENT:STL_ORIGINAL_ISSUE', 'ORIGINAL_NOT_YET_RECOVERED'),
        edge('DOC:NASA-TMX59315:B12', 'DATUM:1963_3A_JAN31_PRINTED_PAIRS', 'PAIRS_NOT_INDEPENDENT_SENSORS'),
        edge('DATUM:1963_3A_JAN31_PRINTED_PAIRS', 'LATENT:mile_subtype', 'PAGE_B12_MILES_SUBTYPE_NOT_PRINTED'),
        edge('DATUM:1963_3A_JAN31_PRINTED_PAIRS', 'LATENT:pair_semantics', 'TWO_PRINTED_VALUES_WITH_UNKNOWN_MAPPING'),
        edge('DATUM:1963_3A_JAN31_PRINTED_PAIRS', 'H:JANUARY_PRINT_CONTEXT_ONLY', 'NOVEMBER_528_NOT_OBSERVED'),
        edge('C241-LONTRA-R49', 'H:SHARED_EDITORIAL_UPSTREAM', 'PRIOR_SOVIET_NASA_CANDIDATE'),
        edge('WORK:STL-SPACE-LOG:v3:n4', 'H:SHARED_EDITORIAL_UPSTREAM', 'STL_ANCESTRY_UNTESTED_FOR_SOVIET_TABLE'),
        edge('H:SHARED_EDITORIAL_UPSTREAM', 'LATENT:upstream_publication', 'NO_STL_ORIGINAL_OR_CHAIN_TO_BSE'),
        edge('H:JANUARY_PRINT_CONTEXT_ONLY', 'MODEL:orbital_cross_epoch', 'DIFFERENT_EPOCHS_NO_TRANSFER'),
        edge('LATENT:mile_subtype', 'MODEL:orbital_cross_epoch', 'MILE_VARIANT_REQUIRED_BEFORE_NUMERIC_CONVERSION'),
        edge('MODEL:orbital_cross_epoch', 'LEAN:candidateStlEpochAndUnitConsistency', 'PREMISES_MISSING_NOT_COMPILED'),
        edge('LEAN:candidateStlEpochAndUnitConsistency', 'PARAM:orbit_prior_527', 'CANDIDATE_NOT_ACTIVATED'),
        edge('H:JANUARY_PRINT_CONTEXT_ONLY', 'PARAM:orbit_prior_528', 'NO_528_MEASUREMENT'),
    ]
    latents = [
        {'id': key, 'unit': unit, 'value': None, 'activation': False}
        for key, unit in (
            ('LATENT:STL_ORIGINAL_ISSUE', 'verified_original_edition_id'),
            ('LATENT:upstream_publication', 'cited_historical_publication'),
            ('LATENT:mile_subtype', 'statute_or_nautical_definition_not_printed'),
            ('LATENT:pair_semantics', 'initial_vs_later_or_other_source'),
            ('LATENT:observational_utc', 'UTC'),
            ('LATENT:station', 'instrument_id'),
            ('LATENT:reference_frame', 'frame_identifier'),
            ('LATENT:instrument_covariance', 'covariance_matrix'),
        )
    ]
    return {
        'schema': 'conde.stl-space-log-dependency/v1',
        'id': 'ABELHA-C241-LONTRA-R51-01',
        'sources': [
            {'occurrence_id': 'C241-LONTRA-R51', 'path': R51_PATH, 'sha256': R51_SHA},
            {'occurrence_id': 'C241-LONTRA-R49', 'path': R49_PATH, 'sha256': R49_SHA,
             'role': 'previous_scientific_bridge_not_new_observation'},
        ],
        'custody': {'url': r51['source_url'], 'pdf_sha256': r51['pdf_sha256'],
                    'pdf_bytes': r51['pdf_bytes'], 'pdf_page_one_based': 105,
                    'print_page': 'B-12', 'printed_credit': r51['printed_reproduction_credit']},
        'source_class': 'HISTORICAL_EDITORIAL_REPRINT_NOT_INSTRUMENT_DATA',
        'stl_original_issue_observed': False,
        'printed_identity': row['international_designation_as_printed'],
        'source_epoch_context': 'initial_orbital_data_as_of_1963_01_31',
        'pair_mapping_proven': False,
        'printed_values': {'period_min': row['period_minutes_in_printed_order'],
                           'perigee_miles_as_printed': row['perigee_altitudes_in_printed_order'],
                           'apogee_miles_as_printed': row['apogee_altitudes_in_printed_order'],
                           'inclination_deg': row['inclinations_degrees_in_printed_order']},
        'altitude_unit_verified': 'miles',
        'altitude_mile_subtype_verified': None,
        'altitude_unit_evidence': 'NASA_TM_X59315_B12_FOOTER_PDF_PAGE_105',
        'diagnostics': {'two_body_km_interpretation_consistent': False,
                        'statute_mile_subtype_not_printed': True,
                        'is_instrumental_measurement': False},
        'other_norad_candidates': [
            {'norad_id': n, 'observation_utc': None, 'physical_constraint': None,
             'activation': False} for n in (527, 528, 529)],
        'hypotheses': ['H:JANUARY_PRINT_CONTEXT_ONLY', 'H:SHARED_EDITORIAL_UPSTREAM'],
        'graph': graph,
        'lean_candidate': 'candidateStlEpochAndUnitConsistency',
        'lean_status': 'CANDIDATE_ONLY_NOT_COMPILED',
        'simulator_parameters': [
            {'id': 'PARAM:orbit_prior_527', 'value': None, 'activation': False},
            {'id': 'PARAM:orbit_prior_528', 'value': None, 'activation': False},
        ],
        'latents': latents,
        'independent_instrumental_observations_added': 0,
        'new_confirmed_norad_528_observations': 0,
        'new_activated_physical_constraints': 0,
        'activation': False,
        'physical_domain_effect': 'THETA_UNCHANGED',
        'next_falsifiable_test': 'Recover STL Space Log vol.3 no.4 original and its mile subtype/paired-column legend, then trace dated publications of 1963 orbital elements to the BSE 1964 page 503; reject any transfer to NORAD 528 without dated instrumental target identification.',
    }


def render(root=ROOT):
    r51, r49 = load(root)
    return (json.dumps(build(r51, r49), sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--write-site', action='store_true')
    modes.add_argument('--check-site', action='store_true')
    args = parser.parse_args()
    output = render()
    if args.write_site:
        OUT.write_bytes(output)
    elif args.check_site:
        require(OUT.read_bytes() == output, 'published JSON changed')
    else:
        print(output.decode(), end='')


if __name__ == '__main__':
    main()
