#!/usr/bin/env python3
"""CGEO-50: qualify broad NARA catalog matches, never infer a spot/can."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'research/geo/cgeo50_nara_locator_search.json'
PARENT = ROOT / 'research/geo/cgeo49_nara_header_crosssheet.json'
TERMS = {'125374': 'm1765-317-00248.jpg', '125370': 'm1765-317-00247.jpg', '133002': 'm1765-317-00249.jpg'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate(d, parent):
    require((d.get('schema'), d.get('id'), d.get('parent_evidence')) == (
        'conde.cgeo.nara-locator-search/v1', 'CGEO-50', ['CGEO-47','CGEO-48','CGEO-49']), 'lineage/schema')
    require((d.get('nara_file_unit'), d.get('degree_square'), d.get('record_group'),
             d.get('series_id'), d.get('microfilm'), d.get('microfilm_roll')) == (
        '46716637', '11S037W', '373', '306062', 'M1765', '317'), 'archival hierarchy')
    require(parent['id'] == 'CGEO-49' and parent['nara_unit'] == d['nara_file_unit'], 'parent unit')
    header_by_sheet = {s['filename']: s for s in parent['sheets']}
    require(d['candidate_overlay'] == TERMS['125374'] and
            d['candidate_handwritten_number'] == header_by_sheet[TERMS['125374']]['handwritten_number'], 'overlay/number')
    require(d['number_printed_field'] == 'O.P. FILE NO.', 'printed field')
    require(d['candidate_exposure_labels'] == ['26','16'], 'exposure labels')
    require(d['candidate_spot_number'] is None and d['candidate_original_negative_can'] is None, 'invented locator')
    require('not an exhaustive negative search' in d['catalog_query_scope'], 'unwarranted completeness claim')
    require(len(d['catalog_searches']) == 3, 'search cardinality')
    require({s['term'] for s in d['catalog_searches']} == set(TERMS), 'terms')
    for s in d['catalog_searches']:
        require(s['url'] == 'https://catalog.archives.gov/proxy/records/search?limit=10&page=1&q=' + s['term'], 'query not replayable')
        require(s['http_status'] == 200 and s['response_bytes'] > 10000 and s['hits_total'] > 10, 'catalog response')
        require(len(s['response_sha256']) == 64 and all(c in '0123456789abcdef' for c in s['response_sha256']), 'unverified hash')
        require(s['first_result_title'] and s['matched_1942_negative_confirmed'] is False, 'false hit')
        require(header_by_sheet[TERMS[s['term']]]['handwritten_number'] == s['term'], 'term not in source')
    require(d['primary_research_guides'] == [
        'https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography',
        'https://unwritten-record.blogs.archives.gov/2019/09/11/researching-foreign-aerial-photography/'], 'missing authority')
    require(d['can_locator_available_on_open_web'] is False and
            d['can_locator_request_channel'] == 'carto@nara.gov' and
            d['archivist_contact_sent'] is False and
            d['can_locator_crosswalk_confirmed'] is False, 'unverified archivist action')
    limits = d['limitations']
    require(limits['public_search_proves_absence_of_negative'] is False and
            limits['film_can_recovered'] is False and
            limits['geometry_georeferenced'] is False and
            limits['orbital_constraints_activated'] is False, 'premature inference')
    for key in ('exposure_date_at_conde_verified', 'conde_urban_center_1963', 'event_location'):
        require(limits[key] is None, 'historical date/geometry promoted')
    require(limits['final_status'] == 'PUBLIC_CATALOG_AMBIGUOUS_ARCHIVIST_LOOKUP_REQUIRED', 'state')
    return len(d['catalog_searches'])


def live_query(d):
    # A live query verifies the endpoint/shape, not mutable counts or 14-Nov hashes.
    checked = 0
    for s in d['catalog_searches']:
        req = Request(s['url'], headers={'User-Agent': 'Conde-CGEO50/1.0'})
        with urlopen(req, timeout=35) as response:
            require(response.status == 200, 'catalog HTTP failure')
            payload = response.read()
        obj = json.loads(payload)['body']['hits']
        require('total' in obj and isinstance(obj.get('hits'), list), 'catalog response shape drift')
        require(obj['total']['value'] >= 1, 'search not returned')
        checked += 1
    return checked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--live', action='store_true')
    args = ap.parse_args()
    d = load(DATA)
    print('CGEO50_CATALOG_AMBIGUITY_PASS', validate(d, load(PARENT)))
    if args.live:
        print('CGEO50_LIVE_SEARCH_PASS', live_query(d))

if __name__ == '__main__':
    main()
