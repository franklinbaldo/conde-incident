"""Adversarial checks: a Soviet printed row does not become independent tracking."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/tle_custody/soviet_bse1964_1963_003_C241_LONTRA_R48.json"

import sys
sys.path.insert(0, str(ROOT / "tools"))
from verify_soviet_bse1964_pdf_r48 import verify_pdf


def require(condition):
    if not condition:
        raise AssertionError("False archival/orbital promotion")


def validate(m):
    require(m["schema"] == "conde.archival_locator_custody/v1")
    require(m["id"] == "C241-LONTRA-R48")
    require(m["work"]["publication_year"] == 1964)
    require(m["work"]["section_pdf"] ==
            "https://istmat.org/files/uploads/35454/14_nauka_i_tehnika.pdf")
    require(m["work"]["printed_page"] == 503)
    require(m["work"]["section_pdf_page_one_based"] == 7)
    c = m["document_custody"]
    require(c["pdf_retrieved"] is True and c["pdf_page_7_visually_inspected"] is True)
    require(c["pdf_bytes"] == 23846637)
    require(c["pdf_page_count"] == 70)
    require(c["pdf_sha256"] ==
            "d2372fe5b073c95366681bf550a0688ee47a6d2b6c4c612125e006a79fcdc613")
    require(c["archival_print_source_physically_inspected"] is False)
    row = m["printed_table_row"]
    require(row["row_number"] == 3)
    require(row["launch_date_printed"] == "16.01")
    require(row["launch_date_inferred_year_from_heading"] == 1963)
    require(row["satellite_designation_printed"] == "Секретный")
    require(row["rocket_printed"] == "Тор — Аджена D")
    require(row["perigee_km_printed"] == 459)
    require(row["apogee_km_printed"] == 533)
    require(row["period_minutes_printed"] == 94.66)
    require(row["inclination_degrees_printed"] == 81.89)
    require(all(row[k] is None for k in (
        "norad_identifier_printed", "cospar_identifier_printed",
        "observation_epoch_printed", "sensor_identifier_printed",
        "raan_degrees_printed")))
    genealogy = m["source_genealogy"]
    require(len(genealogy["print_footnote_periodicals"]) == 5)
    require("Aviation Week" in genealogy["print_footnote_periodicals"])
    require(genealogy["independent_tracking_source_proven"] is False)
    require(genealogy["direct_soviet_station_measurement_claimed"] is False)
    require(genealogy["same_launch_day_is_unique_satellite_identification"] is False)
    target = m["target"]
    require(target["norad"] == [527, 528, 529])
    require(target["designations"] == ["1963-003A", "1963-003B", "1963-003C"])
    require(target["printed_row_explicitly_ids_any_target"] is False)
    require(target["independent_measurements_retrieved"] == 0)
    require(target["new_orbital_constraints_activated"] == 0)
    require(target["matches_november_7_9_1963_window"] is False)
    require(target["relation"] == "DATE_MATCH_ONLY_UNRESOLVED_GENEALOGY")
    require(m["external_archive_contact_sent"] is False)


class SovietBSE1964R48(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads(PATH.read_text(encoding="utf-8"))

    def test_real_evidence(self):
        validate(self.m)

    def mutate_and_reject(self, edits):
        m = copy.deepcopy(self.m)
        edits(m)
        with self.assertRaises(AssertionError):
            validate(m)

    def test_forged_norad_label(self):
        self.mutate_and_reject(
            lambda m: m["printed_table_row"].__setitem__("norad_identifier_printed", 528))

    def test_unsupported_station_observation_epoch(self):
        self.mutate_and_reject(
            lambda m: m["printed_table_row"].__setitem__("observation_epoch_printed",
                                                          "1963-11-08T00:00:00Z"))

    def test_missing_source_independence(self):
        self.mutate_and_reject(
            lambda m: m["source_genealogy"].__setitem__("independent_tracking_source_proven", True))

    def test_same_launch_not_unique_object(self):
        self.mutate_and_reject(
            lambda m: m["source_genealogy"].__setitem__(
                "same_launch_day_is_unique_satellite_identification", True))

    def test_wrong_inc_is_rejected(self):
        self.mutate_and_reject(
            lambda m: m["printed_table_row"].__setitem__("inclination_degrees_printed", 82.89))

    def test_forged_target_measurement(self):
        self.mutate_and_reject(
            lambda m: m["target"].__setitem__("independent_measurements_retrieved", 1))

    def test_no_november_observation(self):
        self.mutate_and_reject(
            lambda m: m["target"].__setitem__("matches_november_7_9_1963_window", True))

    def test_no_orbital_activation(self):
        self.mutate_and_reject(
            lambda m: m["target"].__setitem__("new_orbital_constraints_activated", 1))

    def test_no_mistaken_printed_page(self):
        self.mutate_and_reject(lambda m: m["work"].__setitem__("printed_page", 7))

    def test_no_unverified_pdf_hash(self):
        self.mutate_and_reject(
            lambda m: m["document_custody"].__setitem__("pdf_sha256", "0" * 64))

    def test_western_bibliography_not_erased(self):
        self.mutate_and_reject(
            lambda m: m["source_genealogy"].__setitem__("print_footnote_periodicals", []))

    def test_integrity_verifier_rejects_sha_mutation(self):
        raw = b"%PDF-1.4\nsome content\n%%EOF\n"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.pdf"
            p.write_bytes(raw)
            with self.assertRaises(ValueError):
                verify_pdf(p, len(raw), "0" * 64, check_page_count=False)

    def test_integrity_verifier_rejects_bad_header(self):
        raw = b"NO-PDF-1.4\nsome content\n%%EOF\n"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.pdf"
            p.write_bytes(raw)
            with self.assertRaises(ValueError):
                verify_pdf(p, len(raw), hashlib.sha256(raw).hexdigest(),
                           check_page_count=False)

    def test_integrity_verifier_rejects_truncation(self):
        raw = b"%PDF-1.4\nsome content\n%%EOF\n"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.pdf"
            p.write_bytes(raw[:-4])
            with self.assertRaises(ValueError):
                verify_pdf(p, len(raw), hashlib.sha256(raw).hexdigest(),
                           check_page_count=False)


if __name__ == "__main__":
    unittest.main()
