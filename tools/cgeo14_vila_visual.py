"""Validate CGEO-14 undated Vila do Conde photos and optionally replay original JPEG hashes."""
from __future__ import annotations

import argparse
from datetime import date, datetime
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).resolve().parents[1] / "research/geo/cgeo14_vila_conde_visual_catalogue.json"
BASE = "https://condebahia.wordpress.com/wp-content/uploads/2014/03/"
EXPECTED = (
    ("CGEO14-IMAGE-01", "vila-velha-001.jpg", "vila velha 001", "233264fed3b4475e6ea3aae5efea521f56fe9a1fc8ee6d9c0c602787653ef154", 321338, 1600, 1163),
    ("CGEO14-IMAGE-02", "villa-velha-2-001.jpg", "villa velha 2 001", "3f8a427524b6b4b6abfedf0473d054891608ac2e1e4a2905fec881caabd992a0", 17877, 320, 233),
    ("CGEO14-IMAGE-03", "villa-velha-3-001.jpg", "villa velha 3 001", "468fd60bf0805e1b1dedc8be6e1a4fc9181b74225bc57650c454e31e2c6d46c3", 27755, 320, 233),
)


def validate(data: dict) -> dict:
    if (data.get("schema") != "conde.gis.vila-conde-visual-custody/v1"
            or data.get("id") != "CGEO-14" or data.get("event_date") != "1963-11-08"):
        raise ValueError("catalogue identity or event date changed")
    src = data.get("source_page", {})
    if (src.get("url") != "https://condebahia.wordpress.com/historia/"
            or src.get("published_at") != "2014-03-13T04:39:48+00:00"
            or src.get("html_acquired_sha256") != "3b3b55beb6db73a3d8db18e5fdc4e5c6ba48fd88907601df98951e9854fc54ca"
            or src.get("rights_or_reuse_license", "ABSENT") is not None
            or src.get("archival_provenance_of_original_photos", "ABSENT") is not None
            or src.get("rehost_permitted") is not False):
        raise ValueError("source provenance or permissions promoted")
    if datetime.fromisoformat(src["published_at"]).date() <= date.fromisoformat(data["event_date"]):
        raise ValueError("2014 publication incorrectly promoted to 1963")
    images = data.get("images")
    if not isinstance(images, list) or len(images) != len(EXPECTED):
        raise ValueError("image count changed")
    for row, (identifier, filename, title, sha, size, width, height) in zip(images, EXPECTED):
        if (row.get("id") != identifier or row.get("url") != BASE + filename
                or row.get("embedded_image_title") != title
                or row.get("sha256") != sha or row.get("byte_size") != size
                or row.get("pixel_width") != width or row.get("pixel_height") != height
                or row.get("file_type") != "JPEG"):
            raise ValueError("image identification or acquired-byte integrity changed")
        for field in ("capture_date", "photographer", "latitude", "longitude", "datum",
                      "horizontal_uncertainty_m", "camera_pose"):
            if field not in row or row[field] is not None:
                raise ValueError("unverified capture/georeference promoted: " + field)
        if row.get("independently_geolocated") is not False or row.get("documented_1963_scene") is not False:
            raise ValueError("image falsely assigned geographic or 1963 provenance")
    place = data.get("place_context", {})
    if (place.get("blog_place_label") != "Vila do Conde"
            or place.get("municipality_ibge_code") != "2908606"
            or place.get("municipal_seat_historical_document") != "CGEO-03"
            or place.get("center_of_city_1963_text_original_verified") is not False):
        raise ValueError("place context promoted")
    for field in ("center_equals_Vila_do_Conde_in_1963", "center_equals_Sitio_do_Conde_in_1963",
                  "historical_center_polygon", "historical_center_point", "temporal_georeferencing_bridge"):
        if field not in place or place[field] is not None:
            raise ValueError("historical center position promoted: " + field)
    graph = data.get("dependency_graph", {})
    if (graph.get("independent_historical_captures_confirmed") != 0
            or graph.get("can_constrain_1963_reentry") is not False):
        raise ValueError("unsupported independent historical evidence or physical restriction")
    for field in ("observed_reentry_point", "point_of_view_1963"):
        if field not in graph or graph[field] is not None:
            raise ValueError("unverified event location promoted")
    expected_links = ([(identifier, "CGEO14-BLOG-HISTORIA-2014", "PUBLISHED_IN_SAME_GALLERY")
                       for identifier, *_ in EXPECTED] + [
        ("CGEO14-BLOG-HISTORIA-2014", "CGEO-03", "TOPONYM_CONTEXT_ONLY_NOT_SPATIAL_VERIFICATION"),
        ("CGEO14-BLOG-HISTORIA-2014", "CGEO-13", "FUTURE_COMPARISON_REQUIRES_AUTHENTIC_MAP_SCAN_AND_CONTROL_POINTS")])
    links = [(x.get("from"), x.get("to"), x.get("relation")) for x in graph.get("links", [])]
    if links != expected_links:
        raise ValueError("dependency graph broken")
    return data


def verify_files(data: dict, directory: Path) -> None:
    """Offline hash replay; never substitute fabricated thumbnails for archived photos."""
    for row in data["images"]:
        path = directory / row["url"].rsplit("/", 1)[1]
        blob = path.read_bytes()
        if len(blob) != row["byte_size"] or hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise ValueError("byte/hash mismatch for " + str(path))
        if not blob.startswith(b"\xff\xd8\xff") or not blob.endswith(b"\xff\xd9"):
            raise ValueError("not a complete JPEG: " + str(path))


def evaluate(data: dict) -> dict:
    validate(data)
    return {
        "catalogue_id": "CGEO-14",
        "published_photo_records": [r["id"] for r in data["images"]],
        "source_publication_date": "2014-03-13",
        "capture_dates": [None] * len(EXPECTED),
        "historical_center_geometry": None,
        "center_of_city_1963_verified": False,
        "point_of_reentry": None,
        "can_constrain_orbital_reentry": False,
        "status": "SOURCES_ACQUIRED_CAPTURE_DATES_AND_GEOREFERENCE_UNKNOWN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=CATALOGUE)
    parser.add_argument("--verify-dir", type=Path, default=None)
    args = parser.parse_args()
    data = validate(json.loads(args.catalogue.read_text(encoding="utf-8")))
    if args.verify_dir is not None:
        verify_files(data, args.verify_dir)
    print(json.dumps(evaluate(data), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
