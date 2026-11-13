"""Source and epistemic boundary checks for NORAD 528 NASA catalog day."""
import copy
import json
import unittest
from pathlib import Path
from tools.nasa_528_decay_precision_audit import validate, PATHS

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PATHS]

class DayPrecision(unittest.TestCase):
    def reject(self, idx, mutation):
        items = copy.deepcopy(SOURCES)
        mutation(items[idx])
        with self.assertRaises((ValueError, TypeError, KeyError, StopIteration)):
            validate(*items)

    def test_documentary_bridge_is_connected_but_not_promoted(self):
        x = validate(*SOURCES)
        self.assertEqual(x["catalog_day"], "1963-11-08")
        self.assertEqual(x["report_day_gap_calendar_days_NOT_operational_latency"], 7)
        self.assertIsNone(x["528_timing_sigma_seconds"])
        self.assertEqual(x["physical_constraints_active"], 0)
        self.assertEqual(x["connected_edges"], 5)

    def test_wrong_nasa_day(self):
        self.reject(0, lambda x: x["source"].update(reported_decay_day="1963-11-09"))

    def test_wrong_nasa_hash(self):
        self.reject(0, lambda x: x["source"].update(sha256="0"*64))

    def test_source_changed(self):
        self.reject(1, lambda x: x["sources"][0]["human_table_observation"].update(object_printed="1963 3C"))

    def test_fake_75m_for_528(self):
        self.reject(0, lambda x: x["unknowns"].update(range_sigma_m=75))

    def test_forecast_error_invented(self):
        self.reject(0, lambda x: x["unknowns"].update(forecast_sigma_seconds=3600))

    def test_terminal_instant_invented(self):
        self.reject(0, lambda x: x["unknowns"].update(physical_terminal_utc="1963-11-08T12:00:00Z"))

    def test_day_became_utc_bound(self):
        self.reject(0, lambda x: x["conditional_predicate"].update(active=True))

    def test_observation_type_silently_chosen(self):
        self.reject(0, lambda x: x.update(method_selected="DIRECT_OBSERVATION"))

    def test_spadats_comparator_transferred(self):
        self.reject(0, lambda x: x["comparator"].update(precision_transfer_allowed=True))

    def test_spadats_original_reassigned(self):
        self.reject(2, lambda x: next(o for o in x["occurrences"]
                    if o["id"] == "MOR-NOR-20261112-03").update(source_id="NORAD-528"))

    def test_likelihood_fabricated(self):
        self.reject(0, lambda x: x["likelihood"].update(numeric=0.9))

    def test_domain_promoted(self):
        self.reject(0, lambda x: x["graph"].update(domain_reduced=True))

    def test_lean_promoted(self):
        self.reject(0, lambda x: x["graph"].update(lean_activated=True))

    def test_catalog_gap_as_radar_negative(self):
        self.reject(3, lambda x: x["objects"]["528"].update(
                    status_day_is_observed_non_detection_time=True))

if __name__ == "__main__":
    unittest.main()
