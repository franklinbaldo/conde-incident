"""R52 catalog-vs-facsimile gates: normal and optimized Python compatible."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_stl_locator_r52", BASE / "tools/audit_stl_space_log_locator_r52.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class R52Tests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(mod.SOURCE.read_text(encoding="utf-8"))

    def corrupt(self, path, value):
        data = copy.deepcopy(self.record)
        parent = data
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        with self.assertRaises(ValueError):
            mod.audit(data)

    def test_unmodified_record(self):
        self.assertEqual(mod.audit(self.record), "LOCATORS_ONLY_NO_ORIGINAL_NO_NEW_SENSOR")

    def test_original_not_read(self):
        self.corrupt(["target", "physical_original_retrieved"], True)

    def test_no_invented_original_hash(self):
        self.corrupt(["target", "original_pdf_sha256"], "fake")

    def test_google_books_volume_not_issue(self):
        self.corrupt(["sources", 1, "contains_issue_4"], True)

    def test_commercial_inventory_not_original(self):
        self.corrupt(["sources", 0, "facsimile_retrieved"], True)

    def test_429_is_not_absence(self):
        self.corrupt(["limitations", "commercial_index_http429_is_not_absence"], False)

    def test_nasa_not_new_sensor(self):
        self.corrupt(["sources", 2, "independent_instrumental_observation"], True)

    def test_no_1963_november_observation(self):
        self.corrupt(["limitations", "observations_527_528_529_1963_11_07_to_09"], 1)

    def test_no_orbital_constraint(self):
        self.corrupt(["limitations", "new_orbital_constraints_activated"], 1)

    def test_no_unverified_original_unit(self):
        self.corrupt(["target", "perigee_apogee_units_from_original"], "miles")

    def test_no_unverified_soviet_dependency(self):
        self.corrupt(["limitations", "direct_stl_to_soviet_1964_copying_demonstrated"], True)

if __name__ == "__main__":
    unittest.main()
