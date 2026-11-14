#!/usr/bin/env python3
"""C241-L45: authenticate RU478 original PDF and guard against a false 528 observation."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/sao_ru478_finding_aid_C241-L45.json"
CROSSWALK = ROOT / "research/constraints/morcego_sao_ru478_1963_crosswalk.json"
URL = "https://sirismm.si.edu/EADpdfs/SIA.FARU0478.pdf"
SHA = "e4f2b29b9882cdfac1812b41251b087354e311822d7302e4655a89bc4a06c07e"
SIZE = 118909
LOCATORS = (
    ("RU478-WEATHER-1963", 1, 3, 4, "Iran #9008, 1966, 1965, 1964, 1963"),
    ("RU478-AF-NORAD", 4, 5, 6, "Air Force - NORAD"),
    ("RU478-MONTHLY-REPORTS", 59, 24, 25, "Baker-Nunn Observation Monthly Reports, 1961-1968"),
    ("RU478-TAPE-12546", 65, 25, 26, "12546 All Photo-Reduced Observations through 1974"),
)

def fail_if(condition: bool, message: str) -> None:
    if condition:
        raise ValueError(message)

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def audit(model: dict, crosswalk: dict) -> dict:
    fail_if(model.get("id") != "C241-L45", "wrong C241 ID")
    fail_if(model.get("schema") != "conde.sao-ru478-finding-aid-custody/v1", "wrong schema")
    s = model["source"]
    fail_if(s["url"] != URL or s["sha256"] != SHA or s["bytes"] != SIZE,
            "unverified source, URL, digest or size")
    fail_if((s["pdf_pages"], s["printed_pages"]) != (30, 28), "wrong page offsets")
    fail_if(s["source_class"] != "OFFICIAL_FINDING_AID_NOT_INSTRUMENTAL_LOG",
            "source class promoted")
    fail_if(s["relation_to_existing"] != CROSSWALK.relative_to(ROOT).as_posix(),
            "crosswalk identity drift")
    matched_sources = [src for src in crosswalk["sources"] if src.get("id") == "RU478"]
    fail_if(len(matched_sources) != 1 or matched_sources[0]["url"] != URL,
            "upstream Morcego crosswalk mismatch")
    fail_if(matched_sources[0]["grade"] != "primary_for_archive_holdings_only",
            "archive catalog falsely upgraded")
    anchors = model["anchors"]
    fail_if(len(anchors) != len(LOCATORS), "archive locators dropped or fabricated")
    for item, (id_, box, printed, page, phrase) in zip(anchors, LOCATORS):
        fail_if((item["id"], item["box"], item["printed_page"],
                 item["pdf_page_index_zero_based"], item["phrase"]) !=
                (id_, box, printed, page, phrase), "archive locator altered: " + id_)
        fail_if(not item["fact"] or "opened" not in item["fact"] and
                "unverified" not in item["fact"] and "inspected" not in item["fact"],
                "archival finding presented as instrument: " + id_)
    fail_if(model["object_ids_not_printed_in_these_anchors"] != [527, 528, 529],
            "invented satellite linkage")
    for k in ("individual_observation_utc", "station_for_target_528",
              "observation_angles_for_target_528", "target_528_sensor_sigma"):
        fail_if(model[k] is not None, "fabricated physical observation: " + k)
    fail_if(model["independent_instrumental_observations_recovered"] != 0,
            "unverified observation claimed")
    fail_if(model["physical_constraints_activated"] != 0, "premature physical activation")
    fail_if(model["impact_at_conde"] != "NOT_ESTABLISHED", "impact asserted")
    fail_if(model["derived_from_same_sao_program"] is not True,
            "fabricated independent source")
    fail_if(model["inference"] != "ARCHIVE_HOLDING_ONLY_NOT_528_DETECTION_OR_NONDETECTION",
            "global detection/non-detection conclusion")
    return {"evidence": model["id"], "locators": len(LOCATORS),
            "verified_528_measurements": 0, "physical_constraints": 0}

def live_check(pdf: bytes) -> dict:
    fail_if(len(pdf) != SIZE or hashlib.sha256(pdf).hexdigest() != SHA,
            "original RU478 PDF changed: stop, investigate, do not overwrite digest")
    from pypdf import PdfReader

    pages = PdfReader(io.BytesIO(pdf)).pages
    fail_if(len(pages) != 30, "RU478 PDF page count changed")
    for id_, _, printed, index, phrase in LOCATORS:
        txt = re.sub(r"\s+", " ", pages[index].extract_text() or "")
        # Check source words in page sequence, not a mere PDF file hash.
        parts = phrase.split()
        cursor = 0
        for part in parts:
            cursor = txt.find(part, cursor)
            fail_if(cursor < 0, "missing source text in PDF page: " + id_)
            cursor += len(part)
        fail_if(f"Page {printed} of 28" not in txt, "wrong printed PDF page: " + id_)
    return {"pdf_sha256": SHA, "pdf_bytes": SIZE, "pdf_pages": len(pages),
            "archive_locators_rechecked": len(LOCATORS)}

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--pdf", type=Path, help="Verify an already downloaded original without network")
    args = p.parse_args()
    result = audit(read_json(LEDGER), read_json(CROSSWALK))
    if args.live or args.pdf:
        if args.pdf:
            pdf = args.pdf.read_bytes()
        else:
            with urlopen(Request(URL, headers={"User-Agent": "Conde1963-RU478-Custody/1.0"}),
                         timeout=45) as response:
                pdf = response.read(SIZE + 1)
        result["pdf"] = live_check(pdf)
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
