"""CGEO-82: six historical pages, literal timestamps cannot become Conde hours."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / (
    "research/editorial/cgeo82_uh_00476_00477_pages_20261115.json"
)
EXPECTED_DIGEST = "af6bb77a11d721297752c92cf9829940d48062f32f1658c7bfa0fcaf0b809509"
SHA256 = {
    "00476": "89af71800faf3d447cf7fd3a2ee473ba010516beb8dc45dd200d220ad65c8047",
    "00477": "0a5170a69e037166ef1fdf502797cef8fc74211b45183af0da775eedc7072fb0",
}
SCOPE = [("00476", 1), ("00476", 5), ("00476", 6),
         ("00477", 1), ("00477", 5), ("00477", 6)]


def validate(doc):
    errors = []
    digest = hashlib.sha256(json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != EXPECTED_DIGEST:
        errors.append("entire-source-document-digest")
    if doc.get("id") != "CGEO-82":
        errors.append("id")
    sources = doc.get("sources", [])
    if len(sources) != 2 or {
        s.get("edition"): s.get("sha256") for s in sources
    } != SHA256:
        errors.append("source-sha")
    if not doc.get("method", {}).get("source_sha256_rechecked"):
        errors.append("custody")
    if doc.get("method", {}).get("new_ocr"):
        errors.append("unsupported-ocr")
    pages = doc.get("page_reviews", [])
    if [(p.get("edition"), p.get("pdf_page")) for p in pages] != SCOPE:
        errors.append("scope")
    if any(p.get("status") != "LIDO_INTEGRAL_SEM_MENCAO"
           or p.get("independent_event_hour") is not None
           or p.get("eyewitnesses") != []
           or p.get("incident_article") is not False
           or p.get("new_integral_credit") is not True for p in pages):
        errors.append("invented-page-hour-or-witness")
    if not pages[1].get("articles") or not any(
        "Cosmos 21" in x.get("title", "") for x in pages[1]["articles"]
    ):
        errors.append("lost-satellite-context")
    if any(c.get("phenomenon_hour") is not False or
           not c.get("kind", "").endswith("_NOT_EVENT")
           for c in doc.get("false_candidates", [])):
        errors.append("false-clock-promoted")
    genealogy = doc.get("genealogy", {})
    if (genealogy.get("new_incident_article") is not False or
        genealogy.get("new_independent_eyewitness") is not False or
        genealogy.get("independent_event_hour") is not None or
        genealogy.get("orbital_candidate") is not None or
        genealogy.get("orbital_exclusion_licensed") is not False):
        errors.append("invented-physics")
    coverage = doc.get("coverage", {})
    if tuple(coverage.get(k) for k in (
        "source_package_pages", "previously_certified_integral",
        "newly_certified_integral_this_round", "own_chain_integral_after",
        "lontra_closed_lot_new_integral", "combined_coverage_when_no_overlap",
        "combined_not_yet_integral", "complete_editions_certified"
    )) != (68, 13, 6, 19, 8, 27, 41, 0):
        errors.append("invalid-page-coverage")
    return errors


class TestCGEO82(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(PATH.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertEqual(validate(copy.deepcopy(self.reference)), [])

    def test_adversarial(self):
        changes = {
            "invent-hour": lambda d: d["page_reviews"][0].__setitem__(
                "independent_event_hour", "20h15"),
            "invent-witness": lambda d: d["page_reviews"][5].__setitem__(
                "eyewitnesses", ["anônimo"]),
            "promote-cosmos": lambda d: d["page_reviews"][1].__setitem__(
                "incident_article", True),
            "invent-orbit": lambda d: d["genealogy"].__setitem__(
                "orbital_candidate", 528),
            "change-pdf-sha": lambda d: d["sources"][0].__setitem__(
                "sha256", "0" * 64),
            "invent-page": lambda d: d["page_reviews"][0].__setitem__(
                "pdf_page", 9),
            "inflate-coverage": lambda d: d["coverage"].__setitem__(
                "combined_coverage_when_no_overlap", 68),
            "overwrite-body-prose": lambda d: d["page_reviews"][1].__setitem__(
                "notes", "Conde 20h15 witnessed"),
            "promote-rubric": lambda d: d["false_candidates"][0].__setitem__(
                "phenomenon_hour", True),
            "downgrade-visual": lambda d: d["method"].__setitem__(
                "source_sha256_rechecked", False),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                bad = copy.deepcopy(self.reference)
                change(bad)
                self.assertNotEqual(validate(bad), [], name)


if __name__ == "__main__":
    unittest.main()
