#!/usr/bin/env python3
"""Independent check of C241-T2 using pinned SECONDARY bytes, not radar evidence.

No fitted orbit, atmospheric entry, posterior, or geographical inference.
The test controls below use SYNTHETIC rows; the CI audit reopens actual Parquet.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen

SOURCE = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet"
SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
# Compare against verbatim Git blob 0284f1217557b0ea891b5e51b6ac56bd13529d3f.
L1 = "1 00528U 63003B   63300.61111111  .00000000  00000-0  00000-0 0  9992"
L2 = "2 00528  81.8615 284.1520 0084200 142.3150 218.4210 15.74900000 45124"
FIELDS = ("inclination", "raan", "eccentricity", "arg_perigee", "mean_anomaly", "mean_motion")
ANGULAR = {"raan", "arg_perigee", "mean_anomaly"}
# Serialization limits copied as declared TEST CONDITIONS, not orbital uncertainties.
TOLERANCE = {
    "inclination": 0.00008, "raan": 0.00008,
    "eccentricity": 0.00000006, "arg_perigee": 0.00008,
    "mean_anomaly": 0.00008, "mean_motion": 0.000000006,
}

def checksum(line):
    if len(line) != 69 or line[0] not in "12":
        raise ValueError("invalid TLE line shape")
    return sum(int(c) if c.isdigit() else int(c == "-") for c in line[:68]) % 10

def legacy_elements():
    assert checksum(L1) == int(L1[-1]) and checksum(L2) == int(L2[-1])
    return {
        "inclination": float(L2[8:16]),
        "raan": float(L2[17:25]),
        "eccentricity": float("0." + L2[26:33]),
        "arg_perigee": float(L2[34:42]),
        "mean_anomaly": float(L2[43:51]),
        "mean_motion": float(L2[52:63]),
    }

def legacy_epoch():
    day = Decimal(L1[20:32])
    ordinal = int(day)
    return datetime(1963, 1, 1, tzinfo=timezone.utc) + timedelta(
        days=ordinal - 1,
        microseconds=int(((day - ordinal) * Decimal(86400000000)).to_integral_value()),
    )

def delta(name, a, b):
    d = abs(a - b)
    return min(d % 360, 360 - (d % 360)) if name in ANGULAR else d

def inspect_rows(rows):
    """Never join six fields from different rows/epochs."""
    expected = legacy_elements()
    timestamp = legacy_epoch()
    observations = []
    for index, row in rows:
        if row["norad_id"] != 528:
            continue
        stamp = row["epoch"]
        if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
            raise ValueError("epoch must explicitly use UTC")
        differences = {}
        for key in FIELDS:
            value = float(row[key])
            if not math.isfinite(value):
                raise ValueError("nonfinite field")
            differences[key] = delta(key, value, expected[key])
        observations.append({
            "source_row": index, "epoch": stamp.isoformat(),
            "delta": differences,
            "all_six": all(differences[k] <= TOLERANCE[k] for k in FIELDS),
            "same_epoch": abs(stamp - timestamp) <= timedelta(microseconds=432),
        })
    if not observations:
        raise ValueError("missing satellite 528")
    nearest = min(observations, key=lambda o: (o["delta"]["raan"], o["epoch"], o["source_row"]))
    return {
        "record_count": len(observations),
        "unique_epoch_count": len({v["epoch"] for v in observations}),
        "complete_six_field_matches": sum(v["all_six"] for v in observations),
        "same_epoch_records": sum(v["same_epoch"] for v in observations),
        "nearest_raan_source_row": nearest["source_row"],
        "nearest_raan_epoch": nearest["epoch"],
        "nearest_raan_delta_degrees": nearest["delta"]["raan"],
        "nearest_other_deltas": nearest["delta"],
        "oct27_records": [
            {"source_row": v["source_row"], "raan_delta": v["delta"]["raan"]}
            for v in observations if v["epoch"].startswith("1963-10-27T")
        ],
        "scope": "DIGITAL_SECONDARY_MIRROR_ONLY",
        "primary_1963_tracking": "NOT_VERIFIED",
        "physical_parameter_domain": "NOT_EVALUATED",
        "lean_proof": "NOT_RUN",
        "reentry_or_impact": "NOT_ESTABLISHED",
    }

def read_verified_parquet(path):
    blob = Path(path).read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != SHA256 or blob[:4] != b"PAR1" or blob[-4:] != b"PAR1":
        raise ValueError("source bytes/hash not verified")
    import pyarrow.parquet as pq  # only required for real-data CI
    table = pq.read_table(path, columns=["norad_id", "epoch", *FIELDS])
    return list(enumerate(table.to_pylist()))

def assert_report(r):
    # A separate executable reproduction of the numerical story, pinned to bytes.
    assert (r["record_count"], r["unique_epoch_count"]) == (45, 45), r
    assert (r["complete_six_field_matches"], r["same_epoch_records"]) == (0, 0), r
    assert r["nearest_raan_source_row"] == 2998, r
    assert r["nearest_raan_epoch"] == "1963-08-12T13:35:30.863616+00:00", r
    assert abs(r["nearest_raan_delta_degrees"] - 0.1790852050781) < 1e-8, r
    assert any(q["source_row"] == 3017 and abs(q["raan_delta"] - 85.6259) < 0.0001
               for q in r["oct27_records"]), r

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", required=True)
    p.add_argument("--download", action="store_true")
    p.add_argument("--assert-story", action="store_true")
    args = p.parse_args()
    if args.download:
        with urlopen(SOURCE, timeout=60) as r:
            data = r.read()
        if hashlib.sha256(data).hexdigest() != SHA256:
            raise ValueError("pinned source SHA mismatch")
        Path(args.parquet).write_bytes(data)
    report = inspect_rows(read_verified_parquet(args.parquet))
    if args.assert_story:
        assert_report(report)
    print("GAVIAO_CH05_SECONDARY_RECHECK", json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
