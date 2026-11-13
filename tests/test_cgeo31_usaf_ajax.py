"""CGEO-31: no false image or spatial claims from real AJAX response."""

import copy
import unittest

from tools.cgeo31_usaf_ajax import (EXCERPT, MANIFEST, PARENT, load, verify,
                                    verify_full, extract_document_panel)


class Cgeo31AjaxTest(unittest.TestCase):
    def setUp(self):
        self.record = load(MANIFEST)
        self.parent = load(PARENT)
        self.excerpt = EXCERPT.read_bytes()

    def test_official_replay_excerpt(self):
        self.assertEqual(verify(self.record, self.parent, self.excerpt),
                         "CGEO31_ASYNC_PANEL_EXCERPT_PASS")

    def test_image_claims_and_coordinates_forbidden(self):
        changes = [("response", "image_bytes_acquired", True),
                   ("response", "doc_image_src", "https://example.com/imaginary.jpg"),
                   ("scientific_limits", "flight_date_verified", True),
                   ("scientific_limits", "footprint_verified", True),
                   ("scientific_limits", "historical_center_geometry", [-37, -11]),
                   ("scientific_limits", "can_constrain_orbital_reentry", True)]
        for a, b, val in changes:
            wrong = copy.deepcopy(self.record)
            wrong[a][b] = val
            with self.subTest(field=b), self.assertRaises(ValueError):
                verify(wrong, self.parent, self.excerpt)

    def test_forged_unacquired_image_is_rejected(self):
        forged = self.excerpt.replace(b'id="DocumentoImg"', b'id="DocumentoImg" src="fake.jpg"')
        with self.assertRaises(ValueError):
            verify(self.record, self.parent, forged)

    def test_bad_frame_rejected(self):
        for raw in [b'fake', b'1|#||4|20|updatePanel|DocumentoUpdatePanel|abc|',
                    b'1|#||4|1|updatePanel|DocumentoUpdatePanel|a']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                extract_document_panel(raw)

    def test_no_fake_full_source_replay(self):
        with self.assertRaises(ValueError):
            verify_full(b'fake', self.record, self.excerpt)


if __name__ == "__main__":
    unittest.main()
