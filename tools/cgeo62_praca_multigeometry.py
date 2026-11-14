#!/usr/bin/env python3
"""CGEO-62: distinguish named contemporary OSM plaza polygons and road segments.

Offline validation uses original OSM API XML bytes preserved in this repository.
A dated OSM revision is not a geodetic survey or a 1963 historical observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "research/geo/sources"
MANIFEST = ROOT / "research/geo/cgeo62_praca_severino_vieira.json"
R = 6371000.0
REF_LAT, REF_LON = -11.813, -37.612
PINS = (
    (1571425857, 6022, "061edc2ac58a4d15c1a235ae49f53a03b3d079f6f04ae6c8b8ee97d30bd4194f", 1, "2026-10-24T19:25:38Z", "park", 28),
    (1020642398, 2473, "8e16d32e2525bb80a1374db24880dd307a61780e8263d6ce1746f0f21dce2371", 1, "2022-01-12T19:38:26Z", "park", 11),
    (206041518, 2014, "70e10f18d052c5704792d5e3ce3270fcfefa309cdab34cb79f1d0925a1b3f7f4", 4, "2026-10-24T19:25:38Z", "road", 7),
    (1571425854, 1170, "59dbd93dcc5714bdebc395fb042f37614e9b94a201d50f36af25b799cf1a807b", 1, "2026-10-24T19:25:38Z", "road", 3),
)

def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def xy(lat: float, lon: float) -> tuple[float, float]:
    return (R * math.cos(math.radians(REF_LAT)) * math.radians(lon - REF_LON),
            R * math.radians(lat - REF_LAT))

def latlon(x: float, y: float) -> tuple[float, float]:
    return (REF_LAT + math.degrees(y / R),
            REF_LON + math.degrees(x / (R * math.cos(math.radians(REF_LAT)))))

def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    delta_lat, delta_lon = lat2-lat1, lon2-lon1
    h = math.sin(delta_lat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(delta_lon/2)**2
    return 2*R*math.atan2(math.sqrt(h), math.sqrt(1-h))

def parse(raw: bytes, way_id: int) -> dict:
    root = ET.fromstring(raw)
    way = root.find("way")
    need(root.tag == "osm" and way is not None, "OSM XML structure")
    need(int(way.attrib["id"]) == way_id and way.attrib["visible"] == "true", "way identity/visibility")
    nodes = {n.attrib["id"]:(float(n.attrib["lat"]), float(n.attrib["lon"]))
             for n in root.findall("node")}
    refs = [n.attrib["ref"] for n in way.findall("nd")]
    need(refs and len(refs) == len(set(refs)) + (refs[0] == refs[-1]), "node reuse")
    need(all(r in nodes for r in refs), "missing referenced OSM node")
    coords = [nodes[r] for r in refs]
    tags = {t.attrib["k"]:t.attrib["v"] for t in way.findall("tag")}
    return {"id": way_id, "version": int(way.attrib["version"]),
            "timestamp": way.attrib["timestamp"], "tags": tags, "coords": coords}

def summary(raw: bytes, pin: tuple) -> dict:
    way_id, size, digest, version, timestamp, kind, count = pin
    need(len(raw) == size and hashlib.sha256(raw).hexdigest() == digest,
         f"raw source hash mismatch way {way_id}")
    feat = parse(raw, way_id)
    need(feat["version"] == version and feat["timestamp"] == timestamp,
         "source revision metadata mismatch")
    coords = feat["coords"]
    need(len(coords) == count, "node count mismatch")
    need(feat["tags"].get("name") == "Praça Severino Vieira", "different toponym")
    if kind == "park":
        need(feat["tags"].get("leisure") == "park" and len(coords) >= 4
             and coords[0] == coords[-1], "not a closed park")
    else:
        need(feat["tags"].get("highway") == "tertiary" and coords[0] != coords[-1],
             "not an open road")
    pts = [xy(lat, lon) for lat, lon in coords]
    bbox = [min(p[0] for p in coords), min(p[1] for p in coords),
            max(p[0] for p in coords), max(p[1] for p in coords)]
    result = {"osm_way_id":way_id, "role":kind, "osm_version":version,
              "osm_revision_utc":timestamp, "raw_bytes":size, "raw_sha256":digest,
              "url":f"https://api.openstreetmap.org/api/0.6/way/{way_id}/full",
              "node_count":len(coords), "closed":coords[0]==coords[-1],
              "bbox_latlon":bbox}
    if kind == "park":
        double_area = sum(pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1]
                          for i in range(len(pts)-1))
        need(abs(double_area) > 1 and abs(double_area) < 1000000, "invalid polygon area")
        cx = sum((pts[i][0]+pts[i+1][0])*
                 (pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1])
                 for i in range(len(pts)-1))/(3*double_area)
        cy = sum((pts[i][1]+pts[i+1][1])*
                 (pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1])
                 for i in range(len(pts)-1))/(3*double_area)
        result["area_local_planar_m2"] = round(abs(double_area)/2, 3)
        result["planar_centroid_latlon"] = [round(v, 9) for v in latlon(cx, cy)]
    return result

def point_segment_distance(p, a, b) -> float:
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = max(0., min(1., ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)

def boundary_gap(a: list, b: list) -> float:
    pa, pb = [[xy(*c) for c in poly] for poly in (a,b)]
    segments_a = list(zip(pa, pa[1:]))
    segments_b = list(zip(pb, pb[1:]))
    # Here the polygons have a strictly positive latitude gap, so crossing
    # and containment are already excluded by their bounding boxes.
    need(max(c[0] for c in a) < min(c[0] for c in b)
         or max(c[0] for c in b) < min(c[0] for c in a),
         "source polygon latitude envelopes overlap: recompute intersection")
    return min([point_segment_distance(p, x, y) for p in pa[:-1] for x,y in segments_b] +
               [point_segment_distance(p, x, y) for p in pb[:-1] for x,y in segments_a])

def derive() -> dict:
    features = []
    for pin in PINS:
        raw = (SOURCES / f"cgeo62_osm_way_{pin[0]}.xml").read_bytes()
        features.append(summary(raw, pin))
    a, b = [parse((SOURCES / f"cgeo62_osm_way_{pin[0]}.xml").read_bytes(),
                  pin[0])["coords"] for pin in PINS[:2]]
    gap = boundary_gap(a,b)
    c0, c1 = [tuple(f["planar_centroid_latlon"]) for f in features[:2]]
    osm = (-11.8129758,-37.6138705)
    conder = (-11.813431761000004, -37.60697798199999)
    return {
        "id":"CGEO-62",
        "schema":"conde.gis.osm-plaza-multigeometry/v1",
        "municipality":{"name":"Conde","uf":"BA","ibge_code":"2908606"},
        "source":{"provider":"OpenStreetMap API 0.6","license":"ODbL 1.0",
                  "acquisition_date_utc":"2026-11-14",
                  "coordinate_reference":"OSM geographic lat/lon, nominal WGS84",
                  "horizontal_accuracy_m":None,"survey_epoch":None,
                  "feature_count":4,"independent_historical_observations":0},
        "features":features,
        "comparisons":{"park_centroid_separation_m":round(haversine(c0,c1),3),
                       "park_boundary_gap_approx_m":round(gap,3),
                       "park_centroid_to_osm_town_node_m":[round(haversine(c,osm),3) for c in (c0,c1)],
                       "park_centroid_to_conder_sede_m":[round(haversine(c,conder),3) for c in (c0,c1)],
                       "town_proxy_source":"research/geo/cgeo60_modern_osm_cut.json",
                       "conder_proxy_source":"research/geo/cgeo61_conder_sede_point.json",
                       "projection_note":"equirectangular local approximation at -11.813 deg for areas/gap; not an accuracy claim"},
        "interpretation":{"same_name_features_are_one_1963_center":None,
                          "separate_physical_public_squares_proven":False,
                          "plaza_from_1958_is_identical":None,
                          "municipal_document_2020_same_geometry":None,
                          "plaza_polygon_in_1963":None,
                          "impact_location":None,
                          "can_constrain_orbital_reentry":False,
                          "active_constraint":False}
    }

def validate(data: dict) -> dict:
    current = derive()
    need(data == current, "manifest inconsistent with pinned OSM XML and historical guards")
    return {"features":len(current["features"]),
            "named_park_polygons":2,"named_road_segments":2,
            "park_centroid_separation_m":current["comparisons"]["park_centroid_separation_m"],
            "park_boundary_gap_approx_m":current["comparisons"]["park_boundary_gap_approx_m"],
            "active_constraint":False}

def check_live() -> list:
    out = []
    for pin in PINS:
        wid,size,digest,version,*_ = pin
        req = urllib.request.Request(f"https://api.openstreetmap.org/api/0.6/way/{wid}/full",
                         headers={"User-Agent":"conde-incident-research/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r:
            need(r.status == 200, "live API HTTP failure")
            payload = r.read(40000)
        out.append({"id":wid, "raw_bytes":len(payload),
                    "raw_sha256":hashlib.sha256(payload).hexdigest(),
                    "exact_binary_match":len(payload)==size and hashlib.sha256(payload).hexdigest()==digest})
    return out

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--generate",action="store_true")
    parser.add_argument("--live",action="store_true")
    opts=parser.parse_args()
    if opts.generate:
        print(json.dumps(derive(),indent=2,ensure_ascii=False))
    elif opts.live:
        print(json.dumps(check_live(),indent=2))
    else:
        print(json.dumps(validate(json.loads(MANIFEST.read_text(encoding="utf8"))),indent=2))

