"""C241-R80: first-caderno custody, page claims and adversarial scope checks."""

import copy
import hashlib
import json
import unittest
from pathlib import Path

from test_correio_manha_tartaruga_r79 import (
    MANIFEST as R79_MANIFEST,
    validate as validate_r79,
)

MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R80.json"
)
CANONICAL_SHA256 = "46c6b38f0b2786256ce76cc28898a334c57bb825ec6ce3ed496be255ff115d3d"
PDF_SHA256 = "a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0"
READ = [9, 10, 11, 12]
CUMULATIVE = list(range(1, 13)) + [21]
REMAINING = [p for p in range(1, 29) if p not in CUMULATIVE]


def validate(document, parent=None):
    """Fail closed on invented times, coverage, source identity and lineage."""
    if parent is None:
        parent = json.loads(R79_MANIFEST.read_text(encoding="utf-8"))
    validate_r79(parent)

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(set(document) == {
        "schema", "id", "issue", "checked_utc_date", "source", "reading", "conclusion"
    }, "root fields")
    require(document["schema"] == "conde.local_clock_visual_pages/v1", "schema")
    require(document["id"] == "C241-TARTARUGA-R80" and
            document["issue"] == 871, "identity/issue")
    require(document["checked_utc_date"] == "2026-11-15", "review date")

    source = document["source"]
    require(source == parent["source"], "source must equal R79")
    require(source["sha256"] == PDF_SHA256, "PDF original")
    require(source["bytes"] == 22546215 and
            source["pdf_page_count"] == 28, "size/count")

    reading = document["reading"]
    require(reading["new_pages_fully_examined"] == READ, "new pages")
    require(reading["previous_pages_fully_examined"] ==
            parent["reading"]["cumulative_pages_fully_examined"], "parent pages")
    require(reading["cumulative_pages_fully_examined"] == CUMULATIVE,
            "cumulative pages")
    require(reading["cumulative_pages_not_fully_examined"] == REMAINING,
            "remaining pages")
    require(reading["first_caderno_pdf_pages"] == list(range(1, 13)),
            "first-caderno boundary")
    require(reading["second_caderno_starts_at_pdf_page"] == 13,
            "second-caderno boundary")
    require(reading["first_caderno_fully_examined"] is True,
            "first-caderno status")
    require(reading["second_caderno_remaining_panorama_only"] ==
            [13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28],
            "panorama is not full reading")
    require(reading["edition_fully_examined"] is False, "edition overclaim")
    require(reading["global_negative_asserted"] is False, "global negative")
    require(reading["correio_10_nov_full_edition_examined"] is False,
            "Cervo's edition")

    rows = reading["status_by_pdf_page"]
    require(len(rows) == 4, "page count")
    for page, row in zip(READ, rows, strict=True):
        require(row["pdf_page"] == page, "PDF page id")
        require(row["printed_page"] == (page if page != 12 else None),
                "printed folio must not be invented")
        require(row["status"] == "EXAMINADA", "reading status")
        require(row["relevant_article"] is None, "invented Conde article")
        require(row["conde_event_time_literal"] is None, "invented event time")
        require(row["conde_eyewitness"] is None, "invented eyewitness")
        require(row["orbital_constraint_activated"] is False,
                "orbital overclaim")
    require(rows[3]["printed_folio_status"] ==
            "UNNUMBERED_MASTHEAD_FIRST_CADERNO", "printed folio evidence")
    require(rows[3]["section"].startswith("1.º Caderno"), "section name")

    conclusion = document["conclusion"]
    require(conclusion["classification"] ==
            "NO_INDEPENDENT_CONDE_EVENT_HOUR_IN_COMPLETE_FIRST_CADERNO_AND_EARLIER_PAGE_21",
            "classification")
    require(conclusion["conde_event_time_literal"] is None, "global clock")
    require(conclusion["conde_eyewitness"] is None, "global witness")
    require(conclusion["source_of_report_independent_from_tupi_fbis"] ==
            "UNDETERMINED", "independence")
    require(conclusion["orbital_constraint_activated"] is False,
            "physical exclusion")

    canonical = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "unreviewed interpretation mutation")
    return True


class TestC241R80(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertTrue(validate(self.good))

    def reject(self, path, value):
        changed = copy.deepcopy(self.good)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(changed)

    def test_event_hour_fabrication(self):
        self.reject(("reading", "status_by_pdf_page", 0,
                     "conde_event_time_literal"), "21h07")

    def test_event_witness_fabrication(self):
        self.reject(("reading", "status_by_pdf_page", 3,
                     "conde_eyewitness"), "testemunha fictícia")

    def test_prose_fabrication(self):
        self.reject(("reading", "status_by_pdf_page", 1,
                     "subjects"), "NASA confirma queda em Conde às 20h")

    def test_parent_lineage_fabrication(self):
        parent = json.loads(R79_MANIFEST.read_text(encoding="utf-8"))
        parent["reading"]["status_by_pdf_page"][0]["subjects"] = (
            "NASA confirma queda em Conde às 20h"
        )
        with self.assertRaises(ValueError):
            validate(self.good, parent)

    def test_unprinted_folio_fabricated(self):
        self.reject(("reading", "status_by_pdf_page", 3, "printed_page"), 12)

    def test_section_boundary_mutation(self):
        self.reject(("reading", "second_caderno_starts_at_pdf_page"), 12)

    def test_unread_pages_promoted(self):
        self.reject(("reading", "cumulative_pages_fully_examined"),
                    list(range(1, 29)))

    def test_unread_pages_dropped(self):
        self.reject(("reading", "cumulative_pages_not_fully_examined"), [])

    def test_panorama_promoted(self):
        self.reject(("reading", "second_caderno_remaining_panorama_only"), [])

    def test_full_edition_overclaim(self):
        self.reject(("reading", "edition_fully_examined"), True)

    def test_global_negative_overclaim(self):
        self.reject(("reading", "global_negative_asserted"), True)

    def test_wrong_edition(self):
        self.reject(("source", "edition_number_visual"), "21.658")

    def test_wrong_pdf_digest(self):
        self.reject(("source", "sha256"), "0" * 64)

    def test_promoted_independence(self):
        self.reject(("conclusion", "source_of_report_independent_from_tupi_fbis"),
                    "CONFIRMED")

    def test_promoted_orbital_constraint(self):
        self.reject(("conclusion", "orbital_constraint_activated"), True)

    def test_unreviewed_extra_claim(self):
        changed = copy.deepcopy(self.good)
        changed["is_spacecraft_fragment"] = True
        with self.assertRaises(ValueError):
            validate(changed)


if __name__ == "__main__":
    unittest.main()
