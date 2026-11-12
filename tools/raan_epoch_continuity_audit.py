#!/usr/bin/env python3
"""C241-T7: finite-difference RAAN chronology in a pinned NUMERIC mirror.

No frame transformation, force model, interpolation, sensor independence,
original 1963 NORAD element authentication, or terminal prediction.
"""
import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from audit_norad_1963 import angular_distance_deg, tle_epoch_utc
from legacy_528_fingerprint import (
    EXPECTED_528_CSV_SHA256, LEGACY_LINE1, LEGACY,
    read_528_csv,
)

MIRROR_PAIR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
SOURCE_URL = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet"
NASA_SOURCE = "https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf"
US = timedelta(microseconds=1)
DAY_US = 86_400_000_000


def delta_us(left: datetime, right: datetime) -> int:
    return (right - left) // US


def stamp(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def signed_short_arc_deg(first: float, second: float) -> float:
    """Shortest circular difference, not unwrapped historical motion.

    Exactly 180 degrees has two equally short signs: fail rather than invent
    a direction. Shortest differences are *descriptive*, not a dynamical fit.
    """
    raw = (second - first + 180.0) % 360.0 - 180.0
    if abs(raw) == 180.0:
        raise ValueError("ambiguous 180-degree RAAN arc; direction unknown")
    return raw


def literal_mirror(path: Path) -> tuple[datetime, float]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MIRROR_PAIR_SHA256:
        raise ValueError("secondary literal pair SHA256 mismatch")
    first, second = raw.decode("ascii").splitlines()
    # The independent full TLE syntax gate is run by tle_literal_layout.py.
    # Here, pin the immutable bytes and compare only timestamp and RAAN.
    if first[2:7] != "00528" or second[2:7] != "00528":
        raise ValueError("secondary literal pair catalog mismatch")
    return tle_epoch_utc(first), float(second[17:25])


def audit_raan_timeline(
    rows: list[dict], source_sha: str, mirror_epoch: datetime,
    mirror_raan: float, *, required_count: int | None = None,
) -> dict:
    if required_count is not None and len(rows) != required_count:
        raise ValueError("pinned 528 epoch count changed")
    if len(rows) < 2:
        raise ValueError("need at least two distinct 528 epochs")
    # Validate timestamps BEFORE ordering: mixed naive/aware dates must raise
    # a provenance error, never an incidental Python TypeError.
    for row in rows:
        t = row["epoch_utc"]
        if (not isinstance(t, datetime) or t.tzinfo is None or
                t.utcoffset() != timedelta(0) or t.year != 1963):
            raise ValueError("invalid 1963 UTC epoch or RAAN")
    sorted_rows = sorted(rows, key=lambda x: (x["epoch_utc"], x["source_row"]))
    seen_indices = set()
    for row in sorted_rows:
        value = row["fields"]["raan"]
        t = row["epoch_utc"]
        if (not 0.0 <= value < 360.0 or t.tzinfo is None or
                t.utcoffset() != timedelta(0) or t.year != 1963):
            raise ValueError("invalid 1963 UTC epoch or RAAN")
        if row["source_row"] in seen_indices:
            raise ValueError("duplicate physical source_row")
        seen_indices.add(row["source_row"])
    intervals = []
    for older, newer in zip(sorted_rows, sorted_rows[1:]):
        dt = delta_us(older["epoch_utc"], newer["epoch_utc"])
        if dt <= 0:
            raise ValueError("duplicate/conflicting 528 epoch")
        arc = signed_short_arc_deg(older["fields"]["raan"], newer["fields"]["raan"])
        intervals.append({
            "from_source_row": older["source_row"],
            "to_source_row": newer["source_row"],
            "from_epoch_utc": stamp(older["epoch_utc"]),
            "to_epoch_utc": stamp(newer["epoch_utc"]),
            "gap_microseconds": dt,
            "gap_days": dt / DAY_US,
            "shortest_raan_delta_deg": arc,
            "shortest_raan_difference_rate_deg_per_day": arc * DAY_US / dt,
            "method": "PAIRWISE_CIRCULAR_DIFFERENCE_NOT_FITTED_MOTION",
        })
    legacy_epoch = tle_epoch_utc(LEGACY_LINE1)
    legacy_raan = LEGACY["raan"]
    nearest_raan = min(
        sorted_rows,
        key=lambda x: (angular_distance_deg(x["fields"]["raan"], legacy_raan),
                       x["epoch_utc"], x["source_row"]),
    )
    same_mirror_epoch = [x for x in sorted_rows
                         if abs(delta_us(x["epoch_utc"], mirror_epoch)) <= 432]
    if required_count == 45 and len(same_mirror_epoch) != 1:
        raise ValueError("pinned mirror 528 epoch missing or ambiguous")
    mirror_gap = delta_us(legacy_epoch, mirror_epoch)
    last_epoch = sorted_rows[-1]["epoch_utc"]
    start_of_nasa_decay_day = datetime(1963, 11, 8, tzinfo=timezone.utc)
    day_after = start_of_nasa_decay_day + timedelta(days=1)
    if last_epoch >= start_of_nasa_decay_day:
        # Fail closed: this report is explicitly about the coverage gap.
        raise ValueError("last source epoch is not before NASA date-only record")
    return {
        "status": "SECONDARY_RAAN_CHRONOLOGY_ONLY",
        "provenance": {
            "source_url": SOURCE_URL,
            "source_parquet_sha256": PARQUET_SHA256,
            "source_csv_528_sha256": source_sha,
            "secondary_literal_pair_sha256": MIRROR_PAIR_SHA256,
            "NASA_decay_date_document": NASA_SOURCE,
            "instrumental_independence": "NOT_ESTABLISHED",
            "original_line1_line2_for_45_epochs": "NOT_RECOVERED",
            "reference_frame_1963": "NOT_VERIFIED",
        },
        "samples": len(sorted_rows),
        "adjacent_intervals": len(intervals),
        "first": {"source_row": sorted_rows[0]["source_row"],
                  "epoch_utc": stamp(sorted_rows[0]["epoch_utc"]),
                  "raan_deg": sorted_rows[0]["fields"]["raan"]},
        "last": {"source_row": sorted_rows[-1]["source_row"],
                 "epoch_utc": stamp(last_epoch),
                 "raan_deg": sorted_rows[-1]["fields"]["raan"]},
        "gaps": {
            "max_gap_days": max(x["gap_days"] for x in intervals),
            "max_gap_interval": max(intervals, key=lambda x: x["gap_microseconds"]),
            "intervals_le_24h": sum(x["gap_microseconds"] <= DAY_US for x in intervals),
            "intervals_gt_72h": sum(x["gap_microseconds"] > 3 * DAY_US for x in intervals),
            "last_to_NASA_08Nov_date_only_gap_days": {
                "at_08Nov_00UTC": delta_us(last_epoch, start_of_nasa_decay_day) / DAY_US,
                "before_09Nov_00UTC": delta_us(last_epoch, day_after) / DAY_US,
            },
        },
        "legacy_conflict": {
            "legacy_constructed_epoch_utc": stamp(legacy_epoch),
            "secondary_literal_epoch_utc": stamp(mirror_epoch),
            "epoch_difference_mirror_minus_legacy_microseconds": mirror_gap,
            "legacy_constructed_raan_deg": legacy_raan,
            "secondary_literal_raan_deg": mirror_raan,
            "angular_discrepancy_deg": angular_distance_deg(legacy_raan, mirror_raan),
            "within_same_432us_epoch": abs(mirror_gap) <= 432,
            "nearest_secondary_RAAN_value_regardless_of_epoch": {
                "source_row": nearest_raan["source_row"],
                "epoch_utc": stamp(nearest_raan["epoch_utc"]),
                "raan_deg": nearest_raan["fields"]["raan"],
                "angular_distance_deg": angular_distance_deg(
                    nearest_raan["fields"]["raan"], legacy_raan),
            },
            "secondary_samples_at_literal_mirror_epoch": [
                {"source_row": x["source_row"], "raan_deg": x["fields"]["raan"]}
                for x in same_mirror_epoch
            ],
            "resolution": "UNRESOLVED_PRIMARY_ORIGIN",
        },
        "per_adjacent_epoch_interval": intervals,
        "scope": (
            "Signed short arcs and their secant rates are arithmetic on catalog "
            "numbers at unequal epochs, NOT physical RAAN precession estimates; "
            "gaps are unobserved by this mirror. Historical frame, force model, "
            "identity, terminal UTC/position and Conde impact remain unknown."
        ),
        "lean_4_35_physical_premise": "NOT_PROMOTED_NO_PRIMARY_FRAME_OR_ERROR",
        "simulation_and_holdout": "NOT_RUN_NO_CALIBRATED_TRACK",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--pair", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, sha = read_528_csv(args.csv)  # pin sha256 and validate each row
    mirror_epoch, mirror_raan = literal_mirror(args.pair)
    report = audit_raan_timeline(
        rows, sha, mirror_epoch, mirror_raan, required_count=45)
    if sha != EXPECTED_528_CSV_SHA256:
        raise ValueError("secondary 528 CSV SHA256 changed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "samples": report["samples"],
        "intervals": report["adjacent_intervals"],
        "gap": report["gaps"],
        "legacy_conflict": report["legacy_conflict"],
        "physical_fit": report["simulation_and_holdout"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
