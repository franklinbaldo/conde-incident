"""Companion export regressions: lineage without double-counted witnesses."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_documentary_dependence as depend
import provenance_graph as pg


class DocumentaryDependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = depend.build()
        cls.canonical = json.loads(pg.SITE.read_text())
        cls.by_citation = {
            (item["snapshot_ref"], item["source_id"]): item
            for item in cls.payload["citation_lineages"]
        }

    def test_every_companion_link_has_exact_canonical_citation(self):
        ids = {(r["snapshot_ref"], r["source_id"])
               for r in self.canonical["records"]}
        self.assertEqual(set(self.by_citation), ids)
        self.assertEqual(len(self.by_citation), 29)
        self.assertEqual(self.payload["curated_occurrences"], 28)
        self.assertEqual(self.payload["unmapped_occurrences"], 213)
        self.assertEqual(self.payload["matrix_snapshot_id"], pg.MATRIX_SNAPSHOT_ID)

    def test_lineage_row_hash_and_line_match_pinned_matrix_and_canonical(self):
        matrix = {r["snapshot_ref"]: r for r in
                  pg.matrix_occurrences(pg.MATRIX.read_bytes())}
        self.assertEqual(len(self.by_citation), 29)
        for item in self.canonical["records"]:
            key = (item["snapshot_ref"], item["source_id"])
            exported = self.by_citation[key]
            pinned = matrix[item["snapshot_ref"]]
            self.assertEqual(
                (exported["matrix_line"], exported["row_sha256"]),
                (pinned["matrix_line"], pinned["row_sha256"]))
            self.assertEqual(
                (exported["matrix_line"], exported["row_sha256"]),
                (item["matrix_line"], item["row_sha256"]))

    def test_c232_two_distinct_citations_keep_same_row_identity(self):
        ref = pg.matrix_ref("C232#1")
        rows = [r for r in self.payload["citation_lineages"]
                if r["snapshot_ref"] == ref]
        self.assertEqual({r["source_id"] for r in rows},
                         {"BLUEBOOK_CASES_INDEX_1963", "NARA_BB_CARD_302531013"})
        self.assertEqual(len({(r["matrix_line"], r["row_sha256"])
                              for r in rows}), 1)
        self.assertEqual(len({r["source_id"] for r in rows}), 2)
        self.assertTrue(all(r["independent_physical_observation_count"] is None
                            for r in rows))

    def test_contract_rows_are_addressed_even_when_uncurated(self):
        matrix = {r["snapshot_ref"]: r for r in
                  pg.matrix_occurrences(pg.MATRIX.read_bytes())}
        for contract in self.payload["contract_citation_crosswalk"]:
            for row in contract["occurrences"]:
                pinned = matrix[row["snapshot_ref"]]
                self.assertEqual(
                    (row["matrix_line"], row["row_sha256"]),
                    (pinned["matrix_line"], pinned["row_sha256"]))
                self.assertIn(row["citation_status"],
                              {"CURATED", "UNMAPPED_NOT_CLEARED"})
                self.assertIsNone(row["independent_physical_observation_count"])

    def test_mutated_row_hash_in_canonical_feed_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "research").symlink_to(ROOT / "research", target_is_directory=True)
            (root / "formal").symlink_to(ROOT / "formal", target_is_directory=True)
            out = root / "public/data"
            out.mkdir(parents=True)
            bad = json.loads(pg.SITE.read_text())
            bad["records"][0]["row_sha256"] = "0" * 64
            (out / "conde-source-citations.json").write_text(
                pg.serialize(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError,
                                        "canonical citation feed out of sync"):
                depend.build(root)

    def test_fbis_is_a_transcription_not_second_radio_witness(self):
        row = self.by_citation[pg.matrix_ref("C01#1"), "FBIS_EOP_UAP_D001"]
        self.assertEqual(row["family_id"], "RADIO_TUPI_FBIS")
        self.assertEqual(row["declared_upstream_paths"], [{
            "upstream_source_id": "RADIO_TUPI_19631108",
            "edges": [{
                "from": "FBIS_EOP_UAP_D001",
                "to": "RADIO_TUPI_19631108",
                "kind": "transcribes",
            }]
        }])
        self.assertIsNone(row["independent_physical_observation_count"])

    def test_ntrs_catalogue_and_nasa_report_share_a_work(self):
        ntrs = self.by_citation[pg.matrix_ref("C198#1"), "NTRS_19640001198"]
        nasa = self.by_citation[pg.matrix_ref("C197#1"), "NASA_SSR_19631115"]
        self.assertEqual(ntrs["family_id"], nasa["family_id"])
        self.assertEqual(ntrs["declared_upstream_paths"][0]["upstream_source_id"],
                         "NASA_SSR_19631115")
        self.assertEqual(ntrs["declared_upstream_paths"][0]["edges"][0]["kind"],
                         "catalogue_of_same_work")
        self.assertEqual(nasa["declared_upstream_paths"], [])
        self.assertTrue(self.payload["epistemic_limits"][
            "absence_of_edge_does_not_prove_independence"])

    def test_celestrak_aggregates_two_series_no_third_independent_sensor(self):
        item = self.by_citation[pg.matrix_ref("C23#1"), "CELESTRAK_SPACE_WEATHER"]
        self.assertEqual({
            x["upstream_source_id"] for x in item["declared_upstream_paths"]
        }, {"GFZ_KP_AP_SERIES", "NRC_F107_SERIES"})
        self.assertEqual(len(item["declared_upstream_paths"]), 2)
        self.assertIsNone(item["independent_physical_observation_count"])

    def test_transitive_paths_preserve_exact_declared_edges(self):
        edges = [
            {"from": "TRANSCRIPT", "to": "QUOTE", "kind": "transcribes"},
            {"from": "QUOTE", "to": "UNREAD", "kind": "quotes_uninspected_source"},
        ]
        paths = depend.declared_paths("TRANSCRIPT", edges)
        self.assertEqual(
            [path["upstream_source_id"] for path in paths],
            ["QUOTE", "UNREAD"])
        self.assertEqual([e["kind"] for e in paths[1]["edges"]],
                         ["transcribes", "quotes_uninspected_source"])
        self.assertEqual(depend.declared_paths("UNREAD", edges), [])

    def test_family_rollup_is_citation_count_not_observation_count(self):
        grouped = self.payload["independence_groups"]
        self.assertEqual(sum(x["citation_edges"] for x in grouped), 29)
        nasa = next(x for x in grouped if x["family_id"] == "NORAD_NASA_TRACKING")
        self.assertEqual(nasa["cited_work_ids"].count("NASA_SSR_VOL3_22"), 1)
        self.assertIn("NASA_SSR_19631115", nasa["cited_source_ids"])
        self.assertIn("NTRS_19640001198", nasa["cited_source_ids"])
        radio = next(x for x in grouped if x["family_id"] == "RADIO_TUPI_FBIS")
        self.assertEqual(radio["citation_edges"], 3)
        self.assertIsNone(radio["independent_physical_observation_count"])
        self.assertIsNone(self.payload["epistemic_limits"][
            "independent_physical_observation_count"])

    def test_contract_crosswalk_uses_snapshot_qualified_occurrence(self):
        bridges = {x["contract_id"]: x
                   for x in self.payload["contract_citation_crosswalk"]}
        bridge = bridges["C179_C151_BRIDGE"]
        self.assertEqual(bridge["contract_status"], "DERIVED_ONLY_NO_CONDE_TRANSFER")
        self.assertEqual(
            [x["snapshot_ref"] for x in bridge["occurrences"]],
            [pg.matrix_ref("C179#1"), pg.matrix_ref("C151#1")])
        self.assertEqual(bridge["occurrences"][0]["cited_source_ids"],
                         ["AFSPC_MIRROR_528"])
        self.assertEqual(bridge["occurrences"][0]["declared_upstream_source_ids"], [])
        self.assertIsNone(bridge["occurrences"][0][
            "independent_physical_observation_count"])

    def test_nara_quote_is_uninspected_document_not_field_report(self):
        addenda = self.payload["post_matrix_lineages"]
        self.assertEqual(len(addenda), 1)
        item = addenda[0]
        self.assertEqual(item["id"], "NARA-BB-CONDE-20261112-01")
        self.assertIn("O_GLOBO_19631108_UNINSPECTED",
                      {p["upstream_source_id"] for p in item["declared_upstream_paths"]})
        self.assertIsNone(item["independent_physical_observation_count"])
        self.assertIsNone(self.payload["epistemic_limits"]["verified_reentry_place"])
        self.assertIsNone(self.payload["epistemic_limits"]["verified_reentry_time"])

    def test_companion_feed_is_byte_deterministic_and_bounded(self):
        expected = json.dumps(self.payload, ensure_ascii=False, sort_keys=True,
                              separators=(",", ":")) + "\n"
        self.assertEqual(expected, depend.OUTPUT.read_text())
        self.assertLessEqual(len(expected.encode()), 20_000)


if __name__ == "__main__":
    unittest.main()
