"""C241-P28 scientific source-link status, with explicit negative controls."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_matrix_link_status as status
import provenance_graph as pg


class MatrixLinkStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pg.matrix_occurrences(pg.MATRIX.read_bytes())
        cls.cites = json.loads(status.coverage.CITATIONS.read_bytes())
        cls.bridges = json.loads(status.coverage.OBSERVABLES.read_bytes())
        cls.curated = {r["occurrence"] for r in cls.cites["records"]}
        cls.gaps = {r["occurrence"] for r in cls.rows} - cls.curated

    def analyze(self, rows=None, cites=None, bridges=None, curated=None, gaps=None):
        return status.classify(
            self.rows if rows is None else rows,
            self.cites if cites is None else cites,
            self.bridges if bridges is None else bridges,
            self.curated if curated is None else curated,
            self.gaps if gaps is None else gaps,
        )

    def test_rebuild_241_frozen_occurrences_and_exact_published_bytes(self):
        result = status.rebuild()
        self.assertEqual(result["matrix_occurrences"], 241)
        self.assertEqual(result["index_curated_occurrences"], 28)
        self.assertEqual(result["index_uncurated_occurrences"], 213)
        self.assertEqual(result["reconciled_direct_links"], 30)
        self.assertEqual(result["scientific_links_in_index_uncurated"],
                         ["C227#1", "C228#1"])
        self.assertEqual(status.OUTPUT.read_bytes(), status.encode(result))
        self.assertEqual(result["epistemic_limits"]["physical_domain_effect"],
                         "THETA_UNCHANGED")

    def test_all_occurrences_in_exactly_one_tier(self):
        result = self.analyze()
        tiers = result["categories"]
        all_ids = sum(tiers.values(), [])
        self.assertEqual(set(all_ids), {r["occurrence"] for r in self.rows})
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(result["counts"], dict(zip(status.STATES, [2, 26, 2, 211])))
        self.assertIn("C44#2", tiers[status.STATES[3]])
        self.assertIn("C179#1", tiers[status.STATES[0]])

    def test_non_canonical_indexed_claim_is_not_a_curated_citation(self):
        result = self.analyze()
        self.assertIn("C227#1", self.gaps)
        self.assertIn("C228#1", self.gaps)
        self.assertNotIn("C227#1", result["categories"][status.STATES[1]])
        self.assertEqual(result["epistemic_limits"]["new_instrumental_observations"], 0)

    def test_wrong_index_curated_status_rejected(self):
        for target in ("C227#1", "C228#1", "C44#2"):
            with self.subTest(target=target):
                curated = self.curated | {target}
                gaps = self.gaps - {target}
                with self.assertRaisesRegex(ValueError, "SSG curated/gap"):
                    self.analyze(curated=curated, gaps=gaps)

    def test_missing_or_extra_index_occurrence_rejected(self):
        with self.assertRaisesRegex(ValueError, "SSG curated/gap|silently dropped"):
            self.analyze(gaps=self.gaps - {"C44#2"})
        with self.assertRaisesRegex(ValueError, "SSG.*index"):
            self.analyze(gaps=self.gaps | {"C239#1"})

    def test_duplicate_index_status_rejected(self):
        with self.assertRaisesRegex(ValueError, "SSG curated/gap"):
            self.analyze(gaps=self.gaps | {"C197#1"})

    def test_snapshot_qualified_bridge_required(self):
        changed = copy.deepcopy(self.bridges)
        changed["edges"][0]["matrix_occurrence"] = "C179#1"
        with self.assertRaisesRegex(ValueError, "unsnapshotted"):
            self.analyze(bridges=changed)

    def test_no_legacy_id_collision(self):
        changed = copy.deepcopy(self.rows)
        changed[-1]["snapshot_ref"] = changed[0]["snapshot_ref"]
        with self.assertRaisesRegex(ValueError, "matrix cardinality"):
            self.analyze(rows=changed)

    def test_forged_sensor_activation_rejected(self):
        for k, v in (("activation", True),
                     ("independent_sensor", True),
                     ("instrument_epoch_utc", "1963-12-31T12:00:00Z"),
                     ("instrument_covariance", [[1]]),
                     ("physical_domain_effect", "THETA_REDUCED")):
            with self.subTest(k=k):
                changed = copy.deepcopy(self.bridges)
                changed["pending_december_compilation_edges"][0][k] = v
                with self.assertRaisesRegex(ValueError, "promoted|activated"):
                    self.analyze(bridges=changed)

    def test_forged_documentary_context_not_promoted(self):
        changed = copy.deepcopy(self.bridges)
        changed["pending_documentary_edges"] = [
            {"matrix_context": "C44#2", "activation": False} for _ in range(50)]
        self.assertEqual(self.analyze(bridges=changed)["categories"],
                         self.analyze()["categories"])

    def test_compiled_report_remains_below_file_size_policy(self):
        self.assertLess(len(status.encode(self.analyze())), 20_000)
        self.assertFalse(self.analyze()["epistemic_limits"].get(
            "claim_reentry_in_conde", False))


if __name__ == "__main__":
    unittest.main()
