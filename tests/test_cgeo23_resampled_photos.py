"""CGEO-23 offline safeguards. Real photo replay is opt-in due to remote source custody."""
import copy
import unittest
from tools.cgeo23_resampled_photos import load_contract, validate_contract, MATCHES, ORIGINALS


class Cgeo23ContractTests(unittest.TestCase):
    def setUp(self):
        self.data = load_contract()

    def test_contract_parent_bytes_and_method(self):
        validate_contract(self.data)
        self.assertEqual(MATCHES, {'wp2': 'igreja', 'wp3': 'alto'})

    def test_complete_negative_controls(self):
        for target, expected in MATCHES.items():
            row = self.data['result']['comparison_matrix'][target]
            self.assertEqual(set(row), set(ORIGINALS))
            self.assertLess(row[expected]['mae_rgb'], 4)
            self.assertGreater(row[expected]['gray_pearson'], .995)
            for different in set(ORIGINALS) - {expected}:
                self.assertGreater(row[different]['mae_rgb'], 40)

    def test_reject_geographic_fabrication(self):
        for key, value in (('center_1963_point', [-11.8, -37.6]),
                           ('impact_point', [-11.8, -37.6]),
                           ('crs', 'EPSG:4326'), ('can_constrain_orbital_reentry', True)):
            x = copy.deepcopy(self.data)
            x['geospatial'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_contract(x)

    def test_reject_1959_capture_promotion(self):
        for key in ('exposure_date_1959_authenticated', 'original_negative_verified',
                    'direction_of_copying_verified', 'two_independent_historical_witnesses',
                    'rights_to_redistribute_verified'):
            x = copy.deepcopy(self.data)
            x['result'][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_contract(x)

    def test_tampered_parent_hash_or_reference_rejected(self):
        for group, key in (('wordpress', 'wp2'), ('blogger', 'alto')):
            x = copy.deepcopy(self.data)
            x['sources'][group][key]['sha256'] = '0' * 64
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_contract(x)

    def test_misidentified_photo_rejected(self):
        x = copy.deepcopy(self.data)
        x['result']['match_ids']['wp2'] = 'vila'
        with self.assertRaises(ValueError):
            validate_contract(x)

    def test_control_deletion_rejected(self):
        x = copy.deepcopy(self.data)
        del x['result']['comparison_matrix']['wp3']['passarela']
        with self.assertRaises(ValueError):
            validate_contract(x)

    def test_metric_falsification_rejected(self):
        x = copy.deepcopy(self.data)
        x['result']['comparison_matrix']['wp2']['igreja']['mae_rgb'] = 57
        with self.assertRaises(ValueError):
            validate_contract(x)


if __name__ == '__main__':
    unittest.main()
