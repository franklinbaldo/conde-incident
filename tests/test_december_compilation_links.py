"""C227/C228 cumulative links: a corrected printed cell is not a sensor."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import provenance_graph as pg
import december_compilation_links as dc
import export_observable_dependency_links as observable


class DecemberCompilationLinksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge_raw = (ROOT / dc.BRIDGE).read_bytes()
        cls.bridge = json.loads(cls.bridge_raw)
        cls.rows = pg.matrix_occurrences(pg.MATRIX.read_bytes())

    def test_snapshot_qualified_matrix_and_three_nonindependent_edges(self):
        edges = dc.build(self.bridge, self.rows)
        self.assertEqual(len(edges), 3)
        self.assertEqual([e["matrix_occurrence"].rsplit(":", 1)[-1]
                          for e in edges], ["C227#1", "C227#1", "C228#1"])
        self.assertEqual([e["printed_period_min_not_instrument_observation"]
                          for e in edges], ["89.2", "94.6", None])
        self.assertEqual(len({e["same_work_id"] for e in edges}), 1)
        self.assertEqual(edges[2]["relation"], "CATALOGUE_OF_SAME_WORK_NOT_SECOND_SENSOR")
        self.assertTrue(all(e["instrument_epoch_utc"] is None
                            and e["instrument_covariance"] is None
                            and e["activation"] is False
                            and e["independent_sensor"] is False
                            and e["physical_domain_effect"] == "THETA_UNCHANGED"
                            for e in edges))

    def test_cumulative_aggregate_replays_source_ledger_exactly(self):
        aggregate = observable.build()
        self.assertEqual(aggregate["pending_december_compilation_edges"],
                         dc.build(self.bridge, self.rows))
        self.assertEqual(aggregate["december_bridge_sha256"],
                         dc.hashlib.sha256(self.bridge_raw).hexdigest())

    def test_adversarial_source_edits_are_rejected(self):
        examples = {
            "wrong_period": ("erratum_verified_printed_min", "89.6"),
            "false_sigma": ("sensor_covariance", [[0.1]]),
            "false_epoch": ("sensor_epochs_utc", "1963-12-31T12:00:00Z"),
            "false_tracking": ("source_to_instrument_mapping_verified", True),
            "false_physical_fit": ("active_physical_constraint", True),
            "false_independence": ("same_institutional_family_not_independent_sensors", False),
            "false_errata": ("erratum_state", "STILL_UNRESOLVED"),
            "false_diff": ("conditional_differential_range_min", ["1.00", "1.10"]),
        }
        for label, (key, value) in examples.items():
            with self.subTest(label=label):
                bad = copy.deepcopy(self.bridge)
                bad[key] = value
                with self.assertRaisesRegex(ValueError, "December compilation links"):
                    dc.build(bad, self.rows)

    def test_adversarial_pdf_and_asof_edits_are_rejected(self):
        for key, value in (("pdf_sha256", "0" * 64),
                           ("ntrs", "19640002493"),
                           ("report_as_of_utc_not_sensor_epoch", "1963-12-31T14:00:00Z"),
                           ("matrix_context_not_independent_sensor", ["C228#1"])):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.bridge)
                bad["source_editions"][-1][key] = value
                with self.assertRaises(ValueError):
                    dc.build(bad, self.rows)

    def test_noncanonical_matrix_and_false_context_rejected(self):
        with self.assertRaises(ValueError):
            dc.build(self.bridge, self.rows[:-1])
        bad_rows = copy.deepcopy(self.rows)
        next(r for r in bad_rows if r["occurrence"] == "C227#1")["row_sha256"] =             next(r for r in bad_rows if r["occurrence"] == "C228#1")["row_sha256"]
        with self.assertRaisesRegex(ValueError, "matrix crosswalk"):
            dc.build(self.bridge, bad_rows)


if __name__ == "__main__":
    unittest.main()
