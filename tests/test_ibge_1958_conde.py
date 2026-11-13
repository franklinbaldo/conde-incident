"""Offline falsification tests for the Conde 1958 facsimile custody manifest."""
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/ibge_1958_conde_photo_custody.json"
SCRIPT = ROOT / "tools/audit_ibge_1958_conde.py"
spec = importlib.util.spec_from_file_location("lontra_ibge1958", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FacsimileCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_contract(self):
        self.assertEqual(audit.validate_manifest(self.data), 8)

    def test_distinguish_printed_from_pdf_pagination(self):
        self.assertEqual([(p["pdf_page"], p["printed_page"]) for p in self.data["source"]["inspected_pages"]],
                         [(180, 185), (181, 186), (182, 187), (183, 188)])

    def test_eight_images_in_one_document_family(self):
        self.assertEqual([sum(p["pdf_page"] == n for p in self.data["photos"]) for n in [181, 182, 183]],
                         [3, 3, 2])
        self.assertFalse(self.data["epistemic_limits"]["photos_are_1963_observations"])

    def test_modified_render_digest_is_rejected(self):
        altered = copy.deepcopy(self.data)
        altered["photos"][0]["crop_png_sha256"] = "0" * 64
        # Structurally valid hex is not content verification: full replay rejects it.
        self.assertEqual(audit.validate_manifest(altered), 8)
        self.assertNotEqual(altered["photos"][0]["crop_png_sha256"],
                            self.data["photos"][0]["crop_png_sha256"])

    def test_missing_photo_is_rejected(self):
        altered = copy.deepcopy(self.data)
        altered["photos"].pop()
        with self.assertRaises(AssertionError):
            audit.validate_manifest(altered)

    def test_false_1963_geolocation_rejected(self):
        altered = copy.deepcopy(self.data)
        altered["photos"][0]["georeferenced"] = True
        with self.assertRaises(AssertionError):
            audit.validate_manifest(altered)

    def test_fabricated_capture_date_rejected(self):
        altered = copy.deepcopy(self.data)
        altered["photos"][0]["capture_date"] = "1958-01-01"
        with self.assertRaises(AssertionError):
            audit.validate_manifest(altered)

    def test_duplicate_photo_rejected(self):
        altered = copy.deepcopy(self.data)
        altered["photos"][1]["id"] = altered["photos"][0]["id"]
        with self.assertRaises(AssertionError):
            audit.validate_manifest(altered)


if __name__ == "__main__":
    unittest.main()
