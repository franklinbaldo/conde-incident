#!/usr/bin/env python3
"""G76: modern OSM proxy/FBIS branch sensitivity of archived conditional planes.

Read only SHA-pinned derived plane records, named OSM nodes and a conditional
broadcast-clock contract. This NEVER estimates event time, phase or impact.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path

import c241_conditional_plane_windows as plane

ROOT = Path(__file__).resolve().parents[1]
OSM = "research/geo/cgeo60_modern_osm_cut.json"
CLOCK = "research/constraints/fbis_1963_clock_branches.json"
INDEX = "research/statistics/c241_plane_index.json"
REPORTS = ("528_constant_a", "528_decaying_a_last_secant",
           "637_constant_a", "637_decaying_a_last_secant")
UTC = timezone.utc


def load(repo: Path, filename: str) -> dict:
    return json.loads((repo / filename).read_text(encoding="utf-8"))


def digest(repo: Path, filename: str) -> str:
    return hashlib.sha256((repo / filename).read_bytes()).hexdigest()


def parse_utc(text: str) -> datetime:
    result = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if result.utcoffset() != timedelta(0):
        raise ValueError("timestamp not UTC")
    return result


def validate_inputs(repo: Path):
    index = load(repo, INDEX)
    if (index["schema"] != "conde.c241-conditional-plane-windows/v1"
            or index["source"]["secondary_parquet_sha256"] != plane.SOURCE_SHA256
            or index["phase_constraint"] != "NOT_EVALUATED"
            or index["posterior"] is not False
            or index["active_constraint"] is not False):
        raise ValueError("unapproved plane index or activated constraint")
    for path, sha in index["source"]["source_json_sha256"].items():
        if digest(repo, path) != sha:
            raise ValueError("base geographic input SHA mismatch: " + path)
    camera = index["source"]["coordinate_lat_lon_deg"]
    if camera != [-11.7988, -37.621475]:
        raise ValueError("camera coordinates changed; audit prerequisite")
    osm = load(repo, OSM)
    if osm["schema"] != "conde.gis.modern-osm-place-proxies/v1" or osm["id"] != "CGEO-60":
        raise ValueError("unexpected geographic source")
    nodes = osm["nodes"]
    if len(nodes) != 2 or [n["osm_node_id"] for n in nodes] != [415521889, 4697713641]:
        raise ValueError("missing or reordered OSM source nodes")
    for n, role, expected_geo in zip(nodes, ("modern_osm_named_place_node_not_centroid_of_1963_center",
                                             "modern_osm_named_place_node_not_equated_with_vila20"),
                                     ((-11.8129758, -37.6138705), (-11.7968448, -37.6214666))):
        if ((n["latitude"], n["longitude"]) != expected_geo
                or n["role"] != role or n["source_tag_not_a_positional_certification"] is not True
                or not math.isfinite(n["latitude"]) or not math.isfinite(n["longitude"])
                or not -90 <= n["latitude"] <= 90 or not -180 <= n["longitude"] <= 180
                or len(n["raw_xml_sha256"]) != 64):
            raise ValueError("invalid modern-only source provenance")
    if (osm["castor_handoff"]["historical_centro20_status"] != "NOT_EVALUATED_NO_CUSTODIED_POINT"
            or osm["castor_handoff"]["historical_vila20_status"] != "NOT_EVALUATED_NO_CUSTODIED_POINT"
            or osm["historical_context"]["modern_nodes_equate_to_cgeo20_historical_sites"] is not False
            or osm["historical_context"]["time_bridge_to_1963"] is not None):
        raise ValueError("OSM historical identity incorrectly promoted")
    clock = load(repo, CLOCK)
    if (clock["schema"] != "conde.fbis-clock-branches/v1"
            or clock["verification_status"] != "UNRESOLVED"
            or clock["source"]["header_timezone_verified"] is not False
            or clock["source"]["reported_phenomenon_time"] is not None
            or clock["anchor_rule"]["decision"]["qualifying_anchors"] != 0
            or clock["civil_time_basis"]["guanabara_utc_offset_on_1963_11_08_minutes"] != -120
            or clock["civil_time_basis"]["bahia_utc_offset_on_1963_11_08_minutes"] != -180):
        raise ValueError("broadcast-clock contract changed or falsely verified")
    stamps = {"GMT": datetime(1963, 11, 8, 23, 30, tzinfo=UTC),
              "RIO_LOCAL": datetime(1963, 11, 9, 1, 30, tzinfo=UTC)}
    for key, stamp in stamps.items():
        record = clock["conditional_branches"][key]
        if (parse_utc(record["broadcast_utc_if_assumption_holds"]) != stamp
                or record["orbit_exclusion_licensed"] is not False
                or record["plane_crossing_is_measured_event"] is not False):
            raise ValueError("ambiguous broadcast branch promoted or inconsistent")
    if (clock["conditional_branches"]["OTHER_UNVERIFIED"]["broadcast_utc_if_assumption_holds"]
            is not None):
        raise ValueError("unknown clock branch unexpectedly resolved")
    return index, nodes, clock, stamps


def report_origin(report: dict) -> dict:
    return {"epoch": parse_utc(report["origin_utc"]),
            "raan": report["raan_deg"],
            "inclination": report["inclination_deg"],
            "eccentricity": report["e"],
            "mean_motion": report["mean_motion_rev_day"]}


def one_report(report: dict, baseline: dict, nodes: list[dict]):
    origin = report_origin(report)
    drift = report["da_dt_km_day"]
    norad = report["norad"]
    camera_lat, camera_lon = baseline["source"]["coordinate_lat_lon_deg"]
    old = [parse_utc(w["crossing_utc"]) for w in report["crossings"]]
    old_fn = lambda t: plane.cross_km(t, origin, drift, camera_lat, camera_lon)
    # Recompute, rather than trusting time labels transcribed in a table.
    expected = []
    for day in range(6, 10):
        expected.extend(plane.roots_for_day(old_fn, datetime(1963, 11, day, tzinfo=UTC)))
    if len(old) != len(expected) or any(abs((a-b).total_seconds()) > 1 for a, b in zip(old, expected)):
        raise ValueError("archived camera roots disagree with recomputation")
    result = {"norad": norad, "branch": report["branch"],
              "origin_utc": report["origin_utc"], "points": []}
    for node in nodes:
        lat, lon = node["latitude"], node["longitude"]
        fn = lambda t: plane.cross_km(t, origin, drift, lat, lon)
        roots = []
        for day in range(6, 10):
            roots.extend(plane.roots_for_day(fn, datetime(1963, 11, day, tzinfo=UTC)))
        if len(roots) != len(old):
            raise ValueError("crossing count changed between modern nearby points")
        crossings = []
        for instant, camera_t in zip(roots, old):
            shift = (instant-camera_t).total_seconds()
            if abs(shift) > 180:
                raise ValueError("modern nearby point crossed unrelated root")
            crossings.append({
                "utc": plane.iso(instant),
                "bahia_utc_minus_3": plane.local(instant),
                "shift_from_camera_seconds": round(shift, 2),
                "cross_track_km_at_camera_crossing": round(abs(fn(camera_t)), 4),
                "within_UTC_day_scenario": instant < plane.cutoff_for(norad, "UTC_CIVIL_DAY"),
                "within_Bahia_day_scenario": instant < plane.cutoff_for(norad, "BAHIA_CIVIL_DAY"),
            })
        result["points"].append({"modern_osm_node_id": node["osm_node_id"],
                                 "role": "MODERN_OSM_PROXY_ONLY",
                                 "crossings": crossings})
    return result


def generate(repo: Path) -> dict:
    baseline, nodes, clock, stamps = validate_inputs(repo)
    reports = []
    clock_comparison = []
    for key in REPORTS:
        report = load(repo, "research/statistics/c241_plane_" + key + ".json")
        if (report["norad"] != int(key[:3]) or report["branch"].lower() != key[4:]
                or report["origin_utc"] >= "1963-11-06"):
            raise ValueError("report identity or epoch mismatch: " + key)
        result = one_report(report, baseline, nodes)
        reports.append(result)
        if report["norad"] == 528:
            for point in result["points"]:
                # The evening nominal *plane* root, not a sighting or a reentry time.
                matches = [c for c in point["crossings"]
                           if "1963-11-08T20:00:00Z" <= c["utc"] < "1963-11-09T03:00:00Z"]
                if len(matches) != 1:
                    raise ValueError("expected one Nov 8 evening plane root")
                root = parse_utc(matches[0]["utc"])
                for label, stamp in stamps.items():
                    clock_comparison.append({
                        "branch": report["branch"], "modern_osm_node_id": point["modern_osm_node_id"],
                        "broadcast_assumption": label,
                        "nominal_root_utc": plane.iso(root),
                        "hypothetical_broadcast_utc": plane.iso(stamp),
                        "root_minus_broadcast_minutes": round((root-stamp).total_seconds()/60, 3),
                        "ordering_only": "AFTER" if root > stamp else "BEFORE_OR_EQUAL",
                        "orbit_exclusion_licensed": False,
                    })
    return {
        "schema": "conde.c241-modern-proxy-clock-sensitivity/v1",
        "source_sha256": {key: digest(repo, key) for key in (OSM, CLOCK, INDEX)},
        "source_parquet_sha256": baseline["source"]["secondary_parquet_sha256"],
        "reference_camera_modern_2022": baseline["source"]["camera_id"],
        "reported_event_utc": None, "historical_site_1963": None,
        "centro20": "NOT_EVALUATED_NO_CUSTODIED_POINT",
        "vila20": "NOT_EVALUATED_NO_CUSTODIED_POINT",
        "phase_constraint": "NOT_EVALUATED",
        "posterior": False, "active_constraint": False, "impact_probability": None,
        "same_secondary_lineage": True,
        "clock_branch_decision": clock["verification_status"],
        "broadcast_not_event_time": True,
        "day_end_is_scenario_not_decay_instant": True,
        "reports": reports, "clock_ordering_conditional_only": clock_comparison,
    }


def payload(repo: Path) -> bytes:
    data = (json.dumps(generate(repo), sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")
    if len(data) > 20000:
        raise ValueError("result exceeds 20 KB")
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=ROOT)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    data = payload(args.repo)
    if args.check:
        if args.output.read_bytes() != data:
            raise SystemExit("G76 replay drift")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
    print("G76 modern proxies: 2 nodes, 4 reports, 2 unresolved clock branches; no impact claim")


if __name__ == "__main__":
    main()
