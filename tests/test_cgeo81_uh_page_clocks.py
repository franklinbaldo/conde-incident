"""CGEO-81: source-checked press pages; clock labels cannot become event hours.

Offline integrity checks, not a live archive replay or independent testimony.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / (
    "research/editorial/cgeo81_uh_00472_00473_read_20261115.json"
)
EXPECTED_DIGEST = "11f6ce0a2c75626cad0a44159eaa0786f61e5283788f8ad6b5f589a6ea3cb25e"
PDF_SHA = {
    "00472": "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece",
    "00473": "f37e4afa500fe841546a751e562cc799c33c699decb8967b2ae00b45e721e349",
}
SCOPE = [
    ("00472", 4, "ILEGIVEL_PARCIAL"),
    ("00472", 6, "ILEGIVEL_PARCIAL"),
    ("00473", 1, "LIDO_INTEGRAL_SEM_MENCAO"),
    ("00473", 4, "LIDO_INTEGRAL_SEM_MENCAO"),
    ("00473", 6, "LIDO_INTEGRAL_SEM_MENCAO"),
]


def validate(doc):
    errors = []
    digest = hashlib.sha256(json.dumps(
        doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != EXPECTED_DIGEST:
        errors.append("frozen text and metadata")
    if doc.get("id") != "CGEO-81":
        errors.append("id")
    sources = doc.get("sources", [])
    if len(sources) != 2 or {
        x.get("edition"): x.get("sha256") for x in sources
    } != PDF_SHA:
        errors.append("source sha")
    if not doc.get("method", {}).get("original_pdf_sha256_rechecked"):
        errors.append("source custody")
    if doc.get("method", {}).get("new_ocr"):
        errors.append("unsupported OCR")
    pages = doc.get("page_reviews", [])
    if [(x.get("edition"), x.get("pdf_page"), x.get("status"))
            for x in pages] != SCOPE:
        errors.append("scope")
    if any(x.get("event_hour") is not None or x.get("eyewitnesses") != []
           for x in pages):
        errors.append("invented source")
    if any(x.get("new_integral_credit") or not x.get("unreadable_area")
           for x in pages[:2]):
        errors.append("illegible promoted")
    if any(not x.get("new_integral_credit") for x in pages[2:]):
        errors.append("missing read")
    c = doc.get("coverage", {})
    if tuple(c.get(k) for k in (
        "package_total_pdf_pages", "previously_certified_integral",
        "newly_certified_integral", "integral_after_this_round",
        "not_yet_integral", "complete_issues"
    )) != (68, 10, 3, 13, 55, 0):
        errors.append("invented coverage")
    if c.get("remaining_partial_00472") != [4, 6, 9]:
        errors.append("lost partial pages")
    if any(x.get("phenomenon_hour") is not False or
           not x.get("kind", "").endswith("_NOT_EVENT")
           for x in doc.get("temporal_false_positives", [])):
        errors.append("false clock promoted")
    g = doc.get("genealogy", {})
    if (g.get("new_independent_hour") is not None or
        g.get("new_independent_eyewitness") is not False or
        g.get("orbit_candidate") is not None):
        errors.append("invented witness/orbit")
    return errors


class TestCgeo81(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = json.loads(PATH.read_text(encoding="utf-8"))

    def test_baseline(self):
        self.assertEqual(validate(copy.deepcopy(self.ref)), [])

    def test_adversarial(self):
        cases = {
            "fabricated_clock": lambda d: d["page_reviews"][2].__setitem__("event_hour", "23h00"),
            "fake_witness": lambda d: d["page_reviews"][4].__setitem__("eyewitnesses", ["observador"]),
            "promote_partial": lambda d: d["page_reviews"][0].__setitem__("status", "LIDO_INTEGRAL_SEM_MENCAO"),
            "erase_illegibility": lambda d: d["page_reviews"][1].__setitem__("unreadable_area", None),
            "inflate_coverage": lambda d: d["coverage"].__setitem__("integral_after_this_round", 68),
            "false_clock": lambda d: d["temporal_false_positives"][1].__setitem__("phenomenon_hour", True),
            "editorial_prose": lambda d: d["page_reviews"][2].__setitem__("notes", "Conde 23h witnessed"),
            "invalid_pdf_sha": lambda d: d["sources"][1].__setitem__("sha256", "0" * 64),
            "misidentified_edition": lambda d: d["sources"][1].__setitem__("edition", "00472"),
            "false_orbital_choice": lambda d: d["genealogy"].__setitem__("orbit_candidate", 528),
        }
        for name, mutation in cases.items():
            with self.subTest(name=name):
                bad = copy.deepcopy(self.ref)
                mutation(bad)
                self.assertNotEqual(validate(bad), [], name)


if __name__ == "__main__":
    unittest.main()
