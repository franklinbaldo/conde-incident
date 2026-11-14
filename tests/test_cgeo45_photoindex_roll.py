"""Fail closed for invented dates, frame counts, positions, and source identity."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo45", ROOT / "tools/cgeo45_photoindex_roll.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class RollReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(mod.MANIFEST.read_text())
        cls.p = json.loads(mod.PARENT.read_text())

    def mutate(self, section, key, value):
        d = copy.deepcopy(self.m)
        d[section][key] = value
        with self.assertRaises(ValueError):
            mod.validate(d, self.p)

    def test_positive(self):
        self.assertEqual(mod.validate(self.m, self.p), "CGEO45_CONTRACT_PASS")

    def test_no_intermediate_frames(self):
        self.mutate("limitations", "intermediate_frames_verified", True)

    def test_no_original_frames(self):
        self.mutate("limitations", "original_frames_acquired", True)

    def test_no_date(self):
        self.mutate("limitations", "capture_dates", {"7150": "1963-11-08"})

    def test_no_flight_time(self):
        self.mutate("limitations", "flight_time", "1963-11-08")

    def test_no_datum(self):
        self.mutate("limitations", "datum", "EPSG:4326")

    def test_no_polygon(self):
        self.mutate("limitations", "georeferenced_footprint", [[-37.6, -11.8]])

    def test_no_city_center(self):
        self.mutate("limitations", "center_conde_1963", [-37.6, -11.8])

    def test_no_reentry(self):
        self.mutate("limitations", "reentry_point", [-37.6, -11.8])

    def test_no_orbit(self):
        self.mutate("limitations", "orbital_restriction", True)

    def test_wrong_roll(self):
        d = copy.deepcopy(self.m)
        d["inspection"]["upper"]["roll"] = "59"
        with self.assertRaises(ValueError):
            mod.validate(d, self.p)

    def test_wrong_frame(self):
        d = copy.deepcopy(self.m)
        d["inspection"]["lower"]["printed_frame"] = "7151"
        with self.assertRaises(ValueError):
            mod.validate(d, self.p)

    def test_wrong_crop(self):
        d = copy.deepcopy(self.m)
        d["inspection"]["upper"]["crop_pixels"] = [0, 0, 10, 10]
        with self.assertRaises(ValueError):
            mod.validate(d, self.p)

    def test_wrong_sgb_folder(self):
        d = copy.deepcopy(self.m)
        d["source"]["folder"] = "0335"
        with self.assertRaises(ValueError):
            mod.validate(d, self.p)

    def test_parent_drift(self):
        p = copy.deepcopy(self.p)
        p["acquisition"]["jpeg_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            mod.validate(self.m, p)

    def test_wrong_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bad.jpg"
            path.write_bytes(b"not a real JPEG")
            with self.assertRaises(ValueError):
                mod.verify_image(path, self.m)


if __name__ == "__main__":
    unittest.main()
