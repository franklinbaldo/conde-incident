"""Regression and mutation tests for CGEO-32 source and inference limits."""
import copy
import unittest
from tools.cgeo32_dnocs213_crosswalk import check, load, DNOCS, PETROBRAS, USAF


class DnocsCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.d, self.p, self.u = load(DNOCS), load(PETROBRAS), load(USAF)

    def test_real_catalogue_crosswalk_without_claimed_facsimile(self):
        self.assertIn("CONTRACT_ONLY_PASS", check(self.d, self.p, self.u))
        self.assertNotEqual(self.d["new_locator"]["aerial_photo_nominal_scale_denominator"],
                            self.p["catalogue_occurrence"]["observed_entry"]["aerial_photo_nominal_scale_denominator"])

    def test_rejects_false_source_authentication(self):
        for key, v in (("original_catalogue_pdf_acquired", True), ("printed_page_verified", True),
                       ("original_pdf_sha256", "unknown"), ("independent_catalogue_witnesses", 2)):
            d = copy.deepcopy(self.d)
            d["catalogue_family"][key] = v
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)

    def test_rejects_invented_frame_dates_and_footprints(self):
        for key in ("individual_flight_date", "strip_id", "frame_id", "frame_footprint", "center_of_conde_covered"):
            d = copy.deepcopy(self.d)
            d["new_locator"][key] = "1961-01-01"
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)

    def test_rejects_false_custody_and_independence(self):
        for key in ("original_photoindex_acquired", "original_frame_acquired", "modern_holding_verified"):
            d = copy.deepcopy(self.d)
            d["new_locator"][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)
        d = copy.deepcopy(self.d)
        d["cross_project_comparison"]["independent_aerial_acquisitions_verified"] = 3
        with self.assertRaises(ValueError):
            check(d, self.p, self.u)

    def test_same_mi_does_not_prove_same_flight(self):
        for key in ("dnocs_same_flight_as_pet53d", "dnocs_same_flight_as_usaf632"):
            d = copy.deepcopy(self.d)
            d["cross_project_comparison"][key] = False
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)

    def test_prevent_catalogue_year_becoming_exposure_date(self):
        for key in ("usaf_63_32_is_exposure_date", "nominal_year_dates_every_frame", "full_sheet_coverage_verified"):
            d = copy.deepcopy(self.d)
            d["cross_project_comparison"][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)

    def test_rejects_misindexed_sheet_and_homonym(self):
        for key, v in (("sheet_mi", 38), ("sheet_cim", "SC-24-Z-D-VI"),
                       ("photo_index_nominal_scale_denominator", 100000)):
            d = copy.deepcopy(self.d)
            d["new_locator"][key] = v
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)
        d = copy.deepcopy(self.d)
        d["municipality"]["state"] = "PB"
        with self.assertRaises(ValueError):
            check(d, self.p, self.u)

    def test_rejects_claimed_event_geometry(self):
        for key in ("historical_center_point", "historical_center_polygon", "fall_location"):
            d = copy.deepcopy(self.d)
            d["scientific_link"][key] = [-37.6, -11.8]
            with self.subTest(key=key), self.assertRaises(ValueError):
                check(d, self.p, self.u)
        d = copy.deepcopy(self.d)
        d["scientific_link"]["can_constrain_orbital_reentry"] = True
        with self.assertRaises(ValueError):
            check(d, self.p, self.u)

    def test_must_retain_graph_connections_and_requirements(self):
        d = copy.deepcopy(self.d)
        d["graph_edges"] = d["graph_edges"][:-1]
        with self.assertRaises(ValueError):
            check(d, self.p, self.u)
        d = copy.deepcopy(self.d)
        d["scientific_link"]["activation_requirements"].remove("frame_footprint")
        with self.assertRaises(ValueError):
            check(d, self.p, self.u)


if __name__ == "__main__":
    unittest.main()
