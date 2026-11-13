#!/usr/bin/env python3
"""Verify byte custody and temporal non-retroprojection of a 2017 SEI map."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MANIFEST = (Path(__file__).resolve().parents[1] /
            'research/archive/conde_sei_2017_map_custody_20261113.json')
ORIGINAL = ('https://ftp.sei.ba.gov.br/Geoinformacao/mapas/munic/'
            'vigente/mapa_com_descritivo_atual_2908606.pdf')
POINTS = tuple(f'P{n:02d}' for n in range(1, 17))


def validate(document: dict) -> list[str]:
    """Validate exact source, historical layers, and scientific limits offline."""
    errors = []
    if document.get('schema') != 'conde.sei-map-custody/v1':
        errors.append('schema')
    if document.get('document_id') != 'CGEO-SEI-MAP-2017-01':
        errors.append('document ID')
    if document.get('ibge_code') != '2908606' or document.get('municipality') != 'Conde, Bahia':
        errors.append('municipality')
    if document.get('original_url') != ORIGINAL:
        errors.append('original URL')
    if document.get('document_preparation') != '2017-08':
        errors.append('editorial date')
    if document.get('administrative_division_version') != '2017-06-14':
        errors.append('map version')
    law = document.get('legal_basis') or {}
    if law.get('law') != 'BA 13.720' or law.get('date') != '2017-04-27':
        errors.append('law and date')
    mapinfo = document.get('cartography') or {}
    for key, expected in {'scale': '1:100000', 'projection': 'UTM',
                          'datum': 'SIRGAS2000', 'utm_zone': '24S', 'pdf_pages': 1}.items():
        if mapinfo.get(key) != expected:
            errors.append('cartography ' + key)
    layers = document.get('source_layers') or []
    if (len(layers) != 4 or sorted(x.get('year') for x in layers) != [1973,2007,2007,2010]):
        errors.append('source layers and dates')
    context = document.get('government_context_2013') or {}
    if (context.get('url') != 'https://www.ba.gov.br/seplan/noticias/sei-lanca-canal-de-informacoes-sobre-limites-intermunicipais'
            or context.get('publication_date') != '2013-06-26'
            or context.get('proves_no_intervening_specific_acts') is not False):
        errors.append('2013 official context temporal scope')
    retr = document.get('retrieval') or {}
    if retr.get('date_utc') != '2026-11-13':
        errors.append('retrieval date')
    if retr.get('bytes') != 1105817:
        errors.append('payload bytes')
    if retr.get('sha256') != '8a04fcd2ee0f57dc753de621e7c076f18f4756a8a3398ef8f7877bd4bcfcb61b':
        errors.append('pinned SHA-256')
    if retr.get('pdf_magic') is not True or retr.get('pdf_eof') is not True:
        errors.append('PDF structure')
    if retr.get('visual_inspection') != 'PAGE_1_INSPECTED':
        errors.append('inspection scope')
    if retr.get('wayback_url') is not None:
        errors.append('invented Wayback')
    points = document.get('boundary_points_2017') or []
    if len(points) != 16 or tuple(p.get('id') for p in points) != POINTS:
        errors.append('16 sequenced 2017 points')
    if any(not isinstance(p.get('description'), str) or len(p['description']) < 12 for p in points):
        errors.append('point description')
    assert_year = document.get('epistemology') or {}
    for key in ('2017_map_is_an_independent_1963_survey',
                '2007_2010_2017_source_layers_are_1963_observations',
                '1963_legal_boundary_demonstrated',
                'orbital_constraint_activated',
                'precise_1963_coordinates_established'):
        if assert_year.get(key) is not False:
            errors.append('forbidden retroprojection ' + key)
    if assert_year.get('publisher_original_pdf_inspected') is not True:
        errors.append('custody status')
    if '628/1953' not in assert_year.get('unresolved',''):
        errors.append('unresolved legal source')
    if 'CGEO-06' not in document.get('connections', []):
        errors.append('lineage to 2017 law')
    return errors


def verify_bytes(payload: bytes, document: dict) -> list[str]:
    """Verify independently downloaded PDF bytes, without decoding map coordinates."""
    saved = document['retrieval']
    problems = []
    if len(payload) != saved['bytes']:
        problems.append('PDF byte length mismatch')
    if hashlib.sha256(payload).hexdigest() != saved['sha256']:
        problems.append('PDF SHA-256 mismatch')
    if not payload.startswith(b'%PDF-'):
        problems.append('missing PDF header')
    if b'%%EOF' not in payload[-1024:]:
        problems.append('missing PDF end marker')
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--pdf', type=Path, help='optional local PDF replay, without storing PDF in Git')
    args = parser.parse_args()
    doc = json.loads(args.manifest.read_text(encoding='utf-8'))
    errors = validate(doc)
    if args.pdf:
        errors.extend(verify_bytes(args.pdf.read_bytes(), doc))
    if errors:
        for error in errors:
            print('FAIL:', error)
        return 1
    print('PASS: 2017 SEI map provenance and temporal barrier' +
          (' + PDF byte replay' if args.pdf else ' (PDF byte replay NOT_RUN)'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
