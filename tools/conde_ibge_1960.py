"""CGEO-10: replay historical IBGE cartographic reconstruction, not legal 1963 limits."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/conde_ibge_1960_world_polyconic.json"
SOURCE_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/"
    "evolucao_da_divisao_territorial_do_brasil/"
    "evolucao_da_divisao_territorial_do_brasil_1872_2010/"
    "municipios_1872_1991/divisao_territorial_1872_1991/1960/"
    "05_malha_municipal_1960.zip"
)
ZIP_SHA = "261399b8557ee26c118e94b13cebf3b6b3e1c70e91b5e8438a348847b875120f"
MEMBER_BASE = "05-malha municipal 1960"
MEMBER_SHAS = {
    ".prj": "c90d581eaa847ae6dd5a94043893b99603186ae7d39a58f603e328d2284c2cf1",
    ".dbf": "9487b8851864b5a66edcf49290dfff0e208a7aea649364f30d0b6bd22619fea2",
    ".shp": "2ac08c065cea42ee0f45ff93545e94d0d29a164ccc9a7e6a6ac7616964256b9a",
    ".shx": "3b47bddb84fce48a124fd7b82abe35829b6021ad6da9cd6a8437d25c0a412757",
}
RECORD_SHA = "2970e4ee04d39e1c4865dbdb56ee1a21db9999d8c964ef0f08828c001783c601"
RING_SHA = "735bfbc0f36f6b97c17085824af6f6b4f56f268d94481c05dd75bf8a0a141e23"
RECORD_INDEX = 2448  # zero-based SHP/DBF record index
CRS_NAME = "World_Polyconic"
CODE = "2908606"
NAME = "Conde"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_dbf(raw: bytes, row_index: int) -> dict[str, str]:
    nrecords, = struct.unpack_from("<I", raw, 4)
    header_length, record_length = struct.unpack_from("<HH", raw, 8)
    if not 0 <= row_index < nrecords or header_length < 33:
        raise ValueError("DBF index or header invalid")
    if header_length + nrecords * record_length > len(raw):
        raise ValueError("DBF truncated")
    fields = []
    for offset in range(32, header_length - 1, 32):
        field = raw[offset:offset + 32]
        name = field[:11].split(b"\x00", 1)[0].decode("ascii").lower()
        fields.append((name, field[16]))
    rec = raw[header_length + row_index * record_length:
              header_length + (row_index + 1) * record_length]
    if rec[:1] != b" ":
        raise ValueError("DBF row deleted")
    values = {}
    cursor = 1
    for name, width in fields:
        values[name] = rec[cursor:cursor + width].decode("latin-1").strip()
        cursor += width
    if cursor != record_length:
        raise ValueError("DBF record width mismatch")
    return values


def parse_shp(shp: bytes, shx: bytes, row_index: int) -> tuple[list[list[float]], list[float], str]:
    if (struct.unpack_from(">i", shp, 0)[0] != 9994
            or struct.unpack_from("<i", shp, 32)[0] != 5):
        raise ValueError("not an ESRI polygon shapefile")
    index_offset = 100 + 8 * row_index
    if index_offset + 8 > len(shx):
        raise ValueError("SHP index out of range")
    record_offset, record_length = struct.unpack_from(">ii", shx, index_offset)
    begin, size = record_offset * 2, record_length * 2
    if begin + 8 + size > len(shp) or size < 44:
        raise ValueError("SHP record truncated")
    number, length = struct.unpack_from(">ii", shp, begin)
    if number != row_index + 1 or length != record_length:
        raise ValueError("SHP/SHX record mismatch")
    rec = shp[begin + 8:begin + 8 + size]
    shape_type, = struct.unpack_from("<i", rec, 0)
    bbox = list(struct.unpack_from("<4d", rec, 4))
    parts, npoints = struct.unpack_from("<ii", rec, 36)
    if shape_type != 5 or parts != 1 or npoints != 47:
        raise ValueError("Conde must be exactly one ring with 47 points")
    part_start, = struct.unpack_from("<i", rec, 44)
    if part_start != 0 or 48 + npoints * 16 != len(rec):
        raise ValueError("unexpected part or XY payload length")
    coords = [list(struct.unpack_from("<2d", rec, 48 + i * 16)) for i in range(npoints)]
    if coords[0] != coords[-1]:
        raise ValueError("ring is not closed")
    if ([min(p[0] for p in coords), min(p[1] for p in coords),
         max(p[0] for p in coords), max(p[1] for p in coords)] != bbox):
        raise ValueError("SHP bounds do not match coordinates")
    return coords, bbox, sha(rec)


def extract(zip_path: Path) -> dict:
    raw = zip_path.read_bytes()
    if sha(raw) != ZIP_SHA:
        raise ValueError("official 1960 ZIP SHA256 mismatch, never substitute another file")
    with zipfile.ZipFile(zip_path) as z:
        parts = {}
        for suffix, expected in MEMBER_SHAS.items():
            payload = z.read(MEMBER_BASE + suffix)
            if sha(payload) != expected:
                raise ValueError("archive member checksum mismatch: " + suffix)
            parts[suffix] = payload
    dbf = parse_dbf(parts[".dbf"], RECORD_INDEX)
    if dbf != {"codigo": CODE, "nome": NAME}:
        raise ValueError("record is not Conde BA")
    wkt = parts[".prj"].decode("ascii")
    for required in (
        'PROJCS["World_Polyconic"', 'GEOGCS["GCS_SIRGAS_2000"',
        'DATUM["D_SIRGAS_2000"', 'SPHEROID["GRS_1980"',
        'PARAMETER["Central_Meridian",-54.0]',
        'PARAMETER["Latitude_Of_Origin",0.0]', 'UNIT["Meter",1.0]',
    ):
        if required not in wkt:
            raise ValueError("native projection not confirmed: " + required)
    coords, bbox, record_hash = parse_shp(parts[".shp"], parts[".shx"], RECORD_INDEX)
    if record_hash != RECORD_SHA:
        raise ValueError("Conde source record changed")
    ring_hash = sha(json.dumps(coords, separators=(",", ":")).encode("utf-8"))
    if ring_hash != RING_SHA:
        raise ValueError("Conde XY coordinate payload does not match pinned record")
    return {
        "schema": "conde.gis.ibge-cartographic-1960/v1",
        "id": "CGEO-10",
        "municipality": {"name": NAME, "uf": "BA", "ibge_code": CODE},
        "source": {
            "publisher": "IBGE",
            "catalog": "Evolução da Divisão Territorial do Brasil 1872–2010",
            "nominal_map_year": 1960,
            "archive_url": SOURCE_URL,
            "zip_sha256": ZIP_SHA,
            "members_sha256": MEMBER_SHAS,
            "shapefile_record_index_zero_based": RECORD_INDEX,
            "shapefile_record_sha256": RECORD_SHA,
            "dbf_identifier": dbf,
            "lineage": "Later cartographic reconstruction; archive metadata records ArcGIS projection definition in 2013 and directory file timestamp 2016; not a 1960 survey."
        },
        "native_crs": {
            "name": CRS_NAME,
            "projection": "Polyconic",
            "datum": "SIRGAS_2000",
            "ellipsoid": "GRS_1980",
            "central_meridian_deg": -54.0,
            "latitude_of_origin_deg": 0.0,
            "linear_unit": "metre",
            "epsg_projected": None,
            "prj_sha256": MEMBER_SHAS[".prj"],
            "axis_order": ["easting_m", "northing_m"],
            "wkt_source": MEMBER_BASE + ".prj"
        },
        "native_geometry": {
            "type": "Polygon",
            "coordinates_xy_m": [coords],
            "bbox_xy_m": bbox,
            "vertex_count_with_closure": len(coords),
            "ring_xy_sha256": RING_SHA,
            "topological_quality": "NOT_SURVEY_GRADE_OR_LEGAL_BOUNDARY"
        },
        "historical_1963": {
            "requested_event_date": "1963-11-08",
            "legal_boundary_for_date": None,
            "date_1963_membership": None,
            "coordinate_transformation_to_event_frame": None,
            "geodetic_epoch_and_horizontal_accuracy_m": None,
            "can_constrain_reentry": False,
            "reason": "1960 retrospective municipal map is neither a verified 1963 legal boundary nor a 1963 event observation; CGEO-09 legal chronology remains unresolved."
        },
        "dependency_graph": {
            "nodes": ["CGEO-10", "CGEO-09", "CGEO-01", "CGEO-02",
                      "municipal_cartography_1960", "legal_boundary_1963_LATENT"],
            "edges": [
                {"source": "CGEO-10", "target": "municipal_cartography_1960", "kind": "RETROSPECTIVE_CARTOGRAPHIC_RECONSTRUCTION"},
                {"source": "CGEO-09", "target": "legal_boundary_1963_LATENT", "kind": "NORMATIVE_CONTINUITY_PENDING"},
                {"source": "municipal_cartography_1960", "target": "legal_boundary_1963_LATENT", "kind": "NOT_A_VALIDATED_TEMPORAL_BRIDGE"}
            ]
        }
    }


def load_contract(path: Path = CONTRACT) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "conde.gis.ibge-cartographic-1960/v1":
        raise ValueError("wrong 1960 contract schema")
    s = data.get("source", {})
    if (s.get("zip_sha256") != ZIP_SHA or s.get("archive_url") != SOURCE_URL
            or s.get("shapefile_record_sha256") != RECORD_SHA
            or s.get("members_sha256") != MEMBER_SHAS
            or s.get("dbf_identifier") != {"codigo": CODE, "nome": NAME}):
        raise ValueError("source custody mutated")
    if data.get("native_crs", {}).get("epsg_projected") is not None:
        raise ValueError("invented EPSG projected code")
    xy = data.get("native_geometry", {})
    ring = xy.get("coordinates_xy_m", [[]])[0]
    if (xy.get("vertex_count_with_closure") != 47 or len(ring) != 47
            or ring[0] != ring[-1] or len(xy.get("bbox_xy_m", [])) != 4):
        raise ValueError("native geometry corrupted")
    if (xy.get("ring_xy_sha256") != RING_SHA or
            sha(json.dumps(ring, separators=(",", ":")).encode("utf-8")) != RING_SHA):
        raise ValueError("native geometry corrupted")
    if data.get("historical_1963") != extract_1963_veto():
        raise ValueError("historic 1963 status was illicitly promoted")
    links = data.get("dependency_graph", {}).get("edges", [])
    if not any(e.get("kind") == "NOT_A_VALIDATED_TEMPORAL_BRIDGE" for e in links):
        raise ValueError("missing veto to temporal extrapolation")
    return data


def extract_1963_veto() -> dict:
    return {
        "requested_event_date": "1963-11-08",
        "legal_boundary_for_date": None,
        "date_1963_membership": None,
        "coordinate_transformation_to_event_frame": None,
        "geodetic_epoch_and_horizontal_accuracy_m": None,
        "can_constrain_reentry": False,
        "reason": "1960 retrospective municipal map is neither a verified 1963 legal boundary nor a 1963 event observation; CGEO-09 legal chronology remains unresolved."
    }


def evaluate(day: str, contract: dict) -> dict:
    try:
        date.fromisoformat(day)
    except ValueError as exc:
        raise ValueError("date must be YYYY-MM-DD") from exc
    if contract is None:
        raise ValueError("missing contract")
    return {
        "id": "CGEO-10",
        "query_date": day,
        "geometry_available": "IBGE_RETROSPECTIVE_NOMINAL_1960_POLYGON_NATIVE_METRES",
        "legal_boundary_for_date": None,
        "point_membership_for_date": None,
        "can_constrain_reentry": False,
        "uncertainties": ["time_1960_to_1963", "legal_continuity",
                          "geodetic_epoch", "positional_accuracy", "event_position"],
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--extract", type=Path, help="offline verification of the pinned original ZIP")
    cli.add_argument("--output", type=Path, help="write deterministic JSON to this path")
    cli.add_argument("--date", default="1963-11-08")
    args = cli.parse_args()
    if args.extract:
        result = extract(args.extract)
    else:
        result = evaluate(args.date, load_contract())
    payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
