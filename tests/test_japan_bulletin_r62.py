"""Adversarial checks of a 1963 Japanese holdings locator, not an observation."""
import copy
import hashlib
import json
import unittest

from tools.audit_japan_bulletin_r62 import PATH, check_html, validate


class TestJapanBulletinR62(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(PATH.read_text(encoding="utf-8"))

    def test_honest_holdings(self):
        self.assertTrue(validate(self.base))
        self.assertEqual(self.base["by_issue_reported_holder_count"],
                         {"32": 5, "33": 5, "34": 4, "35": 4, "36": 5, "37": 5})

    def test_snapshot_digest_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            check_html(b"<html>Not the real catalogue</html>", self.base)

    def test_title_or_identity_cannot_be_substituted(self):
        mutations = [
            ("provenance", "url", "https://example.invalid"),
            ("provenance", "ncid", "AA00000000"),
            ("provenance", "html_sha256", hashlib.sha256(b"fake").hexdigest()),
            ("provenance", "retrieved_html_bytes", 1),
            ("provenance", "exact_title_nii", "Бюллетень станций оптического наблюдения ИСЗ"),
            ("provenance", "equivalence_status", "IDENTICAL_PRIMARY_EDITION_CONFIRMED"),
            ("provenance", "hashed_object", "1963 original issue"),
        ]
        for section, key, value in mutations:
            with self.subTest(key=key):
                d = copy.deepcopy(self.base)
                d[section][key] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_no_invented_library_coverage(self):
        d = copy.deepcopy(self.base)
        d["holdings"][3]["issues_1963"].extend([34, 35])
        d["by_issue_reported_holder_count"]["34"] = 5
        d["by_issue_reported_holder_count"]["35"] = 5
        with self.assertRaises(ValueError):
            validate(d)
        d = copy.deepcopy(self.base)
        d["holdings"] = d["holdings"][:-1]
        with self.assertRaises(ValueError):
            validate(d)

    def test_no_promotion_to_original_or_orbit(self):
        for field, value in [
            ("scan_or_issue_contents_accessed", True),
            ("article_original_verified", True),
            ("author_or_pages_from_original_verified", True),
            ("independent_observations_norad_527_528_529", [{"norad": 528}]),
            ("new_orbital_constraints", 1),
        ]:
            with self.subTest(field=field):
                d = copy.deepcopy(self.base)
                d["boundaries"][field] = value
                with self.assertRaises(ValueError):
                    validate(d)

    def test_no_unsolicited_archival_request(self):
        d = copy.deepcopy(self.base)
        d["ready_but_not_sent_request"]["contact_sent"] = True
        with self.assertRaises(ValueError):
            validate(d)


if __name__ == "__main__":
    unittest.main()
