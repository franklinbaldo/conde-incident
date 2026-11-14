"""Reproduce the complete 1965 Hungarian yearbook PDF and enforce evidence boundaries under -O."""
import argparse
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/baja_1966_yearbook_interobs_C241-LONTRA-R39.json"
URL = "https://real-j.mtak.hu/15014/1/csillagaszati_evkonyv_1966.pdf"
SHA = "8061e6c164836e6b6e0e465be801fcb891002204bd3a523b4eda43a81d8d459a"
BYTES = 7868699


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(data, pdf_bytes=None):
    require(data["schema"] == "conde.contemporary_satellite_tracking_bibliography/v1", "schema")
    require(data["id"] == "C241-LONTRA-R39", "id")
    require(data["status"] == "CONTEMPORARY_YEARBOOK_IDENTIFIES_1963_1964_INTEROBS_CAMPAIGN_VOLUMES_NOT_TARGET_OBSERVATIONS", "status")
    s = data["source"]
    for key, expected in {
        "url": URL, "http_status": 200, "https_download_succeeded": True,
        "bytes": BYTES, "sha256": SHA, "publication_year": 1965,
        "cover_year": 1966, "pdf_page_count": 244, "page_zero_based": 120,
        "printed_page": 119, "page_visually_inspected": True,
        "original_print_page_facsimile_retrieved": True,
        "original_interobs_campaign_volumes_retrieved": False
    }.items():
        require(s[key] == expected, "source." + key)
    r = data["report"]
    require(r["report_period"] == "1964-05-01/1965-04-30", "report period")
    require(r["reported_observation_years"] == [1963, 1964], "reported years")
    require(r["states_dataset_from_1963_and_1964_prepared_and_published"] is True, "publication claim")
    require(r["cited_publication_volumes"] == ["Folge I", "Folge II"], "volumes")
    require("Kooperationswochen" in r["cited_publication_title"], "publication title")
    require(r["campaign_coverage_1963_11_07_to_09"] is None, "campaign coverage invented")
    require(r["reported_over_7000_measurements"] is True, "aggregate count qualifier")
    require(r["over_7000_measurements_attributable_to_1963"] is False, "count attributed to wrong period")
    require(r["listed_satellite_codes_for_processing"] == ["60053", "63431"], "satellite codes")
    require(r["listed_satellite_codes_proven_to_be_527_528_529"] is False, "false target identity")
    require(r["station_logs_retrieved"] is False, "station logs not recovered")
    lim = data["limits"]
    for key in ("target_observations_identified", "raw_instrumental_observations_retrieved",
                "november_1963_campaign_confirmed", "original_campaign_volume_pages_read",
                "outreach_sent"):
        require(lim[key] is False, "limits." + key)
    require(lim["new_target_orbital_measurements"] == 0, "false measurements")
    require(lim["orbital_constraints_activated"] == 0, "false orbital constraint")
    require("1963-11-07" in data["follow_up"] and "1963-11-09" in data["follow_up"], "date scope")
    if pdf_bytes is not None:
        require(len(pdf_bytes) == BYTES, "PDF byte length")
        require(hashlib.sha256(pdf_bytes).hexdigest() == SHA, "PDF SHA256")
        require(pdf_bytes.startswith(b"%PDF-"), "PDF magic")
        require(b"%%EOF" in pdf_bytes[-128:], "PDF EOF")
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise RuntimeError("pypdf==6.4.0 required when --pdf-original is used") from e
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
        require(len(reader.pages) == 244, "PDF page count")
        text = reader.pages[120].extract_text() or ""
        for token in ("BAJA", "1963", "1964", "7000", "60053", "63431",
                      "Kooperationswo", "Folge I", "119"):
            require(token in text, "page 119 text missing: " + token)
        require("1963" in text and "két kötetben" in text, "reported two published volumes")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-original", type=Path)
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, args.pdf_original.read_bytes() if args.pdf_original else None)
    print("C241-LONTRA-R39: PDF provenance and evidence boundaries PASS")


if __name__ == "__main__":
    main()
