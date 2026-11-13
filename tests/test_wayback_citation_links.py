"""Offline mutation tests for exact Wayback source-citation joins."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_wayback_citation_links as wb


class WaybackCitationGraphTests(unittest.TestCase):
    def test_canonical_graph_and_no_double_count(self):
        graph = wb.build()
        self.assertEqual((ROOT / wb.OUTPUT).read_bytes(), wb.encode(graph))
        self.assertEqual(graph["counts"]["verified_archived_copies"], 5)
        self.assertEqual(graph["counts"]["nasa_legacy_capture_timestamps"], 3)
        self.assertEqual(graph["counts"]["nasa_legacy_distinct_pdf_payloads"], 1)
        self.assertEqual(graph["counts"]["negative_exact_url_lookups"], 1)
        self.assertEqual(graph["counts"]["matrix_occurrences_linked"], 2)
        self.assertEqual(graph["counts"]["independent_physical_observations_added"], 0)
        capture = [n for n in graph["nodes"]
                   if n["kind"] == "VERIFIED_ARCHIVAL_COPY"]
        self.assertEqual(len(capture), 5)
        self.assertNotEqual(capture[0]["cdx_digest_base32_sha1"],
                            capture[0]["retrieved_bytes_sha256"])
        nasa = [n for n in graph["nodes"]
                if n["kind"] == "FROZEN_MATRIX_CITATION"]
        self.assertEqual({n["source_id"] for n in nasa},
                         {"NASA_SSR_19631115", "NTRS_19640001198"})
        self.assertEqual(len({n["snapshot_ref"] for n in nasa}), 2)
        self.assertTrue(all(n["simulator_value"] is None
                            and n["activation"] is False for n in nasa))

    def test_legacy_nasa_three_copies_one_payload_not_three_sensors(self):
        graph = wb.build()
        nasa_copies = [n for n in graph["nodes"]
                       if ":LEGACY-CAPTURE:" in n["id"]]
        self.assertEqual({n["capture_utc"] for n in nasa_copies}, {
            "2015-02-17T13:30:01Z", "2017-02-28T14:48:59Z",
            "2017-03-02T09:31:49Z"})
        self.assertEqual({n["retrieved_bytes_sha256"] for n in nasa_copies},
                         {wb.NASA_BYTES_SHA256})
        payloads = [n for n in graph["nodes"]
                    if n["kind"] == "ONE_ARCHIVED_DOCUMENT_PAYLOAD"]
        self.assertEqual(len(payloads), 1)
        self.assertEqual(len([e for e in graph["edges"]
                              if e["kind"] == "SAME_BYTES_NOT_INDEPENDENT_ARCHIVAL_WITNESS"
                              and e["to"] == payloads[0]["id"]]), 3)
        self.assertEqual(graph["counts"]["independent_physical_observations_added"], 0)
        self.assertEqual(graph["counts"]["negative_exact_url_lookups"], 1)
        self.assertEqual({n["simulator_value"] for n in graph["nodes"]
                          if n["kind"] == "FROZEN_MATRIX_CITATION"}, {None})

    def test_legacy_nasa_rejects_forgery_and_false_independence(self):
        self.mutate(wb.NASA_LEGACY, lambda x: x["captures"][0]["cdx_record"].update(
            digest="A" * 32))
        self.mutate(wb.NASA_LEGACY, lambda x: x["captures"][1]["replay"].update(
            sha256="0" * 64))
        self.mutate(wb.NASA_LEGACY, lambda x: x["captures"][2]["cdx_record"].update(
            timestamp="20150217133001"))
        self.mutate(wb.NASA_LEGACY, lambda x: x["interpretation"].update(
            captures_are_independent_historical_witnesses=True))
        self.mutate(wb.NASA_LEGACY, lambda x: x.update(
            source_occurrences=["C197#1", "C197#1"]))
        self.mutate(wb.NASA_LEGACY, lambda x: x["current_api_replay"].update(
            sha256="0" * 64))
        self.mutate(wb.NASA_LEGACY, lambda x: x.update(
            source_family="INDEPENDENT_SENSOR"))

    def mutate(self, filename, fn):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in wb.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, target)
            path = root / filename
            data = json.loads(path.read_text())
            fn(data)
            path.write_text(json.dumps(data))
            with self.assertRaises((ValueError, KeyError, TypeError, IndexError)):
                wb.build(root)

    def pilot(self, rid, fn):
        def mutation(x):
            record = next(r for r in x["records"] if r["id"] == rid)
            fn(record)
        self.mutate(wb.PILOT, mutation)

    def test_reject_forged_cdx_and_replay(self):
        rid = "WB-NORAD-1963-H2"
        self.pilot(rid, lambda x: x["cdx_record"].update(digest="A" * 32))
        self.pilot(rid, lambda x: x["replay"].update(sha256="0" * 64))
        self.pilot(rid, lambda x: x["replay"].update(content_type="text/html"))
        self.pilot(rid, lambda x: x["replay"].update(pdf_magic=False))
        self.pilot(rid, lambda x: x["cdx_record"].update(statuscode="302"))

    def test_reject_wrong_archive_original_or_era(self):
        rid = "WB-SAO-RU301"
        self.pilot(rid, lambda x: x.update(
            archived_url=x["archived_url"].replace("id_/", "/")))
        self.pilot(rid, lambda x: x.update(
            capture_utc="1963-11-08T10:52:02Z"))
        self.pilot(rid, lambda x: x.update(
            original_url="https://example.org/other.pdf"))
        self.pilot(rid, lambda x: x["cdx_record"].update(original="https://example.org/a.pdf"))

    def test_negative_nasa_does_not_become_a_capture(self):
        rid = "WB-NASA-SSR-19631115"
        self.pilot(rid, lambda x: x.update(status="VERIFIED_REPLAY"))
        self.pilot(rid, lambda x: x.update(archived_url="https://example.org/fake.pdf"))
        self.pilot(rid, lambda x: x["cdx_lookup"].update(exact_results=1))
        self.pilot(rid, lambda x: x.update(source_refs=["C197#1", "C197#1"]))

    def test_join_identity_and_scientific_activation_gates(self):
        self.mutate(wb.DEPENDENCE, lambda x: next(
            c for c in x["citation_lineages"]
            if c["snapshot_ref"].endswith(":C198#1")
        ).update(source_id="NASA_SSR_19631115"))
        self.mutate(wb.BRIDGES, lambda x: next(
            c for c in x["citation_coverage"]
            if c["occurrence_ref"].endswith(":C197#1")
        ).update(activation=True))
        self.mutate(wb.BRIDGES, lambda x: next(
            c for c in x["citation_coverage"]
            if c["occurrence_ref"].endswith(":C197#1")
        ).update(row_sha256="0" * 64))

    def test_supplementary_not_forced_into_frozen_matrix(self):
        graph = wb.build()
        supplemental = [n for n in graph["nodes"]
                        if n["kind"] == "SUPPLEMENTARY_SOURCE_REF_NOT_MATRIX"]
        self.assertEqual(len(supplemental), 3)
        self.assertTrue(all(n["matrix_snapshot_ref"] is None
                            and n["activation"] is False for n in supplemental))
        self.assertEqual({n["source_ref"] for n in supplemental},
                         {"C241-P8", "SIA-FARU0301", "BN-RU301-20261112-01"})


if __name__ == "__main__":
    unittest.main()
