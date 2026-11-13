"""Adversarial source/cross-identification checks on a non-orbital bridge."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_soviet_catalogue_bridge import HOLDINGS, CROSS, NASA, NASA1977, OUT, build, render


class SovietCatalogueBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = [json.loads((ROOT / p).read_text())
                       for p in (HOLDINGS, CROSS, NASA, NASA1977)]

    def mutate(self, index=None, edit=None):
        docs = copy.deepcopy(self.parents)
        if index is not None:
            edit(docs[index])
        return build(*docs, {})

    def test_valid_evidence_has_six_candidates_not_six_measurements(self):
        b = self.mutate()
        self.assertEqual(b["candidate_join_count"], 6)
        self.assertEqual(b["independent_observations"], 0)
        self.assertEqual(b["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(len(b["source_dependency_graph"]), 12)
        self.assertFalse(b["activation"])
        self.assertEqual([r["value"] for r in b["simulator_latent_parameters"]],
                         [None, None, None])

    def test_missing_original_facsimile_cannot_be_invented(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["candidate_joins"][0].update(
                original_soviet_issue_scan_sha256="f" * 64))

    def test_missing_sensor_epoch_cannot_be_invented(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["candidate_joins"][1].update(
                original_epoch_utc="1963-11-08T18:00:00Z"))

    def test_cross_id_cannot_be_promoted_from_catalogue(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["western_object_aliases"][1].update(
                western_crosswalk="CONFIRMED_PRIMARY_NASA_CATALOG_ONLY"))

    def test_527_not_a_528_measurement(self):
        with self.assertRaises(ValueError):
            self.mutate(2, lambda d: d["source_documents"][0]["row"].update(
                catalog_number_printed=528))

    def test_metadata_is_not_two_sensors(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["bibliographic_cross_checks"][0].update(
                independent_observation=True))

    def test_missing_catalogue_is_not_global_absence(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["bibliographic_cross_checks"][1].update(
                status="PROVED_NO_1963_SOVIET_RECORDS_EXIST"))

    def test_no_physical_activation(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["candidate_joins"][0].update(
                physical_constraint_active=True))

    def test_duplicate_join_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda d: d["candidate_joins"][0].update(
                target_norad=529))

    def test_1977_documentary_crosswalk_is_not_a_measurement(self):
        b = self.mutate()
        self.assertEqual([r["norad"] for r in b["primary_nasa_catalogue_identifications"]],
                         [527, 528, 529])
        self.assertEqual([r["source_id"] for r in b["primary_nasa_catalogue_identifications"]],
                         ["C241-L28", "C241-L32", "C241-L32"])
        self.assertEqual(b["primary_nasa_1977_source"]["decay_day_528"], "1963-11-08")
        self.assertIsNone(b["primary_nasa_1977_source"]["physical_reentry_time"])
        self.assertIsNone(b["primary_nasa_1977_source"]["physical_reentry_place"])
        self.assertEqual(len([x for x in b["source_dependency_graph"]
                              if x["type"].startswith("RETROSPECTIVE_NASA_")]), 2)

    def test_1977_catalogue_cannot_change_528_to_529(self):
        with self.assertRaises(ValueError):
            self.mutate(3, lambda d: d["row"].update(catalog_number_printed=529))

    def test_1977_control_cannot_fabricate_another_object(self):
        with self.assertRaises(ValueError):
            self.mutate(3, lambda d: d["control_rows"][1].update(catalog_number_printed=528))

    def test_1977_day_cannot_claim_exact_reentry_time(self):
        with self.assertRaises(ValueError):
            self.mutate(3, lambda d: d["row"].update(reentry_physical_time_utc="1963-11-08T23:59:00Z"))

    def test_1977_catalogue_cannot_claim_independent_sensor(self):
        with self.assertRaises(ValueError):
            self.mutate(3, lambda d: d["independence"].update(
                independent_528_instrumental_observations_added=1))

    def test_1977_unpinned_pdf_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(3, lambda d: d["source"].update(pdf_sha256="a" * 64))

    def test_stale_publication_and_typed_consumer(self):
        self.assertEqual(OUT.read_bytes(), render())
        lean = (ROOT / "formal/Conde1963/SovietCatalogueCandidate.lean").read_text()
        self.assertIn("C241-L29#1", lean)
        self.assertIn("C241-L29#2", lean)
        self.assertIn("C241-L28", lean)
        self.assertIn("C241-L32", lean)
        self.assertIn("nasaRetrospective1977Labels", lean)
        self.assertIn("none", lean)
        self.assertIn("import Conde1963.SovietCatalogueCandidate",
                      (ROOT / "formal/Conde1963.lean").read_text())
        self.assertLessEqual(OUT.stat().st_size, 20_000)


if __name__ == "__main__":
    unittest.main()
