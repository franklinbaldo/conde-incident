#!/usr/bin/env python3
"""CGEO-61: CONDER contemporary municipal seat as a separate geographic proxy."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo61_conder_sede_point.json"
OSM = ROOT / "research/geo/cgeo60_modern_osm_cut.json"
EARTH_RADIUS_M = 6371000
SERVICES = (
    ("SEDES_MUNICIPAIS_PTO", "MUNICIPIO='CONDE'"),
    ("LOCALIDADES", "COD_MUNICIPIO='2908606'"),
)
ENDPOINT = "https://mapas.conder.ba.gov.br/arcgis/rest/services/BAHIA/"
COORD = [-37.60697798199999, -11.813431761000004]


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def expected_url(name: str, where: str) -> str:
    query = urllib.parse.urlencode({
        "where": where, "outFields": "*", "returnGeometry": "true",
        "outSR": "4326", "f": "geojson", "resultRecordCount": "10",
    })
    return f"{ENDPOINT}{name}/MapServer/0/query?{query}"


def distance_and_bearing(osm: dict, official: dict) -> tuple[float, float]:
    a, b = math.radians(osm["latitude"]), math.radians(official["latitude"])
    c, d = math.radians(osm["longitude"]), math.radians(official["longitude"])
    h = math.sin((b-a)/2)**2 + math.cos(a)*math.cos(b)*math.sin((d-c)/2)**2
    distance = EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(h), math.sqrt(1-h))
    y = math.sin(d-c)*math.cos(b)
    x = math.cos(a)*math.sin(b)-math.sin(a)*math.cos(b)*math.cos(d-c)
    return distance, (math.degrees(math.atan2(y, x))+360) % 360


def validate(data: dict, osm: dict) -> dict:
    need(data["id"] == "CGEO-61" and
         data["schema"] == "conde.gis.conder-sede-point-2026/v1",
         "wrong scientific contract")
    need(data["municipality"] == {"name":"Conde", "uf":"BA", "ibge_code":"2908606"},
         "wrong municipality")
    src = data["source"]
    need(src["organization"] == "CONDER/BA"
         and src["domain"] == "mapas.conder.ba.gov.br"
         and src["spatial_reference"] == "EPSG:4326 (ArcGIS wkid 4326)"
         and src["data_epoch"] is None
         and src["measurement_accuracy_m"] is None
         and src["license"] == "NOT_VERIFIED", "source metadata inflated")
    queries = src["service_queries"]
    need(len(queries) == len(SERVICES), "wrong number of source queries")
    pinned = (
        (232, "dbb93fe280700e3931a30fcef07414030a2eedf5a00b9629ed6496104c2fb7d3"),
        (489, "6d2cbd335863ca5525824312fed51c52c4361a2efcd1d3c5e28a202552c6d708"),
    )
    for record, (name, where), (size, digest) in zip(queries, SERVICES, pinned):
        need(record["raw_bytes"] == size and record["raw_sha256"] == digest,
             "source acquisition hash/size tampered")
        need(record["service"] == name and record["where"] == where
             and record["url"] == expected_url(name,where), "query identity changed")
        need(record["acquired_http_status"] == 200
             and record["raw_bytes"] > 50
             and isinstance(record["raw_sha256"], str)
             and len(record["raw_sha256"]) == 64
             and all(c in "0123456789abcdef" for c in record["raw_sha256"]),
             "missing source custody")
    point = data["point"]
    need(point == {
        "objectid":1038, "code":"290860605000001", "municipal_code":"2908606",
        "name":"Conde", "class":"URBANO / CIDADE / Sede",
        "longitude":COORD[0], "latitude":COORD[1],
        "role":"CONDER_PRESENT_DAY_SEAT_PROXY_ONLY"}, "unverified CONDER point")
    need(data["dependence"] == {
        "services_have_same_objectid_code_coordinates":True,
        "independent_measurements_established":False}, "fake independent evidence")
    need(osm["id"] == "CGEO-60" and osm["municipality"] == data["municipality"],
         "OSM parent source mismatch")
    nodes = osm["nodes"]
    need(len(nodes) == 2 and nodes[0]["osm_node_id"] == 415521889
         and nodes[0]["latitude"] == -11.8129758
         and nodes[0]["longitude"] == -37.6138705,
         "parent OSM proxy unexpectedly changed")
    comp = data["comparator"]
    need(comp["source_contract"] == "research/geo/cgeo60_modern_osm_cut.json"
         and comp["osm_node_id"] == 415521889
         and comp["method"] == "haversine spherical Earth radius 6371000 m",
         "distance lineage not established")
    dist, bearing = distance_and_bearing(nodes[0], point)
    need(abs(dist-comp["separation_m"]) < 0.000001
         and abs(bearing-comp["initial_bearing_deg"]) < 0.000001,
         "distance/bearing did not reproduce")
    guard = data["historical_guards"]
    need(guard == {
        "as_of_november_1963_point":None, "physical_continuity_to_1963":None,
        "georeferencing_accuracy_m":None, "impact_location":None,
        "modern_sede_is_historical_center":False,
        "can_constrain_orbital_reentry":False,
        "active_constraint":False, "posterior":False},
        "historical center / orbital constraint promoted without evidence")
    return {"distance_m":round(dist,6), "bearing_deg":round(bearing,6),
            "historical_center":None, "active_constraint":False}


def inspect_geojson(raw: bytes, record: dict, point: dict) -> dict:
    obj = json.loads(raw)
    need(obj.get("type") == "FeatureCollection" and
         len(obj.get("features", [])) == 1, "wrong GeoJSON feature count")
    feature = obj["features"][0]
    need(feature["type"] == "Feature" and feature["id"] == point["objectid"],
         "wrong feature identity")
    geometry = feature["geometry"]
    need(geometry["type"] == "Point" and geometry["coordinates"] == COORD,
         "source point changed or non-WGS84 coordinates")
    props = feature["properties"]
    need(props["OBJECTID"] == point["objectid"]
         and props["CODIGO"] == point["code"], "official record code mismatch")
    if record["service"] == "SEDES_MUNICIPAIS_PTO":
        need(props["MUNICIPIO"] == "CONDE", "sede city mismatch")
    elif record["service"] == "LOCALIDADES":
        need(props["MUNICIPIO"] == "CONDE"
             and props["COD_MUNICIPIO"] == "2908606"
             and props["UF"] == "BAHIA"
             and props["TIPO"] == "URBANO"
             and props["CATEGORIA"] == "CIDADE"
             and props["NOME"] == "Sede", "localidade classification mismatch")
    else:
        raise ValueError("unknown CONDER layer")
    digest = hashlib.sha256(raw).hexdigest()
    return {"service":record["service"], "semantic_match":True,
            "binary_match":len(raw) == record["raw_bytes"]
                 and digest == record["raw_sha256"],
            "current_bytes":len(raw), "current_sha256":digest}


def replay_live(data: dict) -> list[dict]:
    output = []
    for record in data["source"]["service_queries"]:
        req = urllib.request.Request(record["url"], headers={
            "User-Agent":"conde-incident-cgeo61-custody/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            need(response.status == 200, "CONDER API HTTP error")
            raw = response.read(500000)
        output.append(inspect_geojson(raw, record, data["point"]))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    osm = json.loads(OSM.read_text(encoding="utf-8"))
    result = validate(data, osm)
    if args.live:
        result["live"] = replay_live(data)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
