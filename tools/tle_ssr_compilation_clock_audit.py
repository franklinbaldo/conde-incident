#!/usr/bin/env python3
"""C241-L15: NASA SSR compilation clock is not an orbital sensor epoch."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

EXPECTED = (
    ("19640000428", 20, "1963-10-15", "C241-L12",
     "DOCUMENTARY_CATALOGUE_IN_ORBIT_1963_3B", (
         ("826f260524f6a7b83695e5c01d383025ff0da884656ebcc7fb98a1408c698ce3", 282624),
         ("fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2", 286417))),
    ("19640001198", 22, "1963-11-15", "C241-L11",
     "DOCUMENTARY_ADDITION_TO_DECAY_LIST_1963_3B_DAY_1963_11_08", (
         ("0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674", 327613),)),
    ("19640002493", 23, "1963-11-30", "C241-L11",
     "DOCUMENTARY_NO_REPEAT_IN_INCREMENTAL_DECAY_ADDITIONS", (
         ("9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d", 1266393),)),
)
FAMILY = "NASA_GODDARD_NORAD_SMITHSONIAN_COMPILED_SERIES"
INDEPENDENCE = "ONE_COMPILATION_FAMILY_NOT_THREE_SENSOR_OBSERVATIONS"


def validate_ledger(d):
    if d.get("record_id") != "C241-L15" or d.get("source_family") != FAMILY:
        raise ValueError("wrong evidence ID or lineage family")
    if d.get("independence") != INDEPENDENCE:
        raise ValueError("source independence overclaimed")
    sources = d.get("sources")
    if not isinstance(sources, list) or len(sources) != len(EXPECTED):
        raise ValueError("incomplete edition lineage")
    for s, (ntrs, number, day, occurrence, claim, hashes) in zip(sources, EXPECTED):
        expected_asof = f"{day}T12:00:00Z"
        if (s.get("ntrs_id"), s.get("volume"), s.get("number"),
            s.get("publication_date"), s.get("compilation_as_of_utc"),
            s.get("catalogue_occurrence"), s.get("claim_class")) != (
                ntrs, 3, number, day, expected_asof, occurrence, claim):
            raise ValueError("edition metadata or 1200Z snapshot clock altered")
        if (s.get("url") != f"https://ntrs.nasa.gov/api/citations/{ntrs}/downloads/{ntrs}.pdf"
            or s.get("pdf_page_index_zero_based") != 1
            or s.get("pdf_page_one_based") != 2
            or s.get("facsimile_reading") != "HUMAN_VISUAL_NOT_OCR"):
            raise ValueError("facsimile page, URL or reading provenance altered")
        if s.get("accepted_download_sha256_and_bytes") != [list(x) for x in hashes]:
            raise ValueError("source digest allowlist changed")
        t = datetime.fromisoformat(expected_asof.replace("Z", "+00:00"))
        if t.tzinfo != timezone.utc or t.date().isoformat() != day:
            raise ValueError("invalid compilation timestamp")
    edge = d.get("graph_edge", {})
    if (edge.get("id"), edge.get("from"), edge.get("to"),
        edge.get("relation"), edge.get("state")) != (
            "C241-L15:SSR_SNAPSHOT_CLOCK_VS_PHYSICAL_OBSERVATION_EPOCH",
            "NASA_SSR_COMPILED_AT_1200Z", "TRACKING_MEASUREMENT_EPOCH_UNKNOWN",
            "EDITORIAL_SNAPSHOT_DOES_NOT_IDENTIFY_UPSTREAM_SENSOR_TIME",
            "CONNECTED_PENDING_CALIBRATION"):
        raise ValueError("wrong provenance/observability edge")
    if edge.get("pending") != ["ORIGINAL_SENSOR_RECORD", "EPOCH_OF_MEASUREMENT",
                                "INSTRUMENT_AND_STATION", "ERROR_MODEL", "TLE_LINEAGE"]:
        raise ValueError("missing bridge to physical observation")
    missing = d.get("missing", {})
    if missing.get("edition_21") != "NOT_RECOVERED":
        raise ValueError("missing edition 21 must not be invented")
    for key in ("physical_observation_epoch", "sensor_station", "frame",
                "historical_tle_checksums", "sigma", "physical_identity_528",
                "terminal_time", "terminal_position", "original_raan_284_1520",
                "primary_raan_198_5261"):
        if key not in missing or missing[key] is not None:
            raise ValueError("unsourced physical field: " + key)
    for key in ("earth_impact_claim", "tle_from_ssr",
                "one_independent_measurement_per_issue", "legacy_raan_activated"):
        if missing.get(key) is not False:
            raise ValueError("unsupported physical assertion: " + key)
    if (missing.get("lean_physical_constraint"), missing.get("conde_outcome")) != (
            "NOT_PROMOTED", "INDETERMINATE"):
        raise ValueError("unsupported conclusion")
    return sources


def audit(ledger, pdf_by_ntrs):
    sources = validate_ledger(ledger)
    if set(pdf_by_ntrs) != {s["ntrs_id"] for s in sources}:
        raise ValueError("missing or unexpected PDF input")
    captures = []
    for s in sources:
        raw = pdf_by_ntrs[s["ntrs_id"]]
        if not raw.startswith(b"%PDF-"):
            raise ValueError("not a PDF: " + s["ntrs_id"])
        digest = hashlib.sha256(raw).hexdigest()
        size = len(raw)
        if [digest, size] not in s["accepted_download_sha256_and_bytes"]:
            raise ValueError("unrecognized NASA PDF bytes: " + s["ntrs_id"])
        captures.append({"ntrs_id": s["ntrs_id"], "sha256": digest,
                         "bytes": size, "compilation_as_of_utc": s["compilation_as_of_utc"],
                         "physical_observation_epoch": None, "source_independence": INDEPENDENCE})
    return {"record_id": "C241-L15", "captures": captures, "source_family_count": 1,
            "instrumental_epoch_count": None,
            "pixel_transcription_reproduced_by_ci": False,
            "graph_state": "CONNECTED_PENDING_CALIBRATION",
            "original_tle_recovered": False, "terminal_position": None,
            "conde_outcome": "INDETERMINATE"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--oct15", type=Path, required=True)
    p.add_argument("--nov15", type=Path, required=True)
    p.add_argument("--nov30", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    ledger = json.loads(a.ledger.read_text(encoding="utf-8"))
    report = audit(ledger, {"19640000428": a.oct15.read_bytes(),
                            "19640001198": a.nov15.read_bytes(),
                            "19640002493": a.nov30.read_bytes()})
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("C241-L15: 3 publication snapshots audited; physical sensor epochs unknown")


if __name__ == "__main__":
    main()
