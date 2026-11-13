#!/usr/bin/env python3
"""C241-L23: NASA April 10/30 editorial-listing gap, not disappearance from orbit."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_apr10_listing_C241-L23.json"
GRAPH = ROOT / "research/constraints/ssr_apr10_listing_C241-L23.json"
APRIL = ROOT / "research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json"
SHA256 = "f71ddf0477213e3ee1f47f5094f1d9afe7a52044e94cf18840805bdb48ba5f42"
SIZE = 206176
IDS = ["1963 3A", "1963 3B", "1963 3C"]
CONTROLS = ["1963 4A", "1963 4B", "1963 9A", "1963 9B"]
MISSING_FIELDS = ("instrumental_epoch_utc", "reference_frame", "sensor",
                  "instrument_uncertainty", "identity_of_528", "terminal_time", "terminal_location")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(ledger, graph, april):
    require(ledger.get("id") == "C241-L23", "wrong occurrence")
    src = ledger.get("source", {})
    require(src.get("ntrs_id") == "19630012127" and src.get("publication_date") == "1963-04-10"
            and src.get("issue") == 8 and src.get("volume") == 3
            and src.get("report") == "X-533-63-1" and src.get("nasa_tm") == "NASA-TM-X-50197",
            "April 10 NTRS metadata changed")
    require(src.get("pdf_url") ==
            "https://ntrs.nasa.gov/api/citations/19630012127/downloads/19630012127.pdf"
            and src.get("url") == "https://ntrs.nasa.gov/citations/19630012127",
            "April 10 URL changed")
    require(src.get("compilation_as_of_utc") == "1963-04-10T14:30:00Z"
            and src.get("pdf_pages") == 7
            and src.get("in_orbit_pdf_pages_one_based") == [3, 4, 5, 6, 7]
            and src.get("printed_pages") == "1-5"
            and src.get("inspection") == "VISUAL_ALL_FIVE_ROTATED_TABLE_PAGES_2026-11-13",
            "in-orbit table scope or inspection changed")
    require(src.get("sha256") == SHA256 and src.get("bytes") == SIZE,
            "April 10 PDF bytes identity changed")
    gap = ledger.get("negative_listing", {})
    require(gap.get("scope") == "ONLY_OBJECTS_IN_ORBIT_TABLE_OF_APRIL_10_FACSIMILE"
            and gap.get("missing_designators") == IDS
            and gap.get("present_controls") == CONTROLS
            and gap.get("basis") == "VISUAL_PAGE_BY_PAGE_NOT_TEXT_OCR"
            and gap.get("interpretation") == "NOT_LISTED_IN_THIS_EDITION_NOT_ABSENCE_FROM_ORBIT",
            "negative evidence exceeded inspected document scope")
    subsequent = ledger.get("subsequent_listing", {})
    require(subsequent == {"ntrs_id": "19630012128", "publication_date": "1963-04-30",
            "volume": 3, "issue": 9, "pdf_page_one_based": 7, "printed_page": 5,
            "designators": IDS, "dependency": "C241-L16", "elapsed_publication_days": 20},
            "April 30 bridge changed")
    limits = ledger.get("limits", {})
    require(set(limits) == set(MISSING_FIELDS) | {
            "family", "documentary_change_only", "listing_is_tracking_event",
            "listing_is_launch_date", "physical_absence_inferred",
            "independent_instrument_measurements_added", "lean_promoted", "physical_domain", "conde"},
            "missing or unexpected epistemic limits")
    require(all(limits[k] is None for k in MISSING_FIELDS)
            and limits["family"] == "NASA_GODDARD_NORAD_SAO_COMPILED"
            and limits["documentary_change_only"] is True
            and limits["listing_is_tracking_event"] is False
            and limits["listing_is_launch_date"] is False
            and limits["physical_absence_inferred"] is False
            and limits["independent_instrument_measurements_added"] == 0
            and limits["lean_promoted"] is False
            and limits["physical_domain"] == "UNCHANGED"
            and limits["conde"] == "INDETERMINATE", "false physical or instrumental promotion")
    require(april.get("id") == "C241-L16"
            and april.get("april", {}).get("ntrs") == "19630012128"
            and april.get("april", {}).get("publication") == "1963-04-30", "parent source mismatch")
    rows = april.get("april_rows", [])
    require([x.get("designator") for x in rows] == ["1963-003A", "1963-003B", "1963-003C"]
            and [x.get("nodal_period_min") for x in rows] == ["94.6", "94.1", "94.3"],
            "April 30 parent orbital values changed")

    require(graph.get("id") == "C241-L23:LISTING_GAP"
            and graph.get("schema") == "conde.documentary-listing-gap/v1"
            and graph.get("source_ledger") == str(LEDGER.relative_to(ROOT))
            and graph.get("source_family") == "NASA_NORAD_SAO_SAME_COMPILATION_LINEAGE"
            and graph.get("crosswalk_depends_on") == "C241-L10"
            and graph.get("prior_value_source") == "C241-L16", "graph disconnected")
    expected = [{"object_norad": norad, "printed_designator": designation,
                 "april_10_listed": False, "april_30_listed": True,
                 "operator": "publication_listing_indicator(document,designator)",
                 "measurement_epoch_utc": None, "frame": None, "sigma": None,
                 "meaning": "EDITORIAL_STATUS_NOT_PHYSICAL_STATE"}
                for norad, designation in zip([527, 528, 529], IDS)]
    require(graph.get("records") == expected, "documentary indicator or assumptions changed")
    require(graph.get("dependency_edges") == [
            {"from": "19630012127:VOL3-NO8", "to": "19630012128:VOL3-NO9",
             "type": "DOCUMENTARY_LISTING_CHANGE_WITHIN_20_DAYS"},
            {"from": "C241-L10", "to": "C241-L23:LISTING_GAP",
             "type": "SECONDARY_NORAD_CROSSWALK"},
            {"from": "C241-L16", "to": "C241-L23:LISTING_GAP",
             "type": "CONFIRMS_NEXT_EDITION_ROWS"}], "graph lineage changed")
    require(graph.get("independent_instrument_measurements_added") == 0
            and graph.get("physical_domain_reduced") is False
            and graph.get("lean_promoted") is False, "editorial gap became false physical proof")
    return {"id": "C241-L23", "compared_document_publication_days": 20,
            "edition_8_not_listed": IDS, "edition_9_listed": IDS,
            "independent_instrument_measurements_added": 0,
            "physical_constraints_activated": 0, "conde": "INDETERMINATE"}


def audit(ledger, graph, april, pdf):
    require(pdf.startswith(b"%PDF"), "not PDF")
    require(len(pdf) == SIZE and hashlib.sha256(pdf).hexdigest() == SHA256,
            "source bytes changed; reinspect PDF before updating custody")
    result = validate(ledger, graph, april)
    result["pdf_bytes_verified"] = len(pdf)
    result["pdf_sha256_verified"] = hashlib.sha256(pdf).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    def load(p):
        return json.loads(p.read_text(encoding="utf-8"))
    result = audit(load(LEDGER), load(GRAPH), load(APRIL), args.pdf.read_bytes())
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
