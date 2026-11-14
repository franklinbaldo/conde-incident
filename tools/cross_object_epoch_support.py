#!/usr/bin/env python3
"""NORAD 527/528/529 temporal overlap in SECONDARY records only.

No interpolation, physical propagation, joint orbital fit or reentry claim.
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCE_URL = ("https://huggingface.co/datasets/oxzoid/"
              "space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet")
SOURCE_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
EXPECTED_CSV_SHA256 = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
IDS = (527, 528, 529)
WINDOW_HOURS = (6, 24, 72)  # query windows, NOT observed measurement errors
FIELDS = ("inclination", "raan", "eccentricity", "arg_perigee",
          "mean_anomaly", "mean_motion", "mean_motion_dot", "bstar",
          "intl_designator", "altitude_km")


def micros(td):
    return td // timedelta(microseconds=1)


def parse_utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must end in Z (UTC)")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    if dt.tzinfo != timezone.utc or dt.year != 1963:
        raise ValueError("not UTC in 1963")
    return dt


def read_pinned_csv(path):
    payload = path.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if sha != EXPECTED_CSV_SHA256:
        raise ValueError("CSV SHA256 mismatch: " + sha)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not ({"norad_id", "source_row", "epoch"} | set(FIELDS)).issubset(reader.fieldnames or []):
            raise ValueError("missing columns in pinned CSV")
        return list(reader)


def normalize(raw_rows):
    groups = {sid: {} for sid in IDS}
    counts = {sid: 0 for sid in IDS}
    physical_indices = set()
    for raw in raw_rows:
        try:
            sid, index = int(raw["norad_id"]), int(raw["source_row"])
            if sid not in IDS or str(sid) != str(raw["norad_id"]):
                raise ValueError("unknown satellite")
            if index < 0 or index in physical_indices:
                raise ValueError("duplicate or invalid source_row")
            physical_indices.add(index)
            stamp = parse_utc(raw["epoch"])
            state = tuple(str(raw[k]) for k in FIELDS)
            for k in FIELDS:
                if k != "intl_designator" and not math.isfinite(float(raw[k])):
                    raise ValueError("non-finite orbital numeric: " + k)
        except (KeyError, OverflowError, TypeError) as exc:
            raise ValueError("invalid CSV row") from exc
        counts[sid] += 1
        entry = groups[sid].get(stamp)
        if entry is None:
            groups[sid][stamp] = {"epoch": stamp, "source_rows": [index], "state": state}
        elif entry["state"] != state:
            raise ValueError("conflicting states at one epoch for " + str(sid))
        else:
            entry["source_rows"].append(index)
    out = {}
    for sid in IDS:
        out[sid] = sorted(groups[sid].values(), key=lambda a: a["epoch"])
        if not out[sid]:
            raise ValueError("missing NORAD " + str(sid))
        for entry in out[sid]:
            entry["source_rows"].sort()
    return out, counts


def nearest(epoch, rows):
    stamps = [r["epoch"] for r in rows]
    idx = bisect.bisect_left(stamps, epoch)
    candidates = [rows[i] for i in (idx - 1, idx) if 0 <= i < len(rows)]
    if not candidates:
        return None
    chosen = min(candidates, key=lambda r: (abs(micros(r["epoch"] - epoch)),
                                            r["epoch"], r["source_rows"][0]))
    delta = micros(chosen["epoch"] - epoch)
    return {"epoch_utc": chosen["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "source_rows": chosen["source_rows"], "signed_delta_us": delta,
            "absolute_delta_us": abs(delta), "exact_utc_epoch": delta == 0,
            "half_tle_quantum_or_less": abs(delta) <= 432}


def post_decay_day_controls(by_sat):
    """Return source catalog coverage, not physical before/after decay observations.

    NASA C197 dates the 528 decay to the *day* 1963-11-08. Only epochs
    >= 1963-11-09T00Z are strictly later than the reported calendar day;
    1963-11-08 epochs are temporally ambiguous with respect to decay.
    """
    start = datetime(1963, 11, 8, tzinfo=timezone.utc)
    end = datetime(1963, 11, 9, tzinfo=timezone.utc)

    def as_record(entry):
        if entry is None:
            return None
        return {"epoch_utc": entry["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
                "source_rows": entry["source_rows"]}

    chronology = {}
    for sid in IDS:
        seq = by_sat[sid]
        before = [e for e in seq if e["epoch"] < start]
        during = [e for e in seq if start <= e["epoch"] < end]
        after = [e for e in seq if e["epoch"] >= end]
        chronology[str(sid)] = {
            "distinct_epochs_before_day": len(before),
            "distinct_epochs_on_ambiguous_day": len(during),
            "distinct_epochs_after_day": len(after),
            "last_before_day": as_record(before[-1] if before else None),
            "on_ambiguous_day": [as_record(e) for e in during],
            "first_after_day": as_record(after[0] if after else None),
            "last_after_day": as_record(after[-1] if after else None),
            "post_day_source_rows": [e["source_rows"] for e in after],
            "catalog_gap_last_pre_first_post_seconds":
                micros(after[0]["epoch"] - before[-1]["epoch"]) / 1_000_000
                if after and before else None,
        }
    return {
        "source": "NASA SSR 1963-11-15 C197 day-only decay + SHA-pinned secondary TLE catalog",
        "decay_day_utc": "1963-11-08",
        "guaranteed_after_reported_day_from_utc": "1963-11-09T00:00:00Z",
        "by_norad": chronology,
        "both_controls_have_later_catalog_epochs": all(
            chronology[str(sid)]["distinct_epochs_after_day"] > 0
            for sid in (527, 529)),
        "independent_instrumental_tracking": "NOT_ESTABLISHED",
        "physical_joint_fit": "NOT_RUN",
        "historical_holdout": "NOT_RUN",
        "528_trajectory_restriction": "NONE",
        "impact_time_or_location": "NOT_INFERRED",
    }


def summarize(raw_rows):
    by_sat, counts = normalize(raw_rows)
    coverage = {str(h) + "h": {"527": 0, "529": 0, "both": 0} for h in WINDOW_HOURS}
    exact = {"527": 0, "529": 0, "both": 0}
    near_quantum = {"527": 0, "529": 0, "both": 0}
    used = {527: set(), 529: set()}
    entries = []
    for target in by_sat[528]:
        support = {sid: nearest(target["epoch"], by_sat[sid]) for sid in (527, 529)}
        for sid in (527, 529):
            item = support[sid]
            exact[str(sid)] += int(item["exact_utc_epoch"])
            near_quantum[str(sid)] += int(item["half_tle_quantum_or_less"])
            if item["absolute_delta_us"] <= 72 * 3600 * 1_000_000:
                used[sid].add(tuple(item["source_rows"]))
        exact["both"] += int(all(item["exact_utc_epoch"] for item in support.values()))
        near_quantum["both"] += int(all(item["half_tle_quantum_or_less"] for item in support.values()))
        for hours in WINDOW_HOURS:
            eligible = {sid: support[sid]["absolute_delta_us"] <= hours * 3600 * 1_000_000
                        for sid in (527, 529)}
            for sid in (527, 529):
                coverage[str(hours) + "h"][str(sid)] += int(eligible[sid])
            coverage[str(hours) + "h"]["both"] += int(all(eligible.values()))
        entries.append({"epoch_528_utc": target["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
                        "source_rows_528": target["source_rows"],
                        "nearest_527": support[527], "nearest_529": support[529]})
    extents = {}
    for sid in IDS:
        seq = by_sat[sid]
        gaps = [micros(seq[i]["epoch"] - seq[i-1]["epoch"]) for i in range(1, len(seq))]
        extents[str(sid)] = {
            "rows": counts[sid], "unique_epochs": len(seq),
            "first_utc": seq[0]["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "last_utc": seq[-1]["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "minimum_gap_us": min(gaps) if gaps else None,
            "maximum_gap_us": max(gaps) if gaps else None}
    return {
        "classification": "SECONDARY_EPOCH_AVAILABILITY_ONLY",
        "source": {"parquet_url": SOURCE_URL, "parquet_sha256": SOURCE_SHA256,
                   "derived_csv_sha256": EXPECTED_CSV_SHA256,
                   "instrumental_independence": "NOT_ESTABLISHED"},
        "windows_hours": list(WINDOW_HOURS),
        "window_meaning": "Predeclared calendar-distance queries; NOT observational uncertainty or orbital synchrony",
        "object_extents": extents,
        "post_decay_day_control_coverage": post_decay_day_controls(by_sat),
        "nearest_by_528_epoch": entries,
        "count_of_528_epochs_with_nearby_527_529": coverage,
        "count_of_exact_shared_epochs": exact,
        "count_within_432us": near_quantum,
        "unique_support_epochs_reused_at_most_72h": {str(sid): len(used[sid]) for sid in (527, 529)},
        "primary_1963_tle_lines_frame_and_errors": "NOT_RECOVERED",
        "physical_joint_fit_and_holdouts": "NOT_RUN",
        "lean_handoff": "Only documentary candidate epochs; no authenticated physical feasible parameter domain.",
        "interpretation": "No interpolated vector, terminal time or position; overlapping catalog epochs do not prove radar independence or impact."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = summarize(read_pinned_csv(args.csv))
    if {k: (report["object_extents"][k]["rows"], report["object_extents"][k]["unique_epochs"])
        for k in ("527", "528", "529")} != {"527": (21, 20), "528": (45, 45), "529": (57, 54)}:
        raise ValueError("Pinned corpus row/epoch counts differ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"counts": report["object_extents"],
                      "coverage": report["count_of_528_epochs_with_nearby_527_529"],
                      "exact": report["count_of_exact_shared_epochs"],
                      "physical_fit": report["physical_joint_fit_and_holdouts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
