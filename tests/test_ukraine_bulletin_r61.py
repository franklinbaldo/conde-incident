"""Negative tests for the Kyiv serial holdings and source/genealogy boundary."""
import copy
import json
import unittest
from tools.audit_ukraine_bulletin_r61 import PATH, validate, check_holding_context

CONTEXT = ("Бюллетень станций оптического наблюдения ИСЗ "
           "1958 N3 1962 N25-31 1963 N32-37 1964 N38-43").encode("utf-8")

class TestR61(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(PATH.read_text(encoding="utf-8"))
    def test_valid_record(self):
        self.assertTrue(validate(self.base))
    def test_valid_context(self):
        self.assertTrue(check_holding_context(CONTEXT))
    def test_catalog_mutations(self):
        for key, value in [
            ("serial_title","Another bulletin"),("1963_holding","N33-37"),
            ("html_sha256","0"*64),("verified_html_bytes",0),
            ("source_url","https://example.invalid"),("verified_http_status",404),
            ("custody_scope","1963 primary satellite measurement"),
            ("verification","Original Soviet issue obtained")
        ]:
            with self.subTest(field=key):
                x=copy.deepcopy(self.base);x["catalog"][key]=value
                with self.assertRaises(ValueError):validate(x)
    def test_holding_context_is_not_issue_substring(self):
        for variant in [
            CONTEXT.replace(b"1963 N32-37",b"1963 N33-37"),
            CONTEXT.replace(b"1962 N25-31",b"1962 N24-31"),
            CONTEXT.replace(b"1964 N38-43",b"1964 N37-43"),
            b"Different title 1962 N25-31 1963 N32-37 1964 N38-43"
        ]:
            with self.subTest(variant=variant):
                with self.assertRaises(ValueError):check_holding_context(variant)
    def test_no_primary_promotions(self):
        for key in ("issue_32_facsimile_retrieved","original_article_retrieved",
                    "original_page_read","station_identified_for_527_529","institutional_contact_sent"):
            with self.subTest(key=key):
                x=copy.deepcopy(self.base);x["boundaries"][key]=True
                with self.assertRaises(ValueError):validate(x)
        for key,value in [("independent_observations_norad_527_528_529",[{"norad":528}]),("new_orbital_constraints",1)]:
            x=copy.deepcopy(self.base);x["boundaries"][key]=value
            with self.assertRaises(ValueError):validate(x)
    def test_article_cannot_be_promoted(self):
        for key,value in [("link_to_target_article_status","ARTICLE_READ"),("primary_article_pages_known",True),
                          ("soviet_bulletin_issue",33)]:
            x=copy.deepcopy(self.base);x["target"][key]=value
            with self.assertRaises(ValueError):validate(x)
    def test_catalogs_not_instrumental_witnesses(self):
        x=copy.deepcopy(self.base);x["cross_catalog"]["interpretation"]="Two independent technical observations"
        with self.assertRaises(ValueError):validate(x)

if __name__=="__main__":
    unittest.main()
