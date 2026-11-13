"""CGEO-29: replay a real SGB USAF photoindex tree node, not a frame."""
from __future__ import annotations

import argparse
import hashlib
from html import unescape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/geo/cgeo29_usaf_63_32_photoindex_node.json'
C26 = ROOT / 'research/geo/cgeo26_pet53d_1961_aerial_locator.json'
C27 = ROOT / 'research/geo/cgeo27_sgb_official_aerial_access.json'
NODE = ROOT / 'research/geo/evidence/cgeo29_usaf_1850_node.html'
EXPECTED_LABEL = '1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI'


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def labels_from_full_html(raw: bytes) -> list[str]:
    page = raw.decode('utf-8', errors='replace')
    begin = page.find('<div id="T1"')
    if begin < 0:
        raise ValueError('official tree T1 missing')
    end = page.find('id="T1_ClientState"', begin)
    if end < 0:
        raise ValueError('tree terminator missing')
    tree = page[begin:end]
    return [unescape(s).strip() for s in re.findall(
        r'<span class="rtIn">(.*?)</span>', tree, flags=re.DOTALL)]


def validate(record: dict, c26: dict, c27: dict, excerpt: bytes) -> str:
    if (record['id'], c26['id'], c27['id']) != ('CGEO-29', 'CGEO-26', 'CGEO-27'):
        raise ValueError('wrong crosswalk history')
    if record['municipality'] != c26['municipality'] or record['municipality'] != c27['municipality']:
        raise ValueError('municipality mismatch')
    source = record['official_reader']
    if (source['url'], source['collection_alias'], source['http_status']) != (
        'https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF', 'FotoUSAF', 200):
        raise ValueError('unexpected institutional source')
    if (source['node_label_exact'], source['rendered_tree_node_count'],
        source['node_ordinal_0_based']) != (EXPECTED_LABEL, 1809, 679):
        raise ValueError('tree navigation details changed')
    if hashlib.sha256(excerpt).hexdigest() != source['node_excerpt_sha256']:
        raise ValueError('source-derived tree node excerpt was modified')
    if source['node_excerpt'] != str(NODE.relative_to(ROOT)):
        raise ValueError('excerpt path changed')
    if re.findall(r'<span class="rtIn">([^<]+)</span>', excerpt.decode()) != [EXPECTED_LABEL]:
        raise ValueError('unmatched literal tree node')
    if len(source['sha256']) != 64 or source['acquired_bytes'] != 585747:
        raise ValueError('original response custodian record invalid')
    if source['node_click_or_selection_verified'] is not False or source['actual_photoindex_page_bytes_acquired'] is not False:
        raise ValueError('tree node is not an inspected photoindex page')
    if source['node_is_a_record_level_finding'] is not True:
        raise ValueError('verified node occurrence lost')
    sheet = c26['catalogue_occurrence']['observed_entry']
    cross = record['crosswalk']
    if (cross['sheet_mi'], cross['cgeo26_cim_normalized'],
        cross['usaf_cim_literal'], sheet['sheet_mi'], sheet['sheet_cim']) != (
        1850, 'SC-24-Z-C-VI', 'SC.24-Z-C-VI', 1850, 'SC-24-Z-C-VI'):
        raise ValueError('wrong MI or CIM match')
    if cross['other_project'] != 'PETROBRAS 53 D' or cross['usaf_project_literal'] != 'USAF 63-32':
        raise ValueError('distinct projects were merged')
    if any(cross[k] is not None for k in (
        'same_aerial_flight_or_photoindex_as_pet53d', 'same_observational_lineage', 'index_file_is_pre_incident')):
        raise ValueError('unverified identity, independence or date promoted')
    if cross['printed_project_code_is_a_capture_date'] is not False:
        raise ValueError('63-32 is a project code, not verified exposure date')
    options = {x['alias'] for x in c27['institutional_inventory']['online_collection_options']}
    if source['collection_alias'] not in options:
        raise ValueError('not a declared official collection')
    if record['evidence_state'] != 'OFFICIAL_USAF_PHOTOINDEX_TREE_NODE_VERIFIED_NO_IMAGE_ACQUIRED':
        raise ValueError('evidence maturity overstated')
    if set(record['claims_not_established'].values()) != {True}:
        raise ValueError('negative/positive capture claims unauthorized')
    limits = record['scientific_limits']
    for key in ('historical_center_geometry', 'event_position_1963', 'horizontal_error_m'):
        if limits[key] is not None:
            raise ValueError('unjustified spatial estimate')
    for key in ('original_photoindex_image_acquired', 'individual_aerial_frame_acquired',
                'date_of_individual_capture_verified', 'can_constrain_orbital_reentry'):
        if limits[key] is not False:
            raise ValueError('unacquired imagery was promoted')
    if {edge['to'] for edge in record['graph_edges']} != {
        'CGEO-24', 'CGEO-26', 'CGEO-27', 'CGEO-28', 'CGEO-18'}:
        raise ValueError('cumulative provenance edges lost')
    return 'OFFICIAL_USAF_63_32_MI1850_TREE_NODE_REPLAY_PASS'


def verify_full_html(record: dict, body: bytes) -> str:
    src = record['official_reader']
    if len(body) != src['acquired_bytes'] or hashlib.sha256(body).hexdigest() != src['sha256']:
        raise ValueError('full original HTML source hash/size differs')
    labels = labels_from_full_html(body)
    if len(labels) != src['rendered_tree_node_count']:
        raise ValueError('full tree node count does not match')
    if labels[src['node_ordinal_0_based']] != src['node_label_exact']:
        raise ValueError('target tree node index and label mismatch')
    if labels.count(EXPECTED_LABEL) != 1:
        raise ValueError('target node not unique')
    return 'FULL_ORIGINAL_OFFICIAL_HTML_REPLAY_PASS'


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument('--source-html', type=Path, help='original 585747-byte reader GET, optional')
    args = cli.parse_args()
    record = load(MANIFEST)
    print(validate(record, load(C26), load(C27), NODE.read_bytes()))
    if args.source_html:
        print(verify_full_html(record, args.source_html.read_bytes()))


if __name__ == '__main__':
    main()
