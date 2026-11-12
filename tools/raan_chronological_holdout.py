#!/usr/bin/env python3
"""Cervo: frozen time-disjoint evaluation design for *secondary* 1963 RAAN rows.

No fitting, no predicted orbital state, no likelihood and no posterior.
Time separation does not confer instrumental or documentary independence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from raan_coepoch_audit import parse_records

SCHEMA = "conde.raan-chronological-split/v1"
FIT_END = datetime(1963, 8, 1, tzinfo=timezone.utc)
VALIDATION_END = datetime(1963, 10, 1, tzinfo=timezone.utc)
SPLIT_NAMES = ("fit", "validation", "evaluation")
SOURCE_REL = "research/statistics/raan_527_528_529_1963.json"


def split_label(instant: datetime) -> str:
    """Left-closed UTC blocks, with an exact-date boundary assigned to later set."""
    if instant.tzinfo != timezone.utc:
        raise ValueError("only UTC timestamps supported")
    if not (datetime(1963, 1, 1, tzinfo=timezone.utc) <= instant
            < datetime(1964, 1, 1, tzinfo=timezone.utc)):
        raise ValueError("epoch outside 1963")
    if instant < FIT_END:
        return "fit"
    if instant < VALIDATION_END:
        return "validation"
    return "evaluation"


def build_manifest(source: bytes) -> dict:
    """Return a fully enumerated set assignment, pinned to exact input bytes.

    This audit does not imply that the evaluation block is genuinely blinded:
    historical records and epochs had already been inspected before this split.
    """
    document = json.loads(source)
    grouped, duplicates = parse_records(document)
    memberships: dict[str, dict[str, list[str]]] = {}
    for norad, rows in sorted(grouped.items()):
        by_block: dict[str, list[str]] = {label: [] for label in SPLIT_NAMES}
        for instant, _raan in rows:
            epoch = instant.isoformat(timespec="microseconds").replace("+00:00", "Z")
            by_block[split_label(instant)].append(epoch)
        memberships[str(norad)] = by_block

    totals = {
        block: sum(len(groups[block]) for groups in memberships.values())
        for block in SPLIT_NAMES
    }
    all_keys = [
        (norad, epoch)
        for norad, groups in memberships.items()
        for block in SPLIT_NAMES
        for epoch in groups[block]
    ]
    unique_count = sum(map(len, grouped.values()))
    if len(all_keys) != len(set(all_keys)) or len(all_keys) != unique_count:
        raise ValueError("leakage, duplicate assignment or incomplete membership")
    if set(memberships) != {"527", "528", "529"}:
        raise ValueError("expected the three historical catalog objects")

    return {
        "schema": SCHEMA,
        "source": {
            "path": SOURCE_REL,
            "sha256_of_exact_committed_json_bytes": hashlib.sha256(source).hexdigest(),
            "evidence_ids": document["provenance"]["evidence_ids"] + ["C241-L3"],
            "status": document["provenance"]["status"],
            "lineage": document["provenance"]["lineage"],
        },
        "boundaries": {
            "fit_before_utc": "1963-08-01T00:00:00Z",
            "validation_before_utc": "1963-10-01T00:00:00Z",
            "evaluation_from_utc": "1963-10-01T00:00:00Z",
        },
        "design_status": "RETROSPECTIVE_TIME_SPLIT_NOT_BLINDED",
        "independence_status": "SAME_SECONDARY_DOCUMENTARY_LINEAGE_NOT_INDEPENDENT",
        "statistical_status": "NO_FIT_NO_LIKELIHOOD_NO_POSTERIOR",
        "future_use": (
            "Freeze assignments before future physical calibration; fit parameters only in "
            "fit, use validation for model selection, report evaluation without refitting "
            "or selection. Same-lineage correlation and calendar censoring remain unresolved."
        ),
        "deduplicated_by": ["norad", "epoch_utc"],
        "duplicates_excluded": {str(k): duplicates[k] for k in sorted(duplicates)},
        "memberships": memberships,
        "totals": totals,
        "unique_total": len(all_keys),
        "no_observation_on_1963_11_08_for_528": not any(
            epoch.startswith("1963-11-08")
            for group in memberships["528"].values() for epoch in group
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    destinations = parser.add_mutually_exclusive_group()
    destinations.add_argument("--check", type=Path)
    destinations.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = build_manifest(args.input.read_bytes())
    payload = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if args.check.read_bytes() != payload.encode():
            raise SystemExit("FAIL: committed holdout manifest does not reproduce")
        print("HOLDOUT_MANIFEST_REPRODUCED", manifest["totals"], manifest["unique_total"])
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
