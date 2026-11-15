"""C241-R79: custody and fail-closed page scope for Correio 9 Nov 1963."""

import copy
import hashlib
import json
import unittest
from pathlib import Path

from test_correio_manha_tartaruga_r78 import (
    MANIFEST as R78_MANIFEST,
    validate as validate_r78,
)

MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R79.json"
)
PDF_SHA256 = "a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0"
CANONICAL_SHA256 = "6795d9d37194e80f31425141d707bcd0c1d2b0a58c820eb087190d42c750df1e"
READ = [6, 7, 8]
CUMULATIVE = [1, 2, 3, 4, 5, 6, 7, 8, 21]
REMAINING = [p for p in range(1, 29) if p not in CUMULATIVE]


def validate(document, parent=None):
    """Validate complete R79 interpretation and R78/R77/R76 ancestry."""
    if parent is None:
        parent = json.loads(R78_MANIFEST.read_text(encoding="utf-8"))
    validate_r78(parent)

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(set(document) == {
        "schema", "id", "issue", "checked_utc_date", "source", "reading", "conclusion"
    }, "unexpected root field")
    require(document["schema"] == "conde.local_clock_visual_pages/v1", "schema")
    require(document["id"] == "C241-TARTARUGA-R79", "id")
    require(document["issue"] == 871, "issue")

    source = document["source"]
    require(source["collection_edition"] == "089842/21657", "edition")
    require(source["edition_date_visual"] == "1963-11-09", "date")
    require(source["edition_number_visual"] == "21.657", "number")
    require(source["bytes"] == 22546215 and source["pdf_page_count"] == 28,
            "PDF size/count")
    require(source["sha256"] == PDF_SHA256, "PDF hash")
    require(source["pdf_original_reused_on_ifro"] is True, "provenance")
    require(source["sha256"] == parent["source"]["sha256"], "ancestry PDF identity")

    reading = document["reading"]
    require(reading["new_pages_fully_examined"] == READ, "page scope")
    require(reading["previous_pages_fully_examined"] ==
            parent["reading"]["cumulative_pages_fully_examined"], "parent scope")
    require(reading["cumulative_pages_fully_examined"] == CUMULATIVE,
            "inflated cumulative coverage")
    require(reading["cumulative_pages_not_fully_examined"] == REMAINING,
            "unread coverage")
    require(reading["edition_fully_examined"] is False, "edition-wide overclaim")
    require(reading["global_negative_asserted"] is False, "global negative")
    require(reading["correio_10_nov_full_edition_examined"] is False,
            "other edition")
    rows = reading["status_by_pdf_page"]
    require(len(rows) == len(READ), "row count")
    for page, row in zip(READ, rows, strict=True):
        require(row["pdf_page"] == page and row["printed_page"] == page,
                "printed/PDF folio")
        require(row["section"] == "1.º Caderno", "section")
        require(row["status"] == "EXAMINADA", "status")
        require(row["relevant_article"] is None, "invented Conde article")
        require(row["conde_event_time_literal"] is None, "invented Conde clock")
        require(row["conde_eyewitness"] is None, "invented eyewitness")
        require(row["orbital_constraint_activated"] is False,
                "unearned orbital exclusion")

    conclusion = document["conclusion"]
    require(conclusion["classification"] ==
            "NO_NEW_CONDE_EVENT_HOUR_IN_THREE_ADDITIONAL_FULLY_READ_PAGES",
            "classification")
    require(conclusion["conde_event_time_literal"] is None, "final clock")
    require(conclusion["conde_eyewitness"] is None, "final witness")
    require(conclusion["source_of_report_independent_from_tupi_fbis"] ==
            "UNDETERMINED", "unearned independence")
    require(conclusion["orbital_constraint_activated"] is False,
            "physical overclaim")

    canonical = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "manifest interpretation changed without review")
    return True


class TestC241R79(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertTrue(validate(self.good))

    def reject(self, path, value):
        changed = copy.deepcopy(self.good)
        current = changed
        for key in path[:-1]:
            current = current[key]
        current[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(changed)

    def test_fabricated_time(self):
        self.reject(("reading", "status_by_pdf_page", 0,
                     "conde_event_time_literal"), "20h40")

    def test_fabricated_witness(self):
        self.reject(("reading", "status_by_pdf_page", 1,
                     "conde_eyewitness"), "local eyewitness")

    def test_source_only_prose_mutation(self):
        self.reject(("reading", "status_by_pdf_page", 2, "subjects"),
                    "NASA confirma queda em Conde às 20h15")

    def test_r78_parent_prose_mutation(self):
        parent = json.loads(R78_MANIFEST.read_text(encoding="utf-8"))
        parent["reading"]["status_by_pdf_page"][0]["subjects"] = (
            "NASA confirma queda em Conde às 20h15"
        )
        with self.assertRaises(ValueError):
            validate(self.good, parent)

    def test_wrong_folio(self):
        self.reject(("reading", "status_by_pdf_page", 1, "printed_page"), 12)

    def test_inflated_edition_coverage(self):
        self.reject(("reading", "cumulative_pages_fully_examined"),
                    list(range(1, 29)))

    def test_missing_unread_page(self):
        self.reject(("reading", "cumulative_pages_not_fully_examined"), [])

    def test_global_negative(self):
        self.reject(("reading", "global_negative_asserted"), True)

    def test_fake_full_edition(self):
        self.reject(("reading", "edition_fully_examined"), True)

    def test_wrong_edition(self):
        self.reject(("source", "edition_number_visual"), "21.658")

    def test_wrong_pdf_digest(self):
        self.reject(("source", "sha256"), "0" * 64)

    def test_promoted_independence(self):
        self.reject(("conclusion", "source_of_report_independent_from_tupi_fbis"),
                    "CONFIRMED")

    def test_promoted_orbital_constraint(self):
        self.reject(("conclusion", "orbital_constraint_activated"), True)

    def test_extra_claim(self):
        changed = copy.deepcopy(self.good)
        changed["confirmed_norad_528"] = True
        with self.assertRaises(ValueError):
            validate(changed)


if __name__ == "__main__":
    unittest.main()
