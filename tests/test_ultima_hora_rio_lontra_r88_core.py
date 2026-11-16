"""Lontra R88: immutable signed-off press-page interpretation, not evidence of a physical fall."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/archive/ultima_hora_rio_04203_04204_core_LONTRA_R88.json"
CANONICAL_SHA256 = "d08f82ef2631c8b8bd6aa4e929bad038c2a064f77bd7ab121a24436436d81690"
DIGESTS = {
    "04203": ("cf7b090d711817421c81bc76faed5ec45cbd8e2d1f5efa7bd6d4537be6ec6612", 11178862, 16, [2, 3, 4, 5, 6, 8]),
    "04204": ("445499302be534bf41712a9ef177e75658907200a0ceb689d3c917a8f2fa3f7a", 12652710, 18, [2, 3, 4, 5, 6, 8, 10, 16]),
}


def read_document(path=SOURCE):
    def unique_pairs(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate key: {key}")
            out[key] = value
        return out

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=unique_pairs)


def canonical_digest(document):
    encoded = json.dumps(
        document, sort_keys=True, ensure_ascii=False, allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate(document):
    # Hash the WHOLE historical interpretation, not only numeric metadata.
    if canonical_digest(document) != CANONICAL_SHA256:
        raise ValueError("R88 interpretation changed without re-review")
    if document["id"] != "C241-LONTRA-R88-UHR-CORE":
        raise ValueError("R88 identifier changed")
    if len(document["issues"]) != 2:
        raise ValueError("R88 edition coverage")
    for issue in document["issues"]:
        edition = issue["edition"]
        sha, size, count, pages = DIGESTS[edition]
        if (issue["sha256"], issue["bytes"], issue["pdf_page_count"]) != (sha, size, count):
            raise ValueError("source custody differs from verified originals")
        if [p["pdf_page"] for p in issue["pages"]] != pages:
            raise ValueError("read page numbers changed")
        if issue["prior_cover_page"] != 1 or 1 in pages:
            raise ValueError("cover cannot be promoted to new interior reading")
        assert set(pages).isdisjoint(issue["not_reviewed_pdf_pages"])
        for page in issue["pages"]:
            if (page["status"] != "EXAMINADA"
                    or page["independent_event_hour"] is not None
                    or page["independent_witness"] is not None
                    or page["report_of_conde_ba"] is not False
                    or page["primary_orbital_measurement"] is not False):
                raise ValueError("invented event evidence or non-reviewed page")
    if document["result"]["new_full_page_reviews"] != 14:
        raise ValueError("incorrect full review count")
    if document["result"]["independent_conde_hour"] is not None:
        raise ValueError("invented independent timestamp")
    return True


class TestLontraR88(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = read_document()

    def test_actual_snapshot(self):
        self.assertTrue(validate(self.document))

    def test_exact_pages_and_no_edition_negative(self):
        self.assertEqual([len(i["pages"]) for i in self.document["issues"]], [6, 8])
        self.assertTrue(self.document["result"]["negative_limited_to_reviewed_pages"])
        self.assertEqual(self.document["issues"][1]["pages"][-1]["printed_page"], 6)

    def reject(self, mutate):
        document = copy.deepcopy(self.document)
        mutate(document)
        with self.assertRaises(ValueError):
            validate(document)

    def test_fabricated_hour(self):
        self.reject(lambda d: d["issues"][1]["pages"][4].update(independent_event_hour="20:15"))

    def test_fabricated_article(self):
        self.reject(lambda d: d["issues"][0]["pages"][5]["topics_checked"].append(
            "NASA confirmed satellite impact near Conde"))

    def test_promote_page_not_read(self):
        self.reject(lambda d: d["issues"][1]["pages"][0].update(pdf_page=11))

    def test_fabricated_witness(self):
        self.reject(lambda d: d["issues"][1]["pages"][6].update(independent_witness="invented"))

    def test_manipulate_original_sha(self):
        self.reject(lambda d: d["issues"][0].update(sha256="0" * 64))

    def test_extrapolate_negative_to_all_pages(self):
        self.reject(lambda d: d.update(
            scope="All pages of both editions proven to contain no information about Conde"))

    def test_unreviewed_extra_metadata_rejected(self):
        self.reject(lambda d: d.update(confidence=1))

    def test_real_disk_mutation_fails(self):
        changed = copy.deepcopy(self.document)
        changed["result"]["scientific_update"] += " NASA confirmed a time."
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "changed.json"
            p.write_text(json.dumps(changed, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(read_document(p))

    def test_duplicate_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "dupe.json"
            p.write_text('{"id":"one","id":"two"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_document(p)


if __name__ == "__main__":
    unittest.main()
