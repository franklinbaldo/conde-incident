"""Adversarial checks: UN registered status is not an orbital tracking epoch."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_un_1963_status_bridge import UN, NASA, PRECISION, OUT, build, render


class UnStatusBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = [json.loads((ROOT / p).read_text()) for p in (UN, NASA, PRECISION)]

    def mutate(self, index=None, edit=None):
        parents = copy.deepcopy(self.parents)
        if index is not None:
            edit(parents[index])
        return build(*parents, {})

    def test_three_documentary_rows_are_distinct_from_sensors(self):
        b = self.mutate()
        self.assertEqual([x["norad_via_retrospective_c241_l32"]
                          for x in b["catalogued_elements"]], [527, 528, 529])
        self.assertEqual(b["independent_instrument_observations_added"], 0)
        self.assertEqual(b["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertEqual(len(b["source_dependency_graph"]), 10)
        self.assertTrue(all(x["instrument_epoch_utc"] is None and
                            not x["activation"] for x in b["catalogued_elements"]))
        self.assertTrue(all(x["value"] is None and not x["active"]
                            for x in b["simulator_latent_parameters"]))

    def test_six_original_edges_preserved(self):
        b = self.mutate()
        self.assertEqual(b["source_dependency_graph"][:6],
                         self.parents[0]["graph_extension"]["edges"])

    def test_printed_period_cannot_change(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["docs"][0]["printed_rows"][1].update(
                nodal_period_min_printed="94.7"))

    def test_wrong_norad_crosswalk_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["docs"][0]["printed_rows"][1].update(
                norad_from_nasa_1977=529))

    def test_facsimile_sha_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["docs"][1].update(sha256="0" * 64))

    def test_facsimile_page_swap_rejected(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["docs"][1].update(relevant_pdf_page_index=0))

    def test_publication_date_not_report_cutoff(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["docs"][1].update(
                report_cutoff_printed="2400Z 31 DECEMBER 1963"))

    def test_no_false_terminal_epoch(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["interpretation"].update(
                observation_epoch_528="1963-11-15T00:00:00Z"))

    def test_no_false_un_explicit_radar(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["interpretation"].update(
                independent_sensor_observations_added=1))

    def test_october_incremental_list_is_not_negative_detection(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["interpretation"].update(
                controls_54_55_constrain_survival=True))

    def test_1977_identity_not_1963_sensor(self):
        with self.assertRaises(ValueError):
            self.mutate(1, lambda x: x["row"].update(source_528_sensor_id="RADAR"))

    def test_nasa_day_cannot_activate(self):
        with self.assertRaises(ValueError):
            self.mutate(2, lambda x: x["conditional_predicate"].update(active=True))

    def test_original_graph_activation_stays_false(self):
        with self.assertRaises(ValueError):
            self.mutate(0, lambda x: x["graph_extension"].update(
                physical_domain_reduced=True))

    def test_published_json_byte_exact(self):
        self.assertEqual(OUT.read_bytes(), render())


if __name__ == "__main__":
    unittest.main()
