#!/usr/bin/env python3
"""C241-L64: NASA SSR Omega 1 catalogue date-range is not terminal UTC."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json"
PDF_SHA = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"
PDF_BYTES = 958927
EMPTY = ("printed_norad_id", "terminal_utc", "utc_interval", "sensor",
         "station", "original_observation", "sigma_seconds")


def no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key " + key)
        out[key] = value
    return out


def load(path=PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_keys)


def exact(actual, fields, label):
    if type(actual) is not dict or set(actual) != set(fields):
        raise ValueError(label + " schema")
    for key, expected in fields.items():
        if type(actual[key]) is not type(expected) or actual[key] != expected:
            raise ValueError(label + ": " + key)


def validate(record):
    if type(record) is not dict or set(record) != {
        "id", "kind", "source", "original_row", "identity", "archive_search", "inference"
    }:
        raise ValueError("root schema")
    exact(record["source"], json.loads(r'''{"ntrs_id":"19640003479","publication":"1963-12-15","series":"NASA GSFC Satellite Situation Report, vol. 3, no. 24","pdf_url":"https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf","pdf_sha256":"d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f","pdf_bytes":958927,"pdf_pages":23,"printed_page":15,"zero_based_page":16,"section":"DECAYED OBJECTS (CONT'D)","new_document":true,"individual_instrumental_observation":false}'''), "source")
    exact(record["original_row"], json.loads(r'''{"section_year":"1962 LAUNCHES (CONT'D)","printed_designator":"A OMEGA 1","printed_source":"US","launch_printed":"18 JUN","decay_printed":"29-30 OCT 63","calendar_range_start":"1963-10-29","calendar_range_end":"1963-10-30","interpretation":"PUBLISHED_CALENDAR_RANGE_NOT_UTC_EVENT","printed_norad_id":null,"terminal_utc":null,"utc_interval":null,"sensor":null,"station":null,"original_observation":null,"sigma_seconds":null}'''), "original_row")
    exact(record["identity"], json.loads(r'''{"secondary_norad_id":308,"secondary_cospar":"1962-024A","secondary_name":"FTV 2312 / 1962 Omega 1","secondary_url":"https://keeptrack.space/satellite/00308","secondary_name_crosswalk":"https://en.wikipedia.org/wiki/Samos-F","identity_status":"SECONDARY_CROSSWALK_PENDING_PRIMARY_NORAD_ID","nasa_explicitly_prints_308":false}'''), "identity")
    exact(record["archive_search"], json.loads(r'''{"endpoint":"https://ntrs.nasa.gov/api/citations/search","method":"POST","query":{"q":"SATELLITE SITUATION REPORT","published":{"gte":"1963-10-01","lte":"1963-12-31"},"page":{"size":100,"from":0}},"returned_ids":["19640000428","19640001198","19640002493","19640003479","19640005618"],"no21_in_this_query":true,"no21_nonexistence_established":false}'''), "archive_search")
    exact(record["inference"], json.loads(r'''{"primary_publications_added":1,"independent_original_sensor_observations_added":0,"calibrated_terminal_utc_added":0,"uncertainty_distribution_available":false,"hard_constraints_528_added":0,"conde_impact_demonstrated":false,"prior_snapshot":"C241-L63 unresolved_control=NOT_RECOVERED; preserved byte-for-byte"}'''), "inference")
    if record["id"] != "C241-L64" or record["kind"] != "NASA_SSR_CONTEMPORARY_DECAY_RANGE_CONTROL":
        raise ValueError("ID/kind")
    if any(record["original_row"][key] is not None for key in EMPTY):
        raise ValueError("fabricated terminal measurements")
    return True


def verify_pdf(path):
    data = Path(path).read_bytes()
    if len(data) != PDF_BYTES or not data.startswith(b"%PDF-") or hashlib.sha256(data).hexdigest() != PDF_SHA:
        raise ValueError("uninspected PDF variant or provenance mismatch")
    return True


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--pdf", type=Path)
    args = argp.parse_args()
    validate(load())
    if args.pdf is not None:
        verify_pdf(args.pdf)
    print("C241-L64 VERIFIED: NASA 1962 A OMEGA 1 / 29-30 OCT 63; UTC/sensor/sigma unavailable")


if __name__ == "__main__":
    main()
