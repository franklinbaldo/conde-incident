"""Only checks archival provenance and pending graph links, not orbital truth."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/constraints/morcego_sao_ru478_1963_crosswalk.json"
PRIOR = ROOT / "research/constraints/baker_nunn_ru301_1963_film_index.json"


class MorcegoRU478Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(DATA.read_text(encoding="utf-8"))

    def test_single_institutional_family_not_independent_physical_sources(self):
        self.assertEqual(len(self.d["sources"]), 2)
        self.assertEqual(len(self.d["occurrences"]), 6)
        self.assertEqual({r["independence_family"] for r in self.d["occurrences"]},
                         {"SMITHSONIAN_SAO_PROGRAM"})
        self.assertFalse(any(r["original_instrument_measurement"] for r in self.d["occurrences"]))

    def test_original_ru301_sc8_is_shiraz_not_curacao(self):
        old = json.loads(PRIOR.read_text(encoding="utf-8"))
        self.assertTrue(any(f["station_code"] == "SC-8" for f in old["film_index_entries"]))
        variables = {v["id"]: v["value"] for v in self.d["variables"]}
        self.assertEqual(variables["sc8_site_1963"], "Shiraz, Iran")
        self.assertEqual(variables["sc8_station_code_1963"], "9008")
        self.assertEqual(variables["sc9_site_1963"], "Curaçao, Netherlands Antilles")
        self.assertEqual(variables["sc9_station_code_1963"], "9009")

    def test_all_edges_refer_to_existing_variables_and_never_claim_physical_constraint(self):
        ids = {x["id"] for x in self.d["variables"]}
        self.assertEqual(len(ids), len(self.d["variables"]))
        for edge in self.d["edges"]:
            self.assertTrue(set(edge["variables"]).issubset(ids))
            self.assertFalse(edge["hard_physical_constraint"])
            if edge["metadata_active"]:
                self.assertEqual(edge["status"], "ACTIVE_METADATA_ONLY")
            else:
                self.assertEqual(edge["status"], "CONNECTED_PENDING_EVIDENCE")

    def test_no_invented_1963_observation_clock_or_error(self):
        variables = {v["id"]: v["value"] for v in self.d["variables"]}
        for name in ["ru478_nov63_monthly_report", "tape12546_object528_present",
                     "sc8_1963_station_coordinates", "sc8_1963_exposure_utc",
                     "sc8_1963_angle", "sc8_1963_angle_error",
                     "sc8_1963_clock_correction", "sc8_1963_weather"]:
            self.assertIsNone(variables[name], name)

    def test_catalogue_inventory_is_not_a_sensor_measurement(self):
        self.assertEqual(self.d["domain_reduction"], "NOT_EVALUABLE")
        self.assertEqual(self.d["conclusion"], "NO_CONDE_IMPACT_INFERENCE")
        self.assertTrue(all(not r["hard_physical_constraint"] for r in self.d["occurrences"]))
        self.assertEqual({r["source_id"] for r in self.d["occurrences"]}, {"RU478", "SAO-SR353"})


if __name__ == "__main__":
    unittest.main()
