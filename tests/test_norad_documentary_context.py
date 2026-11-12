"""NORAD documentary identity crosswalk regression and adversarial checks."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_norad_context as norad


class NoradDocumentaryContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = norad.build()

    def test_deterministic_export_and_hard_size_cap(self):
        self.assertEqual(
            norad.serialize(self.payload),
            (ROOT / norad.OUTPUT).read_text())
        self.assertLessEqual(len(norad.serialize(self.payload).encode()), 20_000)

    def test_original_date_beats_catalogue_date(self):
        by_id = {r["source_id"]: r for r in self.payload["records"]}
        for suffix in ("09", "10"):
            record = by_id["MOR-NORAD-1964-NOV30-" + suffix]
            self.assertEqual(record["source_date"], "1964-11-30")
            self.assertEqual(record["catalogue_date_claim"], "1963-11-30")
            self.assertIsNone(record["matrix_occurrence_ref"])

    def test_unrelated_objects_never_become_528_observations(self):
        records = self.payload["records"]
        self.assertEqual(
            {r["occurrence_id"] for r in records},
            {"MOR-NOR-20261112-0" + str(i) for i in range(1, 6)})
        self.assertNotIn(528, {
            obj for rec in records for obj in rec["object_ids_reported_in_this_document"]
        })
        self.assertTrue(all(r["physical_528_constraint"] is None for r in records))
        self.assertTrue(all(r["independent_528_physical_observation_count"] is None
                            for r in records))
        self.assertTrue(all(r["original_pdf_sha256"] is None for r in records))

    def test_nasa_context_not_direct_sensor_edge(self):
        bridge = self.payload["nasa_norad_policy_bridge"]
        self.assertEqual(bridge["relation"],
                         "DATA_EXCHANGE_POSSIBLE_NOT_PROOF_OF_MEASUREMENT_LINEAGE")
        self.assertIsNone(bridge["actual_528_measurement_upstream"])
        self.assertEqual(
            {x["source_id"] for x in bridge["contextual_matrix_citations"]},
            {"NASA_SSR_19631115", "NTRS_19640001198"})
        self.assertTrue(all(x["snapshot_ref"].startswith("matrix:") and
                            len(x["row_sha256"]) == 64
                            for x in bridge["contextual_matrix_citations"]))

    def test_one_custodial_snapshot_hash_binds_records(self):
        import hashlib
        actual = hashlib.sha256((ROOT / norad.AUDIT).read_bytes()).hexdigest()
        self.assertEqual(self.payload["source_audit_sha256"], actual)

    def test_mutations_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in (norad.AUDIT, norad.LINEAGES, norad.CITATIONS):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / name, path)
            audit = json.loads((root / norad.AUDIT).read_text())
            def reject(changed, pattern):
                (root / norad.AUDIT).write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, pattern):
                    norad.build(root)
            bad = json.loads(json.dumps(audit))
            bad["sources"][3]["document_date"] = "1963-11-30"
            reject(bad, "date / lineage")
            bad = json.loads(json.dumps(audit))
            bad["occurrences"][1]["physical_constraint_active"] = True
            reject(bad, "physical-boundary")
            bad = json.loads(json.dumps(audit))
            bad["sources"][1]["scope"] = "object 528"
            reject(bad, "absent from source scope")
            bad = json.loads(json.dumps(audit))
            bad["occurrences"][2]["source_id"] = bad["occurrences"][1]["source_id"]
            reject(bad, "duplicate source-to-occurrence")


if __name__ == "__main__":
    unittest.main()
