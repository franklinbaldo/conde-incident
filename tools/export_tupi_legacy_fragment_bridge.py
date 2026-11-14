#!/usr/bin/env python3
"""C02 FBIS and the verified Última Hora page, as a nonphysical graph.

A wording coincidence is a research question, not evidence of transmission.
Sources are checked against the frozen matrix and canonical documentary feed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import export_documentary_dependence as documentary
import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('public/data/conde-tupi-legacy-fragment-bridge.json')
EDITORIAL = Path('research/editorial/tupi_fragmentos_20261113.md')
LINEAGES = Path('research/provenance/lineages.json')
PARENT = Path('public/data/conde-declared-dependence.json')
LOCATOR = Path('research/archive/ultima_hora_pe_00471_1963_locator_20261113.json')
VERIFIED = Path('research/editorial/ultima_hora_00471_original_verificado_20261114.md')
VERIFIED_SHA256 = '781a53a4a1051c2af9d4260581c4ce72931898b6dab5cbdad8dc11dca8893426'
PDF_SHA256 = 'e121d6ea9784bcb77a02e1a6e3c453f23987103940f5993190237c45499a95ec'
PDF_URL = 'https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf'
PDF_NODE = 'DOC-UH-PE-1963-00471-PDF-20261114'
LOCATOR_SHA256 = 'cf761332644243ec2943d4fd299d292408176c9a1dd5125295a63d16a8ab41a8'
EDITORIAL_SHA256 = '9ab9ecb181bbe262e5696bed8fcf48ab4258a400fc1345bf94380c93f9f589eb'
FBIS = 'FBIS_EOP_UAP_D001'
TUPI = 'RADIO_TUPI_19631108'
UH = 'UH_NORDESTE_1963_00471_P8_LEGACY_READING'


def require(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError('Tupi lineage: ' + label)


def encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def build(parent: dict, lineage: dict, editorial_bytes: bytes, parent_sha256: str,
          locator_bytes: bytes, verified_bytes: bytes) -> dict:
    require(hashlib.sha256(editorial_bytes).hexdigest() == EDITORIAL_SHA256,
            'editorial snapshot changed; re-audit source before updating pin')
    require(hashlib.sha256(locator_bytes).hexdigest() == LOCATOR_SHA256,
            'newspaper locator bytes changed; independently re-audit')
    require(hashlib.sha256(verified_bytes).hexdigest() == VERIFIED_SHA256,
            'newspaper facsimile verification ledger changed; re-audit before repinning')
    verified_text = verified_bytes.decode('utf-8')
    require(PDF_URL in verified_text and PDF_SHA256 in verified_text
            and '4.337.426 bytes' in verified_text
            and '8 páginas' in verified_text
            and 'num buraco de quatro metros de profundidade' in verified_text
            and 'página digital 8' in verified_text
            and 'GET HTTPS reproduzido em 14/11/2026' in verified_text
            and 'não demonstrada' in verified_text,
            'newspaper ledger identity, page, custody or inference limit changed')
    locator = json.loads(locator_bytes)
    require(locator['id'] == 'DOC-UH-PE-1963-00471-LOCATOR'
            and locator['edition'] == '00471'
            and locator['catalog_identifier'] == '765147'
            and locator['docreader_selected_edition'] == '00471'
            and locator['docreader_first_physical_id'] == 5339
            and locator['docreader_last_physical_id'] == 5346
            and locator['docreader_requested_page8_candidate_id'] == 5346
            and locator['docreader_requested_page8_candidate_url']
                == 'https://memoria.bn.gov.br/DocReader/765147/5346'
            and locator['catalog_url']
                == 'https://memoria.bn.gov.br/DocReader/765147/5339'
            and locator['earlier_catalog_selected_edition'] == '00507'
            and locator['earlier_catalog_url']
                == 'https://memoria.bn.gov.br/DocReader/765147/5756'
            and locator['pdf_head_status'] == 403
            and locator['pdf_sha256'] is None
            and locator['page_image_sha256'] is None
            and locator['original_text_verified'] is False
            and locator['page_8_inspected'] is False
            and locator['four_metre_hole_verified'] is False
            and locator['docreader_page8_raster_retrieved'] is False
            and locator['docreader_physical_ids_are_not_printed_pages'] is True,
            'newspaper locator edition, page or custody state changed')
    require(parent['matrix_git_blob_sha1'] == pg.MATRIX_BLOB_SHA,
            'different frozen matrix')
    citations = parent['citation_lineages']
    checked = []
    for occ in ('C01#1', 'C02#1', 'C03#1'):
        matches = [x for x in citations if x['snapshot_ref'] == pg.matrix_ref(occ)]
        require(len(matches) == 1 and matches[0]['source_id'] == FBIS
                and matches[0]['family_id'] == 'RADIO_TUPI_FBIS',
                'FBIS source identity or occurrence reassigned: ' + occ)
        x = matches[0]
        require(x['independent_physical_observation_count'] is None
                and any(p['upstream_source_id'] == TUPI
                        and p['edges'][-1]['kind'] == 'transcribes'
                        for p in x['declared_upstream_paths']),
                'transcription lineage or independence changed: ' + occ)
        rows = pg.matrix_occurrences((ROOT / pg.MATRIX.relative_to(ROOT)).read_bytes())
        row = next((r for r in rows if r['snapshot_ref'] == x['snapshot_ref']), None)
        require(row is not None and x['matrix_line'] == row['matrix_line']
                and x['row_sha256'] == row['row_sha256'],
                'matrix row identity differs: ' + occ)
        checked.append({
            'occurrence_ref': x['snapshot_ref'],
            'source_id': FBIS, 'source_family': 'RADIO_TUPI_FBIS',
            'matrix_line': x['matrix_line'], 'row_sha256': x['row_sha256'],
            'upstream_source_id': TUPI,
            'report_status': 'FACSIMILE_OF_SECONDHAND_BROADCAST_REPORT',
            'physical_observation': False,
        })
    sources = {x['id']: x for x in lineage['sources']}
    require(sources[FBIS]['family'] == sources[TUPI]['family'] == 'RADIO_TUPI_FBIS'
            and sources[TUPI]['url'] is None
            and sources[TUPI]['status'] == 'ORIGINAL_AUDIO_NOT_RECOVERED',
            'origin/broadcast status falsely promoted')
    require('**“Buraco de quatro metros de profundidade”**' in editorial_bytes.decode()
            and 'H0 coincidência; H1 fórmula jornalística comum; H2 contaminação; H3 montagem sem prova'
                in editorial_bytes.decode()
            and 'HTTP 403' in editorial_bytes.decode(),
            'editorial source and competing hypotheses no longer match')
    return {
        'schema': 'conde.tupi-legacy-fragment-bridge/v1',
        'inputs': [
            {'path': str(PARENT), 'sha256': parent_sha256, 'identity': 'CANONICAL_FROZEN_MATRIX_CITATIONS'},
            {'path': str(LINEAGES), 'identity': 'DECLARED_DOCUMENTARY_DEPENDENCE'},
            {'path': str(EDITORIAL), 'sha256': EDITORIAL_SHA256,
             'identity': 'EDITORIAL_INTERPRETATION_NOT_PRIMARY_FACSIMILE'},
            {'path': str(LOCATOR), 'sha256': LOCATOR_SHA256,
             'identity': 'FBN_DOCREADER_EDITION_LOCATOR_NOT_PAGE_FACSIMILE'},
            {'path': str(VERIFIED), 'sha256': VERIFIED_SHA256,
             'identity': 'ORIGINAL_NEWSPAPER_FACSIMILE_VERIFIED_LEDGER_NOT_TUPI_AUDIO'},
        ],
        'documentary_occurrences': checked,
        'comparison': {
            'id': 'FOUR_METRE_WORDING_TUPI_VS_UH00471',
            'tupi_occurrence_ref': pg.matrix_ref('C02#1'),
            'tupi_source_id': FBIS,
            'tupi_claim': 'REPORT_OF_FOUR_METRE_DEEP_HOLE_NOT_VERIFIED_IMPACT',
            'tupi_broadcast_header_literal': '2330 8 NOV 63 W',
            'tupi_broadcast_epoch_utc': None,
            'tupi_time_zone_interpretation': None,
            'other_source_id': UH,
            'other_source_family': 'ULTIMA_HORA_NORDESTE_NEWSPAPER',
            'other_source_url': locator['catalog_url'],
            'other_locator': 'Última Hora Nordeste, edição 00471; IDs DocReader '
                             '5339–5346 não equivalem a paginação impressa; '
                             'PDF original tem página digital 8 verificada',
            'other_document_locator_id': locator['id'],
            'other_page8_candidate_url': locator['docreader_requested_page8_candidate_url'],
            'other_page8_raster_retrieved': locator['docreader_page8_raster_retrieved'],
            'other_printed_page8_inspected': locator['page_8_inspected'],
            'other_verified_digital_page8_inspected': True,
            'other_pdf_page_count_verified': 8,
            'other_pdf_get_status_verified': 200,
            'other_pdf_get_date_verified': '2026-11-14',
            'other_pdf_bytes_verified': 4337426,
            'other_original_facsimile_node': PDF_NODE,
            'other_pdf_url': locator['pdf_exact_url'],
            'other_pdf_head_status': locator['pdf_head_status'],
            'earlier_wrong_docreader_url': locator['earlier_catalog_url'],
            'earlier_wrong_docreader_edition': locator['earlier_catalog_selected_edition'],
            'other_matrix_occurrence_ref': None,
            'other_original_pdf_sha256': PDF_SHA256,
            'other_reported_claim': 'FOUR_METRE_HOLE_IN_DISTINCT_STOLEN_STATUES_NEWS',
            'other_evidence_status': 'ORIGINAL_PDF_PAGE8_TEXT_VERIFIED_NO_PHYSICAL_EVENT',
            'other_previous_403_status': 'HISTORICAL_ACCESS_FAILURE_NOT_CURRENT_CUSTODY',
            'direct_textual_dependency': None,
            'independent_witness_count': None,
            'chronological_priority_proven': False,
            'interpretation': 'COINCIDENT_WORDING_NOT_A_SHARED_PHYSICAL_EVENT',
        },
        'hypotheses': [
            {'id': 'H0_COINCIDENCE', 'status': 'OPEN_UNWEIGHTED'},
            {'id': 'H1_SHARED_JOURNALISTIC_FORMULA', 'status': 'OPEN_UNWEIGHTED'},
            {'id': 'H2_TEXTUAL_CONTAMINATION', 'status': 'OPEN_UNWEIGHTED'},
            {'id': 'H3_FABRICATION', 'status': 'OPEN_UNWEIGHTED'},
        ],
        'candidate': {
            'id': 'TUPI_1963_NARRATIVE_TRANSMISSION_PATH',
            'observable': 'four_metre_claim_present_in_1963_newspaper_and_FBISED_TUPI',
            'inference_operator': 'TEXTUAL_LINEAGE_COMPARISON_PENDING_TUPI_ORIGINAL_AND_CHRONOLOGY',
            'missing_conditions': [
                'original_portuguese_tupi_audio_or_transcript_for_literal_comparison',
                'broadcast_audio_or_script_and_source_chain',
                'edition_print_and_broadcast_time_zones_with_provenance',
                'textual_direction_and_independence_test',
            ],
            'lean_predicate': 'UNFORMALIZED_TEXTUAL_HYPOTHESIS_NOT_PHYSICAL_PREMISE',
            'lean_status': 'CANDIDATE_NOT_PROMOTED',
            'simulator_parameter': 'narrative_transmission_path_not_orbital_state',
            'simulator_value': None,
            'activation': False,
            'physical_domain_effect': 'THETA_UNCHANGED',
        },
        'graph_edges': [
            {'from': TUPI, 'to': FBIS, 'kind': 'TRANSCRIBED_BY'},
            {'from': FBIS, 'to': pg.matrix_ref('C02#1'), 'kind': 'REPORTS_NOT_OBSERVES'},
            {'from': locator['id'], 'to': PDF_NODE,
             'kind': 'EDITION_LOCATOR_LINKED_TO_VERIFIED_ORIGINAL_PDF'},
            {'from': PDF_NODE, 'to': UH, 'kind': 'PAGE8_PRINTED_CLAIM_VERIFIED'},
            {'from': UH, 'to': 'FOUR_METRE_WORDING_TUPI_VS_UH00471',
             'kind': 'CONTEMPORARY_TEXT_COMPARISON_NO_SHARED_EVENT'},
            {'from': pg.matrix_ref('C02#1'), 'to': 'FOUR_METRE_WORDING_TUPI_VS_UH00471',
             'kind': 'WORDING_COMPARISON_NOT_DEPENDENCY_PROOF'},
            {'from': 'FOUR_METRE_WORDING_TUPI_VS_UH00471', 'to': 'TUPI_1963_NARRATIVE_TRANSMISSION_PATH',
             'kind': 'PENDING_TEXTUAL_INFERENCE'},
        ],
        'delta_links': 7,
        'delta_physical_domain': 'NONE',
        'independent_528_physical_observation_count': None,
    }


def from_repo(root: Path = ROOT) -> dict:
    raw = (root / PARENT).read_bytes()
    # Rebuild the parent independently, rather than trusting a stale site file.
    require(raw == encoded(documentary.build(root)), 'stale or altered parent graph')
    return build(json.loads(raw), json.loads((root / LINEAGES).read_text()),
                 (root / EDITORIAL).read_bytes(), hashlib.sha256(raw).hexdigest(),
                 (root / LOCATOR).read_bytes(), (root / VERIFIED).read_bytes())


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument('--check-site', action='store_true')
    args = cli.parse_args()
    expected = encoded(from_repo())
    target = ROOT / OUTPUT
    if args.check_site:
        require(target.read_bytes() == expected, 'site output differs from audited source')
    else:
        target.write_bytes(expected)
    print('Tupi legacy fragment graph OK:', len(expected), 'bytes')


if __name__ == '__main__':
    main()
