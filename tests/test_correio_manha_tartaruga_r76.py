"""Scope guards for C241-R76: two pages cannot become an edition-wide negative."""

import copy
import hashlib
import json
import unittest
from pathlib import Path


MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R76.json"
)
PDF_SHA256 = "a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0"
CANONICAL_SHA256 = "1fce0aad42f3130cb5afb5bd02effde0b16e10dae87de08b8426b4d9e40c73b4"
READ_PAGES = (5, 21)
REMAINING = tuple(p for p in range(1, 29) if p not in READ_PAGES)


def validate(document):
    """Reject a changed custody, page scope, invented Conde hour or orbital claim."""
    def check(condition, reason):
        if not condition:
            raise ValueError(reason)

    check(set(document) == {"schema", "id", "issue", "checked_utc_date", "source", "reading", "conclusion"},
          "unexpected top-level claim")
    check(document["schema"] == "conde.local_clock_visual_pages/v1", "wrong schema")
    check(document["id"] == "C241-TARTARUGA-R76" and document["issue"] == 871, "wrong source identity")

    source = document["source"]
    check(source["collection_edition"] == "089842/21657", "wrong original")
    check(source["edition_date_visual"] == "1963-11-09", "wrong date")
    check(source["edition_number_visual"] == "21.657", "wrong edition")
    check(source["sha256"] == PDF_SHA256, "source PDF hash changed")
    check(source["bytes"] == 22546215 and source["pdf_page_count"] == 28, "source size/pages changed")
    check(source["pdf_original_reused_on_ifro"] is True, "wrong provenance")

    reading = document["reading"]
    check(reading["pages_fully_examined"] == list(READ_PAGES), "scope inflated")
    check(reading["pages_not_fully_examined"] == list(REMAINING), "incomplete remaining set")
    check(reading["edition_fully_examined"] is False, "false full-edition claim")
    check(reading["global_negative_asserted"] is False, "false global negative")
    check(reading["panoramic_overview_is_not_full_reading"] is True, "panorama promoted")
    check(reading["individual_article_previously_read_in_R74_is_not_page_level_negative"] is True, "R74 promoted")
    check(reading["correio_10_nov_full_edition_examined"] is False, "false second edition")
    page_rows = reading["status_by_pdf_page"]
    check(len(page_rows) == 2, "wrong count of pages read")
    for row, page, printed, section in zip(page_rows, READ_PAGES, (5, 9),
                                            ("1.º Caderno", "2.º Caderno"), strict=True):
        check(row["pdf_page"] == page and row["printed_page"] == printed, "page label mismatch")
        check(row["section"] == section and row["status"] == "EXAMINADA", "page status")
        check(row["conde_event_time_literal"] is None, "invented Conde clock")
        check(row["conde_eyewitness"] is None, "invented Conde witness")
        check(row["orbital_constraint_activated"] is False, "invented orbital constraint")
    check(page_rows[0]["reported_location"] == "IGUAPE_SP_RIO_PEROPAVA", "Iguape conflated")
    check(page_rows[0]["original_report_credit"] == "IGUAPE (Do enviado especial da sucursal SP)", "false credit")
    check(page_rows[1]["relevant_article"] is None, "unverified relevant article")

    result = document["conclusion"]
    check(result["classification"] == "NO_NEW_CONDE_EVENT_HOUR_IN_TWO_FULLY_READ_PAGES",
          "false result")
    check(result["conde_event_time_literal"] is None and result["conde_eyewitness"] is None,
          "invented event confirmation")
    check(result["orbital_constraint_activated"] is False, "false orbital exclusion")
    check(result["source_of_report_independent_from_tupi_fbis"] == "UNDETERMINED",
          "false independence claim")
    canonical = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    check(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
          "full R76 interpretative record changed")
    return True


class TestR76(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.good))

    def test_reject_invented_conde_time(self):
        self.mutate(("reading", "status_by_pdf_page", 0, "conde_event_time_literal"), "20h40")

    def test_reject_invented_witness(self):
        self.mutate(("reading", "status_by_pdf_page", 1, "conde_eyewitness"), "Testemunha X")

    def test_reject_false_full_edition(self):
        self.mutate(("reading", "edition_fully_examined"), True)

    def test_reject_false_global_negative(self):
        self.mutate(("reading", "global_negative_asserted"), True)

    def test_reject_fake_page(self):
        self.mutate(("reading", "pages_fully_examined"), [1, 5, 21])

    def test_reject_wrong_hash(self):
        self.mutate(("source", "sha256"), "0" * 64)

    def test_reject_published_date_as_event(self):
        self.mutate(("conclusion", "conde_event_time_literal"), "1963-11-09T20:40")

    def test_reject_orbital_activation(self):
        self.mutate(("reading", "status_by_pdf_page", 0, "orbital_constraint_activated"), True)

    def test_reject_false_independence(self):
        self.mutate(("conclusion", "source_of_report_independent_from_tupi_fbis"), "CONFIRMED")

    def test_reject_extra_claim(self):
        altered = copy.deepcopy(self.good)
        altered["new_satellite_identity"] = "528"
        with self.assertRaises(ValueError):
            validate(altered)

    def test_reject_fabricated_prose_only(self):
        self.mutate(
            ("reading", "status_by_pdf_page", 0, "reading_scope"),
            "NASA confirma queda em Conde às 20h15 (mutante sintético)",
        )

    def test_reject_interpretive_metadata_only(self):
        self.mutate(
            ("conclusion", "further_action"),
            "Testemunha em Conde teria visto NORAD 528 (mutante sintético)",
        )

    def mutate(self, path, value):
        altered = copy.deepcopy(self.good)
        parent = altered
        for step in path[:-1]:
            parent = parent[step]
        parent[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(altered)


if __name__ == "__main__":
    unittest.main()
