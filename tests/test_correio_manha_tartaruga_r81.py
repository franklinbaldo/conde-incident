"""C241-R81: authenticate press originals and prevent fabricated Conde timings."""

import copy
import hashlib
import json
import os
import unittest
from pathlib import Path


MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/archive/conde_correio_manha_1963_11_12_14_C241_TARTARUGA_R81.json"
)
CANONICAL_SHA256 = "133e9dad12bc7fe5db9f6d167c8e9cdc7bafbc318cfc69876107b9246f06a239"
EXPECTED = [
    ("21659", "1963-11-12", "21.659", 20179037,
     "a744f75a91462d2246ecf905353143ffe72a9c326ab0462a1241a4db3a2bc606",
     28, 15, 16, 15),
    ("21660", "1963-11-13", "21.660", 20333897,
     "497cd71b643be03f908e26c2e99100fd24908fb026ca33c8e1667d49ee897bc0",
     26, 12, 13, 11),
    ("21661", "1963-11-14", "21.661", 21320531,
     "d3b6301c192f8513c8a9a53a06d18eb47fc82b76fda45b6438bc1f416e8854e0",
     28, 13, 14, 13),
]


def read_document(path=MANIFEST):
    """Reject duplicate JSON keys instead of accepting the last value."""
    def no_duplicates(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate key " + key)
            obj[key] = value
        return obj

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicates)


def validate(document):
    """Independent runtime guards remain active under python -O."""
    def require(condition, reason):
        if not condition:
            raise ValueError(reason)

    require(set(document) == {
        "schema", "id", "issue", "checked_utc_date",
        "provenance", "sources", "reading", "conclusion"
    }, "root fields")
    require(document["schema"] == "conde.local_clock_press_nucleus/v1",
            "schema")
    require(document["id"] == "C241-TARTARUGA-R81"
            and document["issue"] == 871
            and document["checked_utc_date"] == "2026-11-15",
            "identity and date")

    provenance = document["provenance"]
    require(provenance["collection"] ==
            "Hemeroteca Digital da Biblioteca Nacional, coleção 089842",
            "archive collection")
    require(provenance["executor"] == "Ifro", "executor")
    require(provenance["not_all_pages_fully_read"] is True,
            "partial reading disclosure")

    sources = document["sources"]
    require(len(sources) == 3, "source count")
    for row, (issue, date, number, size, digest, pages,
              last_first, first_second, last_folio) in zip(
                  sources, EXPECTED, strict=True
              ):
        require(row["issue"] == issue, "issue number")
        require(row["date_visual"] == date
                and row["edition_number_visual"] == number,
                "edition printed cover")
        require(row["url"] ==
                f"https://hemeroteca-pdf.bn.gov.br/089842/"
                f"per089842_1963_{issue}.pdf", "original PDF locator")
        require(row["bytes"] == size and row["sha256"] == digest,
                "original PDF integrity")
        require(row["pdf_page_count"] == pages, "PDF page count")
        require(row["first_caderno_last_pdf_page"] == last_first
                and row["second_caderno_first_pdf_page"] == first_second
                and row["last_page_printed_folio"] == last_folio,
                "physical section boundary")
        require(row["cover_date_and_number_checked"] is True,
                "visual cover")

    reading = document["reading"]
    require(reading["issue"] == "21659", "reading issue")
    require(reading["new_pages_fully_examined"] == [1, 2, 3, 4],
            "new fully read pages")
    require(reading["remaining_first_caderno_pages_not_fully_read"]
            == list(range(5, 16)), "unread nucleus preserved")
    require(reading["other_issues_status"] ==
            "FIRST_CADERNO_BOUNDARY_MAPPED_ONLY_NO_COLUMN_READING",
            "mapping is not page reading")
    require(reading["global_negative_asserted"] is False
            and reading["all_three_issues_fully_read"] is False,
            "must not assert global negative")
    rows = reading["status_by_pdf_page"]
    require(len(rows) == 4, "page rows")
    for page, row in enumerate(rows, 1):
        require(row["pdf_page"] == page
                and row["printed_page"] == page, "folio mapping")
        require(row["status"] == "EXAMINADA", "visual reading")
        require(row["conde_relevant_article"] is None
                and row["conde_event_time_literal"] is None
                and row["conde_eyewitness"] is None,
                "fabricated article, hour or witness")
        require(row["orbital_constraint_activated"] is False,
                "orbit not licensed")
    satellite = rows[3]["other_satellite_article"]
    require(satellite["title"] == "SATÉLITE"
            and satellite["wire_credit"] == "UPI-CM"
            and satellite["location"] == "Base Vandenberg, Califórnia"
            and satellite["event_class"] == "OTHER_LAUNCH_NOT_CONDE"
            and satellite["conde_event_time_literal"] is None
            and satellite["orbit_identity_528_637_established"] is False,
            "unrelated Vandenberg wire misclassified")

    result = document["conclusion"]
    require(result["classification"] ==
            "FOUR_PAGE_LOCAL_NEGATIVE_21659_WITH_THREE_ORIGINALS_IN_CUSTODY",
            "scope")
    require(result["conde_event_time_literal"] is None
            and result["conde_eyewitness"] is None, "global time/witness")
    require(result["report_independence_from_tupi_diarios_fbis"] ==
            "UNDETERMINED", "independence")
    require(result["orbit_528_or_637_exclusion_licensed"] is False,
            "orbital exclusion")
    canonical = json.dumps(
        document, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == CANONICAL_SHA256,
            "unreviewed interpretation mutation")
    return True


