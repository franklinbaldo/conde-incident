#!/usr/bin/env python3
"""NORAD January-June 1963 source custody: camera control != an observation."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/norad_1963_janjun_cold_lake_C241-L57.json"
PDF_URL = "https://documents.theblackvault.com/documents/afhistory/norad/%28U%29%201963%20NORAD%20CONAD%20History%20Jan-Jun.pdf"
SHA256 = "0ee50f207563618f98173d61be9bcc1db1b0a2afa83978ec9d6ee797a5d806f6"
BYTES = 12_218_228
PAGES = 107
EXPECTED_EVENTS = {
    "1963-01-09": "PLAN_REVIEW",
    "1963-02-12": "REQUEST_REVIEW",
    "1963-03-19": "NORAD_RESPONSE",
    "1963-05-09": "CAPABILITIES_ANALYSIS_SUBMITTED",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("NORAD-JANJUN-C241-L57: " + reason)


def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for k, value in pairs:
        require(k not in result, "duplicate JSON key: " + k)
        result[k] = value
    return result


def read_manifest(path: Path = MANIFEST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


def audit(manifest: dict) -> dict:
    require(type(manifest) is dict and set(manifest) == {
        "schema", "evidence_id", "source", "events", "cold_lake",
        "independence", "individual_527_528_529_observations_recovered",
        "norad_528_observation_utc", "norad_528_observation_station",
        "norad_528_sigma", "terminal_event_utc", "orbital_parameters",
        "physical_constraint_active", "next_acquisition",
    }, "manifest schema")
    require(manifest["schema"] == "conde.norad-1963-janjun-cold-lake/v1"
            and manifest["evidence_id"] == "C241-L57", "source identity")
    source = manifest["source"]
    require(type(source) is dict and set(source) == {
        "title", "reporting_period", "publication_date", "source_owner",
        "official_archive_index", "accessed_pdf_url", "pdf_bytes", "pdf_sha256",
        "pdf_pages", "printed_pages", "pdf_page_indices_zero_based",
        "page_mapping_status", "reading_status", "retrieval_date", "source_class"
    }, "source fields")
    require(source["accessed_pdf_url"] == PDF_URL
            and source["pdf_bytes"] == BYTES and source["pdf_sha256"] == SHA256
            and source["pdf_pages"] == PAGES, "source bytes or URL changed")
    require(source["publication_date"] == "1963-11-01"
            and source["reporting_period"] == "1963-01-01/1963-06-30",
            "editorial date mistaken for instrument epoch")
    require(source["printed_pages"] == [33, 34]
            and source["pdf_page_indices_zero_based"] == [47, 48]
            and source["page_mapping_status"] == "INFERRED_FROM_ADJACENT_RENDER_P35_INDEX49"
            and source["reading_status"] == "INDEXED_TEXT_TARGET_PAGES_VISUAL_PENDING",
            "unverified page promoted into fully visual proof")
    require(source["source_class"] == "CONTEMPORARY_INSTITUTIONAL_HISTORY_NOT_SENSOR_LOG",
            "history promoted into a sensor log")
    require(type(manifest["events"]) is list
            and len(manifest["events"]) == len(EXPECTED_EVENTS),
            "event count")
    observed = {}
    for event in manifest["events"]:
        require(type(event) is dict and set(event) == {
            "date", "kind", "claim", "instrumental_observation"
        }, "event fields")
        require(type(event["claim"]) is str and len(event["claim"]) >= 35,
                "claim description")
        require(event["date"] in EXPECTED_EVENTS
                and event["kind"] == EXPECTED_EVENTS[event["date"]]
                and event["date"] not in observed, "event chronology or duplication")
        require(event["instrumental_observation"] is False,
                "institutional planning became an orbital measurement")
        observed[event["date"]] = True
    require(set(observed) == set(EXPECTED_EVENTS), "event missing")
    station = manifest["cold_lake"]
    require(type(station) is dict and set(station) == {
        "camera", "operator", "place", "statement", "exact_effective_date",
        "station_operation_claim", "report_for_528", "spadats_528_receipt",
        "caveat"
    }, "station fields")
    require(station["camera"] == "Baker-Nunn"
            and station["operator"] == "Royal Canadian Air Force (RCAF)"
            and station["place"] == "Cold Lake, Alberta, Canada",
            "RCAF Cold Lake confused with NASA/SAO or PARL")
    require(station["station_operation_claim"] is True
            and station["exact_effective_date"] is None
            and station["report_for_528"] is None
            and station["spadats_528_receipt"] is None,
            "camera control promoted to dated 528 observation/receipt")
    require("not proof" in station["caveat"].lower(), "limit caveat missing")
    require("not an automatically independent" in manifest["independence"],
            "false independence from related NORAD/RCAF reporting")
    require(type(manifest["individual_527_528_529_observations_recovered"]) is int
            and manifest["individual_527_528_529_observations_recovered"] == 0,
            "invented measurement count")
    for key in ("norad_528_observation_utc", "norad_528_observation_station",
                "norad_528_sigma", "terminal_event_utc", "orbital_parameters"):
        require(manifest[key] is None, "invented 528 physics: " + key)
    require(manifest["physical_constraint_active"] is False, "premature physical activation")
    require(type(manifest["next_acquisition"]) is str
            and "box 72" in manifest["next_acquisition"]
            and "NORAD 528" in manifest["next_acquisition"],
            "missing targeted archival search")
    return {"id": "C241-L57", "institutional_events": len(observed),
            "individual_observations": 0, "physical_constraints": 0,
            "target_page_visual_review": "PENDING"}


def verify_pdf(data: bytes) -> dict:
    require(len(data) == BYTES, "PDF length changed; do not silently accept")
    require(hashlib.sha256(data).hexdigest() == SHA256, "PDF hash changed")
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data), strict=True)
    require(len(reader.pages) == PAGES, "PDF pagination differs")
    require(not reader.is_encrypted, "source unexpectedly encrypted")
    return {"pdf_sha256": SHA256, "pdf_bytes": BYTES, "pages": PAGES,
            "target_page_visual_review": "PENDING"}


def download_pdf() -> bytes:
    req = Request(PDF_URL, headers={"User-Agent": "Conde1963-Research-Custody/1.0"})
    with urlopen(req, timeout=55) as response:
        result = response.read(BYTES + 1)
    require(len(result) <= BYTES, "PDF exceeds expected length")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group()
    group.add_argument("--pdf", type=Path)
    group.add_argument("--live", action="store_true")
    args = p.parse_args()
    summary = audit(read_manifest())
    if args.pdf or args.live:
        summary["pdf"] = verify_pdf(args.pdf.read_bytes() if args.pdf else download_pdf())
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
