"""C241-L18/L19 source-locked consumer: reject historical 94.8 without editing legacy."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_ssr_source_locked_links import NOV15, NOV30, LEGACY, HOUSE, OUT, build, render


class SourceLockedSSRSpec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = json.loads(NOV15.read_text())
        cls.b = json.loads(NOV30.read_text())
        cls.g = json.loads(LEGACY.read_text())
        cls.house = json.loads(HOUSE.read_text())

    def test_two_ledgers_canonicalize_erroneous_frozen_graph(self):
        original = next(x for x in self.g["observations"]
                        if x["id"] == "SSR-1963-11-30-NORAD527-nodal_period")
        self.assertEqual(original["value"], 94.8)
        out = build(self.a, self.b, self.g, self.house)
        self.assertEqual(out["canonical_value_min"], "94.6")
        self.assertEqual(out["canonical_value_seconds"], "5676")
        self.assertEqual(out["documentary_delta_min"], "0.0")
        self.assertEqual(out["checked_control_cells"], 16)
        self.assertEqual(out["checked_distinct_control_objects"], [527, 529])
        self.assertFalse(out["active_physical_constraint"])
        self.assertEqual(out["physical_domain_effect"], "THETA_UNCHANGED")
        self.assertIsNone(out["simulator_observation_epoch_utc"])
        self.assertIsNone(out["simulator_instrument_error"])
        self.assertIsNone(out["simulator_calibrated_value"])
        self.assertEqual(out["linked_lean_contract"], "formal/Conde1963/SsrNovember.lean")
        self.assertEqual([x["occurrence_id"] for x in out["linked_sources"]],
                         ["C241-L19#1", "C241-L18:19640002493"])

    def test_ledger_94_8_rejected_even_if_legacy_already_had_it(self):
        bad = copy.deepcopy(self.b)
        doc = next(x for x in bad["sources"] if x["ntrs_id"] == "19640002493")
        next(x for x in doc["rows"] if x["designator"] == "1963-003A")["period_min"] = "94.8"
        with self.assertRaisesRegex(ValueError, "ledger/handoff mismatch"):
            build(self.a, bad, self.g, self.house)

    def test_ledger_document_hash_must_match_custody(self):
        bad = copy.deepcopy(self.b)
        next(x for x in bad["sources"] if x["ntrs_id"] == "19640002493")["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "custody, digest"):
            build(self.a, bad, self.g, self.house)

    def test_nov15_independent_source_is_exactly_locked(self):
        bad = copy.deepcopy(self.a)
        bad["documents"][0]["rows"][0]["period_min"] = "94.8"
        with self.assertRaisesRegex(ValueError, "ledger/handoff mismatch"):
            build(bad, self.b, self.g, self.house)

    def test_cannot_double_count_nov30_edition(self):
        bad = copy.deepcopy(self.b)
        entry = next(x for x in bad["sources"] if x["ntrs_id"] == "19640002493")
        bad["sources"].append(copy.deepcopy(entry))
        with self.assertRaisesRegex(ValueError, "duplicate November 30"):
            build(self.a, bad, self.g, self.house)

    def test_publication_as_of_is_not_tracking_epoch(self):
        bad = copy.deepcopy(self.b)
        next(x for x in bad["sources"] if x["ntrs_id"] == "19640002493")["as_of_utc"] = "1963-11-08T12:00:00Z"
        with self.assertRaisesRegex(ValueError, "published-as-of"):
            build(self.a, bad, self.g, self.house)

    def test_legacy_observation_no_longer_can_be_any_value(self):
        bad = copy.deepcopy(self.g)
        next(x for x in bad["observations"]
             if x["id"] == "SSR-1963-11-30-NORAD527-nodal_period")["value"] = 94.7
        with self.assertRaisesRegex(ValueError, "invalid arithmetic|NASA facsimile source-value mismatch"):
            build(self.a, self.b, bad, self.house)

    def test_congressional_source_connects_without_sensor_claim(self):
        out = build(self.a, self.b, self.g, self.house)["institutional_provenance"]
        self.assertEqual(out["occurrence_id"], "C241-L20#1")
        self.assertEqual(len(out["institutional_links"]), 4)
        self.assertIsNone(out["per_object_input_lineage"])
        self.assertFalse(out["physical_constraint_activated"])

    def test_1965_report_date_is_not_1963_observation_epoch(self):
        bad = copy.deepcopy(self.house)
        bad["observation_epoch_utc"] = "1963-11-08T12:00:00Z"
        with self.assertRaisesRegex(ValueError, "promoted into sensor"):
            build(self.a, self.b, self.g, bad)

    def test_1961_agreement_not_misdated_as_report(self):
        bad = copy.deepcopy(self.house)
        bad["report_published_on"] = bad["historical_agreement_on"]
        with self.assertRaisesRegex(ValueError, "custody or date"):
            build(self.a, self.b, self.g, bad)

    def test_optional_navspasur_channel_not_erased(self):
        bad = copy.deepcopy(self.house)
        bad["transcribed_links"].pop(2)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            build(self.a, self.b, self.g, bad)

    def test_norad_catalog_not_labeled_exclusive_sensor(self):
        bad = copy.deepcopy(self.house)
        bad["per_object_527_528_529_input_lineage_verified"] = True
        with self.assertRaisesRegex(ValueError, "promoted into sensor"):
            build(self.a, self.b, self.g, bad)

    def test_site_artifact_is_deterministic_source_consumer(self):
        self.assertEqual(OUT.read_text(encoding="utf-8"), render())
        self.assertLess(OUT.stat().st_size, 20000)


if __name__ == "__main__":
    unittest.main()
