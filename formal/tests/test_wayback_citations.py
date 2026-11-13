"""WB-01: adversarial identity and timestamp guards for Lean documentary input."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "formal/scripts"))
import compile_wayback_citations as compiler


class WaybackCitationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(compiler.SOURCE.read_text())
        cls.dependence = json.loads(compiler.DEPENDENCE.read_text())

    def test_compiled_graph_reproducible_from_custody(self):
        self.assertEqual(compiler.SOURCE.read_bytes(),
                         compiler.upstream.encode(compiler.upstream.build()))
        code = compiler.assemble(self.graph, self.dependence)
        self.assertEqual(compiler.TARGET.read_text(), code)
        self.assertLess(len(code.encode()), 20_000)
        self.assertEqual(code.count("eventTimeUtc := none, activated := false"), 2)
        self.assertEqual(code.count("cdxSha1Base32 := some"), 2)
        self.assertIn("archivedUrl := none", code)
        self.assertIn("captureStatus := .exactUrlNotInIndex", code)
        self.assertEqual(code.count("captureId := "), 5)
        self.assertEqual(code.count('pdfSha256 := "0f27ed20'), 3)
        self.assertEqual(code.count("kind := ."), 13)
        self.assertEqual(code.count("matrixRef := none, activated := false"), 3)

    def test_c197_and_c198_share_one_nasa_work_and_no_event_time(self):
        citations = [x for x in self.graph["nodes"]
                     if x["kind"] == "FROZEN_MATRIX_CITATION"]
        self.assertEqual({x["snapshot_ref"].split(":")[-1] for x in citations},
                         {"C197#1", "C198#1"})
        self.assertTrue(all(x["simulator_value"] is None and not x["activation"]
                            for x in citations))
        records = json.loads((ROOT / "public/data/conde-source-citations.json").read_text())
        by_ref = {x["snapshot_ref"].split(":")[-1]: x
                  for x in records["records"] if x["snapshot_ref"].endswith((":C197#1", ":C198#1"))}
        self.assertEqual({r["work_id"] for r in by_ref.values()}, {"NASA_SSR_VOL3_22"})

    def test_rejects_misreported_provenance_and_derived_measurement(self):
        cases = (
            (lambda g: g["counts"].update(independent_physical_observations_added=1),
             "cardinalities/observations"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "FROZEN_MATRIX_CITATION").update(activation=True),
             "event time invented/parameter activated"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "FROZEN_MATRIX_CITATION").update(simulator_value="1963-11-13T00:00:00Z"),
             "event time invented/parameter activated"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "FROZEN_MATRIX_CITATION").update(source_id="AFSPC_MIRROR_528"),
             "citation mismatch"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "VERIFIED_ARCHIVAL_COPY").update(capture_utc="1963-11-15T00:00:00Z"),
             "capture / PDF integrity"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "VERIFIED_ARCHIVAL_COPY").update(retrieved_bytes_sha256="0"*64),
             "capture / PDF integrity"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "NEGATIVE_EXACT_URL_LOOKUP").update(scope="DOCUMENT_NOT_FOUND"),
             "negative lookup promoted"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "SUPPLEMENTARY_SOURCE_REF_NOT_MATRIX").update(activation=True),
             "supplementary source promoted"),
            (lambda g: next(x for x in g["nodes"] if x["kind"] == "ONE_ARCHIVED_DOCUMENT_PAYLOAD").update(distinct_documentary_payload_count=3),
             "legacy NASA unique PDF payload"),
            (lambda g: next(x for x in g["nodes"] if ":LEGACY-CAPTURE:" in x["id"]).update(retrieved_bytes_sha256="0"*64),
             "legacy Wayback aliases"),
            (lambda g: next(x for x in g["nodes"] if ":LEGACY-CAPTURE:" in x["id"]).update(capture_utc="1963-11-15T00:00:00Z"),
             "capture / PDF integrity"),
            (lambda g: g["edges"].pop(), "stale/missing graph edge"),
            (lambda g: g["edges"][3].update(kind="DOCUMENTARY_CONTEXT_ONLY"),
             "changed relation"),
        )
        for mutation, expected in cases:
            broken = copy.deepcopy(self.graph)
            mutation(broken)
            with self.subTest(expected=expected), self.assertRaisesRegex(ValueError, expected):
                compiler.assemble(broken, self.dependence)

    def test_parent_upstream_lineage_cannot_claim_two_independent_sensors(self):
        broken = copy.deepcopy(self.dependence)
        row = next(x for x in broken["citation_lineages"]
                   if x["snapshot_ref"].endswith(":C198#1"))
        row["declared_upstream_paths"] = []
        with self.assertRaisesRegex(ValueError, "NTRS catalogue lineage"):
            compiler.assemble(self.graph, broken)

    def test_stale_parent_export_refused(self):
        changed = copy.deepcopy(self.graph)
        changed["matrix_git_blob_sha1"] = "0"*40
        with self.assertRaisesRegex(ValueError, "matrix snapshot"):
            compiler.assemble(changed, self.dependence)


if __name__ == "__main__":
    unittest.main()
