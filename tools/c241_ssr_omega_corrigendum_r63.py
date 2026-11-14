#!/usr/bin/env python3
"""C241-L65: fail-closed erratum of the NASA 1962 OMEGA 1 printed label."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L64 = ROOT / "research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json"
L65 = ROOT / "research/tle_custody/nasa_ssr_omega1_corrigendum_C241-L65.json"
PDF_SHA = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"


def no_duplicates(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError("duplicate key: " + key)
        data[key] = value
    return data


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicates)


def require_equal(actual, expected, name):
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError(name + ": expected " + repr(expected))


def validate(legacy, correction):
    if not isinstance(legacy, dict) or not isinstance(correction, dict):
        raise ValueError("missing records")
    if set(correction) != {"id", "kind", "corrects", "source",
                           "disambiguation", "inference"}:
        raise ValueError("correction schema")
    require_equal(legacy.get("id"), "C241-L64", "legacy ID")
    old = legacy["original_row"]
    require_equal(old["printed_designator"], "A OMEGA 1", "archived error")
    require_equal(old["printed_source"], "US", "legacy source")
    require_equal(old["launch_printed"], "18 JUN", "legacy launch")
    require_equal(old["decay_printed"], "29-30 OCT 63", "legacy calendar")
    require_equal(legacy["source"]["pdf_sha256"], PDF_SHA, "legacy PDF")

    require_equal(correction["id"], "C241-L65", "correction ID")
    require_equal(correction["kind"],
                  "NASA_SSR_VISUAL_TRANSCRIPTION_CORRIGENDUM", "kind")
    require_equal(correction["corrects"], {
        "record": "C241-L64",
        "field": "original_row.printed_designator",
        "legacy_value": "A OMEGA 1",
        "correct_value": "OMEGA 1",
        "legacy_record_immutable": True
    }, "correction mapping")
    s = correction["source"]
    require_equal(set(s), {"ntrs_id", "pdf_url", "pdf_sha256", "zero_based_page",
                          "printed_page", "section_year", "printed_source",
                          "launch_printed", "decay_printed", "visual_inspection"},
                  "source fields")
    for name, value in {
        "ntrs_id": "19640003479",
        "pdf_url": "https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf",
        "pdf_sha256": PDF_SHA,
        "zero_based_page": 16,
        "printed_page": 15,
        "section_year": "1962 LAUNCHES (CONT'D)",
        "printed_source": "US",
        "launch_printed": "18 JUN",
        "decay_printed": "29-30 OCT 63"
    }.items():
        require_equal(s[name], value, "source." + name)
    if not isinstance(s["visual_inspection"], str) or not all(
        part in s["visual_inspection"] for part in
        ("OMEGA 1", "OMEGA 2", "OMEGA 3", "A BETA 1")
    ):
        raise ValueError("adjacent page labels not documented")
    d = correction["disambiguation"]
    require_equal(set(d), {"correct_us_label", "other_label", "other_country",
                          "other_launch_date", "other_identification",
                          "other_reference", "other_reference_class",
                          "primary_norad_id_printed", "crosswalk_norad_308"},
                  "disambiguation fields")
    for key, value in {
        "correct_us_label": "1962 OMEGA 1",
        "other_label": "1962 A OMEGA 1",
        "other_country": "USSR",
        "other_launch_date": "1962-09-27",
        "other_identification": "Cosmos 9",
        "other_reference": "https://planet4589.org/space/un/un_taba1.html",
        "other_reference_class": "SECONDARY_UN_INDEX",
        "primary_norad_id_printed": None,
        "crosswalk_norad_308": "SECONDARY_ONLY"
    }.items():
        require_equal(d[key], value, "disambiguation." + key)
    require_equal(correction["inference"], {
        "new_independent_sensor_observations": 0,
        "actual_terminal_utc": None,
        "terminal_sigma_hours": None,
        "historical_mcmc": "NOT_RUN",
        "active_constraint_528": False,
        "impact_geography": None
    }, "inference")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", type=Path, default=L64)
    parser.add_argument("--correction", type=Path, default=L65)
    args = parser.parse_args()
    validate(load(args.legacy), load(args.correction))
    print("C241-L65 PASS: 1962 OMEGA 1 (US), not 1962 A OMEGA 1 (USSR); "
          "NORAD 308 crosswalk still secondary; no terminal UTC or posterior")


if __name__ == "__main__":
    main()
