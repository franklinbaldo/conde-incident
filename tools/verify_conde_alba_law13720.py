#!/usr/bin/env python3
"""Check ALBA 2017 law facsimile custody and 2017-only reciprocal endpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MANIFEST = (Path(__file__).resolve().parents[1] /
            "research/archive/conde_alba_law13720_custody_20261113.json")
SOURCE = ("https://ftp.sei.ba.gov.br/Geoinformacao/leis/lim_mun/aprov/"
          "lei-no-13720-de-27-de-abril-de-2017.pdf")
SHA256 = "76134441592ebc234dbd3856560ed6375f956f8e126c8ecced5244b9a38d89d9"
ANCHORS = {
    "salobrinho": ("-11°39'45,89\"", "-37°44'50,27\""),
    "itapicuru_atlantic": ("-11°44'27,80\"", "-37°30'40,44\""),
    "inhambupe_atlantic": ("-12°05'54,08\"", "-37°41'09,25\""),
    "mangues_itapicuru": ("-11°44'16,86\"", "-37°48'44,48\""),
}
EDGES = (
    ("Jandaira", "I", "salobrinho", "itapicuru_atlantic"),
    ("Oceano Atlantico", "II", "itapicuru_atlantic", "inhambupe_atlantic"),
    ("Esplanada", "III", "inhambupe_atlantic", "mangues_itapicuru"),
    ("Rio Real", "IV", "mangues_itapicuru", "salobrinho"),
)
REVERSE = {"Jandaira": "15-IV", "Esplanada": "11-III", "Rio Real": "20-IV"}


def validate(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "conde.alba-legal-facsimile/v1":
        errors.append("schema")
    if doc.get("document_id") != "CGEO-ALBA-L13720-2017-01":
        errors.append("document identity")
    for key, expected in {
        "original_url": SOURCE, "law_number": "13.720",
        "signed_date": "2017-04-27", "publication_date": "2017-04-28",
        "publication_issue": "22.166",
    }.items():
        if doc.get(key) != expected:
            errors.append("source " + key)
    custody = doc.get("custody") or {}
    for key, expected in {
        "bytes": 354121, "sha256": SHA256, "mime_or_magic": "%PDF-1.6",
        "pdf_eof": True, "pdf_leaf_page_count": 11,
        "visual_inspection": "PRINTED_PAGES_9_10", "archive_url": None,
    }.items():
        if custody.get(key, object()) != expected:
            errors.append("custody " + key)
    cite = doc.get("cite") or {}
    if (cite.get("pdf_page_indices_zero_based") != [3, 4]
            or cite.get("printed_pages") != [9, 10]
            or cite.get("law") != "art. 1, par. 8, incisos I-IV"):
        errors.append("law citation pagination")
    anchors = doc.get("boundary_anchors_2017") or []
    if len(anchors) != 4 or len({p.get("id") for p in anchors}) != 4:
        errors.append("four anchor identities")
    for p in anchors:
        key = p.get("id")
        if key not in ANCHORS or (p.get("lat_dms"), p.get("lon_dms")) != ANCHORS.get(key):
            errors.append("coordinate anchor " + str(key))
    sides = doc.get("boundary_cycle_2017") or []
    actual = tuple((e.get("neighbor"), e.get("inciso"), e.get("from"), e.get("to"))
                   for e in sides)
    if actual != EDGES:
        errors.append("2017 boundary order and pinned endpoints")
    for idx in range(len(sides)):
        if sides[idx].get("to") != sides[(idx + 1) % len(sides)].get("from"):
            errors.append("2017 endpoint cycle disconnected")
    reverse = doc.get("reciprocal_references_2017") or []
    if len(reverse) != 3 or {r.get("neighbor") for r in reverse} != set(REVERSE):
        errors.append("reciprocal source coverage")
    for r in reverse:
        side = next((s for s in sides if s.get("neighbor") == r.get("neighbor")), {})
        if (r.get("section") != REVERSE.get(r.get("neighbor"))
                or r.get("from") != side.get("to")
                or r.get("to") != side.get("from")):
            errors.append("reciprocal end point " + str(r.get("neighbor")))
    genealogy = doc.get("legal_genealogy") or {}
    if (genealogy.get("reference_law") != "BA 628/1953"
            or genealogy.get("reference_status") != "RETROSPECTIVE_LEGAL_REFERENCE_IN_2017"
            or genealogy.get("temporal_conclusion") != "2017_VIGENCY_ONLY"):
        errors.append("genealogy cannot prove continuity")
    for key in ("recovered_1953_facsimile", "recovered_1953_annexes",
                "checked_intervening_acts_1954_1963"):
        if genealogy.get(key) is not False:
            errors.append("unverified 1953 material " + key)
    epi = doc.get("epistemology") or {}
    if epi.get("official_2017_legislative_facsimile") is not True:
        errors.append("official law citation")
    for key in ("independent_1963_boundary_survey", "1963_legal_boundary_demonstrated",
                "law_2017_coordinates_are_1963_observations",
                "orbital_constraint_activated", "precise_1963_coordinates_established"):
        if epi.get(key) is not False:
            errors.append("forbidden backdating " + key)
    if "CGEO-SEI-MAP-2017-01" not in doc.get("dependencies", []):
        errors.append("missing map dependency")
    return errors


def verify_bytes(payload: bytes, doc: dict) -> list[str]:
    """Verify an independently supplied PDF, not a derivative or web index."""
    custody = doc["custody"]
    errors = []
    if len(payload) != custody["bytes"]:
        errors.append("PDF byte length")
    if hashlib.sha256(payload).hexdigest() != custody["sha256"]:
        errors.append("PDF SHA-256")
    if not payload.startswith(b"%PDF-1.6"):
        errors.append("PDF magic")
    if b"%%EOF" not in payload[-1024:]:
        errors.append("PDF EOF")
    # This source is a subset of a Diário Oficial issue containing other laws.
    if len(re.findall(rb"/Type\s*/Page\b", payload)) != custody["pdf_leaf_page_count"]:
        errors.append("PDF leaf page count")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pdf", type=Path, help="optional downloaded primary PDF")
    args = parser.parse_args()
    doc = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(doc)
    if args.pdf:
        errors.extend(verify_bytes(args.pdf.read_bytes(), doc))
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: 2017 ALBA legislative provenance and reciprocal end points"
          + (" + official PDF byte replay" if args.pdf else
             " (PDF byte replay NOT_RUN)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
