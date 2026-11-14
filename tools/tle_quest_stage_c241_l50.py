#!/usr/bin/env python3
"""C241-L50: enforce source integrity and prevent group-stage labels becoming 528 observations."""
import argparse
import hashlib
import json
import pathlib
import urllib.request

LEDGER = pathlib.Path(__file__).resolve().parents[1] / "research/tle_custody/quest_stage_C241-L50.json"
URL = "https://planet4589.org/jcm/pubs/space/papers/1995/Quest95b.pdf"
SHA = "9dec4037537ea648a41501381c62d0f6eadfbd4fad807d27eb1fd7f748eb1ed1"
EXPECTED_ROWS = [
    {"ferret": 2, "vehicle": "2312", "date": "1962 Jun 18", "stage": "Thor Agena B"},
    {"ferret": 3, "vehicle": "2313", "date": "1963 Jan 16", "stage": "Thor Agena D",
     "orbit_as_printed": "459 x 533 x 81.9", "period_as_printed": "94.7"},
    {"ferret": 4, "vehicle": "2314", "date": "1963 Jun 29", "stage": "TAT Agena B"},
]
EXPECTED_COMPARISON = {
    "nasa_sp4004_1964": "D, group 1963-3, page 502, C241-L15",
    "nsa_1975": "D, 7153/2313, indexed text pending facsimile",
    "modern_gunter": "B, 2313, modern secondary catalog",
    "source_independence": "editorial publication; independent instrumental origin not established",
}
EXPECTED_SOURCE = {
    "author": "Jonathan McDowell",
    "title": "U.S. Reconnaissance Satellite Programs, Part 2: Beyond Imaging",
    "publication": "Quest vol. 4 no. 4 (1995)",
    "url": URL, "bytes": 14469995, "sha256": SHA,
    "pages": 7, "pdf_page_index_zero_based": 1, "printed_page": 40,
    "text_layer_characters": 0,
    "inspection": "Full PDF downloaded and hashed; page 40 visually read in raster crop, not OCR.",
}
EXPECTED_TARGET = {"designator": "1963-003B", "individual_row": False,
                   "observation_utc": None, "station": None, "frame": None,
                   "sigma": None, "object_hardware": None, "decay_hour": None,
                   "impact_location": None}
NEXT = "Find engineering record for Agena 2313 B/D and raw 1963-003B observation with UTC, station, frame and uncertainty."


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key " + key)
        obj[key] = value
    return obj


def load(path=LEDGER):
    return json.loads(pathlib.Path(path).read_text("utf-8"), object_pairs_hook=unique_keys)


def audit(data):
    expected_keys = {"schema", "evidence_id", "status", "physical_constraint_active",
                     "source", "rows", "comparison", "norad528",
                     "status_of_orbital_parameters", "next_test"}
    if set(data) != expected_keys:
        raise ValueError("schema drift")
    if data["schema"] != "c241-l50-quest-stage-v1" or data["evidence_id"] != "C241-L50":
        raise ValueError("identity drift")
    if data["status"] != "RETROSPECTIVE_EDITORIAL_NO_INSTRUMENTAL_MEASUREMENT":
        raise ValueError("editorial source promoted to telemetry")
    if data["physical_constraint_active"] is not False:
        raise ValueError("premature physical inference")
    if data["source"] != EXPECTED_SOURCE:
        raise ValueError("source custody or visual scope drift")
    if data["rows"] != EXPECTED_ROWS:
        raise ValueError("facsimile cell or controls drift")
    if data["comparison"] != EXPECTED_COMPARISON:
        raise ValueError("cross-source conflict or independence drift")
    if data["norad528"] != EXPECTED_TARGET:
        raise ValueError("unobserved NORAD 528 hardware/telemetry invented")
    if data["status_of_orbital_parameters"] != "THETA_UNCHANGED" or data["next_test"] != NEXT:
        raise ValueError("future evidence represented as present")
    return True


def verify_pdf(data, content):
    if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-1024:]:
        raise ValueError("truncated or invalid original PDF")
    if len(content) != data["source"]["bytes"] or hashlib.sha256(content).hexdigest() != data["source"]["sha256"]:
        raise ValueError("PDF hash or size differs from reviewed snapshot")
    from io import BytesIO
    from pypdf import PdfReader
    doc = PdfReader(BytesIO(content))
    if len(doc.pages) != data["source"]["pages"]:
        raise ValueError("page count drift")
    if sum(len(p.extract_text() or "") for p in doc.pages) != data["source"]["text_layer_characters"]:
        raise ValueError("scan/text-layer drift")
    return True


def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--source-file", type=pathlib.Path)
    g.add_argument("--verify-remote", action="store_true")
    args = parser.parse_args()
    data = load()
    audit(data)
    if args.source_file:
        verify_pdf(data, args.source_file.read_bytes())
    if args.verify_remote:
        with urllib.request.urlopen(urllib.request.Request(URL,
                       headers={"User-Agent": "Conde-C241-L50/1.0"}), timeout=80) as r:
            verify_pdf(data, r.read())
    print("C241-L50 PASS: editorial stage conflict; no new NORAD 528 telemetry")

if __name__ == "__main__":
    main()
