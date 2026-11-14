#!/usr/bin/env python3
"""Fail-closed custody of NARA RG373 M1765 overlay JPEGs, not air-photo negatives."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'research/geo/cgeo47_nara_m1765_conde_pre1963.json'
EXPECTED = {
    '11S037W': ('46716637', '1942-1943', 6),
    '11S038W': ('46716645', '1942-1945', 8),
}
NARA_PREFIX = 'https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/'


def require(value, message):
    if not value:
        raise ValueError(message)


def load_manifest(path=MANIFEST):
    return json.loads(Path(path).read_text())


def validate(manifest):
    require(manifest.get('id') == 'CGEO-47', 'wrong science ID')
    require(manifest.get('schema') == 'conde.cgeo.nara-m1765-pre1963/v1', 'wrong schema')
    require(manifest['lineage'] == {'prior': 'CGEO-46', 'related_sgb': 'CGEO-45', 'same_flight_as_sgb': None}, 'false source linkage')
    units = manifest['units']
    require(len(units) == 2, 'expected two archived degree squares')
    require({u['degree_square'] for u in units} == set(EXPECTED), 'missing or duplicate degree square')
    ids, urls = set(), set()
    for unit in units:
        square = unit['degree_square']
        record_id, cover, count = EXPECTED[square]
        require(unit['nara_id'] == record_id, 'wrong NARA file unit')
        require(unit['title'] == 'Overlay indexes for degree square ' + square, 'wrong title')
        require((unit['microform'], unit['roll'], unit['record_group'], unit['series_id']) == ('M1765','317','373','306062'), 'wrong archive hierarchy')
        require(unit['cover_period_printed'] == cover, 'wrong period')
        require(unit['catalog_query_url'] == 'https://catalog.archives.gov/proxy/records/search?limit=10&page=1&q=' + square, 'wrong catalog query')
        require(unit['catalog_response_bytes'] > 1000 and re.fullmatch('[0-9a-f]{64}', unit['catalog_response_sha256']), 'invalid catalog response custody')
        images = unit['images']
        require(len(images) == count, 'unexpected count of genuine images')
        for index, obj in enumerate(images):
            fname = f'm1765-317-{245+index if square=="11S037W" else 251+index:05d}.jpg'
            require(obj['filename'] == fname, 'unexpected or missing microfilm scan')
            require(obj['url'].startswith(NARA_PREFIX) and obj['url'].endswith('/'+fname), 'untrusted object URL')
            require(str(obj['object_id']).isdigit() and obj['object_id'] not in ids, 'reused object ID')
            require(obj['url'] not in urls, 'reused source URL')
            ids.add(obj['object_id']); urls.add(obj['url'])
            require(100_000 <= obj['bytes'] <= 20_000_000, 'unreasonable byte count')
            require(re.fullmatch('[0-9a-f]{64}', obj['sha256']), 'missing full SHA-256')
            role = ('index_cover' if index==0 else 'geographic_base_map' if index==1 else 'flight_overlay')
            require(obj['role'] == role, 'misclassified scan')
    interpretation = manifest['direct_visual_inspection']
    require(interpretation['11S037W_base_map'] == 'm1765-317-00246.jpg', 'lost Conde base map reference')
    require(interpretation['conde_label_visible_on_base_map'] is True, 'lost independently inspected toponym')
    require(interpretation['index_overlays_are_flight_diagrams_not_aerial_photographs'] is True, 'overlays misrepresented as photos')
    limits = manifest['limitations']
    require(limits['units_in_catalog_verified'] is True and limits['all_listed_geographic_jpegs_custodied'] is True, 'custody state conflict')
    for key in ('individual_original_negatives_acquired', 'georeferenced_footprints_validated', 'photograph_of_conde_town_acquired', 'orbital_constraints_activated'):
        require(limits[key] is False, 'premature scientific promotion: ' + key)
    for key in ('town_center_geometry_1963', 'event_reentry_location'):
        require(limits[key] is None, 'invented historical location: ' + key)
    return len(ids)


def get_bytes(url):
    req = Request(url, headers={'User-Agent': 'Conde-GEO/CGEO47 provenance-check', 'Accept': 'application/json, image/jpeg'})
    with urlopen(req, timeout=35) as resp:
        require(resp.status == 200, 'HTTP not 200')
        return resp.read()


def verify_catalog(manifest):
    for unit in manifest['units']:
        body = json.loads(get_bytes(unit['catalog_query_url']))['body']['hits']
        require(body['total']['value'] >= 1, 'no catalog hits')
        hits = [h for h in body['hits'] if h.get('_id') == unit['nara_id']]
        require(len(hits) == 1, 'wrong catalog match')
        r = hits[0]['_source']['record']
        require(r['title'] == unit['title'], 'catalog title drift')
        require(any(a.get('recordGroupNumber') == 373 for a in r['ancestors']), 'not in record group 373')
        require(any(a.get('naId') == 306062 for a in r['ancestors']), 'wrong RG373 series')
        require(any(x['identifier'] == 'M1765' for x in r['microformPublications']), 'wrong microfilm')
        expected = {x['objectId']: x for x in r['digitalObjects'] if x['objectFilename'] != 'how-to-read-an-overlay.jpg'}
        require(len(expected) == len(unit['images']), 'NARA scan set drift')
        for image in unit['images']:
            x = expected.get(image['object_id'])
            require(x is not None and (x['objectUrl'], x['objectFilename'], x['objectFileSize']) == (image['url'],image['filename'],image['bytes']), 'NARA object metadata drift')
    return 'CGEO47_LIVE_CATALOG_PASS'


def verify_images(manifest, selected=None, cached_directory=None):
    checked = 0
    for unit in manifest['units']:
        for image in unit['images']:
            if selected and image['filename'] not in selected:
                continue
            if cached_directory:
                b = (Path(cached_directory) / (unit['degree_square'] + '_' + image['filename'])).read_bytes()
            else:
                b = get_bytes(image['url'])
            require(b.startswith(b'\xff\xd8\xff') and b.endswith(b'\xff\xd9'), 'not complete JPEG')
            require(len(b) == image['bytes'], 'JPEG size drift')
            require(hashlib.sha256(b).hexdigest() == image['sha256'], 'JPEG SHA256 drift')
            checked += 1
    require(checked == (len(selected) if selected else 14), 'not all intended images checked')
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Re-fetch both NARA catalogs and all 14 original JPEGs')
    parser.add_argument('--cached-directory', help='Verify already acquired original NARA JPEGs')
    a = parser.parse_args()
    manifest = load_manifest()
    print('CGEO47_MANIFEST_PASS',validate(manifest))
    if a.live:
        print(verify_catalog(manifest))
        print('CGEO47_LIVE_IMAGES_PASS',verify_images(manifest))
    if a.cached_directory:
        print('CGEO47_CACHED_IMAGES_PASS',verify_images(manifest,cached_directory=a.cached_directory))


if __name__ == '__main__':
    main()
