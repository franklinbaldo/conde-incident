#!/usr/bin/env python3
"""IBGE municipality boundary custody + native SIRGAS2000 point tests.

Only handles the pinned BA shapefile archives for Conde (one polygon ring).
No transformation to WGS84, historic boundary inference, or event location.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile

MUNICIPALITY_CODE = "2908606"
EARTH_SPHERE_M = 6371008.8  # approximate distance guard only, NOT official IBGE area
SOURCES = {
    2022: {
        "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/BA/BA_Municipios_2022.zip",
        "zip_sha256": "6559f564071dec2d49e3c55061049190054ea71121cb02e2e6d9cbf8e9bc7c48",
        "record_sha256": "6d7f5a4704bec09f09a9fcbc4d82cd287cae1c541d7606ffd51a805d8d87b678",
        "vertices": 3303,
        "record_index": 104,
        "coordinate_sha256": "e75bf5c81c4e08b5d6f6e249de36c4b28c4593c048537d8fc823c4fee92a79db",
    },
    2025: {
        "url": "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/BA/BA_Municipios_2025.zip",
        "zip_sha256": "cac0d02febfaaf1da20d0d5c1fe5d6289377ffaa745c8334ec9b7d85a413956f",
        "record_sha256": "e31617673efb495573fcde3a7bfe34d7644d1be66db140ac34aef01840c4a79d",
        "vertices": 3260,
        "record_index": 305,
        "coordinate_sha256": "98fdbae58b24ef150bed02b389d9f5834bc8741a53d43ecf6664fec7d6224111",
    },
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _dbf_rows(data: bytes) -> list[dict[str, str]]:
    if len(data) < 33:
        raise ValueError("invalid DBF header")
    count = struct.unpack_from("<I", data, 4)[0]
    header = struct.unpack_from("<H", data, 8)[0]
    size = struct.unpack_from("<H", data, 10)[0]
    if header > len(data) or size < 2 or len(data) < header + count * size:
        raise ValueError("invalid DBF lengths")
    fields = []
    offset = 32
    while offset < header and data[offset] != 13:
        f = data[offset:offset + 32]
        if len(f) != 32:
            raise ValueError("truncated DBF field")
        fields.append((f[:11].split(b"\x00")[0].decode("ascii"), f[16]))
        offset += 32
    if offset >= header or not fields:
        raise ValueError("invalid DBF fields")
    records = []
    for index in range(count):
        record = data[header + index * size:header + (index + 1) * size]
        if record[0] != 32:
            raise ValueError("deleted or invalid DBF record")
        values, cursor = {}, 1
        for name, length in fields:
            values[name] = record[cursor:cursor + length].decode("utf-8").strip()
            cursor += length
        if cursor != size:
            raise ValueError("DBF row width differs from fields")
        records.append(values)
    return records


def extract_conde(archive: bytes, year: int) -> dict:
    """Extract unchanged native longitude/latitude coordinates, fail closed."""
    if year not in SOURCES:
        raise ValueError("unapproved source year")
    spec = SOURCES[year]
    if _sha256(archive) != spec["zip_sha256"]:
        raise ValueError("IBGE source ZIP SHA256 differs from pinned acquisition")
    base = f"BA_Municipios_{year}"
    with zipfile.ZipFile(__import__("io").BytesIO(archive)) as z:
        prj = z.read(base + ".prj").decode("ascii")
        if not all(word in prj for word in
                   ('GCS_SIRGAS_2000', 'D_SIRGAS_2000', 'Degree')):
            raise ValueError("unexpected source CRS; cannot silently transform")
        if z.read(base + ".cpg").strip() != b"UTF-8":
            raise ValueError("unexpected DBF character encoding")
        rows = _dbf_rows(z.read(base + ".dbf"))
        hits = [(n, row) for n, row in enumerate(rows)
                if row.get("CD_MUN") == MUNICIPALITY_CODE]
        if len(hits) != 1:
            raise ValueError("Conde municipality code absent/ambiguous")
        index, row = hits[0]
        if index != spec["record_index"] or row.get("NM_MUN") != "Conde" or row.get("SIGLA_UF") != "BA":
            raise ValueError("unexpected DBF identity or row position")
        shx = z.read(base + ".shx")
        shp = z.read(base + ".shp")
        start, count_words = struct.unpack_from(">ii", shx, 100 + 8 * index)
        record_start = start * 2
        record_number, length_words = struct.unpack_from(">ii", shp, record_start)
        record = shp[record_start + 8:record_start + 8 + length_words * 2]
        if record_number != index + 1 or length_words != count_words:
            raise ValueError("shp/shx record mismatch")
        if _sha256(record) != spec["record_sha256"]:
            raise ValueError("Conde SHP record no longer matches pinned source")
        if struct.unpack_from("<i", record, 0)[0] != 5:
            raise ValueError("only planar ESRI polygon supported")
        box = struct.unpack_from("<4d", record, 4)
        parts, n = struct.unpack_from("<ii", record, 36)
        if parts != 1 or n != spec["vertices"]:
            # Never accidentally mis-handle islands, holes or topology changes.
            raise ValueError("single-ring source assumption changed")
        if struct.unpack_from("<i", record, 44)[0] != 0:
            raise ValueError("ring must begin at index zero")
        points = [list(struct.unpack_from("<2d", record, 48 + i * 16))
                  for i in range(n)]
        if points[0] != points[-1] or any(
            not (math.isfinite(lon) and math.isfinite(lat)
                 and -180 <= lon <= 180 and -90 <= lat <= 90)
            for lon, lat in points
        ):
            raise ValueError("invalid coordinates/ring closure")
        computed_box = [min(p[0] for p in points), min(p[1] for p in points),
                        max(p[0] for p in points), max(p[1] for p in points)]
        if any(abs(a - b) > 1e-8 for a, b in zip(box, computed_box)):
            raise ValueError("SHP bbox differs from vertices")
        area = float(row["AREA_KM2"])
        if not (900 < area < 1000):
            raise ValueError("invalid area attribute")
        return {
            "schema": "conde.gis.municipal-boundary-native/v1",
            "jurisdiction": {"municipality_code_ibge": MUNICIPALITY_CODE,
                             "municipality": "Conde", "state": "BA"},
            "source": {"agency": "IBGE", "edition": year, "archive_url": spec["url"],
                       "archive_sha256": spec["zip_sha256"],
                       "shp_record_sha256": spec["record_sha256"],
                       "shapefile_name": base, "dbf_record_index_zero_based": index},
            "coordinates": {"reference_system": "SIRGAS 2000",
                            "epsg": 4674,
                            "axis_order": ["longitude", "latitude"],
                            "units": "decimal_degrees",
                            "transform_to_wgs84_performed": False,
                            "reference_epoch": None},
            "metadata": {"reported_area_km2": area, "vertices_including_closure": n,
                         "bbox_lonlat": computed_box,
                         "boundary_positional_accuracy_m": None,
                         "valid_in_november_1963": "NOT_ESTABLISHED",
                         "not_observation_of_fall_or_reentry": True},
            # GeoJSON-like polygon positions in EPSG:4674; not claimed as RFC 7946 WGS84.
            "geometry": {"type": "Polygon", "coordinates": [points]},
        }


def read_snapshot(path: Path) -> dict:
    o = json.loads(path.read_text(encoding="utf-8"))
    if o.get("schema") != "conde.gis.municipal-boundary-native/v1" or o.get("coordinates", {}).get("epsg") != 4674:
        raise ValueError("invalid boundary contract/CRS")
    year = o.get("source", {}).get("edition")
    if year not in SOURCES or o["source"].get("archive_sha256") != SOURCES[year]["zip_sha256"]:
        raise ValueError("unapproved source provenance")
    if o.get("jurisdiction", {}).get("municipality_code_ibge") != MUNICIPALITY_CODE:
        raise ValueError("wrong municipality")
    if o["source"].get("archive_url") != SOURCES[year]["url"] or o["source"].get("shp_record_sha256") != SOURCES[year]["record_sha256"]:
        raise ValueError("source mismatch")
    ring = o.get("geometry", {}).get("coordinates", [[]])[0]
    if (o["geometry"]["type"] != "Polygon" or
        len(o["geometry"]["coordinates"]) != 1 or
        len(ring) != SOURCES[year]["vertices"] or ring[0] != ring[-1] or
        any(not isinstance(p, list) or len(p) != 2 or not all(math.isfinite(v) for v in p)
            for p in ring)):
        raise ValueError("invalid polygon structure")
    canonical_points = json.dumps(ring, ensure_ascii=False, separators=(",", ":")).encode()
    if _sha256(canonical_points) != SOURCES[year]["coordinate_sha256"]:
        raise ValueError("coordinates do not match pinned source")
    if o.get("metadata", {}).get("reported_area_km2") != 931.106:
        raise ValueError("unexpected area attribute")
    if o.get("metadata", {}).get("valid_in_november_1963") != "NOT_ESTABLISHED":
        raise ValueError("historical status must remain unknown")
    return o


def ring_position(lon: float, lat: float, ring: list[list[float]],
                  boundary_margin_m: float = 0.0) -> dict:
    """Inside polygon and approximate distance to nearest edge (guard only).

    Distance uses tangent-plane equirectangular approximation, never a
    certified geodetic/error bound. User-supplied margin is NOT measured accuracy.
    """
    if not (math.isfinite(lon) and math.isfinite(lat) and
            -180 <= lon <= 180 and -90 <= lat <= 90 and
            math.isfinite(boundary_margin_m) and 0 <= boundary_margin_m <= 100000):
        raise ValueError("invalid geographic query or margin")
    inside = False
    scale_x = EARTH_SPHERE_M * math.pi / 180 * math.cos(math.radians(lat))
    scale_y = EARTH_SPHERE_M * math.pi / 180
    min_dist2 = math.inf
    for (ax, ay), (bx, by) in zip(ring, ring[1:]):
        if (ay > lat) != (by > lat) and lon < (bx - ax) * (lat - ay) / (by - ay) + ax:
            inside = not inside
        x0, y0 = (ax - lon) * scale_x, (ay - lat) * scale_y
        dx, dy = (bx - ax) * scale_x, (by - ay) * scale_y
        t = max(0, min(1, -(x0 * dx + y0 * dy) / (dx * dx + dy * dy))) if dx * dx + dy * dy > 0 else 0
        min_dist2 = min(min_dist2, (x0 + t * dx) ** 2 + (y0 + t * dy) ** 2)
    dist = math.sqrt(min_dist2)
    return {
        "modern_polygon_membership": (
            "NEAR_BOUNDARY" if dist <= boundary_margin_m + 1e-7 else
            "INSIDE" if inside else "OUTSIDE"),
        "approx_distance_to_polygon_edge_m": round(dist, 3),
        "user_selected_boundary_margin_m": boundary_margin_m,
        "distance_method": "LOCAL_EQUIRECTANGULAR_APPROX_NOT_GEODETIC_CERTIFICATE",
    }


def evaluate(lon: float, lat: float, date_utc: str, point_crs: str,
             margin_m: float, snapshot_2022: dict, snapshot_2025: dict) -> dict:
    """No exclusion of Conde in 1963 from modern administrative polygons."""
    if point_crs != "EPSG:4674":
        raise ValueError("CRS transformation/error budget required before spatial comparison")
    try:
        observation_date = date.fromisoformat(date_utc)
    except (TypeError, ValueError) as exc:
        raise ValueError("date must be YYYY-MM-DD") from exc
    by_edition = {}
    for snapshot in (snapshot_2022, snapshot_2025):
        if snapshot["source"]["edition"] not in (2022, 2025):
            raise ValueError("wrong snapshot edition")
        y = str(snapshot["source"]["edition"])
        by_edition[y] = ring_position(lon, lat, snapshot["geometry"]["coordinates"][0], margin_m)
    result_codes = {v["modern_polygon_membership"] for v in by_edition.values()}
    if "NEAR_BOUNDARY" in result_codes:
        compare = "INDETERMINATE_NEAR_MODERN_BOUNDARY"
    elif len(result_codes) > 1:
        compare = "DISCORDANT_MODERN_EDITIONS"
    else:
        compare = "CONSISTENT_MODERN_" + next(iter(result_codes))
    return {
        "schema": "conde.gis.point-eligibility/v1",
        "query": {"lon": lon, "lat": lat, "point_crs": point_crs,
                  "date": observation_date.isoformat()},
        "source_edition_results": by_edition,
        "modern_comparison": compare,
        "historical_1963_membership": (
            "UNRESOLVED_NO_1963_BOUNDARY"
            if observation_date.year == 1963 else "NOT_ASSESSED"),
        "can_constrain_historical_orbital_reentry": False,
        "suitable_for_geodetic_distance_to_impact": False,
        "missing": [
            "certified 1963 municipality polygon or legal boundary reconstruction",
            "source boundary positional error and geodetic frame transformation",
            "geolocated independent observation or calibrated reentry model",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extract", type=Path, help="pinned IBGE ZIP to extract")
    ap.add_argument("--year", type=int, choices=sorted(SOURCES))
    ap.add_argument("--output", type=Path, help="write extracted native-CRS JSON")
    ap.add_argument("--lon", type=float, help="explicit query longitude")
    ap.add_argument("--lat", type=float, help="explicit query latitude")
    ap.add_argument("--date", default="1963-11-08", help="date of question (ISO)")
    ap.add_argument("--point-crs", default="EPSG:4674")
    ap.add_argument("--boundary-margin-m", type=float, default=0.0)
    ap.add_argument("--dir", type=Path, default=Path("research/geo"))
    args = ap.parse_args()
    if args.extract is not None:
        if args.year is None or args.output is None:
            ap.error("--extract requires --year and --output")
        payload = extract_conde(args.extract.read_bytes(), args.year)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
                               + "\n", encoding="utf-8")
        print(json.dumps({"edition": args.year, "source": payload["source"]["archive_url"],
                          "vertices": payload["metadata"]["vertices_including_closure"]}))
        return 0
    if args.lon is None or args.lat is None:
        ap.error("supply --lon and --lat, or --extract")
    a = read_snapshot(args.dir / "conde_ibge_2022_sirgas2000.json")
    b = read_snapshot(args.dir / "conde_ibge_2025_sirgas2000.json")
    print(json.dumps(evaluate(args.lon, args.lat, args.date, args.point_crs,
                              args.boundary_margin_m, a, b),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
