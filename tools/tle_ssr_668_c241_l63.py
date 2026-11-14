#!/usr/bin/env python3
"""C241-L63: verify contemporary catalogue decay day, not physical terminal time."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_terminal_control_668_C241-L63.json"
SHA = "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2"
URL = "https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf"
EMPTY = ("terminal_utc", "terminal_time_interval", "instrumental_station",
         "sensor", "error_sigma", "raw_tle", "original_observation")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key " + key)
        result[key] = value
    return result


def load(path=LEDGER):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object)


def exact(actual, fields, label):
    if type(actual) is not dict or set(actual) != set(fields):
        raise ValueError(label + " schema")
    for key, expected in fields.items():
        if type(actual[key]) is not type(expected) or actual[key] != expected:
            raise ValueError(label + ": " + key)


def validate(data):
    if type(data) is not dict or set(data) != {
        "id", "kind", "source", "catalogue_day", "lineage",
        "unresolved_control", "inference"
    }:
        raise ValueError("root schema")
    if data["id"] != "C241-L63" or data["kind"] != "NASA_SSR_CONTEMPORARY_DECAY_DAY_CONTROL":
        raise ValueError("ledger identity")
    exact(data["source"], {
        "ntrs_id": "19640000428", "publication": "1963-10-15",
        "series": "NASA GSFC Satellite Situation Report, volume 3, number 20",
        "pdf_url": URL, "pdf_sha256": SHA, "pdf_bytes": 286417, "pdf_pages": 9,
        "zero_based_page": 8, "printed_page": 7,
        "section": "PLEASE ADD THE FOLLOWING TO THE DECAYED OBJECTS LIST",
        "preexisting_same_publication": "C241-L12",
        "independently_observed_sensor": False
    }, "source")
    exact(data["catalogue_day"], {
        "printed_designator": "1963 37 A", "printed_norad_id": None,
        "secondary_norad_id": 668, "secondary_designator": "1963-037A",
        "secondary_crosswalk": "https://keeptrack.space/satellite/668",
        "source": "US", "launch_printed": "24 SEP", "decay_printed": "12 OCT 63",
        "decay_calendar_date": "1963-10-12", "time_precision": "CALENDAR_DAY_LABEL_ONLY",
        **{key: None for key in EMPTY}
    }, "catalogue_day")
    exact(data["lineage"], {
        "related_un_inventory": "https://www.unoosa.org/documents/pdf/inf055E.pdf",
        "related_un_label": "1963-37A", "related_un_cutoff": "2400Z 15 OCTOBER 1963",
        "related_un_occurrence": "C241-L33",
        "independently_corroborated_sensor": False,
        "independence_of_nasa_and_un": False,
        "independent_original_668_observations": 0
    }, "lineage")
    exact(data["unresolved_control"], {
        "secondary_norad_id": 308, "secondary_catalogue_day": "1963-10-30",
        "source": "https://keeptrack.space/satellite/308",
        "primary_day": "NOT_RECOVERED", "primary_terminal_utc": None,
        "original_sensor_log": None
    }, "unresolved_control")
    exact(data["inference"], {
        "novel_primary_publications": 0, "original_sensor_observations_added": 0,
        "calibrated_terminal_times_added": 0, "historical_528_constraints_added": 0,
        "atmospheric_model_update": False, "conde_impact_demonstrated": False
    }, "inference")
    return True


def verify_pdf(path):
    blob = Path(path).read_bytes()
    if not blob.startswith(b"%PDF-") or len(blob) != 286417 or hashlib.sha256(blob).hexdigest() != SHA:
        raise ValueError("unreviewed PDF variant or source integrity mismatch")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    validate(load())
    if args.pdf is not None:
        verify_pdf(args.pdf)
    print("C241-L63 VERIFIED: 1963 37 A / 12 OCT 63 (catalogue day); "
          "0 sensors, 0 terminal UTC, 0 constraints on 528")


if __name__ == "__main__":
    main()
