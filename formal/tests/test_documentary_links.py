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

if __name__ == "__main__":
    unittest.main()
