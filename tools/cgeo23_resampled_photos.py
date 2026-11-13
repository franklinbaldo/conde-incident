"""CGEO-23: compare genuine 2012 and 2014 photo files, with optional Pillow replay."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'research/geo/cgeo23_resampled_photo_lineage.json'
PARENTS = {
    'blogger': ROOT / 'research/geo/cgeo19_1959_editorial_photographs.json',
    'wordpress': ROOT / 'research/geo/cgeo14_vila_conde_visual_catalogue.json',
}
ORIGINALS = {'vila': 0, 'passarela': 1, 'alto': 2, 'igreja': 3}
THUMBNAILS = {'wp2': 1, 'wp3': 2}
MATCHES = {'wp2': 'igreja', 'wp3': 'alto'}


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding='utf-8'))


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def validate_contract(contract: dict) -> None:
    if (contract.get('schema'), contract.get('id')) != ('conde.gis.resampled-photo-lineage/v1', 'CGEO-23'):
        raise ValueError('CGEO-23 schema identity lost')
    c19 = json.loads(PARENTS['blogger'].read_text(encoding='utf-8'))
    c14 = json.loads(PARENTS['wordpress'].read_text(encoding='utf-8'))
    for key, i in ORIGINALS.items():
        child = contract['sources']['blogger'][key]
        parent = c19['images'][i]
        if (child['parent_id'], child['sha256'], child['byte_size'], child['url']) != (
            parent['id'], parent['sha256'], parent['byte_size'], parent['source_url']):
            raise ValueError('CGEO-19 source identity drift: ' + key)
    for key, i in THUMBNAILS.items():
        child = contract['sources']['wordpress'][key]
        parent = c14['images'][i]
        if (child['parent_id'], child['sha256'], child['byte_size'], child['url']) != (
            parent['id'], parent['sha256'], parent['byte_size'], parent['url']):
            raise ValueError('CGEO-14 source identity drift: ' + key)
    result = contract['result']
    if result['match_ids'] != MATCHES or result['method'] != 'Pillow_13.0.0_RGB_LANCZOS_gray_Pearson':
        raise ValueError('method or pair mapping drift')
    for key, expected in MATCHES.items():
        row = result['comparison_matrix'][key]
        if set(row) != set(ORIGINALS):
            raise ValueError('negative control removed')
        if not (row[expected]['mae_rgb'] < 4 and row[expected]['gray_pearson'] > 0.995):
            raise ValueError('matching score invalid')
        if not all(row[k]['mae_rgb'] > 40 and row[k]['gray_pearson'] < 0.7 for k in ORIGINALS if k != expected):
            raise ValueError('confusing negative control')
        if row[expected]['mae_rgb'] != min(r['mae_rgb'] for r in row.values()):
            raise ValueError('best-match label wrong')
    for field in ('exposure_date_1959_authenticated', 'original_negative_verified',
                  'same_originating_frame_proven_without_resampling_assumptions',
                  'direction_of_copying_verified', 'original_photographer_verified',
                  'two_independent_historical_witnesses', 'rights_to_redistribute_verified'):
        if result[field] is not False:
            raise ValueError('unsupported lineage promotion: ' + field)
    geo = contract['geospatial']
    if geo['can_constrain_orbital_reentry'] is not False:
        raise ValueError('unfounded orbital constraint')
    for field in ('center_1963_point', 'center_1963_polygon', 'impact_point',
                  'historic_camera_location', 'crs', 'horizontal_error_m'):
        if geo[field] is not None:
            raise ValueError('unfounded location: ' + field)


def gray_pearson(first, second) -> float:
    # These are small, 320 x 233 thumbnails. Deliberately no NumPy dependency.
    a = list(first.convert('L').get_flattened_data())
    b = list(second.convert('L').get_flattened_data())
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((v - ma)**2 for v in a)
    vb = sum((v - mb)**2 for v in b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def replay(blogger_dir: Path, wp2: Path, wp3: Path, contract: dict) -> dict:
    try:
        from PIL import Image, ImageChops, ImageStat, __version__
    except ImportError as exc:
        raise RuntimeError('Pillow==13.0.0 required for image replay') from exc
    if __version__ != '13.0.0':
        raise ValueError('Pillow version drift')
    sources = {}
    for name, idx in ORIGINALS.items():
        sources[name] = blogger_dir / f'img{idx+1}.jpg'
    thumbs = {'wp2': wp2, 'wp3': wp3}
    for group, paths in (('blogger', sources), ('wordpress', thumbs)):
        for name, path in paths.items():
            b = path.read_bytes()
            stored = contract['sources'][group][name]
            if (len(b), digest(b)) != (stored['byte_size'], stored['sha256']):
                raise ValueError('real JPEG hash mismatch: ' + group + '/' + name)
    matrix = {}
    for wname, wpath in thumbs.items():
        with Image.open(wpath) as obj:
            thumb = obj.convert('RGB')
        matrix[wname] = {}
        for bname, bpath in sources.items():
            with Image.open(bpath) as obj:
                resized = obj.convert('RGB').resize(thumb.size, Image.Resampling.LANCZOS)
            stat = ImageStat.Stat(ImageChops.difference(resized, thumb))
            mae = sum(stat.mean) / 3
            correlation = gray_pearson(resized, thumb)
            recorded = contract['result']['comparison_matrix'][wname][bname]
            if abs(mae - recorded['mae_rgb']) > 0.06 or abs(correlation - recorded['gray_pearson']) > 0.00005:
                raise ValueError('metric mismatch: ' + wname + '/' + bname)
            matrix[wname][bname] = {'mae_rgb': round(mae, 3), 'gray_pearson': round(correlation, 6)}
    validate_contract(contract)
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser(description='CGEO-23: pinned JPEGs, RGB resampling, and negative controls')
    parser.add_argument('--blogger-dir', type=Path)
    parser.add_argument('--wp2', type=Path)
    parser.add_argument('--wp3', type=Path)
    args = parser.parse_args()
    c = load_contract()
    validate_contract(c)
    if any((args.blogger_dir, args.wp2, args.wp3)):
        if not all((args.blogger_dir, args.wp2, args.wp3)):
            parser.error('must supply all six real JPEGs, never partial source coverage')
        matrix = replay(args.blogger_dir, args.wp2, args.wp3, c)
        print(json.dumps({'status': 'REAL_JPEG_PIXELS_PASS', 'matrix': matrix}, ensure_ascii=False))
    else:
        print('CGEO-23 OFFLINE_CONTRACT_PASS (NOT a real-JPEG replay)')


if __name__ == '__main__':
    main()
