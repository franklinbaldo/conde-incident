#!/usr/bin/env python3
"""Predeclared J2-only versus static-RAAN control on real short-gap catalog pairs.

The source is a checksum-pinned SECONDARY mirror, not authenticated 1963
tracking. A dimensional diagnostic never activates a physical constraint.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.cross_object_epoch_support import (  # noqa: E402
    EXPECTED_CSV_SHA256, SOURCE_SHA256, SOURCE_URL, FIELDS,
    normalize, read_pinned_csv,
)
from tools.tle_raan_continuity_1963 import short_arc_deg  # noqa: E402

# Unfitted Kepler/J2 constants used in the existing C179#1 physical bridge.
MU_KM3_S2 = 398600.4418
R_EQUATOR_KM = 6378.137
J2 = 1.08262668e-3
DAY_S = 86400.0
MAX_GAP_S = DAY_S  # fixed selection before residuals; NOT an error bound
IDS = (527, 528, 529)


def j2_nodal_deg_day(state: tuple[str, ...]) -> float:
    """Secular proxy using TLE mean fields (not SGP4 or a verified frame)."""
    i = float(state[FIELDS.index("inclination")])
    e = float(state[FIELDS.index("eccentricity")])
    rev_day = float(state[FIELDS.index("mean_motion")])
    if not (math.isfinite(i) and 0 <= i <= 180 and math.isfinite(e)
            and 0 <= e < 1 and math.isfinite(rev_day) and rev_day > 0):
        raise ValueError("invalid J2 input inclination/eccentricity/mean_motion")
    n = rev_day * 2 * math.pi / DAY_S
    a = (MU_KM3_S2 / n**2)**(1/3)
    rate = -1.5 * J2 * n * (R_EQUATOR_KM / (a * (1 - e**2)))**2 * math.cos(math.radians(i))
    return math.degrees(rate) * DAY_S


def audit(by_sat: dict) -> dict:
    if sorted(by_sat) != list(IDS):
        raise ValueError("missing/extra NORAD objects")
    result = {
        "contract": "conde.secondary-raan-j2-short-gap/v1",
        "source": {"occurrence": "C241-L4", "secondary_parquet": SOURCE_URL,
                   "parquet_sha256": SOURCE_SHA256,
                   "derived_csv_sha256": EXPECTED_CSV_SHA256,
                   "independence": "MODERN_CATALOG_MIRROR_NOT_PRIMARY_TRACKING"},
        "method": {"model": "KEPLER_J2_SECULAR_PROXY_UNCALIBRATED",
                   "baseline": "ZERO_RAAN_DRIFT", "window_hours": 24,
                   "max_gap_is_sensor_sigma": False,
                   "mu_km3_s2": MU_KM3_S2, "r_equator_km": R_EQUATOR_KM, "J2": J2},
        "admissible_domain_change": "NONE_NO_AUTHENTICATED_FRAME_OR_SENSOR_ERRORS",
        "objects": {},
    }
    for sat in IDS:
        for row in by_sat[sat]:
            t = row["epoch"]
            if t.tzinfo is None or t.utcoffset() != timedelta(0):
                raise ValueError("non-UTC epoch")
        seq = sorted(by_sat[sat], key=lambda x: x["epoch"])
        pairs = []
        for a, b in zip(seq, seq[1:]):
            seconds = (b["epoch"] - a["epoch"]).total_seconds()
            if seconds <= 0:
                raise ValueError("duplicate/decreasing epoch")
            if seconds > MAX_GAP_S:
                continue
            old = float(a["state"][FIELDS.index("raan")])
            new = float(b["state"][FIELDS.index("raan")])
            observed = short_arc_deg(old, new)
            rate = j2_nodal_deg_day(a["state"])
            predicted = rate * seconds / DAY_S
            residual = short_arc_deg(predicted % 360, observed % 360)
            pairs.append({
                "source_rows_start": a["source_rows"], "source_rows_end": b["source_rows"],
                "epoch_start_utc": a["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
                "epoch_end_utc": b["epoch"].isoformat(timespec="microseconds").replace("+00:00", "Z"),
                "gap_hours": seconds / 3600,
                "observed_delta_deg": observed,
                "j2_proxy_rate_deg_day": rate,
                "j2_proxy_delta_deg": predicted,
                "j2_signed_residual_deg": residual,
                "static_abs_error_deg": abs(observed),
                "j2_abs_residual_deg": abs(residual),
            })
        summary = {"unique_epochs": len(seq), "adjacent_pairs_at_most_24h": len(pairs),
                   "pairs": pairs}
        if pairs:
            summary["static_mae_deg"] = sum(x["static_abs_error_deg"] for x in pairs) / len(pairs)
            summary["j2_mae_deg"] = sum(x["j2_abs_residual_deg"] for x in pairs) / len(pairs)
            summary["j2_beats_static_on_circular_MAE"] = summary["j2_mae_deg"] < summary["static_mae_deg"]
        else:
            summary["status"] = "NO_SHORT_GAP_PAIRS"
        result["objects"][str(sat)] = summary
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    groups, counts = normalize(read_pinned_csv(args.csv))
    if counts != {527: 21, 528: 45, 529: 57}:
        raise ValueError("C241-L4 source row inventory changed")
    report = audit(groups)
    if {int(k): v["unique_epochs"] for k, v in report["objects"].items()} != {527: 20, 528: 45, 529: 54}:
        raise ValueError("C241-L4 epoch inventory changed")
    if {int(k): v["adjacent_pairs_at_most_24h"] for k, v in report["objects"].items()} != {527: 0, 528: 3, 529: 3}:
        raise ValueError("short-gap eligibility changed; inspect source before interpreting")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: {field: value for field, value in v.items() if field != "pairs"}
                      for k, v in report["objects"].items()}, sort_keys=True))


if __name__ == "__main__":
    main()
