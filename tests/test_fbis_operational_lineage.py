"""C241-P42: adversarial custody, one-work genealogy, and non-promotion."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_matrix_coverage as coverage
import export_fbis_operational_lineage as fbis
import provenance_graph as pg


class FbisOperationalLineageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pg.matrix_occurrences(pg.MATRIX.read_bytes())
        cls.data = fbis.build()

    def test_all_three_frozen_occurrences_are_source_locked(self):
        self.assertEqual(len(self.data["edges"]), 3)
        self.assertEqual(self.data["counts"]["source_works"], 1)
        self.assertEqual(self.data["counts"]["independent_instrumental_sources"], 0)
        self.assertEqual([e["matrix_occurrence"].rsplit(":", 1)[-1]
                          for e in self.data["edges"]],
                         ["C212#1", "C213#1", "C214#1"])
        self.assertTrue(all(e["source_work_id"] == fbis.SOURCE_ID
                            for e in self.data["edges"]))
        self.assertEqual(self.data["source"]["source_pdf_sha256"], fbis.SOURCE_PDF_SHA256)
        self.assertEqual(self.data["source"]["source_pdf_size_bytes"], fbis.SOURCE_PDF_SIZE)
        self.assertFalse(self.data["source"]["raw_pdf_bytes_replayed_this_run"])
        self.assertEqual(fbis.OUTPUT.read_bytes(), fbis.encoded(self.data))

    def test_crosswalk_adds_three_documentary_links_not_three_sensors(self):
        result = coverage.rebuild()
        self.assertEqual(result["represented_in_either"], 30)
        self.assertEqual(result["documented_in_either_two_feeds_or_fbis"], 33)
        self.assertEqual(result["supplemental_documentary_links_distinct_occurrences"], 3)
        layer = result["supplemental_context_layers"]["fbis_operational_history"]
        self.assertEqual(layer["source_works"], 1)
        self.assertEqual(layer["occurrences"], ["C212#1", "C213#1", "C214#1"])
        self.assertEqual(layer["physical_domain_effect"], "THETA_UNCHANGED")

    def test_mutated_source_or_temporal_identity_rejected(self):
        for field, value in (
            ("work_id", "ANOTHER_WORK"),
            ("publication_date", "1963-11-08"),
            ("url", "https://example.com"),
            ("source_pdf_sha256", "0" * 64),
            ("source_pdf_size_bytes", 0),
            ("raw_pdf_bytes_replayed_this_run", True),
            ("source_count", 3),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["source"][field] = value
                with self.assertRaisesRegex(ValueError, "source identity"):
                    fbis.audit(data, self.rows)

    def test_source_pdf_replay_rejects_short_and_invalid_content(self):
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "source.pdf"
            pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
            with self.assertRaisesRegex(ValueError, "byte length"):
                fbis.verify_source_pdf(pdf)
            with self.assertRaisesRegex(ValueError, "file missing"):
                fbis.verify_source_pdf(pdf.with_name("missing.pdf"))
            # A sparse same-size fake catches attacks that pass the byte-count gate.
            with pdf.open("wb") as stream:
                stream.seek(fbis.SOURCE_PDF_SIZE - 1)
                stream.write(b"X")
            with self.assertRaisesRegex(ValueError, "header"):
                fbis.verify_source_pdf(pdf)
            with pdf.open("r+b") as stream:
                stream.write(b"%PDF-1.4")
            with self.assertRaisesRegex(ValueError, "EOF"):
                fbis.verify_source_pdf(pdf)
            with pdf.open("r+b") as stream:
                stream.seek(-6, 2)
                stream.write(b"%%EOF\n")
            with self.assertRaisesRegex(ValueError, "digest"):
                fbis.verify_source_pdf(pdf)

    def test_mutated_line_hash_page_and_shared_family_rejected(self):
        for field, value in (
            ("matrix_occurrence", pg.matrix_ref("C212#1")),
            ("matrix_row_sha256", "0" * 64),
            ("matrix_line", 55),
            ("printed_page", 54),
            ("pdf_zero_based_index", 55),
            ("source_work_id", "INDEPENDENT_CIA_STATION"),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["edges"][1][field] = value
                with self.assertRaises(ValueError):
                    fbis.audit(data, self.rows)

    def test_false_attribution_and_orbital_activation_rejected(self):
        for field, value in (
            ("independent_instrument_1963", True),
            ("activation", True),
            ("active_physical_constraint", True),
            ("instrument_epoch_utc", "1963-11-08T12:00:00Z"),
            ("station_attributed_to_tupi", "Panama"),
            ("tupi_reception_log", "hypothetical"),
            ("physical_domain_effect", "THETA_REDUCED"),
            ("status", "OBSERVED_PHYSICAL_EVENT"),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["edges"][0][field] = value
                with self.assertRaises(ValueError):
                    fbis.audit(data, self.rows)

    def test_limits_and_duplicate_work_contradictions_rejected(self):
        data = copy.deepcopy(self.data)
        data["counts"]["source_works"] = 3
        with self.assertRaisesRegex(ValueError, "counting"):
            fbis.audit(data, self.rows)
        data = copy.deepcopy(self.data)
        data["epistemic_limits"]["panama_did_not_prove_tupi_interception"] = False
        with self.assertRaisesRegex(ValueError, "epistemic limit"):
            fbis.audit(data, self.rows)

    def test_frozen_matrix_tampering_rejected(self):
        rows = copy.deepcopy(self.rows)
        next(row for row in rows if row["occurrence"] == "C214#1")["row_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            # Source locks also need to check against frozen canonical rows
            fbis.audit(self.data, rows)


if __name__ == "__main__":
    unittest.main()
