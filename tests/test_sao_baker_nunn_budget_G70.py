"""Source-locked G70 confidence budget and adversarial no-calibration gate."""
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from sao_baker_nunn_budget_G70 import (  # noqa: E402
    LEDGER, check_ledger, check_pdf, conditional_clock_displacement_arcsec,
)


class BakerNunn1973Budget(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_authentic_report_metadata_and_five_rate_bins(self):
        d = check_ledger(self.doc)
        self.assertEqual(d["table_1"]["rows"][-1]["vhf_along"], 3.7)
        self.assertEqual(d["source"]["printed_page_numbers"], [25, 26])

    def test_historical_holdout_remains_unrun(self):
        d = check_ledger(self.doc)
        self.assertEqual(d["activation"]["state"], "CANDIDATE_NOT_ACTIVATED")
        self.assertIsNone(d["activation"]["observational_covariance_for_g64"])
        self.assertEqual(d["activation"]["independent_1963_holdout"], "NOT_RUN")

    def test_table_reordering_transcription_and_units_fail(self):
        for mut in (
            lambda d: d["table_1"]["rows"].reverse(),
            lambda d: d["table_1"]["rows"][2].__setitem__("vhf_along", 2.2),
            lambda d: d["table_1"]["rows"][4].__setitem__("rate_max", 4000),
            lambda d: d["table_1"].__setitem__("units_rate", "deg/s"),
            lambda d: d["table_1"].__setitem__("units_error", "radians"),
        ):
            with self.subTest(mutation=repr(mut)):
                d = copy.deepcopy(self.doc)
                mut(d)
                with self.assertRaises(ValueError):
                    check_ledger(d)

    def test_source_year_genealogy_sha_and_page_identity_fail_closed(self):
        for field, value in (
            ("publication_date", "1963-11-08"),
            ("nasa_ntrs_id", "19630000000"),
            ("pdf_sha256", "0" * 64),
            ("evidence_class", "1963_SENSOR_RECORD"),
            ("pdf_page_numbers_one_based", [25, 26]),
        ):
            with self.subTest(field=field):
                d = copy.deepcopy(self.doc)
                d["source"][field] = value
                with self.assertRaises(ValueError):
                    check_ledger(d)

    def test_retro_clock_not_satellite_specific_sigma(self):
        for field, value in (
            ("observation_epoch_rms_s_approx", 1.0),
            ("historical_scope", "NORAD_528_1963"),
            ("clock_and_sync", "EECo VLF all 1963"),
        ):
            with self.subTest(field=field):
                d = copy.deepcopy(self.doc)
                d["clock"][field] = value
                with self.assertRaises(ValueError):
                    check_ledger(d)

    def test_any_activation_attempt_is_rejected(self):
        for field, value in (
            ("state", "CALIBRATED"),
            ("instrumental_utc_epochs", ["1963-11-07T00:00:00Z"]),
            ("observational_covariance_for_g64", [[1e-6, 0], [0, 1e-6]]),
            ("historical_likelihood", 1.0),
            ("historical_orbital_domain_reduction", True),
            ("independent_1963_holdout", "PASS"),
            ("impact_location_or_probability", {"Conde": 0.8}),
        ):
            with self.subTest(field=field):
                d = copy.deepcopy(self.doc)
                d["activation"][field] = value
                with self.assertRaises(ValueError):
                    check_ledger(d)

    def test_clock_sensitivity_is_conditional(self):
        a = conditional_clock_displacement_arcsec(250, .001)
        b = conditional_clock_displacement_arcsec(2000, .001)
        self.assertEqual(a["conditional_clock_component_arcsec"], .25)
        self.assertEqual(b["conditional_clock_component_arcsec"], 2.)
        self.assertIsNone(a["historical_528_sigma_arcsec"])

    def test_clock_sensitivity_rejects_invalid_numbers(self):
        for rate, error in (
            (-1, .001), (1, -1), (True, .001), (math.nan, 1),
            (1, math.inf), ("250", .001), (1e308, 1e308)
        ):
            with self.subTest(rate=rate, error=error), self.assertRaises(ValueError):
                conditional_clock_displacement_arcsec(rate, error)

    def test_pdf_wrong_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "fake.pdf"
            p.write_bytes(b"%PDF-1.7\nnot the original")
            with self.assertRaisesRegex(ValueError, "source bytes mismatch"):
                check_pdf(p)


if __name__ == "__main__":
    unittest.main()
