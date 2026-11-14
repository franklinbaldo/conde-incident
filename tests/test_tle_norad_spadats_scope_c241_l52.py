"""C241-L52 adversarial tests: institutional SPADATS plans are not NORAD 528 measurements."""
import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import tle_norad_spadats_scope_c241_l52 as a

class ScopeTest(unittest.TestCase):
    def setUp(self):
        self.d = a.load()

    def rejects(self, edit):
        x = copy.deepcopy(self.d)
        edit(x)
        with self.assertRaises(ValueError):
            a.audit(x)

    def test_clean_ledger(self):
        self.assertTrue(a.audit(self.d))

    def test_hash_mutation(self):
        self.rejects(lambda x: x["source"].update(sha256="0" * 64))

    def test_size_mutation(self):
        self.rejects(lambda x: x["source"].update(bytes=7111329))

    def test_origin_mutation(self):
        self.rejects(lambda x: x["source"].update(institution="NASA"))

    def test_fictitious_instrument(self):
        self.rejects(lambda x: x["scope"].update(instrumental_observation_528="SAO 1963-11-08"))

    def test_date_invention(self):
        self.rejects(lambda x: x["scope"].update(epoch_528_utc="1963-11-08T12:00:00Z"))

    def test_fictitious_sigma(self):
        self.rejects(lambda x: x["scope"].update(sigma_528=0.01))

    def test_unearned_independence(self):
        self.rejects(lambda x: x["scope"].update(independent_instrumental_family_count=2))

    def test_request_as_actual_transfer(self):
        self.rejects(lambda x: x["scope"].update(actual_1963_sao_to_spadats_528_transfer=True))

    def test_premature_activation(self):
        self.rejects(lambda x: x["scope"].update(physical_constraint_active=True))

    def test_fictitious_location(self):
        self.rejects(lambda x: x["scope"].update(impact_location_528="Conde"))

    def test_page_error(self):
        self.rejects(lambda x: x["events"][0].update(pdf_page_index=69))

    def test_wrong_year(self):
        self.rejects(lambda x: x["events"][0].update(date="1964-07-17"))

    def test_planned_recast_as_installed(self):
        self.rejects(lambda x: x["events"][2].update(kind="confirmed-operational-coverage"))

    def test_extra_metric(self):
        self.rejects(lambda x: x.update(accuracy_km=0.01))

    def test_bad_pdf(self):
        with self.assertRaises(ValueError):
            a.verify_pdf(self.d, b"%PDF-1.4\n%%EOF")

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=a.unique_pairs)

if __name__ == "__main__":
    unittest.main()
