"""CGEO-59 adversarial catalog-contract checks, independent of assertions."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cgeo59_nara_query_audit import PATH, validate  # noqa: E402


class NaraSearchTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(PATH.read_text(encoding="utf-8"))

    def reject(self, mutate):
        snapshot = copy.deepcopy(self.doc)
        mutate(snapshot)
        with self.assertRaises(ValueError):
            validate(snapshot)

    def test_accept_custodied_snapshot(self):
        self.assertEqual(validate(self.doc), {"queries": 4, "squares": 11, "distractors": 4})

    def test_wrong_schema(self):
        self.reject(lambda d: d.update(schema="other"))

    def test_wrong_endpoint(self):
        self.reject(lambda d: d.update(endpoint="https://example.org"))

    def test_missing_query(self):
        self.reject(lambda d: d["queries"].pop())

    def test_query_id_mutation(self):
        self.reject(lambda d: d["queries"][0].update(id="alien"))

    def test_query_string_mutation(self):
        self.reject(lambda d: d["queries"][0].update(q="125374"))

    def test_query_limit(self):
        self.reject(lambda d: d["queries"][0].update(limit=100))

    def test_bad_http(self):
        self.reject(lambda d: d["queries"][0].update(http_status=403))

    def test_bytes_missing(self):
        self.reject(lambda d: d["queries"][0].update(body_bytes=0))

    def test_hash_bad(self):
        self.reject(lambda d: d["queries"][0].update(sha256="not-a-hash"))

    def test_unrelated_becomes_overlay(self):
        self.reject(lambda d: d["queries"][0]["results"][-1].update(
            title="Overlay indexes for degree square 99S999W"))

    def test_duplicate_naid(self):
        self.reject(lambda d: d["queries"][0]["results"][1].update(
            naid=d["queries"][0]["results"][0]["naid"]))

    def test_targeted_conde_wrong_naid(self):
        self.reject(lambda d: d["queries"][2]["results"][0].update(naid="12345678"))

    def test_negative_control_nonzero(self):
        self.reject(lambda d: d["queries"][3].update(total_hits=1))

    def test_candidate_count(self):
        self.reject(lambda d: d["derived"].update(candidate_count=12))

    def test_fake_intersection(self):
        self.reject(lambda d: d["derived"].update(common_naids_between_primary_queries=[]))

    def test_fake_spot_number(self):
        self.reject(lambda d: d["limits"].update(spot_number="125374"))

    def test_fake_photo(self):
        self.reject(lambda d: d["limits"].update(original_aerial_photograms_acquired=1))

    def test_fake_geometry(self):
        self.reject(lambda d: d["limits"].update(historical_urban_center_1963=[0, 0]))

    def test_fake_orbit(self):
        self.reject(lambda d: d["limits"].update(orbital_constraint_activated=True))

    def test_contact_not_authorized(self):
        self.reject(lambda d: d["limits"].update(contact_sent=True))


if __name__ == "__main__":
    unittest.main()
