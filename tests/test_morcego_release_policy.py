"""Morcego: NASA/NORAD policy graph, auditable but not re-entry evidence."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research" / "constraints" / "morcego_1963_tracking_release_policy.json"


def validate_policy_graph(data):
    assert data["schema"] == "conde.documentary-publication-control/v1"
    sources = {s["id"]: s for s in data["source_families"]}
    observations = {o["id"]: o for o in data["observations"]}
    variables = {v["id"]: v for v in data["latent_variables"]}
    assert len(sources) == len(data["source_families"])
    assert len(observations) == len(data["observations"])
    assert len(variables) == len(data["latent_variables"])
    assert data["status"]["new_primary_instrumental_measurement_528"] is False
    assert data["status"]["physical_domain_reduced"] == "NOT_EVALUABLE_FROM_POLICY_DOCUMENTS"
    assert data["status"]["independent_528_witness"] is False
    for source in sources.values():
        assert source["source_url"].startswith("https://")
        assert source["existing_matrix_crossref"]
        assert source["sha256"] is None or len(source["sha256"]) == 64
    for obs in observations.values():
        assert obs["source"] in sources, obs["id"]
        assert obs["physical_constraint_active"] is False, obs["id"]
        assert obs["classification"] != "PRIMARY_528_SENSOR_OBSERVATION"
    for edge in data["relationships"]:
        assert edge["from"] in observations, edge["id"]
        assert edge["to"] in observations or edge["to"] in variables, edge["id"]
        assert edge["condition"], edge["id"]
        assert edge["status"] != "ACTIVE_HARD_PHYSICAL_CONSTRAINT"
    assert len({e["id"] for e in data["relationships"]}) == len(data["relationships"])
    return sources, observations, variables


class PolicyDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SRC.read_text(encoding="utf-8"))

    def test_complete_provenance_with_unknown_measurements(self):
        sources, observations, variables = validate_policy_graph(self.data)
        self.assertEqual(len(sources), 3)
        self.assertEqual(len(observations), 6)
        self.assertEqual(len(self.data["relationships"]), 6)
        self.assertFalse(variables["tracking_measurement_528"]["known"])

    def test_period_of_reporting_is_not_terminal_orbit_interval(self):
        entry = next(x for x in self.data["observations"]
                     if x["field"] == "normal_tracking_request_window")
        self.assertEqual(entry["value"], 6)
        self.assertEqual(entry["units"], "hours")
        self.assertIn("NOT_A_REENTRY_TIME", entry["classification"])

    def test_same_1963_hearing_does_not_count_as_independent_sensors(self):
        sources, *_ = validate_policy_graph(self.data)
        self.assertEqual(
            sources["MOR-NASA-1963-AP"]["dependence_family"],
            sources["MOR-HOUSE-1965"]["dependence_family"])
        self.assertNotEqual(
            sources["MOR-NAVSPASUR-1962-MOA"]["dependence_family"],
            sources["MOR-HOUSE-1965"]["dependence_family"])

    def test_publication_day_differs_from_testimony_day(self):
        item = next(o for o in self.data["observations"] if o["source"] == "MOR-NASA-1963-AP")
        self.assertEqual(item["date_of_claim"], "1963-05-23")
        self.assertEqual(item["publication_date"], "1963-05-24")

    def test_do_not_activate_or_infer_military_object_classification(self):
        self.assertFalse(self.data["status"]["new_primary_instrumental_measurement_528"])
        self.assertEqual(self.data["status"]["narrowing_predicate_lean"],
                         "PENDING_PRIMARY_STATION_TIME_ANGLE_RECORD")
        self.assertNotIn("528", str(next(
            o for o in self.data["observations"] if o["field"] == "classification_decision_authority"
        )["value"]))

    def test_no_fabricated_source_sha_or_orbit(self):
        self.assertTrue(all(s["sha256"] is None for s in self.data["source_families"]))
        self.assertTrue(all(v["known"] is False for v in self.data["latent_variables"]
                            if v["physical"]))

    def test_graph_rejects_unjustified_hard_physics(self):
        modified = json.loads(json.dumps(self.data))
        modified["observations"][0]["physical_constraint_active"] = True
        with self.assertRaises(AssertionError):
            validate_policy_graph(modified)

    def test_links_fail_if_source_is_orphan(self):
        modified = json.loads(json.dumps(self.data))
        modified["observations"][0]["source"] = "FICTIONAL"
        with self.assertRaises(AssertionError):
            validate_policy_graph(modified)


if __name__ == "__main__":
    unittest.main()
