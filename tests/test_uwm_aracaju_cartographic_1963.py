"""Archive audit: UWM Aracaju-SE facsimile is not a verified 1963 legal polygon."""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/uwm_aracaju_se_1954_1961_cartographic_custody.json"


def validate(document: dict) -> None:
    item = document["object"]
    text = document["facsimile_reading"]
    epistemic = document["epistemic_and_model_links"]
    images = document["binary_snapshots"]

    if document["schema"] != "conde.historical-cartographic-iiif-custody/v1":
        raise ValueError("unexpected schema")
    if document["occurrence_id"] != "ARCH-UWM-ARACAJU-SE-10814-20261112":
        raise ValueError("unexpected source identifier")
    if item["contentdm_item_id"] != "10814" or item["original_filename_from_api"] != "10806.jp2":
        raise ValueError("catalogue object identity changed")
    if item["scale_denominator"] != 500000 or item["listed_publication_year"] != "1954":
        raise ValueError("historic map metadata changed")
    if "1954" not in text["footnote_1_transcription"] or "1961" not in text["footnote_2_transcription"]:
        raise ValueError("facsimile imprint dates altered")
    if item["original_jp2_downloaded"] or item["original_jp2_sha256"] is not None:
        raise ValueError("unverified JP2 must remain explicitly unknown")
    if item["numeric_georeferencing_performed"] or item["spatial_reference_system"] is not None or item["datum"] is not None:
        raise ValueError("unjustified georeferencing")
    for key in ("map_1963_available_at_event", "administrative_boundary_1963", "legal_confrontations_1963",
                "historical_polygon_1963", "coordinates_of_alleged_fall"):
        if epistemic[key] is not None:
            raise ValueError("unsupported historical boundary or coordinate: " + key)
    if epistemic["historical_reentry_inside_conde_evaluable"] or epistemic["orbital_and_physical_constraint"] != "NOT_ACTIVATED":
        raise ValueError("unsupported physical constraint")
    if epistemic["constraint_status"] != "CONNECTED_PENDING_CALIBRATION":
        raise ValueError("invalid pending status")
    if len(images) != 6 or len({x["role"] for x in images}) != 6:
        raise ValueError("missing or duplicated IIIF snapshot")
    probe = document["original_binary_probe"]
    if probe["url"] != document["public_access"]["download_uri_from_custodian_api"]:
        raise ValueError("original JP2 URL mismatch")
    if not probe["url"].endswith("/api/collection/agdm/id/10814/download"):
        raise ValueError("unsupported JP2 download URI")
    if probe["head_status"] != 200 or probe["get_status"] != 200:
        raise ValueError("unverified original JP2 HTTP status")
    if probe["head_content_type"] != "image/jp2" or probe["get_content_type"] != "image/jp2":
        raise ValueError("unexpected original JP2 MIME")
    if probe["bytes_of_body_read"] != 32 or not probe["body_prefix_hex"].startswith("0000000c6a5020200d0a870a"):
        raise ValueError("missing original JP2 signature")
    if probe["get_content_range"] is not None or probe["range_support_observed"]:
        raise ValueError("unsupported HTTP range claim")
    if not probe["partial_response_only"] or probe["full_body_sha256"] is not None or probe["full_body_byte_count"] is not None:
        raise ValueError("unjustified full original custody")
    if probe["whole_file_transfer_attempt"] != "TIMEOUT_200S":
        raise ValueError("whole transfer result not tracked")
    for x in images:
        if x["http_status"] != 200 or x["bytes"] < 100:
            raise ValueError("unverified HTTP snapshot")
        if re.fullmatch(r"[0-9a-f]{64}", x["sha256"]) is None:
            raise ValueError("invalid SHA-256 syntax")
        if "collections.lib.uwm.edu" not in x["url"]:
            raise ValueError("non-custodian source")


class UWMCartographicCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_structurally_guarded(self) -> None:
        validate(self.record)

    def test_sheet_pre_1963_components_and_later_road_update_are_separate(self) -> None:
        self.assertEqual(self.record["object"]["title_catalog_short"], "Aracaju - SE, Brazil 1954")
        self.assertIn("Dezembro de 1954", self.record["facsimile_reading"]["footnote_1_transcription"])
        self.assertIn("1961", self.record["facsimile_reading"]["footnote_2_transcription"])
        self.assertEqual(self.record["facsimile_reading"]["locality_visible"], "CONDE")
        self.assertIsNone(self.record["object"]["original_map_print_date_verified"])

    def test_preview_and_crops_are_derivatives_not_original_jp2(self) -> None:
        self.assertEqual(self.record["object"]["original_mime_from_api"], "image/jp2")
        self.assertTrue(all(x["content_type"] == "image/jpeg"
                            for x in self.record["binary_snapshots"] if x["role"].startswith("derived_")))
        self.assertEqual(self.record["object"]["iiif_width_px"], 9603)
        self.assertEqual(self.record["object"]["iiif_height_px"], 7783)

    def test_original_jp2_prefix_is_not_whole_file_fixity(self) -> None:
        probe = self.record["original_binary_probe"]
        self.assertEqual(probe["get_status"], 200)
        self.assertEqual(probe["range_header_requested"], "bytes=0-31")
        self.assertFalse(probe["range_support_observed"])
        self.assertTrue(probe["jp2_magic_header_confirmed"])
        self.assertIsNone(probe["full_body_sha256"])

    def test_no_retroprojection_to_1963_municipal_limits(self) -> None:
        e = self.record["epistemic_and_model_links"]
        self.assertFalse(e["historical_reentry_inside_conde_evaluable"])
        self.assertIsNone(e["historical_polygon_1963"])
        self.assertIsNone(e["legal_confrontations_1963"])
        self.assertGreaterEqual(len(e["missing_bridges"]), 4)

    def test_fabricated_polygon_and_false_jp2_hash_rejected(self) -> None:
        import copy
        fake = copy.deepcopy(self.record)
        fake["epistemic_and_model_links"]["historical_polygon_1963"] = [[-37.6, -11.8]]
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate(fake)
        fake = copy.deepcopy(self.record)
        fake["original_binary_probe"]["full_body_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "unjustified full original custody"):
            validate(fake)
        fake = copy.deepcopy(self.record)
        fake["object"]["original_jp2_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "unverified"):
            validate(fake)


if __name__ == "__main__":
    unittest.main()
