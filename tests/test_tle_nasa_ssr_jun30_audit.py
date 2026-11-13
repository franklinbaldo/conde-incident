"""Scientific and adversarial tests of original NASA June 30 1963 compilation."""
import copy
import json
import unittest
from pathlib import Path
from tools.tle_nasa_ssr_jun30_audit import validate, audit

ROOT = Path(__file__).resolve().parents[1]
read = lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))
LEDGER = read("research/tle_custody/nasa_ssr_jun30_1963_C241-L22.json")
GRAPH = read("research/constraints/ssr_jun30_1963_observables_C241-L22.json")
APRIL = read("research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json")
JULY = read("research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json")
AUGUST = read("research/tle_custody/nasa_ssr_aug15_1963_C241-L17.json")


class JuneCustody(unittest.TestCase):
    def invalid(self, index, mutation):
        items = [copy.deepcopy(x) for x in (LEDGER, GRAPH, APRIL, JULY, AUGUST)]
        mutation(items[index])
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate(*items)

    def test_four_editions_period_528_and_no_physics(self):
        r = validate(LEDGER, GRAPH, APRIL, JULY, AUGUST)
        self.assertEqual(r["documentary_period_528_min"], ["94.1", "93.7", "93.6", "93.3"])
        self.assertEqual(r["publication_deltas_min_NOT_physical_rates"], ["-0.4", "-0.1", "-0.3"])
        self.assertEqual(r["documentary_scalar_fields_connected"], 12)
        self.assertIsNone(r["individual_observation_epochs_utc"])
        self.assertEqual(r["physical_constraints_activated"], 0)

    def test_all_three_objects_present(self):
        self.assertEqual([r["norad_crosswalk"] for r in LEDGER["rows"]], [527, 528, 529])
        self.assertEqual(len(GRAPH["observables"]), 12)

    def test_wrong_ntrs(self):
        self.invalid(0, lambda x: x["source"].update(ntrs_id="19630012131"))

    def test_wrong_pdf_page(self):
        self.invalid(0, lambda x: x["source"].update(pdf_page_index_zero_based=6))

    def test_wrong_nasa_report(self):
        self.invalid(0, lambda x: x["source"].update(nasa_tm="NASA-TM-X-50364"))

    def test_wrong_pdf_sha(self):
        self.invalid(0, lambda x: x["source"].update(sha256="0" * 64))

    def test_wrong_pdf_bytes(self):
        self.invalid(0, lambda x: x["source"].update(bytes=0))

    def test_wrong_period_528(self):
        self.invalid(0, lambda x: x["rows"][1].update(period_min="94.7"))

    def test_wrong_perigee_529(self):
        self.invalid(0, lambda x: x["rows"][2].update(perigee_km=472))

    def test_wrong_527_inclination(self):
        self.invalid(0, lambda x: x["rows"][0].update(inclination_deg="81.88"))

    def test_swaps_object_id(self):
        self.invalid(0, lambda x: x["rows"][1].update(norad_crosswalk=529))

    def test_drops_row(self):
        self.invalid(0, lambda x: x["rows"].pop())

    def test_invents_station(self):
        self.invalid(0, lambda x: x["limits"].update(tracking_station="SAO"))

    def test_invents_epoch(self):
        self.invalid(0, lambda x: x["limits"].update(instrumental_epoch_utc="1963-06-30T12:00:00Z"))

    def test_invents_sigma(self):
        self.invalid(0, lambda x: x["limits"].update(measurement_sigma="0.01"))

    def test_invents_location(self):
        self.invalid(0, lambda x: x["limits"].update(terminal_location="Conde"))

    def test_activates_physical_domain(self):
        self.invalid(0, lambda x: x["limits"].update(physical_domain="CONSTRAINED"))

    def test_removes_dependency(self):
        self.invalid(0, lambda x: x["dependencies"].pop("july_31"))

    def test_invents_scalar_epoch(self):
        self.invalid(1, lambda x: x["observables"][4].update(latent_epoch_utc="1963-06-30T12:00:00Z"))

    def test_loses_unit(self):
        self.invalid(1, lambda x: x["observables"][7].update(unit="min"))

    def test_loses_operator(self):
        self.invalid(1, lambda x: x["observables"][2].update(operator="unknown"))

    def test_loses_bridge(self):
        self.invalid(1, lambda x: x["observables"][3].update(required_bridges=[]))

    def test_claims_independent_sensors(self):
        self.invalid(1, lambda x: x.update(independent_instrument_measurements_added=3))

    def test_claims_lean(self):
        self.invalid(1, lambda x: x.update(lean_promoted=True))

    def test_breaks_editorial_lineage(self):
        self.invalid(1, lambda x: x["dependency_edges"].pop())

    def test_april_source_replaced(self):
        self.invalid(2, lambda x: x["april"].update(ntrs="unknown"))

    def test_april_period_replaced(self):
        self.invalid(2, lambda x: x["april_rows"][1].update(nodal_period_min="93.7"))

    def test_july_529_errata_regression(self):
        self.invalid(3, lambda x: x["sources"][0]["rows"][2].update(perigee_km=425))

    def test_august_period_replaced(self):
        self.invalid(4, lambda x: x["rows"][1].update(nodal_period_min="94.1"))

    def test_rejects_unrelated_pdf(self):
        with self.assertRaisesRegex(ValueError, "source bytes changed"):
            audit(LEDGER, GRAPH, APRIL, JULY, AUGUST, b"%PDF-1.4\nFAKE")

    def test_rejects_non_pdf(self):
        with self.assertRaisesRegex(ValueError, "not PDF"):
            audit(LEDGER, GRAPH, APRIL, JULY, AUGUST, b"not pdf")


if __name__ == "__main__":
    unittest.main()
