"""C241-R77: guard reading scope of the Correio da Manhã edition 21657."""

import copy
import hashlib
import json
import unittest
from pathlib import Path


MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R77.json"
)
ORIGINAL_SHA256 = "a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0"
CANONICAL_SHA256 = "d919eaf19b9808b88957368cb21381f569878a8c0181b355eb9e2246b79cb85b"
READ = [1, 2]
CUMULATIVE = [1, 2, 5, 21]
REMAINING = [p for p in range(1, 29) if p not in CUMULATIVE]


def validate(document):
    """Fail closed if a partial historical read is silently promoted."""
    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(set(document) == {
        "schema", "id", "issue", "checked_utc_date", "source", "reading", "conclusion"
    }, "unexpected top-level field")
    require(document["schema"] == "conde.local_clock_visual_pages/v1", "schema")
    require(document["id"] == "C241-TARTARUGA-R77", "source id")
    require(document["issue"] == 871, "issue id")
    s = document["source"]
    require(s["collection_edition"] == "089842/21657", "edition")
    require(s["edition_date_visual"] == "1963-11-09", "date")
    require(s["edition_number_visual"] == "21.657", "number")
    require(s["bytes"] == 22546215 and s["pdf_page_count"] == 28, "source size")
    require(s["sha256"] == ORIGINAL_SHA256, "source hash")
    require(s["pdf_original_reused_on_ifro"] is True, "custody")

    r = document["reading"]
    require(r["new_pages_fully_examined"] == READ, "new page list")
    require(r["previous_pages_fully_examined"] == [5, 21], "prior certified scope")
    require(r["cumulative_pages_fully_examined"] == CUMULATIVE, "inflated coverage")
    require(r["cumulative_pages_not_fully_examined"] == REMAINING, "remaining coverage")
    require(r["edition_fully_examined"] is False, "unearned edition negative")
    require(r["global_negative_asserted"] is False, "invented global negative")
    require(r["correio_10_nov_full_edition_examined"] is False, "other edition")
    require(len(r["status_by_pdf_page"]) == 2, "wrong rows")
    for page, row in zip(READ, r["status_by_pdf_page"], strict=True):
        require(row["pdf_page"] == page and row["printed_page"] == page, "folio")
        require(row["section"] == "1.º Caderno", "section")
        require(row["status"] == "EXAMINADA", "reading status")
        require(row["relevant_article"] is None, "unverified article")
        require(row["conde_event_time_literal"] is None, "invented event time")
        require(row["conde_eyewitness"] is None, "invented eyewitness")
        require(row["orbital_constraint_activated"] is False, "orbital overclaim")
    c = document["conclusion"]
    require(
        c["classification"]
        == "NO_NEW_CONDE_EVENT_HOUR_IN_TWO_ADDITIONAL_FULLY_READ_PAGES",
        "classification",
    )
    require(c["conde_event_time_literal"] is None, "invented final hour")
    require(c["conde_eyewitness"] is None, "invented final eyewitness")
    require(c["source_of_report_independent_from_tupi_fbis"] == "UNDETERMINED",
            "independence overclaim")
    require(c["orbital_constraint_activated"] is False, "false physical attribution")

    canonical = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "manifest interpreted text or metadata changed without review")
    return True


class TestC241R77(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_original(self):
        self.assertTrue(validate(self.good))

    def reject(self, path, value):
        changed = copy.deepcopy(self.good)
        node = changed
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(changed)

    def test_reject_fabricated_clock(self):
        self.reject(("reading", "status_by_pdf_page", 0, "conde_event_time_literal"), "20h40")

    def test_reject_fabricated_witness(self):
        self.reject(("reading", "status_by_pdf_page", 1, "conde_eyewitness"), "X")

    def test_reject_edition_wide_negative(self):
        self.reject(("reading", "global_negative_asserted"), True)

    def test_reject_fake_full_edition(self):
        self.reject(("reading", "edition_fully_examined"), True)

    def test_reject_wrong_historical_edition(self):
        self.reject(("source", "edition_number_visual"), "21.658")

    def test_reject_swapped_source_hash(self):
        self.reject(("source", "sha256"), "0" * 64)

    def test_reject_inflated_page_count(self):
        self.reject(("reading", "cumulative_pages_fully_examined"), list(range(1, 29)))

    def test_reject_corrupted_printed_folio(self):
        self.reject(("reading", "status_by_pdf_page", 0, "printed_page"), 8)

    def test_reject_event_clock_in_conclusion(self):
        self.reject(("conclusion", "conde_event_time_literal"), "1963-11-08T20:40")

    def test_reject_satellite_link(self):
        self.reject(("conclusion", "orbital_constraint_activated"), True)

    def test_reject_independence_claim(self):
        self.reject(("conclusion", "source_of_report_independent_from_tupi_fbis"), "CONFIRMED")

    def test_reject_subtle_claim_in_text(self):
        self.reject(("reading", "status_by_pdf_page", 0, "subjects"),
                    "Conde: eyewitness photographed a satellite")

    def test_reject_extra_field(self):
        changed = copy.deepcopy(self.good)
        changed["confirmed_528"] = True
        with self.assertRaises(ValueError):
            validate(changed)


if __name__ == "__main__":
    unittest.main()
