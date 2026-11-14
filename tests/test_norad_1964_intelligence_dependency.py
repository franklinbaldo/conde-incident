"""Adversarial contracts for the 1964 NORAD Z-window, not a 1963 sensor log."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_norad_1964_intelligence_dependency as bridge


class NORADClockContext(unittest.TestCase):
    def setUp(self):
        self.l65, self.l64 = bridge.load()
        self.p = bridge.build(self.l65, self.l64)

    def falsify_source(self, section, key, value):
        x = copy.deepcopy(self.l65)
        x[section][key] = value
        with self.assertRaises(ValueError):
            bridge.build(x, self.l64)

    def falsify_output(self, section, key, value):
        x = copy.deepcopy(self.p)
        x[section][key] = value
        with self.assertRaises(ValueError):
            bridge.validate(x)

    def test_site_bytes(self):
        self.assertEqual(bridge.OUTPUT.read_bytes(), bridge.render())

    def test_no_new_sensor_or_constraints(self):
        self.assertEqual(0, self.p["new_independent_instrumental_observations_528"])
        self.assertEqual("THETA_UNCHANGED", self.p["physical_domain_effect"])
        self.assertIsNone(self.p["simulator_parameters"][1]["value"])

    def test_documentary_paths(self):
        g = {(x["source"], x["target"]) for x in self.p["graph"]}
        self.assertIn(("DOC:C241-L65", "ROW:COSMOS34-1964"), g)
        self.assertIn(("H:NO_TRANSFER_1964_TO_1963", "LEAN:candidateNoCalibrationTransfer"), g)
        self.assertIn(("LEAN:candidateNoCalibrationTransfer", "PARAM:terminal_sigma_528"), g)

    def test_not_1963(self):
        self.falsify_source("report", "event_date", "1963-11-08")

    def test_not_confirmed_deorbit(self):
        self.falsify_source("report", "qualifier", "confirmed")

    def test_not_1963_528(self):
        self.falsify_source("interpretation", "same_event_as_1963_norad_528", True)

    def test_not_1963_308(self):
        self.falsify_source("interpretation", "same_event_as_1963_norad_308", True)

    def test_no_false_sigma(self):
        self.falsify_source("report", "time_uncertainty_sigma_seconds", 300)

    def test_no_fabricated_sensor(self):
        self.falsify_source("report", "sensor", "radar hypothetical")

    def test_no_synthetic_epoch(self):
        self.falsify_source("report", "observation_epoch", "1964-07-09T09:33Z")

    def test_no_1964_to_528_transfer(self):
        self.falsify_source("interpretation", "permits_five_minute_sigma_for_528", True)

    def test_no_528_point(self):
        self.falsify_source("interpretation", "permits_utc_terminal_point_for_528", True)

    def test_no_primary_norad308_identity(self):
        l64 = copy.deepcopy(self.l64)
        l64["observation"]["nasa_printed_norad_id"] = 308
        with self.assertRaises(ValueError):
            bridge.build(self.l65, l64)

    def test_no_sensor_transfer_in_output(self):
        self.p["records"][0]["sensor"] = "fabricated"
        with self.assertRaises(ValueError):
            bridge.validate(self.p)

    def test_no_numeric_sigma_in_output(self):
        self.p["records"][0]["calibrated_sigma_seconds"] = 300
        with self.assertRaises(ValueError):
            bridge.validate(self.p)

    def test_no_physical_activation(self):
        self.p["activation"] = True
        with self.assertRaises(ValueError):
            bridge.validate(self.p)

    def test_no_lean_promotion(self):
        self.p["lean_candidates"][0]["activation"] = True
        with self.assertRaises(ValueError):
            bridge.validate(self.p)

    def test_no_parameter_promotion(self):
        self.p["simulator_parameters"][0]["value"] = 300
        with self.assertRaises(ValueError):
            bridge.validate(self.p)

    def test_no_duplicate_graph_edge(self):
        self.p["graph"].append(copy.deepcopy(self.p["graph"][0]))
        with self.assertRaises(ValueError):
            bridge.validate(self.p)

    def test_wrong_parent_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for path in (bridge.L65, bridge.L64):
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            (root / bridge.L64).write_bytes((root / bridge.L64).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(root)

    def test_wrong_norad_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for path in (bridge.L65, bridge.L64):
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((ROOT / path).read_bytes())
            (root / bridge.L65).write_bytes((root / bridge.L65).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(root)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            bridge.unique_pairs([("x", 1), ("x", 2)])


if __name__ == "__main__":
    unittest.main()
