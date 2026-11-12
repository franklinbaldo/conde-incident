#!/usr/bin/env python3
"""Audit COS EOR-delimited payload sizes, NOT NMC ON20 soundings.

This does NOT decode ON20, WMO station IDs, dates, levels, or measurements.
Control-word offsets and lengths refer to the original archive bytes.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from audit_nmc_y20175_cos import inspect, BlockingError

MAX_WORD_BYTES = 8


def percentile(values, percent):
    """Nearest-rank-like order statistic at floor(p*(n-1)), defined precisely."""
    return values[(len(values) - 1) * percent // 100]


def audit(path, custody):
    # The existing auditor validates *all* COS structural links and raw SHA first.
    verified = inspect(
        path,
        expected_sha256=custody.get("archive_sha256"),
        expected_size=custody.get("archive_bytes"),
    )
    raw_digest = hashlib.sha256()
    lengths = []
    sample = []
    eof_locations = []
    last_eor_offset = None
    payload_length = 0
    pending_length = 0
    idx = 0
    with Path(path).open("rb") as stream:
        while True:
            stream.seek(idx * MAX_WORD_BYTES)
            word = int.from_bytes(stream.read(MAX_WORD_BYTES), "big")
            marker = word >> 60
            fwi = word & 0x1FF
            offset = idx * MAX_WORD_BYTES

            if marker == 8:
                last_eor_offset = offset
                ordinal = len(lengths) + 1
                lengths.append(pending_length)
                if ordinal <= 5:
                    sample.append({
                        "ordinal": ordinal,
                        "eor_byte_offset": offset,
                        "payload_bytes_before_eor": pending_length,
                    })
                pending_length = 0
            elif marker == 14:
                eof_locations.append({
                    "byte_offset": offset,
                    "eor_markers_seen": len(lengths),
                    "pending_payload_bytes": pending_length,
                })
            elif marker == 15:
                break

            stream.seek(offset + MAX_WORD_BYTES)
            payload = stream.read(fwi * MAX_WORD_BYTES)
            if len(payload) != fwi * MAX_WORD_BYTES:
                raise BlockingError("short payload read")
            raw_digest.update(payload)
            payload_length += len(payload)
            pending_length += len(payload)
            idx += fwi + 1

    if len(lengths) != verified["controls"]["EOR"]:
        raise BlockingError("EOR coverage mismatch")
    if len(eof_locations) != verified["controls"]["EOF"]:
        raise BlockingError("EOF coverage mismatch")
    if pending_length:
        raise BlockingError("payload after last EOR is unassigned")
    if sum(lengths) != payload_length:
        raise BlockingError("payload bytes differ from EOR sum")

    distribution = Counter(lengths)
    ordered = sorted(lengths)
    report = {
        "schema": "conde.nmc-y20175-cos-payload-sizes/v1",
        "inventory_id": "MET-NMC-COS-LENGTHS-20261112-01",
        "upstream_custody_id": "MET-NMC-COS-20261112-01",
        "archive_bytes": verified["archive_bytes"],
        "archive_sha256": verified["archive_sha256"],
        "source_url": "https://osdf-director.osg-htc.org/ncar-gdex/d353000/Y20175",
        "dataset_doi": "10.5065/R592-TX59",
        "size_unit": "bytes of COS payload words excluding BCW/RCW controls",
        "eor_delimited_payloads": len(lengths),
        "total_payload_bytes": payload_length,
        "payload_stream_sha256": raw_digest.hexdigest(),
        "distinct_payload_lengths": len(distribution),
        "min_payload_bytes": ordered[0],
        "max_payload_bytes": ordered[-1],
        "percentiles_floor_index": {
            str(p): percentile(ordered, p) for p in (1, 5, 10, 25, 50, 75, 90, 95, 99)
        },
        "length_histogram": {
            str(length): distribution[length] for length in sorted(distribution)
        },
        "first_five_eor": sample,
        "eof_markers": eof_locations,
        "last_eor": {
            "ordinal": len(lengths),
            "byte_offset": last_eor_offset,
            "payload_bytes_before_eor": lengths[-1],
        },
        "source_semantics": "COS_EOR_DELIMITED_PAYLOAD_NOT_WEATHER_REPORT",
        "on20_station_record_decoding": "NOT_RUN",
        "station_day_matches": None,
        "station_day_absences": None,
        "orbital_constraint": "NOT_ACTIVATED",
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    custody = json.loads(args.manifest.read_text(encoding="utf8"))
    try:
        result = audit(args.file, custody)
    except BlockingError as exc:
        parser.exit(2, "COS_LENGTH_AUDIT_FAIL: %s\n" % exc)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
