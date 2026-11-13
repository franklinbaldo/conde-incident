#!/usr/bin/env python3
"""Source-locked documentary graph for the three unclosed Lontra handoffs.

This does not refetch archives, georeference 1963, or emit orbital predicates.
The input custody files remain the independent source of all archival claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'IBGE_CGEO10': 'research/geo/ibge_conde_1960_retro_mesh_2026-11-12.json',
    'UWM_10814': 'research/geo/uwm_aracaju_se_1954_1961_cartographic_custody.json',
    'NARA_302531012': 'research/archives/nara_bluebook_conde_naid_302531012_2026-11-12.md',
}
OUTPUT = 'public/data/conde-historical-dependency-links.json'
IBGE_ZIP = '261399b8557ee26c118e94b13cebf3b6b3e1c70e91b5e8438a348847b875120f'
NARA_JP2 = {
    '0809.jp2': ('302531013', '4e8e460cfe8dfa0f0d6ea6b02017e6ff63915935dc5be5bde8e96f52faf6f326'),
    '0810.jp2': ('302531014', '136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9'),
    '0811.jp2': ('302531015', 'f9c55ab0b14d6e121a4419bef72519a68db29a9ceea6c5bca5ea31fb826cdce7'),
}
NARA_BASE = 'https://catalog.archives.gov/medialz/partners/dc-metro/rg-341/597821/T1206-ProjectBlueBook_0049/images/'


def require(value: bool, reason: str) -> None:
    if not value:
        raise ValueError('historical documentary graph: ' + reason)


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')


def build(root: Path = ROOT) -> dict:
    raw = {k: (root / p).read_bytes() for k, p in FILES.items()}
    ibge, uwm = (json.loads(raw[k]) for k in ('IBGE_CGEO10', 'UWM_10814'))
    nara = raw['NARA_302531012'].decode('utf-8')
    geo = ibge['method_and_limits']
    ib = ibge['source']['binary']
    require(ibge['record_id'] == 'CGEO-10'
            and ibge['source']['url'].startswith('https://geoftp.ibge.gov.br/')
            and ib['source_zip_sha256'] == IBGE_ZIP
            and ib['municipality_code'] == '2908606'
            and ib['shapefile_record_1based'] == 2449
            and ib['vertex_count_including_closure'] == 47
            and ibge['source']['archive_year_label'] == 1960
            and ibge['source']['publication_year'] == 2011,
            'IBGE identity, date, numeric record or source bytes drift')
    require(geo['geographic_status'] == 'RETROSPECTIVE_COARSE_PROXY_ONLY'
            and geo['source_legal_boundary_1963'] is None
            and geo['horizontal_accuracy_m'] is None
            and geo['admissible_historical_boundary_1963'] is False
            and geo['verified_intervening_legal_changes_1960_1963'] is False
            and geo['orbital_constraint_activated'] is False,
            'IBGE reconstructed geometry promoted to historical boundary')
    obj = uwm['object']
    links = uwm['epistemic_and_model_links']
    reading = uwm['facsimile_reading']
    require(uwm['occurrence_id'] == 'ARCH-UWM-ARACAJU-SE-10814-20261112'
            and obj['contentdm_item_id'] == '10814'
            and obj['listed_publication_year'] == '1954'
            and obj['scale_denominator'] == 500000
            and obj['original_jp2_downloaded'] is False
            and obj['original_jp2_sha256'] is None
            and uwm['public_access']['catalog'] ==
            'https://collections.lib.uwm.edu/digital/collection/agdm/id/10814/'
            and 'CONDE' == reading['locality_visible']
            and '1961' in reading['footnote_2_transcription'],
            'UWM map locator, date or original file integrity drift')
    require(links['constraint_status'] == 'CONNECTED_PENDING_CALIBRATION'
            and links['orbital_and_physical_constraint'] == 'NOT_ACTIVATED'
            and links['historical_polygon_1963'] is None
            and links['administrative_boundary_1963'] is None
            and links['coordinates_of_alleged_fall'] is None
            and links['historical_reentry_inside_conde_evaluable'] is False
            and links['related_legacy_claim_ids'] == ['C24'],
            'UWM metadata improperly promoted to 1963 boundary or impact')
    require('naId: 302531012' in nara and 'T1206, rolo 49' in nara
            and '8 Nov 1963' in nara and 'O GLOBO' in nara
            and '14 NOV 1963' in nara and '21 NOV 1963' in nara
            and 'não' in nara.lower() and 'Hoax' in nara,
            'NARA case unit dates, newspaper candidate or caution missing')
    for name, (object_id, sha) in NARA_JP2.items():
        require(any(name in row and object_id in row and sha in row
                    and NARA_BASE + name in row
                    for row in nara.splitlines() if row.startswith('|')),
                'NARA image table identity/hash mismatch: ' + name)
    # NARA's 3 digital objects are pages of ONE administrative case unit.
    docs = [
        {'id': 'NARA-BB-302531012', 'kind': 'ADMINISTRATIVE_FILE_UNIT',
         'url': 'https://catalog.archives.gov/id/302531012',
         'content_family': 'ONE_BLUE_BOOK_CASE_FILE_NOT_THREE_WITNESSES',
         'claimed_physical_observation': None},
    ]
    for name, (object_id, sha) in NARA_JP2.items():
        docs.append({'id': 'NARA-' + object_id, 'kind':
                     {'0809.jp2': 'ADMINISTRATIVE_RECORD_CARD',
                      '0810.jp2': 'USAIRA_TELEGRAM_CITES_NEWSPAPER',
                      '0811.jp2': 'USAIRA_TELEGRAM_REPEATS_CONSULAR_CHAIN'}[name],
                     'url': NARA_BASE + name, 'sha256': sha,
                     'digital_object_id': object_id, 'file_unit': 'NARA-BB-302531012',
                     'independent_physical_witness': False})
    docs += [
        {'id': 'O-GLOBO-1963-11-08-CANDIDATE', 'kind': 'UNRECOVERED_NEWSPAPER_ISSUE',
         'url': None, 'date_mentioned_in_telegram': '1963-11-08',
         'independent_reporting': None, 'actual_edition_verified': False},
        {'id': 'UWM-AGDM-10814', 'kind': 'HISTORICAL_CARTOGRAPHIC_FACSIMILE',
         'url': uwm['public_access']['catalog'], 'map_base_edition_year': 1954,
         'roads_update_year': 1961, 'scan_publication_date': None,
         'original_file_sha256': None, 'toponym': 'CONDE',
         'georeferenced_for_1963': False},
        {'id': 'IBGE-CGEO-10', 'kind': 'RETROSPECTIVE_1960_STATISTICAL_MESH',
         'url': ibge['source']['url'], 'source_zip_sha256': IBGE_ZIP,
         'source_year_label': 1960, 'publication_year': 2011,
         'municipality_code': '2908606', 'vertices_including_closure': 47,
         'horizontal_accuracy_m': None, 'contemporary_1963_survey': False},
        {'id': 'CONDE-BOUNDARY-1963-PENDING', 'kind': 'MISSING_HISTORICAL_LEGAL_GEOMETRY',
         'dated_legal_act': None, 'historical_datum': None,
         'survey_uncertainty_m': None, 'boundary_1963': None,
         'physical_filter_activated': False},
        {'id': 'C24#1', 'kind': 'MATRIX_CURRENT_GEOGRAPHY_REFERENCE',
         'current_geography_is_1963_boundary': False},
    ]
    edges = [
        {'from': 'NARA-302531013', 'to': 'NARA-BB-302531012', 'kind': 'ADMINISTRATIVE_CLASSIFICATION_IN_CASE'},
        {'from': 'NARA-302531014', 'to': 'NARA-BB-302531012', 'kind': 'USAIRA_CORRESPONDENCE_IN_CASE'},
        {'from': 'NARA-302531015', 'to': 'NARA-302531014', 'kind': 'SAME_CONSULAR_CIRCULATION_CHAIN_NOT_SECOND_WITNESS'},
        {'from': 'NARA-302531014', 'to': 'O-GLOBO-1963-11-08-CANDIDATE', 'kind': 'CITES_UNRECOVERED_ISSUE_NOT_VERIFIED'},
        {'from': 'UWM-AGDM-10814', 'to': 'C24#1', 'kind': 'HISTORICAL_TOPONYM_CONTEXT_NOT_BOUNDARY'},
        {'from': 'IBGE-CGEO-10', 'to': 'C24#1', 'kind': 'RETROSPECTIVE_MUNICIPAL_PROXY_NOT_1963_SURVEY'},
    ]
    ids = [d['id'] for d in docs]
    require(len(ids) == len(set(ids)) and
            all(e['from'] in ids and e['to'] in ids for e in edges),
            'duplicate node or orphan edge')
    return {
        'schema': 'conde.historical-documentary-dependency-graph/v1',
        'id': 'POLVO-C241-P14-GEO-BB-DEPENDENCIES',
        'issue': 'https://github.com/franklinbaldo/conde-incident/issues/88',
        'handoffs': [f'https://github.com/franklinbaldo/polvo/issues/{n}' for n in (2, 4, 6)],
        'custody_source_sha256': {FILES[k]: hashlib.sha256(v).hexdigest() for k, v in raw.items()},
        'nodes': docs, 'edges': edges,
        'rejected_edges': [
            {'from': 'UWM-AGDM-10814', 'to': 'CONDE-BOUNDARY-1963-PENDING',
             'reason': 'UNKNOWN_LEGAL_VALIDITY_DATUM_SURVEY_UNCERTAINTY'},
            {'from': 'IBGE-CGEO-10', 'to': 'CONDE-BOUNDARY-1963-PENDING',
             'reason': 'BACKCAST_FROM_1991_MESH_NOT_1963_BOUNDARY'},
            {'from': 'NARA-302531013', 'to': 'CONDE-BOUNDARY-1963-PENDING',
             'reason': 'ADMINISTRATIVE_LABEL_NOT_PHYSICAL_GEOGRAPHY'},
        ],
        'candidate_links': [
            {'variable': 'conde_municipal_boundary_1963',
             'source_candidates': ['UWM-AGDM-10814', 'IBGE-CGEO-10'],
             'status': 'CONNECTED_PENDING_CALIBRATION',
             'requires': ['legally_effective_1963_boundary', 'historical_geodetic_frame',
                          'accuracy_and_epoch', 'independent_geometry_confrontation'],
             'value': None, 'lean_predicate': None, 'simulator_filter': None},
            {'variable': 'original_O_Globo_1963_11_08_lineage',
             'source_candidates': ['NARA-302531014'],
             'status': 'CONNECTED_PENDING_SOURCE_RECOVERY',
             'requires': ['original_newspaper_fascimile', 'page_and_edition',
                          'attribution_and_wire_credit'], 'value': None,
             'lean_predicate': None, 'simulator_filter': None},
        ],
        'provenance': {
            'nara_digital_images_one_administrative_unit': 3,
            'nara_independent_physical_witnesses_added': 0,
            'uwm_original_jp2_fully_hashed': False,
            'ibge_1991_retroconstruction_is_1963_survey': False,
            'one_institutional_cartography_family_not_two_independent_1963_surveys': True,
            'source_records_refetched_by_exporter': False,
        },
        'result': {'new_connected_edges': len(edges),
                   'new_activated_physical_predicates': 0,
                   'admissible_orbital_domain': 'UNCHANGED_NOT_EVALUATED',
                   'historical_impact_location': None},
    }


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    group = cli.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = cli.parse_args()
    data = encode(build())
    require(len(data) < 20_000, 'export exceeds project size policy')
    target = ROOT / OUTPUT
    if args.write:
        target.write_bytes(data)
    else:
        require(target.exists() and target.read_bytes() == data, 'export stale or modified')
    print('HISTORICAL_DEPENDENCY_LINKS_OK', len(data))


if __name__ == '__main__':
    main()
