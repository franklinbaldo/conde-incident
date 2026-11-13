#!/usr/bin/env python3
"""C241-L16: source-pinned two-publication comparison, not TLE epochs."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
try:
    from tools.tle_nasa_ssr_oct15_audit import validate_ledger as validate_oct
except ModuleNotFoundError:
    from tle_nasa_ssr_oct15_audit import validate_ledger as validate_oct

PIN = ("87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38", 592923)
EXPECTED = [
    ("1963-003A", "1963 3A", "94.6", "81.89", 537, 460),
    ("1963-003B", "1963 3B", "94.1", "81.87", 505, 435),
    ("1963-003C", "1963 3C", "94.3", "81.88", 531, 437),
]
UNKNOWN = ("source_tle_pair", "raan_deg", "frame", "sensor", "sigma",
           "terminal_time", "terminal_location", "identity_528")


def validate(april, october):
    a, b, lim = april["april"], april["october"], april["limits"]
    if april["id"] != "C241-L16":
        raise ValueError("wrong evidence ID")
    if (a["ntrs"], a["publication"], a["volume"], a["number"],
        a["url"], a["pdf_page_index_zero_based"], a["printed_page"],
        a["data_as_of"], a["sha256"], a["bytes"]) != (
            "19630012128", "1963-04-30", 3, 9,
            "https://ntrs.nasa.gov/api/citations/19630012128/downloads/19630012128.pdf",
            6, 5, "1430Z APR 30 1963", *PIN):
        raise ValueError("unverified April source identity")
    if (b["id"], b["ntrs"], b["publication"], b["ledger"]) != (
            "C241-L12", "19640000428", "1963-10-15",
            "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"):
        raise ValueError("incorrect later source")
    validate_oct(october)
    if (lim["status"], lim["source_independence"], lim["issue_21"],
        lim["lean"], lim["graph"], lim["outcome"]) != (
            "PRIMARY_CONTEMPORARY_PUBLICATION_NOT_INSTRUMENTAL_ORBIT",
            "NOT_ESTABLISHED", "NOT_RECOVERED", "NOT_PROMOTED",
            "CONNECTED_PENDING_CALIBRATION", "INDETERMINATE"):
        raise ValueError("historical data wrongly promoted")
    for field in ("date_is_orbital_epoch", "delta_is_time_derivative", "printed_norad_ids"):
        if lim[field] is not False:
            raise ValueError("invented observation: " + field)
    for field in UNKNOWN:
        if lim[field] is not None:
            raise ValueError("invented physical data: " + field)
    if len(april["april_rows"]) != 3 or len(october["catalog_rows"]) != 3:
        raise ValueError("exactly three source rows expected")
    result = []
    for row, later, exp in zip(april["april_rows"], october["catalog_rows"], EXPECTED):
        got = (row["designator"], row["printed"], row["nodal_period_min"],
               row["inclination_deg"], row["apogee_km"], row["perigee_km"])
        if got != exp or row["source"] != "US" or row["launch"] != "1963-01-16":
            raise ValueError("April facsimile transcription changed")
        if row["designator"] != later["international_designator"]:
            raise ValueError("wrong cross-edition object")
        if any(type(row[k]) is not int for k in ("apogee_km", "perigee_km")):
            raise ValueError("invalid printed altitude unit")
        if row["perigee_km"] <= 0 or row["apogee_km"] < row["perigee_km"]:
            raise ValueError("invalid altitude")
        result.append({
            "designator": row["designator"],
            "april_period_min": row["nodal_period_min"],
            "october_period_min": later["nodal_period_min_printed"],
            "published_delta_period_min_not_physical_rate": str(
                Decimal(later["nodal_period_min_printed"]) - Decimal(row["nodal_period_min"])),
            "published_delta_apogee_km": later["apogee_km_printed"] - row["apogee_km"],
            "published_delta_perigee_km": later["perigee_km_printed"] - row["perigee_km"],
            "epoch_of_elements": None,
            "independent_sensor_observation": False
        })
    return result


def audit(april, october, blob):
    rows = validate(april, october)
    if not blob.startswith(b"%PDF-"):
        raise ValueError("not PDF")
    if (hashlib.sha256(blob).hexdigest(), len(blob)) != PIN:
        raise ValueError("April PDF SHA-256/bytes mismatch")
    return {"record_id": "C241-L16", "rows": rows,
            "source_april_sha256": PIN[0], "source_april_bytes": PIN[1],
            "primary_tle_pairs_found": False, "physical_domain_reduced": False,
            "pixels_checked_by_ci": False, "conde_outcome": "INDETERMINATE"}


def main():
    p = argparse.ArgumentParser()
    for name in ("ledger", "october", "pdf", "output"):
        p.add_argument("--" + name, required=True, type=Path)
    args = p.parse_args()
    result = audit(json.loads(args.ledger.read_text()),
                   json.loads(args.october.read_text()), args.pdf.read_bytes())
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("C241-L16: three contemporary documentary rows compared, no TLE epoch")


if __name__ == "__main__":
    main()
