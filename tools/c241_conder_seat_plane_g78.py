#!/usr/bin/env python3
"""G78: two distinct MODERN Conde location proxies vs NORAD 528 orbital-plane roots.

Conditional geometry only, no historical geocode, phase, event time, or impact.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

import c241_modern_boundary_plane_g77 as g77
import c241_plane_proxy_clock_g76 as g76
import c241_conditional_plane_windows as plane
import cgeo61_conder_sede_point as cgeo61

ROOT = Path(__file__).resolve().parents[1]
CONDER = "research/geo/cgeo61_conder_sede_point.json"
BRANCHES = g77.BRANCHES


def generate(repo: Path) -> dict:
    baseline, nodes, clock, _stamps = g76.validate_inputs(repo)
    official = g76.load(repo, CONDER)
    osm = g76.load(repo, g76.OSM)
    spatial = cgeo61.validate(official, osm)
    if (spatial["active_constraint"] or spatial["historical_center"] is not None
            or official["dependence"]["independent_measurements_established"]):
        raise ValueError("modern CONDER views promoted to independent historical evidence")
    point = official["point"]
    lat, lon = point["latitude"], point["longitude"]
    if point["role"] != "CONDER_PRESENT_DAY_SEAT_PROXY_ONLY":
        raise ValueError("historical center incorrectly promoted")
    osm_node = nodes[0]
    results = []
    for branch in BRANCHES:
        record = g76.load(repo, g77.REPORT_PATH.format(branch))
        if (record["norad"] != 528 or record["branch"].lower() != branch
                or record["origin_utc"] >= "1963-11-06"):
            raise ValueError("unapproved orbit branch/epoch")
        reference = g77.evening_root(record, baseline)
        origin = g76.report_origin(record)
        model = lambda t, a, b: plane.cross_km(
            t, origin, record["da_dt_km_day"], a, b)
        osm_root = g77.nearest_root(
            lambda t: model(t, osm_node["latitude"], osm_node["longitude"]), reference)
        official_root = g77.nearest_root(lambda t: model(t, lat, lon), reference)
        offset = (official_root-osm_root).total_seconds()
        if not math.isfinite(offset) or abs(offset) >= 180:
            raise ValueError("modern proxies paired with different plane crossings")
        results.append({
            "norad": 528, "branch": branch,
            "reference_modern_camera_root_utc": reference.isoformat(),
            "osm_conde_root_utc": osm_root.isoformat(),
            "conder_sede_root_utc": official_root.isoformat(),
            "official_minus_osm_seconds": round(offset, 3),
            "official_minus_camera_seconds": round((official_root-reference).total_seconds(), 3),
            "osm_minus_camera_seconds": round((osm_root-reference).total_seconds(), 3),
            "conder_cross_track_km_at_osm_root": round(abs(model(osm_root, lat, lon)), 6),
        })
    inputs = (CONDER, g76.OSM, g76.INDEX, g76.CLOCK)
    inputs += tuple(g77.REPORT_PATH.format(b) for b in BRANCHES)
    return {
        "schema": "conde.c241-modern-conder-seat-plane-sensitivity/v1",
        "source_sha256": {p: hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in inputs},
        "distance_between_modern_proxies_m": spatial["distance_m"],
        "official_source_role": point["role"],
        "osm_source_role": osm_node["role"],
        "independent_instrumental_measurements": False,
        "source_observation_epoch": None,
        "historical_1963_site": None,
        "coordinate_approximation": "EPSG:4326 and EPSG:4674 used as WGS84 proxies; no certified datum transform",
        "point_position_accuracy_m": None,
        "orbital_phase": "NOT_EVALUATED",
        "clock_branch": clock["verification_status"],
        "broadcast_is_observed_event_time": False,
        "active_constraint": False,
        "posterior": False,
        "impact_probability": None,
        "results": results,
    }


def payload(repo: Path) -> bytes:
    data = (json.dumps(generate(repo), sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")
    if len(data) > 20000:
        raise ValueError("G78 report exceeds 20 KB")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = payload(args.repo)
    if args.check:
        if args.output.read_bytes() != data:
            raise SystemExit("G78 replay/source mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
    print("G78: two modern Conde proxies; historical site and orbital phase unresolved")


if __name__ == "__main__":
    main()
