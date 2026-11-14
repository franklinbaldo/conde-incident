#!/usr/bin/env python3
"""C241-L67: printed-date bijection between NASA SSR editions, not an ID proof."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/tle_custody/nasa_ssr_omega308_date_matches_C241-L67.json"
PARENT = ROOT / "research/tle_custody/nasa_ssr_omega308_cross_edition_C241-L66.json"
SHA63 = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"
SHA77 = "c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8"

EXPECTED_63 = [
    ("OMEGA 1", "18 JUN", "29-30 OCT 63"),
    ("OMEGA 2", "18 JUN", "12 JUL 62"),
    ("OMEGA 3", "18 JUN", "14 JUL 62"),
]
EXPECTED_77 = [
    ("OMEGA 2", 308, "18 JUN", "29-30 OCT 63"),
    ("OMEGA 3", 310, "18 JUN", "12 JUL 62"),
    ("A-ALPHA 5", 314, "18 JUN", "14 JUL 62"),
]


def unique_pairs(rows):
    """Reject duplicate signatures rather than silently choosing a name."""
    mapping = {}
    for row in rows:
        key = row["launch"], row["decay"]
        if key in mapping:
            raise ValueError("ambiguous printed date signature: " + str(key))
        mapping[key] = row
    return mapping


def derive(contemporary, retrospective):
    old, new = unique_pairs(contemporary), unique_pairs(retrospective)
    if set(old) != set(new):
        raise ValueError("unmatched printed date signatures")
    return [
        {
            "contemporary_name": row["printed_name"],
            "retrospective_name": new[(row["launch"], row["decay"])]["printed_name"],
            "retrospective_catalog_number": new[(row["launch"], row["decay"])]["catalog_number"],
        }
        for row in contemporary
    ]


def no_duplicate_keys(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError("duplicate JSON key: " + key)
        data[key] = value
    return data


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_keys)


def exact(actual, expected, label):
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError("C241-L67 invalid " + label)


def validate(data, parent):
    exact(set(data), {"id", "kind", "inherited", "editions", "match_fields",
                      "contemporary_rows", "retrospective_rows",
                      "date_signature_matches", "limits"}, "fields")
    exact(data["id"], "C241-L67", "id")
    exact(data["kind"], "NASA_SSR_PRINTED_DATE_SIGNATURE_MATCH_WITHOUT_IDENTITY_PROOF", "kind")
    exact(data["inherited"], ["C241-L65", "C241-L66"], "lineage")
    exact(data["match_fields"], ["launch", "decay"], "signature")
    exact(data["editions"], {
        "contemporary": {
            "ntrs_id": "19640003479", "publication": "1963-12-15",
            "pdf_page_1based": 17, "sha256": SHA63, "catalog_number_printed": False
        },
        "retrospective": {
            "ntrs_id": "19780009188", "publication": "1977-12-31",
            "pdf_page_1based": 46, "sha256": SHA77, "catalog_number_printed": True
        }
    }, "sources")
    c = data["contemporary_rows"]
    r = data["retrospective_rows"]
    exact(c, [
        {"printed_name": name, "launch": launch, "decay": decay}
        for name, launch, decay in EXPECTED_63
    ], "1963 table")
    exact(r, [
        {"printed_name": name, "catalog_number": number,
         "launch": launch, "decay": decay}
        for name, number, launch, decay in EXPECTED_77
    ], "1977 table")
    exact(data["date_signature_matches"], derive(c, r), "derived bijection")
    exact(data["limits"], {
        "date_match_is_instrumental_identity": False,
        "edition_independence": "SAME_NASA_GSFC_REPORT_FAMILY",
        "calendar_is_utc_timing_measurement": False,
        "terminal_event_utc": None,
        "terminal_sigma_seconds": None,
        "independent_instrumental_measurements": 0,
        "historical_mcmc": "NOT_RUN",
        "active_constraint_528": False,
        "impact_probability": None,
    }, "inference limits")
    exact(parent["id"], "C241-L66", "parent")
    source63 = parent["sources"]["contemporary_1963"]
    source77 = parent["sources"]["retrospective_1977"]
    exact(source63["sha256"], SHA63, "parent 1963 bytes")
    exact(source77["sha256"], SHA77, "parent 1977 bytes")
    for index, old in enumerate(c):
        original = source63["visually_read_rows"][index]
        exact((old["printed_name"], old["launch"], old["decay"]),
              (original["designator"], original["launch"], original["decay"]),
              "parent 1963 row")
    for index in (0, 1):
        old = r[index]
        original = source77["visually_read_rows"][index + 1]
        exact((old["printed_name"], old["catalog_number"], old["launch"],
               old["decay"]),
              (original["designator"], original["catalog_number"],
               original["launch"], original["decay"]), "parent 1977 row")
    return True


def main():
    validate(load(DATA), load(PARENT))
    print("C241-L67 PASS: 3 printed-date signatures matched, 0 independent "
          "terminal observations; identity and MCMC NOT_CONFIRMED/NOT_RUN")


if __name__ == "__main__":
    main()
