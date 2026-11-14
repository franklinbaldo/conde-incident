#!/usr/bin/env python3
"""Immutable RU263 box-72 addendum: archive folders, not orbital measurements."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/ru263_cold_lake_box72_addendum_C241-L53.json"
URL = "https://sirismm.si.edu/EADpdfs/SIA.FARU0263.pdf"
PDF_SHA = "0648a4807160099c1c5146f9a90e8ab291af8cb7a0eff1f5a9ca0bc53e074603"
BASE_SHA = "40bbfda2f2440bae8344f9b42177622e1c3d7eee6aed34560f69e203b01cc473"
BASE = "research/tle_custody/sao_ru263_station_files_C241-L53.json"
EXPECTED = (
    ("RU263-COLD-LAKE-S9-OPERATIONS", 9, 72, 47, 48, "#420 Operations, 1963-1965."),
    ("RU263-COLD-LAKE-S9-INVENTORY", 9, 72, 47, 48, "#130 Inventory and audits, 1963."),
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("RU263-BOX72: " + message)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key " + key)
        out[key] = value
    return out


def read_model(path: Path = LEDGER) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def audit(model: dict, root: Path = ROOT) -> dict:
    require(set(model) == {
        "schema", "id", "amendment", "parent_manifest_path", "parent_manifest_sha256",
        "source_pdf_sha256", "source_pdf_bytes", "anchors",
        "independent_instrumental_observations", "individual_observations_recovered",
        "norad_528_observation_utc", "spadats_528_transfer_receipt",
        "physical_constraint_active", "next_acquisition",
    }, "top-level fields differ")
    require(model["schema"] == "conde.ru263-station-file-addendum/v1"
            and model["id"] == "C241-L53" and model["amendment"] == "C241-L54",
            "parent source identity or amendment")
    require(model["parent_manifest_path"] == BASE
            and model["parent_manifest_sha256"] == BASE_SHA, "parent ledger provenance")
    require(hashlib.sha256((root / BASE).read_bytes()).hexdigest() == BASE_SHA,
            "parent ledger bytes drift")
    require(model["source_pdf_sha256"] == PDF_SHA
            and model["source_pdf_bytes"] == 192142, "PDF variant drift")
    anchors = model["anchors"]
    require(type(anchors) is list and len(anchors) == len(EXPECTED),
            "must contain precisely two folders")
    for item, expected in zip(anchors, EXPECTED):
        require(type(item) is dict and set(item) == {
            "id", "series", "box", "printed_page", "pdf_page_index_zero_based",
            "phrase", "scope",
        }, "folder structure")
        require(tuple(item[k] for k in (
            "id", "series", "box", "printed_page",
            "pdf_page_index_zero_based", "phrase")) == expected, "folder locator")
        require("not " in item["scope"].lower(), "unqualified observation inference")
    require(model["independent_instrumental_observations"] == 0
            and model["individual_observations_recovered"] == 0
            and model["norad_528_observation_utc"] is None
            and model["spadats_528_transfer_receipt"] is None
            and model["physical_constraint_active"] is False,
            "finding aid promoted into measurement/receipt or activation")
    require(type(model["next_acquisition"]) is str
            and "box 72" in model["next_acquisition"], "acquisition incomplete")
    return {"evidence_id": "C241-L53", "additional_folders": 2,
            "physical_constraints": 0}


def verify_pdf(pdf: bytes) -> dict:
    require(len(pdf) == 192142 and hashlib.sha256(pdf).hexdigest() == PDF_SHA,
            "changed PDF bytes; do not auto-update hash")
    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(pdf)).pages
    require(len(pages) == 58, "page count")
    text = re.sub(r"\s+", " ", pages[48].extract_text() or "")
    require("Page 47 of 56" in text, "printed/PDF page offset")
    start = text.find("Cold Lake, Canada")
    end = text.find("Curacao", start)
    require(start >= 0 and end > start, "station subsection delimitation")
    section = text[start:end]
    for record in EXPECTED:
        require(record[-1] in section, "folder is not under Cold Lake: " + record[0])
    return {"bytes": len(pdf), "sha256": PDF_SHA, "pdf_pages": len(pages),
            "checked_folders": len(EXPECTED)}


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pdf", type=Path)
    mode.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = audit(read_model())
    if args.live or args.pdf:
        if args.pdf:
            data = args.pdf.read_bytes()
        else:
            with urlopen(Request(URL, headers={"User-Agent": "Conde1963-RU263-Box72/1.0"}),
                         timeout=45) as response:
                data = response.read(192143)
        result["pdf"] = verify_pdf(data)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
