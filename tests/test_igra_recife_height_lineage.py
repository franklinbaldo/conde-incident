"""Verify that NOAA IGRA heights are not promoted into independent instrument calibration."""
import copy
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1] / "research" / "meteorology"

def validate(card):
    src = card["historical_source"]
    assert src["station_id"] == "BRM00082900"
    assert src["upstream"] == "ncdc6301"
    assert src["independent_archival_families"] == 1
    assert len(src["archive_sha256"]) == 64
    assert card["modern_document"]["printed_pages"] == [12, 20]
    place = card["place"]
    assert place["location_1963_verified"] is False
    assert place["location_uncertainty_1963_m"] is None
    assert place["measured_at_conde"] is False
    height = card["height_origin"]
    assert height["verified_for_1963_recife"] is False
    assert height["source_specific_procedure"] is None
    assert height["pressure_temperature_height_independent"] is False
    assert height["noaa_igra_created_estimates"] is False
    assert height["common_report_precisions_m"] == [1, 10]
    assert height["report_precision_is_accuracy"] is False
    assert height["instrumental_sigma_m"] is None
    result = card["inference"]
    for f in ["model_residual_is_independent_instrument_calibration",
              "hypsometric_residual_is_instrument_error",
              "terminal_time_or_position_inferred", "physical_constraint_activated"]:
        assert result[f] is False
    for f in ["residual_sigma_m", "recife_conde_transfer_sigma_m"]:
        assert result[f] is None
    assert len(card["epochs"]) == 3
    assert sum(e["layers"] for e in card["epochs"]) == 78
    for epoch in card["epochs"]:
        original = json.loads((BASE / epoch["prior_json"]).read_text())
        assert epoch["release_time_utc"] is None
        assert epoch["nominal_utc"] == original["epoch"]["nominal_utc_date"] + "T12:00:00Z"
        assert original["epoch"]["actual_release_utc"] is None
        assert original["epoch"]["missing_time_code"] == 9999
        assert original["source"]["station_id"] == src["station_id"]
        assert original["source"]["upstream"] == src["upstream"]
        assert original["source"]["archive_sha256"] == src["archive_sha256"]
        assert epoch["levels"] == original["source_levels"]
        assert epoch["layers"] == original["adjacent_layers"]
        assert original["interpretation"]["residual_is_measurement_error"] is False

class HeightLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card = json.loads((BASE / "igra_recife_height_lineage_1963.json").read_text())

    def test_source_and_seventy_eight_layers(self):
        validate(self.card)

    def test_no_report_precision_promoted_to_sigma(self):
        for field, value in [("report_precision_is_accuracy", True),
                             ("instrumental_sigma_m", 1),
                             ("verified_for_1963_recife", True),
                             ("pressure_temperature_height_independent", True)]:
            other = copy.deepcopy(self.card)
            other["height_origin"][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(other)

    def test_no_conditional_residual_promoted_to_constraint(self):
        for field, value in [("model_residual_is_independent_instrument_calibration", True),
                             ("hypsometric_residual_is_instrument_error", True),
                             ("residual_sigma_m", 10),
                             ("recife_conde_transfer_sigma_m", 2000),
                             ("physical_constraint_activated", True)]:
            other = copy.deepcopy(self.card)
            other["inference"][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(other)

    def test_bad_date_or_archival_independence_rejected(self):
        other = copy.deepcopy(self.card)
        other["epochs"][1]["nominal_utc"] = "1963-11-08T23:59:00Z"
        with self.assertRaises(AssertionError):
            validate(other)
        other = copy.deepcopy(self.card)
        other["historical_source"]["independent_archival_families"] = 3
        with self.assertRaises(AssertionError):
            validate(other)

if __name__ == "__main__":
    unittest.main()
