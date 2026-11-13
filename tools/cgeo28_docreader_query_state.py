"""CGEO-28: distinguish DocReader query pre-fill from a verified catalogue hit.

Replay exact, small DOM excerpts extracted from the real SGB response bodies.
Original whole HTML is not redistributed; SHA-256/byte counts support optional
live-file replay. GET URLs are not evidence of search results.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/geo/cgeo28_docreader_query_state.json'
PRIOR = ROOT / 'research/geo/cgeo27_sgb_official_aerial_access.json'
RAW_NAMES = {'Esplanada': 'Esplanada.html', '53 D': '53_20D.html', 'MI 1850': 'MI_201850.html'}


class ReaderDOM(HTMLParser):
    def __init__(self):
        super().__init__()
        self.term = None
        self.folder_title = None
        self.folder_text = ''
        self.folder_pages = ''
        self._target = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'input' and d.get('name') == 'PesquisarTxt':
            self.term = d.get('value')
        if tag == 'span' and d.get('id') == 'PastaTxt':
            self.folder_title = d.get('title')
            self._target = 'folder'
        if tag == 'span' and d.get('id') == 'PagTotalLbl':
            self._target = 'pages'

    def handle_data(self, data):
        if self._target == 'folder':
            self.folder_text += data
        if self._target == 'pages':
            self.folder_pages += data

    def handle_endtag(self, tag):
        if tag == 'span':
            self._target = None


def inspect(source: bytes) -> ReaderDOM:
    parser = ReaderDOM()
    parser.feed(source.decode('utf-8-sig', errors='replace'))
    return parser


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def validate(record: dict, prior: dict, excerpts: dict[str, bytes]) -> str:
    if record['id'] != 'CGEO-28' or prior['id'] != 'CGEO-27':
        raise ValueError('unexpected provenance identifiers')
    if record['municipality'] != prior['municipality']:
        raise ValueError('municipality changed')
    if record['conclusion'] != 'URL_QUERY_PREPOPULATES_INPUT_NO_VERIFIED_SEARCH_EXECUTION':
        raise ValueError('unverified search was promoted')
    if record['catalogue_result_status'] != 'UNKNOWN_NOT_SEARCHED_OR_UNVERIFIED':
        raise ValueError('search-result absence/presence cannot be concluded')
    if record['target_record_found'] is not None or record['target_record_absent'] is not None:
        raise ValueError('no record-level result was obtained')
    if set(excerpts) != set(RAW_NAMES) or len(record['observations']) != 3:
        raise ValueError('incomplete actual response excerpts')
    if len({o['sha256'] for o in record['observations']}) != 3:
        raise ValueError('response identities collapsed')
    for o in record['observations']:
        if o['query'] not in RAW_NAMES or o['http_status'] != 200:
            raise ValueError('unexpected query or transport')
        if o['url'] != ('https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=CPRM&pesq=' + o['query'].replace(' ', '%20')):
            raise ValueError('query endpoint changed')
        if o['search_executed_confirmed'] is not False:
            raise ValueError('GET alone does not verify a search')
        source = excerpts[o['query']]
        if hashlib.sha256(source).hexdigest() != o['excerpt_sha256']:
            raise ValueError('actual DOM excerpt changed')
        parsed = inspect(source)
        if parsed.term != o['query'] or parsed.folder_text.strip() != record['shared_active_folder']:
            raise ValueError('GET query did not share the first-folder state')
        if parsed.folder_title != record['shared_active_folder'] or parsed.folder_pages.strip() != record['shared_folder_pages']:
            raise ValueError('unexpected folder/page provenance')
        if not (o['sha256'] and o['bytes'] > len(source)):
            raise ValueError('invalid source acquisition metadata')
    post = record['postback_attempt']
    if (post['http_status'], post['method'], post['term'], post['active_folder_unchanged'],
        post['search_execution_confirmed'], post['search_results_extracted']) != (200,'POST','Esplanada',True,False,False):
        raise ValueError('POST attempt overinterpreted')
    if post['bytes'] < 1000 or len(post['sha256']) != 64:
        raise ValueError('POST custody invalid')
    limits = record['scientific_limits']
    for key in ('project_53d_mi1850_inventory_hit','historical_center_geometry','event_position_1963','horizontal_error_m'):
        if limits[key] is not None:
            raise ValueError('premature GIS/catalogue inference')
    for key in ('aerial_frame_acquired','photo_index_acquired','date_of_individual_capture_verified','can_constrain_orbital_reentry'):
        if limits[key] is not False:
            raise ValueError('unverified material promoted')
    if {x['to'] for x in record['graph_edges']} != {'CGEO-27','CGEO-26','CGEO-18'}:
        raise ValueError('cumulative linkage broken')
    return 'READER_GET_QUERY_IS_NOT_PROOF_OF_EXECUTED_SEARCH'


def verify_full(record: dict, whole: dict[str, bytes], post: bytes) -> str:
    if set(whole) != set(RAW_NAMES):
        raise ValueError('missing original whole response')
    for o in record['observations']:
        b = whole[o['query']]
        if len(b) != o['bytes'] or hashlib.sha256(b).hexdigest() != o['sha256']:
            raise ValueError('full source bytes do not match documented acquisition')
        parsed = inspect(b)
        if parsed.term != o['query'] or parsed.folder_text.strip() != record['shared_active_folder']:
            raise ValueError('full response differs from archived excerpt')
    p = record['postback_attempt']
    if len(post) != p['bytes'] or hashlib.sha256(post).hexdigest() != p['sha256']:
        raise ValueError('POST body mismatch')
    if inspect(post).folder_text.strip() != record['shared_active_folder']:
        raise ValueError('POST initial folder mismatch')
    return 'FOUR_REAL_HTTP_BODIES_REPLAY_PASS'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, help='optional directory of 3 GET and 1 POST HTML bodies acquired on 2026-11-13')
    args = parser.parse_args()
    record = load(MANIFEST)
    excerpts = {o['query']:(ROOT/o['excerpt']).read_bytes() for o in record['observations']}
    print(validate(record, load(PRIOR), excerpts))
    if args.source_dir:
        whole = {term:(args.source_dir/fn).read_bytes() for term,fn in RAW_NAMES.items()}
        post = (args.source_dir/'Esplanada_POST.html').read_bytes()
        print(verify_full(record, whole, post))


if __name__ == '__main__':
    main()
