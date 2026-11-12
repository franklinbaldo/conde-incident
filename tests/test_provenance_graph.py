"""Documentary provenance regressions; no network or historical event claims."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import provenance_graph as pg


class DocumentaryProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(pg.LINEAGES.read_text())
        cls.raw = pg.MATRIX.read_bytes()
        cls.graph, cls.citations = pg.build(cls.config, cls.raw)

    def test_matrix_occurrences_preserved_exactly_including_collisions(self):
        self.assertEqual(len(self.graph["matrix_occurrences"]), 241)
        self.assertEqual(len({r["label"] for r in self.graph["matrix_occurrences"]}), 238)
        for id_ in ("C44", "C45", "C46"):
            matching = [r for r in self.graph["matrix_occurrences"] if r["label"] == id_]
            self.assertEqual([r["index"] for r in matching], [1, 2])
            self.assertNotEqual(matching[0]["row_sha256"], matching[1]["row_sha256"])
            self.assertNotEqual(matching[0]["claim_text"], matching[1]["claim_text"])
            self.assertEqual([r["citation_status"] for r in matching],
                             ["UNMAPPED_NOT_CLEARED", "UNMAPPED_NOT_CLEARED"])

    def test_nara_bluebook_addendum_is_linked_without_rewriting_frozen_matrix(self):
        updates = self.graph["post_matrix_occurrences"]
        self.assertEqual(len(updates), 1)
        rec = updates[0]
        self.assertEqual(rec["id"], "NARA-BB-CONDE-20261112-01")
        self.assertEqual(rec["related_matrix_snapshot_refs"], [
            pg.matrix_ref(occ) for occ in rec["related_matrix_occurrences"]])
        self.assertEqual(rec["nara_fileunit_naid"], 302531012)
        self.assertEqual(rec["nara_object_id"], 302531014)
        self.assertEqual(rec["image_filename"], "0810.jp2")
        self.assertEqual(rec["image_sha256"],
                         "136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9")
        self.assertEqual(rec["telegram_date"], "1963-11-14")
        self.assertEqual(rec["reported_newspaper_date"], "1963-11-08")
        self.assertIsNone(rec["newspaper_page"])
        self.assertIsNone(rec["newspaper_publication_time"])
        self.assertEqual(rec["journalistic_source_independence"], "UNRESOLVED")
        self.assertIsNone(rec["physical_constraint"])
        self.assertEqual(rec["status"], "CONNECTED_PENDING_DOCUMENTARY_VERIFICATION")
        self.assertTrue({"C232#1", "C238#1", "C01#1", "C03#1"} <=
                        set(rec["related_matrix_occurrences"]))
        deps = {(e["from"], e["to"], e["kind"])
                for e in self.graph["source_dependencies"]}
        self.assertIn(("NARA_AIRA_TELEGRAM_19631114",
                       "O_GLOBO_19631108_UNINSPECTED",
                       "quotes_uninspected_source"), deps)
        self.assertEqual(len(self.graph["matrix_occurrences"]), 241)
        self.assertEqual(len(self.citations["records"]), 29)

    def test_nara_addendum_rejects_duplicate_orphan_and_unverified_claim(self):
        for mutation in ("duplicate", "unknown_matrix", "missing_source",
                         "invented_page", "invented_independence", "bad_checksum"):
            config = copy.deepcopy(self.config)
            row = config["post_matrix_occurrences"][0]
            if mutation == "duplicate":
                config["post_matrix_occurrences"].append(copy.deepcopy(row))
            elif mutation == "unknown_matrix":
                row["related_matrix_occurrences"].append("C999#1")
            elif mutation == "missing_source":
                row["source_id"] = "UNINDEXED_NEW_DOCUMENT"
            elif mutation == "invented_page":
                row["newspaper_page"] = 2
            elif mutation == "invented_independence":
                row["journalistic_source_independence"] = "INDEPENDENT"
            else:
                row["image_sha256"] = "unknown"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                pg.build(config, self.raw)

    def test_later_merges_cannot_silently_erase_nara_ledger(self):
        config = copy.deepcopy(self.config)
        config.pop("post_matrix_occurrences")
        with self.assertRaisesRegex(ValueError, "required cumulative"):
            pg.build(config, self.raw)
        config = copy.deepcopy(self.config)
        config["post_matrix_occurrences"] = []
        with self.assertRaisesRegex(ValueError, "required cumulative"):
            pg.build(config, self.raw)

    def test_post_matrix_source_image_crosswalk_rejects_well_formed_wrong_ids(self):
        # Valid-looking alternatives previously passed format checks and appeared
        # on the site as an incorrectly attributed NARA scan.
        cases = {
            "another_valid_sha256": ("image_sha256", "0" * 64),
            "another_nara_object": ("nara_object_id", 302531015),
            "another_nara_unit": ("nara_fileunit_naid", 302531011),
            "another_image_name": ("image_filename", "0811.jp2"),
            "existing_but_wrong_report": ("report_path", "AGENTS.md"),
        }
        for label, (field, altered) in cases.items():
            with self.subTest(label=label):
                config = copy.deepcopy(self.config)
                config["post_matrix_occurrences"][0][field] = altered
                with self.assertRaisesRegex(ValueError, "source/image/custody crosswalk mismatch"):
                    pg.build(config, self.raw)

    def test_unreviewed_physical_sounding_citation_scopes_are_rejected(self):
        for label in ("OBSERVED_CONDE_CRATER", "CONFIRMED_TERMINAL_POSITION",
                      "PRIMARY_FIELD_SIGHTING"):
            with self.subTest(scope=label):
                config = copy.deepcopy(self.config)
                config["citations"][0]["scope"] = label
                with self.assertRaisesRegex(ValueError, "scope not approved"):
                    pg.build(config, self.raw)

    def test_citation_scope_must_match_its_documentary_relation(self):
        config = copy.deepcopy(self.config)
        config["citations"][0]["scope"] = "CATALOGUED_DAY_ONLY"
        with self.assertRaisesRegex(ValueError, "scope not approved"):
            pg.build(config, self.raw)

    def test_real_mapping_coverage_is_not_inflated_by_unmapped_default_dict(self):
        self.assertEqual(self.citations["curated_occurrences"], 28)
        self.assertEqual(self.citations["unmapped_occurrences"], 213)
        self.assertEqual(len(self.citations["records"]), 29)
        self.assertEqual(self.graph["citation_summary"]["curated_occurrences"], 28)
        self.assertEqual(self.graph["citation_summary"]["unmapped_occurrences"], 213)

    def test_every_citation_resolves_source_and_exact_matrix_line_and_hash(self):
        src = {s["id"] for s in self.graph["sources"]}
        by_occ = {r["occurrence"]: r for r in self.graph["matrix_occurrences"]}
        matrix_lines = self.raw.decode().splitlines()
        for c in self.citations["records"]:
            self.assertIn(c["source_id"], src)
            row = by_occ[c["occurrence"]]
            self.assertEqual(c["matrix_line"], row["matrix_line"])
            self.assertEqual(hashlib.sha256(
                matrix_lines[c["matrix_line"] - 1].encode().strip(b"\n")
            ).hexdigest(), c["row_sha256"])
            self.assertTrue(c["not_a_verified_conde_physical_event"])
        self.assertEqual({c["occurrence"] for c in self.citations["records"]},
                         {r["occurrence"] for r in by_occ.values()
                          if r["citation_status"] == "CURATED"})

    def test_lineage_fbis_and_nasa_cannot_be_counted_as_independent_sensors(self):
        src = {s["id"]: s for s in self.config["sources"]}
        for sid in ("RADIO_TUPI_19631108", "FBIS_EOP_UAP_D001"):
            self.assertEqual(src[sid]["family"], "RADIO_TUPI_FBIS")
        for sid in ("NASA_SSR_19631115", "NTRS_19640001198",
                    "NASA_SSR_19631130", "AFSPC_MIRROR_528"):
            self.assertEqual(src[sid]["family"], "NORAD_NASA_TRACKING")
        self.assertEqual(src["NASA_SSR_19631115"]["work_id"],
                         src["NTRS_19640001198"]["work_id"])
        edges = {(e["from"], e["to"], e["kind"]) for e in self.config["dependencies"]}
        self.assertIn(("FBIS_EOP_UAP_D001", "RADIO_TUPI_19631108", "transcribes"), edges)
        self.assertIn(("NTRS_19640001198", "NASA_SSR_19631115",
                       "catalogue_of_same_work"), edges)
        self.assertIsNone(self.graph["limits"]["independent_physical_tracking_count"])

    def test_nasa_date_record_is_day_only_and_not_geolocated(self):
        day = [x for x in self.citations["records"] if x["occurrence"] == "C197#1"]
        self.assertEqual(len(day), 1)
        self.assertEqual(day[0]["relation"], "catalogued_day")
        self.assertEqual(day[0]["source_id"], "NASA_SSR_19631115")
        self.assertEqual(day[0]["scope"], "CATALOGUED_DAY_ONLY")
        self.assertIsNone(self.graph["limits"]["verified_reentry_time_utc"])
        self.assertIsNone(self.graph["limits"]["verified_reentry_location"])
        self.assertFalse(self.graph["limits"]["verified_Conde_impact"])

    def test_environment_archive_and_repackaging_not_528_measurement(self):
        references = {c["occurrence"]: c for c in self.citations["records"]}
        self.assertEqual(references["C151#1"]["scope"], "RECIFE_ONLY_NO_CONDE_INFERENCE")
        self.assertEqual(references["C18#1"]["scope"], "SPACE_WEATHER_NOT_ORBIT")
        self.assertEqual(references["C23#1"]["scope"],
                         "AGGREGATE_IS_NOT_THIRD_PRIMARY_OBSERVATION")
        dependencies = {(e["from"], e["to"]) for e in self.graph["source_dependencies"]}
        self.assertIn(("CELESTRAK_SPACE_WEATHER", "GFZ_KP_AP_SERIES"), dependencies)
        self.assertIn(("CELESTRAK_SPACE_WEATHER", "NRC_F107_SERIES"), dependencies)

    def test_missing_citation_source_fails(self):
        c = copy.deepcopy(self.config)
        c["citations"][0]["source_id"] = "NON_EXISTENT"
        with self.assertRaisesRegex(ValueError, "orphan"):
            pg.build(c, self.raw)

    def test_bad_occurrence_and_unqualified_collided_C44_fail(self):
        for value in ["C44", "C44#3", "C999#1"]:
            c = copy.deepcopy(self.config)
            c["citations"][0]["occurrence"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "orphan"):
                pg.build(c, self.raw)

    def test_duplicate_citation_and_unsafe_impact_claim_fail(self):
        c = copy.deepcopy(self.config)
        c["citations"].append(copy.deepcopy(c["citations"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            pg.build(c, self.raw)
        c = copy.deepcopy(self.config)
        c["citations"][0]["scope"] = "PHYSICAL_IMPACT_CONFIRMED"
        with self.assertRaisesRegex(ValueError, "physical"):
            pg.build(c, self.raw)

    def test_regressions_of_source_dependencies_fail(self):
        for bad in ("remove_tupi", "wrong_nasa", "cycle", "missing_ce"):
            c = copy.deepcopy(self.config)
            if bad == "remove_tupi":
                c["dependencies"] = [e for e in c["dependencies"]
                                     if e["from"] != "FBIS_EOP_UAP_D001"]
            elif bad == "wrong_nasa":
                next(s for s in c["sources"] if s["id"] == "NTRS_19640001198")[
                    "work_id"] = "OTHER"
            elif bad == "cycle":
                c["dependencies"].append({
                    "from": "RADIO_TUPI_19631108",
                    "to": "FBIS_EOP_UAP_D001", "kind": "transcribes"})
            else:
                c["dependencies"] = [e for e in c["dependencies"]
                                     if e["from"] != "CELESTRAK_SPACE_WEATHER"]
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                pg.build(c, self.raw)

    def test_snapshot_qualified_citations_and_contracts_are_complete(self):
        prefix = "matrix:" + pg.MATRIX_BLOB_SHA + ":"
        for entry in self.graph["matrix_occurrences"]:
            self.assertEqual(entry["snapshot_ref"], prefix + entry["occurrence"])
        for cite in self.citations["records"]:
            self.assertEqual(cite["snapshot_ref"], prefix + cite["occurrence"])
        for contract in self.graph["contracts"]:
            self.assertEqual(contract["snapshot_refs"],
                             [prefix + occurrence for occurrence in contract["occurrences"]])
        self.assertEqual(self.citations["matrix_snapshot_id"], pg.MATRIX_SNAPSHOT_ID)

    def test_legacy_c144_c151_aliases_are_explicitly_non_equivalent(self):
        aliases = self.graph["legacy_alias_conflicts"]
        self.assertEqual(len(aliases), 8)
        self.assertEqual([a["matrix_ref"].split(":")[-1] for a in aliases],
                         [f"C{i}#1" for i in range(144, 152)])
        self.assertTrue(all(not a["equivalent_claim"] for a in aliases))
        self.assertTrue(all("ORIGINAL_ZIP_NOT_LOCATED" in a["legacy_source_status"]
                            for a in aliases))
        self.assertNotEqual(aliases[-1]["legacy_claim"], aliases[-1]["matrix_claim"])
        self.assertIn("triangulação", aliases[-1]["legacy_claim"])
        self.assertIn("Recife", aliases[-1]["matrix_claim"])
        self.assertEqual(len(self.citations["legacy_alias_conflicts"]), 8)
        self.assertTrue(all(a["not_a_verified_physical_event"] for a in aliases))
        self.assertIsNone(self.graph["limits"]["independent_physical_tracking_count"])

    def test_cannot_join_legacy_c151_with_current_recife_winds(self):
        legacy_ref = self.graph["legacy_alias_conflicts"][-1]["legacy_ref"]
        self.assertIn(":C151#1", legacy_ref)
        for poisoned in (legacy_ref, "C151#1", "matrix:badsha:C151#1"):
            with self.subTest(reference=poisoned):
                config = copy.deepcopy(self.config)
                next(c for c in config["citations"] if c["occurrence"] == "C151#1")[
                    "snapshot_ref"] = poisoned
                with self.assertRaisesRegex(ValueError, "citation snapshot mismatch"):
                    pg.build(config, self.raw)

    def test_contract_cannot_take_legacy_alias_as_matrix_constraint(self):
        config = copy.deepcopy(self.config)
        bridge = next(x for x in config["contracts"] if x["id"] == "C179_C151_BRIDGE")
        bridge["snapshot_refs"][1] = self.graph["legacy_alias_conflicts"][-1]["legacy_ref"]
        with self.assertRaisesRegex(ValueError, "contract snapshot mismatch"):
            pg.build(config, self.raw)

    def test_bluebook_c232_c235_crosswalk_and_coverage(self):
        for occurrence in ("C232#1", "C233#1", "C234#1", "C235#1"):
            citations = [c for c in self.citations["records"] if c["occurrence"] == occurrence]
            self.assertTrue(citations)
            self.assertTrue(all(c["not_a_verified_conde_physical_event"] for c in citations))
            self.assertTrue(all(c["snapshot_ref"] == pg.matrix_ref(occurrence)
                                for c in citations))
        c232 = [c for c in self.citations["records"] if c["occurrence"] == "C232#1"]
        self.assertEqual({c["source_id"] for c in c232},
                         {"BLUEBOOK_CASES_INDEX_1963", "NARA_BB_CARD_302531013"})
        self.assertNotIn("C237#1", {c["occurrence"] for c in self.citations["records"]})

    def test_three_nara_scans_are_one_case_and_share_consular_account(self):
        sources = {s["id"]: s for s in self.graph["sources"]}
        unit = "NARA_BB_UNIT_302531012"
        children = [s for s in sources.values() if s.get("file_unit_id") == unit]
        self.assertEqual({s["nara_object_id"] for s in children},
                         {302531013, 302531014, 302531015})
        self.assertEqual(len({s["sha256_reported"] for s in children}), 3)
        self.assertEqual({s["family"] for s in children}, {"USAF_AIRA_BLUEBOOK"})
        edges = {(e["from"], e["to"], e["kind"]) for e in self.graph["source_dependencies"]}
        self.assertEqual(len([e for e in edges if e[1] == unit and
                              e[2] == "part_of_archival_unit"]), 3)
        self.assertIn(("NARA_USAIRA_C116_302531015", "NARA_AIRA_TELEGRAM_19631114",
                       "refers_to_prior_telegram"), edges)
        self.assertIn(("NARA_USAIRA_C116_302531015", "DOS_A628_19631120",
                       "reports_shared_consular_account"), edges)

    def test_site_exports_same_g18_nara_lead_with_citable_report(self):
        lead, = self.citations["post_matrix_occurrences"]
        self.assertEqual(lead["id"], "NARA-BB-CONDE-20261112-01")
        self.assertEqual(self.graph["post_matrix_occurrences"], self.citations["post_matrix_occurrences"])
        self.assertEqual(lead["source_id"], "NARA_AIRA_TELEGRAM_19631114")
        self.assertTrue(lead["report_citation_url"].endswith("/0810.jp2"))
        self.assertEqual(lead["report_object_sha256"],
                         "136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9")
        self.assertEqual(lead["report_file_unit_id"], "NARA_BB_UNIT_302531012")
        self.assertIsNone(lead["newspaper_publication_time"])
        self.assertEqual(lead["journalistic_source_independence"], "UNRESOLVED")
        self.assertIsNone(lead["physical_constraint"])
        self.assertTrue(lead["not_a_verified_conde_physical_event"])

    def test_nara_object_and_consular_adversarial_mutations_fail(self):
        for bad in ("nara_family", "scan_hash", "missing_unit_edge",
                    "lost_consular_shared_upstream", "invented_time"):
            c = copy.deepcopy(self.config)
            if bad == "nara_family":
                next(s for s in c["sources"] if s["id"] == "NARA_BB_CARD_302531013")[
                    "family"] = "DOS_CONSULAR"
            elif bad == "scan_hash":
                next(s for s in c["sources"] if s["id"] == "NARA_AIRA_TELEGRAM_19631114")[
                    "sha256_reported"] = "0" * 64
            elif bad == "missing_unit_edge":
                c["dependencies"] = [e for e in c["dependencies"]
                                     if e["from"] != "NARA_BB_CARD_302531013"]
            elif bad == "lost_consular_shared_upstream":
                c["dependencies"] = [e for e in c["dependencies"]
                                     if e["kind"] != "reports_shared_consular_account"]
            else:
                c["post_matrix_occurrences"][0]["newspaper_publication_time"] = "20:00"
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                pg.build(c, self.raw)

    def test_tampered_matrix_rejected_before_export(self):
        with self.assertRaisesRegex(ValueError, "matrix snapshot"):
            pg.build(self.config, self.raw.replace(b"1963", b"1964", 1))

    def test_site_export_is_deterministic(self):
        _, ref = pg.build(self.config, self.raw)
        self.assertEqual(pg.serialize(ref), pg.SITE.read_text())
        self.assertEqual(pg.serialize(ref), pg.serialize(ref))


if __name__ == "__main__":
    unittest.main()
