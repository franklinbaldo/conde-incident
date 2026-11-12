#!/usr/bin/env python3
"""Offline integrity and structure check for Wayback-preserved NMC ON20 PDF."""
import argparse
import hashlib
import json
import re
from pathlib import Path

MANIFEST = (Path(__file__).resolve().parents[1] /
            "research/meteorology/ncep_on20_wayback_custody_20261112.json")


def check_manifest(record):
    if record["epistemic_status"] != "PDF_BYTES_RETRIEVED_CONTENT_NOT_YET_TRANSCRIBED":
        raise ValueError("content-reading state unverified")
    if record["applicability_to_1963"] != "NOT_ESTABLISHED":
        raise ValueError("compatibility with 1963 cannot be asserted")
    if record["tape_decoded"] is not False or record["station_day_matches"] is not None:
        raise ValueError("source cannot create station/day records")
    if record["physical_constraint"] != "NOT_ACTIVATED":
        raise ValueError("physical constraint activated by documentation alone")


def verify_pdf(raw, record):
    expected = record["preservation"]
    if len(raw) != expected["byte_length"]:
        raise ValueError("wrong byte length")
    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected["sha256"]:
        raise ValueError("SHA256 mismatch")
    if not raw.startswith(expected["pdf_header"].encode("ascii")):
        raise ValueError("not PDF header")
    if not raw.rstrip().endswith(b"%%EOF"):
        raise ValueError("no PDF EOF")
    if not re.search(rb"/Root\s+\d+\s+\d+\s+R", raw):
        raise ValueError("no PDF catalog root")
    pages = len(re.findall(rb"/Type\s*/Page\b", raw))
    images = len(re.findall(rb"/Subtype\s*/Image\b", raw))
    if pages != expected["page_object_count"] or images != expected["image_object_count"]:
        raise ValueError("wrong PDF object counts")
    if not re.search(rb"/Count\s+" + str(expected["page_tree_count_marker"]).encode() + rb"\b", raw):
        raise ValueError("page tree count marker missing")
    return {"status": "PDF_BYTES_AND_STRUCTURAL_MARKERS_VERIFIED", "sha256": sha,
            "bytes": len(raw), "page_objects": pages, "image_objects": images,
            "visual_pages_read": False, "on20_decoded": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    args = ap.parse_args()
    record = json.loads(args.manifest.read_text(encoding="utf-8"))
    check_manifest(record)
    print(json.dumps(verify_pdf(args.pdf.read_bytes(), record), indent=2))


if __name__ == "__main__":
    main()
