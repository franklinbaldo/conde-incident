"""CGEO-35: source-native image pixel inspection without geodetic promotion."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from tools.cgeo34_uwm_jp2 import ROOT, MANIFEST as PARENT, read, verify_original

MANIFEST = ROOT / 'research/geo/cgeo35_uwm_jp2_raster_anchors.json'
EXPECTED_SHA = 'a42b07caee45dd378a319de770d5d4dcf5a386b279874d64812710daf8329243'
EXPECTED_ORIGINAL_SHA = '6637246d2a68a2e7024e07829caa35a8af0a707905e6c606109f1da52ae808b3'


def verify_contract(d: dict, parent: dict) -> str:
    view = d['inspection']
    pixels = d['image_space_only']
    lim = d['scientific_limits']
    if (d['id'], d['parent_id'], d['schema']) != (
        'CGEO-35', 'CGEO-34', 'conde.gis.jp2-native-raster-inspection/v1'):
        raise ValueError('wrong record identity')
    if (d['source_jp2_sha256'] != parent['asset']['sha256'] or
        d['source_jp2_sha256'] != EXPECTED_ORIGINAL_SHA or
        d['raster_native_size_px'] != [parent['asset']['width_px'],parent['asset']['height_px']] or
        d['source_same_sheet_as_parent'] is not True or
        d['source_url'] != parent['asset']['catalog']):
        raise ValueError('broken original source chain')
    if view['decoder'] != 'Pillow 13.0.0 / OpenJPEG' or view['reduction_levels'] != 1:
        raise ValueError('different decoding contract')
    if (view['original_pixel_roi_xyxy'], view['decoded_pixel_roi_xyxy'],
        view['decoded_size_px'], view['crop_size_px'], view['rgb_pixel_sha256']) != (
        [4250,5200,5000,5670], [2125,2600,2500,2835], [4802,3892],
        [375,235], EXPECTED_SHA):
        raise ValueError('ROI or original pixel digest changed')
    if view['source_preview_committed_to_git'] is not False:
        raise ValueError('unlicensed derivative distribution')
    if d['literal_visible_toponyms'] != ['CONDE','Vila Velha','Itapicuru']:
        raise ValueError('unreviewed toponyms')
    if (pixels['conde_label_and_settlement_symbol_original_px_roi'],
        pixels['conde_symbol_original_px_visual_estimate'],
        pixels['visual_estimate_tolerance_px'],
        pixels['vila_velha_label_original_px_roi']) != (
        [4390,5380,4590,5470],[4465,5413],20,[4380,5310,4510,5380]):
        raise ValueError('unreviewed feature pixel bounds')
    hx = d['historical_context']
    if (hx['printed_base_edition_year'],hx['roads_update_year'],hx['scale_denominator'],
        hx['new_independent_historical_witness']) != (1954,1961,500000,False):
        raise ValueError('anachronistic dating or false independence')
    if {(e['to'],e['kind']) for e in d['graph_edges']} != {
        ('CGEO-34','DERIVED_RASTER_VIEW_SAME_AUTHENTICATED_JP2'),
        ('CGEO-20','TWO_NAMED_LOCALITIES_NEED_TEMPORAL_GEOMETRIC_BRIDGE'),
        ('CGEO-18','NO_BRIDGE_TO_TRANSLATED_REPORT_OF_CITY_CENTER')}:
        raise ValueError('incorrect evidence lineage')
    for k in ('historical_city_center_polygon_1963','municipal_boundary_1963',
              'original_map_geodetic_datum','control_points_with_error',
              'center_world_coordinates','observed_reentry_location',
              'ground_position_uncertainty_m','map_pixel_to_world_transform'):
        if lim.get(k,'MISSING') is not None:
            raise ValueError('unjustified physical coordinates: '+k)
    if any(lim.get(k) is not False for k in (
            'can_constrain_orbital_reentry','supports_independent_historical_observation')):
        raise ValueError('false science promotion')
    if d['epistemic_status'] != 'AUTHENTICATED_DIGITAL_SURROGATE_RASTER_INSPECTED_AT_REDUCED_RESOLUTION_NO_SPATIAL_CALIBRATION':
        raise ValueError('unreviewed epistemic status')
    return 'CGEO35_CONTRACT_PASS'


def verify_raster(path: Path, d: dict, parent: dict) -> str:
    # The full bitstream must match the archived original before decoding.
    h = bytes.fromhex((ROOT / parent['asset']['header_fixture']).read_text('ascii'))
    verify_original(path, parent, h)
    try:
        import PIL
        from PIL import Image
    except ImportError as e:
        raise RuntimeError('Install Pillow==13.0.0 for real JP2 decode') from e
    if PIL.__version__ != '13.0.0':
        raise ValueError('decoder version changed')
    with Image.open(path) as im:
        if im.format != 'JPEG2000' or im.mode != 'RGB' or list(im.size) != d['raster_native_size_px']:
            raise ValueError('not the expected 3-channel original JP2')
        im.reduce = d['inspection']['reduction_levels']
        im.load()
        if list(im.size) != d['inspection']['decoded_size_px']:
            raise ValueError('unexpected reduced image size')
        crop = im.crop(tuple(d['inspection']['decoded_pixel_roi_xyxy']))
        if list(crop.size) != d['inspection']['crop_size_px']:
            raise ValueError('wrong crop dimensions')
        if hashlib.sha256(crop.tobytes()).hexdigest() != d['inspection']['rgb_pixel_sha256']:
            raise ValueError('original JP2 RGB pixels diverge from reviewed crop')
    return 'CGEO35_NATIVE_JP2_CROP_REPLAY_PASS'


def main() -> None:
    args = argparse.ArgumentParser()
    args.add_argument('--original', type=Path)
    parsed = args.parse_args()
    d, parent = read(MANIFEST), read(PARENT)
    print(verify_contract(d,parent))
    if parsed.original:
        print(verify_raster(parsed.original,d,parent))

if __name__ == '__main__':
    main()
