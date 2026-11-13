"""C241-L18: reject damaged documentary chain or premature physical claim."""
import copy
import json
import unittest
from pathlib import Path
from tools.tle_nasa_ssr_jul_dec_audit import validate, audit

LEDGER = json.loads((Path(__file__).resolve().parents[1] /
    "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json").read_text())


class LateNASAReports(unittest.TestCase):
    def mutate(self, change):
        obj = copy.deepcopy(LEDGER)
        change(obj)
        with self.assertRaises((ValueError, AssertionError, KeyError, TypeError)):
            validate(obj)

    def test_survivor_series_and_no_physical_claim(self):
        report = validate(LEDGER)
        self.assertEqual(report["distinct_source_editions"], 3)
        self.assertEqual(report["survivor_529_nov_dec_current_facsimile_readings"], ["92.2", "89.2"])
        self.assertEqual(report["survivor_527_nov_dec_periods"], ["94.6", "94.6"])
        self.assertEqual(report["529_nov_dec_delta_range_min_after_89_2_reconciliation_tenth_rounding"],
                         ["2.90", "3.10"])
        self.assertFalse(report["physical_domain_reduced"])
        self.assertEqual(report["independent_instrument_measurements_found"], 0)

    def test_reject_old_july_3c_perigee_transcription(self):
        self.mutate(lambda x: x["sources"][0]["rows"][2].update(perigee_km=425))

    def test_erratum_chain_preserved(self):
        self.assertEqual(LEDGER["sources"][0]["perigee_transcription_erratum"]["prior_ledger_value_km"], 425)
        self.assertEqual(LEDGER["sources"][0]["rows"][2]["perigee_km"], 452)
        self.mutate(lambda x: x["sources"][0].pop("perigee_transcription_erratum"))

    def test_date_forgery(self):
        self.mutate(lambda x: x["sources"][0].update(published="1963-08-01"))

    def test_asof_is_not_instrument_time(self):
        self.mutate(lambda x: x["data_lineage"].update(
            source_report_reference_time_is_instrument_epoch=True))

    def test_rename_object(self):
        self.mutate(lambda x: x["sources"][0]["rows"][1].update(designator="1963-003A"))

    def test_period_mutation(self):
        self.mutate(lambda x: x["sources"][1]["rows"][1].update(period_min="93.2"))

    def test_artifact_hash_mutation(self):
        self.mutate(lambda x: x["sources"][2].update(sha256="0" * 64))

    def test_incorrect_pdf_page(self):
        self.mutate(lambda x: x["sources"][0].update(pdf_page_index=5))

    def test_duplicate_rows(self):
        self.mutate(lambda x: x["sources"][0]["rows"].append(
            dict(x["sources"][0]["rows"][0])))

    def test_invent_sensor(self):
        self.mutate(lambda x: x["data_lineage"].update(instrument_station="Diyarbakir"))

    def test_invent_precision(self):
        self.mutate(lambda x: x["data_lineage"].update(measurement_uncertainty_sigma=0.001))

    def test_elevate_catalogue_to_independent_measurements(self):
        self.mutate(lambda x: x["data_lineage"].update(independent_sensor_samples=3))

    def test_remove_old_disputed_reading(self):
        self.mutate(lambda x: x["sources"][2].pop("transcription_conflict"))

    def test_c227_transcription_erratum_cannot_be_rolled_back(self):
        self.assertEqual(LEDGER["sources"][2]["transcription_conflict"]["status"],
                         "RESOLVED_AS_TRANSCRIPTION_ERRATUM_NOT_INSTRUMENT_VALIDATION")
        self.mutate(lambda x: x["sources"][2]["transcription_conflict"].update(
            status="OPEN_REQUIRES_INDEPENDENT_REVIEW"))

    def test_reject_forged_visual_review_page(self):
        self.mutate(lambda x: x["sources"][2]["transcription_conflict"]["independent_review"].update(
            pdf_page_index=5))

    def test_reject_missing_prior_c227_value(self):
        self.mutate(lambda x: x["sources"][2]["transcription_conflict"]["independent_review"].update(
            superseded_c227_period_min=None))

    def test_activate_disputed_value(self):
        self.mutate(lambda x: x["sources"][2]["transcription_conflict"].update(
            eligible_for_calibrated_physical_fit=True))

    def test_assume_robust_uncertainty_reduction(self):
        self.mutate(lambda x: x["use_as_constraint"].update(
            quantified_uncertainty_reduction="CONFIRMED"))

    def test_wrong_lean_contract(self):
        self.mutate(lambda x: x["use_as_constraint"].update(bridge="C241-P9"))

    def test_invent_orbit_phase(self):
        self.mutate(lambda x: x["data_lineage"].update(relative_orbital_phase=0))

    def test_reject_nonpdf(self):
        with self.assertRaisesRegex(ValueError, "not PDF"):
            audit(LEDGER, {key: b"not a PDF" for key in
                ("19630012290", "19640002493", "19640005618")})

    def test_reject_wrong_hash(self):
        with self.assertRaisesRegex(ValueError, "source bytes changed"):
            audit(LEDGER, {key: b"%PDF-1.4\nWRONG\n" for key in
                ("19630012290", "19640002493", "19640005618")})


if __name__ == "__main__":
    unittest.main()
