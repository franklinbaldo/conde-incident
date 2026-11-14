"""Adversarial checks for provenance of 1964 Soviet / 1963 NASA print crosswalk."""
import copy
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import export_soviet_nasa_dependency_bridge as bridge


class SovietNasaDependency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.hashes = bridge.load()

    def mutate(self, identifier, action):
        inputs = copy.deepcopy(self.data)
        action(inputs[identifier])
        with self.assertRaises(ValueError):
            bridge.build(inputs, self.hashes)

    def test_replay_deterministic(self):
        import json
        self.assertEqual(bridge.OUT.read_bytes(), bridge.render())
        data = json.loads(bridge.render())
        self.assertEqual(len(data["graph"]), 14)
        self.assertEqual(len(data["latents"]), 8)
        self.assertEqual([x["norad_id"] for x in data["other_target_candidates"]], [527, 528, 529])
        self.assertEqual(data["nasa_print_row"], "1963-003A")
        self.assertIsNone(data["soviet_row_explicit_norad_id"])
        self.assertIsNone(data["independent_instrumental_families"])
        self.assertIsNone(data["instrumental_observation_epoch_utc"])
        self.assertFalse(data["activation"])
        self.assertEqual(data["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertTrue(all(e["activation"] is False for e in data["graph"]))
        self.assertTrue(all(p["value"] is None and p["activation"] is False for p in data["latents"]))
        self.assertEqual(data["printed_orbital_comparison"]["period_min"]["absolute_difference_min"], "0.06")
        self.assertFalse(data["printed_orbital_comparison"]["period_min"]["nasa_one_decimal_rounding_of_soviet"])

    def test_mutated_source_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            for path, _ in bridge.SOURCES.values():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            self.assertEqual(bridge.render(root), bridge.render())
            target = root / bridge.SOURCES["C241-LONTRA-R49"][0]
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source hash drift"):
                bridge.render(root)

    def test_identity_and_independence_cannot_be_promoted(self):
        self.mutate("C241-LONTRA-R49", lambda x: x["sources"]["soviet"].update(printed_norad=528))
        self.mutate("C241-LONTRA-R49", lambda x: x["sources"]["nasa"].update(row_designator="1963-003B"))
        self.mutate("C241-LONTRA-R49", lambda x: x["interpretation"].update(independent_soviet_sensor_or_time_utc_proven=True))
        self.mutate("C241-LONTRA-R48", lambda x: x["target"].update(measured_NORAD_527_528_529_in_retrieved_document=True))

    def test_dates_and_values_are_not_orbital_observation_epoch(self):
        self.mutate("C241-LONTRA-R49", lambda x: x["sources"]["soviet"].update(publication_year=1963))
        self.mutate("C241-LONTRA-R49", lambda x: x["comparison"]["period_min"].update(nasa_one_decimal_rounding_of_soviet=True))
        self.mutate("C241-LONTRA-R49", lambda x: x["comparison"]["apogee_km"].update(nasa=532))
        self.mutate("C241-L18", lambda x: x["sources"][1]["rows"][0].update(perigee_km=458))

    def test_duplicate_json_keys_fail_closed(self):
        import json
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"activation":false,"activation":true}', object_pairs_hook=bridge.no_duplicate_keys)


if __name__ == "__main__":
    unittest.main()
