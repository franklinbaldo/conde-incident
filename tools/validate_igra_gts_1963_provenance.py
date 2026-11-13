"""Validate historical IGRA family lineage without backdating 2006/2014 catalogues."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/meteorology/igra_gts_1963_provenance.json"
OLDER = ROOT / "research/meteorology/igra_recife_height_lineage_1963.json"


def validate(data, older):
    if data["schema"] != "conde.igra-gts-1963-provenance/v1":
        raise ValueError("wrong schema")
    article = data["sources"]["igra_methods_2006"]
    wmo = data["sources"]["wmo_historical_catalogue_scope"]
    if (article["published"] != "2006-01-01"
            or article["doi"] != "10.1175/JCLI3594.1"
            or article["binary_sha256"] is not None):
        raise ValueError("source date or integrity overstated")
    if (wmo["catalogue_vintage_found"] != "2014-07"
            or wmo["historical_1963_catalogue_obtained"] is not False
            or wmo["raw_html_bytes"] != 29556
            or wmo["raw_html_sha256"] != "6c8b5b69b9f38c6c569a10b5a8ecd3572e6c5221e3e0ac2654d5540b38e8c56a"):
        raise ValueError("historical WMO source misrepresented")
    historic = data["general_igra_processing_documented_in_2006"]
    if (historic["ncdc_gts_core_interval"] != "1963-1970"
            or "WMO No. 9 Volume A 2004" not in historic["station_name_country_auxiliary_metadata_sources_include"]
            or historic["station_number_compositing_documented"] is not True
            or historic["same_station_raw_and_modern_id_guaranteed"] is not False):
        raise ValueError("archive-method caveats lost")
    case = data["recife_case"]
    if (case["archive_station_id"] != older["historical_source"]["station_id"]
            or case["upstream_code_in_existing_pin"] != older["historical_source"]["upstream"]
            or case["original_archive_sha256"] != older["historical_source"]["archive_sha256"]
            or not re.fullmatch(r"[a-f0-9]{64}", case["original_archive_sha256"])):
        raise ValueError("archive parent mismatch")
    unknowns = ["original_1963_launch_site_wmo_id", "original_1963_launch_site_coordinates",
                "original_1963_release_time_utc", "original_1963_radiosonde_model",
                "pressure_temperature_gph_covariance", "transfer_uncertainty_recife_conde"]
    if any(case[x] is not None for x in unknowns):
        raise ValueError("unwarranted instrument/time/position inference")
    if any(case[x] is not False for x in ["upstream_yearly_code_proven_to_be_original_recife_gts_message",
                                               "original_gts_message_obtained", "original_1963_station_catalogue_obtained",
                                               "original_sensor_and_processing_log_obtained"]):
        raise ValueError("original records not obtained")
    interp = data["interpretation"]
    if (interp["catalogue_date_not_observation_date"] is not True
            or interp["meteorology_1963_at_conde_measured"] is not False
            or interp["admissible_domain_reduction"] is not False
            or interp["hard_physical_constraints_added"] != 0
            or interp["independent_measurements_added"] != 0
            or data["status"] != "CONNECTED_PENDING_CALIBRATION"):
        raise ValueError("metadata silently promoted to physical constraint")
    if set(data["dependencies"]) != {"C149", "C150", "C151", "C193"}:
        raise ValueError("dependency lineage changed")
    return True


if __name__ == "__main__":
    validate(json.loads(SOURCE.read_text()), json.loads(OLDER.read_text()))
    print("PASS IGRA 1963 GTS method vs retrospective station metadata")
