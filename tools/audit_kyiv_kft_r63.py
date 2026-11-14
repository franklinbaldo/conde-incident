"""Temporal custody of Kyiv station 1023: later KFT is not a 1963 sensor."""
from __future__ import annotations
import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/tle_custody/kyiv_kft_instrument_era_C241_LONTRA_R63.json"
DOI = "10.33099/2707-1383-2020-38-4-254-272"
ARCHIVE_IDS = {"ССШСЗ-04-18-01": "1-7", "ССШСЗ-04-18-02": "1-12"}

def validate(data: dict) -> bool:
    if data.get("schema") != "conde.archival_instrument_era_locator/v1" or data.get("id") != "C241-LONTRA-R63":
        raise ValueError("source identity or schema altered")
    s = data.get("source", {})
    expected = {
        "type": "RETROSPECTIVE_RESEARCH_ARTICLE_2020", "doi": DOI,
        "article_url": "https://viv.nuou.org.ua/article/view/229864",
        "pdf_url": "https://viv.nuou.org.ua/article/download/229864/228719/523958",
        "publication_date": "2020-12-02", "printed_page_visual_checked": 263,
        "pdf_page_visual_checked_one_based": 10,
        "pdf_bytes_recovered_in_executor": False, "pdf_bytes_sha256": None, "pdf_bytes_length": None,
        "source_read_method": "WEB_PDF_PAGE_VISUALLY_INSPECTED",
    }
    for k, v in expected.items():
        if s.get(k, object()) != v:
            raise ValueError("article custody altered: " + k)
    h = data.get("historical_facts", {})
    dates = {
        "station_code": "1023", "station_city": "Kyiv",
        "station_visual_observation_started": 1957,
        "station_reported_operating_end": 1989, "kyiv_kft_model": "КФТ-10/20",
        "instrument_received_from_moscow_year": 1965,
        "observatory_prepared_instrument_year": 1966,
        "additional_chronograph_shutter_timing_project_year": 1969,
        "timing_delays_report_year": 1976,
        "source_page_for_station_and_arrival": 263,
        "source_page_for_1976_delays": 265,
    }
    for k, v in dates.items():
        if h.get(k) != v:
            raise ValueError("instrument era altered: " + k)
    if h.get("timing_delays_s") != {"chronograph": 0.029, "shutter": 0.004}:
        raise ValueError("1976 delays changed")
    if not (h["station_visual_observation_started"] <= 1963 < h["instrument_received_from_moscow_year"]):
        raise ValueError("timeline no longer discriminates 1963")
    files = data.get("archival_followups", [])
    if len(files) != 2 or {item.get("file"): item.get("leaves") for item in files} != ARCHIVE_IDS:
        raise ValueError("archive shelfmarks altered")
    if any(item.get("source_page") != 265 or "МКАО" not in item.get("holder", "") for item in files):
        raise ValueError("archive context altered")
    b = data.get("boundaries", {})
    for k in ("kft_1023_in_service_in_1963", "may_transfer_1976_precision_to_1963",
              "original_archival_files_read", "archive_contacted"):
        if b.get(k) is not False:
            raise ValueError("false promotion: " + k)
    if b.get("station_exists_in_1963") is not True:
        raise ValueError("discarded earlier station history")
    if b.get("observations_identified_norad_527_528_529") != [] or b.get("new_orbital_constraints") != 0:
        raise ValueError("invented target observation or physical constraint")
    if b.get("epistemic_class") != "RETROSPECTIVE_INSTRUMENT_TIMELINE_NOT_PRIMARY_OBSERVATION":
        raise ValueError("misclassified 2020 retrospective")
    return True

if __name__ == "__main__":
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")))
    print("C241-LONTRA-R63 PASS: 1965 instrument is not 1963 sensor; no orbit constraints")
