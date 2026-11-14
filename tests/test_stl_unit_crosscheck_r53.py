"""R53 adversarial ledger checks, valid with both normal Python and -O."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("unit_r53", ROOT / "tools/audit_stl_unit_crosscheck_r53.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class R53(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(mod.SOURCE.read_text(encoding="utf-8"))

    def invalid(self, path, new):
        data = copy.deepcopy(self.data)
        node = data
        for segment in path[:-1]:
            node = node[segment]
        node[path[-1]] = new
        with self.assertRaises(ValueError):
            mod.audit(data)

    def test_valid_five_row_crosscheck(self):
        results = mod.audit(self.data)
        self.assertEqual(len(results), 5)
        for row in results:
            self.assertLess(row["miles_residual_minutes"], row["km_residual_minutes"])

    def test_syncom_independent_scale_control(self):
        row = mod.audit(self.data)[3]
        self.assertGreater(row["km_residual_minutes"], 600)
        self.assertLess(row["miles_residual_minutes"], 0.5)

    def test_cosmos_low_orbit_control(self):
        row = mod.audit(self.data)[2]
        self.assertGreater(row["km_residual_minutes"], 2)
        self.assertLess(row["miles_residual_minutes"], 0.1)

    def test_original_not_retrieved(self):
        self.invalid(["source", "upstream_original_retrieved"], True)

    def test_not_certified_in_original(self):
        self.invalid(["conclusion", "unit_in_original_STL_issue_certified"], True)

    def test_not_certified_on_page(self):
        self.invalid(["conclusion", "unit_printed_on_B12_directly_certified"], True)

    def test_not_independent_from_nasa_R51(self):
        self.invalid(["conclusion", "independent_from_R51"], True)

    def test_not_new_sensor(self):
        self.invalid(["conclusion", "new_instrumental_sensors"], 1)

    def test_not_new_527_529_control(self):
        self.invalid(["conclusion", "new_observations_527_528_529_november"], 1)

    def test_not_new_orbital_constraint(self):
        self.invalid(["conclusion", "new_orbital_constraints_activated"], 1)

    def test_sha_mutation(self):
        self.invalid(["source", "pdf_sha256"], "0" * 64)

    def test_page_mutation(self):
        self.invalid(["source", "pdf_page_one_based"], 104)

    def test_high_orbit_transcription_mutation(self):
        self.invalid(["rows", 3, 4], 22975)

    def test_low_orbit_transcription_mutation(self):
        self.invalid(["rows", 2, 3], 128)

    def test_mile_scale_mutation(self):
        self.invalid(["physics", "statute_mile_km"], 1.0)


if __name__ == "__main__":
    unittest.main()
