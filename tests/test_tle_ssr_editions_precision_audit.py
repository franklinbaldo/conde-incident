"""C241-L27 adversarial controls: printed SSR digits are not radar accuracies."""
import copy
import unittest

from tools.tle_ssr_editions_precision_audit import validate, read, MODEL, DECAY

MODEL_DATA = read(MODEL)
LEDGERS = {d["ledger"]: read(d["ledger"]) for d in MODEL_DATA["docs"]}
DECAY_DATA = read(DECAY)


class NineEditions(unittest.TestCase):
    def reject(self, mutator):
        model, ledgers, decay = copy.deepcopy(
            (MODEL_DATA, LEDGERS, DECAY_DATA)
        )
        mutator(model, ledgers, decay)
        with self.assertRaises((ValueError, KeyError, StopIteration, TypeError)):
            validate(model, ledgers, decay)

    def test_nine_editions_twenty_three_rows(self):
        out = validate(MODEL_DATA, LEDGERS, DECAY_DATA)
        self.assertEqual(out["distinct_compiled_NASA_editions"], 9)
        self.assertEqual(out["linked_compiled_rows"], 23)
        self.assertEqual(out["rows_per_object_NORAD_secondary_crosswalk"],
                         {527: 9, 528: 5, 529: 9})
        self.assertTrue(out["precision_is_not_sensor_sigma"])
        self.assertEqual(out["physical_constraints_active"], 0)
        self.assertTrue(all(x["instrument_observation_epoch"] is None
                            and x["instrument_sigma"] is None
                            for x in out["rows"]))

    def test_loses_an_edition(self):
        self.reject(lambda m, l, d: m["docs"].pop())

    def test_duplicate_edition(self):
        self.reject(lambda m, l, d: m["docs"].append(
            copy.deepcopy(m["docs"][0])))

    def test_swaps_publication_day(self):
        self.reject(lambda m, l, d: m["docs"][3].update(
            published="1963-08-16"))

    def test_mistaken_original_pdf_digest(self):
        self.reject(lambda m, l, d: m["docs"][2].update(
            pdf_sha256="0" * 64))

    def test_wrong_as_of_page(self):
        self.reject(lambda m, l, d: m["docs"][1].update(
            pdf_page_index=6))

    def test_regress_july_452_to_425(self):
        self.reject(lambda m, l, d: l[
            "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
        ]["sources"][0]["rows"][2].update(perigee_km=425))

    def test_regress_december_89_2_to_89_6(self):
        self.reject(lambda m, l, d: l[
            "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
        ]["sources"][2]["rows"][1].update(period_min="89.6"))

    def test_invent_sixth_528_line(self):
        self.reject(lambda m, l, d: m["docs"][5]["objects"].append(528))

    def test_lose_528_october_line(self):
        self.reject(lambda m, l, d: l[
            "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"
        ]["catalog_rows"].pop(1))

    def test_drift_from_primary_decay_day(self):
        self.reject(lambda m, l, d: d["sources"][0][
            "human_table_observation"].update(decay_day="1963-11-09"))

    def test_quantization_called_sigma(self):
        self.reject(lambda m, l, d: m.update(
            nominal_half_steps_are_sensor_sigma=True))

    def test_printed_epoch_called_sensor_epoch(self):
        self.reject(lambda m, l, d: m.update(
            printed_as_of_is_tracking_epoch=True))

    def test_rounding_rule_claimed_historically_verified(self):
        self.reject(lambda m, l, d: m.update(
            report_rounding_rule_verified=True))

    def test_completes_missing_sensor_with_number(self):
        self.reject(lambda m, l, d: m.update(
            raw_instrument_528_sigma=0.005))

    def test_completes_missing_sensor_with_invented_station(self):
        self.reject(lambda m, l, d: m.update(
            raw_instrument_528_sensor="Shemya"))

    def test_treat_sources_as_nine_independent_radars(self):
        self.reject(lambda m, l, d: m.update(
            independent_source_family_count=9))

    def test_activates_lean_physics(self):
        self.reject(lambda m, l, d: m["graph"].update(
            lean_promoted=True))

    def test_wrong_source_period_precision(self):
        self.reject(lambda m, l, d: l[
            "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"
        ]["catalog_rows"][1].update(nodal_period_min_printed="92.40"))


if __name__ == "__main__":
    unittest.main()
