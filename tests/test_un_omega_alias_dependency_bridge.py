"""Fail-closed R60 UN Omega alias and editorial cutoff bridge."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import export_un_omega_alias_dependency_bridge as bridge


class TestUnOmegaAliasBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = bridge.load()
        cls.result = bridge.build(cls.data)

    def test_site_exact_source_hashes(self):
        self.assertEqual((bridge.ROOT / bridge.OUTPUT).read_bytes(), bridge.render())
        self.assertEqual({x["sha256"] for x in self.result["sources"]},
                         {x[1] for x in bridge.SOURCES.values()})

    def test_graph_and_identity(self):
        r = self.result
        self.assertEqual("C241-ABELHA-R60-UN-OMEGA", r["id"])
        self.assertEqual(28, r["delta_links"])
        self.assertEqual(5, len(r["latents"]))
        self.assertEqual(2, len(r["simulator_parameters"]))
        self.assertFalse(r["activation"])
        self.assertEqual("NOT_PROMOTED", r["lean_candidate"]["status"])
        self.assertTrue(all(x["value"] is None and not x["activation"]
                            for x in r["latents"] + r["simulator_parameters"]))

    def test_fragments_not_main_object(self):
        r = self.result["reported_roles"]
        self.assertEqual("MAIN_REGISTERED_OBJECT", r["1962 Omega 1"])
        self.assertEqual("FRAGMENT", r["1962 Omega 2"])
        self.assertEqual("FRAGMENT", r["1962 Omega 3"])

    def test_calendar_does_not_create_terminal_epoch(self):
        c = self.result["calendar_comparison"]
        self.assertEqual("Decay before", c["un_heading"])
        self.assertEqual("1963-10-31", c["un_calendar_cutoff"])
        self.assertIsNone(c["converted_terminal_utc"])
        self.assertIsNone(c["crosswalk_norad_308"])
        self.assertFalse(c["calendar_label_is_calibrated_utc"])
        self.assertEqual(0, self.result["delta_orbital_constraints"])
        self.assertEqual("THETA_UNCHANGED", self.result["physical_domain_effect"])

    def test_un_manifest_mutations(self):
        for section, key, value in [
            ("sources", "original_un_document_scans_verified", True),
            ("sources", "instrumental_independence_from_nasa_catalog_verified", True),
            ("boundaries", "direct_un_to_norad_308_crosswalk", True),
            ("boundaries", "terminal_instant_utc", "1963-10-31T00:00:00Z"),
            ("boundaries", "terminal_sigma_hours", 1.0),
        ]:
            d = copy.deepcopy(self.data)
            d["UN-R66"][section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                bridge.build(d)

    def test_fragment_and_cutoff_mutations(self):
        for row, key, value in [
            (1, "role", "MAIN_REGISTERED_OBJECT"),
            (2, "role", "MAIN_REGISTERED_OBJECT"),
            (3, "field_heading", "Decay at"),
            (3, "reported_before_date", "1963-10-30"),
        ]:
            d = copy.deepcopy(self.data)
            d["UN-R66"]["transcribed_rows"][row][key] = value
            with self.subTest(row=row, key=key), self.assertRaises(ValueError):
                bridge.build(d)

    def test_nasa_genealogy_cannot_promote_identity(self):
        for key, value in [
            ("identity_norad_308", 308),
            ("report_cutoff_is_observation_epoch", True),
            ("activation", True),
        ]:
            d = copy.deepcopy(self.data)
            d["NASA-OMEGA-R58"]["october_catalogue"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                bridge.build(d)

    def test_output_mutations_are_rejected(self):
        for section, key, value in [
            ("calendar_comparison", "converted_terminal_utc", "1963-10-30T00:00:00Z"),
            ("calendar_comparison", "crosswalk_norad_308", 308),
            ("lean_candidate", "status", "PROMOTED"),
            ("simulator_parameters", 0,
             {"id": bridge.PARAMETERS[0], "value": 30.0, "activation": True}),
            ("graph", 0,
             dict(self.result["graph"][0], activation=True)),
        ]:
            d = copy.deepcopy(self.result)
            d[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                bridge.validate(d)

    def test_pinned_sha_prevents_unreviewed_source_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path, _ in bridge.SOURCES.values():
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((bridge.ROOT / path).read_bytes())
            key = bridge.SOURCES["UN-R66"][0]
            (root / key).write_bytes((root / key).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(root)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"cutoff": "before", "cutoff": "at"}',
                       object_pairs_hook=bridge.unique_keys)


if __name__ == "__main__":
    unittest.main()
