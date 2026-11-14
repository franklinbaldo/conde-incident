"""Validate archival assertions without mistaking a viewer for a downloaded PDF."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/interobs_ftd_translation_C241-LONTRA-R41.json"

def need(condition, message):
    if not condition:
        raise ValueError(message)

def validate(d):
    need(d["schema"] == "conde.archival_interobs_translation/v1", "schema")
    need(d["id"] == "C241-LONTRA-R41", "id")
    need(d["audit_date"] == "2026-11-14", "audit date")
    doc = d["document"]
    for k,v in {"report_number":"FTD-HT-23-856-68",
        "accession":"AD 684833","translation_date":"1968-09-20",
        "original_year":1967,"original_issue":6,
        "original_copy_retrieved":False}.items():
        need(doc[k] == v, "document."+k)
    need(doc["facsimile_viewer"].startswith("https://scispace.com/pdf/"), "facsimile locator")
    a = d["access"]
    for k,v in {"cover_pdf_page_zero_based":0,
        "critical_pdf_pages_zero_based":[25,26],
        "critical_printed_pages":[18,19],
        "cover_and_critical_pages_visually_inspected":True,
        "pdf_viewer_readable":True,
        "local_pdf_download_http_status":403,
        "local_pdf_download_success":False,
        "full_pdf_bytes":None,"full_pdf_sha256":None,
        "full_pdf_page_count":None,"downloaded_pdf_replay":"NOT_RUN",
        "original_russian_facsimile_retrieved":False}.items():
        need(a[k] == v, "access."+k)
    r = d["report"]
    need(r["author"] == "M. Ill", "author")
    need(r["first_detailed_interobs_observation_year"] == 1963, "historical year")
    need(r["first_detailed_observation_month"] == "August", "first observation month")
    need(r["regular_special_sessions_from_year"] == 1964, "regular sessions")
    need(r["positions_approximate_by_year"] == {"1963":600,"1964":6400,
        "1965":12200,"1966":40000}, "approximate counts")
    need(r["positions_are_approximate"] is True, "counts must be approximate")
    need(r["all_observations_reported_sent_to"] == "Baja, Hungary", "archive route")
    need(r["original_station_logs_retrieved"] is False, "source records absent")
    need(r["observations_are_not_specific_to_norad_targets"] is True, "not target counts")
    s = d["scope"]
    need(s["target_norad_ids"] == [527,528,529], "target ids")
    need(s["target_international_designators"] == ["1963-003A","1963-003B","1963-003C"], "target designation")
    for k in ("target_observations_identified",
              "target_specific_1963_11_07_to_09_campaign_confirmed",
              "independent_target_sensor_claimed","external_outreach_sent"):
        need(s[k] is False, "fabricated target observation: "+k)
    need(s["orbital_constraints_activated"] == 0, "false orbital constraint")
    need(s["new_instrumental_target_measurements"] == 0, "false target measurement")
    need("Folge I-II" in d["follow_up"] and "1963-11-09" in d["follow_up"], "next acquisition")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args()
    validate(json.loads(args.manifest.read_text(encoding="utf-8")))
    print("C241-LONTRA-R41 archival scope PASS; downloaded PDF replay NOT_RUN")
