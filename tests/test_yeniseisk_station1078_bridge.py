"""Mutation tests for C241-L38 -> dependency graph -> typed pending candidate."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_yeniseisk_station1078_bridge import SOURCE, PARENT, OUT, build, render


class Station1078BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
        cls.parent = json.loads((ROOT / PARENT).read_text(encoding="utf-8"))

    def mutant(self, idx, mutate):
        documents = [copy.deepcopy(self.source), copy.deepcopy(self.parent)]
        mutate(documents[idx])
        with self.assertRaises(ValueError):
            build(*documents, {})

    def test_cumulative_paths_and_no_premature_fit(self):
        data = build(self.source, self.parent, {})
        self.assertEqual(len(data["dependency_graph"]), 11)
        self.assertEqual([p["norad"] for p in data["simulator_latent_parameters"]],
                         [527, 528, 529])
        self.assertEqual(data["source_occurrence"], "C241-L38")
        self.assertEqual(data["source_independence"]["relation_to_parent_soviet_publication"],
                         "UNDETERMINED")
        self.assertFalse(data["source"]["transport_tls_authenticated"])
        self.assertFalse(data["source"]["november_1963_journal_confirmed"])
        self.assertFalse(data["activation"])
        self.assertEqual(data["new_numeric_orbital_constraints"], 0)
        self.assertEqual(data["physical_domain_effect"], "THETA_UNCHANGED")
        for p in data["simulator_latent_parameters"]:
            self.assertIsNone(p["value"])
            self.assertIsNone(p["station_position_1963"])
            self.assertIsNone(p["observation_epoch_utc"])
            self.assertIsNone(p["observed_direction"])
            self.assertIsNone(p["instrument_sigma"])
            self.assertFalse(p["activation"])

    def test_mutant_fabricated_november_journals(self):
        self.mutant(0, lambda d: d["institutional_history"].update(journal_november_1963_confirmed=True))

    def test_mutant_present_day_custodian(self):
        self.mutant(0, lambda d: d["institutional_history"].update(present_day_holding_confirmed=True))

    def test_mutant_original_instrumental_facsimile(self):
        self.mutant(0, lambda d: d["institutional_history"].update(source_original_observation_facsimile=True))

    def test_mutant_fake_tls_authenticity(self):
        self.mutant(0, lambda d: d["retrieved_transport_copy"].update(tls_certificate_validated=True))

    def test_mutant_fake_target(self):
        self.mutant(0, lambda d: d["route"].update(target_objects_explicitly_identified=True))

    def test_mutant_fake_coordinates(self):
        self.mutant(0, lambda d: d["route"].update(station_coordinates_confirmed_for_1963=True))

    def test_mutant_fabricated_independent_observations(self):
        self.mutant(0, lambda d: d.update(independent_target_measurements=1))

    def test_mutant_moved_epoch(self):
        self.mutant(0, lambda d: d["route"].update(candidate_observation_dates=["1963-11-08"]))

    def test_mutant_source_digest(self):
        self.mutant(0, lambda d: d["retrieved_transport_copy"].update(sha256="a" * 64))

    def test_mutant_parent_activated(self):
        self.mutant(1, lambda d: d["simulator_latent_parameters"][0].update(value="observed"))

    def test_mutant_parent_wrong_identity(self):
        self.mutant(1, lambda d: d.update(source_occurrence="C241-L99"))

    def test_exact_export_parent_sha_and_lean_declaration(self):
        result = render()
        data = json.loads(result)
        self.assertEqual(result, OUT.read_bytes())
        self.assertEqual(data["parent_sha256"][str(SOURCE)],
                         hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest())
        self.assertEqual(data["parent_sha256"][str(PARENT)],
                         hashlib.sha256((ROOT / PARENT).read_bytes()).hexdigest())
        lean = (ROOT / "formal/Conde1963/SovietCatalogueCandidate.lean").read_text()
        self.assertIn("def sovietStation1078JournalRoutes", lean)
        self.assertIn('sourceOccurrence := "C241-L38"', lean)
        self.assertLess(len(result), 20_000)


if __name__ == "__main__":
    unittest.main()
