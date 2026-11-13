"""Validate SGB institutional photogrammetry access without inferring 1961 coverage.

Only a 205-byte verbatim excerpt of the actual form is checked in; whole
source bytes are identified by their acquisition SHA-256 but not redistributed.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
C26 = ROOT / 'research/geo/cgeo26_pet53d_1961_aerial_locator.json'
C27 = ROOT / 'research/geo/cgeo27_sgb_official_aerial_access.json'
EXCERPT = ROOT / 'research/geo/evidence/cgeo27_sgb_collection_options.txt'
SEARCH_URL = 'https://acervo.sgb.gov.br/docreader/Pesquisa/acervo_digital.html'
READER_URL = 'https://acervo.sgb.gov.br/docreader/DocReader.aspx'
ALIASES = {'CPRM': 'Fotos Aéreas CPRM', 'DNPM bk': 'Fotos Aéreas DNPM',
           'FotoDNPM': 'Fotoíndices DNPM', 'FotoUSAF': 'Fotoíndices USAF'}


class OptionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.options = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'option':
            self.current = dict(attrs).get('value')

    def handle_data(self, data):
        if self.current is not None and data.strip():
            self.options[self.current] = data.strip()
            self.current = None

    def handle_endtag(self, tag):
        if tag == 'option':
            self.current = None


def parse_options(source):
    parser = OptionParser()
    parser.feed(source)
    return parser.options


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def check(record, prior, source_excerpt):
    assert record['id'] == 'CGEO-27' and prior['id'] == 'CGEO-26'
    if record['municipality'] != prior['municipality']:
        raise ValueError('municipal crosswalk changed')
    entry = prior['catalogue_occurrence']['observed_entry']
    target = record['target_archival_request']
    if (target['project'], target['nominal_year'], target['sheet_mi'],
        target['sheet_cim']) != (entry['project'].split(' - Projeto ')[-1],
                                entry['project_nominal_year'], entry['sheet_mi'],
                                entry['sheet_cim']):
        raise ValueError('source lead differs from CGEO-26')
    if target['existing_origin_grade'] != prior['catalogue_occurrence']['source_grade']:
        raise ValueError('original catalogue unverified')
    if target['search_result_status'] != 'NOT_VERIFIED_IN_OFFICIAL_CATALOGUE':
        raise ValueError('the SGB search form is not a photo catalogue hit')
    snapshots = record['official_source_snapshots']
    if len(snapshots) != 4 or snapshots[0]['url'] != SEARCH_URL:
        raise ValueError('institutional source manifest changed')
    if snapshots[0]['http_status'] != 200 or snapshots[0]['acquired_bytes'] != 5816:
        raise ValueError('unconfirmed source acquisition')
    if snapshots[0]['sha256'] != 'e09f4503966cb335920fb6c92d6fed2aea00bf2d304cb675e55c6f870f1d6c3e':
        raise ValueError('original search page acquisition SHA changed')
    if hashlib.sha256(source_excerpt).hexdigest() != snapshots[0]['excerpt_sha256']:
        raise ValueError('acquired source excerpt changed')
    if any(s['body_archived_in_project'] for s in snapshots):
        raise ValueError('body was not stored in this project')
    if parse_options(source_excerpt.decode('utf-8')) != ALIASES:
        raise ValueError('official collection aliases differ from excerpt')
    expected = [{'label': ''.join(ch for ch in unicodedata.normalize('NFKD', v) if not unicodedata.combining(ch)), 'alias': k}
                for k, v in ALIASES.items()]
    if record['institutional_inventory']['online_collection_options'] != expected:
        raise ValueError('manifest does not match official source excerpts')
    for name in ('project_53d_entry_found_in_official_online_search_results',
                 'online_photo_index_exists_for_mi1850_proven',
                 'institutional_possession_of_exact_1961_items_verified'):
        if record['institutional_inventory'][name] is not None:
            raise ValueError('unverified archival result claimed')
    if record['institutional_inventory']['archivists_contacted']:
        raise ValueError('no outreach was authorized or performed')
    if record['institutional_inventory']['official_web_form_verified'] is not True:
        raise ValueError('observed real HTML form not properly identified')
    limits = record['scientific_limits']
    if any(limits[k] for k in ('project_nominal_year_is_individual_frame_date',
                              'catalogue_sheet_implies_full_photo_coverage',
                              'official_search_form_proves_target_file_exists',
                              'official_search_form_proves_target_file_is_accessible_online',
                              'catalogue_original_pdf_acquired',
                              'photo_index_original_acquired',
                              'aerial_frames_original_acquired',
                              'pre_1963_individual_frame_confirmed',
                              'can_constrain_orbital_reentry')):
        raise ValueError('premature archival/temporal/orbital promotion')
    if any(limits[k] is not None for k in ('center_polygon_1963','fall_point_1963','horizontal_error_m')):
        raise ValueError('geography cannot yet be constrained')
    if {e['to'] for e in record['graph_edges']} != {'CGEO-26','CGEO-24','CGEO-17','CGEO-18'}:
        raise ValueError('cumulative evidence lineage broken')
    return 'OFFICIAL_INSTITUTIONAL_ACCESS_VERIFIED_NO_53D_RESULT'


def query_url(alias, term):
    if alias not in ALIASES:
        raise ValueError('unverified archive alias')
    return READER_URL + '?' + urlencode({'bib': alias, 'pesq': term})


def verify_full_source(source):
    """Verify independently obtained bytes without interpreting search results."""
    expected = load(C27)['official_source_snapshots'][0]
    if len(source) != expected['acquired_bytes'] or hashlib.sha256(source).hexdigest() != expected['sha256']:
        raise ValueError('full official source bytes do not match acquisition')
    observed = parse_options(source.decode('utf-8-sig'))
    if any(observed.get(k) != v for k, v in ALIASES.items()):
        raise ValueError('official collection aliases are incomplete')
    return 'ORIGINAL_WEB_FORM_BYTES_REPLAY_PASS'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-body', type=Path, help='actual full HTML obtained from official page')
    ap.add_argument('--live', action='store_true', help='fetch official form and report whether it matches the archived acquisition')
    args = ap.parse_args()
    print(check(load(C27), load(C26), EXCERPT.read_bytes()))
    if args.source_body:
        print(verify_full_source(args.source_body.read_bytes()))
    if args.live:
        with urlopen(SEARCH_URL, timeout=15) as response:
            raw = response.read(100000)
        print(verify_full_source(raw))
    print('Candidate online lookup (not a confirmed hit):', query_url('CPRM','Esplanada 1850'))


if __name__ == '__main__':
    main()
