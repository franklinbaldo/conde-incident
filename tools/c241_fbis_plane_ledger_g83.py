#!/usr/bin/env python3
"""G83: project already-versioned plane crossing times onto conditional FBIS clocks.

Pure join over files on disk. Does not propagate or fit an orbit or estimate
time of the event. Ordering of geometric roots never licenses an exclusion.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLOCK = "research/constraints/fbis_1963_clock_branches.json"
REPORTS = tuple(
    f"research/statistics/c241_plane_{norad}_{model}.json"
    for norad in (528, 637)
    for model in ("constant_a", "decaying_a_last_secant")
)
OUTPUT = "research/statistics/c241_fbis_plane_ledger_g83.json"
UTC = timezone.utc
BAHIA = timezone(timedelta(hours=-3))


def read(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def utc(stamp: str) -> datetime:
    if not isinstance(stamp, str) or not stamp.endswith("Z"):
        raise ValueError("timestamp must be explicitly UTC")
    value = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if value.utcoffset() != timedelta(0):
        raise ValueError("timestamp must be UTC")
    return value


def generate(root: Path) -> dict:
    clock = read(root, CLOCK)
    if (
        clock["schema"] != "conde.fbis-clock-branches/v1"
        or clock["verification_status"] != "UNRESOLVED"
        or clock["source"]["header_timezone_verified"] is not False
        or clock["source"]["reported_phenomenon_time"] is not None
        or clock["anchor_rule"]["decision"]["qualifying_anchors"] != 0
        or clock["civil_time_basis"]["bahia_utc_offset_on_1963_11_08_minutes"] != -180
        or clock["civil_time_basis"]["guanabara_utc_offset_on_1963_11_08_minutes"] != -120
    ):
        raise ValueError("unresolved clock guard changed: review evidence before replay")
    conditional = clock["conditional_branches"]
    stamps = {}
    for branch, expected in (
        ("GMT", "1963-11-08T23:30Z"),
        ("RIO_LOCAL", "1963-11-09T01:30Z"),
    ):
        record = conditional[branch]
        if record["orbit_exclusion_licensed"] is not False:
            raise ValueError("clock cannot license orbital exclusion")
        stamp = utc(record["broadcast_utc_if_assumption_holds"])
        if stamp != utc(expected):
            raise ValueError("conditional FBIS clock changed; review sources")
        stamps[branch] = stamp
    if (
        conditional["OTHER_UNVERIFIED"]["broadcast_utc_if_assumption_holds"] is not None
        or conditional["OTHER_UNVERIFIED"]["orbit_exclusion_licensed"] is not False
    ):
        raise ValueError("unknown clock promoted to a timestamp")

    source_sha = {}
    rows = []
    source_sha[CLOCK] = hashlib.sha256((root / CLOCK).read_bytes()).hexdigest()
    for path in REPORTS:
        original = read(root, path)
        source_sha[path] = hashlib.sha256((root / path).read_bytes()).hexdigest()
        stem = Path(path).stem
        if (
            original["norad"] != int(stem.split("_")[2])
            or original["branch"] != ("CONSTANT_A" if stem.endswith("constant_a") else "DECAYING_A_LAST_SECANT")
            or len(original["crossings"]) not in (8, 9)
        ):
            raise ValueError("unexpected orbital source identity or count")
        cutoffs = {name: utc(val) for name, val in original["cutoffs_utc"].items()}
        if set(cutoffs) != {"UTC_CIVIL_DAY", "BAHIA_CIVIL_DAY"}:
            raise ValueError("NASA day interpretations missing")
        previous = None
        for c in original["crossings"]:
            t = utc(c["crossing_utc"])
            if previous is not None and t <= previous:
                raise ValueError("crossings must be unique and increasing")
            previous = t
            local = t.astimezone(BAHIA).strftime("%Y-%m-%dT%H:%M:%S")
            if local.replace("T", " ") != c["crossing_bahia_utc_minus_3"]:
                raise ValueError("archived Bahia local time mismatch")
            rows.append({
                "norad": original["norad"],
                "orbital_model": original["branch"],
                "crossing_utc": c["crossing_utc"],
                "bahia_utc_minus_3": local,
                "gmt_conditional_order": "BEFORE" if t <= stamps["GMT"] else "AFTER",
                "rio_local_conditional_order": "BEFORE" if t <= stamps["RIO_LOCAL"] else "AFTER",
                "other_unverified_conditional_order": None,
                "independent_event_time_871": None,
                "within_nasa_utc_day_scenario": t < cutoffs["UTC_CIVIL_DAY"],
                "within_nasa_bahia_day_scenario": t < cutoffs["BAHIA_CIVIL_DAY"],
            })
    counts = {}
    for norad in (528, 637):
        for model in ("CONSTANT_A", "DECAYING_A_LAST_SECANT"):
            subset = [r for r in rows if r["norad"] == norad and r["orbital_model"] == model]
            counts[f"{norad}_{model}"] = {
                "rows": len(subset),
                "gmt_before": sum(r["gmt_conditional_order"] == "BEFORE" for r in subset),
                "gmt_after": sum(r["gmt_conditional_order"] == "AFTER" for r in subset),
                "rio_before": sum(r["rio_local_conditional_order"] == "BEFORE" for r in subset),
                "rio_after": sum(r["rio_local_conditional_order"] == "AFTER" for r in subset),
            }
    return {
        "schema": "conde.c241-fbis-plane-ledger/g83",
        "issues": [870, 886, 871],
        "clock_decision": "UNRESOLVED",
        "conditional_broadcast_utc": {k: v.strftime("%Y-%m-%dT%H:%M:%SZ") for k, v in stamps.items()},
        "conditional_broadcast_other": None,
        "historical_event_time_utc": None,
        "modern_camera_proxy_only": True,
        "plane_not_orbital_phase": True,
        "nasa_day_cutoff_not_observed_reentry_instant": True,
        "orbit_exclusion_licensed": False,
        "active_constraint": False,
        "posterior": False,
        "impact_probability": None,
        "source_sha256": source_sha,
        "counts": counts,
        "rows": rows,
    }


def payload(root: Path) -> bytes:
    return (json.dumps(generate(root), indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=Path(OUTPUT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else args.repo / args.output
    expected = payload(args.repo)
    if args.check:
        if output.read_bytes() != expected:
            raise SystemExit("G83 replay mismatch")
        print("G83 byte-exact replay PASS")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(expected)


if __name__ == "__main__":
    main()
