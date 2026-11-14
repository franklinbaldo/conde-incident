"""Adversarial regression for NASA SSR 29-30 Oct control 308 source genealogy."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_ssr308_l64_dependency as bridge


class SSR308DependencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l64, cls.r59 = bridge.load()

    def case(self):
        return bridge.build(copy.deepcopy(self.l64), copy.deepcopy(self.r59))

    def test_exact_rebuild_of_public_feed(self):
        self.assertEqual(bridge.OUTPUT.read_bytes(), bridge.render())

    def test_sha256_of_both_parents_pinned(self):
        self.assertEqual(64, len(bridge.L64_SHA))
        self.assertEqual(64, len(bridge.R59_SHA))
        self.assertEqual([bridge.L64_SHA, bridge.R59_SHA],
                         [s["sha256"] for s in self.case()["sources"]])

    def test_original_printed_range_and_separate_secondary_day(self):
        o = self.case()["observation"]
        self.assertEqual(["1963-10-29", "1963-10-30"], o["printed_calendar_range"])
        self.assertEqual("1963-10-30", o["r59_secondary_calendar_day"])
        self.assertFalse(o["range_is_instrumental_utc"])

    def test_provisional_identity_never_nasa_printed_norad(self):
        o = self.case()["observation"]
        self.assertEqual(308, o["secondary_norad_id"])
        self.assertEqual("SECONDARY_CROSSWALK_PENDING_PRIMARY_NORAD_ID", o["identity_grade"])
        self.assertIsNone(o["nasa_printed_norad_id"])

    def test_graph_reaches_lean_and_simulator_without_promotion(self):
        p = self.case()
        pairs = {(e["source"], e["target"]) for e in p["graph"]}
        self.assertIn(("DOC:C241-L64", "ROW:NASA-OMEGA1-1963"), pairs)
        self.assertIn(("H:CALENDAR_RANGE_NOT_UTC",
                       "LATENT:NORAD:308:terminal_utc"), pairs)
        self.assertIn(("LATENT:NORAD:308:terminal_utc",
                       "LEAN:candidateTerminalControlEvidence"), pairs)
        self.assertIn(("LEAN:candidateTerminalControlEvidence",
                       "PARAM:terminal_error_control_308"), pairs)
        self.assertEqual(14, len(pairs))
        for e in p["graph"]:
            self.assertTrue(e["documentary_only"])
            self.assertFalse(e["activation"])

    def test_physics_and_holdout_remain_inactive(self):
        p = self.case()
        self.assertFalse(p["activation"])
        self.assertEqual("THETA_UNCHANGED", p["physical_domain_effect"])
        self.assertEqual("NOT_RUN", p["historical_mcmc"])
        self.assertEqual(0, p["new_activated_physical_constraints"])
        self.assertEqual(0, p["new_independent_instrumental_observations"])
        for item in p["simulator_parameters"]:
            self.assertIsNone(item["value"])
            self.assertFalse(item["activation"])

    def test_no_utc_station_sensor_or_error_invented(self):
        o = self.case()["observation"]
        for field in ("terminal_event_utc", "terminal_sigma_seconds", "station",
                      "sensor", "reference_frame", "independent_instrumental_lineages"):
            self.assertIsNone(o[field])

    def test_corrupt_l64_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            for path in (bridge.L64, bridge.R59):
                f = p / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((ROOT / path).read_bytes())
            f = p / bridge.L64
            f.write_bytes(f.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(p)

    def test_corrupt_r59_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            for path in (bridge.L64, bridge.R59):
                f = p / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((ROOT / path).read_bytes())
            f = p / bridge.R59
            f.write_bytes(f.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(p)

    def test_reject_fabricated_nasa_norad(self):
        source = copy.deepcopy(self.l64)
        source["original_row"]["printed_norad_id"] = 308
        with self.assertRaises(ValueError):
            bridge.build(source, self.r59)

    def test_reject_edited_primary_day(self):
        source = copy.deepcopy(self.l64)
        source["original_row"]["calendar_range_start"] = "1963-10-30"
        with self.assertRaises(ValueError):
            bridge.build(source, self.r59)

    def test_reject_crosswalk_as_primary(self):
        source = copy.deepcopy(self.l64)
        source["identity"]["identity_status"] = "PRIMARY_NASA_CONFIRMED"
        with self.assertRaises(ValueError):
            bridge.build(source, self.r59)

    def test_reject_r59_day_relabel(self):
        parent = copy.deepcopy(self.r59)
        next(x for x in parent["observations"] if x["norad_id"] == 308)[
            "reported_calendar_day"] = "1963-10-29"
        with self.assertRaises(ValueError):
            bridge.build(self.l64, parent)

    def test_reject_fake_terminal_utc(self):
        p = self.case()
        p["observation"]["terminal_event_utc"] = "1963-10-30T00:00:00Z"
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_fake_zero_sigma(self):
        p = self.case()
        p["observation"]["terminal_sigma_seconds"] = 0
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_theta_activation(self):
        p = self.case()
        p["simulator_parameters"][0]["value"] = 12.0
        p["simulator_parameters"][0]["activation"] = True
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_duplicate_edge(self):
        p = self.case()
        p["graph"].append(copy.deepcopy(p["graph"][0]))
        with self.assertRaises(ValueError):
            bridge.validate(p)

    def test_reject_sensor_count_as_new_observation(self):
        p = self.case()
        p["new_independent_instrumental_observations"] = 1
        with self.assertRaises(ValueError):
            bridge.validate(p)


if __name__ == "__main__":
    unittest.main()
