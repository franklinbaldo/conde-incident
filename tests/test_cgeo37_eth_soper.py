"""Adversarial CGEO-37 tests: custodianship, chronology, and refusal of geo-promotion."""
import copy
import tempfile
import unittest
from pathlib import Path
from tools.cgeo37_eth_soper import load_contract, validate_contract, verify_file, EXPECTED_SHA


class Cgeo37Tests(unittest.TestCase):
    def setUp(self):
        self.doc = load_contract()

    def altered(self, modify):
        other = copy.deepcopy(self.doc)
        modify(other)
        with self.assertRaises(ValueError):
            validate_contract(other)

    def test_reference_contract(self):
        self.assertEqual(validate_contract(self.doc), "CGEO37_CONTRACT_PASS")

    def test_printed_and_online_dates_differ(self):
        self.altered(lambda d: d["historical_work"].update(printed_year=1963))
        self.altered(lambda d: d["eth_custody"].update(online_since="1914-07-01"))

    def test_new_holder_not_new_survey(self):
        self.altered(lambda d: d["comparison"].update(independent_survey_or_1963_observation=True))
        self.altered(lambda d: d["comparison"].update(same_physical_copy_demonstrated=True))
        self.altered(lambda d: d["comparison"].update(pixel_identity_demonstrated=True))

    def test_explicit_lineage_and_source_not_silenced(self):
        self.altered(lambda d: d["historical_work"].update(reported_cartographic_source="Soper alone"))
        self.altered(lambda d: d["observations"].update(topography_has_explicit_multiple_sources=False))

    def test_no_1963_center_or_reentry_location(self):
        self.altered(lambda d: d["limits"].update(historical_city_center_polygon_1963=[-37, -12]))
        self.altered(lambda d: d["limits"].update(reported_impact_coordinates=[-37, -12]))
        self.altered(lambda d: d["limits"].update(can_constrain_orbital_reentry=True))

    def test_pixels_are_not_terrestrial_positions(self):
        self.altered(lambda d: d["observations"].update(geographic_coords_for_toponyms_from_this_work=[-37, -12]))
        self.altered(lambda d: d["observations"].update(iiif_canvas_px_are_not_geographic_coords=False))

    def test_custody_cannot_silently_change(self):
        self.altered(lambda d: d["eth_custody"].update(pdf_sha256="0" * 64))
        self.altered(lambda d: d["eth_custody"].update(iiif_manifest_bytes=1))

    def test_absent_binary_is_not_replayed(self):
        with self.assertRaises(FileNotFoundError):
            verify_file(Path("/missing/eth_soper.pdf"), 2020098, EXPECTED_SHA["pdf"], "pdf")

    def test_fake_binary_is_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            fake = Path(path) / "fake.pdf"
            fake.write_bytes(b"%PDF-1.4 fake")
            with self.assertRaises(ValueError):
                verify_file(fake, 2020098, EXPECTED_SHA["pdf"], "pdf")


if __name__ == "__main__":
    unittest.main()
