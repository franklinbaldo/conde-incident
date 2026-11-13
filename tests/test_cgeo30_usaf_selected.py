"""CGEO-30 adversarial checks: selected official folder is not an aerial frame."""

import copy
import unittest

from tools.cgeo30_usaf_selected import EXCERPT, MANIFEST, PARENT, load, verify, verify_original


class Cgeo30UsafSelectedTests(unittest.TestCase):
    def setUp(self):
        self.record = load(MANIFEST)
        self.parent = load(PARENT)
        self.html = EXCERPT.read_bytes()

    def test_real_excerpt_confirms_telerik_selection(self):
        self.assertEqual(verify(self.record, self.parent, self.html),
                         "USAF_SELECTION_EVIDENCE_REPLAY_PASS")

    def test_mistaken_label_or_selected_value_rejected(self):
        for original, replacement in [(b"1850", b"1851"), (b'":"680"', b'":"679"')]:
            changed = self.html.replace(original, replacement)
            with self.subTest(original=original), self.assertRaises(ValueError):
                verify(self.record, self.parent, changed)

    def test_claimed_image_url_framing_and_1963_geometry_rejected(self):
        for path, value in [
            (("selection", "document_image_src_in_server_html"), "/image.png"),
            (("image_load_attempt", "document_image_src_in_server_html"), "/image.png"),
            (("scientific_limits", "original_photoindex_image_acquired"), True),
            (("scientific_limits", "date_of_capture_verified"), True),
            (("scientific_limits", "event_position_1963"), [-37.7, -11.7]),
            (("scientific_limits", "can_constrain_orbital_reentry"), True),
            (("export_probe", "actual_pdf_acquired"), True),
        ]:
            wrong = copy.deepcopy(self.record)
            wrong[path[0]][path[1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                verify(wrong, self.parent, self.html)

    def test_no_fake_source_replay(self):
        for stage in ["selection", "image"]:
            with self.subTest(stage=stage), self.assertRaises(ValueError):
                verify_original(self.record, b"fake response", stage)


if __name__ == "__main__":
    unittest.main()
