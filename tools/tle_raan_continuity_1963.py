#!/usr/bin/env python3
"""C241-L4: circular RAAN differences and gaps in a pinned SECONDARY mirror.

Finite differences are descriptive catalog arithmetic, never physical
precession estimates. No historical frame, sensor covariance, orbit fit,
terminal observation or impact is inferred.
"""
import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cross_object_epoch_support import (FIELDS, SOURCE_URL, SOURCE_SHA256,
                                        EXPECTED_CSV_SHA256, normalize, read_pinned_csv)
from tle_literal_layout import MIRROR_SHA256, audit_literal_file

DAY_US = 86_400_000_000
QUANTUM_HALF_US = 432
LEGACY_RAAN_DEG = 284.1520  # FORENSIC ONLY: unproven site vector, NOT observation
NASA_DECAY_DAY = datetime(1963, 11, 8, tzinfo=timezone.utc)
NASA_DOCUMENT = "https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf"


def elapsed_us(a, b):
    return (b - a) // timedelta(microseconds=1)


def iso(t):
    return t.isoformat(timespec="microseconds").replace("+00:00", "Z")


def short_arc_deg(a, b):
    """Signed shortest circular arc; a half-circle has no unique sign."""
    if not (math.isfinite(a) and math.isfinite(b) and
            0 <= a < 360 and 0 <= b < 360):
        raise ValueError("invalid RAAN range or non-finite input")
    value = (b - a + 180) % 360 - 180
    if math.isclose(abs(value), 180, abs_tol=1e-10):
        raise ValueError("ambiguous 180-degree circular direction")
    return value


