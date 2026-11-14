#!/usr/bin/env python3
"""Audit page-index correction and prevent editorial camera counts becoming 528 data."""
import argparse
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "research/tle_custody/norad_1963_janjun_cold_lake_C241-L57.json"
ADDENDUM = ROOT / "research/tle_custody/norad_1963_janjun_visual_addendum_C241-L58.json"
PARENT_SHA = "4132de53581548fbe867677fdb220668c3a05b400df822b8fa59c880fd756ab8"
PDF_SHA = "0ee50f207563618f98173d61be9bcc1db1b0a2afa83978ec9d6ee797a5d806f6"


def require(condition, error):
    if not condition:
        raise ValueError("C241-L58 " + error)


def unique(pairs):
    result = {}
    for key, val in pairs:
        require(key not in result, "duplicate key")
        result[key] = val
    return result


def audit(m, parent=None):
    require(type(m) is dict and set(m) == {
        "schema", "evidence_id", "parent_id", "parent_sha256", "source",
        "prior_error", "pages", "visual_scope", "inventory", "cold_lake",
        "epistemic", "acquisition",
    }, "schema")
    require((m["schema"], m["evidence_id"], m["parent_id"], m["parent_sha256"]) ==
            ("conde.c241.visual-correction/v1", "C241-L58", "C241-L57", PARENT_SHA),
            "lineage")
    require(hashlib.sha256(PARENT.read_bytes() if parent is None else parent).hexdigest() ==
            PARENT_SHA, "parent bytes were changed")
    src = m["source"]
    require(src == {
        "url": "https://documents.theblackvault.com/documents/afhistory/norad/%28U%29%201963%20NORAD%20CONAD%20History%20Jan-Jun.pdf",
        "sha256": PDF_SHA, "bytes": 12218228, "pdf_pages": 107,
        "publication_date": "1963-11-01", "independent_source": False,
    }, "source not original")
    require(m["prior_error"] == {
        "claimed_printed_pages": [33, 34],
        "claimed_zero_based_indices": [47, 48],
        "status": "OFF_BY_ONE_AND_MISSING_PAGE_35",
    }, "original error lost")
    require(type(m["pages"]) is list and len(m["pages"]) == 3, "page count")
    facts = (
        "USAF five cameras, one to Canada, SAO twelve, total seventeen",
        "January Defence accuracy review, February JCS request, March NORAD response",
        "May NORAD analysis submitted; RCAF Cold Lake under NORAD direct control",
    )
    for i, p in enumerate(m["pages"]):
        require(p == {
            "printed": 33 + i, "pdf_one_based": 47 + i, "pdf_zero_based": 46 + i,
            "fact": facts[i], "visual_checked": True,
        }, "incorrect page mapping or claim")
    require(m["visual_scope"] == "MANUAL_CHECK_OF_PRINTED_PAGES_33_TO_35_NOT_ORBITAL_MEASUREMENT",
            "manual verification misrepresented")
    require(m["inventory"] == {
        "USAF_original": 5, "USAF_to_Canada_mid_1962": 1, "SAO_for_NASA": 12,
        "total_in_existence": 17, "Canada_part_of_original_five": True,
    }, "camera inventory double counted")
    require(m["cold_lake"] == {
        "operator": "RCAF", "control": "NORAD", "claim_printed_page": 35,
        "effective_date": None, "528_exposure_utc": None,
        "528_data_receipt": None, "528_instrument_sigma": None,
    }, "camera control promoted to measurement")
    require(m["epistemic"] == {
        "source_class": "CONTEMPORARY_INSTITUTIONAL_HISTORY",
        "independent_instrumental_observations": 0,
        "active_physical_constraint": False, "528_terminal_utc": None,
        "528_impact_location": None,
    }, "invented independent observations or geography")
    require("box 72" in m["acquisition"] and "NORAD 528" in m["acquisition"],
            "missing targeted acquisition")
    return {"id": "C241-L58", "corrected_pdf_pages": [47, 48, 49],
            "new_instrumental_observations": 0, "physical_constraint": False}


def verify_pdf(raw):
    require(len(raw) == 12218228 and hashlib.sha256(raw).hexdigest() == PDF_SHA,
            "facsimile bytes/hash mismatch")
    from pypdf import PdfReader
    doc = PdfReader(io.BytesIO(raw), strict=True)
    require(len(doc.pages) == 107 and not doc.is_encrypted, "PDF structure")
    return {"pdf_pages": 107, "visual_review": "HUMAN_DOCUMENTED_NOT_AUTOMATED"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path)
    args = p.parse_args()
    m = json.loads(ADDENDUM.read_text(encoding="utf-8"), object_pairs_hook=unique)
    result = audit(m)
    if args.pdf:
        result["pdf"] = verify_pdf(args.pdf.read_bytes())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
