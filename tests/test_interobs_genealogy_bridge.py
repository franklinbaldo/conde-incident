"""Reject source mutation or promotion of INTEROBS aggregate context to 528 observations."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_interobs_genealogy_bridge import SOURCES, OUTPUT, build, render


class InterobsGenealogyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {k: json.loads((ROOT / path).read_bytes()) for k, (path, _) in SOURCES.items()}

    def mutate(self, key, section, name, value):
        s = copy.deepcopy(self.sources)
        s[key][section][name] = value
        with self.assertRaises(ValueError):
            build(s)

    def test_replay_and_inactive_contract(self):
        self.assertEqual(render(), OUTPUT.read_bytes())
        d = json.loads(render())
        self.assertEqual(d["approximate_interobs_positions_1963_all_objects"], 600)
        self.assertIsNone(d["matrix_occurrence"])
        self.assertEqual(len(d["dependency_graph"]), 9)
        self.assertEqual(len(d["simulator_latent_parameters"]), 18)
        self.assertFalse(d["activation"])
        self.assertEqual(d["independent_target_observations_added"], 0)
        self.assertEqual(d["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(d["source_custody"][3]["source_sha256"], None)
        self.assertTrue(all(not e["activation"] for e in d["dependency_graph"]))
        self.assertTrue(all(p["value"] is None and not p["activation"] for p in d["simulator_latent_parameters"]))

    def test_reject_source_cross_object_transfer(self):
        self.mutate("C241-LONTRA-R38", "study", "object_is_1963_003_abc", True)
        self.mutate("C241-LONTRA-R38", "study", "campaign_includes_1963_nov_07_to_09", True)
        self.mutate("C241-LONTRA-R38", "study", "fixes_total_in_table_2", 600)

    def test_reject_invented_target_campaign(self):
        self.mutate("C241-LONTRA-R39", "report", "campaign_coverage_1963_11_07_to_09", True)
        self.mutate("C241-LONTRA-R39", "report", "listed_satellite_codes_proven_to_be_527_528_529", True)
        self.mutate("C241-LONTRA-R40", "preface", "actual_list_1_or_list_2_retrieved", True)
        self.mutate("C241-LONTRA-R41", "scope", "target_observations_identified", True)
        self.mutate("C241-LONTRA-R41", "scope", "target_specific_1963_11_07_to_09_campaign_confirmed", True)

    def test_reject_wrong_dates_and_unverified_pdf_digest(self):
        self.mutate("C241-LONTRA-R39", "source", "cover_year", 1965)
        self.mutate("C241-LONTRA-R40", "source", "covered_observation_year", 1963)
        self.mutate("C241-LONTRA-R41", "document", "translation_date", "1967-01-01")
        self.mutate("C241-LONTRA-R41", "access", "full_pdf_sha256", "0" * 64)
        self.mutate("C241-LONTRA-R41", "report", "positions_are_approximate", False)

    def test_manifest_sha_and_output_guards(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for path, _ in SOURCES.values():
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            self.assertEqual(render(root), render())
            path = root / SOURCES["C241-LONTRA-R41"][0]
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                render(root)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for path, _ in SOURCES.values():
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            self.assertEqual(build(self.sources), json.loads(render(root)))


if __name__ == "__main__":
    unittest.main()
