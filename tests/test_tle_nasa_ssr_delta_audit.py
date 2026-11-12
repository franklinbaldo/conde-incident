"""Adversarial synthetic controls for NASA report custody (not facsimile OCR)."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_nasa_ssr_delta_audit import validate

LEDGER = Path(__file__).resolve().parents[1] / "research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json"


class TestNasaSsrCustody(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = copy.deepcopy(json.loads(LEDGER.read_text(encoding="utf-8")))
        self.paths = []
        for row in self.ledger["sources"]:
            contents = ("%PDF-1.4\nfixture=" + row["ntrs_id"] + "\n%%EOF\n").encode()
            row["sha256"] = hashlib.sha256(contents).hexdigest()
            path = Path(self.temp.name) / (row["ntrs_id"] + ".pdf")
            path.write_bytes(contents)
            self.paths.append(path)

    def test_valid_synthetic_custody_keeps_nulls(self):
        result = validate(self.ledger, self.paths)
        self.assertEqual(result["catalog_decay_day_only"], "1963-11-08")
        self.assertEqual(result["source_independence"], "SAME_NASA_SSR_SERIES_NOT_TWO_TRACKING_SENSORS")
        for key in ("historical_tle_pairs", "measurement_sigma", "frame", "terminal_time_or_position"):
            self.assertIsNone(result[key])
        self.assertEqual(result["conde_outcome"], "INDETERMINATE")
        self.assertFalse(result["human_visual_extraction_reproduced_by_ci"])

    def test_changed_byte_rejected(self):
        self.paths[0].write_bytes(self.paths[0].read_bytes() + b"X")
        with self.assertRaisesRegex(ValueError, "complete PDF"):
            validate(self.ledger, self.paths)

    def test_syntactically_valid_pdf_with_changed_digest_rejected(self):
        self.paths[1].write_bytes(b"%PDF-1.4\nchanged\n%%EOF\n")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            validate(self.ledger, self.paths)

    def test_reversed_files_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            validate(self.ledger, list(reversed(self.paths)))

    def test_non_pdf_rejected_even_with_matching_sha(self):
        content = b"garbage not a PDF"
        self.paths[0].write_bytes(content)
        self.ledger["sources"][0]["sha256"] = hashlib.sha256(content).hexdigest()
        with self.assertRaisesRegex(ValueError, "complete PDF"):
            validate(self.ledger, self.paths)

    def test_missing_one_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "both NASA PDF"):
            validate(self.ledger, self.paths[:1])

    def test_source_id_changed_rejected(self):
        self.ledger["sources"][0]["ntrs_id"] = "19640002493"
        with self.assertRaisesRegex(ValueError, "sequence"):
            validate(self.ledger, self.paths)

    def test_unreviewed_pdf_page_rejected(self):
        self.ledger["sources"][1]["page_index_zero_based"] = 8
        with self.assertRaisesRegex(ValueError, "page reference"):
            validate(self.ledger, self.paths)

    def test_ocr_claim_rejected(self):
        self.ledger["sources"][0]["reading_method"] = "OCR"
        with self.assertRaisesRegex(ValueError, "manual review"):
            validate(self.ledger, self.paths)

    def test_modified_decay_day_rejected(self):
        self.ledger["sources"][0]["human_table_observation"]["decay_day"] = "1963-11-09"
        with self.assertRaisesRegex(ValueError, "15 Nov"):
            validate(self.ledger, self.paths)

    def test_nonincremental_nov30_rejected(self):
        self.ledger["sources"][1]["human_table_observation"]["kind"] = "COMPLETE_DECAYED_LIST"
        with self.assertRaisesRegex(ValueError, "incremental additions"):
            validate(self.ledger, self.paths)

    def test_false_repeat_nov30_rejected(self):
        self.ledger["sources"][1]["human_table_observation"]["1963_3B_in_additions"] = True
        with self.assertRaisesRegex(ValueError, "incremental additions"):
            validate(self.ledger, self.paths)

    def test_reversed_date_rejected(self):
        self.ledger["sources"][1]["publication_date"] = "1963-11-01"
        with self.assertRaisesRegex(ValueError, "chronology"):
            validate(self.ledger, self.paths)

    def test_url_identifier_mismatch_rejected(self):
        self.ledger["sources"][0]["url"] = "https://ntrs.nasa.gov/api/citations/19640001198/downloads/other.pdf"
        with self.assertRaisesRegex(ValueError, "URL/id"):
            validate(self.ledger, self.paths)


if __name__ == "__main__":
    unittest.main()
