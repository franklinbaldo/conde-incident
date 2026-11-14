#!/usr/bin/env python3
"""R51: validate archival NASA reproduction without promoting a table into sensor data."""
from hashlib import sha256
import json
from math import pi, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/tle_custody/stl_space_log_nasa_r51.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def circular_period_min(perigee, apogee, km_per_unit=1):
    earth_radius_km = 6371.0
    earth_mu_km3_s2 = 398600.4418
    radius = earth_radius_km + (perigee + apogee) * km_per_unit / 2
    return 2 * pi * sqrt(radius ** 3 / earth_mu_km3_s2) / 60


def audit(data, pdf_path=None):
    require(data['id'] == 'C241-LONTRA-R51', 'Evidence ID')
    require(data['document_role'] == 'historical_editorial_reproduction_not_observation', 'Lineage')
    require(data['document_number'] == 'NASA TM X-59315 / N167-17917', 'Document')
    require(data['pdf_page_count'] == 117 and data['pdf_critical_page_one_based'] == 105 and data['printed_page'] == 'B-12', 'Page mapping')
    require(data['visual_inspection'] == 'completed_2026-11-14_on_colab_offloaded_render', 'Visual inspection')
    require(data['printed_reproduction_credit'] == 'Material Reproduced from STL SPACE LOG, Vol. 3, No. 4, Space Laboratories, Inc.', 'Credit')
    require(data['stl_original_issue_retrieved'] is False, 'Original STL issue not seen')
    row = data['printed_row']
    require(row['international_designation_as_printed'] == '1963 3A' and row['launch_date_as_printed'] == 'Jan 16, 1963', 'Identity')
    require(row['row_note'] == 'In orbit: classified payload (initial orbital data as of January 31, 1963)', 'Printed initial-data as-of note drifted')
    require(row['period_minutes_in_printed_order'] == [94.7, 94.6], 'Both periods')
    require(row['perigee_altitudes_in_printed_order'] == [298, 286], 'Both perigees')
    require(row['apogee_altitudes_in_printed_order'] == [322, 334], 'Both apogees')
    require(row['inclinations_degrees_in_printed_order'] == [82.0, 81.9], 'Both inclinations')
    require(row['perigee_apogee_unit_on_b12'] == 'miles', 'B-12 printed altitude units')
    require(row['unit_legend_location'] == 'B-12 lower-right footer (PDF page 105/117)', 'Unit provenance')
    require(row['mile_variant_as_printed'] is None, 'No unsupported statute/nautical subtype')
    require(row['station_or_instrument'] is None and row['individual_measurement_utc'] is None and row['observational_uncertainty'] is None, 'No invented sensor')
    q = data['scientific_interpretation']
    require(q['km_status'] == 'CONTRADICTS_PRINTED_B12_MILES_LEGEND', 'Reject unsupported kilometers')
    require(q['miles_as_printed_confirmed'] is True, 'Printed unit not verified')
    require(q['printed_pair_is_not_two_independent_sensors'] and q['orbital_data_date_is_not_1963_11_07_09'], 'No double counting')
    require(q['original_stl_pages_or_date_verified'] is False and q['candidate_upstream_proven'] is False, 'No proven direct genealogy')
    require(q['km_interpretation_inconsistent_with_printed_period_under_two_body_assumption'], 'Physical diagnostic preserved')
    require(q['statute_mile_interpretation_numerically_plausible_not_documented'], 'Not a verified conversion')
    for k in ('new_1963_11_07_09_measurements', 'independent_instrumental_sensors_added', 'new_physical_constraints_activated'):
        require(q[k] == 0, 'Unsupported scientific promotion: ' + k)
    require(q['archive_external_contact_sent'] is False, 'Unauthorized external contact')
    require(abs(circular_period_min(298, 322) - 90.58) < 0.03, 'km diagnostic')
    require(abs(circular_period_min(298, 322, 1.609344) - 94.45) < 0.03, 'miles diagnostic')
    if pdf_path is not None:
        b = Path(pdf_path).read_bytes()
        require(len(b) == data['pdf_bytes'] == 31749209, 'PDF size changed')
        require(b[:8].startswith(b'%PDF-1.') and b'%%EOF' in b[-256:], 'PDF completeness')
        require(sha256(b).hexdigest() == data['pdf_sha256'] == 'f77b0e8998d467dd457d0ab8e8012e6e9d69c60fb6180aa3d68f1e8422b32786', 'PDF SHA256')
    return 'EDITORIAL_REPRODUCTION_MILES_PRINTED_SUBTYPE_PENDING_ZERO_CONSTRAINTS'


if __name__ == '__main__':
    import sys
    print(audit(json.loads(SOURCE.read_text()), sys.argv[1] if len(sys.argv) > 1 else None))
