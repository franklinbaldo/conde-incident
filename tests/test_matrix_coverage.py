"""Two-feed snapshot coverage: only explicit and authenticated occurrences count."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_matrix_coverage as audit
import provenance_graph as pg


class MatrixCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pg.matrix_occurrences(pg.MATRIX.read_bytes())
        cls.cites = json.loads(audit.CITATIONS.read_bytes())
        cls.bridges = json.loads(audit.OBSERVABLES.read_bytes())
        cls.archive = json.loads(audit.ARCHIVE.read_bytes())
        cls.cartography = json.loads(audit.CARTOGRAPHY.read_bytes())

    def test_actual_two_feed_coverage(self):
        result = audit.rebuild()
        self.assertEqual(result["matrix_occurrences"], 241)
        self.assertGreaterEqual(result["curated_occurrences"], 28)
        self.assertGreaterEqual(result["bridge_occurrences"], 4)
        self.assertEqual(result["bridge_edges"], sum(len(self.bridges[x]) for x in audit.BRIDGE_SECTIONS))
        self.assertGreaterEqual(result["represented_in_either"], 30)
        self.assertEqual(result["not_represented_in_these_feeds"],
                         241 - result["represented_in_either"])
        self.assertNotIn("C227#1", result["not_represented_ids"])
        self.assertNotIn("C228#1", result["not_represented_ids"])
        self.assertEqual(result["activated_physical_constraints_from_these_bridges"], 0)
        self.assertIn("C44#2", result["not_represented_ids"])

    def test_duplicate_bridge_edges_are_not_new_occurrences(self):
        data = copy.deepcopy(self.bridges)
        data["pending_december_compilation_edges"].append(
            copy.deepcopy(data["pending_december_compilation_edges"][0]))
        result = audit.audit(self.rows, self.cites, data)
        self.assertEqual(result["represented_in_either"],
                         audit.audit(self.rows, self.cites, self.bridges)["represented_in_either"])
        self.assertEqual(result["bridge_edges"],
                         1 + sum(len(self.bridges[x]) for x in audit.BRIDGE_SECTIONS))

    def test_wrong_snapshot_rejected(self):
        data = copy.deepcopy(self.bridges)
        data["matrix_git_blob_sha1"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "cross-snapshot"):
            audit.audit(self.rows, self.cites, data)

    def test_wrong_row_hash_or_line_rejected(self):
        cites = copy.deepcopy(self.cites)
        cites["records"][0]["row_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "row hash"):
            audit.audit(self.rows, cites, self.bridges)
        bridges = copy.deepcopy(self.bridges)
        bridges["edges"][0]["matrix_line"] = 0
        with self.assertRaisesRegex(ValueError, "line disagrees"):
            audit.audit(self.rows, self.cites, bridges)

    def test_unsnapshotted_or_forged_occurrence_rejected(self):
        bridges = copy.deepcopy(self.bridges)
        bridges["edges"][0]["matrix_occurrence"] = "C179#1"
        with self.assertRaisesRegex(ValueError, "unsnapshotted"):
            audit.audit(self.rows, self.cites, bridges)
        bridges["edges"][0]["matrix_occurrence"] = pg.matrix_ref("C239#1")
        with self.assertRaisesRegex(ValueError, "missing"):
            audit.audit(self.rows, self.cites, bridges)

    def test_never_infer_independence_or_instrument(self):
        for key, value in (("independent_sensor", True),
                           ("instrument_epoch_utc", "1963-12-31T12:00:00Z"),
                           ("instrument_covariance", [[0.01]]),
                           ("physical_domain_effect", "THETA_REDUCED"),
                           ("activation", True)):
            with self.subTest(key=key):
                bridges = copy.deepcopy(self.bridges)
                bridges["pending_december_compilation_edges"][0][key] = value
                with self.assertRaisesRegex(ValueError, "promoted|activated"):
                    audit.audit(self.rows, self.cites, bridges)

    def test_do_not_count_unqualified_context_as_link(self):
        bridges = copy.deepcopy(self.bridges)
        bridges["pending_documentary_edges"] = [
            {"matrix_context": "C44#1", "activation": False} for _ in range(50)]
        self.assertEqual(audit.audit(self.rows, self.cites, bridges)
                         ["represented_in_either"],
                         audit.audit(self.rows, self.cites, self.bridges)["represented_in_either"])

    def test_actual_archival_and_cartographic_context(self):
        result = audit.rebuild()
        ctx = result["supplemental_context_layers"]
        self.assertEqual(result["represented_in_either"], 30)
        self.assertEqual(result["not_represented_in_these_feeds"], 211)
        self.assertEqual(ctx["archival_distinct_matrix_occurrences"], 2)
        self.assertEqual(ctx["archival_new_matrix_occurrences"], 0)
        self.assertEqual(ctx["unqualified_cartographic_context_ids"], ["C24#1"])
        self.assertEqual(ctx["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertIn("C24#1", result["not_represented_ids"])

    def test_reject_archive_synthetic_row_hash_or_line(self):
        for key, replacement in (("row_sha256", "0" * 64), ("matrix_line", 0)):
            with self.subTest(key=key):
                archive = copy.deepcopy(self.archive)
                next(n for n in archive["nodes"] if n.get("kind") == "FROZEN_MATRIX_CITATION")[key] = replacement
                with self.assertRaisesRegex(ValueError, "archival citation row/line"):
                    audit.audit_context_layers(self.rows, self.cites, archive, self.cartography)

    def test_reject_archive_unqualified_or_independent_sensor(self):
        for key, value in (("activation", True), ("simulator_value", 123),
                           ("new_physical_observations", 1)):
            with self.subTest(key=key):
                archive = copy.deepcopy(self.archive)
                next(n for n in archive["nodes"] if n.get("kind") == "FROZEN_MATRIX_CITATION")[key] = value
                with self.assertRaisesRegex(ValueError, "falsely activated"):
                    audit.audit_context_layers(self.rows, self.cites, archive, self.cartography)
        archive = copy.deepcopy(self.archive)
        archive["counts"]["nasa_legacy_distinct_pdf_payloads"] = 3
        with self.assertRaisesRegex(ValueError, "lineage"):
            audit.audit_context_layers(self.rows, self.cites, archive, self.cartography)

    def test_reject_archive_forged_snapshotted_record(self):
        archive = copy.deepcopy(self.archive)
        next(n for n in archive["nodes"] if n.get("kind") == "FROZEN_MATRIX_CITATION")["snapshot_ref"] = "matrix:a7978c3a75a153b16ab70118a92c434bba674cb7:C24#1"
        with self.assertRaisesRegex(ValueError, "outside verified"):
            audit.audit_context_layers(self.rows, self.cites, archive, self.cartography)

    def test_reject_map_pixel_promoted_to_geographic_coordinate(self):
        for key, value in (("geographic_coordinates", [-37.6, -11.8]),
                           ("ground_tolerance_m", 1)):
            with self.subTest(key=key):
                cart = copy.deepcopy(self.cartography)
                cart["image_coordinate_datum"][key] = value
                with self.assertRaisesRegex(ValueError, "falsely georeferenced"):
                    audit.audit_context_layers(self.rows, self.cites, self.archive, cart)

    def test_reject_map_false_physical_or_renamed_context(self):
        for key, value in (("activation", True),
                           ("new_numeric_orbital_constraints", 1),
                           ("independent_physical_witnesses_added", 1),
                           ("physical_domain_effect", "THETA_REDUCED")):
            with self.subTest(key=key):
                cart = copy.deepcopy(self.cartography)
                cart[key] = value
                with self.assertRaisesRegex(ValueError, "promoted"):
                    audit.audit_context_layers(self.rows, self.cites, self.archive, cart)
        cart = copy.deepcopy(self.cartography)
        cart["dependency_graph"][3]["to"] = "C197#1"
        with self.assertRaisesRegex(ValueError, "map context"):
            audit.audit_context_layers(self.rows, self.cites, self.archive, cart)


if __name__ == "__main__":
    unittest.main()
