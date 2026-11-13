"""CGEO-25 independent regressions against temporal and document custody promotion."""
import copy
import unittest
from tools.cgeo25_esplanada_lineage import load, validate


class Cgeo25Tests(unittest.TestCase):
    def setUp(self):
        self.c = load()

    def test_custody_and_temporal_chain(self):
        validate(self.c)
        self.assertEqual(self.c['target_sheet']['sheet_publication_year'], 1973)

    def test_cannot_promote_1973_as_pre_event_sheet(self):
        for field, new in (('sheet_publication_year', 1961), ('sheet_original_acquired', True),
                           ('sheet_prior_to_incident', True), ('mi', 38)):
            c = copy.deepcopy(self.c)
            c['target_sheet'][field] = new
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(c)

    def test_cannot_promote_1998_source_as_1963_observation(self):
        for key in ('edition_1973_is_direct_contemporary_evidence',
                    'sources_are_independent_observations_of_incident', 'can_constrain_orbital_reentry'):
            c = copy.deepcopy(self.c)
            c['historical_use'][key] = True
            with self.subTest(field=key), self.assertRaises(ValueError):
                validate(c)

    def test_cannot_invent_event_georeference(self):
        for key in ('center_point_1963', 'center_polygon_1963', 'fall_location_1963',
                    'horizontal_error_m', 'historic_datum'):
            c = copy.deepcopy(self.c)
            c['historical_use'][key] = [-11.8, -37.6] if 'point' in key else 'EPSG:4326'
            with self.subTest(field=key), self.assertRaises(ValueError):
                validate(c)

    def test_prior_25000_sheets_not_assumed_authenticated(self):
        for field in ('individual_sheet_dates_authenticated', 'individual_sheet_bytes_acquired',
                      'coverage_of_1963_conde_center_authenticated'):
            c = copy.deepcopy(self.c)
            c['prior_cartographic_inputs_reported_by_sgb'][field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(c)

    def test_mutated_sources_rejected(self):
        for key in self.c['sources']:
            for field, new in (('sha256', '0' * 64), ('size_bytes', 0), ('issued_year', 1963)):
                c = copy.deepcopy(self.c)
                c['sources'][key][field] = new
                with self.subTest(key=key, field=field), self.assertRaises(ValueError):
                    validate(c)

    def test_catalogue_not_sheet_artifact(self):
        c = copy.deepcopy(self.c)
        c['sources']['sudene_1997_catalogue']['full_map_sheet_in_pdf'] = True
        with self.assertRaises(ValueError):
            validate(c)

    def test_wrong_sheet_numbers_rejected(self):
        c = copy.deepcopy(self.c)
        c['prior_cartographic_inputs_reported_by_sgb']['sheet_identifiers'][0] = '721-4-1'
        with self.assertRaises(ValueError):
            validate(c)


if __name__ == '__main__':
    unittest.main()
