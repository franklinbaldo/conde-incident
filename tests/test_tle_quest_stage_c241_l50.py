"""Adversarial tests for Quest 1995 and NORAD 528 epistemic boundary."""
import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import tle_quest_stage_c241_l50 as a


class TestQuestStage(unittest.TestCase):
    def setUp(self):
        self.data = a.load()

    def invalid(self, edit):
        d = copy.deepcopy(self.data)
        edit(d)
        with self.assertRaises(ValueError):
            a.audit(d)

    def test_valid(self):
        self.assertTrue(a.audit(self.data))

    def test_source_hash_mutation(self):
        self.invalid(lambda d: d["source"].update(sha256="0" * 64))

    def test_source_size_mutation(self):
        self.invalid(lambda d: d["source"].update(bytes=14469994))

    def test_page_mutation(self):
        self.invalid(lambda d: d["source"].update(printed_page=41))

    def test_pdf_page_index_mutation(self):
        self.invalid(lambda d: d["source"].update(pdf_page_index_zero_based=0))

    def test_unearned_visual_claim(self):
        self.invalid(lambda d: d["source"].update(inspection="OCR verified"))

    def test_conflict_erased(self):
        self.invalid(lambda d: d["rows"][1].update(stage="Thor Agena B"))

    def test_control_2314_erased(self):
        self.invalid(lambda d: d["rows"][2].update(stage="TAT Agena D"))

    def test_control_2312_swapped(self):
        self.invalid(lambda d: d["rows"][0].update(vehicle="2313"))

    def test_orbit_fabricated_precision(self):
        self.invalid(lambda d: d["rows"][1].update(period_as_printed="94.70 +/- 0.01"))

    def test_no_instrument_promotion(self):
        self.invalid(lambda d: d.update(status="INSTRUMENTAL_OBSERVATION"))

    def test_no_physical_activation(self):
        self.invalid(lambda d: d.update(physical_constraint_active=True))

    def test_no_528_identity_from_group(self):
        self.invalid(lambda d: d["norad528"].update(object_hardware="Agena D"))

    def test_no_528_epoch(self):
        self.invalid(lambda d: d["norad528"].update(observation_utc="1963-11-08T00:00:00Z"))

    def test_no_528_sigma(self):
        self.invalid(lambda d: d["norad528"].update(sigma=0.01))

    def test_no_528_place(self):
        self.invalid(lambda d: d["norad528"].update(impact_location="Conde"))

    def test_no_independent_sensor_claim(self):
        self.invalid(lambda d: d["comparison"].update(source_independence="independent radar observation"))

    def test_no_known_nsa_facs_claim(self):
        self.invalid(lambda d: d["comparison"].update(nsa_1975="D facsimile visually verified"))

    def test_extra_field(self):
        self.invalid(lambda d: d.update(impact_confirmed=True))

    def test_duplicate_json_key(self):
        with self.assertRaises(ValueError):
            json.loads('{"a":1, "a":2}', object_pairs_hook=a.unique_keys)

    def test_malformed_pdf(self):
        with self.assertRaises(ValueError):
            a.verify_pdf(self.data, b"%PDF-fake%%EOF")


if __name__ == "__main__":
    unittest.main()
