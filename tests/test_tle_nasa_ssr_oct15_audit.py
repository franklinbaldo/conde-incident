"""Adversarial no-network controls for primary NASA publication custody."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from tools.tle_nasa_ssr_oct15_audit import audit, validate_ledger

LEDGER = (Path(__file__).resolve().parents[1] /
          "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json")


class Oct15AuditTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(LEDGER.read_text(encoding="utf-8"))

    def bad(self, transform):
        d = copy.deepcopy(self.data)
        transform(d)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate_ledger(d)

    def test_three_rows_are_preserved(self):
        r = validate_ledger(self.data)
        self.assertEqual([x["international_designator"] for x in r],
                         ["1963-003A", "1963-003B", "1963-003C"])

    def test_reciprocal_not_tle_mean_motion(self):
        r = validate_ledger(self.data)
        self.assertEqual(r[1]["nodal_period_min_as_printed"], "92.4")
        self.assertNotIn("tle_mean_motion", r[1])
        self.assertEqual(r[1]["nodal_cycles_per_day_reciprocal_not_tle_mean_motion"],
                         str(__import__("decimal").Decimal(1440) /
                             __import__("decimal").Decimal("92.4")))

    def test_wrong_source_id(self):
        self.bad(lambda d: d["source"].update(ntrs_id="19640001198"))

    def test_wrong_file_hash(self):
        self.bad(lambda d: d["source"].update(sha256="0" * 64))

    def test_wrong_file_size(self):
        self.bad(lambda d: d["source"].update(bytes=1))

    def test_wrong_printed_page(self):
        self.bad(lambda d: d["source"].update(page_printed=8))

    def test_wrong_pdf_page(self):
        self.bad(lambda d: d["source"].update(page_index_zero_based=7))

    def test_suppress_index_typo(self):
        self.bad(lambda d: d["source"].update(ntrs_metadata_report_number="X-533-63-1"))

    def test_falsely_claim_ocr(self):
        self.bad(lambda d: d["source"].update(transcription_method="OCR_VERIFIED"))

    def test_one_missing_row(self):
        self.bad(lambda d: d["catalog_rows"].pop())

    def test_duplicate_row(self):
        self.bad(lambda d: d["catalog_rows"].__setitem__(2, d["catalog_rows"][1]))

    def test_period_mutation(self):
        self.bad(lambda d: d["catalog_rows"][1].update(nodal_period_min_printed="92.5"))

    def test_apogee_mutation(self):
        self.bad(lambda d: d["catalog_rows"][1].update(apogee_km_printed=400))

    def test_fabricated_raan(self):
        self.bad(lambda d: d["epistemic"].update(raan_deg="198.5261"))

    def test_fabricated_frame(self):
        self.bad(lambda d: d["epistemic"].update(physical_reference_frame="TEME"))

    def test_legacy_activated(self):
        self.bad(lambda d: d["epistemic"].update(legacy_raan_2841520_as_observation=True))

    def test_fabricated_terminal_time(self):
        self.bad(lambda d: d["epistemic"].update(terminal_time="1963-11-08T23:59:00Z"))

    def test_missing_intermediate_edition_is_preserved(self):
        self.bad(lambda d: d["cross_edition"].update(edition_21="CONFIRMED_ABSENT"))

    def test_non_pdf_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a PDF"):
            audit(self.data, b"not a PDF")

    def test_wrong_pdf_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "hash or byte-count"):
            audit(self.data, b"%PDF-1.4\n" + b"FAKE" * 100 + b"\n%%EOF\n")


if __name__ == "__main__":
    unittest.main()
