"""CGEO-11: verify primary cartographic methodology and dependent safety gates."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from tools.conde_ibge_lineage import (
    PDF_SHA, CONTRACT, CGEO10, evaluate, validate, verify_pdf,
)


class HistoricalIBGELineageTest(unittest.TestCase):
    def setUp(self):
        self.data = validate()

    def with_mutation(self, modifier):
        clone = copy.deepcopy(self.data)
        modifier(clone)
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "changed.json"
            path.write_text(json.dumps(clone), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(path)

    def test_documentary_primary_method_source_and_page(self):
        source = self.data["documentary_evidence"]
        self.assertEqual(source["pdf_sha256"], PDF_SHA)
        self.assertEqual(source["pdf_size_bytes"], 15484)
        self.assertEqual(source["page_1_based"], 1)
        self.assertEqual(source["publisher"], "IBGE")
        self.assertEqual(source["classification"], "OFFICIAL_PRIMARY_METHOD_STATEMENT")

    def test_derived_from_1991_not_two_independent_historical_surveys(self):
        method = self.data["official_methodology"]
        self.assertEqual(method["base_mesh_nominal_year"], 1991)
        self.assertEqual(method["nominal_year_of_derived_conde_record"], 1960)
        self.assertIs(method["independence_from_1991_topology"], False)
        self.assertIs(method["cartographic_precision_claimed"], False)
        self.assertIsNone(method["numeric_horizontal_accuracy_m"])

    def test_export_has_no_event_or_location_inference(self):
        for day in ("1960-07-01", "1963-11-08", "2025-11-12"):
            result = evaluate(day, self.data)
            self.assertIsNone(result["point_membership"])
            self.assertIsNone(result["legal_boundary_for_1963"])
            self.assertIsNone(result["positional_accuracy_m"])
            self.assertFalse(result["can_filter_1963_reentry_positions"])
            self.assertFalse(result["can_compute_1963_location_probability"])

    def test_bridge_points_to_1991_base_and_refuses_1963(self):
        edges = self.data["dependency_graph"]["edges"]
        self.assertEqual(len(edges), 4)
        self.assertIn("NOT_A_VALIDATED_TEMPORAL_OR_PRECISION_BRIDGE",
                      {edge["kind"] for edge in edges})

    def test_refuse_fake_quantified_accuracy(self):
        self.with_mutation(lambda d: d["official_methodology"].update(
            {"numeric_horizontal_accuracy_m": 10}))

    def test_refuse_independence_upgrade(self):
        self.with_mutation(lambda d: d["official_methodology"].update(
            {"independence_from_1991_topology": True}))

    def test_refuse_1963_filter(self):
        self.with_mutation(lambda d: d["castor_export"].update(
            {"can_filter_1963_reentry_positions": True}))

    def test_refuse_1963_event_point(self):
        self.with_mutation(lambda d: d["castor_export"].update(
            {"event_point_1963": [-37.6, -11.8]}))

    def test_refuse_discarded_temporal_bridge(self):
        self.with_mutation(lambda d: d["dependency_graph"].update({"edges": []}))

    def test_rejects_fake_pdf(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "fake.pdf"
            p.write_bytes(b"%PDF" + b"0" * 15480)
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                verify_pdf(p, self.data)

    def test_source_mesh_still_valid(self):
        self.assertTrue(CONTRACT.is_file())
        self.assertTrue(CGEO10.is_file())
        self.assertEqual(validate()["id"], "CGEO-11")


if __name__ == "__main__":
    unittest.main()
