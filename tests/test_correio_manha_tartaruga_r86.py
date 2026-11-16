"""C241-R86: the 14 Nov 1963 expert interview is not an independent event clock or eyewitness."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/archive/conde_correio_manha_1963_11_14_C241_TARTARUGA_R86.json"
EXPECTED_TITLE = "CIENTISTA NÃO CRÊ EM NOVO METEORITO"
EXPECTED_ATTRIBUTION = "Walter da Silva Curvello, do Museu Nacional, disse ao Correio da Manhã"
EXPECTED_PDF_SHA = "d3b6301c192f8513c8a9a53a06d18eb47fc82b76fda45b6438bc1f416e8854e0"


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key: " + key)
        result[key] = value
    return result


def load(path=FILE):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def validate(d):
    require(d["schema"] == "conde.local_clock_press_documentary_find/v1", "schema")
    require(d["id"] == "C241-TARTARUGA-R86" and d["issue"] == 871, "identity")
    sources = d["sources"]
    require([s["edition"] for s in sources] == ["21660", "21661"], "editions")
    require([s["bytes"] for s in sources] == [20333897, 21320531], "source bytes")
    require(sources[0]["sha256"] == "497cd71b643be03f908e26c2e99100fd24908fb026ca33c8e1667d49ee897bc0", "21660 sha")
    require(sources[1]["sha256"] == EXPECTED_PDF_SHA, "21661 sha")
    require(sources[0]["visual_panorama_pages"] == [9, 10, 11, 12], "21660 coverage")
    require(sources[1]["visual_panorama_pages"] == list(range(1, 14)), "21661 coverage")
    require(all(s["new_pages_certified_integral"] == [] for s in sources), "panorama overclaimed")
    require("not full page-by-page four-quadrant certification" in d["method"]["visual_evidence"], "method scope")
    article = d["key_find"]
    require((article["edition"], article["pdf_page"], article["printed_folio"]) == ("21661", 7, "7"), "article locator")
    require(article["article_title"] == EXPECTED_TITLE and article["attribution_printed"] == EXPECTED_ATTRIBUTION, "interview provenance")
    require(article["source_independence_class"] == "INDEPENDENT_EDITORIAL_EXPERT_COMMENT_NOT_PRIMARY_EYEWITNESS", "comment not eyewitness")
    require("não fornece uma testemunha independente" in article["interpretation"], "not a primary witness")
    require(article["conde_municipality_explicit"] is False and article["local_event_hour_literal"] is None
            and article["local_event_hour_basis"] is None and article["named_event_eyewitness"] is None
            and article["identified_norad_object"] is None and article["event_location_confirmed"] is None
            and article["orbital_constraint_active"] is False, "invented event fact")
    require([a["pdf_page"] for a in d["other_relevant_articles"]] == [9, 8, 10], "crosscheck pages")
    require(d["other_relevant_articles"][0]["geography"] == "São Mateus, Espírito Santo", "ES story")
    require(all(a["conde_time"] is None and a["independent_eye_witness"] is None for a in d["other_relevant_articles"]), "unrelated clocks/witness")
    scope = d["scope"]
    require(scope["panorama_triage_not_integral"] is True and scope["new_pages_certified_integral"] == []
            and scope["all_core_pages_examined"] is False and scope["negative_for_entire_editions"] is False, "unsupported completion")
    require(scope["event_mentioned_in_21661"] is True and scope["local_clock_independent_found"] is False
            and scope["primary_witness_independent_found"] is False
            and scope["do_not_exclude_528_or_637"] is True, "unsupported physics")
    return True


class TestR86(unittest.TestCase):
    def setUp(self):
        self.d = load()

    def test_document(self):
        self.assertTrue(validate(self.d))

    def mutate(self, fn):
        x = copy.deepcopy(self.d)
        fn(x)
        with self.assertRaises(ValueError):
            validate(x)

    def test_false_hour(self):
        self.mutate(lambda d: d["key_find"].__setitem__("local_event_hour_literal", "20h15"))

    def test_false_witness(self):
        self.mutate(lambda d: d["key_find"].__setitem__("named_event_eyewitness", "João"))

    def test_false_indept_observation(self):
        self.mutate(lambda d: d["key_find"].__setitem__("source_independence_class", "PRIMARY_WITNESS"))

    def test_conde_location(self):
        self.mutate(lambda d: d["key_find"].__setitem__("conde_municipality_explicit", True))

    def test_false_completion(self):
        self.mutate(lambda d: d["scope"].__setitem__("all_core_pages_examined", True))

    def test_false_negative(self):
        self.mutate(lambda d: d["scope"].__setitem__("event_mentioned_in_21661", False))

    def test_false_orbit(self):
        self.mutate(lambda d: d["key_find"].__setitem__("orbital_constraint_active", True))

    def test_wrong_source(self):
        self.mutate(lambda d: d["sources"][1].__setitem__("sha256", "0" * 64))

    def test_fake_integral(self):
        self.mutate(lambda d: d["sources"][1].__setitem__("new_pages_certified_integral", [7]))

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"hour":null,"hour":"20h15"}', object_pairs_hook=no_duplicates)


if __name__ == "__main__":
    unittest.main()
