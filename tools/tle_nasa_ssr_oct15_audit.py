#!/usr/bin/env python3
"""C241-L12: pinned 1963 NASA SSR facsimile vs reported catalog values.

Human transcriptions are checked for internal consistency only. Bytes/hash do
not establish that a human transcription is correct or independent of NORAD.
"""
import argparse
import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

SOURCE_SHA = "826f260524f6a7b83695e5c01d383025ff0da884656ebcc7fb98a1408c698ce3"
EXPECTED_ROWS = (
    ("1963-003A", "1963 3A", "94.6", "81.89", 531, 462),
    ("1963-003B", "1963 3B", "92.4", "81.87", 401, 376),
    ("1963-003C", "1963 3C", "93.3", "81.87", 458, 408),
)


def validate_ledger(ledger):
    src = ledger.get("source", {})
    ep = ledger.get("epistemic", {})
    if ledger.get("record_id") != "C241-L12":
        raise ValueError("unexpected evidence record")
    if src.get("ntrs_id") != "19640000428":
        raise ValueError("wrong NTRS source")
    if src.get("pdf_url") != ("https://ntrs.nasa.gov/api/citations/"
                              "19640000428/downloads/19640000428.pdf"):
        raise ValueError("source URL mismatch")
    if src.get("sha256") != SOURCE_SHA or src.get("bytes") != 282624:
        raise ValueError("unpinned facsimile bytes")
    if (src.get("volume"), src.get("number"), src.get("page_index_zero_based"),
        src.get("page_in_pdf_one_based"), src.get("page_printed")) != (3, 20, 6, 7, 5):
        raise ValueError("wrong volume/page provenance")
    if (src.get("report_number_printed"), src.get("ntrs_metadata_report_number"),
        src.get("report_number_disagreement")) != (
            "X-533-63-1", "X-583-63-1", "UNRESOLVED_INDEX_VS_FACSIMILE"):
        raise ValueError("document/metadata disagreement must remain explicit")
    if src.get("transcription_method") != "HUMAN_VISUAL_FACSIMILE_NOT_PDF_TEXT_EXTRACTION":
        raise ValueError("must not claim machine image verification")
    if src.get("printed_table") != "OBJECTS IN ORBIT":
        raise ValueError("wrong historical table type")
    if date.fromisoformat(src["publication_date"]) != date(1963, 10, 15):
        raise ValueError("unexpected publication date")
    rows = ledger.get("catalog_rows")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("require precisely three original rows")
    seen = set()
    converted = []
    for row, expected in zip(rows, EXPECTED_ROWS):
        current = (row.get("international_designator"), row.get("printed"),
                   row.get("nodal_period_min_printed"), row.get("inclination_deg_printed"),
                   row.get("apogee_km_printed"), row.get("perigee_km_printed"))
        if current != expected:
            raise ValueError("visual transcription differs from reviewed rows")
        if row["international_designator"] in seen:
            raise ValueError("duplicate designator")
        seen.add(row["international_designator"])
        if row.get("source") != "US" or row.get("launch") != "1963-01-16":
            raise ValueError("wrong publication row source/launch")
        period = Decimal(row["nodal_period_min_printed"])
        if period <= 0 or not (0 < row["perigee_km_printed"] <= row["apogee_km_printed"]):
            raise ValueError("invalid printed orbital fields")
        converted.append({
            "international_designator": row["international_designator"],
            "nodal_period_min_as_printed": str(period),
            "nodal_cycles_per_day_reciprocal_not_tle_mean_motion": str(
                Decimal(1440) / period),
        })
    cross = ledger.get("cross_edition", {})
    if (cross.get("later_ntrs_id"), cross.get("later_publication_date"),
        cross.get("later_reported_1963_3B_decay_day"),
        cross.get("edition_21"), cross.get("instrumental_independence")) != (
            "19640001198", "1963-11-15", "1963-11-08",
            "NOT_RECOVERED", "NOT_ESTABLISHED"):
        raise ValueError("cross-edition chronology or independence misreported")
    if not (date(1963, 10, 15) < date.fromisoformat(
            cross["later_reported_1963_3B_decay_day"]) < date(1963, 11, 15)):
        raise ValueError("chronology reversed")
    for key in ("raw_tle_pairs", "historical_tle_checksum", "raan_deg",
                "physical_reference_frame", "observation_epoch", "sensor", "sigma",
                "terminal_time", "terminal_location", "physical_identity_528"):
        if ep.get(key) is not None:
            raise ValueError("unsourced physical field: " + key)
    for key in ("legacy_raan_2841520_as_observation",
                "secondary_raan_1985261_as_primary", "publication_is_tracking_epoch"):
        if ep.get(key) is not False:
            raise ValueError("independence or observation falsely promoted: " + key)
    if (ep.get("lean_physical_constraint"), ep.get("graph_state"),
        ep.get("conde_outcome")) != (
            "NOT_PROMOTED", "CONNECTED_PENDING_CALIBRATION", "INDETERMINATE"):
        raise ValueError("premature physical conclusion")
    return converted


def audit(ledger, pdf_bytes):
    rows = validate_ledger(ledger)
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("not a PDF")
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    if digest != SOURCE_SHA or len(pdf_bytes) != 282624:
        raise ValueError("NASA facsimile hash or byte-count mismatch")
    return {
        "record_id": "C241-L12",
        "source": ledger["source"]["pdf_url"],
        "source_sha256": digest,
        "source_bytes": len(pdf_bytes),
        "catalog_rows": rows,
        "transcription_verified_by_pixels_in_ci": False,
        "metadata_number_conflict": "X-533-63-1_PRINT_VS_X-583-63-1_NTRS",
        "catalog_1963_3B_in_orbit_in_oct15_issue": True,
        "catalog_1963_3B_decay_day_reported_nov15": "1963-11-08",
        "historical_tle_available": False,
        "observed_terminal_state": None,
        "evidence_independence": "NOT_ESTABLISHED",
        "graph_state": "CONNECTED_PENDING_CALIBRATION",
        "conde_outcome": "INDETERMINATE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    report = audit(ledger, args.pdf.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
                           + "\n", encoding="utf-8")
    print("C241-L12: verified one NASA facsimile; three documentary rows")


if __name__ == "__main__":
    main()
