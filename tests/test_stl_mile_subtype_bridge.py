"""R53 bridge fidelity and adversarial physical no-promotion tests; work under -O."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_stl_mile_subtype_bridge as bridge

class R53Bridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r53, cls.parent = bridge.load()

    def test_site_exact_bytes(self):
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())

    def test_zero_promotions_and_family_dependency(self):
        d = bridge.build(self.r53, self.parent)
        self.assertFalse(d["activation"])
        self.assertEqual("THETA_UNCHANGED", d["physical_domain_effect"])
        self.assertEqual(0, d["new_activated_physical_constraints"])
        self.assertIsNone(d["physical_observation_count_in_corpus"])
        self.assertEqual(0, d["new_november_observations_527_528_529"])
        self.assertFalse(d["independent_from_R51"])
        self.assertEqual(0, d["new_independent_instrumental_observations"])
        self.assertTrue(all(e["documentary_only"] and not e["activation"] for e in d["graph"]))
        self.assertTrue(all(x["value"] is None and not x["activation"] for x in d["latents"]))
        self.assertTrue(all(x["value"] is None and not x["activation"] for x in d["simulator_parameters"]))

    def test_all_five_controls_not_november_528(self):
        d = bridge.build(self.r53, self.parent)
        self.assertEqual(["1963 3A", "1963 3A", "1963 6A", "1963 4A", "1963 4A"],
                         [x["designation"] for x in d["diagnostics"]["rows"]])
        self.assertEqual("miles", d["printed_unit_verified"])
        self.assertEqual("statute_miles", d["numerically_favoured_subtype"])
        self.assertFalse(d["original_STL_unit_subtype_certified"])
        self.assertIsNone(d["subtype_value_for_orbit_simulation"])
        self.assertIn("NORAD 528", d["not_equivalent_to"])

    def reject(self, source, path, value):
        r53, parent = copy.deepcopy(self.r53), copy.deepcopy(self.parent)
        target = r53 if source == "r53" else parent
        for step in path[:-1]:
            target = target[step]
        target[path[-1]] = value
        with self.assertRaises(ValueError):
            bridge.build(r53, parent)

    def test_no_fabricated_stl_original(self):
        self.reject("r53", ["source", "upstream_original_retrieved"], True)

    def test_no_fake_statute_legend(self):
        self.reject("r53", ["conclusion", "statute_subtype_certified_by_printed_legend"], True)

    def test_no_new_sensor(self):
        self.reject("r53", ["conclusion", "new_instrumental_sensors"], 1)

    def test_no_new_november_observation(self):
        self.reject("r53", ["conclusion", "new_observations_527_528_529_november"], 1)

    def test_nautical_not_supported(self):
        self.reject("r53", ["conclusion", "favoured_by_internal_consistency"], "nautical_miles")

    def test_parent_not_528(self):
        self.reject("parent", ["printed_identity"], "1963 3B")

    def test_parent_not_activated(self):
        self.reject("parent", ["activation"], True)

    def test_parent_same_pdf(self):
        self.reject("parent", ["custody", "pdf_sha256"], "0" * 64)

    def test_parent_no_certified_subtype(self):
        self.reject("parent", ["altitude_mile_subtype_verified"], "statute_miles")

    def test_parent_unknown_column_semantics(self):
        self.reject("parent", ["pair_mapping_proven"], True)

    def check_tamper(self, path):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for src in (bridge.R53_PATH, bridge.PARENT_PATH):
                target = root / src
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / src).read_bytes())
            target = root / path
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(root)

    def test_r53_hash_mutant(self):
        self.check_tamper(bridge.R53_PATH)

    def test_parent_hash_mutant(self):
        self.check_tamper(bridge.PARENT_PATH)

if __name__ == "__main__":
    unittest.main()
