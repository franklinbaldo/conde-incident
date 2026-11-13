"""CGEO-25: validate the original-source custody and temporal non-promotion."""
import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CONTRACT = BASE / 'research/geo/cgeo25_esplanada_edition_lineage.json'
EXPECTED_SOURCES = {
    'sudene_1997_catalogue': (1785142, 'ab10ed33aa5e68094e519f83ec42fa200f908abd1d5de1b13a55312093785694', 1997),
    'sgb_1998_planimetry': (579200, '8748db4313e80c660f65ba3d4b44c3ceb4ca9a8f202cf6eb30e61c33da102d1b', 1998),
    'sgb_1998_topography': (1181396, 'f0a34c1bc0f2eafbaf991d6c65d21a411ae0563c1f3490d7a332395bc1fc0cb9', 1998),
}
SHEETS = ('721-4-2', '721-4-3', '721-4-4', '725-1-1', '725-1-2', '725-1-4')

# Pin *which* documents and printed claims each digest describes. Merely checking
# HTTPS, length and a declared SHA lets an unrelated URL inherit source custody.
SOURCE_DETAILS = {
    'sudene_1997_catalogue': {
        'url': 'https://www.gov.br/sudene/pt-br/centrais-de-conteudo/catalogo-1-para-100000-pdf/@@display-file/file',
        'local_filename': 'sudene_catalogo.pdf',
        'pdf_page_index': 124, 'printed_page': 133,
        'catalogue_record': 'MI-1850', 'full_map_sheet_in_pdf': False,
    },
    'sgb_1998_planimetry': {
        'url': 'https://rigeo.sgb.gov.br/server/api/core/bitstreams/69f40826-c61e-4f46-b5a5-b50d2a279627/content',
        'local_filename': '69f40826-c61e-4f46-b5a5-b50d2a279627.pdf',
        'pdf_page_index': 0, 'map_subject': 'Acajutiba, Apora e Rio Real; na Bahia',
    },
    'sgb_1998_topography': {
        'url': 'https://rigeo.sgb.gov.br/server/api/core/bitstreams/c7a40a7e-22d8-48f2-9276-a889e6d1a676/content',
        'local_filename': 'c7a40a7e-22d8-48f2-9276-a889e6d1a676.pdf',
        'pdf_page_index': 0, 'map_subject': 'Acajutiba, Apora e Rio Real; na Bahia',
    },
}
SOURCE_BASE_FIELDS = {'size_bytes', 'sha256', 'issued_year', 'verified_pdf_bytes'}



def load():
    return json.loads(CONTRACT.read_text(encoding='utf-8'))


def require(condition, error):
    if not condition:
        raise ValueError(error)


def validate(data):
    require(data['schema'] == 'conde.gis.cartographic-edition-lineage/v1' and data['id'] == 'CGEO-25', 'schema/id')
    require(data['municipality']['ibge_code'] == 2908606 and data['municipality']['state'] == 'BA', 'wrong Conde')
    sheet = data['target_sheet']
    for name, val in {'mi': 1850, 'nomenclature': 'SC.24-Z-C-VI', 'scale_denominator': 100000,
                      'sheet_publication_year': 1973, 'sheet_original_acquired': False,
                      'sheet_prior_to_incident': False}.items():
        require(sheet[name] == val, f'sheet {name}')
    require(sheet['coverage_graticule'] == {'south': -12.0, 'north': -11.5, 'west': -38.0, 'east': -37.5}, 'bbox')
    require(set(data['sources']) == set(EXPECTED_SOURCES), 'sources')
    for key, (size, sha, year) in EXPECTED_SOURCES.items():
        src = data['sources'][key]
        details = SOURCE_DETAILS[key]
        require(set(src) == SOURCE_BASE_FIELDS | set(details), f'unreviewed source field {key}')
        require(src['size_bytes'] == size and src['sha256'] == sha and src['issued_year'] == year,
                f'custody {key}')
        require(src['verified_pdf_bytes'] is True, f'PDF status {key}')
        for field, expected in details.items():
            require(src[field] == expected, f'source document identity {key}:{field}')
    old = data['prior_cartographic_inputs_reported_by_sgb']
    require(old['source_family'] == 'PETROBRAS / SACS / GEOFOTO', 'source family')
    require(old['sheet_scale_denominator'] == 25000 and old['production_year_interval_in_1998_source'] == [1956, 1963], 'source period')
    require(tuple(old['sheet_identifiers']) == SHEETS, 'sheet identifiers')
    for key in ('individual_sheet_dates_authenticated', 'individual_sheet_bytes_acquired',
                'coverage_of_1963_conde_center_authenticated'):
        require(old[key] is False, f'premature elevation {key}')
    historic = data['historical_use']
    require(historic['event_date'] == '1963-11-08', 'event date')
    for key in ('edition_1973_is_direct_contemporary_evidence', 'sources_are_independent_observations_of_incident',
                'can_constrain_orbital_reentry'):
        require(historic[key] is False, f'false inference {key}')
    for key in ('center_point_1963', 'center_polygon_1963', 'fall_location_1963', 'horizontal_error_m', 'historic_datum'):
        require(historic[key] is None, f'unsupported geographic value {key}')
    require({x['to'] for x in data['dependencies']} >= {'CGEO-24', 'CGEO-17', 'CGEO-18'}, 'parent chain')


def replay_local(data, directory):
    for key, src in data['sources'].items():
        path = directory / src['local_filename']
        size = path.stat().st_size
        require(size == src['size_bytes'], f'byte length {key}')
        with path.open('rb') as fh:
            require(fh.read(5) == b'%PDF-', f'not a PDF {key}')
            h = hashlib.sha256(b'%PDF-')
            while chunk := fh.read(65536):
                h.update(chunk)
        require(h.hexdigest() == src['sha256'], f'SHA mismatch {key}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sources-dir', type=Path)
    args = ap.parse_args()
    data = load()
    validate(data)
    if args.sources_dir:
        replay_local(data, args.sources_dir)
        print('CGEO-25 PASS: contract + 3 authentic PDF byte replays')
    else:
        print('CGEO-25 PASS: OFFLINE contract only, no source bytes rechecked')


if __name__ == '__main__':
    main()
