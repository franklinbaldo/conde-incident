"""Real source-pinned archive coverage; no invented stations or physics."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'tools/audit_igra_neighbors_1963.py'
SPEC = importlib.util.spec_from_file_location('igra_neighbors_1963', SRC)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
CARD = ROOT / 'research/meteorology/igra_nearby_1963_source_refresh.json'


class NeighborArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = json.loads(CARD.read_text())

    def test_pinned_manifest_and_original_recife_excerpts(self):
        MOD.validate_card(self.card)
        self.assertEqual([s['sounding_headers_1963'] for s in self.card['stations']], [0, 346, 0])
        self.assertEqual([s['total_sounding_headers'] for s in self.card['stations']], [20448, 14977, 7954])
        self.assertTrue(self.card['recife_current_zip_sha_differs_from_older_pin'])
        self.assertTrue(self.card['recife_1963_nov_07_09_original_byte_excerpts_unchanged'])

    def test_wrong_station_or_year_cannot_be_silently_accepted(self):
        good = b'#BRM00082599 1967 01 18 12 9999   16 ncdc6324           -59167  -352500\n'
        self.assertEqual(MOD.header_date(good, 'BRM00082599'), '1967-01-18')
        for row in (good.replace(b'82599', b'82900'), good.replace(b'1967', b'1963').replace(b'01 18', b'19 18')):
            with self.assertRaises(ValueError):
                MOD.header_date(row, 'BRM00082599')

    def test_false_coverage_and_false_physical_constraint_rejected(self):
        for section, value in (
            (('stations', 0, 'sounding_headers_1963'), 1),
            (('stations', 2, 'first_after_1963'), '1963-11-08'),
            (('conclusions', 'recife_to_conde_transfer_error_m_s'), 0),
            (('conclusions', 'geographic_or_orbital_constraint_activated'), True),
            (('conclusions', 'no_historical_launch_in_those_cities_in_1963'), False),
            (('recife_1963_nov_07_09_original_byte_excerpts_unchanged',), False),
            (('stations', 1, 'nov_1963_excerpt_matches_previous_sha'), {}),
        ):
            altered = deepcopy(self.card)
            target = altered
            for key in section[:-1]:
                target = target[key]
            target[section[-1]] = value
            with self.subTest(section=section), self.assertRaises(ValueError):
                MOD.validate_card(altered)

    def test_wrong_original_excerpt_rejected(self):
        for d, sha in MOD.OLD_EXCERPTS.items():
            self.assertEqual(MOD.digest(MOD.local_excerpt(d)), sha)


if __name__ == '__main__':
    unittest.main()
