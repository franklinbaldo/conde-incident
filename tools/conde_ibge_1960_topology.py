"""CGEO-12: exact native-XY topology of the IBGE *retrospective* Conde 1960 mesh.

A geometric audit of an archived drawing is not a survey, a 1963 legal boundary
or a location observation. Pure stdlib, no synthetic source geometries.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
import json
from pathlib import Path
from tools.conde_ibge_1960 import load_contract as load_source

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "research/geo/conde_ibge_1960_topology_audit.json"

def point(xy):
    if len(xy) != 2:
        raise ValueError("each point must have two projected coordinates")
    try:
        pair = tuple(Decimal(str(v)) for v in xy)
    except (ValueError, TypeError) as exc:
        raise ValueError("non-numeric point") from exc
    if not all(v.is_finite() for v in pair):
        raise ValueError("non-finite point")
    return pair

def orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

def between(a, b, c):
    return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))

def intersects(a, b, c, d):
    """Any segment intersection, including touches and collinear overlaps."""
    o1, o2, o3, o4 = (orientation(a, b, c), orientation(a, b, d),
                       orientation(c, d, a), orientation(c, d, b))
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return any(o == 0 and between(u, v, p) for o, u, v, p in (
        (o1, a, b, c), (o2, a, b, d), (o3, c, d, a), (o4, c, d, b)))

def native_topology(ring):
    pts = [point(xy) for xy in ring]
    if len(pts) < 4 or pts[0] != pts[-1]:
        raise ValueError("ring must contain >=3 edges and close")
    n = len(pts) - 1
    if len(set(pts[:-1])) != n:
        raise ValueError("duplicate vertex")
    if any(pts[i] == pts[i + 1] for i in range(n)):
        raise ValueError("zero-length edge")
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if intersects(pts[i], pts[i + 1], pts[j], pts[j + 1]):
                raise ValueError(f"nonadjacent edges intersect: {i},{j}")
    twice_area = sum((pts[i][0] * pts[i + 1][1]
                     - pts[i + 1][0] * pts[i][1]) for i in range(n))
    if twice_area == 0:
        raise ValueError("zero planar area")
    signed = twice_area / 2
    return {
        "vertices_with_closure": len(pts),
        "edges": n,
        "nonadjacent_self_intersections": 0,
        "duplicate_vertices_excluding_closure": 0,
        "ring_orientation_native_xy": "CLOCKWISE" if signed < 0 else "COUNTERCLOCKWISE",
        "signed_native_planar_area_m2": str(signed),
        "absolute_native_planar_area_m2": str(abs(signed)),
        "absolute_native_planar_area_km2": str(abs(signed) / Decimal(1000000)),
    }

def compute():
    source = load_source()
    geom = source["native_geometry"]
    result = native_topology(geom["coordinates_xy_m"][0])
    if result["vertices_with_closure"] != 47:
        raise ValueError("unexpected source vertex count")
    return {
        "schema": "conde.gis.ibge-1960-native-topology/v1",
        "id": "CGEO-12",
        "source": {
            "polygon_id": "CGEO-10",
            "source_ring_sha256": geom["ring_xy_sha256"],
            "source_zip_sha256": source["source"]["zip_sha256"],
            "native_crs": source["native_crs"],
            "evidence_dependencies": ["CGEO-10", "CGEO-11"],
            "independent_geographical_observation": False,
        },
        "calculation": {
            "method": "Decimal shoelace and pairwise exact decimal segment intersections",
            "coordinates": "CGEO-10 native projected (easting_m,northing_m)",
            **result,
            "reported_positional_accuracy_m": None,
            "interpretation": "PLANAR_METRIC_OF_RETROSPECTIVE_DRAWING_NOT_SURVEYED_SURFACE_AREA",
        },
        "scope": {
            "historic_1963_legal_polygon": None,
            "1963_event_position": None,
            "1963_point_membership": None,
            "1963_position_error_m": None,
            "can_restrict_historical_reentry": False,
            "cannot_infer_boundary_change_from_area": True,
            "nominal_1960_year_not_measurement_epoch": True,
            "reason": "CGEO-11 documents derivation from 1991 and no cartographic precision. Topological validity is not temporal or geodetic accuracy.",
        },
        "dependency_graph": {
            "edges": [
                {"source": "CGEO-10", "target": "CGEO-12", "kind": "COMPUTED_FROM_SAME_PINNED_VERTICES_NOT_NEW_SOURCE"},
                {"source": "CGEO-11", "target": "CGEO-12", "kind": "LIMITS_HISTORICAL_ACCURACY_INTERPRETATION"},
                {"source": "CGEO-12", "target": "LEGAL_BOUNDARY_CONDE_1963_LATENT", "kind": "NOT_A_VALIDATED_TEMPORAL_BRIDGE"},
            ]
        },
    }

def validate(path=AUDIT):
    expected = compute()
    actual = json.loads(Path(path).read_text(encoding="utf-8"))
    if actual != expected:
        raise ValueError("CGEO-12 audit differs from exact pinned CGEO-10 computation")
    return actual

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", action="store_true")
    args = cli.parse_args()
    result = validate() if args.check else compute()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
