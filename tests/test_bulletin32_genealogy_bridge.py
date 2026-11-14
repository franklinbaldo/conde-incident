"""Adversarial tests for Bulletin 32 bibliographic custody, not NORAD measurements."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import export_bulletin32_genealogy_bridge as bridge


class Bulletin32GenealogyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r60, cls.r61 = bridge.load()
        cls.payload = bridge.build(cls.r60, cls.r61)

    def test_round_trip_exact_publication(self):
        self.assertEqual(bridge.OUTPUT.read_bytes(), bridge.render())
        self.assertTrue(bridge.validate(self.payload))

    def test_bibliographic_and_holdings_paths_are_distinct(self):
        paths = {(e["source"], e["target"]) for e in self.payload["graph"]}
        self.assertIn(("REF:OSZCZAK-1969-13", "WORK:SOVIET-BULLETIN-32-1963"), paths)
        self.assertIn(("DOC:C241-LONTRA-R61", "HOLDING:SOVIET-BULLETIN-32"), paths)
        self.assertIn(("HOLDING:SOVIET-BULLETIN-32", "H:ARTICLE_IDENTITY_UNVERIFIED"), paths)
        self.assertNotIn(("HOLDING:SOVIET-BULLETIN-32", "REF:OSZCZAK-1969-13"), paths)

    def test_all_contracts_inactive(self):
        self.assertEqual(16, self.payload["delta_links"])
        self.assertEqual(0, self.payload["delta_orbital_constraints"])
        self.assertIsNone(self.payload["independence_of_underlying_1963_observations"])
        self.assertEqual("THETA_UNCHANGED", self.payload["physical_domain_effect"])
        self.assertEqual("NOT_PROMOTED", self.payload["lean_candidate"]["status"])
        self.assertTrue(all(not p["activation"] and p["value"] is None
                            for p in self.payload["simulator_parameters"]))
        self.assertTrue(all(e["documentary_only"] and not e["activation"]
                            for e in self.payload["graph"]))

    def test_article_identity_cannot_be_promoted_from_holdings(self):
        for key, value in (("link_to_target_article_status", "ARTICLE_FOUND"),
                           ("primary_article_pages_known", True),
                           ("soviet_bulletin_issue", 33)):
            with self.subTest(key=key):
                r61 = copy.deepcopy(self.r61)
                r61["target"][key] = value
                with self.assertRaises(ValueError):
                    bridge.build(self.r60, r61)

    def test_original_cannot_be_invented(self):
        for key in ("issue_32_facsimile_retrieved", "original_article_retrieved",
                    "station_identified_for_527_529"):
            with self.subTest(key=key):
                r61 = copy.deepcopy(self.r61)
                r61["boundaries"][key] = True
                with self.assertRaises(ValueError):
                    bridge.build(self.r60, r61)

    def test_norad_observation_cannot_be_invented(self):
        for source in ("r60", "r61"):
            r60, r61 = copy.deepcopy(self.r60), copy.deepcopy(self.r61)
            if source == "r60":
                r60["boundaries"]["observations_norad_527_528_529"] = [{"norad": 528}]
            else:
                r61["boundaries"]["independent_observations_norad_527_528_529"] = [{"norad": 528}]
            with self.subTest(source=source), self.assertRaises(ValueError):
                bridge.build(r60, r61)

    def test_1969_bibliography_not_a_1963_measurement(self):
        r60 = copy.deepcopy(self.r60)
        r60["source"]["year"] = 1963
        with self.assertRaises(ValueError):
            bridge.build(r60, self.r61)

    def test_site_mutants_are_rejected(self):
        for section, key, value in (
            ("lean_candidate", "status", "PROMOTED"),
            ("graph", 0, dict(self.payload["graph"][0], activation=True)),
            ("simulator_parameters", 0, {"id": "optical_timing_offset_528",
                                          "value": 0.01, "activation": True}),
        ):
            with self.subTest(field=key):
                p = copy.deepcopy(self.payload)
                p[section][key] = value
                with self.assertRaises(ValueError):
                    bridge.validate(p)

    def test_tampered_manifest_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / bridge.R61
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(self.r61, ensure_ascii=False).replace(
                "N32-37", "N33-37"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 drift"):
                bridge.load_source(root, bridge.R61, bridge.SHA61)

    def test_duplicate_source_json_keys_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate source JSON key"):
            json.loads('{"id":"first","id":"second"}',
                       object_pairs_hook=bridge.reject_duplicate_keys)


if __name__ == "__main__":
    unittest.main()
