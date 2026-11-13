"""Audit CGEO-15 modern camera viewpoints without promoting them into a 1963 event."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).resolve().parents[1] / "research/geo/cgeo15_vila_matriz_2022_camera_points.json"
EXPECTED = (
    ("CGEO15-CAMERA-01", "fa483bae3ae85d4eeb33bc76748f123515c5f87eca7b9a69f35fd2523d97df6d", 5365818, -11.798800, -37.621475),
    ("CGEO15-CAMERA-02", "04e5752d902055071e6ba9e414610bf1ccc1c11d64a93f165df2cd65e6bb3cfa", 3632175, -11.798532, -37.621659),
)

def validate(data: dict) -> dict:
    if (data.get("schema") != "conde.gis.vila-conde-camera-custody/v1"
            or data.get("id") != "CGEO-15" or data.get("event_date") != "1963-11-08"):
        raise ValueError("invalid CGEO-15 identity")
    place = data["place_context"]
    if place.get("ibge_municipality_code") != "2908606" or place.get("building_wikidata") != "Q62063348":
        raise ValueError("wrong municipality or church")
    for k in ("building_centroid", "building_footprint", "municipal_center_1963_point",
              "municipal_center_1963_polygon", "reported_object_location_1963"):
        if k not in place or place[k] is not None:
            raise ValueError("historical location falsely promoted: " + k)
    images = data.get("captured_images", [])
    if len(images) != len(EXPECTED):
        raise ValueError("unexpected camera count")
    for row, (id_, digest, size, lat, lon) in zip(images, EXPECTED):
        if (row.get("id") != id_ or row.get("sha256") != digest or row.get("bytes") != size
                or row.get("license") != "CC BY-SA 4.0"
                or not row.get("original_file", "").startswith("https://upload.wikimedia.org/wikipedia/commons/")
                or row.get("photographer") != "Túllio F"
                or not row.get("capture_local", "").startswith("2022-09-15T")
                or row.get("capture_timezone", "NOT_NULL") is not None):
            raise ValueError("photographic provenance changed")
        point = row["camera_point_from_commons"]
        if (point.get("latitude") != lat or point.get("longitude") != lon
                or point.get("coordinate_role") != "point_of_view"
                or point.get("gps_coordinate_epoch") != "2022-09-15"
                or point.get("srs_usable_for_1963") is not False):
            raise ValueError("camera coordinates promoted or modified")
        for k in ("datum", "epsg", "gps_horizontal_error_m"):
            if k not in point or point[k] is not None:
                raise ValueError("unsupported GIS calibration: " + k)
    archive = data["archived_candidate"]
    if (archive.get("id") != "CGEO15-IBGE-1958-VOL-XX"
            or archive.get("acquired_sha256") != "440bd7eaa42c712c89e65111fbebb7b8f77430f76ecff2be0a96d4eacb11a741"
            or archive.get("acquired_bytes") != 72579243
            or archive.get("pages_visually_inspected") != 0
            or archive.get("conde_page_identified") is not False
            or archive.get("conde_photographs_verified") is not False
            or archive.get("status") != "BYTES_ACQUIRED_CONTENT_NOT_INSPECTED_RESOURCE_LIMIT"):
        raise ValueError("historical volume falsely promoted")
    graph = data["dependency_graph"]
    edges = [(v.get("from"), v.get("to"), v.get("relation")) for v in graph.get("links", [])]
    expected_edges = [
        ("CGEO15-CAMERA-01", "CGEO15-PHOTOGRAPHIC-SESSION-2022", "SAME_PHOTOGRAPHER_SESSION"),
        ("CGEO15-CAMERA-02", "CGEO15-PHOTOGRAPHIC-SESSION-2022", "SAME_PHOTOGRAPHER_SESSION"),
        ("CGEO15-PHOTOGRAPHIC-SESSION-2022", "CGEO-14", "MODERN_GEOREFERENCE_CONTEXT_NOT_HISTORICAL_PHOTO_DATUM"),
        ("CGEO15-IBGE-1958-VOL-XX", "CGEO-03", "CONTEMPORANEOUS_SOURCE_CANDIDATE_NOT_YET_PAGE_INSPECTED"),
    ]
    if (edges != expected_edges
            or graph.get("historical_independent_observations_confirmed") != 0
            or graph.get("modern_photographic_sessions_confirmed") != 1
            or graph.get("can_constrain_1963_reentry") is not False):
        raise ValueError("invalid graph independence or temporal veto")
    export = data["castor_contract"]
    for k in ("temporal_bridge_2022_to_1963", "event_location", "event_buffer_m",
              "historical_center_geometries", "position_accuracy_m"):
        if k not in export or export[k] is not None:
            raise ValueError("Castor contract contains fabricated constraint: " + k)
    if export.get("orbital_constraint_activated") is not False:
        raise ValueError("unsupported orbital promotion")
    return data


def verify_bytes(data: dict, path: Path) -> None:
    """Require acquired original files. No network request or fabricated fixture."""
    for row in data["captured_images"]:
        target = path / Path(row["original_file"]).name
        contents = target.read_bytes()
        if len(contents) != row["bytes"] or hashlib.sha256(contents).hexdigest() != row["sha256"]:
            raise ValueError("bytes/hash mismatch: " + str(target))
    if (path / "ibge-enciclopedia-vol20-1958.pdf").exists():
        raw = (path / "ibge-enciclopedia-vol20-1958.pdf").read_bytes()
        archive = data["archived_candidate"]
        if len(raw) != archive["acquired_bytes"] or hashlib.sha256(raw).hexdigest() != archive["acquired_sha256"]:
            raise ValueError("IBGE archive hash mismatch")


def evaluate(data: dict) -> dict:
    validate(data)
    return {
        "catalogue_id": "CGEO-15",
        "modern_viewpoint_coordinates_only": [
            [x["camera_point_from_commons"]["longitude"],
             x["camera_point_from_commons"]["latitude"]]
            for x in data["captured_images"]
        ],
        "coordinate_reference_system": None,
        "historical_center_geometry": None,
        "1963_observed_event_location": None,
        "can_constrain_orbital_reentry": False,
        "status": "MODERN_IMAGE_POINTS_ONLY_ARCHIVAL_BRIDGE_PENDING"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=CATALOGUE)
    parser.add_argument("--verify-dir", type=Path)
    args = parser.parse_args()
    data = validate(json.loads(args.catalogue.read_text(encoding="utf-8")))
    if args.verify_dir:
        verify_bytes(data, args.verify_dir)
    print(json.dumps(evaluate(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
