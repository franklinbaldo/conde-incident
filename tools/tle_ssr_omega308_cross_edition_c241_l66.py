#!/usr/bin/env python3
"""C241-L66: immutable NASA SSR cross-edition Omega/NORAD 308 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/tle_custody/nasa_ssr_omega308_cross_edition_C241-L66.json"
L64 = ROOT / "research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json"
L65 = ROOT / "research/tle_custody/nasa_ssr_omega1_corrigendum_C241-L65.json"
S63 = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"
S77 = "c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8"


def without_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate key: " + key)
        out[key] = value
    return out


def load(path=DATA):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=without_duplicate_keys)


def eq(actual, expected, label):
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError("C241-L66 invalid " + label)


def validate(document, legacy, corrigendum):
    if type(document) is not dict:
        raise ValueError("document type")
    eq(set(document), {"id", "kind", "previous_records", "sources",
                       "finding", "inference"}, "schema")
    eq(document["id"], "C241-L66", "id")
    eq(document["kind"], "NASA_SSR_CROSS_EDITION_OMEGA_308_DISCREPANCY", "kind")
    eq(document["previous_records"], ["C241-L64", "C241-L65", "C241-L32"], "lineage")
    s63 = document["sources"]["contemporary_1963"]
    s77 = document["sources"]["retrospective_1977"]
    eq(set(document["sources"]), {"contemporary_1963", "retrospective_1977"},
       "source keys")
    eq(s63, {
        "ntrs_id": "19640003479",
        "publication": "1963-12-15",
        "pdf_url": "https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf",
        "sha256": S63, "bytes": 958927, "pages": 23,
        "pdf_page_1based": 17, "printed_page": 15, "printed_norad_number": None,
        "visually_read_rows": [
            {"designator": "OMEGA 1", "launch": "18 JUN", "decay": "29-30 OCT 63"},
            {"designator": "OMEGA 2", "launch": "18 JUN", "decay": "12 JUL 62"},
            {"designator": "OMEGA 3", "launch": "18 JUN", "decay": "14 JUL 62"},
        ],
        "row_alignment_uncertainty": "NEIGHBOR_DATES_REQUIRE_INDEPENDENT_CONFIRMATION",
    }, "1963 original")
    eq(s77, {
        "ntrs_id": "19780009188",
        "pdf_url": "https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf",
        "sha256": S77, "bytes": 11563410, "pages": 115,
        "pdf_page_1based": 46, "printed_page": -42,
        "visually_read_rows": [
            {"designator": "OMEGA 1", "catalog_number": 307,
             "source": "US", "launch": "17 JUN", "decay": "18 JUN 62"},
            {"designator": "OMEGA 2", "catalog_number": 308,
             "source": "US", "launch": "18 JUN", "decay": "29-30 OCT 63"},
            {"designator": "OMEGA 3", "catalog_number": 310,
             "source": "US", "launch": "18 JUN", "decay": "12 JUL 62"},
        ],
        "source_already_in_custody": "C241-L32",
    }, "1977 original")
    eq(document["finding"], {
        "retrospective_explicit_norad_crosswalk": "OMEGA 2 = 308 IN 1977 NASA TABLE",
        "contemporary_matching_launch_and_decay_label": "OMEGA 1",
        "label_conflict": "UNRESOLVED_PRINTED_NAME_CROSS_EDITION",
        "same_launch_and_decay_dates": True,
        "cause_of_discrepancy": None,
        "contemporary_omega1_identity_to_308":
            "NOT_CONFIRMED_BY_CONCURRENT_PRIMARY_ROW",
    }, "findings")
    eq(document["inference"], {
        "new_primary_pdf_families": 0,
        "independent_instrumental_measurements": 0,
        "terminal_event_utc": None, "terminal_sigma_seconds": None,
        "station": None, "sensor": None,
        "contemporaneous_norad_308_printed": False,
        "retrospective_norad_308_printed": True,
        "historical_mcmc": "NOT_RUN",
        "active_constraint_528": False, "impact_geography": None,
    }, "inference")
    eq(legacy["id"], "C241-L64", "preserved L64")
    eq(legacy["original_row"]["printed_designator"], "A OMEGA 1",
       "L64 original error immutable")
    eq(corrigendum["id"], "C241-L65", "preserved L65")
    eq(corrigendum["corrects"]["correct_value"], "OMEGA 1",
       "L65 first correction")
    eq(legacy["source"]["pdf_sha256"], S63, "legacy source hash")
    eq(corrigendum["source"]["pdf_sha256"], S63, "first correction source hash")
    return True


def verify_pdf(path, variant):
    expected = {"1963": (958927, S63), "1977": (11563410, S77)}
    if variant not in expected:
        raise ValueError("unknown PDF variant")
    data = Path(path).read_bytes()
    size, sha = expected[variant]
    if len(data) != size or not data.startswith(b"%PDF-"):
        raise ValueError("PDF variant/size mismatch")
    if hashlib.sha256(data).hexdigest() != sha:
        raise ValueError("PDF SHA-256 mismatch")
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdf63", type=Path)
    p.add_argument("--pdf77", type=Path)
    args = p.parse_args()
    validate(load(), load(L64), load(L65))
    if args.pdf63 is not None:
        verify_pdf(args.pdf63, "1963")
    if args.pdf77 is not None:
        verify_pdf(args.pdf77, "1977")
    print("C241-L66 PASS: 1977 NASA OMEGA 2=308; 1963 OMEGA 1 conflict,"
          " no UTC/sigma/instrument/528 restriction")


if __name__ == "__main__":
    main()
