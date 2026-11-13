"""Adversarial tests for documentary to hypothesis to latent-parameter bridges."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_contextual_scientific_bridges as bridge

class ScientificBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = bridge.build(ROOT)
        cls.by_id = {r["id"]: r for r in cls.data["records"]}

    def test_all_nine_links_remain_inactive(self):
        self.assertEqual(len(self.data["records"]), len(self.by_id))
        self.assertEqual(len(self.by_id), 9)
        self.assertEqual(len(self.data["source_feeds_sha256"]), 3)
        self.assertTrue(all(not r["activation"] and r["simulator_value"] is None
                            and r["independent_physical_observation_count"] is None
                            for r in self.data["records"]))
        self.assertEqual(self.data["epistemic_limits"]["activated_constraints"], 0)
        self.assertIsNone(self.data["epistemic_limits"]["verified_reentry_time"])
        self.assertEqual(self.data["matrix_git_blob_sha1"],
                         "a7978c3a75a153b16ab70118a92c434bba674cb7")

    def test_all_curated_citations_are_traced_without_activation(self):
        cov = self.data["citation_coverage"]
        counts = self.data["citation_coverage_counts"]
        self.assertEqual((counts["curated_edges"], counts["curated_occurrences"],
                          counts["unmapped_occurrences"]), (29, 28, 213))
        self.assertEqual(counts["explicit_documentary_bridges"], 3)
        self.assertEqual(counts["documentary_edges_not_assessed_for_lean"], 26)
        self.assertEqual(len({(x["occurrence_ref"], x["source_id"]) for x in cov}), 29)
        self.assertEqual(len({x["occurrence_ref"] for x in cov}), 28)
        self.assertTrue(all(x["activation"] is False and x.get("simulator_value") is None
                            and x["row_sha256"] and x["matrix_line"] > 0 for x in cov))
        unmapped = [x for x in cov if x["bridge_record_id"] is None]
        self.assertEqual(len(unmapped), 26)
        self.assertTrue(all(x["hypothesis_link"] is None
                            and x["simulator_parameter"] is None
                            and x["lean_status"] == "DOCUMENTARY_ONLY_NOT_ASSESSED"
                            for x in unmapped))

    def test_c232_dual_custody_citation_is_one_occurrence_not_two_measurements(self):
        cov = [x for x in self.data["citation_coverage"]
               if x["occurrence_ref"].endswith(":C232#1")]
        self.assertEqual({x["source_id"] for x in cov},
                         {"BLUEBOOK_CASES_INDEX_1963", "NARA_BB_CARD_302531013"})
        self.assertEqual(len({x["row_sha256"] for x in cov}), 1)
        self.assertEqual({x["bridge_record_id"] for x in cov}, {None})

    def test_coverage_joins_only_exact_documentary_citations(self):
        documentary = bridge.depend.build(ROOT)
        actual = {(x["occurrence_ref"], x["source_id"]): x
                  for x in self.data["citation_coverage"]}
        expected = {(x["snapshot_ref"], x["source_id"]): x
                    for x in documentary["citation_lineages"]}
        self.assertEqual(set(actual), set(expected))
        for key, item in expected.items():
            self.assertEqual(actual[key]["row_sha256"], item["row_sha256"])
            self.assertEqual(actual[key]["matrix_line"], item["matrix_line"])
            self.assertEqual(actual[key]["source_family"], item["family_id"])

    def test_nasa_and_catalogue_are_one_work_not_two_sensor_reads(self):
        pair = [self.by_id["NASA_DAY_C197_1"], self.by_id["NASA_DAY_C198_1"]]
        self.assertEqual(pair[0]["shared_work_id"], pair[1]["shared_work_id"])
        self.assertEqual(pair[0]["source_family"], pair[1]["source_family"])
        self.assertEqual({x["simulator_parameter"] for x in pair},
                         {"reentry_terminal_timestamp_528"})
        self.assertTrue(all(x["lean_status"] == "DAY_ONLY_PREMISE_NO_TERMINAL_TIME"
                            for x in pair))
        self.assertNotEqual(pair[0]["row_sha256"], pair[1]["row_sha256"])

    def test_fbis_tupi_and_external_norad_are_not_measurements(self):
        radio = self.by_id["REPORT_TUPI_FBIS_C01"]
        self.assertEqual(radio["upstream_source_ids"], ["RADIO_TUPI_19631108"])
        self.assertIsNone(radio["simulator_parameter"])
        nor = [self.by_id[f"MOR-NOR-20261112-0{x}"] for x in range(1, 6)]
        self.assertEqual({x["source_id"] for x in nor},
                         {"MOR-NORAD-1961-AGREEMENT", "MOR-NORAD-1963-NOV12",
                          "MOR-NORAD-1963-NOV14", "MOR-NORAD-1964-NOV30-09",
                          "MOR-NORAD-1964-NOV30-10"})
        self.assertEqual(nor[-1]["source_date"], "1964-11-30")
        self.assertEqual(nor[-1]["catalogue_date_claim"], "1963-11-30")
        self.assertTrue(all(528 not in x["objects_in_document"] for x in nor))

    def test_cgeo10_preserves_missing_originals(self):
        x = self.by_id["CGEO10_1963_BOUNDARY_LATENT"]
        self.assertTrue(x["occurrence_ref"].startswith("CGEO-10:"))
        self.assertEqual(x["lean_status"], "NOT_PROMOTED")
        self.assertEqual(len(x["required_bridges"]), 4)
        self.assertEqual(x["simulator_parameter"],
                         "sim_param_legal_boundary_Conde_BA_1963")

    def test_historical_nmc_manual_is_separate_conditional_bridge(self):
        links = self.data["supplementary_links"]
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["id"], "C241-L14-NMC-ON20-LAYOUT")
        path = ROOT / links[0]["path"]
        import hashlib
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), links[0]["sha256"])
        link = json.loads(path.read_text())
        self.assertEqual(link["manual_publication_year"], 1964)
        self.assertIsNone(link["validated_1963_layout_reference"])
        self.assertIsNone(link["decoded_station_day_matches"])
        self.assertEqual(link["tape_source_id"], "MET-NMC-20261112-09")
        self.assertFalse(link["active_physical_constraint"])

    def test_export_matches_byte_for_byte(self):
        raw = (ROOT / bridge.OUTPUT).read_bytes()
        self.assertEqual(raw, bridge.serialize(self.data).encode())
        self.assertLessEqual(len(raw), 20_000)

    def test_tampered_source_feed_rejected_even_if_still_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "public/data"
            target.mkdir(parents=True)
            for path, _ in bridge.INPUTS:
                (root / path).write_bytes((ROOT / path).read_bytes())
            (root / bridge.on20.OUTPUT).write_bytes((ROOT / bridge.on20.OUTPUT).read_bytes())
            (root / "public/data/conde-source-citations.json").write_bytes(
                (ROOT / "public/data/conde-source-citations.json").read_bytes())
            (root / "research").symlink_to(ROOT / "research", target_is_directory=True)
            (root / "formal").symlink_to(ROOT / "formal", target_is_directory=True)
            bad_path = root / "public/data/conde-norad-context.json"
            bad = json.loads(bad_path.read_text())
            bad["records"][-1]["source_date"] = "1963-11-30"
            bad_path.write_text(bridge.serialize(bad))
            with self.assertRaisesRegex(ValueError, "stale/tampered source feed"):
                bridge.build(root)

    def _mutate_input(self, path_suffix, edit):
        # Mock the source builder and accompanying published JSON to force
        # the semantic guard, not merely the feed-content hash, to run.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.joinpath("public/data").mkdir(parents=True)
            root.joinpath("research").symlink_to(ROOT / "research", target_is_directory=True)
            root.joinpath("formal").symlink_to(ROOT / "formal", target_is_directory=True)
            (root / bridge.on20.OUTPUT).write_bytes((ROOT / bridge.on20.OUTPUT).read_bytes())
            inputs = []
            for path, builder in bridge.INPUTS:
                data = copy.deepcopy(builder(ROOT))
                if path.endswith(path_suffix):
                    edit(data)
                (root / path).write_text(bridge.serialize(data))
                inputs.append((path, lambda ignored, v=data: v))
            with mock.patch.object(bridge, "INPUTS", tuple(inputs)):
                return bridge.build(root)

    def test_1964_original_relabelled_as_1963_rejected(self):
        with self.assertRaisesRegex(ValueError, "misdated 1964 original"):
            self._mutate_input("conde-norad-context.json",
                               lambda d: d["records"][-1].update(
                                   source_date="1963-11-30"))

    def test_norad_528_object_injection_rejected(self):
        with self.assertRaisesRegex(ValueError, "false 528 observation"):
            self._mutate_input("conde-norad-context.json",
                               lambda d: d["records"][1].update(
                                   object_ids_reported_in_this_document=[528]))

    def test_cgeo_boundary_activation_without_originals_rejected(self):
        with self.assertRaisesRegex(ValueError, "proxy promoted"):
            self._mutate_input("conde-cgeo10-provenance.json",
                               lambda d: d["constraint_candidate"].update(
                                   activation=True))

    def test_nasa_ntrs_duplicate_work_injection_rejected(self):
        with self.assertRaisesRegex(ValueError, "work treated as independent"):
            self._mutate_input("conde-declared-dependence.json",
                               lambda d: next(x for x in d["citation_lineages"]
                               if x["source_id"] == "NTRS_19640001198").update(
                                   independent_physical_observation_count=2))

if __name__ == "__main__":
    unittest.main()
