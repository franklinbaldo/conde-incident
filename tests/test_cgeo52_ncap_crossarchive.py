"""Adversarial checks: 403 and HTML shell never imply no historical frames."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo52",ROOT/"tools/cgeo52_ncap_crossarchive.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Cgeo52Tests(unittest.TestCase):
    def setUp(self):
        self.data = m.load(m.DATA)
        self.parent = m.load(m.PARENT)

    def reject(self, change):
        d = copy.deepcopy(self.data)
        change(d)
        with self.assertRaises(ValueError):
            m.validate(d,self.parent)

    def test_valid(self): self.assertEqual(m.validate(self.data,self.parent),3)
    def test_wrong_archive(self): self.reject(lambda d:d["nara"].update(file_unit="999"))
    def test_fake_spot(self): self.reject(lambda d:d["nara"].update(spot_number="125374"))
    def test_fake_negative(self): self.reject(lambda d:d["nara"].update(negative_can="ON001"))
    def test_fake_download(self): self.reject(lambda d:d["route"].update(public_negative_url="https://example.org/photo.jpg"))
    def test_false_direct_access(self): self.reject(lambda d:d["sources"][1].update(content_acquired=True))
    def test_false_200(self): self.reject(lambda d:d["sources"][1].update(http_status=200))
    def test_false_brazil_absence(self): self.reject(lambda d:d["sources"][1].update(absence_of_brazil_photographs_proven=True))
    def test_claim_zero_hits(self): self.reject(lambda d:d["sources"][2].update(zero_photograph_hits_proven=True))
    def test_html_as_json(self): self.reject(lambda d:d["sources"][2].update(body_format="JSON"))
    def test_fake_ncap_image(self): self.reject(lambda d:d["route"].update(individual_conde_film_digitized=True))
    def test_false_external_contact(self): self.reject(lambda d:d["route"].update(contact_sent=True))
    def test_false_city_geometry(self): self.reject(lambda d:d["limitations"].update(center_geometry_1963=[-37,-11]))
    def test_false_orbital_constraint(self): self.reject(lambda d:d["limitations"].update(orbital_constraints_activated=True))
    def test_false_independence(self): self.reject(lambda d:d["limitations"].update(source_families_independent_photographs=1))

if __name__ == "__main__":
    unittest.main()
