"""CGEO-63: source-labeled editorial variants, chronology and epistemic gates."""
import copy
import json
import unittest
from tools import cgeo63_praca_editorial_variants as c63

BASE = json.loads(c63.MANIFEST.read_text(encoding="utf-8"))


class EditorialPlaceGate(unittest.TestCase):
    def setUp(self):
        self.d = copy.deepcopy(BASE)

    def bad(self, change):
        change(self.d)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            c63.validate(self.d)

    def test_valid(self):
        r = c63.validate(self.d)
        self.assertEqual(r["distinct_2018_editorial_venues"], 1)
        self.assertEqual(r["historical_contemporary_records"], 0)
        self.assertFalse(r["orbital_constraint"])

    def test_variant_not_independent_witness(self):
        self.bad(lambda d: d["interpretation"].update(independent_2018_venue_witnesses=2))

    def test_wrong_city(self):
        self.bad(lambda d: d["municipality"].update(ibge_code="2906907"))

    def test_tampered_original_hash(self):
        self.bad(lambda d: d["sources"][0].update(raw_sha256="0"*64))

    def test_2018_original_not_versioned(self):
        self.bad(lambda d: d["sources"][0].update(raw_bytes_versioned=True))

    def test_2018_count_tamper(self):
        self.bad(lambda d: d["sources"][0]["literal_utf8_counts"].update({"Severiano Vieira": 1}))

    def test_2018_venue_name_tamper(self):
        self.bad(lambda d: d["readings"][1].update(literal="Praça Severiano Lima"))

    def test_bust_year_tamper(self):
        self.bad(lambda d: d["readings"][3].update(event_date="1958-07-08"))

    def test_1904_claim_must_remain_retrospective(self):
        self.bad(lambda d: d["readings"][2].update(verification="primary_contemporary_claim"))

    def test_2025_http_403_not_200(self):
        self.bad(lambda d: d["sources"][1].update(retrieval_status="ACQUIRED"))

    def test_no_invented_2025_sha(self):
        self.bad(lambda d: d["sources"][1].update(raw_sha256="0"*64))

    def test_no_1958_plaza_merge(self):
        self.bad(lambda d: d["interpretation"].update(identity_with_1958_praca_severiano_lima=True))

    def test_no_2020_geometry_bridge(self):
        self.bad(lambda d: d["interpretation"].update(identity_with_2020_severino_vieira_geometry=True))

    def test_no_osm_equivalence(self):
        self.bad(lambda d: d["interpretation"].update(identity_with_modern_osm_ways=[1020642398]))

    def test_no_1963_center_polygon(self):
        self.bad(lambda d: d["interpretation"].update(historical_center_polygon_1963=[-11.8, -37.6]))

    def test_no_1963_event_point(self):
        self.bad(lambda d: d["interpretation"].update(event_location_1963=[-11.8, -37.6]))

    def test_no_invented_precision(self):
        self.bad(lambda d: d["interpretation"].update(positional_uncertainty_m=50))

    def test_no_orbital_activation(self):
        self.bad(lambda d: d["interpretation"].update(can_constrain_orbital_reentry=True))

    def test_no_active_constraint(self):
        self.bad(lambda d: d["interpretation"].update(active_constraint=True))

    def test_no_identity_rename_document(self):
        self.bad(lambda d: d["interpretation"].update(street_or_plaza_rename_document="inferred"))

    def test_no_1963_survey_for_municipal_2020_document(self):
        self.bad(lambda d: d["sources"][2].update(survey_geometry_1963={"lat": -11.8}))


if __name__ == "__main__":
    unittest.main()
