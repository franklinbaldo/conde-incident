"""CGEO-49 adversarial checks: a heading is not yet a film can."""
import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cgeo49_nara_headers", HERE / "tools/cgeo49_nara_headers.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class HeaderTests(unittest.TestCase):
    def setUp(self):
        self.d = module.load(module.DATA)
        self.parent = module.load(module.PARENT)

    def reject(self, modify):
        changed = copy.deepcopy(self.d)
        modify(changed)
        with self.assertRaises(ValueError):
            module.validate(changed, self.parent)

    def test_source_contract(self):
        self.assertEqual(module.validate(self.d, self.parent), 4)
    def test_wrong_unit(self):
        self.reject(lambda x: x.update(nara_unit="46716645"))
    def test_missing_sheet(self):
        self.reject(lambda x: x["sheets"].pop())
    def test_image_substitution(self):
        self.reject(lambda x: x["sheets"][1].update(sha256="0"*64))
    def test_swapped_number(self):
        self.reject(lambda x: x["sheets"][0].update(handwritten_number="125374"))
    def test_fake_spot(self):
        self.reject(lambda x: x["sheets"][1].update(verified_spot_number="125374"))
    def test_fake_can(self):
        self.reject(lambda x: x["sheets"][2].update(verified_negative_can="ON024198"))
    def test_date_promotion(self):
        self.reject(lambda x: x["sheets"][1].update(header_date_status="verified_exposure_date"))
    def test_heading_assumed_spot(self):
        self.reject(lambda x: x["cross_sheet_inferences"].update(number_125374_is_confirmed_spot=True))
    def test_repeat_pair_drift(self):
        self.reject(lambda x: x["cross_sheet_inferences"].update(number_repeated_on=["m1765-317-00249.jpg"]))
    def test_exposure_overclaim(self):
        self.reject(lambda x: x["cross_sheet_inferences"].update(images_of_conde_confirmed=True))
    def test_negative_overclaim(self):
        self.reject(lambda x: x["limitations"].update(original_aerial_negative_acquired=True))
    def test_1963_geometry(self):
        self.reject(lambda x: x["limitations"].update(historical_center_geometry_1963=[-37.6,-11.8]))
    def test_event_location(self):
        self.reject(lambda x: x["limitations"].update(reentry_location=[-37.6,-11.8]))
    def test_date_at_conde(self):
        self.reject(lambda x: x["limitations"].update(verified_aerial_exposure_date_at_conde="1942-09-20"))
    def test_orbit_claim(self):
        self.reject(lambda x: x["limitations"].update(orbital_constraints_activated=True))

if __name__ == "__main__":
    unittest.main()
