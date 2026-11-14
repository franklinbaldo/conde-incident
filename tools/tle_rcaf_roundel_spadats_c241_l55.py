"""Audit RCAF Roundel September 1963: a network claim is not a 528 tracking datum."""

import argparse
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/rcaf_roundel_spadats_1963_C241-L55.json"
SHA = "830a7707f3ce611172ff6b6942794654b1fc30d564f97e2b7bf78f2c981657b3"
EXPECTED_ANCHORS = (
    ("RCAF_COLD_LAKE_SPADATS", "The RCAF input into SPADATS is from a Baker-Nunn camera installation at RCAF Station Cold Lake.", "PUBLISHED_SYSTEM_LEVEL_OPERATIONAL_ASSERTION"),
    ("DRB_PRINCE_ALBERT", "such as the Canadian Defence Research Board's tracker unit at Prince Albert", "PUBLISHED_NETWORK_DESCRIPTION"),
    ("RCAF_CAMERA_PHOTO", "AC A. Dew and LAC K. Dodds work with a satellite tracking camera.", "ILLUSTRATION_WITH_CAPTION"),
)
NULL_FIELDS = ("norad_528_observation_utc", "norad_528_observation_station", "norad_528_sensor_sigma", "norad_528_transmission_receipt", "norad_528_frame")
ROOT_KEYS = {"schema", "evidence_id", "source", "anchors", "independence", *NULL_FIELDS, "cold_lake_named_observations_recovered", "physical_constraint_active", "orbit_parameters", "impact_at_conde", "related_evidence", "next_acquisition"}
SOURCE_KEYS = {"institution", "periodical", "issue", "publication_date_precision", "url", "retrieval_date", "sha256", "bytes", "pdf_pages", "printed_page", "pdf_page_index_zero_based", "source_class", "scan_pdf_creation_date"}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key}")
        result[key] = value
    return result


def read_model(path=LEDGER):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(doc):
    require(isinstance(doc, dict) and set(doc) == ROOT_KEYS, "ledger keys changed")
    require(doc["schema"] == "conde.c241-l55-rcaf-spadats-custody/v1" and doc["evidence_id"] == "C241-L55", "identity drift")
    s = doc["source"]
    require(isinstance(s, dict) and set(s) == SOURCE_KEYS, "source schema changed")
    expected = {
        "institution": "Royal Canadian Air Force", "periodical": "Roundel", "issue": "September 1963",
        "publication_date_precision": "MONTH_ONLY", "retrieval_date": "2026-11-14",
        "url": "https://publications.rcaf.info/RCAF/Roundel/1963/Roundel-1963-09.pdf",
        "sha256": SHA, "bytes": 36226444, "pdf_pages": 36, "printed_page": 5,
        "pdf_page_index_zero_based": 6, "source_class": "CONTEMPORARY_RCAF_EDITORIAL_ACCOUNT_NOT_RAW_SENSOR_DATA",
        "scan_pdf_creation_date": "2022-06-01",
    }
    require(s == expected, "source metadata changed")
    anchors = doc["anchors"]
    require(isinstance(anchors, list) and len(anchors) == 3, "anchor count changed")
    for anchor, (aid, phrase, kind) in zip(anchors, EXPECTED_ANCHORS):
        require(isinstance(anchor, dict) and set(anchor) == {"id", "text", "kind", "evidentiary_scope"}, "anchor schema changed")
        require(anchor["id"] == aid and anchor["text"] == phrase and anchor["kind"] == kind, "anchor modified")
        require(isinstance(anchor["evidentiary_scope"], str) and any(x in anchor["evidentiary_scope"].lower() for x in ("not ", "no ")), "scope guard lost")
    indep = doc["independence"]
    require(set(indep) == {"editorial_provenance", "independent_instrumental_observations_recovered", "duplicate_528_measurement_with_other_ledgers"}, "independence keys changed")
    require(indep["independent_instrumental_observations_recovered"] == 0 and indep["duplicate_528_measurement_with_other_ledgers"] is None, "instrumental independence fabricated")
    require("unverified" in indep["editorial_provenance"], "independence warning removed")
    require(all(doc[key] is None for key in NULL_FIELDS), "unrecovered NORAD 528 field populated")
    require(doc["cold_lake_named_observations_recovered"] == 0, "individual observation fabricated")
    require(doc["physical_constraint_active"] is False and doc["orbit_parameters"] == "THETA_UNCHANGED", "premature physics activation")
    require(doc["impact_at_conde"] == "NOT_ESTABLISHED", "impact conclusion fabricated")
    require(doc["related_evidence"] == ["C241-L52", "C241-L53", "C241-L54"], "lineage drift")
    require("#420" in doc["next_acquisition"] and "NORAD 528" in doc["next_acquisition"], "acquisition plan lost")
    return {"evidence_id": doc["evidence_id"], "anchors": len(anchors), "physical_constraints": 0}


def normalized(text):
    return re.sub(r"\s+", " ", text).replace("\u00ad", "")


def verify_pdf(raw, doc=None):
    doc = doc or read_model()
    s = doc["source"]
    require(raw[:4] == b"%PDF", "not PDF")
    require(len(raw) == s["bytes"] and hashlib.sha256(raw).hexdigest() == s["sha256"], "PDF identity drift")
    # Integration tests run without pypdf installed; bad bytes must fail first.
    from pypdf import PdfReader

    pdf = PdfReader(io.BytesIO(raw), strict=False)
    require(len(pdf.pages) == s["pdf_pages"], "PDF page count drift")
    page = normalized(pdf.pages[s["pdf_page_index_zero_based"]].extract_text() or "")
    for anchor in doc["anchors"]:
        require(normalized(anchor["text"]) in page, f"missing page anchor {anchor['id']}")
    require("SEPTEMBER 1963" in page and re.search(r"\b5\b", page), "printed page marker absent")
    return {"verified_pdf_bytes": len(raw), "sha256": s["sha256"], "printed_page": 5}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    model = read_model()
    print(json.dumps(audit(model)))
    if args.live or args.pdf:
        if args.pdf:
            raw = args.pdf.read_bytes()
        else:
            req = urllib.request.Request(model["source"]["url"], headers={"User-Agent": "conde-orbit-custody/1.0"})
            with urllib.request.urlopen(req, timeout=70) as response:
                raw = response.read(model["source"]["bytes"] + 1)
        print(json.dumps(verify_pdf(raw, model)))


if __name__ == "__main__":
    main()
