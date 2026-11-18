"""Adversarial offline tests for the documentary-only cumulative overlay consumer."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_documentary_overlay_index.py"
spec = importlib.util.spec_from_file_location("documentary_overlay", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
REG = Path("research/constraints/documentary_overlay_registry.json")
PARENT = Path("research/constraints/ssr_1963_observable_graph.json")
FEED = Path("public/data/conde-press-nucleus-provenance-r37.json")
SITE = Path("public/data/conde-documentary-overlay-index.json")


class DocumentaryOverlayConsumerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in [REG, PARENT, FEED, SITE]:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / path).read_bytes())

    def read(self, path):
        return json.loads((self.root / path).read_text(encoding="utf-8"))

    def write(self, path, data):
        (self.root / path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def repin(self, feed):
        self.write(FEED, feed)
        registry = self.read(REG)
        registry["feeds"][0]["sha256"] = hashlib.sha256(
            (self.root / FEED).read_bytes()
        ).hexdigest()
        self.write(REG, registry)

    def append_synthetic_second_feed(self, *, distinct_occurrences=False, source_change=None):
        """Compose two fully pinned test feeds without adding historical evidence."""
        feed = copy.deepcopy(self.read(FEED))
        feed["id"] = "SYNTHETIC-SECOND-FEED"
        if distinct_occurrences:
            renamed = {o["id"]: o["id"] + ":SECOND" for o in feed["occurrences"]}
            for node in feed["nodes"]:
                node["id"] = renamed.get(node["id"], node["id"])
            for edge in feed["edges"]:
                edge["source"] = renamed.get(edge["source"], edge["source"])
                edge["target"] = renamed.get(edge["target"], edge["target"])
            for occurrence in feed["occurrences"]:
                occurrence["id"] = renamed[occurrence["id"]]
        if source_change is not None:
            field, value = source_change
            source = next(s for s in feed["sources"] if s["id"] == "SRC:R79")
            source[field] = value
        path = Path("public/data/synthetic-overlay-second.json")
        self.write(path, feed)
        registry = self.read(REG)
        # Subtests reuse the temporary tree: replace the preceding synthetic
        # receipt instead of leaving a stale pin for the same file path.
        registry["feeds"] = [
            ref for ref in registry["feeds"] if ref["id"] != feed["id"]
        ]
        receipt = copy.deepcopy(registry["feeds"][0])
        receipt.update({
            "id": feed["id"],
            "path": str(path),
            "sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest(),
            "occurrence_ids": [o["id"] for o in feed["occurrences"]],
        })
        registry["feeds"].append(receipt)
        self.write(REG, registry)

    def test_cross_feed_duplicate_occurrence_rejected_with_valid_pins(self):
        self.append_synthetic_second_feed()
        with self.assertRaisesRegex(ValueError, "cross-feed occurrence id conflict"):
            module.load_index(self.root)

    def test_cross_feed_source_custody_cannot_change_after_repin(self):
        for field, value in (
            ("path", "synthetic/another-record.json"),
            ("source_url", "https://example.invalid/different-edition.pdf"),
            ("source_pdf_sha256", "a" * 64),
            ("editorial_family", "UNRELATED_EDITORIAL_GROUP"),
        ):
            with self.subTest(field=field):
                self.append_synthetic_second_feed(
                    distinct_occurrences=True, source_change=(field, value)
                )
                with self.assertRaisesRegex(ValueError, "cross-feed source custody conflict"):
                    module.load_index(self.root)

    def test_distinct_cross_feed_occurrences_with_shared_custody_are_allowed(self):
        self.append_synthetic_second_feed(distinct_occurrences=True)
        result = module.load_index(self.root)
        ids = [item["occurrence_id"] for item in result["occurrence_crosswalk"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(result["counts"]["documentary_occurrences"], 8)
        self.assertEqual(result["counts"]["documentary_nodes"], 21)
        self.assertEqual(result["counts"]["documentary_edges"], 32)
        self.assertEqual(result["counts"]["delta_physical_domain"], 0)

    def test_index_is_actual_materialized_consumer_and_parent_unchanged(self):
        before = (self.root / PARENT).read_bytes()
        result = module.load_index(self.root)
        self.assertEqual(result, self.read(SITE))
        self.assertEqual(result["interpretation"], "DOCUMENTARY_ONLY_NOT_PHYSICAL_OBSERVATIONS")
        self.assertEqual(result["counts"]["documentary_nodes"], 17)
        self.assertEqual(result["counts"]["documentary_edges"], 20)
        self.assertEqual(result["counts"]["documentary_occurrences"], 4)
        self.assertEqual(result["counts"]["parent_added_observations"], 0)
        self.assertEqual(result["counts"]["parent_added_physical_bridges"], 0)
        self.assertEqual(result["counts"]["delta_physical_domain"], 0)
        self.assertEqual(before, (self.root / PARENT).read_bytes())
        self.assertEqual(result, module.load_index(self.root))

    def test_repeat_import_is_idempotent(self):
        baseline = module.load_index(self.root)
        registry = self.read(REG)
        registry["feeds"].append(copy.deepcopy(registry["feeds"][0]))
        self.write(REG, registry)
        self.assertEqual(baseline, module.load_index(self.root))

    def test_conflicting_duplicate_id_is_not_silently_deduplicated(self):
        registry = self.read(REG)
        second = copy.deepcopy(registry["feeds"][0])
        second["sha256"] = "0" * 64
        registry["feeds"].append(second)
        self.write(REG, registry)
        with self.assertRaisesRegex(ValueError, "conflicting duplicate feed id"):
            module.load_index(self.root)

    def test_changed_feed_bytes_fail_even_if_json_remains_valid(self):
        feed = self.read(FEED)
        feed["scope_note"] += " tampered"
        self.write(FEED, feed)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            module.load_index(self.root)

    def test_orphan_edge_rejected_after_digest_repin(self):
        feed = self.read(FEED)
        feed["edges"][0]["target"] = "DOC:NONEXISTENT"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "orphan documentary edge"):
            module.load_index(self.root)

    def test_physical_relation_rejected_after_digest_repin(self):
        feed = self.read(FEED)
        feed["edges"][0]["relation"] = "INSTRUMENTAL_MEASUREMENT"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "invalid documentary edge"):
            module.load_index(self.root)

    def test_latent_activation_rejected_after_digest_repin(self):
        feed = self.read(FEED)
        next(n for n in feed["nodes"] if n["kind"] == "LATENT")["value"] = "1963-11-08T12:00:00Z"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "physical node promoted"):
            module.load_index(self.root)

    def test_event_hour_and_primary_witness_not_inferred(self):
        for field, value in [("event_time_utc", "1963-11-08T12:00:00Z"),
                             ("named_event_eyewitness", "anonymous witness"),
                             ("identified_norad_object", 528)]:
            with self.subTest(field=field):
                feed = self.read(FEED)
                feed["occurrences"][0][field] = value
                self.repin(feed)
                with self.assertRaisesRegex(ValueError, "promoted to physical observation"):
                    module.load_index(self.root)
                self.write(FEED, json.loads((ROOT / FEED).read_text(encoding="utf-8")))
                registry = self.read(REG)
                registry["feeds"][0]["sha256"] = hashlib.sha256(
                    (self.root / FEED).read_bytes()
                ).hexdigest()
                self.write(REG, registry)

    def test_editorial_family_does_not_become_independent_instrument(self):
        feed = self.read(FEED)
        next(s for s in feed["sources"] if s["id"] == "SRC:R86")["editorial_family"] = "INDEPENDENT_RADAR"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "Correio duplicate editorial family"):
            module.load_index(self.root)

    def test_publication_and_research_dates_are_not_interchanged(self):
        feed = self.read(FEED)
        historical = feed["occurrences"][0]
        historical["research_date"] = historical["publication_date"]
        historical["publication_date"] = None
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "publication date conflated"):
            module.load_index(self.root)

    def test_repin_does_not_promote_primary_witness_independence(self):
        feed = self.read(FEED)
        occurrence = next(o for o in feed["occurrences"]
                          if o["id"] == "OCC:CM21658:DENIAL")
        occurrence["source_independence"] = "INDEPENDENT_PRIMARY_EVENT_WITNESS_CONFIRMED"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "unverified occurrence independence"):
            module.load_index(self.root)

    def test_repin_does_not_swap_publication_dates_between_occurrences(self):
        feed = self.read(FEED)
        denial = next(o for o in feed["occurrences"]
                      if o["id"] == "OCC:CM21658:DENIAL")
        expert = next(o for o in feed["occurrences"]
                      if o["id"] == "OCC:CM21661:CURVELLO")
        denial["publication_date"], expert["publication_date"] = (
            expert["publication_date"], denial["publication_date"]
        )
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "publication date differs from occurrence identity"):
            module.load_index(self.root)

    def test_repin_does_not_swap_correio_pdf_custody(self):
        feed = self.read(FEED)
        denial = next(s for s in feed["sources"] if s["id"] == "SRC:R79")
        expert = next(s for s in feed["sources"] if s["id"] == "SRC:R86")
        for field in ("path", "source_url", "source_pdf_sha256"):
            denial[field], expert[field] = expert[field], denial[field]
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "P1 source custody drift"):
            module.load_index(self.root)

    def test_repin_does_not_retarget_source_url(self):
        feed = self.read(FEED)
        denial = next(s for s in feed["sources"] if s["id"] == "SRC:R79")
        denial["source_url"] = denial["source_url"].replace("#page=8", "#page=7")
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "P1 source custody drift"):
            module.load_index(self.root)

    def test_repin_does_not_relabel_pdf_hash(self):
        feed = self.read(FEED)
        denial = next(s for s in feed["sources"] if s["id"] == "SRC:R79")
        denial["source_pdf_sha256"] = "0" * 64
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "P1 source custody drift"):
            module.load_index(self.root)

    def test_repin_does_not_promote_occurrence_type(self):
        feed = self.read(FEED)
        denial = next(o for o in feed["occurrences"]
                      if o["id"] == "OCC:CM21658:DENIAL")
        denial["type"] = "PRIMARY_EVENT_EYEWITNESS_CONFIRMED"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "P1 occurrence source/document/type drift"):
            module.load_index(self.root)

    def test_repin_does_not_swap_page_with_denominator_unchanged(self):
        feed = self.read(FEED)
        edition = next(e for e in feed["coverage"]["editions"]
                       if e["family"] == "UH_NE" and e["edition"] == "00472")
        edition["examined_pdf_pages"][-1] = 11  # 10 -> 11; still 144/4
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "audited coverage scope drift"):
            module.load_index(self.root)

    def test_repin_does_not_change_date_of_examined_edition(self):
        feed = self.read(FEED)
        edition = next(e for e in feed["coverage"]["editions"]
                       if e["family"] == "UH_NE" and e["edition"] == "00472")
        edition["publication_date"] = "1963-11-10"
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "audited coverage scope drift"):
            module.load_index(self.root)

    def test_coverage_negative_not_physical_absence(self):
        feed = self.read(FEED)
        feed["coverage"]["physical_absence_proven"] = True
        self.repin(feed)
        with self.assertRaisesRegex(ValueError, "bounded search promoted"):
            module.load_index(self.root)

    def test_path_traversal_fails_closed(self):
        registry = self.read(REG)
        registry["feeds"][0]["path"] = "../../untrusted.json"
        self.write(REG, registry)
        with self.assertRaisesRegex(ValueError, "missing or unsafe file"):
            module.load_index(self.root)

    def test_duplicate_json_keys_are_rejected(self):
        (self.root / REG).write_text('{"schema":"x","schema":"y"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            module.load_index(self.root)

    def test_missing_or_extra_index_entry_fails_semantic_check(self):
        altered = self.read(SITE)
        altered["counts"]["parent_added_observations"] = 1
        self.write(SITE, altered)
        self.assertNotEqual(self.read(SITE), module.load_index(self.root))


if __name__ == "__main__":
    unittest.main()
