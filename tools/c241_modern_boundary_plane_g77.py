#!/usr/bin/env python3
"""G77: conditional orbital-plane crossing sensitivity at MODERN IBGE boundary vertices.

This computes an exact local plane root for each catalogued vertex, not an
impact corridor, certified 1963 boundary, satellite phase, or historical event.
Only the two pinned modern editions and the two G76 NORAD 528 models are used.
A vertex extremum is NOT a mathematically exhaustive polygon-area bound.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path

import c241_conditional_plane_windows as plane
import c241_plane_proxy_clock_g76 as g76
import conde_gis as gis

ROOT = Path(__file__).resolve().parents[1]
EDITION_PATH = "research/geo/conde_ibge_{}_sirgas2000.json"
REPORT_PATH = "research/statistics/c241_plane_528_{}.json"
BRANCHES = ("constant_a", "decaying_a_last_secant")
UTC = timezone.utc


def nearest_root(fn, reference: datetime) -> datetime:
    """Locate a nearby transverse zero with Newton steps and a residual check.

    At the geometries used here, the crossing slope is nonzero. Refuse a
    singular or far-away solution instead of silently pairing a different root.
    """
    result = reference
    for _ in range(4):
        value = fn(result)
        slope = (fn(result + timedelta(seconds=2))
                 - fn(result - timedelta(seconds=2))) / 4
        if not (math.isfinite(value) and math.isfinite(slope)) or abs(slope) < 1e-8:
            raise ValueError("nonfinite or tangent plane crossing")
        step = -value / slope
        if not math.isfinite(step) or abs(step) > 180:
            raise ValueError("crossing root outside local window")
        result = result + timedelta(seconds=step)
        if abs((result - reference).total_seconds()) > 180:
            raise ValueError("root matches a different plane crossing")
    # The upstream G76 GMST uses a single Julian-day float; its ~40 us
    # time quantization at 1963 implies centimeter-scale crossing residuals.
    # A 5 cm numerical-only tolerance avoids fictitious sub-ULP precision.
    if not math.isfinite(fn(result)) or abs(fn(result)) > 5e-5:
        raise ValueError("plane root failed independent residual check")
    return result


def evening_root(report: dict, baseline: dict) -> datetime:
    camera_lat, camera_lon = baseline["source"]["coordinate_lat_lon_deg"]
    origin = g76.report_origin(report)
    model = lambda t: plane.cross_km(t, origin, report["da_dt_km_day"],
                                    camera_lat, camera_lon)
    day = datetime(1963, 11, 8, tzinfo=UTC)
    candidates = [t for t in plane.roots_for_day(model, day) if t.hour >= 20]
    archived = [g76.parse_utc(x["crossing_utc"]) for x in report["crossings"]
                if x["crossing_utc"].startswith("1963-11-08T2")]
    if (len(candidates) != 1 or len(archived) != 1
            or abs((candidates[0] - archived[0]).total_seconds()) > 1):
        raise ValueError("Nov 8 camera root cannot be independently reproduced")
    return candidates[0]


def generate(repo: Path) -> dict:
    baseline, _nodes, _clock, _stamps = g76.validate_inputs(repo)
    snapshots = {}
    for year in (2022, 2025):
        snapshot = gis.read_snapshot(repo / EDITION_PATH.format(year))
        coords = snapshot["coordinates"]
        metadata = snapshot["metadata"]
        if (snapshot["source"]["edition"] != year or coords["epsg"] != 4674
                or coords["axis_order"] != ["longitude", "latitude"]
                or coords["transform_to_wgs84_performed"] is not False
                or metadata["valid_in_november_1963"] != "NOT_ESTABLISHED"
                or metadata["boundary_positional_accuracy_m"] is not None):
            raise ValueError("modern IBGE boundary promoted to historical geometry")
        snapshots[year] = snapshot

    results = []
    for branch in BRANCHES:
        report = g76.load(repo, REPORT_PATH.format(branch))
        if (report["norad"] != 528 or report["branch"].lower() != branch
                or report["origin_utc"] >= "1963-11-06"):
            raise ValueError("unexpected secondary orbit source")
        center = evening_root(report, baseline)
        origin = g76.report_origin(report)
        model = lambda t, lat, lon: plane.cross_km(
            t, origin, report["da_dt_km_day"], lat, lon)
        editions = []
        for year, snapshot in snapshots.items():
            vertices = snapshot["geometry"]["coordinates"][0][:-1]
            if not vertices:
                raise ValueError("empty modern boundary")
            samples = []
            for lon, lat in vertices:
                root = nearest_root(lambda t: model(t, lat, lon), center)
                samples.append(((root - center).total_seconds(), lat, lon))
            low, high = min(samples), max(samples)
            editions.append({
                "edition": year,
                "vertices_sampled_excluding_closure": len(samples),
                "boundary_vertex_shift_seconds": {
                    "minimum": round(low[0], 3),
                    "maximum": round(high[0], 3),
                },
                "extremum_vertices_lat_lon_deg": {
                    "minimum": [low[1], low[2]],
                    "maximum": [high[1], high[2]],
                },
            })
        results.append({
            "norad": 528, "branch": branch,
            "reference_modern_camera_crossing_utc": plane.iso(center),
            "editions": editions,
        })

    inputs = (g76.INDEX, g76.OSM, g76.CLOCK)
    inputs += tuple(EDITION_PATH.format(y) for y in (2022, 2025))
    inputs += tuple(REPORT_PATH.format(b) for b in BRANCHES)
    return {
        "schema": "conde.c241-modern-boundary-vertex-plane-sensitivity/v1",
        "source_sha256": {p: hashlib.sha256((repo / p).read_bytes()).hexdigest()
                          for p in inputs},
        "source_parquet_sha256": baseline["source"]["secondary_parquet_sha256"],
        "coordinate_source_crs": "EPSG:4674",
        "geodesy_conversion_applied": False,
        "modern_boundary_editions_only": [2022, 2025],
        "historic_1963_boundary_status": "NOT_ESTABLISHED",
        "surface_sampling": "BOUNDARY_VERTICES_ONLY_NOT_AREA_ENVELOPE",
        "orbit_lineage": "SECONDARY_TLE_SHARED",
        "phase_constraint": "NOT_EVALUATED",
        "active_constraint": False,
        "posterior": False,
        "impact_probability": None,
        "observed_event_utc": None,
        "clock_branch_resolved": False,
        "reports": results,
    }


def payload(repo: Path) -> bytes:
    data = (json.dumps(generate(repo), ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")
    if len(data) > 20000:
        raise ValueError("G77 report exceeds 20 KB")
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
            raise SystemExit("G77 source or calculation drift")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
    print("G77: two modern boundaries, two NORAD 528 scenarios; historical event NOT_INFERRED")


if __name__ == "__main__":
    main()
