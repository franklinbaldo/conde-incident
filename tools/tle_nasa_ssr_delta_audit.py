#!/usr/bin/env python3
"""Verify bytes/lineage of two NASA SSR facsimiles, never infer terminal orbit.

Tables are HUMAN VISUAL transcriptions of scans; hashes verify only bytes.
"""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

EXPECTED_IDS = ("19640001198", "19640002493")


def validate(ledger, source_files):
    if ledger.get("record_id") != "C241-L11" or ledger.get("catalog_object") != "1963-003B":
        raise ValueError("unexpected ledger identity")
    sources = ledger.get("sources")
    if not isinstance(sources, list) or tuple(r.get("ntrs_id") for r in sources) != EXPECTED_IDS:
        raise ValueError("NASA issue sequence must remain fixed")
    if len(source_files) != len(sources):
        raise ValueError("need both NASA PDF files")
    checked = []
    for row, path in zip(sources, source_files):
        payload = Path(path).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if not payload.startswith(b"%PDF-") or not payload.rstrip().endswith(b"%%EOF"):
            raise ValueError("not a complete PDF: " + row["ntrs_id"])
        if digest != row.get("sha256"):
            raise ValueError("PDF SHA-256 mismatch: " + row["ntrs_id"])
        if row.get("page_index_zero_based") != 9 or row.get("page_printed") != 8:
            raise ValueError("human-reviewed page reference changed")
        if row.get("reading_method") != "HUMAN_VISUAL_SCAN_NOT_MACHINE_OCR":
            raise ValueError("manual review must not be represented as machine extraction")
        if not row.get("url", "").endswith("/" + row["ntrs_id"] + ".pdf"):
            raise ValueError("NTRS URL/id mismatch")
        date.fromisoformat(row["publication_date"])
        checked.append({"ntrs_id": row["ntrs_id"], "sha256": digest,
                        "bytes": len(payload), "pdf_page": 10,
                        "printed_page": 8, "publication_date": row["publication_date"],
                        "human_table_observation": row["human_table_observation"]})
    old, new = (r["human_table_observation"] for r in sources)
    if old.get("kind") != "ADDITION_TO_DECAYED_OBJECTS_LIST" or old.get("object_printed") != "1963 3B" or old.get("decay_day") != "1963-11-08":
        raise ValueError("15 Nov visual observation changed")
    if new.get("kind") != "INCREMENTAL_DECAYED_OBJECTS_ADDITIONS" or new.get("1963_3B_in_additions") is not False:
        raise ValueError("30 Nov report must be interpreted as incremental additions")
    if date.fromisoformat(sources[0]["publication_date"]) >= date.fromisoformat(sources[1]["publication_date"]):
        raise ValueError("reversed publication chronology")
    return {
        "record_id": "C241-L11", "status": "DOCUMENTARY_CUSTODY_NOT_ORBIT_DETERMINATION",
        "checked_source_files": checked,
        "catalog_decay_day_only": "1963-11-08",
        "reporting_sequence": "15_NOV_LISTS_3B_30_NOV_ONLY_ADDITIONS_NOT_REPETITION",
        "source_independence": "SAME_NASA_SSR_SERIES_NOT_TWO_TRACKING_SENSORS",
        "human_visual_extraction_reproduced_by_ci": False,
        "physical_component_identity": None, "historical_tle_pairs": None,
        "frame": None, "measurement_sigma": None,
        "legacy_raan_284_1520_as_observation": False,
        "secondary_raan_198_5261_as_primary": False,
        "constraint": "CONNECTED_PENDING_CALIBRATION",
        "lean_physical_predicate": "NOT_PROMOTED",
        "terminal_time_or_position": None, "conde_outcome": "INDETERMINATE",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--pdf15", type=Path, required=True)
    p.add_argument("--pdf30", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = validate(json.loads(a.ledger.read_text(encoding="utf-8")), [a.pdf15, a.pdf30])
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("C241-L11", result["status"], len(result["checked_source_files"]))


if __name__ == "__main__":
    main()
