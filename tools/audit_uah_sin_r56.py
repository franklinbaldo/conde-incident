"""Fail-closed custody check of the 1963 UAH space-tracking digest."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/tle_custody/uah_sin_196311_C241_LONTRA_R56.json"
SHA = "f953ffe533a7f6e0a3430c6381903be57dd98521523622e4b6e90c7830080318"
URL = "https://digitalprojects.uah.edu/files/original/195/3372/spaceintelligencenotes_19631100.pdf"


def audit(d):
    if d.get("id") != "C241-LONTRA-R56" or d.get("evidence_class") != "CONTEMPORARY_REPRINT_OF_SOVIET_INSTRUMENT_METHOD":
        raise ValueError("source identity")
    s = d.get("source", {})
    expected_source = {
        "pdf_url": URL, "catalogue_url": "https://digitalprojects.uah.edu/items/show/3372",
        "publisher": "George C. Marshall Space Flight Center, Space Systems Information Branch",
        "volume": 4, "issue": 11, "publication_month": "1963-11",
        "http_status": 200, "mime": "application/pdf", "downloaded_bytes": 10004789,
        "sha256": SHA, "pages": 28, "image_only_no_text_layer": True,
        "visually_inspected_pdf_pages_one_based": [1, 3, 5, 6, 24],
        "original_pdf_retrieved": True,
    }
    for k, v in expected_source.items():
        if s.get(k) != v:
            raise ValueError("invalid source: " + k)
    m = d.get("instrument_digest", {})
    expected_digest = {
        "printed_page": 24, "pdf_page_one_based": 24, "section": "TRACKING",
        "shutter_open_delay_seconds": 0.0022,
        "shutter_open_uncertainty_seconds": 0.0002,
        "shutter_close_delay_seconds": 0.0002,
        "shutter_close_uncertainty_seconds": 0.0002,
        "chronograph_delay_seconds_at_210_v": 0.0268,
        "chronograph_delay_seconds_at_230_v": 0.0254,
        "chronograph_voltage_difference_seconds": 0.0014,
        "secondary_us_report_number": "1521678463",
        "secondary_us_report_date": "1963-06-19",
        "claimed_original_journal": "Astronomicheskiy Zhurnal, Moskva, no. 5, May 1963",
        "original_russian_paper_retrieved": False,
        "us_intelligence_report_retrieved": False,
        "observation_record_in_digest": False,
    }
    for k, v in expected_digest.items():
        if m.get(k) != v:
            raise ValueError("unsupported instrument claim: " + k)
    if abs(m["chronograph_delay_seconds_at_210_v"] - m["chronograph_delay_seconds_at_230_v"] - m["chronograph_voltage_difference_seconds"]) > 1e-12:
        raise ValueError("inconsistent chronograph arithmetic")
    if m.get("devices_named") != ["NAFA-3S/25-S camera", "21-P chronograph", "1P-M pulse adapter", "PRV radio receiver", "SPV-3 photocell", "8-loop cathode oscillograph"]:
        raise ValueError("incorrect instrument names")
    if d.get("context") != {"printed_pages_visually_checked": [3, 5, 6], "soviet_radio_astronomy_visit_lovell_reported": True, "context_is_independent_satellite_measurement": False}:
        raise ValueError("context promoted to sensor")
    if d.get("conclusions") != {
        "observations_norad_527_528_529": [],
        "instrument_epochs_1963_11_07_to_09": [],
        "new_independent_sensors": 0,
        "activated_orbital_constraints": 0,
        "instrument_delays_transferable_to_527_528_529": False,
        "institutional_contacts_sent": 0,
    }:
        raise ValueError("unsupported orbital promotion")
    return True


def replay(pdf):
    p = Path(pdf)
    if not p.is_file() or p.stat().st_size != 10004789:
        return False
    sha = hashlib.sha256()
    with p.open("rb") as f:
        if f.read(5) != b"%PDF-":
            return False
        f.seek(max(0, p.stat().st_size - 200))
        if b"%%EOF" not in f.read():
            return False
        f.seek(0)
        while chunk := f.read(1024 * 1024):
            sha.update(chunk)
    return sha.hexdigest() == SHA


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True, help="retrieved UAH scan; mandatory byte replay")
    args = parser.parse_args()
    audit(json.loads(SOURCE.read_text(encoding="utf-8")))
    if not replay(args.pdf):
        parser.error("original PDF bytes mismatch")
    print("R56 OK: UAH 1963-11 digest scanned PDF verified; no NORAD observation promoted")
