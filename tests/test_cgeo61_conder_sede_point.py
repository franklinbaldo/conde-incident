"""CGEO-61: adversarial evidence checks for a modern CONDER map service."""
import copy
import json
import unittest

from tools.cgeo61_conder_sede_point import (
    MANIFEST, OSM, distance_and_bearing, expected_url, inspect_geojson, validate,
)

BASE = json.loads(MANIFEST.read_text(encoding="utf-8"))
PARENT = json.loads(OSM.read_text(encoding="utf-8"))
SEDE = {
    "type":"FeatureCollection", "features":[{
        "type":"Feature", "id":1038,
        "geometry":{"type":"Point","coordinates":[-37.60697798199999,-11.813431761000004]},
        "properties":{"OBJECTID":1038,"CODIGO":"290860605000001","MUNICIPIO":"CONDE"}}]}
LOCAL = copy.deepcopy(SEDE)
LOCAL["features"][0]["properties"].update({
    "COD_MUNICIPIO":"2908606", "UF":"BAHIA", "TIPO":"URBANO",
    "CATEGORIA":"CIDADE", "NOME":"Sede"})
RAW_SEDE = json.dumps(SEDE).encode("utf-8")
RAW_LOCAL = json.dumps(LOCAL).encode("utf-8")


class TestConderSede(unittest.TestCase):
    def setUp(self):
        self.d = copy.deepcopy(BASE)
        self.parent = copy.deepcopy(PARENT)

    def rejects(self, modify):
        modify(self.d)
        with self.assertRaises((ValueError, TypeError, KeyError)):
            validate(self.d, self.parent)

    def test_positive_and_result(self):
        result = validate(self.d, self.parent)
        self.assertEqual(result["distance_m"], 751.891919)
        self.assertEqual(result["bearing_deg"], 93.86713)
        self.assertIsNone(result["historical_center"])
        self.assertFalse(result["active_constraint"])

    def test_real_endpoint_structure(self):
        self.assertEqual(
            expected_url("SEDES_MUNICIPAIS_PTO", "MUNICIPIO='CONDE'"),
            self.d["source"]["service_queries"][0]["url"])

    def test_source_geojson_semantics_without_faking_binary(self):
        a = inspect_geojson(RAW_SEDE, self.d["source"]["service_queries"][0], self.d["point"])
        b = inspect_geojson(RAW_LOCAL, self.d["source"]["service_queries"][1], self.d["point"])
        self.assertTrue(a["semantic_match"] and b["semantic_match"])
        self.assertFalse(a["binary_match"] or b["binary_match"])

    def test_reject_wrong_city(self):
        self.rejects(lambda d:d["municipality"].update(uf="PB"))

    def test_reject_fake_dataset_capture_date(self):
        self.rejects(lambda d:d["source"].update(data_epoch="1963"))

    def test_reject_fake_accuracy(self):
        self.rejects(lambda d:d["source"].update(measurement_accuracy_m=3))

    def test_reject_unverified_license(self):
        self.rejects(lambda d:d["source"].update(license="Public Domain"))

    def test_reject_query_substitution(self):
        self.rejects(lambda d:d["source"]["service_queries"][0].update(url="https://fake.example/"))

    def test_reject_wrong_spatial_reference(self):
        self.rejects(lambda d:d["source"].update(spatial_reference="EPSG:3857"))

    def test_reject_substituted_source_sha256(self):
        self.rejects(lambda d:d["source"]["service_queries"][0].update(raw_sha256="0"*64))

    def test_reject_substituted_source_size(self):
        self.rejects(lambda d:d["source"]["service_queries"][1].update(raw_bytes=490))

    def test_reject_new_official_coordinates(self):
        self.rejects(lambda d:d["point"].update(longitude=-37.60))

    def test_reject_fake_independence(self):
        self.rejects(lambda d:d["dependence"].update(independent_measurements_established=True))

    def test_reject_fake_1963_center(self):
        self.rejects(lambda d:d["historical_guards"].update(as_of_november_1963_point=[0,0]))

    def test_reject_bridge_to_1963(self):
        self.rejects(lambda d:d["historical_guards"].update(physical_continuity_to_1963=True))

    def test_reject_assumed_accuracy_m(self):
        self.rejects(lambda d:d["historical_guards"].update(georeferencing_accuracy_m=5))

    def test_reject_impact_location(self):
        self.rejects(lambda d:d["historical_guards"].update(impact_location=0))

    def test_reject_orbital_activation(self):
        self.rejects(lambda d:d["historical_guards"].update(active_constraint=True))

    def test_reject_posterior(self):
        self.rejects(lambda d:d["historical_guards"].update(posterior=True))

    def test_reject_false_comparator_distance(self):
        self.rejects(lambda d:d["comparator"].update(separation_m=0.0))

    def test_reject_source_point_changed(self):
        sample = copy.deepcopy(SEDE)
        sample["features"][0]["geometry"]["coordinates"][0] = -37.5
        with self.assertRaises(ValueError):
            inspect_geojson(json.dumps(sample).encode(), self.d["source"]["service_queries"][0],self.d["point"])

    def test_reject_source_class_changed(self):
        sample = copy.deepcopy(LOCAL)
        sample["features"][0]["properties"]["CATEGORIA"] = "VILA"
        with self.assertRaises(ValueError):
            inspect_geojson(json.dumps(sample).encode(), self.d["source"]["service_queries"][1],self.d["point"])

    def test_reject_source_record_code_changed(self):
        sample = copy.deepcopy(SEDE)
        sample["features"][0]["properties"]["CODIGO"] = "2908705"
        with self.assertRaises(ValueError):
            inspect_geojson(json.dumps(sample).encode(), self.d["source"]["service_queries"][0],self.d["point"])

    def test_reject_extra_feature(self):
        sample = copy.deepcopy(SEDE)
        sample["features"].append(copy.deepcopy(sample["features"][0]))
        with self.assertRaises(ValueError):
            inspect_geojson(json.dumps(sample).encode(), self.d["source"]["service_queries"][0],self.d["point"])

    def test_reject_parent_osm_mutation(self):
        self.parent["nodes"][0]["longitude"] = -37.9
        with self.assertRaises(ValueError):
            validate(self.d,self.parent)

    def test_distance_symmetry_and_direction(self):
        official = self.d["point"]
        osm = self.parent["nodes"][0]
        distance, bearing = distance_and_bearing(osm,official)
        reverse, back = distance_and_bearing(official,osm)
        self.assertAlmostEqual(distance,reverse,places=7)
        self.assertLess(abs((bearing+180-back+180)%360-180),0.5)


if __name__ == "__main__":
    unittest.main()
