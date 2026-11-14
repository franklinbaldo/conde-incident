#!/usr/bin/env python3
"""C241-L51: pin original NSA/NRO PDFs; reject invented 528 hardware or telemetry."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[1]
LEDGER = BASE / "research/tle_custody/declassified_facsimiles_C241-L51.json"

EXPECTED = [
    {
        "id": "NSA-BYE-19385-75", "title": "NSA in Space", "authored_year": 1975,
        "release_date": "2017-11-08",
        "url": "https://www.governmentattic.org/26docs/NSAinSpaceViaNRO_1975.pdf",
        "filename": "NSAinSpaceViaNRO_1975.pdf", "bytes": 4853647,
        "sha256": "3d5d7a22608d3eb9ab23f61f46da924708d471917f77ee5f3a68ae8910aeab74",
        "pdf_pages": 248, "pdf_page_1_based": 132, "printed_page": 5,
        "printed_page_section": "Appendix A payload summary, not main text page 5",
        "readout": {"mission": "7153", "payload": "698 BK IV", "vehicle": "2313",
                    "launch_vehicle": "Thor-Agena D", "date_as_printed": "16 Jan 63"},
        "class": "RETROSPECTIVE_ADMINISTRATIVE_TABLE_VISUALLY_CHECKED"
    },
    {
        "id": "NRO-SIGINT-STORY-1994", "title": "The SIGINT Satellite Story",
        "authored_year": 1994, "release_date": None,
        "url": "https://www.governmentattic.org/19docs/NRO-SIGINTsatStory_1994u.pdf",
        "filename": "NRO-SIGINTsatStory_1994u.pdf", "bytes": 14454222,
        "sha256": "1bffa3e121073c8a312c9f67393efac09aa0a322e18ce039e592df0454e13c8a",
        "pdf_pages": 430, "pdf_page_1_based": 123, "printed_page": 90,
        "printed_page_section": "History narrative on vehicle 2313 and adjacent 2314",
        "readout": {
            "mission": "7153", "vehicle": "2313",
            "date_as_printed": "16 January 1963",
            "launch_vehicle_wording": "using a Thor",
            "mission_duration_wording": "only two days due to a battery failure",
            "next_vehicle": "2314",
            "next_booster_wording": "launched on 29 June 1963 using a TAT booster"
        },
        "class": "RETROSPECTIVE_MISSION_HISTORY_VISUALLY_CHECKED"
    }
]
CONFLICT = {
    "nsa_1975_vehicle_2313": "Agena D",
    "nasa_1964_launch_group_1963_3": "Agena D (C241-L15, not object-specific)",
    "quest_1995_2313": "Agena D (C241-L50, editorial)",
    "modern_gunter_2313": "Agena B (secondary catalog)",
    "nro_1994_2313": "Thor only; no Agena variant given on inspected page",
    "result": "UNRESOLVED_HARDWARE_VARIANT", "same_observation_family_claim": False
}
TARGET = {
    "catalog_identifier": "1963-003B/NORAD 528 (linked by C241-L32, not printed here)",
    "hardware_identity": None, "observation_utc": None, "station": None,
    "frame": None, "sigma": None, "decay_hour": None, "impact_location": None
}
NEXT = "Acquire contemporaneous 2313 stage engineering record and SPADATS/SAO measurements of 528 with UTC/station/frame/error."


def unique_keys(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError("duplicate JSON key: " + k)
        obj[k] = v
    return obj


def load(path=LEDGER):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_keys)


def audit(data):
    if not isinstance(data, dict) or set(data) != {
        "schema", "evidence_id", "status", "physical_constraint_active", "documents",
        "conflict", "norad528", "orbital_parameters", "next_test"
    }:
        raise ValueError("manifest schema drift")
    if data["schema"] != "c241-l51-declassified-facsimiles-v1" or data["evidence_id"] != "C241-L51":
        raise ValueError("evidence identity drift")
    if data["status"] != "RETROSPECTIVE_DOCUMENTARY_ONLY" or data["physical_constraint_active"] is not False:
        raise ValueError("retrospective history promoted to physical constraint")
    if data["documents"] != EXPECTED:
        raise ValueError("document hashes, page addresses or visually checked rows drift")
    if data["conflict"] != CONFLICT:
        raise ValueError("stage variant wrongly resolved or asserted independent")
    if data["norad528"] != TARGET:
        raise ValueError("NORAD 528 observations or hardware invented")
    if data["orbital_parameters"] != "THETA_UNCHANGED" or data["next_test"] != NEXT:
        raise ValueError("future evidence represented as recovered")
    return True


def verify_file(document, file_path, full_pdf=False):
    file_path = Path(file_path)
    digest = hashlib.sha256()
    total = 0
    start = b""
    tail = b""
    with file_path.open("rb") as f:
        while chunk := f.read(1 << 16):
            if not start:
                start = chunk[:8]
            tail = (tail + chunk)[-1024:]
            total += len(chunk)
            digest.update(chunk)
    if not start.startswith(b"%PDF-") or b"%%EOF" not in tail:
        raise ValueError("invalid or truncated PDF bytes")
    if total != document["bytes"] or digest.hexdigest() != document["sha256"]:
        raise ValueError("original PDF byte identity differs from reviewed snapshot")
    if full_pdf:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path), strict=True)
        if len(reader.pages) != document["pdf_pages"]:
            raise ValueError("PDF pagination differs from reviewed snapshot")
    return True


def verify_sources(data, source_dir, full_pdf=False):
    for doc in data["documents"]:
        verify_file(doc, Path(source_dir) / doc["filename"], full_pdf=full_pdf)
    return True


def download_sources(data, folder):
    for doc in data["documents"]:
        req = Request(doc["url"], headers={"User-Agent": "Conde-C241-L51-provenance/1.0"})
        with urlopen(req, timeout=90) as response, (Path(folder) / doc["filename"]).open("wb") as out:
            if response.status != 200:
                raise ValueError("upstream did not return full PDF")
            shutil.copyfileobj(response, out, 1 << 16)


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group()
    g.add_argument("--source-dir", type=Path)
    g.add_argument("--verify-remote", action="store_true")
    p.add_argument("--full-pdf", action="store_true", help="verify page count with pypdf")
    args = p.parse_args()
    data = load()
    audit(data)
    if args.source_dir:
        verify_sources(data, args.source_dir, full_pdf=args.full_pdf)
    elif args.verify_remote:
        with tempfile.TemporaryDirectory(prefix="c241-l51-") as tmp:
            download_sources(data, tmp)
            verify_sources(data, tmp, full_pdf=args.full_pdf)
    print("C241-L51 PASS: PDFs pinned; Agena B/D unresolved; no NORAD 528 measurements")

if __name__ == "__main__":
    main()
