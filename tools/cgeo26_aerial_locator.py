"""CGEO-26: validate archival lead without mistaking a sheet index for a frame."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C26 = ROOT / 'research/geo/cgeo26_pet53d_1961_aerial_locator.json'
C24 = ROOT / 'research/geo/cgeo24_esplanada_sheet_index.json'
C25 = ROOT / 'research/geo/cgeo25_esplanada_edition_lineage.json'
MIRRORS = (
    'https://it.scribd.com/doc/190899422/acervo-foto-pdf',
    'https://pt.scribd.com/doc/50811476/acervo-foto',
    'https://www.yumpu.com/pt/document/view/8190809/acervo-fotografico-multimeios-cprm',
)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check(record, sheet, edition):
    require(record['id'] == 'CGEO-26' and record['schema'] == 'conde.gis.historical-aerial-archive-locator/v1', 'contract')
    require(record['municipality'] == {'name': 'Conde', 'state': 'BA', 'ibge_code': 2908606}, 'municipality')
    cat = record['catalogue_occurrence']
    require(cat['catalogue_date'] == '2003-06', 'date of source catalogue')
    require(cat['source_grade'] == 'SECONDARY_WEB_TRANSCRIPTION_OF_UNACQUIRED_CATALOGUE', 'source grade')
    require(tuple(cat['web_mirrors']) == MIRRORS and cat['mirror_pages_independent'] is False, 'catalogue lineage')
    for key, target in {'catalogue_original_pdf_acquired': False, 'catalogue_page_verified': False, 'catalogue_sha256': None}.items():
        require(cat[key] is target, 'unverified catalogue')
    entry = cat['observed_entry']
    expected = {'project': 'PETROBRAS - Projeto 53 D', 'region': 'Nordeste', 'project_nominal_year': 1961,
                'aerial_photo_nominal_scale_denominator': 25000, 'photo_index_nominal_scale_denominator': 100000,
                'sheet_mi': 1850, 'sheet_cim': 'SC-24-Z-C-VI', 'sheet_label': 'Esplanada', 'sheet_states': ['BA', 'SE']}
    require(entry == expected, 'catalogue entry misread')
    loc = record['nominal_coverage_crosswalk']
    require(loc['parent'] == 'CGEO-24' and loc['target_mi'] == 1850, 'sheet dependency')
    ref_sheet = next(s for s in sheet['nominal_graticule']['sheets'] if s['mi'] == 1850)
    require(loc['sheet_bbox_w_s_e_n'] == ref_sheet['bbox'], 'bbox not inherited from CGEO-24')
    require(loc['modern_cameras_in_nominal_sheet'] == [c['id'] for c in sheet['camera_observations']], 'camera ids')
    west, south, east, north = ref_sheet['bbox']
    for cam in sheet['camera_observations']:
        require(west <= cam['lon'] <= east and south <= cam['lat'] <= north, 'camera not in sheet')
        require(cam['epoch'] == '2022-09-15' and cam['mi_expected'] == 1850, 'camera epoch and index')
    for key in ('full_sheet_aerial_coverage_verified', 'individual_flight_line_or_photo_footprint_known',
                'historical_urban_center_inside_flight_footprint_verified'):
        require(loc[key] is False, 'index promoted to footprint: ' + key)
    art = record['artifact_status']
    for key in ('original_photo_index_acquired', 'original_aerial_frames_acquired',
                'original_negative_acquired', 'current_holding_status_confirmed'):
        require(art[key] is False, 'unacquired artifact: ' + key)
    for key in ('individual_frame_capture_date', 'film_roll_and_frame_ids', 'flight_coverage_geometry',
                'photo_control_points', 'horizontal_datum', 'horizontal_error_m'):
        require(art[key] is None, 'unsupported artifact detail: ' + key)
    temporal = record['temporal_and_independence']
    require(temporal['incident_date'] == '1963-11-08' and entry['project_nominal_year'] < 1963, 'historical date')
    require(temporal['nominal_project_year_predates_incident'] is True, 'nominal year flag')
    require(edition['target_sheet']['sheet_publication_year'] == 1973, 'parent edition changed')
    require(temporal['same_artifact_as_sudene_1973_mi1850'] is False, 'confused photo/map artifacts')
    require(temporal['same_observational_lineage_as_1956_1963_sacs_geofoto_sheets'] is None, 'unsupported independence claim')
    for key in ('each_frame_proven_pre_incident', 'separate_independent_1963_witness', 'can_constrain_orbital_reentry'):
        require(temporal[key] is False, 'premature inference: ' + key)
    require(temporal['candidate_for_retrospective_urban_geometry'] is True, 'potential route not recorded')
    for key in ('center_point_1963', 'center_polygon_1963', 'fall_location_1963'):
        require(temporal[key] is None, 'invented center/impact: ' + key)
    require({x['to'] for x in record['graph_edges']} == {'CGEO-24', 'CGEO-25', 'CGEO-17', 'CGEO-18'}, 'graph dependencies')
    return 'CGEO-26 CONTRACT_ONLY_PASS: 1961 archive locator; NO ORIGINAL FILM OR CATALOGUE VERIFIED'


def main():
    print(check(load(C26), load(C24), load(C25)))


if __name__ == '__main__':
    main()
