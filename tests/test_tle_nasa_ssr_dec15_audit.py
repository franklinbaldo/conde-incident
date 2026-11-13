"""Documentary custody tests for NASA SSR volume 3 issue 24, Dec 15 1963."""
import copy
import json
import unittest
from pathlib import Path
from tools.tle_nasa_ssr_dec15_audit import validate, audit

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
LEDGER = read("research/tle_custody/nasa_ssr_dec15_1963_C241-L21.json")
GRAPH = read("research/constraints/ssr_dec15_1963_observables_C241-L21.json")
NOV15 = read("research/tle_custody/nasa_ssr_nov15_1963_C241-L19.json")
LATE = read("research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json")


class DecemberEdition(unittest.TestCase):
    def invalid(self, index, change):
        inputs = [copy.deepcopy(v) for v in (LEDGER, GRAPH, NOV15, LATE)]
        change(inputs[index])
        with self.assertRaises((ValueError, KeyError, TypeError, StopIteration)):
            validate(*inputs)

    def test_two_survivors_and_four_edition_series(self):
        output = validate(LEDGER, GRAPH, NOV15, LATE)
        self.assertEqual([x["object_norad"] for x in output], [527, 529])
        self.assertEqual(output[0]["printed_nodal_period_min"],
                         ["94.6", "94.6", "94.6", "94.6"])
        self.assertEqual(output[1]["printed_nodal_period_min"],
                         ["92.6", "92.2", "91.6", "89.2"])
        self.assertEqual(output[1]["published_deltas_min_NOT_physical_rates"],
                         ["-0.4", "-0.6", "-2.4"])
        self.assertIsNone(output[1]["individual_observation_epochs_utc"])

    def test_no_fictional_observation_or_decay_inference(self):
        self.assertEqual(LEDGER["not_listed_in_objects_in_orbit"],
                         ["1963-003B"])
        self.assertEqual(GRAPH["independent_instrument_measurements_added"], 0)
        self.assertFalse(GRAPH["lean_promoted"])

    def test_wrong_ntrs(self):
        self.invalid(0, lambda x: x["source"].update(ntrs_id="19640003478"))

    def test_wrong_publication(self):
        self.invalid(0, lambda x: x["source"].update(publication_date="1963-12-14"))

    def test_wrong_issue_number(self):
        self.invalid(0, lambda x: x["source"].update(issue=21))

    def test_wrong_page(self):
        self.invalid(0, lambda x: x["source"].update(pdf_page_index_zero_based=5))

    def test_wrong_sha(self):
        self.invalid(0, lambda x: x["source"].update(sha256="0" * 64))

    def test_wrong_bytes(self):
        self.invalid(0, lambda x: x["source"].update(bytes=958926))

    def test_wrong_3c_period(self):
        self.invalid(0, lambda x: x["rows"][1].update(period_min="92.6"))

    def test_wrong_3c_perigee(self):
        self.invalid(0, lambda x: x["rows"][1].update(perigee_km=374))

    def test_wrong_3a_inclination(self):
        self.invalid(0, lambda x: x["rows"][0].update(inclination_deg="81.89"))

    def test_duplicate_designator(self):
        self.invalid(0, lambda x: x["rows"].append(dict(x["rows"][0])))

    def test_claims_absence_proves_impact(self):
        self.invalid(0, lambda x: x.update(absence_meaning="CRASH_CONFIRMED"))

    def test_invents_528_sensor(self):
        self.invalid(0, lambda x: x["limits"].update(tracking_station="NORAD"))

    def test_invents_sigma(self):
        self.invalid(0, lambda x: x["limits"].update(measurement_sigma=0.01))

    def test_invents_epoch(self):
        self.invalid(0, lambda x: x["limits"].update(instrumental_epoch_utc="1963-12-15T12:00:00Z"))

    def test_invents_terminal_position(self):
        self.invalid(0, lambda x: x["limits"].update(terminal_location="Conde"))

    def test_promotes_fictional_lean_bound(self):
        self.invalid(0, lambda x: x["limits"].update(lean="PROVED"))

    def test_promotes_graph(self):
        self.invalid(1, lambda x: x.update(physical_domain_reduced=True))

    def test_sets_sensor_independence(self):
        self.invalid(1, lambda x: x.update(independent_instrument_measurements_added=2))

    def test_forgets_forward_model_bridge(self):
        self.invalid(1, lambda x: x["observables"][1].update(required_bridges=[]))

    def test_forgets_graph_operator(self):
        self.invalid(1, lambda x: x["observables"][1].update(operator="fitted_tle(529)"))

    def test_disconnected_document_series(self):
        self.invalid(1, lambda x: x["dependency_edges"].pop())

    def test_parent_graph_changed(self):
        self.invalid(1, lambda x: x.update(parent_graph="UNKNOWN"))

    def test_denies_november_observation(self):
        self.invalid(2, lambda x: x["documents"][0]["rows"][1].update(period_min="94.0"))

    def test_roll_back_dec31_errata(self):
        self.invalid(3, lambda x: next(y for y in x["sources"]
                        if y["ntrs_id"]=="19640005618")["rows"][1].update(period_min="89.6"))

    def test_wrong_nov30_edition(self):
        self.invalid(3, lambda x: next(y for y in x["sources"]
                        if y["ntrs_id"]=="19640002493").update(issue=24))

    def test_non_pdf(self):
        with self.assertRaisesRegex(ValueError, "not PDF"):
            audit(LEDGER, GRAPH, NOV15, LATE, b"wrong")

    def test_wrong_pdf_bytes(self):
        with self.assertRaisesRegex(ValueError, "source bytes changed"):
            audit(LEDGER, GRAPH, NOV15, LATE, b"%PDF-1.4\nFORGED\n")


if __name__ == "__main__":
    unittest.main()
