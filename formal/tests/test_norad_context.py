"""C241-L15: independent checks for typed NORAD context, not physical tracking."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal/scripts"))
import compile_norad_context as compiler


class NoradLeanContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custody = compiler.export.build()
        cls.payload = json.loads(compiler.INPUT.read_text(encoding="utf-8"))

    def test_generated_lean_is_current_and_small(self):
        text = compiler.assemble(self.payload, self.custody)
        self.assertEqual(compiler.TARGET.read_text(encoding="utf-8"), text)
        self.assertLess(len(text.encode("utf-8")), 20_000)
        self.assertEqual(text.count("physical528Constraint := none"), 5)

    def test_identifiers_are_not_cnn_or_tracking(self):
        ids = {r["source_id"] for r in self.payload["records"]}
        self.assertEqual(ids, set(compiler.EXPECTED_IDS))
        self.assertNotIn(528, {i for r in self.payload["records"] for i in
                               r["object_ids_reported_in_this_document"]})
        self.assertTrue(all(r["matrix_occurrence_ref"] is None for r in self.payload["records"]))
        refs = self.payload["nasa_norad_policy_bridge"]["contextual_matrix_citations"]
        self.assertEqual({r["snapshot_ref"].split(":")[-1] for r in refs}, {"C197#1", "C198#1"})

    def test_refuses_fake_528_measurement_and_source_alias(self):
        changes = (
            (lambda j: j["records"][1]["object_ids_reported_in_this_document"].append(528),
             "catalogue objects changed"),
            (lambda j: j["records"][2].update(physical_528_constraint="Conde"),
             "invented Cnn/528/physical/hash identity"),
            (lambda j: j["records"][0].update(matrix_occurrence_ref="C197#1"),
             "invented Cnn/528/physical/hash identity"),
            (lambda j: j["records"][4].update(original_pdf_sha256="0"*64),
             "invented Cnn/528/physical/hash identity"),
            (lambda j: j["records"][3].update(source_date="1963-11-30"),
             "document year or catalogue discrepancy lost"),
            (lambda j: j["nasa_norad_policy_bridge"].update(actual_528_measurement_upstream="radar"),
             "unverified 528 measurement lineage"),
            (lambda j: j["nasa_norad_policy_bridge"]["contextual_matrix_citations"][0].update(snapshot_ref="C197#1"),
             "non-snapshot-qualified Cnn citation"),
        )
        for mutate, message in changes:
            changed = copy.deepcopy(self.payload)
            mutate(changed)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                compiler.assemble(changed, changed)

    def test_stale_export_cannot_be_accepted(self):
        changed = copy.deepcopy(self.payload)
        changed["source_audit_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "stale or not audited"):
            compiler.assemble(changed, self.custody)


if __name__ == "__main__":
    unittest.main()
