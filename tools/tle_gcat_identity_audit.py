#!/usr/bin/env python3
"""C241-L13: audit GCAT classification versus modern catalog, not a TLE."""
import argparse
import hashlib
import json
import re
from pathlib import Path

GCAT_URL = "https://planet4589.org/space/gcat/data/cat/auxcat.html"
GCAT_527 = re.compile(
    r"\bA00324\s+00527\s+1963-003\s+1963-003A\s+R2\s+"
    r"Agena\s+B\s+2313\b"
)
SOURCE_IDS = (
    "NASA_OCT15", "GCAT_AUX", "KEEPTRACK_527",
    "SECONDARY_DEB_528", "SECONDARY_DEB_529",
)
NO_PHYSICAL = (
    "physical_piece_528", "physical_piece_529", "frame_528",
    "instrumental_sigma_528", "original_tle_528", "raw_measurement_528",
)


def validate_ledger(doc):
    if doc.get("record_id") != "C241-L13":
        raise ValueError("wrong evidence record")
    sources = doc.get("sources")
    if not isinstance(sources, list) or tuple(x.get("id") for x in sources) != SOURCE_IDS:
        raise ValueError("source ordering/identity drift")
    nasa, gcat, payload, debris_b, debris_c = sources
    if (nasa.get("ntrs_id"), nasa.get("publication_date"),
        nasa.get("printed_designators"), nasa.get("physical_piece_description")) != (
        "19640000428", "1963-10-15",
        ["1963 3A", "1963 3B", "1963 3C"], None):
        raise ValueError("NASA documentary scope changed")
    if (gcat.get("url"), gcat.get("record_key"), gcat.get("catalog_number"),
        gcat.get("designation"), gcat.get("classification_code"), gcat.get("name")) != (
        GCAT_URL, "A00324", "00527", "1963-003A", "R2", "Agena B 2313"):
        raise ValueError("GCAT row classification/identity changed")
    if (payload.get("url"), payload.get("classification_label"),
        payload.get("bus_label")) != (
        "https://keeptrack.space/satellite/00527", "Payload", "SAMOS F-2"):
        raise ValueError("secondary payload label changed")
    for source, number, piece in ((debris_b, "00528", "1963-003B"),
                                  (debris_c, "00529", "1963-003C")):
        if (source.get("catalog_number"), source.get("designation"),
            source.get("classification_label"), source.get("engineering_piece")) != (
            number, piece, "Debris", None):
            raise ValueError("debris classified as authenticated component")
    if gcat.get("source_sha256") is not None or gcat.get("measurement_source") is not None:
        raise ValueError("GCAT live content or measurement incorrectly authenticated")
    if nasa.get("raw_sensor_records") is not None:
        raise ValueError("NASA situation report is not raw observation")
    c = doc.get("comparison", {})
    for field in NO_PHYSICAL:
        if c.get(field, "MISSING") is not None:
            raise ValueError("fabricated physical parameter: " + field)
    for field in ("identity_transfer_from_527_to_528",
                  "identity_transfer_from_527_to_529",
                  "classification_is_not_observation",
                  "legacy_raan_2841520_observed",
                  "secondary_raan_1985261_authenticated_primary"):
        expected = field == "classification_is_not_observation"
        if c.get(field) is not expected:
            raise ValueError("illegitimate classification/RAAN promotion: " + field)
    if c.get("gcat_auxcat_absence_is_not_global_catalog_absence") is not True:
        raise ValueError("invalid closed-world assumption about auxcat")
    if c.get("tracking_lineage_independence") != "NOT_ESTABLISHED":
        raise ValueError("catalogs cannot certify independent tracking")
    if (c.get("lean_physical_constraint"), c.get("graph_state"),
        c.get("conde_outcome")) != (
        "NOT_PROMOTED", "CONNECTED_PENDING_CALIBRATION", "INDETERMINATE"):
        raise ValueError("unjustified orbital conclusion")
    edges = doc.get("edges")
    if not isinstance(edges, list) or len(edges) != 5 or any(
        e.get("independent_sensor") is not False for e in edges
    ):
        raise ValueError("source-dependency graph has independent measurements")
    return c


def find_gcat_row(raw):
    """Validate a live auxiliary catalog *row*; not the original sensor dataset."""
    text = raw.decode("utf-8")
    matches = [line for line in text.splitlines()
               if GCAT_527.search(line)]
    if len(matches) != 1:
        raise ValueError("missing/ambiguous GCAT 00527 R2 row")
    line = matches[0]
    if "1969 Jan  9" not in line and not re.search(r"1969\s+Jan\s+9\b", line):
        raise ValueError("GCAT row missing known 527 decay-date label")
    return line.strip()


def audit(doc, raw=None):
    validate_ledger(doc)
    result = {
        "record_id": "C241-L13",
        "gcat_row_authenticated_by_live_snapshot": False,
        "gcat_source_sha256": None,
        "gcat_source_bytes": None,
        "gcat_row": None,
        "norad_528_engineering_component": None,
        "norad_529_engineering_component": None,
        "classification_conflict_implies_physical_contradiction": False,
        "instrumental_independence": "NOT_ESTABLISHED",
        "graph_state": "CONNECTED_PENDING_CALIBRATION",
        "conde_outcome": "INDETERMINATE",
    }
    if raw is not None:
        result["gcat_row"] = find_gcat_row(raw)
        result["gcat_source_sha256"] = hashlib.sha256(raw).hexdigest()
        result["gcat_source_bytes"] = len(raw)
        result["gcat_row_authenticated_by_live_snapshot"] = True
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--gcat-file", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    raw = args.gcat_file.read_bytes() if args.gcat_file else None
    report = audit(ledger, raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
                           + "\n", encoding="utf-8")
    print("C241-L13: 527 catalog-classification checked; 528/529 material identity unknown")


if __name__ == "__main__":
    main()
