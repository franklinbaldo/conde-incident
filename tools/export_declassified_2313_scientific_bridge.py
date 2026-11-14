#!/usr/bin/env python3
"""C241-L51: two verified facsimiles bridge documentary identity, not orbital data."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_quest_stage_scientific_bridge as previous

SOURCE = 'research/tle_custody/declassified_facsimiles_C241-L51.json'
PARENT = 'public/data/conde-quest-stage-scientific-bridge.json'
OUT = ROOT / 'public/data/conde-declassified-2313-scientific-bridge.json'
PINS = {
    SOURCE: '8dd677f66becd34112e0370f5fe6c676110b4828e73083783dcab12a00f7412c',
    PARENT: 'e68ef57489f65be7209070e542125444c36fd4bf6ff181916984f13f0865b9e7',
}


def require(condition, why):
    if not condition:
        raise ValueError('C241-L51 bridge: ' + why)


def no_duplicate_keys(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, 'duplicate JSON key: ' + k)
        result[k] = v
    return result


def sources(root=ROOT):
    loaded = {}
    for rel, digest in PINS.items():
        raw = (root / rel).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, 'source hash drift: ' + rel)
        loaded[rel] = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    return loaded


def build(data, parent_revalidated=True):
    m, parent = data[SOURCE], data[PARENT]
    from tools.tle_declassified_facsimiles_c241_l51 import audit as original_audit
    original_audit(m)
    require(m['schema'] == 'c241-l51-declassified-facsimiles-v1'
            and m['evidence_id'] == 'C241-L51'
            and m['status'] == 'RETROSPECTIVE_DOCUMENTARY_ONLY'
            and m['physical_constraint_active'] is False
            and m['orbital_parameters'] == 'THETA_UNCHANGED', 'source status')
    docs = m['documents']
    require(len(docs) == 2 and {d['id'] for d in docs} == {
        'NSA-BYE-19385-75', 'NRO-SIGINT-STORY-1994'}, 'document identity/count')
    by_id = {d['id']: d for d in docs}
    nsa, nro = by_id['NSA-BYE-19385-75'], by_id['NRO-SIGINT-STORY-1994']
    require(nsa['title'] == 'NSA in Space' and nsa['authored_year'] == 1975
            and nsa['release_date'] == '2017-11-08'
            and nsa['url'] == 'https://www.governmentattic.org/26docs/NSAinSpaceViaNRO_1975.pdf'
            and nsa['bytes'] == 4853647
            and nsa['sha256'] == '3d5d7a22608d3eb9ab23f61f46da924708d471917f77ee5f3a68ae8910aeab74'
            and nsa['pdf_pages'] == 248 and nsa['pdf_page_1_based'] == 132
            and nsa['printed_page'] == 5 and 'Appendix A' in nsa['printed_page_section']
            and nsa['class'] == 'RETROSPECTIVE_ADMINISTRATIVE_TABLE_VISUALLY_CHECKED',
            'NSA facsimile/page/hash drift')
    require(nsa['readout'] == {
        'mission': '7153', 'payload': '698 BK IV', 'vehicle': '2313',
        'launch_vehicle': 'Thor-Agena D', 'date_as_printed': '16 Jan 63'},
        'NSA readout changed')
    require(nro['title'] == 'The SIGINT Satellite Story' and nro['authored_year'] == 1994
            and nro['release_date'] is None
            and nro['url'] == 'https://www.governmentattic.org/19docs/NRO-SIGINTsatStory_1994u.pdf'
            and nro['bytes'] == 14454222
            and nro['sha256'] == '1bffa3e121073c8a312c9f67393efac09aa0a322e18ce039e592df0454e13c8a'
            and nro['pdf_pages'] == 430 and nro['pdf_page_1_based'] == 123
            and nro['printed_page'] == 90
            and nro['class'] == 'RETROSPECTIVE_MISSION_HISTORY_VISUALLY_CHECKED',
            'NRO facsimile/page/hash drift')
    require(nro['readout'] == {
        'mission': '7153', 'vehicle': '2313',
        'date_as_printed': '16 January 1963',
        'launch_vehicle_wording': 'using a Thor',
        'mission_duration_wording': 'only two days due to a battery failure',
        'next_vehicle': '2314',
        'next_booster_wording': 'launched on 29 June 1963 using a TAT booster'},
        'NRO readout changed')
    require(m['conflict'] == {
        'nsa_1975_vehicle_2313': 'Agena D',
        'nasa_1964_launch_group_1963_3': 'Agena D (C241-L15, not object-specific)',
        'quest_1995_2313': 'Agena D (C241-L50, editorial)',
        'modern_gunter_2313': 'Agena B (secondary catalog)',
        'nro_1994_2313': 'Thor only; no Agena variant given on inspected page',
        'result': 'UNRESOLVED_HARDWARE_VARIANT',
        'same_observation_family_claim': False}, 'B/D independence conflict drift')
    require(m['norad528']['catalog_identifier'].startswith('1963-003B/NORAD 528')
            and all(m['norad528'][k] is None for k in (
                'hardware_identity', 'observation_utc', 'station', 'frame',
                'sigma', 'decay_hour', 'impact_location')), 'unobserved 528 must be null')
    require(parent['schema'] == 'conde.quest-stage-scientific-bridge/v1'
            and parent['id'] == 'ABELHA-C241-L50-01'
            and parent['source_occurrences'] == ['C241-L50', 'C241-L15', 'C241-L48', 'C241-L40']
            and parent['independence']['nro_pdf_verified'] is False
            and parent['physical_domain_effect'] == 'THETA_UNCHANGED'
            and parent['activation'] is False
            and parent['new_528_instrumental_observations'] == 0
            and len(parent['simulator_latent_parameters']) == 8,
            'parent scope/provenance changed')
    require(all(p['value'] is None and p['activation'] is False
                for p in parent['simulator_latent_parameters']), 'parent activated latents')
    require(parent_revalidated is True, 'parent must be independently reproduced')

    def edge(a, b, relation):
        return {'from': a, 'to': b, 'relation': relation,
                'independent_instrumental_observation': False, 'activation': False}

    edges = [
        edge('C241-L51', 'DOC:NSA-BYE-19385-75', 'VERIFIED_FACSIMILE_SHA256'),
        edge('C241-L51', 'DOC:NRO-SIGINT-STORY-1994', 'VERIFIED_FACSIMILE_SHA256'),
        edge('DOC:NSA-BYE-19385-75', 'ROW:NSA:p132:APPENDIX-A:p5', 'VISUALLY_READ_1975_TABLE'),
        edge('ROW:NSA:p132:APPENDIX-A:p5', 'VEHICLE:2313', 'MISSION_7153_LAUNCH_LABEL_D'),
        edge('DOC:NRO-SIGINT-STORY-1994', 'TEXT:NRO:p123:print90', 'VISUALLY_READ_1994_NARRATIVE'),
        edge('TEXT:NRO:p123:print90', 'VEHICLE:2313', 'THOR_MISSION_7153_NO_AGENA_VARIANT'),
        edge('TEXT:NRO:p123:print90', 'H:7153_BATTERY_FAILURE', 'TWO_DAY_OPERATION_NOT_REENTRY'),
        edge('C241-L50', 'VEHICLE:2313', 'EARLIER_QUEST1995_LABEL_D'),
        edge('C241-L15', 'LAUNCH:1963-003', 'NASA1964_GROUP_LABEL_D_NOT_PIECE'),
        edge('C241-L40', 'VEHICLE:2313', 'MODERN_GCAT_LABEL_B'),
        edge('C241-L48', 'DOC:NRO-SIGINT-STORY-1994', 'PREVIOUS_TEXT_ONLY_NOW_FACSIMILE_AUDITED'),
        edge('VEHICLE:2313', 'H:2313_B_OR_D', 'CONFLICT_UNRESOLVED'),
        edge('LAUNCH:1963-003', 'NORAD:528/1963-003B', 'GROUP_ASSOCIATION_NOT_PIECE_IDENTITY'),
        edge('NORAD:528/1963-003B', 'H:528_PIECE_IDENTITY', 'ENGINEERING_IDENTITY_UNVERIFIED'),
        edge('H:2313_B_OR_D', 'LATENT:2313:stage', 'ENGINEERING_VARIANT_REQUIRED'),
        edge('H:528_PIECE_IDENTITY', 'LATENT:528:hardware', 'DEBRIS_PIECE_MAPPING_REQUIRED'),
        edge('DOC:NRO-SIGINT-STORY-1994', 'LATENT:528:tracking_utc', 'NO_528_OBSERVATION'),
    ]
    return {
        'schema': 'conde.declassified-2313-scientific-bridge/v1',
        'id': 'ABELHA-C241-L51-01',
        'source_occurrences': ['C241-L51', 'C241-L50', 'C241-L15', 'C241-L48', 'C241-L40'],
        'related_matrix_occurrence': 'C197#1',
        'matrix_relationship': 'NASA_DECAY_CONTEXT_NOT_PIECE_IDENTITY_OR_MASS',
        'input_sha256': dict(PINS),
        'parent_bridge': {'id': parent['id'], 'sha256': PINS[PARENT],
                          'status_at_publication': 'NRO_TEXT_ONLY_IN_L48',
                          'new_status': 'NRO_1994_FACSIMILE_VERIFIED_IN_L51',
                          'does_not_modify_parent_evidence': True},
        'facsimiles': [{
            'id': d['id'], 'source_url': d['url'], 'document_year': d['authored_year'],
            'release_date': d['release_date'], 'pdf_sha256': d['sha256'],
            'pdf_bytes': d['bytes'], 'pdf_pages': d['pdf_pages'],
            'physical_pdf_page': d['pdf_page_1_based'],
            'printed_page': d['printed_page'], 'printed_section': d['printed_page_section'],
            'hash_scope': 'FULL_PDF_BYTES_NOT_PAGE_IMAGE',
            'documentary_class': d['class'], 'observation_of_norad_528': False,
        } for d in (nsa, nro)],
        'independence': {
            'facsimiles_count': 2,
            'historical_measurements_added': 0,
            'editorial_agreement_proves_instrumental_independence': False,
            'documentary_genealogy_independence': None,
            'the_1994_nro_page_labels_agena_variant': False,
            'nro_battery_failure_is_reentry_epoch': False,
        },
        'dependency_graph': edges,
        'hypotheses': [
            {'id': 'H:2313_B_OR_D', 'status': 'OPEN_ENGINEERING_PROOF_MISSING'},
            {'id': 'H:528_PIECE_IDENTITY', 'status': 'OPEN_PHYSICAL_MAPPING_MISSING'},
            {'id': 'H:7153_BATTERY_FAILURE', 'status': 'DOCUMENTED_MISSION_END_NOT_ORBITAL_DECAY'},
            {'id': 'H:528_OBSERVABLES', 'status': 'OPEN_SPADATS_SAO_PRIMARY_LOGS_MISSING'},
        ],
        'lean_candidate': 'Conde1963.stage2313RequiresEngineeringIdentity',
        'lean_status': 'DOCUMENTARY_CANDIDATE_NOT_COMPILED_ORBITAL_PROOF',
        'simulator_latent_parameters': parent['simulator_latent_parameters'],
        'instrumental_epoch_utc': None,
        'instrumental_station': None,
        'instrumental_frame': None,
        'instrumental_covariance': None,
        'new_528_instrumental_observations': 0,
        'activation': False,
        'physical_domain_effect': 'THETA_UNCHANGED',
        'next_test': 'Original 1963 engineering identification for Agena 2313 and NORAD 528 piece-specific SPADATS/SAO observation with UTC, station, reference frame and covariance.',
    }


def render(root=ROOT):
    data = sources(root)
    require(previous.render(root) == (root / PARENT).read_bytes(),
            'parent bridge does not reproduce independently')
    return (json.dumps(build(data), ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()


def main():
    ap = argparse.ArgumentParser()
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument('--write-site', action='store_true')
    modes.add_argument('--check-site', action='store_true')
    args = ap.parse_args()
    payload = render()
    if args.write_site:
        OUT.write_bytes(payload)
    elif args.check_site:
        require(OUT.read_bytes() == payload, 'exported bytes diverge')
    else:
        print(payload.decode(), end='')


if __name__ == '__main__':
    main()
