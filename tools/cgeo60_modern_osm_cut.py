#!/usr/bin/env python3
"""CGEO-60: validate modern OSM node custody and prohibit historical promotion."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo60_modern_osm_cut.json"
EXPECTED_IDS = (415521889, 4697713641)
EXPECTED_TAGS = (("Conde", "town"), ("Villa Velha", "village"))
RADIUS_KM = 6371.0


def require(predicate: bool, message: str) -> None:
    if not predicate:
        raise ValueError(message)


def haversine_km(a: dict, b: dict) -> float:
    lat1, lat2 = map(math.radians, (a["latitude"], b["latitude"]))
    dlat = lat2 - lat1
    dlon = math.radians(b["longitude"] - a["longitude"])
    h = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * RADIUS_KM * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def validate(d: dict) -> dict:
    require(d["id"] == "CGEO-60" and d["schema"] == "conde.gis.modern-osm-place-proxies/v1",
            "wrong contract identity")
    require(d["municipality"] == {"name": "Conde", "uf": "BA", "ibge_code": "2908606"},
            "wrong municipality")
    require(d["source"]["provider"] == "OpenStreetMap API v0.6"
            and d["source"]["license"] == "ODbL 1.0"
            and d["source"]["no_inference_of_ibge_survey_geolocation"] is True,
            "OSM provenance not established")
    nodes = d["nodes"]
    require(len(nodes) == 2 and [n["osm_node_id"] for n in nodes] == list(EXPECTED_IDS),
            "OSM node IDs changed")
    for n, (name, place) in zip(nodes, EXPECTED_TAGS):
        require(n["name_exact"] == name and n["place_tag"] == place, "OSM tag mismatch")
        require(n["url"] == f"https://api.openstreetmap.org/api/0.6/node/{n['osm_node_id']}",
                "OSM source URL mismatch")
        require(n["osm_version"] >= 1 and "Z" == n["record_modified_utc"][-1],
                "missing versioned provenance")
        require(n["http_status_at_acquisition"] == 200 and n["raw_xml_bytes"] > 100
                and len(n["raw_xml_sha256"]) == 64
                and all(c in "0123456789abcdef" for c in n["raw_xml_sha256"]),
                "missing original XML custody")
        require(n["source_tag_not_a_positional_certification"] is True,
                "IBGE tag cannot certify geometry")
        require(isinstance(n["latitude"], (int, float))
                and isinstance(n["longitude"], (int, float))
                and math.isfinite(n["latitude"]) and math.isfinite(n["longitude"])
                and -12.2 < n["latitude"] < -11.5 and -38 < n["longitude"] < -37.4,
                "point outside municipality vicinity")
        require("not_" in n["role"], "unjustified historical equation")
    require(nodes[0]["osm_version"] == 18 and nodes[1]["osm_version"] == 3,
            "source node edition changed")
    require(nodes[0]["record_modified_utc"] == "2026-09-18T15:25:50Z"
            and nodes[1]["record_modified_utc"] == "2023-12-12T22:34:35Z",
            "source node temporal provenance changed")
    require(nodes[0]["latitude"] == -11.8129758
            and nodes[0]["longitude"] == -37.6138705
            and nodes[1]["latitude"] == -11.7968448
            and nodes[1]["longitude"] == -37.6214666,
            "coordinates differ from recorded source XML")
    dist = haversine_km(*nodes)
    v = d["derived"]
    require(abs(dist - v["great_circle_distance_km_earth_radius_6371"]) < 0.000001,
            "distance not reproducible")
    require(v["distance_is_between_two_osm_nodes_not_urban_extent_or_accuracy"] is True,
            "node spacing cannot be treated as municipal extent")
    require(v["feature_diameter_scenario_m"] == 4 and v["usaf_photo_scale_denominator"] == 60000,
            "hypothetical scenario altered")
    film_mm = v["feature_diameter_scenario_m"] * 1000 / v["usaf_photo_scale_denominator"]
    require(abs(film_mm - v["diameter_on_analog_photo_mm_scenario"]) < 0.000001,
            "scale arithmetic does not reproduce")
    require(v["detectability"] == "NOT_DEMONSTRATED_IMAGE_RESOLUTION_CONTRAST_TIME_UNKNOWN",
            "unsupported claim that a 4m feature is detectable")
    h = d["historical_context"]
    for k in ("cgeo20_centro20_point_1963", "cgeo20_vila20_point_1963",
              "time_bridge_to_1963", "reentry_impact_location"):
        require(h[k] is None, f"{k}: false historical geocoding")
    require(h["nara_flights_candidate_year"] == 1942
            and h["nara_index_preparation_year"] == 1956
            and h["nara_can_show_november_1963_trace"] is False
            and h["sgb_usaf_photoindex_date_label"] == "1964-1970"
            and h["sgb_is_a_validated_1963_capture"] is False
            and h["modern_nodes_equate_to_cgeo20_historical_sites"] is False
            and h["can_constrain_orbital_reentry"] is False,
            "time-lineage/geometry guard violated")
    c = d["castor_handoff"]
    require(c["modern_proxy_sensitivity_inputs_only"] is True
            and c["source_geometry_role"] == "named_osm_place_nodes"
            and c["historical_centro20_status"] == "NOT_EVALUATED_NO_CUSTODIED_POINT"
            and c["historical_vila20_status"] == "NOT_EVALUATED_NO_CUSTODIED_POINT"
            and c["phase_constraint"] == "NOT_EVALUATED"
            and c["posterior"] is False
            and c["active_constraint"] is False,
            "unjustified activation of orbital or historical constraint")
    require(c["candidate_comparison_can_be_run_as_separately_labelled_counterfactual"] is True,
            "counterfactual must be distinctly labelled")
    return {"distance_km": round(dist, 6), "film_scenario_mm": round(film_mm, 6),
            "historical_center": None, "active_constraint": False}


def parse_osm_node(xml: bytes, expected: dict) -> dict:
    root = ET.fromstring(xml)
    require(root.tag == "osm" and root.attrib.get("version") == "0.6", "not OSM XML")
    items = root.findall("node")
    require(len(items) == 1, "exactly one OSM node required")
    item = items[0]
    tags = {el.attrib["k"]: el.attrib["v"] for el in item.findall("tag")}
    require(int(item.attrib["id"]) == expected["osm_node_id"], "wrong node")
    require(int(item.attrib["version"]) == expected["osm_version"], "node edited after custody")
    require(item.attrib["timestamp"] == expected["record_modified_utc"], "wrong node epoch")
    require(float(item.attrib["lat"]) == expected["latitude"]
            and float(item.attrib["lon"]) == expected["longitude"], "OSM point changed")
    require(tags.get("name") == expected["name_exact"]
            and tags.get("place") == expected["place_tag"], "name/place mismatch")
    require(tags.get("source") == expected["source_tag"], "source tag mismatch")
    return {"id": expected["osm_node_id"], "sha256": hashlib.sha256(xml).hexdigest(),
            "bytes": len(xml), "semantic_match": True,
            "binary_match": len(xml) == expected["raw_xml_bytes"]
            and hashlib.sha256(xml).hexdigest() == expected["raw_xml_sha256"]}


def replay_live(nodes: list[dict]) -> list[dict]:
    out = []
    for n in nodes:
        request = urllib.request.Request(n["url"], headers={
            "User-Agent": "conde-incident-cgeo60-scientific-custody/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            require(response.status == 200, "source request failed")
            body = response.read(2_000_000)
        out.append(parse_osm_node(body, n))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="verify current XML against pinned nodes")
    a = parser.parse_args()
    d = json.loads(CONTRACT.read_text(encoding="utf-8"))
    result = validate(d)
    if a.live:
        result["live"] = replay_live(d["nodes"])
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
