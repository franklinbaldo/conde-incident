"""CGEO-62: tests replaying OSM's original XML source, including mutations."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import cgeo62_praca_multigeometry as c62

BASE = json.loads(c62.MANIFEST.read_text(encoding="utf8"))

class PlazaEvidence(unittest.TestCase):
    def setUp(self):
        self.m = copy.deepcopy(BASE)

    def bad(self, mutate):
        mutate(self.m)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            c62.validate(self.m)

    def test_valid_exact_source_replay(self):
        result = c62.validate(self.m)
        self.assertEqual(result["features"], 4)
        self.assertEqual(result["named_park_polygons"], 2)
        self.assertEqual(result["named_road_segments"], 2)
        self.assertEqual(result["park_centroid_separation_m"], 138.611)
        self.assertEqual(result["park_boundary_gap_approx_m"], 61.795)
        self.assertFalse(result["active_constraint"])

    def test_metadata_different_revision_years(self):
        self.assertEqual([p["osm_revision_utc"][:4] for p in self.m["features"][:2]],
                         ["2026","2022"])

    def test_park_areas_are_derived_not_survey(self):
        self.assertEqual([p["area_local_planar_m2"] for p in self.m["features"][:2]],
                         [1039.09,2423.692])

    def test_two_named_parks_are_not_two_independent_historical_sources(self):
        self.assertEqual(self.m["source"]["independent_historical_observations"],0)
        self.assertFalse(self.m["interpretation"]["separate_physical_public_squares_proven"])

    def test_town_and_conder_are_separate_comparators(self):
        self.assertEqual(self.m["comparisons"]["town_proxy_source"],
                         "research/geo/cgeo60_modern_osm_cut.json")
        self.assertEqual(self.m["comparisons"]["conder_proxy_source"],
                         "research/geo/cgeo61_conder_sede_point.json")

    def test_raw_osm_urls_are_identified(self):
        for p in self.m["features"]:
            self.assertEqual(p["url"],f"https://api.openstreetmap.org/api/0.6/way/{p['osm_way_id']}/full")

    def test_mutation_source_sha(self):
        self.bad(lambda m:m["features"][0].update(raw_sha256="0"*64))

    def test_mutation_feature_id(self):
        self.bad(lambda m:m["features"][0].update(osm_way_id=123))

    def test_mutation_polygon_area(self):
        self.bad(lambda m:m["features"][1].update(area_local_planar_m2=100))

    def test_mutation_park_into_road(self):
        self.bad(lambda m:m["features"][0].update(role="road"))

    def test_mutation_claims_same_1963_center(self):
        self.bad(lambda m:m["interpretation"].update(same_name_features_are_one_1963_center=True))

    def test_mutation_claims_separate_plazas(self):
        self.bad(lambda m:m["interpretation"].update(separate_physical_public_squares_proven=True))

    def test_mutation_claims_1958_match(self):
        self.bad(lambda m:m["interpretation"].update(plaza_from_1958_is_identical=True))

    def test_mutation_claims_2020_continuity(self):
        self.bad(lambda m:m["interpretation"].update(municipal_document_2020_same_geometry=True))

    def test_mutation_claims_1963_polygon(self):
        self.bad(lambda m:m["interpretation"].update(plaza_polygon_in_1963=[-11.813,-37.612]))

    def test_mutation_claims_impact_location(self):
        self.bad(lambda m:m["interpretation"].update(impact_location=[-11.813,-37.612]))

    def test_mutation_activates_orbital_constraint(self):
        self.bad(lambda m:m["interpretation"].update(can_constrain_orbital_reentry=True))

    def test_mutation_activates_evidence(self):
        self.bad(lambda m:m["interpretation"].update(active_constraint=True))

    def test_mutation_claims_1963_survey_epoch(self):
        self.bad(lambda m:m["source"].update(survey_epoch="1963-11-08"))

    def test_mutation_claims_precision(self):
        self.bad(lambda m:m["source"].update(horizontal_accuracy_m=2))

    def test_mutation_invents_independent_historical_sources(self):
        self.bad(lambda m:m["source"].update(independent_historical_observations=4))

    def test_mutation_fake_centroid_distance(self):
        self.bad(lambda m:m["comparisons"].update(park_centroid_separation_m=1.0))

    def test_mutation_fake_gap(self):
        self.bad(lambda m:m["comparisons"].update(park_boundary_gap_approx_m=0.0))

    def test_source_byte_flip_fails_hash(self):
        pin = c62.PINS[0]
        original = (c62.SOURCES/f"cgeo62_osm_way_{pin[0]}.xml").read_bytes()
        bad = original.replace(b"Severino",b"Severina")
        self.assertNotEqual(bad,original)
        with self.assertRaisesRegex(ValueError,"raw source hash mismatch"):
            c62.summary(bad,pin)

    def test_wrong_osm_way_identity_fails(self):
        pin = c62.PINS[0]
        original = (c62.SOURCES/f"cgeo62_osm_way_{pin[0]}.xml").read_bytes()
        with self.assertRaises(ValueError):
            c62.parse(original, 1020642398)

    def test_open_osm_road_cannot_become_park(self):
        pin = c62.PINS[2]
        original = (c62.SOURCES/f"cgeo62_osm_way_{pin[0]}.xml").read_bytes()
        mutated_pin = (*pin[:5],"park",pin[6])
        with self.assertRaisesRegex(ValueError,"not a closed park"):
            c62.summary(original,mutated_pin)

    def test_poly_overlap_requires_new_topology_logic(self):
        p=[(-11.8,-37.6),(-11.8,-37.59),(-11.79,-37.59),(-11.8,-37.6)]
        with self.assertRaisesRegex(ValueError,"envelopes overlap"):
            c62.boundary_gap(p,p)

if __name__ == "__main__":
    unittest.main()

