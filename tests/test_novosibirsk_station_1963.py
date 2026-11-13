import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/verify_novosibirsk_station_1963.py"
spec = importlib.util.spec_from_file_location("station_c241_l31", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class StationLocatorTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(mod.MANIFEST.read_text(encoding="utf-8"))

    def test_manifest(self):
        self.assertTrue(mod.validate(self.data))

    def test_no_promotion_of_observations(self):
        for key, bad in [
            ("primary_observations_for_targets_retrieved", 1),
            ("orbital_constraint_activated", True),
            ("historical_1963_observing_epoch_verified", True),
            ("station_position_or_site_code_promoted_to_orbit", True),
        ]:
            with self.subTest(key=key), self.assertRaises(AssertionError):
                d = copy.deepcopy(self.data)
                d[key] = bad
                mod.validate(d)

    def test_site_code_not_assigned_to_november(self):
        d = copy.deepcopy(self.data)
        d["station"]["specific_site_on_1963_11_08"] = 1090
        with self.assertRaises(AssertionError):
            mod.validate(d)

    def test_later_camera_not_moved_to_1963(self):
        d = copy.deepcopy(self.data)
        d["station"]["later_camera"]["delivered_year"] = 1963
        with self.assertRaises(AssertionError):
            mod.validate(d)

    def test_17_years_not_counted_as_1963(self):
        d = copy.deepcopy(self.data)
        d["station"]["aggregate_measurements_reported"]["measurements_in_1963_only"] = 100000
        with self.assertRaises(AssertionError):
            mod.validate(d)

    def test_html_replay_rejects_tampering(self):
        fake = b"x" * self.data["source"]["bytes"]
        with self.assertRaises(AssertionError):
            mod.validate(self.data, fake)


if __name__ == "__main__":
    unittest.main()
