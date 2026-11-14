"""Adversarial CGEO-60: false historical center, time, and photo-resolution claims."""
import copy
import json
import unittest
from tools.cgeo60_modern_osm_cut import CONTRACT, haversine_km, parse_osm_node, validate

SOURCE = json.loads(CONTRACT.read_text(encoding="utf-8"))


class TestModernOSMCut(unittest.TestCase):
    def setUp(self):
        self.d = copy.deepcopy(SOURCE)

    def fails(self, edit):
        edit(self.d)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate(self.d)

    def test_positive(self):
        self.assertEqual(validate(self.d), {
            "distance_km": 1.975064, "film_scenario_mm": 0.066667,
            "historical_center": None, "active_constraint": False})

    def test_distance_symmetric(self):
        self.assertAlmostEqual(haversine_km(*self.d["nodes"]),
                               haversine_km(*list(reversed(self.d["nodes"]))))

    def test_reject_wrong_municipality(self):
        self.fails(lambda x: x["municipality"].update(uf="PB"))

    def test_reject_wrong_osm_id(self):
        self.fails(lambda x: x["nodes"][0].update(osm_node_id=123))

    def test_reject_wrong_place_tag(self):
        self.fails(lambda x: x["nodes"][1].update(place_tag="town"))

    def test_reject_false_2026_version(self):
        self.fails(lambda x: x["nodes"][0].update(osm_version=19))

    def test_reject_wrong_node_timestamp(self):
        self.fails(lambda x: x["nodes"][1].update(record_modified_utc="1963-11-08T00:00:00Z"))

    def test_reject_source_coordinate_mutation(self):
        self.fails(lambda x: x["nodes"][0].update(latitude=-11.8))

    def test_reject_renaming_villa_velha_to_vila20(self):
        self.fails(lambda x: x["nodes"][1].update(name_exact="Vila do Conde"))

    def test_reject_false_ibge_accuracy(self):
        self.fails(lambda x: x["nodes"][0].update(source_tag_not_a_positional_certification=False))

    def test_reject_missing_custody_hash(self):
        self.fails(lambda x: x["nodes"][0].update(raw_xml_sha256="NO_HASH"))

    def test_reject_wrong_derived_distance(self):
        self.fails(lambda x: x["derived"].update(great_circle_distance_km_earth_radius_6371=0))

    def test_reject_detectability_claim(self):
        self.fails(lambda x: x["derived"].update(detectability="DETECTABLE"))

    def test_reject_inflated_feature_scenario(self):
        self.fails(lambda x: x["derived"].update(feature_diameter_scenario_m=40))

    def test_reject_1942_as_post_event(self):
        self.fails(lambda x: x["historical_context"].update(nara_can_show_november_1963_trace=True))

    def test_reject_1963_centro_point(self):
        self.fails(lambda x: x["historical_context"].update(cgeo20_centro20_point_1963=[-37.6,-11.8]))

    def test_reject_1963_vila_point(self):
        self.fails(lambda x: x["historical_context"].update(cgeo20_vila20_point_1963=[-37.62,-11.8]))

    def test_reject_1963_temporal_bridge(self):
        self.fails(lambda x: x["historical_context"].update(time_bridge_to_1963=True))

    def test_reject_fall_location(self):
        self.fails(lambda x: x["historical_context"].update(reentry_impact_location=[0,0]))

    def test_reject_equating_osm_localities(self):
        self.fails(lambda x: x["historical_context"].update(modern_nodes_equate_to_cgeo20_historical_sites=True))

    def test_reject_active_orbital_constraint(self):
        self.fails(lambda x: x["castor_handoff"].update(active_constraint=True))

    def test_reject_posterior_claim(self):
        self.fails(lambda x: x["castor_handoff"].update(posterior=True))

    def test_reject_fictional_centro20_eval(self):
        self.fails(lambda x: x["castor_handoff"].update(historical_centro20_status="EVALUATED"))

    def test_xml_semantics_and_binary_independence(self):
        n = self.d["nodes"][0]
        body = (f'<osm version="0.6"><node id="{n["osm_node_id"]}" '
                f'version="{n["osm_version"]}" timestamp="{n["record_modified_utc"]}" '
                f'lat="{n["latitude"]}" lon="{n["longitude"]}">'
                '<tag k="name" v="Conde"/><tag k="place" v="town"/>'
                '<tag k="source" v="IBGE"/></node></osm>').encode()
        record = parse_osm_node(body,n)
        self.assertTrue(record["semantic_match"])
        self.assertFalse(record["binary_match"])

    def test_xml_reject_unverified_new_version(self):
        n=self.d["nodes"][1]
        body=(f'<osm version="0.6"><node id="{n["osm_node_id"]}" '
              f'version="4" timestamp="{n["record_modified_utc"]}" '
              f'lat="{n["latitude"]}" lon="{n["longitude"]}">'
              '<tag k="name" v="Villa Velha"/><tag k="place" v="village"/>'
              '</node></osm>').encode()
        with self.assertRaises(ValueError):
            parse_osm_node(body,n)


if __name__ == "__main__":
    unittest.main()
