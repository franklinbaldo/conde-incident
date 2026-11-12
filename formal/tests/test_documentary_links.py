"""Regression tests for documentary-to-Lean data, not orbit fit."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal/scripts"))
from compile_documentary_links import assemble, ref_parts, GRAPH, LINEAGES, MATRIX, TARGET  # noqa: E402
from tools.provenance_graph import build  # noqa: E402

class DocumentaryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(LINEAGES.read_text(encoding="utf-8"))
        cls.matrix = MATRIX.read_bytes()
        cls.graph = json.loads(GRAPH.read_text(encoding="utf-8"))

    def test_lean_generated_from_exact_curated_rows(self):
        code, report = assemble(self.config, self.matrix, self.graph)
        self.assertEqual(TARGET.read_text(encoding="utf-8"), code)
        self.assertEqual(report["matrix_occurrences"], 241)
        self.assertEqual(report["curated_documentary_links"], 29)
        self.assertEqual(report["curated_documentary_occurrences"], 28)
        self.assertEqual(report["unmapped_documentary_occurrences"], 213)
        self.assertEqual(report["secondary_528_fields"], 6)
        self.assertEqual(report["provenance_work_count_for_C197_C198"], 1)
        self.assertNotIn('reportedDecimal := "284.152', code)

    def test_c44_c45_c46_cannot_be_resolved_without_explicit_occurrence(self):
        known = {f"C{i:02d}#1" for i in range(1, 10)} | \
                {f"C{i}#1" for i in range(10, 239)} | \
                {"C44#2", "C45#2", "C46#2"}
        for label in ("C44", "C45", "C46", "C144", "C179", "C999#1", "C44#3"):
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, "unresolved or ambiguous"):
                ref_parts(label, known)
        self.assertEqual(ref_parts("C44#2", known), (44, 2))

    def test_ntrs_is_metadata_of_same_work_not_new_sensor(self):
        bad = copy.deepcopy(self.config)
        record = next(s for s in bad["sources"] if s["id"] == "NTRS_19640001198")
        record["work_id"] = "FORGED_INDEPENDENT_WORK"
        with self.assertRaisesRegex(ValueError, "independent document"):
            assemble(bad, self.matrix, self.graph)

    def test_c179_rejects_changed_element_or_unjustified_activation(self):
        changed = copy.deepcopy(self.graph)
        element = next(o for o in changed["observations"] if o["object_id"] == 528 and
                       o["observable"] == "raan")
        element["constraint_status"] = "ACTIVE_HARD"
        with self.assertRaisesRegex(ValueError, "prematurely promoted"):
            assemble(self.config, self.matrix, changed)

    def test_c179_rejects_different_orbit_source(self):
        bad = copy.deepcopy(self.graph)
        o = next(o for o in bad["observations"] if o["object_id"] == 528)
        o["matrix_local_id"] = "C144#1"
        with self.assertRaisesRegex(ValueError, "prematurely promoted"):
            assemble(self.config, self.matrix, bad)

    def test_nasa_8_nov_remains_a_day_only(self):
        bad = copy.deepcopy(self.config)
        next(c for c in bad["citations"] if c["occurrence"] == "C197#1")["scope"] = "KNOWN_TERMINAL_TIME"
        # The provenance layer now blocks unauthorized scope codes before the
        # later Lean bridge's critical-C197-specific safeguard runs.
        with self.assertRaisesRegex(ValueError, "scope not approved|critical C179/C197/C198"):
            assemble(bad, self.matrix, self.graph)

    def test_frozen_matrix_will_not_silently_alias_legacy_c144(self):
        bad = self.matrix.replace(b"C144", b"C144_LEGACY", 1)
        with self.assertRaisesRegex(ValueError, "matrix snapshot differs"):
            assemble(self.config, bad, self.graph)

    def test_documentary_citations_do_not_become_independent_measurements(self):
        _, feed = build(self.config, self.matrix)
        tracking = [r for r in feed["records"] if r["source_family"] == "NORAD_NASA_TRACKING"]
        self.assertGreater(len(tracking), 2)
        self.assertEqual({r["source_family"] for r in tracking}, {"NORAD_NASA_TRACKING"})
        self.assertEqual({r["work_id"] for r in tracking if r["occurrence"] in ("C197#1", "C198#1")},
                         {"NASA_SSR_VOL3_22"})



class DeclaredContractAncestryTests(unittest.TestCase):
    """Contract -> snapshot occurrence -> source -> explicit upstream chain."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "formal/scripts"))
        from compile_contract_lineage import (
            assemble as assemble_contracts, SOURCE, CANONICAL, TARGET as CONTRACT_TARGET,
        )
        from export_documentary_dependence import build as build_dependence
        cls.assemble = staticmethod(assemble_contracts)
        cls.canonical = json.loads(CANONICAL.read_text())
        cls.companion = json.loads(SOURCE.read_text())
        cls.expected = build_dependence()
        cls.target = CONTRACT_TARGET

    def test_contracts_are_typed_snapshot_qualified_and_byte_reproducible(self):
        code, stats = self.assemble(self.companion, self.canonical, self.expected)
        self.assertEqual(self.target.read_text(), code)
        self.assertEqual((stats["contracts"], stats["contract_occurrences"],
                          stats["contract_citation_links"], stats["declared_upstream_paths"]),
                         (3, 8, 8, 1))
        self.assertEqual(stats["active_constraints_added"], 0)
        self.assertEqual(stats["new_numeric_observations"], 0)
        self.assertIn("contractDocumentaryLineages", code)
        self.assertIn('relation := "catalogue_of_same_work"', code)
        self.assertNotIn('reportedDecimal := "284.1520"', code)

    def test_c198_ntrs_is_catalogue_of_nasa_work_not_second_instrument(self):
        c = next(c for c in self.companion["contract_citation_crosswalk"]
                 if c["contract_id"] == "C197_DOCUMENTARY")
        ntrs = next(o for o in c["occurrences"] if o["snapshot_ref"].endswith("C198#1"))
        self.assertEqual(ntrs["cited_source_ids"], ["NTRS_19640001198"])
        self.assertEqual(ntrs["declared_upstream_source_ids"], ["NASA_SSR_19631115"])
        code, _ = self.assemble(self.companion, self.canonical, self.expected)
        self.assertIn('sourceId := "NTRS_19640001198"', code)
        self.assertIn('targetId := "NASA_SSR_19631115"', code)

    def test_c151_snapshot_cannot_resolve_to_legacy_wind_false_alias(self):
        c = next(c for c in self.companion["contract_citation_crosswalk"]
                 if c["contract_id"] == "C179_C151_BRIDGE")
        current = next(o for o in c["occurrences"] if o["snapshot_ref"].endswith("C151#1"))
        self.assertIn("matrix:a7978c3a75a153b16ab70118a92c434bba674cb7:", current["snapshot_ref"])
        self.assertEqual(current["cited_source_ids"], ["NOAA_IGRA_RECIFE_1963"])
        bad = copy.deepcopy(self.companion)
        badref = next(o for c in bad["contract_citation_crosswalk"]
                      if c["contract_id"] == "C179_C151_BRIDGE"
                      for o in c["occurrences"] if o["snapshot_ref"].endswith("C151#1"))
        badref["snapshot_ref"] = "matrix:0000000000000000000000000000000000000000:C151#1"
        with self.assertRaisesRegex(ValueError, "companion differs"):
            self.assemble(bad, self.canonical, self.expected)

    def test_mutated_ancestry_kind_fails_closed(self):
        bad = copy.deepcopy(self.companion)
        ntrs = next(c for c in bad["citation_lineages"]
                    if c["source_id"] == "NTRS_19640001198")
        ntrs["declared_upstream_paths"][0]["edges"][0]["kind"] = "independent_tracking"
        with self.assertRaisesRegex(ValueError, "companion differs"):
            self.assemble(bad, self.canonical, self.expected)

    def test_new_contract_status_cannot_be_silently_activated(self):
        bad = copy.deepcopy(self.companion)
        bad["contract_citation_crosswalk"][0]["contract_status"] = "ACTIVE_HARD"
        with self.assertRaisesRegex(ValueError, "companion differs"):
            self.assemble(bad, self.canonical, self.expected)

if __name__ == "__main__":
    unittest.main()
