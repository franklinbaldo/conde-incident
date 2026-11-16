"""C241-R88: archival page custody and orthogonal negatives for false Conde dates."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/archive/conde_correio_manha_1963_11_14_C241_TARTARUGA_R88.json"
R87 = ROOT / "research/archive/conde_correio_manha_1963_11_13_C241_TARTARUGA_R87.json"
R86 = ROOT / "research/archive/conde_correio_manha_1963_11_14_C241_TARTARUGA_R86.json"
EXPECTED_SHA = "d3b6301c192f8513c8a9a53a06d18eb47fc82b76fda45b6438bc1f416e8854e0"


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path=FILE):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def validate(d):
    require(d["schema"] == "conde.local_clock_press_nucleus_increment/v1", "schema")
    require(d["id"] == "C241-TARTARUGA-R88" and d["research_issue"] == 871, "identity")
    require(d["predecessor_manifest"] == str(R87.relative_to(ROOT)), "R87 provenance")
    require(d["prior_panorama_manifest"] == str(R86.relative_to(ROOT)), "R86 provenance")
    require(R87.is_file() and R86.is_file(), "missing provenance manifests")
    s = d["source"]
    require(s["edition"] == "21661" and s["printed_date"] == "1963-11-14", "edition")
    require(s["pdf_pages"] == 28 and s["original_bytes"] == 21320531, "source size")
    require(s["original_sha256"] == EXPECTED_SHA, "source digest")
    require(s["first_caderno_pdf_pages"] == [1, 13] and s["additional_science_pdf_page"] == 21, "caderno mapping")
    require("84 recortes" in d["method"]["render"] and "3200 px" in d["method"]["render"], "visual inspection")
    require("max_memory_mb=128" in d["method"]["controller"], "controller budget")
    readings = d["readings"]
    expected = list(range(1, 14)) + [21]
    require([x["pdf_page"] for x in readings] == expected, "coverage sequence")
    require([x["status"] for x in readings] == ["EXAMINADA_VISUALMENTE_INTEGRAL"] * 14, "false certification")
    require(all(x["conde_event_hour_literal"] is None
                and x["conde_independent_eyewitness"] is None
                and x["conde_orbital_object"] is None for x in readings), "invented Conde fact")
    require("Iguape/SP" in readings[10]["subjects"] and "29 DE OUTUBRO" in readings[10]["subjects"], "p11 incident")
    require("TV-Tupi" in readings[7]["subjects"] and "21h45" in readings[7]["subjects"], "p8 chronology")
    case = d["distinct_case"]
    require(case["pdf_page"] == 11 and case["title"] == "HOMENS-RÃS NADA ACHAM EM IGUAPE", "distinct story")
    require(case["alleged_event_date"] == "1963-10-29" and "São Paulo" in case["location"], "separate geography")
    require(case["time_precision"] == "tarde (sem hora numérica)"
            and case["conde_event"] is False and case["identified_norad_object"] is None
            and case["physical_recovery_confirmed"] is False, "false Iguape import")
    expert = d["expert_comment"]
    require(expert["classification"] == "INDEPENDENT_EDITORIAL_EXPERT_COMMENT_NOT_PRIMARY_EYEWITNESS", "expert is not eyewitness")
    require(expert["event_hour_literal"] is None
            and expert["named_event_witness"] is None
            and expert["conde_municipality_explicit"] is False, "false local evidence")
    require("4 horas e 47 minutos" in expert["unrelated_clock"], "false time import")
    tv = d["broadcast_crosscheck"]
    require(tv["advertised_day"] == "1963-11-14" and tv["scheduled_time"] == "21h45", "broadcast chronology")
    require(tv["identifies_1963_11_08_coverage"] is False and tv["conde_event_hour_literal"] is None, "false 8 Nov Tupi")
    require(d["other_science_page"]["pdf_page"] == 21 and d["other_science_page"]["conde_report"] is None, "science page")
    scope = d["scope"]
    require(scope["new_pages_certified_integral"] == expected
            and scope["first_caderno_fully_examined"] is True
            and scope["additional_science_page_fully_examined"] is True, "coverage assertions")
    require(scope["entire_edition_fully_examined"] is False
            and scope["second_caderno_fully_examined"] is False
            and scope["global_edition_negative_asserted"] is False, "false global negative")
    require(all(scope[k] is False for k in (
        "independent_conde_local_time_found",
        "independent_conde_eyewitness_found",
        "conde_physical_recovery_confirmed",
        "orbital_constraint_528_or_637_active"
    )), "unsupported physics")
    return True


class TestC241R88(unittest.TestCase):
    def setUp(self):
        self.doc = load()

    def test_real_manifest(self):
        self.assertTrue(validate(self.doc))

    def mutate(self, fn):
        d = copy.deepcopy(self.doc)
        fn(d)
        with self.assertRaises(ValueError):
            validate(d)

    def test_false_hour(self):
        self.mutate(lambda d: d["readings"][6].__setitem__("conde_event_hour_literal", "20h15"))

    def test_false_witness(self):
        self.mutate(lambda d: d["readings"][10].__setitem__("conde_independent_eyewitness", "João"))

    def test_iguape_as_conde(self):
        self.mutate(lambda d: d["distinct_case"].__setitem__("conde_event", True))

    def test_iguape_as_norad528(self):
        self.mutate(lambda d: d["distinct_case"].__setitem__("identified_norad_object", 528))

    def test_iguape_recovery(self):
        self.mutate(lambda d: d["distinct_case"].__setitem__("physical_recovery_confirmed", True))

    def test_expert_as_witness(self):
        self.mutate(lambda d: d["expert_comment"].__setitem__("classification", "PRIMARY_EYEWITNESS"))

    def test_false_tupi_time(self):
        self.mutate(lambda d: d["broadcast_crosscheck"].__setitem__("identifies_1963_11_08_coverage", True))

    def test_false_global_negative(self):
        self.mutate(lambda d: d["scope"].__setitem__("global_edition_negative_asserted", True))

    def test_false_full_edition(self):
        self.mutate(lambda d: d["scope"].__setitem__("entire_edition_fully_examined", True))

    def test_wrong_pdf_hash(self):
        self.mutate(lambda d: d["source"].__setitem__("original_sha256", "0" * 64))

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"conde_hour":null,"conde_hour":"20h15"}', object_pairs_hook=reject_duplicate_keys)


if __name__ == "__main__":
    unittest.main()
