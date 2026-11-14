"""R59 source-locked archival leads: adversarial tests, safe under Python -O."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_terminal_control_r59_bridge as bridge


class TerminalControlR59BridgeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger, cls.auditor = bridge.load()

    def case(self):
        return bridge.build(self.ledger, self.auditor)

    def test_site_exact(self):
        self.assertEqual(bridge.OUTPUT.read_bytes(), bridge.render())

    def test_source_pins(self):
        self.assertEqual(64, len(bridge.LEDGER_SHA))
        self.assertEqual(64, len(bridge.AUDITOR_SHA))
        self.assertEqual("C241-1963-TERMINAL-CONTROLS-R59",
                         self.case()["input_sources"][0]["id"])

    def test_seven_distinct_identifiers_and_only_four_new_leads(self):
        obj = self.case()
        self.assertEqual([292, 308, 565, 668], obj["archive_search_order"])
        self.assertEqual(146, obj["catalogue_epochs_new_candidates_total"])
        self.assertEqual({292: 53, 308: 52, 565: 31, 668: 10,
                          637: 25, 688: 1, 528: 45},
                         {e["norad_id"]: e["catalogue_epochs_1963"] for e in obj["observations"]})
        self.assertEqual("TARGET_NOT_CONTROL",
                         next(e for e in obj["observations"] if e["norad_id"] == 528)["role"])

    def test_no_simulation_activation_or_empirical_lean_proof(self):
        obj = self.case()
        self.assertFalse(obj["activation"])
        self.assertEqual("NOT_RUN", obj["historical_mcmc"])
        self.assertEqual("CANDIDATE_ONLY_NOT_COMPILED", obj["lean_status"])
        self.assertEqual("THETA_UNCHANGED", obj["physical_domain_effect"])
        self.assertEqual(0, obj["new_independent_instrumental_observations"])
        self.assertEqual(0, obj["new_activated_physical_constraints"])
        self.assertFalse(obj["catalogue_epochs_are_independent_instrumental_observations"])
        for e in obj["graph"]:
            self.assertFalse(e["activation"])
            self.assertTrue(e["documentary_only"])
        for p in obj["latents"] + obj["simulator_parameters"]:
            self.assertFalse(p["activation"])
            self.assertIsNone(p["value"])

    def test_every_candidate_connected_to_lean_and_parameter(self):
        obj = self.case()
        pairs = {(e["source"], e["target"]) for e in obj["graph"]}
        for sid in bridge.NEW_CANDIDATES:
            self.assertIn(("DOC:R59-LEDGER", f"LEAD:NORAD:{sid}"), pairs)
            self.assertIn((f"LEAD:NORAD:{sid}", f"LATENT:NORAD:{sid}:terminal_utc"), pairs)
            self.assertIn((f"LATENT:NORAD:{sid}:terminal_utc",
                           "LEAN:candidateTerminalControlEvidence"), pairs)
            self.assertIn(("LEAN:candidateTerminalControlEvidence",
                           f"PARAM:terminal_error_control_{sid}"), pairs)

    def test_uncertainty_is_null_not_zero(self):
        for item in self.case()["observations"]:
            self.assertIsNone(item["terminal_sigma_seconds"])
            self.assertIsNone(item["terminal_event_utc"])
            self.assertIsNone(item["date_as_instrumental_utc"])
            self.assertIsNone(item["independent_instrumental_lineages"])
            self.assertIsNone(item["instrument_station"])

    def test_reject_source_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for path in (bridge.LEDGER, bridge.AUDITOR):
                f = root / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((ROOT / path).read_bytes())
            f = root / bridge.LEDGER
            f.write_bytes(f.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(root)

    def test_reject_auditor_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for path in (bridge.LEDGER, bridge.AUDITOR):
                f = root / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes((ROOT / path).read_bytes())
            f = root / bridge.AUDITOR
            f.write_bytes(f.read_bytes().replace(b"ONE_SECONDARY_SPACE_TRACK_MIRROR",
                                                  b"INDEPENDENT_TERMINAL_SENSOR"))
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                bridge.load(root)

    def test_reject_new_physical_observation(self):
        obj = self.case()
        obj["new_independent_instrumental_observations"] = 1
        with self.assertRaises(ValueError):
            bridge.validate(obj)

    def test_reject_calibrated_utc_fabrication(self):
        obj = self.case()
        obj["observations"][0]["terminal_event_utc"] = "1963-11-26T12:00:00Z"
        with self.assertRaises(ValueError):
            bridge.validate(obj)

    def test_reject_zero_sigma(self):
        obj = self.case()
        obj["observations"][0]["terminal_sigma_seconds"] = 0
        with self.assertRaises(ValueError):
            bridge.validate(obj)

    def test_reject_duplicate_edge(self):
        obj = self.case()
        obj["graph"].append(copy.deepcopy(obj["graph"][0]))
        with self.assertRaises(ValueError):
            bridge.validate(obj)

    def test_reject_catalogue_as_independent_sensors(self):
        obj = self.case()
        obj["catalogue_epochs_are_independent_instrumental_observations"] = True
        with self.assertRaises(ValueError):
            bridge.validate(obj)

    def test_reject_role_drift(self):
        with patch.dict(bridge.screen.CASES,
                        {528: ("1963-11-08", "https://ntrs.nasa.gov/",
                               "NASA_SSR_CALENDAR_DAY_TZ_UNVERIFIED", "CANDIDATE")}):
            with self.assertRaises(ValueError):
                self.case()

    def test_reject_count_drift(self):
        with patch.dict(bridge.screen.EXPECTED_DISTINCT, {292: 54}):
            with self.assertRaises(ValueError):
                self.case()


if __name__ == "__main__":
    unittest.main()
