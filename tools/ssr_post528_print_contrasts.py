#!/usr/bin/env python3
"""Source-locked, exact contrasts of printed NASA SSR periods (not orbital inference)."""
from __future__ import annotations

from decimal import Decimal
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/statistics/ssr_post528_print_contrasts_C241.json"
DATA = ROOT / "research/tle_custody"
DESIGNATORS = ("1963-003A", "1963-003B", "1963-003C")
DATES = ("1963-04-30", "1963-07-31", "1963-08-15", "1963-10-15",
         "1963-11-15", "1963-11-30", "1963-12-15", "1963-12-31")
HASHES = {
    "1963-04-30": "87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38",
    "1963-07-31": "9b00bf8323b1de80a34920f73c658f70f766a51632a13473a408679f0e5a03d9",
    "1963-08-15": "4e5cb0205577bc1b0959088db9ca3ae7a05f8de480b5ece9b86c385437636968",
    "1963-10-15": "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2",
    "1963-11-15": "0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674",
    "1963-11-30": "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d",
    "1963-12-15": "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f",
    "1963-12-31": "d9504a8641baa65c208e41034e77b0e9b1cc01b4acb2a4f95541bd9e75d3783d",
}
FILENAMES = {
    "apr": "nasa_ssr_apr_oct_1963_C241-L16.json",
    "jul_dec": "nasa_ssr_jul_dec_1963_C241-L18.json",
    "aug": "nasa_ssr_aug15_1963_C241-L17.json",
    "oct": "nasa_ssr_1963_oct15_C241-L12.json",
    "nov": "nasa_ssr_nov15_1963_C241-L19.json",
    "dec15": "nasa_ssr_dec15_1963_C241-L21.json",
}
HALF_PRINT_CENTIMIN = 5  # conditional nearest 0.1 min rounding


def read_sources() -> dict:
    return {key: json.loads((DATA / filename).read_text())
            for key, filename in FILENAMES.items()}


def _period(value: object) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+\.[0-9]", value):
        raise ValueError("printed period must be literal with one decimal digit")
    cents = int(Decimal(value) * 100)
    if cents <= 0:
        raise ValueError("printed period must be positive")
    return cents


def reports(documents: dict | None = None) -> list[dict]:
    d = read_sources() if documents is None else documents
    if set(d) != set(FILENAMES):
        raise ValueError("expected five source ledgers")
    jul_dec = {v["published"]: v for v in d["jul_dec"]["sources"]}
    if set(jul_dec) != {"1963-07-31", "1963-11-30", "1963-12-31"}:
        raise ValueError("incomplete July/November/December source family")
    nov = d["nov"]["documents"]
    dec15 = d["dec15"]
    if (dec15["id"] != "C241-L21" or dec15["source"]["ntrs_id"] != "19640003479"
        or dec15["source"]["compilation_as_of_utc"] != "1963-12-15T12:00:00Z"
        or dec15["not_listed_in_objects_in_orbit"] != ["1963-003B"]
        or dec15["limits"]["independent_sensor_observation"] is not False
        or dec15["limits"]["instrumental_epoch_utc"] is not None):
        raise ValueError("Dec 15 source provenance or interpretation drift")
    if {row["designator"]: row["norad_crosswalk"] for row in dec15["rows"]} != {
        "1963-003A": 527, "1963-003C": 529
    } or len(dec15["rows"]) != 2:
        raise ValueError("Dec 15 object crosswalk drift")
    if len(nov) != 1:
        raise ValueError("November 15 ledger must have exactly one document")
    specs = [
        ("1963-04-30", "C241-L16", d["apr"]["april"]["sha256"],
         d["apr"]["april_rows"], "designator", "nodal_period_min"),
        ("1963-07-31", "C241-L18", jul_dec["1963-07-31"]["sha256"],
         jul_dec["1963-07-31"]["rows"], "designator", "period_min"),
        ("1963-08-15", "C241-L17", d["aug"]["source"]["sha256"],
         d["aug"]["rows"], "designator", "nodal_period_min"),
        ("1963-10-15", "C241-L12", d["oct"]["source"]["sha256"],
         d["oct"]["catalog_rows"], "international_designator", "nodal_period_min_printed"),
        ("1963-11-15", "C241-L19", nov[0]["sha256"],
         nov[0]["rows"], "designator", "period_min"),
        ("1963-11-30", "C241-L18", jul_dec["1963-11-30"]["sha256"],
         jul_dec["1963-11-30"]["rows"], "designator", "period_min"),
        ("1963-12-15", "C241-L21", dec15["source"]["sha256"],
         dec15["rows"], "designator", "period_min"),
        ("1963-12-31", "C241-L18", jul_dec["1963-12-31"]["sha256"],
         jul_dec["1963-12-31"]["rows"], "designator", "period_min"),
    ]
    metadata_dates = (
        d["apr"]["april"]["publication"],
        jul_dec["1963-07-31"]["published"],
        d["aug"]["source"]["publication"],
        d["oct"]["source"]["publication_date"],
        nov[0]["date"],
        jul_dec["1963-11-30"]["published"],
        dec15["source"]["publication_date"],
        jul_dec["1963-12-31"]["published"],
    )
    if metadata_dates != DATES:
        raise ValueError("source publication metadata drift")
    result = []
    for day, occurrence, sha, rows, id_key, period_key in specs:
        if sha != HASHES[day]:
            raise ValueError(f"source sha256 drift for {day}")
        values = {}
        for row in rows:
            designator = row[id_key]
            if designator not in DESIGNATORS or designator in values:
                raise ValueError(f"duplicate or unknown designator in {day}")
            values[designator] = _period(row[period_key])
        expected = set(DESIGNATORS) if day <= "1963-10-15" else {"1963-003A", "1963-003C"}
        if set(values) != expected:
            raise ValueError(f"source membership drift for {day}")
        result.append({"report_date_not_observation_epoch": day, "occurrence": occurrence,
                       "pdf_sha256": sha, "printed_centiminutes": values,
                       "source_family": "NASA_GODDARD_COMPILED_SHARED_TRACKING"})
    if tuple(x["report_date_not_observation_epoch"] for x in result) != DATES:
        raise ValueError("report date/order drift")
    if result[-2]["printed_centiminutes"]["1963-003C"] != 9160:
        raise ValueError("December 15 3C value drift")
    if result[-1]["printed_centiminutes"]["1963-003C"] != 8920:
        raise ValueError("December 3C transcription reverted from 89.2 to 89.6")
    return result


