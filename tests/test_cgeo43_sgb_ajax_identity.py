"""Adversarial tests for CGEO-43 using the four real source-derived excerpts."""
import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cgeo43", ROOT / "tools/cgeo43_sgb_ajax_identity.py")
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
MANIFEST = json.loads((ROOT / "research/geo/cgeo43_sgb_ajax_folder_identity.json").read_text())


def load(path):
    return (ROOT / path).read_bytes()


class SgbAjaxIdentityTests(unittest.TestCase):
    def test_real_excerpts_reject_false_image(self):
        self.assertEqual(mod.verify(MANIFEST, load), "CGEO43_FALLBACK_FALSE_ATTRIBUTION_BLOCKED")

    def test_get_1850_is_not_ajax_0335(self):
        p = MANIFEST["probes"][0]
        self.assertFalse(mod.compare_pair(mod.parse_excerpt(load(p["pre_selection"]["file"])),
                                          mod.parse_excerpt(load(p["ajax"]["file"]))))

    def test_second_control_1851_also_falls_back(self):
        p = MANIFEST["probes"][1]
        self.assertFalse(mod.compare_pair(mod.parse_excerpt(load(p["pre_selection"]["file"])),
                                          mod.parse_excerpt(load(p["ajax"]["file"]))))

    def test_tampered_selected_label_fails_hash(self):
        p = MANIFEST["probes"][0]["pre_selection"]["file"]
        def tampered(path):
            return load(path).replace(b"1850 Projeto", b"0335 Projeto") if path == p else load(path)
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            mod.verify(MANIFEST, tampered)

    def test_tampered_ajax_value_fails_hash(self):
        p = MANIFEST["probes"][0]["ajax"]["file"]
        def tampered(path):
            return load(path).replace(b"_selectedValue: 1", b"_selectedValue: 680") if path == p else load(path)
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            mod.verify(MANIFEST, tampered)

    def test_relabeling_cache_to_1850_is_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["probes"][0]["ajax"]["label"] = m["probes"][0]["pre_selection"]["label"]
        with self.assertRaisesRegex(ValueError, "response identity"):
            mod.verify(m, load)

    def test_reassigning_image_to_1850_is_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["image_response_observed"]["attribution"] = "MI_1850"
        with self.assertRaisesRegex(ValueError, "unearned image attribution"):
            mod.verify(m, load)

    def test_counterfeit_image_sha_is_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["image_response_observed"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "cached image"):
            mod.verify(m, load)

    def test_orbital_promotion_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["can_constrain_orbital_reentry"] = True
        with self.assertRaisesRegex(ValueError, "orbital"):
            mod.verify(m, load)

    def test_geom_promotion_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["historical_center_geometry"] = [0, 0]
        with self.assertRaisesRegex(ValueError, "historical geometry"):
            mod.verify(m, load)

    def test_missing_image_src_is_not_positive(self):
        p = MANIFEST["probes"][0]
        before = mod.parse_excerpt(load(p["pre_selection"]["file"]))
        after = dict(before)
        self.assertFalse(mod.compare_pair(before, after))

    def test_duplicate_observation_is_invalid(self):
        text = load(MANIFEST["probes"][0]["pre_selection"]["file"])
        with self.assertRaises(ValueError):
            mod.parse_excerpt(text + b"PastaTxt: fake\n")


if __name__ == "__main__":
    unittest.main()