def audit_series(series, literal_epoch, literal_raan, *, expected_epochs=None):
    """Audit normalized 528 entries; each entry carries its original source_rows."""
    if expected_epochs is not None and len(series) != expected_epochs:
        raise ValueError("pinned 528 epoch count changed")
    if len(series) < 2:
        raise ValueError("at least two 528 epochs required")
    raan_index = FIELDS.index("raan")
    normalized = []
    seen_rows = set()
    for item in series:
        t = item["epoch"]
        if (not isinstance(t, datetime) or t.tzinfo is None or
                t.utcoffset() != timedelta(0) or t.year != 1963):
            raise ValueError("invalid 1963 UTC epoch")
        ids = item["source_rows"]
        if not ids or any(not isinstance(i, int) or i < 0 or i in seen_rows for i in ids):
            raise ValueError("duplicate or invalid source_row")
        seen_rows.update(ids)
        raan = float(item["state"][raan_index])
        short_arc_deg(raan, raan)  # validate finite and angular range
        normalized.append((t, min(ids), sorted(ids), raan))
    normalized.sort()
    intervals = []
    for a, b in zip(normalized, normalized[1:]):
        dt = elapsed_us(a[0], b[0])
        if dt <= 0:
            raise ValueError("duplicate/conflicting 528 UTC epoch")
        arc = short_arc_deg(a[3], b[3])
        intervals.append({
            "from_source_rows": a[2], "to_source_rows": b[2],
            "from_epoch_utc": iso(a[0]), "to_epoch_utc": iso(b[0]),
            "gap_microseconds": dt, "gap_days": dt / DAY_US,
            "shortest_signed_RAAN_delta_deg": arc,
            "arithmetic_secant_deg_per_day": arc * DAY_US / dt,
            "meaning": "DESCRIPTIVE_CIRCULAR_DIFFERENCE_NOT_ORBIT_PROPAGATION",
        })
    if (not isinstance(literal_epoch, datetime) or literal_epoch.tzinfo is None or
            literal_epoch.utcoffset() != timedelta(0) or literal_epoch.year != 1963):
        raise ValueError("invalid literal UTC epoch")
    short_arc_deg(literal_raan, literal_raan)
    same_epoch = [x for x in normalized
                  if abs(elapsed_us(x[0], literal_epoch)) <= QUANTUM_HALF_US]
    if len(same_epoch) != 1:
        raise ValueError("secondary literal epoch missing/ambiguous within 432 us")
    if abs(short_arc_deg(same_epoch[0][3], literal_raan)) > 0.00006:
        raise ValueError("secondary literal RAAN disagrees with numeric mirror")
    last_epoch = normalized[-1][0]
    if last_epoch >= NASA_DECAY_DAY:
        raise ValueError("last numeric epoch is not before NASA date-only decay")
    nearest = min(normalized, key=lambda x: (
        abs(short_arc_deg(x[3], LEGACY_RAAN_DEG)), x[0], x[1]))
    maximum = max(intervals, key=lambda x: x["gap_microseconds"])
    return {
        "id": "C241-L4",
        "status": "CONNECTED_PENDING_CALIBRATION",
        "samples": len(normalized),
        "adjacent_intervals": len(intervals),
        "first_epoch_utc": iso(normalized[0][0]),
        "last_epoch_utc": iso(last_epoch),
        "max_gap_days": maximum["gap_days"],
        "max_gap_source_rows": [maximum["from_source_rows"], maximum["to_source_rows"]],
        "intervals_at_most_24h": sum(x["gap_microseconds"] <= DAY_US for x in intervals),
        "intervals_over_72h": sum(x["gap_microseconds"] > 3 * DAY_US for x in intervals),
        "days_last_record_to_NASA_date_only": {
            "at_1963_11_08_00UTC": elapsed_us(last_epoch, NASA_DECAY_DAY) / DAY_US,
            "before_1963_11_09_00UTC": elapsed_us(
                last_epoch, NASA_DECAY_DAY + timedelta(days=1)) / DAY_US,
        },
        "literal_528": {
            "epoch_utc": iso(literal_epoch), "raan_deg": literal_raan,
            "same_epoch_source_rows": same_epoch[0][2],
            "delta_epoch_microseconds": elapsed_us(same_epoch[0][0], literal_epoch),
            "delta_raan_deg": short_arc_deg(same_epoch[0][3], literal_raan),
        },
        "legacy_284_1520_FORENSIC_NOT_OBSERVATION": {
            "angle_deg": LEGACY_RAAN_DEG,
            "source": None, "status": "UNPROVEN_INACTIVE",
            "difference_from_literal_deg": abs(short_arc_deg(literal_raan, LEGACY_RAAN_DEG)),
            "nearest_secondary_by_angle_ONLY": {
                "source_rows": nearest[2], "epoch_utc": iso(nearest[0]),
                "raan_deg": nearest[3],
                "angular_distance_deg": abs(short_arc_deg(nearest[3], LEGACY_RAAN_DEG)),
            },
        },
        "intervals": intervals,
        "constraint_link": {
            "catalog_observable": "delta_RAAN_short = wrap(raan_next - raan_prev)",
            "epochs_unit": "UTC microseconds", "RAAN_unit": "degrees",
            "candidate_model_observable": "RAAN(t_next; theta) - RAAN(t_prev; theta)",
            "historical_reference_frame": None,
            "sensor_error_covariance": None,
            "independent_primary_TLEs": None,
            "physics_predicate_Lean_4_35_0": "NOT_PROMOTED",
            "admissible_domain_delta": "NOT_COMPUTED",
            "simulation_holdouts": "NOT_RUN",
            "reason": "Historical frame, original TLE lines, sensor errors and independent tracking missing",
        },
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", required=True, type=Path)
    p.add_argument("--pair", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    groups, counts = normalize(read_pinned_csv(args.csv))  # SHA-pinned 123 source rows
    if counts != {527: 21, 528: 45, 529: 57}:
        raise ValueError("pinned source counts changed")
    literal = audit_literal_file(args.pair)  # 69-column checksums + pinned LF/bytes
    t = datetime.fromisoformat(literal["epoch_utc"].replace("Z", "+00:00"))
    report = audit_series(groups[528], t, float(literal["values"]["raan"]["decimal"]),
                          expected_epochs=45)
    report["provenance"] = {
        "secondary_parquet_url": SOURCE_URL,
        "secondary_parquet_SHA256": SOURCE_SHA256,
        "derived_123_row_csv_SHA256": EXPECTED_CSV_SHA256,
        "secondary_literal_528_SHA256": MIRROR_SHA256,
        "NASA_day_only_document": NASA_DOCUMENT,
        "source_family": "MODERN_CATALOG_MIRRORS_INDEPENDENCE_NOT_ESTABLISHED",
        "original_45_TLE_pairs_checksum_frame_error": "NOT_RECOVERED",
        "object_528_material_identity": "NOT_VERIFIED",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "samples", "adjacent_intervals", "max_gap_days",
        "intervals_at_most_24h", "intervals_over_72h")}, sort_keys=True))


if __name__ == "__main__":
    main()
