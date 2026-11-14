"""Adversarial CGEO-51 institutional access constraints."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cgeo51", ROOT / "tools/cgeo51_nara_copy_access.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class NaraCopyTests(unittest.TestCase):
    def setUp(self):
        self.d = m.read(m.DATA)
        self.parent = m.read(m.PARENT)

    def reject(self, fn):
        d = copy.deepcopy(self.d)
        fn(d)
        with self.assertRaises(ValueError):
            m.validate(d, self.parent)

    def test_valid(self): self.assertEqual(m.validate(self.d, self.parent), 3)
    def test_spot_fake(self): self.reject(lambda d: d["nara"].update(spot_number="125374"))
    def test_can_fake(self): self.reject(lambda d: d["nara"].update(can_number="ON12345"))
    def test_other_overlay(self): self.reject(lambda d: d["nara"].update(overlay="m1765-317-00249.jpg"))
    def test_op_wrong(self): self.reject(lambda d: d["nara"].update(op_file_number="133002"))
    def test_invent_remote_scan(self): self.reject(lambda d: d["access_policy"].update(remote_film_copy_offered=True))
    def test_false_public_locator(self): self.reject(lambda d: d["access_policy"].update(locator_is_open_online=True))
    def test_false_external_contact(self): self.reject(lambda d: d["actions"].update(contact_sent=True))
    def test_false_scan(self): self.reject(lambda d: d["actions"].update(negatives_acquired=True))
    def test_fake_copy_on_site(self): self.reject(lambda d: d["access_policy"].update(onsite_camera_or_scanner_possible=False))
    def test_invalid_source(self): self.reject(lambda d: d["sources"][1].update(url="https://example.com"))
    def test_fake_photo(self): self.reject(lambda d: d["limitations"].update(authentic_photo_of_urban_conde=True))
    def test_fake_exposure_date(self): self.reject(lambda d: d["limitations"].update(photo_exposure_date="1942-09-20"))
    def test_fake_center(self): self.reject(lambda d: d["limitations"].update(historical_city_center_1963=[1,2]))
    def test_fake_orbit(self): self.reject(lambda d: d["limitations"].update(orbital_constraint_activated=True))

if __name__ == "__main__":
    unittest.main()
