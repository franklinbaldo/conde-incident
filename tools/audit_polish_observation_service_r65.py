"""Fail-closed custody audit of the 1964 Polish aggregate observing service report."""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/tle_custody/polish_observation_service_C241_LONTRA_R65.json"


def validate(data: dict) -> bool:
    if data.get("id") != "C241-LONTRA-R65" or data.get("schema") != "conde.archival_observation_service_report/v1":
        raise ValueError("identity/schema")
    s = data["source"]
    fixed = {
        "title": "Udział Polski w badaniach przestrzeni kosmicznej",
        "publication_year": 1964, "issue": 3, "full_pdf_bytes": 4882674,
        "full_pdf_sha256": "0664d3134c15e999a67158c1dfd013a49e435fc00dbe86c78fc2b2452b526c94",
        "full_pdf_pages": 62, "pdf_pages_one_based": [30, 31],
        "printed_pages": [190, 191],
        "verification": "FULL_BINARY_DOWNLOADED_IFRO_AND_VISUAL_SCREENSHOT_PDF_PAGES_30_31",
        "url": "https://www.urania.edu.pl/pliki/archiwum/postepy_astronomii_1964_03.pdf",
    }
    for key, value in fixed.items():
        if s.get(key) != value:
            raise ValueError("source immutable: " + key)
    service = data["reported_service"]
    expected = {
        "started_year": 1957, "observations_through_year": 1963,
        "aggregate_count_lower_bound_exclusive": 25000,
        "count_scope": "MULTI_YEAR_MULTI_TARGET_ALL_STATIONS",
        "satellite_origins": ["USSR", "USA"],
        "measurement_methods": ["visual", "photographic", "radio"],
        "stations_approx_before_1964": 10, "stations_in_1964": 12,
        "cospar_station_id_first": 1151, "cospar_station_id_last": 1162,
        "international_coordination_center": "Moscow",
        "echo1_project_since": 1963
    }
    for key, value in expected.items():
        if service.get(key) != value:
            raise ValueError("aggregate service misrepresented: " + key)
    b = data["boundaries"]
    expected_boundary = {
        "observations_for_norad_527_528_529": [], "independent_measurement_rows_recovered": 0,
        "object_specific_time_observed": None, "original_station_logs_recovered": False,
        "individual_station_instrument_calibration_recovered": False, "new_orbital_constraints": 0,
        "author_or_institution_contacted": False,
        "interpretation": "CONTEMPORANEOUS_AGGREGATE_SERVICE_REPORT_NOT_OBJECT_MEASUREMENTS",
    }
    for key, value in expected_boundary.items():
        if key not in b or b[key] != value:
            raise ValueError("unsupported orbit/sensor promotion: " + key)
    return True


def main() -> None:
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")))
    print("PASS C241-LONTRA-R65: scanned service report kept separate from object observations")


if __name__ == "__main__":
    main()
