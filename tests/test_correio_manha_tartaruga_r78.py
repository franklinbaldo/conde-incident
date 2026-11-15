"""C241-R78: fail-closed scope for Correio da Manhã pages 3 and 4."""

import copy
import hashlib
import json
import unittest
from pathlib import Path

from test_correio_manha_tartaruga_r77 import (
    MANIFEST as R77_MANIFEST, validate as validate_r77,
)
from test_correio_manha_tartaruga_r76 import MANIFEST as R76_MANIFEST


MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R78.json"
)
PDF_SHA = "a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0"
CANONICAL_SHA = "8364e18e52037b03ae97a796e8b622def8a5cc1e0dba3296b3012b666b562895"
PAGES = [3, 4]
CUMULATIVE = [1, 2, 3, 4, 5, 21]
REMAINING = [p for p in range(1, 29) if p not in CUMULATIVE]


def validate(document, parent=None, ancestor=None):
    """Validate R78 plus the complete R77→R76 interpretation ancestry."""
    if parent is None:
        parent = json.loads(R77_MANIFEST.read_text(encoding="utf-8"))
    validate_r77(parent, ancestor)

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(set(document) == {
        "schema", "id", "issue", "checked_utc_date", "source", "reading", "conclusion"
    }, "unexpected root field")
    require(document["schema"] == "conde.local_clock_visual_pages/v1", "schema")
    require(document["id"] == "C241-TARTARUGA-R78", "id")
    require(document["issue"] == 871, "issue")
    src = document["source"]
    require(src["collection_edition"] == "089842/21657", "edition")
    require(src["edition_date_visual"] == "1963-11-09", "date")
    require(src["edition_number_visual"] == "21.657", "number")
    require(src["bytes"] == 22546215 and src["pdf_page_count"] == 28, "source size")
    require(src["sha256"] == PDF_SHA, "PDF hash")
    require(src["pdf_original_reused_on_ifro"] is True, "provenance")

    reading = document["reading"]
    require(reading["new_pages_fully_examined"] == PAGES, "new scope")
    require(reading["previous_pages_fully_examined"] ==
            parent["reading"]["cumulative_pages_fully_examined"], "prior scope source-only")
    require(src["sha256"] == parent["source"]["sha256"], "prior PDF identity")
    require(reading["cumulative_pages_fully_examined"] == CUMULATIVE, "inflated coverage")
    require(reading["cumulative_pages_not_fully_examined"] == REMAINING, "remaining pages")
    require(reading["edition_fully_examined"] is False, "fake edition-wide read")
    require(reading["global_negative_asserted"] is False, "fake global negative")
    require(reading["correio_10_nov_full_edition_examined"] is False, "other edition")
    require(len(reading["status_by_pdf_page"]) == 2, "row count")
    for page, row in zip(PAGES, reading["status_by_pdf_page"], strict=True):
        require(row["pdf_page"] == page and row["printed_page"] == page, "folio")
        require(row["status"] == "EXAMINADA", "page status")
        require(row["section"] == "1.º Caderno", "section")
        require(row["relevant_article"] is None, "unverified Conde article")
        require(row["conde_event_time_literal"] is None, "invented time")
        require(row["conde_eyewitness"] is None, "invented witness")
        require(row["orbital_constraint_activated"] is False, "physical overclaim")
    conclusion = document["conclusion"]
    require(conclusion["classification"] ==
            "NO_NEW_CONDE_EVENT_HOUR_IN_TWO_ADDITIONAL_FULLY_READ_PAGES",
            "classification")
    require(conclusion["conde_event_time_literal"] is None, "conclusion clock")
    require(conclusion["conde_eyewitness"] is None, "conclusion witness")
    require(conclusion["source_of_report_independent_from_tupi_fbis"] ==
            "UNDETERMINED", "unearned independence")
    require(conclusion["orbital_constraint_activated"] is False, "orbit exclusion")

    canonical = json.dumps(document, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA,
            "manifest interpretation changed without review")
    return True


class TestC241R78(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertTrue(validate(self.good))

    def test_reject_mutated_R77_source_only(self):
        parent = json.loads(R77_MANIFEST.read_text(encoding="utf-8"))
        parent["reading"]["status_by_pdf_page"][0]["subjects"] = (
            "NASA confirma Conde às 20h15 (mutante sintético)"
        )
        with self.assertRaises(ValueError):
            validate(self.good, parent)

    def test_reject_mutated_R76_grandparent_only(self):
        ancestor = json.loads(R76_MANIFEST.read_text(encoding="utf-8"))
        ancestor["reading"]["status_by_pdf_page"][0]["reading_scope"] = (
            "NASA confirma Conde às 20h15 (mutante sintético)"
        )
        with self.assertRaises(ValueError):
            validate(self.good, ancestor=ancestor)

    def reject(self, path, value):
        changed = copy.deepcopy(self.good)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(changed)

    def test_fabricated_hour(self):
        self.reject(("reading", "status_by_pdf_page", 0, "conde_event_time_literal"), "20h15")

    def test_fabricated_witness(self):
        self.reject(("reading", "status_by_pdf_page", 1, "conde_eyewitness"), "observer")

    def test_fabricated_in_prose(self):
        self.reject(("reading", "status_by_pdf_page", 1, "subjects"),
                    "Conde 20h15; eyewitness identifies NORAD 528")

    def test_wrong_folio(self):
        self.reject(("reading", "status_by_pdf_page", 0, "printed_page"), 11)

    def test_fake_full_edition(self):
        self.reject(("reading", "edition_fully_examined"), True)

    def test_global_negative(self):
        self.reject(("reading", "global_negative_asserted"), True)

    def test_inflated_count(self):
        self.reject(("reading", "cumulative_pages_fully_examined"), list(range(1, 29)))

    def test_missing_remaining_page(self):
        self.reject(("reading", "cumulative_pages_not_fully_examined"), [])

    def test_changed_source_hash(self):
        self.reject(("source", "sha256"), "0" * 64)

    def test_wrong_edition(self):
        self.reject(("source", "edition_number_visual"), "21.658")

    def test_promoted_independence(self):
        self.reject(("conclusion", "source_of_report_independent_from_tupi_fbis"),
                    "CONFIRMED")

    def test_promoted_orbit(self):
        self.reject(("conclusion", "orbital_constraint_activated"), True)

    def test_extra_claim(self):
        changed = copy.deepcopy(self.good)
        changed["confirmed_norad_528"] = True
        with self.assertRaises(ValueError):
            validate(changed)


if __name__ == "__main__":
    unittest.main()
