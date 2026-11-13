"""CGEO-19: verify attributed 1959 Conde photographs without inferred coordinates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo19_1959_editorial_photographs.json"
EXPECTED = {
    "vila_1959_claim": ("b0c17c9bae3a4397d1572b300b26967e703fe1c0bdb05c624819dd34c16abde3", 316900, 1959),
    "passarela_2012_claim": ("68f669f9e39896695f7d0deb677c81ae18ae93b941524f2bbde0cc76df1149c7", 215602, 2012),
    "alto_vila_1959_claim": ("01263381c8108b6a0e33f11861ac6cc7afe200d9f359d2077dd2d198e9f88a2f", 235387, 1959),
    "igreja_monte_1959_claim": ("071e3b27fa599beedb4f9e2e93bf597badee9c10b5acba120c4157f84fb441c6", 237049, 1959),
}
CAPTIONS = {
    "vila_1959_claim": "VILLA DO CONDE, CONDE-BAHIA - 1959",
    "passarela_2012_claim": "PÔR DO SOL DE CONDE-BA. FOTO TIRADA SOBRE A PASSARELA EM NOVEMBRO 2012",
    "alto_vila_1959_claim": "ALTO DA VILLA DO CONDE, CONDE-BAHIA - 1959",
    "igreja_monte_1959_claim": "IGREJA NOSSA SENHORA DO MONTE VILLA DO CONDE, CONDE-BAHIA - 1959",
}
SOURCE_HTML_SHA = "dbe5afead3991dfce8c5f1260a596979b46e897776e86b3eeedf295364aebf1f"


def validate(data: dict) -> None:
    if data["schema"] != "conde.gis.photo-editorial-date-claim/v1" or data["id"] != "CGEO-19":
        raise ValueError("incorrect contract")
    if data["municipality"]["ibge_code"] != "2908606" or data["municipality"]["uf"] != "BA":
        raise ValueError("incorrect Conde")
    source = data["source"]
    if (source["publication_timestamp"] != "2012-12-10T16:15:00-03:00"
            or source["html_bytes_retrieved"] != 103798
            or source["html_sha256_at_retrieval"] != SOURCE_HTML_SHA
            or not source["url"].startswith("https://geografiadetalhada.blogspot.com/")):
        raise ValueError("editorial source custody drift")
    for k in ("original_negative_archive_identified", "author_or_photographer_of_1959_images_verified",
              "license_for_redistribution_verified"):
        if source[k] is not False:
            raise ValueError("unverified author/negative/license promotion: " + k)
    photos = data["images"]
    if len(photos) != 4 or [p["order"] for p in photos] != [1, 2, 3, 4]:
        raise ValueError("images lost or reordered")
    if {p["id"] for p in photos} != set(EXPECTED):
        raise ValueError("image identities drifted")
    for photo in photos:
        ident = photo["id"]
        sha, size, year = EXPECTED[ident]
        if (photo["sha256"], photo["byte_size"], photo["published_capture_year_claim"]) != (sha, size, year):
            raise ValueError("bytes/year claim drift: " + ident)
        if photo["caption"] != CAPTIONS[ident] or not photo["source_url"].startswith(
                "https://blogger.googleusercontent.com/img/b/"):
            raise ValueError("unverified caption or photo locator: " + ident)
        if photo["source_capture_date_authenticated"] is not False:
            raise ValueError("editorial year promoted to authentic image capture date")
        if photo["source_photographer_authenticated"] is not False:
            raise ValueError("unknown photographer promoted")
        if photo["location_verified_to_building_or_street"] is not False:
            raise ValueError("a caption is not a georeference")
        for k in ("exif_capture_datetime", "exif_gps", "camera_coordinates", "geo_registration_points"):
            if photo[k] is not None:
                raise ValueError("unknown photo metadata filled: " + k)
    claims = data["editorial_claims"]
    if (claims["claimed_1959_images"] != 3
            or claims["claimed_november_2012_images"] != 1
            or claims["independent_publications_in_this_contract"] != 1):
        raise ValueError("source count or 2012 photo incorrectly counted")
    for k in ("capture_year_1959_proven", "photo_authenticity_and_location_1963_proven",
              "original_image_byte_equality", "transformation_or_pixel_identity_verified"):
        if claims[k] is not False:
            raise ValueError("unsupported historical or duplication inference: " + k)
    if claims["first_photo_possible_republication_in_2014"] != "POSSIBLE_SAME_BASENAME_ONLY_NOT_PROVEN_DUPLICATE":
        raise ValueError("2014 copy falsely authenticated")
    geo = data["geospatial_export"]
    if geo["can_constrain_orbital_reentry"] is not False or geo["epistemic_status"] != (
            "2012_EDITORIAL_CLAIM_OF_1959_IMAGERY_WITH_UNVERIFIED_CAPTURE_DATES"):
        raise ValueError("photo context promoted to orbital constraint")
    for k in ("historical_center_point", "historical_center_polygon", "matched_1958_ibge_square",
              "landmark_point_1963", "event_impact_location", "camera_positions_1959",
              "legal_boundary_1963", "crs", "horizontal_accuracy_m"):
        if geo[k] is not None:
            raise ValueError("unsupported geographic position or precision: " + k)
    expected_links = {
        ("CGEO-19", "CGEO-14"),
        ("CGEO-19", "CGEO-17"),
        ("CGEO-19", "CGEO-18"),
        ("CGEO-19", "LON-IBGE1958-CONDE-01"),
    }
    if not expected_links.issubset({(edge["from"], edge["to"]) for edge in data["dependencies"]}):
        raise ValueError("missing documentary lineage")


def verify_source_bytes(path: Path, expected_sha: str, expected_size: int) -> None:
    data = path.read_bytes()
    if len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError("original downloaded source bytes do not match manifest")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="optional original 2012 post HTML snapshot")
    parser.add_argument("--jpeg-dir", type=Path, help="optional directory with img1.jpg through img4.jpg")
    args = parser.parse_args()
    validate(json.loads(CONTRACT.read_text(encoding="utf-8")))
    if args.html:
        verify_source_bytes(args.html, SOURCE_HTML_SHA, 103798)
    if args.jpeg_dir:
        for order, (sha, size, _) in enumerate(EXPECTED.values(), start=1):
            verify_source_bytes(args.jpeg_dir / f"img{order}.jpg", sha, size)
    print("CGEO-19: PASS contract" + (" + actual supplied source bytes" if args.html or args.jpeg_dir else " (offline only)"))


if __name__ == "__main__":
    main()