def _difference(first: int, last: int, components: int = 2) -> dict:
    center = first - last
    margin = HALF_PRINT_CENTIMIN * components
    return {"center_centiminutes": center,
            "interval_centiminutes": [center - margin, center + margin],
            "strictly_positive_under_rounding": center - margin > 0}


def build(documents: dict | None = None) -> dict:
    source_reports = reports(documents)
    by_day = {r["report_date_not_observation_epoch"]: r["printed_centiminutes"]
              for r in source_reports}
    post_days = DATES[3:]
    post = {}
    for designator in ("1963-003A", "1963-003C"):
        post[designator] = [
            {"earlier_report": a, "later_report": b,
             "printed_earlier_minus_later": _difference(by_day[a][designator],
                                                        by_day[b][designator])}
            for a, b in zip(post_days, post_days[1:])
        ]
    did = []
    for a, b in zip(post_days, post_days[1:]):
        change_c = by_day[a]["1963-003C"] - by_day[b]["1963-003C"]
        change_a = by_day[a]["1963-003A"] - by_day[b]["1963-003A"]
        did.append({"earlier_report": a, "later_report": b,
                    "C_minus_A_printed_change_contrast": _difference(change_c, change_a, 4)})
    first, last = post_days[0], post_days[-1]
    long_did = _difference(by_day[first]["1963-003C"]-by_day[last]["1963-003C"],
                           by_day[first]["1963-003A"]-by_day[last]["1963-003A"], 4)
    return {
        "schema": "conde.ssr-post528-printed-contrast/v1",
        "classification": "SOURCE_LOCKED_DOCUMENTARY_CONTRAST_NOT_ORBITAL_LIKELIHOOD",
        "sources": source_reports,
        "period_unit": "centiminutes integer (1/100 minute)",
        "rounding_assumption": "nearest tenth minute, each printed center +/- 5 centiminutes; not sensor uncertainty",
        "post_cataloged_528_day": "1963-11-08 (NASA compiled catalog day, no terminal epoch)",
        "post_528_report_dates": list(post_days[1:]),
        "not_listed_528": list(post_days[1:]),
        "not_listed_is_nondetection": False,
        "post_october_adjacent_contrasts": post,
        "C_minus_A_difference_in_differences": did,
        "C_minus_A_october_december": long_did,
        "limits": {
            "instrumental_epoch": None, "sensor_and_covariance": None,
            "source_independence": "NOT_ESTABLISHED_SHARED_NASA_NORAD_LINEAGE",
            "holdout": "RETROSPECTIVE_NOT_BLIND_NO_PHYSICAL_FORWARD_OPERATOR",
            "rate_by_publication_interval": "NOT_IDENTIFIED",
            "mcmc_historical": "NOT_RUN",
            "geographic_exclusion": "NOT_AUTHORIZED",
            "active_physical_constraint": False,
            "next_discriminant": "dated 527/529/528 raw tracks with frames, calibrations, covariance and independent source genealogy",
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    encoded = (json.dumps(build(), ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode()
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != encoded:
            raise SystemExit("source-locked report drift")
    else:
        OUT.write_bytes(encoded)


if __name__ == "__main__":
    main()
