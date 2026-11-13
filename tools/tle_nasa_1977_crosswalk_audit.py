#!/usr/bin/env python3
"""C241-L32: validate NASA's retrospective 1963-003B/528 catalog identity."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "research/tle_custody/nasa_ssr_dec1977_528_identity_C241-L32.json"
SHA = "c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8"
SIZE = 11563410
NTRS = "19780009188"
PDF_URL = "https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf"
PAIR = re.compile(r"(?<![0-9])1963\s+003B\s+528(?![0-9])", re.IGNORECASE)
CONTROL = re.compile(r"(?<![0-9])1963\s+003A\s+527(?![0-9])", re.IGNORECASE)


def require(test, label):
    if not test:
        raise ValueError(label)


def validate(d):
    require(d["schema"] == "conde.nasa-retrospective-satellite-catalog-crosswalk/v1"
            and d["record_id"] == "C241-L32", "ledger identity")
    s = d["source"]
    require(s["title"] == "Satellite Situation Report, Volume 17, Number 6"
            and s["report_number"] == "NASA-TM-79345"
            and s["ntrs_id"] == NTRS
            and s["date_published"] == "1977-12-31"
            and s["pdf_url"] == PDF_URL
            and s["ntrs_url"] == "https://ntrs.nasa.gov/citations/" + NTRS
            and s["pdf_sha256"] == SHA
            and s["pdf_bytes"] == SIZE
            and s["document_kind"] == "ORIGINAL_NASA_1977_PUBLICATION_RETROSPECTIVE_CATALOG_NOT_1963_SENSOR"
            and s["table_section"] == "DECAYED OBJECTS"
            and s["year_group"] == "1963 LAUNCHES", "NASA publication custody changed")
    r = d["row"]
    require(r["international_designator_printed"] == "1963 003B"
            and type(r["catalog_number_printed"]) is int
            and r["catalog_number_printed"] == 528
            and r["identity_match"] in {
                "CANDIDATE_OCR_PENDING_PAGE_IMAGE", "DIRECT_VISUAL_VERIFIED"},
            "crosswalk claim changed")
    require(all(r[x] is None for x in (
                "source_528_sensor_id", "original_1963_tle_pair",
                "original_1963_observation_epoch_utc",
                "reentry_physical_time_utc", "reentry_location"))
            and r["decay_date_cell_crosscheck"] == "1963-11-08"
            and r["reported_decay_day_from_1977_table"] == "1963-11-08"
            and r["decay_day_timezone"] is None
            and r["decay_day_error_seconds"] is None,
            "sensor or reentry claim invented")
    require(s["page_index_zero_based"] is None or (
                type(s["page_index_zero_based"]) is int
                and s["page_index_zero_based"] >= 0), "bad page index")
    if r["identity_match"] == "DIRECT_VISUAL_VERIFIED":
        require(s["full_page_visual_review"] == "VISUALLY_VERIFIED_1977_SOURCE"
                and s["page_index_zero_based"] == 46
                and s["printed_page"] == 43
                and "43454971351" in s["visual_basis"], "visual review not supported")
    else:
        require(s["full_page_visual_review"] == "PENDING_DIRECT_REVIEW_AFTER_RUNNER_RENDER"
                and s["printed_page"] is None, "candidate incorrectly certified")
    require(d["control_rows"] == [
        {"international_designator_printed": "1963 003A",
         "catalog_number_printed": 527,
         "decay_day_printed": "1969-01-09",
         "role": "POSITIVE_PREVIOUSLY_KNOWN_C241-L28"},
        {"international_designator_printed": "1963 003C",
         "catalog_number_printed": 529,
         "decay_day_printed": "1963-12-31",
         "role": "ADDITIONAL_NASA_1977_RETROSPECTIVE_PRIMARY_CROSSWALK"}
    ], "NASA visual control rows changed")
    deps = d["dependencies"]
    require(deps == [
        "research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json",
        "research/constraints/nasa_528_decay_precision_C197_20261113.json"
    ], "dependency graph disconnected")
    require([x["occurrence"] for x in d["context"] if "occurrence" in x] ==
            ["C197#1", "C241-L28", "C241-L10"], "provenance not linked")
    ind = d["independence"]
    require(ind["upstream_catalog_family"] == "NASA_NORAD_OR_SAO_SHARED_TRACKING_POSSIBLE"
            and ind["does_not_constitute_additional_radar_tracking"]
            and ind["independent_528_instrumental_observations_added"] == 0
            and ind["chronology_not_contemporary_to_1963"]
            and ind["second_document_does_not_independently_validate_reentry"],
            "retrospective report counted as independent sensor")
    g = d["graph"]
    require(len(g["proposed_edges"]) == 6
            and g["constraint_status"] == "DOCUMENTARY_CROSSWALK_VERIFIED_NO_PHYSICAL_CONSTRAINT"
            and g["physical_constraints_activated"] == 0
            and g["lean_predicates_activated"] == 0
            and not g["change_to_simulation_parameters"]
            and not g["localized_impact_inferred"], "unjustified orbital inference")
    return {"record_id": d["record_id"], "publication": s["date_published"],
            "catalog_pair": ["1963 003B", 528],
            "other_primary_retrospective_pairs": [["1963 003A", 527], ["1963 003C", 529]],
            "528_reported_decay_day": r["reported_decay_day_from_1977_table"],
            "printed_page": s["printed_page"],
            "source": PDF_URL, "source_kind": s["document_kind"],
            "epistemic_grade": r["identity_match"],
            "physical_constraints_activated": 0,
            "independent_instrumental_observations": 0}


def verify_pdf(pdf: Path):
    b = pdf.read_bytes()
    require(b.startswith(b"%PDF"), "not a PDF")
    require(len(b) == SIZE, "NASA source length mismatch")
    require(hashlib.sha256(b).hexdigest() == SHA, "NASA source SHA mismatch")
    # Try both extraction orders; never infer a page number from a global match.
    modes = ("-raw", "-layout")
    by_mode = {}
    for mode in modes:
        run = subprocess.run(
            ["pdftotext", mode, str(pdf), "-"],
            capture_output=True, check=True, text=True)
        pages = run.stdout.split("\f")
        candidates = []
        controls = []
        for i, page in enumerate(pages):
            if PAIR.search(page):
                candidates.append(i)
            if CONTROL.search(page):
                controls.append(i)
        by_mode[mode] = {"pair_pages_0based": candidates,
                         "control_pages_0based": controls}
    pages = sorted(set(p for x in by_mode.values() for p in x["pair_pages_0based"]))
    controls = sorted(set(p for x in by_mode.values() for p in x["control_pages_0based"]))
    require(pages == [46], "NASA 003B/528 row moved from PDF index 46")
    require(pages == controls, "527 control not on same printed PDF page")
    return {"pdf_bytes_verified": len(b), "sha256_verified": SHA,
            "pair_page_index_zero_based": pages[0],
            "pair_page_number_1based": pages[0] + 1,
            "extraction_modes": by_mode,
            "visual_confirmation": "NOT_AUTOMATICALLY_INFERRED_FROM_OCR"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, default=LEDGER_PATH)
    p.add_argument("--pdf", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = validate(json.loads(args.ledger.read_text(encoding="utf-8")))
    if args.pdf:
        result["pdf_audit"] = verify_pdf(args.pdf)
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
