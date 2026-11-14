"""Adversarial mutations of the real, 14-image NARA custody manifest."""
import copy
import importlib.util
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'tools/cgeo47_nara_m1765.py'
spec = importlib.util.spec_from_file_location('cgeo47',P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NaraM1765Test(unittest.TestCase):
    def setUp(self):
        self.data = m.load_manifest()

    def rejects(self,change):
        data = copy.deepcopy(self.data)
        change(data)
        with self.assertRaises(ValueError):
            m.validate(data)

    def test_real_manifest(self):
        self.assertEqual(m.validate(self.data),14)

    def test_bad_schema(self):
        self.rejects(lambda d: d.update(schema='legacy'))

    def test_false_sgb_equivalence(self):
        self.rejects(lambda d: d['lineage'].update(same_flight_as_sgb=True))

    def test_missing_square(self):
        self.rejects(lambda d: d['units'].pop())

    def test_duplicate_square(self):
        self.rejects(lambda d: d['units'][1].update(degree_square='11S037W'))

    def test_bad_record_id(self):
        self.rejects(lambda d: d['units'][0].update(nara_id='46716645'))

    def test_wrong_period(self):
        self.rejects(lambda d: d['units'][0].update(cover_period_printed='1963'))

    def test_bad_source_url(self):
        self.rejects(lambda d: d['units'][0]['images'][0].update(url='https://example.com/fake.jpg'))

    def test_wrong_jpeg_bytes(self):
        self.rejects(lambda d: d['units'][0]['images'][0].update(bytes=1))

    def test_invalid_sha(self):
        self.rejects(lambda d: d['units'][0]['images'][0].update(sha256='pending'))

    def test_reused_object(self):
        self.rejects(lambda d: d['units'][1]['images'][0].update(object_id=d['units'][0]['images'][0]['object_id']))

    def test_missing_image(self):
        self.rejects(lambda d: d['units'][0]['images'].pop())

    def test_no_negatives_as_jpegs(self):
        self.rejects(lambda d: d['limitations'].update(individual_original_negatives_acquired=True))

    def test_no_fake_town_photo(self):
        self.rejects(lambda d: d['limitations'].update(photograph_of_conde_town_acquired=True))

    def test_no_false_georef(self):
        self.rejects(lambda d: d['limitations'].update(georeferenced_footprints_validated=True))

    def test_no_fictitious_center(self):
        self.rejects(lambda d: d['limitations'].update(town_center_geometry_1963=[-37.6,-11.8]))

    def test_no_orbit_effect(self):
        self.rejects(lambda d: d['limitations'].update(orbital_constraints_activated=True))

    def test_wrong_role(self):
        self.rejects(lambda d: d['units'][0]['images'][1].update(role='air_photo'))


if __name__ == '__main__':
    unittest.main()