class TestC241R81(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = read_document()

    def test_baseline(self):
        self.assertTrue(validate(self.good))

    def reject(self, keys, value):
        changed = copy.deepcopy(self.good)
        target = changed
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        with self.assertRaises(ValueError):
            validate(changed)

    def test_wrong_pdf_hash(self):
        self.reject(("sources", 0, "sha256"), "0" * 64)

    def test_wrong_pdf_bytes(self):
        self.reject(("sources", 2, "bytes"), 0)

    def test_wrong_issue_date(self):
        self.reject(("sources", 1, "date_visual"), "1963-11-12")

    def test_made_up_section_boundary(self):
        self.reject(("sources", 1, "second_caderno_first_pdf_page"), 12)

    def test_made_up_printed_page(self):
        self.reject(("sources", 1, "last_page_printed_folio"), 12)

    def test_unread_pages_promoted(self):
        self.reject(("reading", "remaining_first_caderno_pages_not_fully_read"), [])

    def test_unread_issues_promoted(self):
        self.reject(("reading", "all_three_issues_fully_read"), True)

    def test_made_up_global_negative(self):
        self.reject(("reading", "global_negative_asserted"), True)

    def test_made_up_hour(self):
        self.reject(("reading", "status_by_pdf_page", 0,
                     "conde_event_time_literal"), "20h15")

    def test_made_up_witness(self):
        self.reject(("reading", "status_by_pdf_page", 2,
                     "conde_eyewitness"), "testemunha inventada")

    def test_unrelated_satellite_promotion(self):
        self.reject(("reading", "status_by_pdf_page", 3,
                     "other_satellite_article", "event_class"),
                    "CONDE_ORBIT_528")

    def test_activated_orbit(self):
        self.reject(("conclusion", "orbit_528_or_637_exclusion_licensed"), True)

    def test_rewritten_subject_prose(self):
        self.reject(("reading", "status_by_pdf_page", 3,
                     "subjects"), "NASA comprovou queda em Conde às 20h15")

    def test_unreviewed_field(self):
        changed = copy.deepcopy(self.good)
        changed["certainty"] = 1.0
        with self.assertRaises(ValueError):
            validate(changed)

    def test_duplicate_key_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "double.json"
            p.write_text('{"issue":871,"issue":872}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_document(p)

    def test_original_pdf_replay_when_provisioned(self):
        """Only runs an actual byte replay when originals are present."""
        directory = os.environ.get("C241_R81_PDF_DIR")
        if not directory:
            self.skipTest("FBN PDFs not provisioned; replay on Ifro")
        for issue, _, _, size, sha256, *_ in EXPECTED:
            pdf = Path(directory) / f"{issue}.pdf"
            self.assertTrue(pdf.is_file(), f"missing original {pdf}")
            self.assertEqual(pdf.stat().st_size, size)
            h = hashlib.sha256()
            with pdf.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(chunk)
            self.assertEqual(h.hexdigest(), sha256)


if __name__ == "__main__":
    unittest.main()
