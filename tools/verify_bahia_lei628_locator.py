#!/usr/bin/env python3
"""Fail closed on historical-law search index vs official facsimile, no network."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlsplit

MANIFEST = Path(__file__).resolve().parents[1] / 'research/archive/bahia_lei628_1953_locator_20261113.json'
STATUS = 'UNDETERMINED_PENDING_ORIGINAL_ANNEXES_AND_INTERVENING_ACTS'


def validate(data: dict) -> list[str]:
    errors = []
    if data.get('schema') != 'conde.bahia-lei628-index-locator/v1':
        errors.append('unknown schema')
    if data.get('record_id') != 'BA-LEI628-1953-INDEX-20261113':
        errors.append('law record identity changed')
    ident = data.get('legal_identity') or {}
    if (ident.get('act') != 'Lei estadual 628' or ident.get('act_date') != '1953-12-30'
            or ident.get('target_municipality') != 'Conde, Bahia'
            or ident.get('target_date') != '1963-11-08'):
        errors.append('law or municipality identity changed')
    if ident.get('administrative_table_period_in_indexed_art_1') != ['1954-01-01', '1958-12-31']:
        errors.append('indexed administrative period mismatch')
    if (ident.get('article_1_mentions_annex') != 'quadro I'
            or ident.get('article_2_mentions_annexes') != ['II', 'III', 'IV', 'V', 'VI']):
        errors.append('indexed annex locator mismatch')
    loc = data.get('locator') or {}
    u = urlsplit(str(loc.get('url', '')))
    if (u.scheme != 'https' or u.netloc != 'leisestaduais.com.br'
            or '/lei-ordinaria-n-628-1953-bahia-' not in u.path):
        errors.append('non-matching source URL')
    if (loc.get('type') != 'THIRD_PARTY_SEARCH_INDEX_SNIPPET'
            or loc.get('search_indexed') is not True
            or loc.get('direct_open') != 'HTTP_403'):
        errors.append('search result improperly promoted to retrieved source')
    for field in ('direct_original_text_inspected', 'annexes_retrieved',
                  'official_1953_1954_facsimile_retrieved', 'full_original_text_verified'):
        if loc.get(field) is not False:
            errors.append('unverified source promoted: ' + field)
    if any(loc.get(field) is not None for field in ('pdf_bytes', 'pdf_sha256', 'printed_page')):
        errors.append('fabricated original PDF metadata')
    official = data.get('official_repository_locator') or {}
    if (official.get('url') != 'https://www.ba.gov.br/casacivil/43/legislacao'
            or official.get('law_specific_original_found_there') is not False):
        errors.append('generic institutional portal confused with law facsimile')
    interp = data.get('interpretation') or {}
    if (interp.get('legal_status_on_target_date') != STATUS
            or interp.get('indexed_law_caption_not_original_fascimile') is not True):
        errors.append('unverified historical legal boundary determination')
    for field in ('caption_period_end_proves_1963_limits_expired',
                  'law_1953_alone_proves_boundary_on_target_date',
                  '2017_boundary_retrojected_to_1963',
                  'new_geographic_coordinates', 'new_orbital_constraint'):
        if interp.get(field) is not False:
            errors.append('false physical or historical inference: ' + field)
    if not data.get('outstanding') or not data.get('prior_source_chain'):
        errors.append('missing scientific dependency/next legal search')
    return errors


if __name__ == '__main__':
    errors = validate(json.loads(MANIFEST.read_text(encoding='utf-8')))
    if errors:
        raise SystemExit('\n'.join(errors))
    print('BAHIA_1953_LAW_INDEX_ONLY_OK')
