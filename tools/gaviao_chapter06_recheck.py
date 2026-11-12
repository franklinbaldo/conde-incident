#!/usr/bin/env python3
"""Independent calendar-only audit of C241-T3 over a SHA-pinned secondary Parquet.

Deliberately does NOT import Tartaruga's extractor/nearest-neighbor algorithm,
its derived CSV or its expected report. Cross-product scan, not orbital fitting.
"""
import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

SOURCE = ("https://huggingface.co/datasets/oxzoid/space-track-tle-history/"
          "resolve/4b4fb3a/data/tle_1963.parquet")
SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
SATELLITES = (527, 528, 529)
HOUR_WINDOWS = (6, 24, 72)
TLE_HALF_QUANTUM_US = 432  # a comparison rule, NOT measured timing uncertainty


def delta_microseconds(a, b):
    return (a - b) // timedelta(microseconds=1)


def normalize(rows):
    """Input tuples (NORAD ID, UTC datetime, physical Parquet row index)."""
    grouped = defaultdict(lambda: defaultdict(list))
    seen_indices = set()
    for satellite, epoch, source_row in rows:
        if satellite not in SATELLITES or type(satellite) is not int:
            raise ValueError("unexpected NORAD identifier")
        if (not isinstance(epoch, datetime) or epoch.tzinfo is None
                or epoch.utcoffset() != timedelta(0) or epoch.year != 1963):
            raise ValueError("epoch must be timezone-aware UTC in 1963")
        if type(source_row) is not int or source_row < 0 or source_row in seen_indices:
            raise ValueError("invalid or reused physical Parquet row index")
        seen_indices.add(source_row)
        grouped[satellite][epoch].append(source_row)
    for satellite in SATELLITES:
        if not grouped[satellite]:
            raise ValueError(f"no records for NORAD {satellite}")
    return {satellite: {epoch: sorted(indices) for epoch, indices in grouped[satellite].items()}
            for satellite in SATELLITES}


def nearest_by_exhaustive_scan(target, epoch_indices):
    """Deliberately O(N) oracle with deterministic earlier-time tie-break."""
    return min(epoch_indices, key=lambda epoch:
               (abs(delta_microseconds(epoch, target)), epoch, epoch_indices[epoch][0]))


def summarize(rows):
    by_sat = normalize(rows)
    dates = {s: sorted(by_sat[s]) for s in SATELLITES}
    totals = {str(s): {"rows": sum(len(v) for v in by_sat[s].values()),
                       "unique_epochs": len(dates[s])} for s in SATELLITES}
    coverage = {f"{h}h": {"527": 0, "529": 0, "both": 0} for h in HOUR_WINDOWS}
    exact = {"527": 0, "529": 0, "both": 0}
    half = {"527": 0, "529": 0, "both": 0}
    reused = {527: set(), 529: set()}
    for t in dates[528]:
        chosen = {s: nearest_by_exhaustive_scan(t, by_sat[s]) for s in (527, 529)}
        gaps = {s: abs(delta_microseconds(chosen[s], t)) for s in (527, 529)}
        for s in (527, 529):
            exact[str(s)] += int(gaps[s] == 0)
            half[str(s)] += int(gaps[s] <= TLE_HALF_QUANTUM_US)
            if gaps[s] <= 72 * 3600 * 1_000_000:
                reused[s].add(chosen[s])
        exact["both"] += int(all(gaps[s] == 0 for s in (527, 529)))
        half["both"] += int(all(gaps[s] <= TLE_HALF_QUANTUM_US for s in (527, 529)))
        for hours in HOUR_WINDOWS:
            ok = {s: gaps[s] <= hours * 3600 * 1_000_000 for s in (527, 529)}
            for s in (527, 529):
                coverage[f"{hours}h"][str(s)] += int(ok[s])
            coverage[f"{hours}h"]["both"] += int(all(ok.values()))
    return {
        "status": "SECONDARY_CALENDAR_ONLY",
        "source_sha256": SHA256,
        "custody": "SHA_VERIFIES_MIRROR_BYTES_NOT_1963_INSTRUMENT",
        "objects": totals,
        "zero_delta": exact,
        "within_432us": half,
        "windows": coverage,
        "distinct_nearest_support_epochs_within_72h": {
            str(s): len(reused[s]) for s in (527, 529)},
        "last_528_utc": dates[528][-1].isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "528_epoch_in_november": any(d.month == 11 for d in dates[528]),
        "lean_physical_restriction": "NOT_JUSTIFIED",
        "numerical_joint_fit": "NOT_RUN",
        "impact_or_reentry_location": "UNDETERMINED",
    }


def check_chapter_six(report):
    """Assertions test the chapter's exact numerical statements, not truth of radar."""
    assert report["objects"] == {
        "527": {"rows": 21, "unique_epochs": 20},
        "528": {"rows": 45, "unique_epochs": 45},
        "529": {"rows": 57, "unique_epochs": 54}}, report
    assert report["zero_delta"] == {"527": 0, "529": 0, "both": 0}, report
    assert report["within_432us"] == {"527": 0, "529": 0, "both": 0}, report
    assert report["windows"] == {
        "6h": {"527": 2, "529": 6, "both": 1},
        "24h": {"527": 5, "529": 18, "both": 2},
        "72h": {"527": 16, "529": 35, "both": 15}}, report
    assert report["distinct_nearest_support_epochs_within_72h"] == {"527": 13, "529": 28}, report
    assert report["last_528_utc"] == "1963-10-27T14:40:16.132512Z", report
    assert report["528_epoch_in_november"] is False, report


def load_pinned(path, download=False):
    if download:
        with urlopen(SOURCE, timeout=120) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError("remote secondary archive changed bytes")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != SHA256:
        raise ValueError("pinned Parquet SHA256 mismatch")
    if not payload.startswith(b"PAR1") or not payload.endswith(b"PAR1"):
        raise ValueError("not a Parquet container")
    import pyarrow.parquet as pq
    table = pq.read_table(path, columns=["norad_id", "epoch"])
    records = []
    for source_row, record in enumerate(table.to_pylist()):
        if record["norad_id"] in SATELLITES:
            records.append((record["norad_id"], record["epoch"], source_row))
    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parquet", type=Path, required=True)
    p.add_argument("--download", action="store_true")
    p.add_argument("--assert-story", action="store_true")
    args = p.parse_args()
    report = summarize(load_pinned(args.parquet, download=args.download))
    if args.assert_story:
        check_chapter_six(report)
    print("GAVIAO_CH06_INDEPENDENT " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
