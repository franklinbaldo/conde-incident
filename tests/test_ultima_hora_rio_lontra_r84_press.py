"""G100: fail closed on every published interpretation in Lontra R84-PRESS.

This authenticates the reviewed JSON snapshot, not the FBN source bytes or
the historical reading. Source file replay remains an independent gate.
"""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/archive/ultima_hora_rio_police_and_covers_LONTRA_R84.json"
INTERPRETATION_SHA256 = "5c7b15bafe4b9f1dae23532d969d04ac40b7b82de35391d27d2b46811e790292"


def read_document(path=SOURCE):
    def no_duplicate_keys(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_keys)


def interpretation_sha256(document):
    canonical = json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate(document):
    """Reject unreviewed source narratives even with unchanged numeric counts."""
    if interpretation_sha256(document) != INTERPRETATION_SHA256:
        raise ValueError("R84-PRESS full interpretation changed without review")
    if document["id"] != "C241-LONTRA-R84-PRESS":
        raise ValueError("incorrect press-reading identifier")
    focal = document["focal_source"]
    if focal["edition"] != "04201" or focal["pages"][0]["pdf_page"] != 12:
        raise ValueError("incorrect observed press page")
    page = focal["pages"][0]
    if not (page["status"] == "EXAMINADA"
            and page["independent_event_hour"] is None
            and page["independent_witness"] is None
            and page["event_report_conde_ba"] is False):
        raise ValueError("unsupported independent event claim")
    covers = document["cover_identifications"]
    if len(covers) != 3 or [x["edition"] for x in covers] != [
        "04202", "04203", "04204"
    ]:
        raise ValueError("cover count/identity")
    for cover in covers:
        if (cover["review_level"] != "COVER_ONLY"
                or cover["inner_pages_status"] != "NOT_READ"
                or cover["event_report_conde_ba"] is not None
                or cover["independent_event_hour"] is not None):
            raise ValueError("cover promoted to unperformed reading")
    return True


class TestLontraR84Press(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = read_document()

    def test_original_reviewed_snapshot(self):
        self.assertTrue(validate(self.document))

    def reject(self, mutate):
        doc = copy.deepcopy(self.document)
        mutate(doc)
        with self.assertRaises(ValueError):
            validate(doc)

    def test_fabricated_press_article(self):
        self.reject(lambda x: x["focal_source"]["pages"][0]["articles"].append(
            "NASA confirmou queda de satélite em Conde às 20h15"))

    def test_rewritten_police_section_description(self):
        self.reject(lambda x: x["focal_source"]["mapping"].update(
            police_section_identification="NASA confirma Conde"))

    def test_fabricated_source_provenance(self):
        self.reject(lambda x: x["focal_source"].update(
            sha256="0" * 64))

    def test_fake_eyewitness(self):
        self.reject(lambda x: x["focal_source"]["pages"][0].update(
            independent_witness="testemunha inventada"))

    def test_cover_date_rewritten(self):
        self.reject(lambda x: x["cover_identifications"][1].update(
            date_printed="1963-11-12"))

    def test_promote_unread_edition(self):
        self.reject(lambda x: x["cover_identifications"][2].update(
            inner_pages_status="EXAMINADA"))

    def test_fabricated_global_conclusion(self):
        self.reject(lambda x: x.update(
            result="O evento de Conde ocorreu às 20h15."))

    def test_unreviewed_new_metadata_field(self):
        self.reject(lambda x: x.update(confidence=1.0))

    def test_real_disk_mutation_fails(self):
        changed = copy.deepcopy(self.document)
        changed["focal_source"]["pages"][0]["false_positive_guard"] += (
            "; NASA confirmou Conde às 20h15")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mutated.json"
            path.write_text(json.dumps(changed, ensure_ascii=False),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(read_document(path))

    def test_duplicate_json_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"id":"R84","id":"FALSE"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_document(path)


if __name__ == "__main__":
    unittest.main()
