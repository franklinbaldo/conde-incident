"""Adversarial tests for AFU retrospective source and incomplete custody."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("zvenigorod_memoir", ROOT / "tools/verify_zvenigorod_afu_memoir_route.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ZvenigorodAFUMemoir(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(module.MANIFEST.read_text(encoding="utf-8"))

    def reject(self, path, value):
        x = copy.deepcopy(self.doc)
        d = x
        for key in path[:-1]:
            d = d[key]
        d[path[-1]] = value
        with self.assertRaises(AssertionError):
            module.validate(x)

    def test_valid_manifest(self):
        self.assertTrue(module.validate(self.doc))

    def test_exact_bytes_and_origin(self):
        self.reject(["source","sha256"],"0"*64)
        self.reject(["source","byte_length"],613157)
        self.reject(["source","url"],"https://another.example/memoir")

    def test_charset_conflict_not_silenced(self):
        self.reject(["source","effective_decoding"],"windows-1251")
        self.reject(["source","html_meta_charset"],"koi8-r")

    def test_different_dates_do_not_merge(self):
        self.reject(["source","historical_claims",0,"date"],"2007-05")
        self.reject(["source","historical_claims",1,"date"],"1963")

    def test_no_original_1963_measurements(self):
        self.reject(["source","historical_claims",1,"independent_target_measurement"], True)
        self.reject(["observables","independent_measurements"],1)
        self.reject(["observables","orbital_constraints_activated"],1)

    def test_archival_survival_and_object_identification_unknown(self):
        for name in self.doc["open_questions"]:
            with self.subTest(field=name):
                self.reject(["open_questions",name], True)

    def test_outreach_not_sent(self):
        self.reject(["outreach_sent"],True)

    def test_replay_source_optional(self):
        html = Path("/workspace/lontra-r35-source/msu-memoir.html")
        if not html.exists():
            self.skipTest("Original bytes not present in this runner")
        raw = html.read_bytes()
        module.validate(self.doc,raw)
        with self.assertRaises(AssertionError):
            module.validate(self.doc,raw[:-1]+b"x")

if __name__ == "__main__":
    unittest.main()

