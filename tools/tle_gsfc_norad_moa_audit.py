#!/usr/bin/env python3
"""Audit 1962 institutional transfer agreement, not a physical orbit observation."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/gsfc_norad_moa_1962_C241-L24.json"
PARENT = ROOT / "research/tle_custody/congressional_ssr_chain_C241-L20.json"
URL = ("https://www.govinfo.gov/content/pkg/SERIALSET-12667_05_00-002-0197-0000/"
       "pdf/SERIALSET-12667_05_00-002-0197-0000.pdf")
SHA = "a08b4c505a37c09d1eb9c33ed14cc56228fd5e67f7ec1645f38554310bd60ca0"
EDGES = [
    ("NAVSPASUR", "GSFC", "SCIENTIFIC_LAUNCH_STATION_TIME_ANGLE_REQUEST",
     "NOMINAL_SIX_HOURS_CONDITIONAL", 15),
    ("NORAD_SPADATS", "GSFC", "PERIODIC_UNCLASSIFIED_CATALOG",
     "CATALOG_NOT_RAW_OBSERVATION", 16),
    ("GSFC_SIN", "NORAD", "ROUTINE_REDUCED_OBSERVATIONS",
     "DIRECTION_GSFC_TO_NORAD", 16),
    ("NORAD_SENSORS", "GSFC", "ON_REQUEST_SENSOR_DATA",
     "NASA_TRACKED_OBJECTS_USUALLY_FIRST_EIGHT_ORBITS", 16),
    ("NORAD_HEADQUARTERS", "GSFC", "CLASSIFICATION_RELEASE_GATE",
     "NEED_TO_KNOW_NOT_PROOF_OF_528_CLASSIFICATION", 16),
]
FIELDS = {"norad", "observation_id", "station", "sensor", "epoch_utc", "frame", "sigma"}

def validate(data: dict, parent: dict, pdf: Path | None = None) -> dict:
    doc = data.get("document", {})
    expected_doc = {
        "title": "Satellite Information from the National Aeronautics and Space Administration",
        "report": "H. Rept. 89-197", "published_on": "1965-03-22",
        "url": URL, "pdf_bytes": 9297493, "pdf_sha256": SHA,
        "pdf_pages_human": [21,22], "pdf_pages_index_zero": [20,21],
        "printed_pages": [15,16], "visual_review": "2026-11-13",
        "exhibit": "5", "agreement_date": "1962-05",
        "parent_id": "C241-L20#1",
        "effective_for_object_1963_003": "NOT_ESTABLISHED",
    }
    if (data.get("id"), data.get("kind"), doc) != (
        "C241-L24#1", "institutional_channel_not_object_measurement",
        expected_doc
    ):
        raise ValueError("document provenance, scope, date, page or digest mismatch")
    if (
        parent.get("id") != "C241-L20#1"
        or parent.get("url") != URL
        or parent.get("pdf_bytes") != 9297493
        or parent.get("pdf_sha256") != SHA
        or parent.get("historical_agreement_on") != "1961-11-07"
    ):
        raise ValueError("parent document lineage does not match")
    channels = data.get("channels")
    if not isinstance(channels, list) or len(channels) != len(EDGES):
        raise ValueError("missing or duplicate institutional channel")
    for index, (edge, expected) in enumerate(zip(channels, EDGES), start=1):
        if not isinstance(edge, dict) or edge != {
            "id": f"C241-L24:channel-{index}",
            "from": expected[0], "to": expected[1],
            "relation": expected[2], "qualifier": expected[3],
            "printed_page": expected[4],
        }:
            raise ValueError(f"changed direction, condition or identity: {index}")
    if data.get("navspasur_nominal_hours") != 6:
        raise ValueError("changed conditional six-hour scope")
    objects = data.get("objects")
    if not isinstance(objects, list) or len(objects) != 3:
        raise ValueError("missing per-object unknowns")
    for n, record in zip((527, 528, 529), objects):
        if (
            not isinstance(record, dict)
            or set(record) != FIELDS
            or record.get("norad") != n
            or any(v is not None for k,v in record.items() if k != "norad")
        ):
            raise ValueError("unverified 1963 observation artificially activated")
    if (
        data.get("independence") != "SAME_DOCUMENT_FAMILY_AS_C241-L20"
        or data.get("activation") != "CONNECTED_PENDING_CALIBRATION"
        or data.get("physical_domain_effect") != "THETA_UNCHANGED"
        or data.get("archive_targets") != [
            "NORAD/SPADATS 1963-003 catalog transmission to GSFC",
            "GSFC requests and NAVSPASUR station-time-angle observations keyed to 527/528/529",
            "GSFC SIN reduced observations and NORAD sensor-data requests for 1963-003",
        ]
    ):
        raise ValueError("institutional source misrepresented as physical evidence")
    replayed = False
    if pdf is not None:
        digest = hashlib.sha256()
        size = 0
        with pdf.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
                size += len(block)
        if size != 9297493 or digest.hexdigest() != SHA:
            raise ValueError("original PDF bytes changed or incomplete")
        replayed = True
    return {
        "occurrence": data["id"], "pdf_replayed": replayed,
        "channels_connected": len(channels), "new_independent_sources": 0,
        "new_instrumental_observations": 0, "physical_constraints_activated": 0
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--parent", type=Path, default=PARENT)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = validate(json.loads(args.ledger.read_text(encoding="utf-8")),
                      json.loads(args.parent.read_text(encoding="utf-8")), args.pdf)
    text = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
