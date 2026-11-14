#!/usr/bin/env python3
"""C241-L53: independently authenticate RU263 finding aid and block false orbital inference."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/sao_ru263_station_files_C241-L53.json"
URL = "https://sirismm.si.edu/EADpdfs/SIA.FARU0263.pdf"
SHA = "0648a4807160099c1c5146f9a90e8ab291af8cb7a0eff1f5a9ca0bc53e074603"
SIZE = 192142
LOCATORS = (
    ("RU263-COLD-LAKE-OPERATIONS", 2, 36, 14, 15, "Cold Lake, Canada, 1963-1965"),
    ("RU263-COLD-LAKE-ENGINEERING", 8, 67, 43, 44, "Cold Lake, Canada, 1961-1963"),
    ("RU263-IRAN-ENGINEERING", 8, 69, 43, 44, "Iran, 1959-1963"),
    ("RU263-CURACAO-ENGINEERING", 8, 68, 43, 44, "Curacao, 1959-1963"),
    ("RU263-COLD-LAKE-S9-OPERATIONS", 9, 72, 47, 48, "#420 Operations, 1963-1965."),
    ("RU263-COLD-LAKE-S9-INVENTORY", 9, 72, 47, 48, "#130 Inventory and audits, 1963."),
)

def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result

def read_model(path: Path = LEDGER) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)

def audit(model: dict) -> dict:
    check(model.get("schema") == "conde.sao-ru263-station-records-custody/v1", "schema drift")
    check(model.get("id") == "C241-L53", "evidence ID drift")
    check(set(model) == {
        "schema", "id", "source", "anchors", "related_conde_evidence",
        "cross_collection_independent_observations", "norad_527_observation",
        "norad_528_observation", "norad_529_observation", "norad_528_station",
        "norad_528_utc", "norad_528_sensor_sigma",
        "norad_528_data_received_by_spadats",
        "individual_observations_recovered_from_this_finding_aid",
        "physical_constraints_activated", "impact_at_conde", "inference", "next_acquisition",
    }, "unexpected/missing top-level field")
    src = model["source"]
    check(set(src) == {
        "repository", "creator", "collection", "catalog_url", "url", "sha256",
        "bytes", "pdf_pages", "printed_pages", "boxes_in_collection", "source_class",
    }, "unexpected/missing source field")
    check(src["url"] == URL and src["sha256"] == SHA and src["bytes"] == SIZE,
          "PDF identity modified")
    check(src["repository"] == "Smithsonian Institution Archives", "custodian modified")
    check(src["catalog_url"].endswith("siris_arc_216832"), "catalog identity modified")
    check((src["pdf_pages"], src["printed_pages"], src["boxes_in_collection"]) ==
          (58, 56, 82), "finding aid size/structure modified")
    check(src["source_class"] == "OFFICIAL_FINDING_AID_NOT_INSTRUMENTAL_OBSERVATIONS",
          "archive inventory promoted to instrumental observation")
    check(len(model["anchors"]) == len(LOCATORS), "archive locators dropped/added")
    for item, locator in zip(model["anchors"], LOCATORS):
        check(set(item) == {"id", "series", "box", "printed_page",
                             "pdf_page_index_zero_based", "phrase", "scope"},
              "unexpected/missing archive anchor key")
        actual = tuple(item[k] for k in ("id", "series", "box", "printed_page",
                                          "pdf_page_index_zero_based", "phrase"))
        check(actual == locator, "archive locator mismatch: " + locator[0])
        check("not" in item["scope"].lower() or "no observation" in item["scope"].lower(),
              "archive file reclassified as measurement: " + locator[0])
    check(model["related_conde_evidence"] == ["C241-L43", "C241-L45", "C241-L52"],
          "upstream source bridge changed")
    for key in ("norad_527_observation", "norad_528_observation", "norad_529_observation",
                "norad_528_station", "norad_528_utc", "norad_528_sensor_sigma"):
        check(model[key] is None, "invented observation: " + key)
    check(model["cross_collection_independent_observations"] == "UNKNOWN",
          "independent instruments manufactured")
    check(model["norad_528_data_received_by_spadats"] == "UNKNOWN",
          "data transfer assumed")
    check(model["individual_observations_recovered_from_this_finding_aid"] == 0,
          "finding aid upgraded to individual observations")
    check(model["physical_constraints_activated"] == 0, "false physical constraint")
    check(model["impact_at_conde"] == "NOT_ESTABLISHED", "unsupported location")
    check(model["inference"] == "HOLDINGS_AND_TECHNICAL_FILE_LEADS_ONLY", "unsupported inference")
    return {"id": model["id"], "holdings_located": len(LOCATORS), "observations_recovered": 0}

def live_check(pdf: bytes) -> dict:
    check(len(pdf) == SIZE and hashlib.sha256(pdf).hexdigest() == SHA,
          "RU263 source bytes changed: investigate before changing baseline")
    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(pdf)).pages
    check(len(pages) == 58, "RU263 PDF page count changed")
    for identifier, _, _, printed, pdf_index, phrase in LOCATORS:
        page = re.sub(r"\s+", " ", pages[pdf_index].extract_text() or "")
        check(f"Page {printed} of 56" in page, "wrong page mapping: " + identifier)
        # Whitespace-normalized continuous text is sufficient for a finding-aid label.
        check(phrase in page, "missing locator phrase: " + identifier)
        if identifier.startswith("RU263-COLD-LAKE-S9-"):
            # Bind the label to the Cold Lake subsection, not to another station on page 47.
            start = page.find("Cold Lake, Canada")
            end = page.find("Curacao", start)
            section = page[start:end if end != -1 else None] if start >= 0 else ""
            check(phrase in section, "folder label not under Cold Lake: " + identifier)
    return {"bytes": SIZE, "sha256": SHA, "pdf_pages": len(pages), "anchors_checked": len(LOCATORS)}

def main() -> None:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group()
    group.add_argument("--pdf", type=Path)
    group.add_argument("--live", action="store_true")
    args = p.parse_args()
    result = audit(read_model())
    if args.live or args.pdf:
        if args.pdf:
            payload = args.pdf.read_bytes()
        else:
            with urlopen(Request(URL, headers={"User-Agent": "Conde1963-RU263-Custody/1.0"}),
                         timeout=45) as resp:
                payload = resp.read(SIZE + 1)
        result["pdf_verification"] = live_check(payload)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
