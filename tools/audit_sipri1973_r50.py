#!/usr/bin/env python3
"""Audit SIPRI 1973 as later editorial identification, not an independent sensor."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'research/tle_custody/sipri1973_1963_003a_C241_LONTRA_R50.json'


def require(test, message):
    if not test:
        raise ValueError(message)


def load():
    source = json.loads(FILE.read_text(encoding='utf-8'))
    soviet = json.loads((ROOT / source['comparison']['soviet_1964_ledger']).read_text(encoding='utf-8'))
    nasa = json.loads((ROOT / source['comparison']['nasa_1963_ledger']).read_text(encoding='utf-8'))
    return source, soviet, nasa


def audit(source, soviet, nasa, pdf_path=None):
    require(source['id'] == 'C241-LONTRA-R50', 'Unknown case')
    s, row, comparison = source['source'], source['printed_row'], source['comparison']
    require(s['publication_year'] == 1973 and soviet['work']['publication_year'] == 1964,
            'Chronology must preserve 1964 earlier than 1973')
    require(s['institution'] == 'Stockholm International Peace Research Institute (SIPRI)', 'Custodian')
    require(s['printed_page'] == 84 and s['table'].startswith('3A.2'), 'Wrong location')
    require(s['critical_page_visually_inspected'] is False and s['pdf_page_one_based'] is None,
            'Unverified PDF page or visual claim')
    require(row['designation'] == 'USAF (1963-03A)', 'Wrong object identity')
    require(row['launch_vehicle'] == 'Van Th/A-D', 'Wrong printed launch vehicle')
    require(row['launch_date_gmt_as_printed'] == '16 Jan 2248', 'Wrong printed launch time')
    require(row['perigee_km'] == soviet['printed_table_row']['perigee_km_printed'] == 459,
            'Perigee mismatch')
    require(row['apogee_km'] == soviet['printed_table_row']['apogee_km_printed'] == 533,
            'Apogee mismatch')
    require(Decimal(row['period_min']) == Decimal(str(soviet['printed_table_row']['period_minutes_printed'])) == Decimal('94.66'),
            'Period mismatch')
    require(Decimal(row['inclination_deg']) == Decimal(str(soviet['printed_table_row']['inclination_degrees_printed'])) == Decimal('81.89'),
            'Inclination mismatch')
    require(soviet['printed_table_row']['norad_identifier_printed'] is None,
            'Do not retroactively add NORAD to Soviet printed source')
    require(comparison['soviet_all_four_orbital_values_exact_match'] is True,
            'False four-field interpretation')
    require(comparison['soviet_launch_vehicle_label_agenad_match'] is True,
            'False launcher interpretation')
    require(comparison['later_sipri_explicit_1963_003a_supports_candidate_identity'] is True and
            comparison['soviet_printed_designation_is_anonymous'] is True,
            'Identity must remain a hypothesis about earlier text')
    require(comparison['soviet_1964_derived_from_sipri_1973_possible'] is False,
            '1973 cannot be upstream for 1964 publication')
    require(comparison['both_derived_from_earlier_western_compilation_possible'] is True,
            'Upstream genealogical uncertainty omitted')
    for item in ('observation_epoch_utc', 'instrument_station', 'measurement_uncertainty', 'raan_deg', 'source_of_orbital_elements'):
        require(row[item] is None, 'Invented instrumental data: ' + item)
    for item in ('independent_instrumental_sources_count_added', 'new_1963_11_07_09_observations', 'new_physical_constraints_activated'):
        require(comparison[item] == 0, 'False constraint promotion: ' + item)
    require(s['archive_external_contact_sent'] is False, 'External contact not authorized')
    nasa_rows = [r for sc in nasa['sources'] for r in sc['rows'] if r.get('designator') == '1963-003A']
    require(any(r['perigee_km'] == 459 and r['apogee_km'] == 533 for r in nasa_rows),
            'Incorrect NASA object lineage')
    require(s['pdf_bytes'] == 10149951 and s['pdf_sha256'] ==
            'e4938f51e42243e36aa632e6385fbb024b688e5062f5dff2ff965f9023591b6e', 'PDF manifest corrupted')
    if pdf_path:
        path = Path(pdf_path)
        dig = hashlib.sha256()
        with path.open('rb') as file:
            header = file.read(8)
            require(header.startswith(b'%PDF-1.'), 'PDF magic mismatch')
            dig.update(header)
            for block in iter(lambda: file.read(1024 * 1024), b''):
                dig.update(block)
        require(path.stat().st_size == s['pdf_bytes'] and dig.hexdigest() == s['pdf_sha256'],
                'PDF bytes integrity mismatch')
        with path.open('rb') as file:
            file.seek(-64, 2)
            require(b'%%EOF' in file.read(), 'Incomplete PDF EOF')
    return 'LATER_IDENTIFIED_ROW_NOT_INDEPENDENT_SENSOR'


if __name__ == '__main__':
    import sys
    print(audit(*load(), pdf_path=sys.argv[1] if len(sys.argv) > 1 else None))
