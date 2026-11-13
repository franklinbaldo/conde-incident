"""Audit modern independent catalog labels, never reconstruct 1963 station metadata."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / 'research/meteorology/recife_wmoid_catalogues_1963_bridge.json'
EXCERPT = ROOT / 'research/meteorology/recife_wmoid_catalogue_excerpts.txt'
SOURCES = {
    'ceda': {
        'url': 'https://artefacts.ceda.ac.uk/badc_datadocs/radiosglobe/southamerica.html',
        'sha256': 'dc8354d3f2d012838e26c6f80b68849fa784ad917732e816ab86fc54ffa03a29',
        'bytes': 6302,
    },
    'sgb': {
        'url': 'https://rigeo.sgb.gov.br/items/1f0cc1e9-5f8b-4c8b-b816-a88a2665b854',
        'sha256': '8a310e76a75b74267c74e934742585e9363f930b2278d3a2df45db86d419ae6a',
        'bytes': 464477,
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract(source: str, data: bytes) -> str:
    text = data.decode('utf-8')
    if source == 'ceda':
        matches = [x for x in text.splitlines() if re.match(r'^82900\s+Recife/Curado\b', x)]
        if len(matches) != 1:
            raise ValueError('CEDA Recife/Curado 82900 absent or duplicated')
        return matches[0]
    if source == 'sgb':
        titles = re.findall(r'<title>(.*?)</title>', text, re.I | re.S)
        if len(titles) != 1:
            raise ValueError('SGB title absent or duplicated')
        title = html.unescape(titles[0]).strip()
        if not re.search(r'estação pluviográfica Aeroporto de Recife, código 82899$', title):
            raise ValueError('SGB code/site label changed')
        return title
    raise ValueError(source)


def make_excerpt(ceda: str, sgb: str) -> bytes:
    return ('CEDA\t' + ceda + '\nSGB\t' + sgb + '\n').encode('utf-8')


def check(manifest: dict, excerpt: bytes) -> None:
    if manifest['schema'] != 'conde.recife-wmoid-catalogue-crosscheck/v1':
        raise ValueError('schema')
    if sha(excerpt) != manifest['excerpt_sha256']:
        raise ValueError('excerpt SHA mismatch')
    lines = excerpt.decode('utf-8').splitlines()
    if len(lines) != 2 or not lines[0].startswith('CEDA\t') or not lines[1].startswith('SGB\t'):
        raise ValueError('snapshot shape')
    if not re.match(r'^CEDA\t82900\s+Recife/Curado\b', lines[0]):
        raise ValueError('CEDA station mismatch')
    if 'Aeroporto de Recife, código 82899' not in lines[1]:
        raise ValueError('SGB station mismatch')
    records = manifest['catalogue_records']
    if [r['wmo_id'] for r in records] != [82900, 82899]:
        raise ValueError('WMO IDs wrongly merged')
    if {r['source_key'] for r in records} != {'ceda', 'sgb'}:
        raise ValueError('source ancestry')
    for r in records:
        if r['catalogue_label'] not in excerpt.decode('utf-8'):
            raise ValueError('catalogue label not in excerpt')
        if r['physical_measurement_1963'] or r['independent_igra_sounding']:
            raise ValueError('retroprojection/source independence')
    for k in ('historical_1963_instrument', 'historical_1963_launch_coordinates',
              'historical_1963_gph_method', 'historical_1963_sensor_covariance',
              'recife_to_conde_transfer_error', 'new_drag_constraint'):
        if manifest['physical_1963'][k] is not None:
            raise ValueError('unverified 1963 parameter promoted')
    if manifest['status'] != 'CONNECTED_PENDING_CALIBRATION':
        raise ValueError('unsupported promotion')
    if manifest['sources'] != SOURCES:
        raise ValueError('unpinned source')
    if len(manifest['edges']) < 3:
        raise ValueError('missing cumulative linkage')


def fetch(url: str) -> bytes:
    with urlopen(Request(url, headers={'User-Agent': 'Conde-1963-meteorology-audit/1.0'}), timeout=30) as f:
        return f.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', required=True)
    parser.add_argument('--download', action='store_true', help='verify live source excerpt against committed snapshot')
    args = parser.parse_args()
    manifest = json.loads(ARTIFACT.read_text(encoding='utf-8'))
    excerpt = EXCERPT.read_bytes()
    check(manifest, excerpt)
    if args.download:
        current = {k: fetch(v['url']) for k, v in SOURCES.items()}
        lines = {k: extract(k, b) for k, b in current.items()}
        if make_excerpt(lines['ceda'], lines['sgb']) != excerpt:
            raise ValueError('live source wording differs from committed excerpt')
        for k, data in current.items():
            print(k, 'bytes', len(data), 'SHA256', sha(data),
                  'matches_original_snapshot', sha(data) == SOURCES[k]['sha256'])
    print('PASS: labels 82899/82900 distinct; 1963 calibration PENDING')


if __name__ == '__main__':
    main()
