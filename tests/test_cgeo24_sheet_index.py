import copy
import tempfile
import unittest
from pathlib import Path
from tools.cgeo24_sheet_index import load, sheet_for, validate, verify_pdf

class TopographicIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load()
        cls.grid = cls.data["nominal_graticule"]["sheets"]

    def test_contract(self):
        validate(self.data)

    def test_2022_cameras_inside_esplanada(self):
        for pt in self.data["camera_observations"]:
            self.assertEqual(sheet_for(pt["lon"], pt["lat"], self.grid), 1850)

    def test_south_is_porto_sauipe(self):
        self.assertEqual(sheet_for(-37.75, -12.25, self.grid), 1906)

    def test_east_is_riacho_tabatinga(self):
        self.assertEqual(sheet_for(-37.25, -11.75, self.grid), 1851)

    def test_exact_edges_remain_ambiguous(self):
        self.assertEqual(sheet_for(-37.75, -12, self.grid), "BOUNDARY_UNRESOLVED")
        self.assertEqual(sheet_for(-37.5, -11.75, self.grid), "BOUNDARY_UNRESOLVED")

    def test_outside_and_invalid(self):
        self.assertIsNone(sheet_for(-36.5, -11.75, self.grid))
        with self.assertRaises(ValueError):
            sheet_for(190, -11.75, self.grid)

    def test_1963_center_and_fall_not_inferred(self):
        bad = copy.deepcopy(self.data)
        bad["historical"]["fall_location_1963"] = [-37.62, -11.8]
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_inventory_is_not_map_date(self):
        bad = copy.deepcopy(self.data)
        bad["sources"]["sudene"]["edition_year_of_underlying_map"] = 1963
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_forged_pdf_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fake.pdf"
            path.write_bytes(b"%PDF-fake")
            self.assertFalse(verify_pdf(self.data["sources"]["ibge"], path))

    def test_conde_pb_not_bahia(self):
        self.assertFalse(self.data["false_friends"][0]["is_conde_bahia"])

if __name__ == "__main__":
    unittest.main()
