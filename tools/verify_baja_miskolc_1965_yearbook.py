"""Verify the full 1964-published Hungarian yearbook and forbid promoted orbital claims."""
import argparse
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/baja_miskolc_1965_yearbook_C241-LONTRA-R42.json"
URL = "https://real-j.mtak.hu/15941/1/csillagaszati_evkonyv_1965.pdf"
SHA = "c76ff17e965af626bbf0f85a3f0f4b1f86b3804ff84e5e5867cf74e8f65039f4"
BYTES = 6850486


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(data, pdf_bytes=None):
    require(data["schema"] == "conde.contemporary_satellite_tracking_bibliography/v1", "schema")
    require(data["id"] == "C241-LONTRA-R42", "id")
    require(data["status"] == "PRIMARY_1964_YEARBOOK_REPORTS_HUNGARIAN_STATION_CAPACITY_AND_AMERICAN_SATELLITE_OBSERVATIONS_WITHOUT_TARGET_IDENTITIES", "status")
    source = data["source"]
    for key, val in {"url": URL, "http_status": 200, "tls_validated": True,
                     "bytes": BYTES, "sha256": SHA, "pdf_pages": 206,
                     "publication_year": 1964, "cover_year": 1965,
                     "full_pdf_retrieved": True, "instrumental_logs_retrieved": False}.items():
        require(source[key] == val, "source." + key)
    require(source["pages"] == [
        {"section": "Baja", "printed_page": 109, "pdf_index_zero_based": 110, "visually_inspected": True},
        {"section": "Baja", "printed_page": 110, "pdf_index_zero_based": 111, "visually_inspected": True},
        {"section": "Miskolc", "printed_page": 112, "pdf_index_zero_based": 113, "visually_inspected": True},
    ], "page mapping")
    baja = data["baja"]
    require(baja["report_period"] == "1963-04-01/1964-04", "Baja period")
    require(baja["reported_chronograph_readout_accuracy_seconds"] == 0.005, "timing")
    for key in ("readout_accuracy_not_per_position_astrometric_error", "observations_predominantly_visual",
                "soviet_supplied_nafa_camera_test_exposures_reported", "nafa_model_exact_ocr_conflicted_between_pages"):
        require(baja[key] is True, "baja." + key)
    require(baja["nafa_scientific_program_in_report_period"] is False, "no scientific NAFA")
    require(baja["nafa_scientific_program_blocker"] == "lack of suitable film by end of reporting period", "NAFA film")
    require(baja["interobs_participants_reported"] == 25, "participants")
    require(baja["interobs_western_participants_reported"] == 2, "western participants")
    require(baja["specific_527_528_529_observation"] is None, "no Baja target")
    miskolc = data["miskolc"]
    require(miskolc["station_activity_since"] == "1963-05-01", "Miskolc start")
    require(miskolc["aggregate_positional_measurements"] == 218, "218 aggregate")
    require(miskolc["soviet_and_american_satellites_observed"] is True, "both origins")
    require(miskolc["observations_visual_during_period"] is True, "visual modality")
    require(miskolc["observations_on_1963_11_07_to_09"] is None, "unknown November coverage")
    require(miskolc["american_satellite_target_identity_confirmed"] is False, "no target identification")
    require(miskolc["raw_measurement_rows_retrieved"] is False, "no instrumental rows")
    for key in ("target_observations_identified", "raw_instrumental_observations_retrieved",
                "november_1963_campaign_confirmed", "position_uncertainty_inferred_from_chronograph", "outreach_sent"):
        require(data["limits"][key] is False, "limits." + key)
    for key in ("orbital_constraints_activated", "new_target_orbital_measurements"):
        require(data["limits"][key] == 0, "limits." + key)
    require("1963-11-07" in data["follow_up"] and "1963-11-09" in data["follow_up"], "followup dates")
    if pdf_bytes is not None:
        require(len(pdf_bytes) == BYTES, "PDF bytes")
        require(hashlib.sha256(pdf_bytes).hexdigest() == SHA, "PDF hash")
        require(pdf_bytes[:5] == b"%PDF-", "PDF magic")
        require(b"%%EOF" in pdf_bytes[-128:], "PDF EOF")
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise RuntimeError("pypdf==6.4.0 is required for PDF replay") from e
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
        require(len(reader.pages) == 206, "PDF page count")
        by_page = {i: reader.pages[i].extract_text() or "" for i in (110, 111, 113)}
        for token in ("BAJA", "NAFA 3c/25", "0,005", "1963", "1964"):
            require(token in by_page[110], "p109 missing " + token)
        for token in ("25", "0,005", "film", "110"):
            require(token in by_page[111], "p110 missing " + token)
        for token in ("MISKOLC", "1963", "218", "am erikai", "AT-1", "112"):
            require(token in by_page[113], "p112 missing " + token)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-original", type=Path)
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, args.pdf_original.read_bytes() if args.pdf_original else None)
    print("C241-LONTRA-R42: source provenance and orbital-claim gate PASS")


if __name__ == "__main__":
    main()
