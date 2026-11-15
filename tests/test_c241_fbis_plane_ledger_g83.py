"""G83: adversarial tests for clock/plane join without historical inference."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import c241_fbis_plane_ledger_g83 as m  # noqa: E402


class ClockPlaneLedgerG83(unittest.TestCase):
    def test_exact_replay_and_decision_guards(self):
        data = m.generate(ROOT)
        self.assertEqual(m.payload(ROOT), (ROOT / m.OUTPUT).read_bytes())
        self.assertEqual(len(data["rows"]), 34)
        self.assertEqual(data["clock_decision"], "UNRESOLVED")
        self.assertFalse(data["orbit_exclusion_licensed"])
        self.assertFalse(data["active_constraint"])
        self.assertFalse(data["posterior"])
        self.assertIsNone(data["impact_probability"])
        self.assertIsNone(data["historical_event_time_utc"])
        self.assertTrue(all(r["independent_event_time_871"] is None
                            and r["other_unverified_conditional_order"] is None
                            for r in data["rows"]))

    def test_both_models_and_clock_split(self):
        counts = m.generate(ROOT)["counts"]
        for model in ("CONSTANT_A", "DECAYING_A_LAST_SECANT"):
            a = counts["528_" + model]
            self.assertEqual((a["rows"], a["gmt_before"], a["gmt_after"]), (9, 6, 3))
            self.assertEqual((a["rio_before"], a["rio_after"]), (7, 2))
            b = counts["637_" + model]
            self.assertEqual((b["rows"], b["gmt_before"], b["gmt_after"]), (8, 6, 2))
            self.assertEqual((b["rio_before"], b["rio_after"]), (6, 2))

    def test_only_one_528_root_changes_order_with_clock(self):
        rows = [r for r in m.generate(ROOT)["rows"] if r["norad"] == 528]
        switched = [r for r in rows if r["gmt_conditional_order"] != r["rio_local_conditional_order"]]
        self.assertEqual(len(switched), 2)
        self.assertTrue(all(r["crossing_utc"].startswith("1963-11-08T23:4") for r in switched))
        self.assertTrue(all(r["gmt_conditional_order"] == "AFTER"
                            and r["rio_local_conditional_order"] == "BEFORE" for r in switched))

    def sandbox(self, target: Path) -> None:
        for path in (m.CLOCK, *m.REPORTS):
            dst = target / path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, dst)

    def mutate(self, target: Path, path: str, fn) -> None:
        file = target / path
        data = json.loads(file.read_text(encoding="utf-8"))
        fn(data)
        file.write_text(json.dumps(data), encoding="utf-8")

    def test_reject_clock_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root, m.CLOCK, lambda d: d.__setitem__("verification_status", "VERIFIED"))
            with self.assertRaisesRegex(ValueError, "clock guard"):
                m.generate(root)

    def test_reject_unverified_branch_fabrication(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root, m.CLOCK, lambda d: d["conditional_branches"]["OTHER_UNVERIFIED"].__setitem__(
                "broadcast_utc_if_assumption_holds", "1963-11-09T00:00Z"))
            with self.assertRaisesRegex(ValueError, "unknown clock"):
                m.generate(root)

    def test_reject_mismatched_bahia_hour(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root, m.REPORTS[0], lambda d: d["crossings"][0].__setitem__(
                "crossing_bahia_utc_minus_3", "1963-11-05 00:00:00"))
            with self.assertRaisesRegex(ValueError, "Bahia"):
                m.generate(root)

    def test_reject_repeated_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sandbox(root)
            self.mutate(root, m.REPORTS[0], lambda d: d["crossings"].__setitem__(
                1, deepcopy(d["crossings"][0])))
            with self.assertRaisesRegex(ValueError, "unique"):
                m.generate(root)

    def test_source_637_past_day_cutoff_never_licensed(self):
        rows = [r for r in m.generate(ROOT)["rows"] if r["norad"] == 637]
        self.assertTrue(any(not r["within_nasa_utc_day_scenario"] for r in rows))
        self.assertTrue(any(not r["within_nasa_bahia_day_scenario"] for r in rows))
        self.assertFalse(m.generate(ROOT)["orbit_exclusion_licensed"])


if __name__ == "__main__":
    unittest.main()
