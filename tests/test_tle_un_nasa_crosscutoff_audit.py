"""C241-L36: adversarial verification of UN versus NASA printed values."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.tle_un_nasa_crosscutoff_audit import (
    ROOT, MODEL, UN, NASA, IDENTITY, check_original_pdfs, validate,
)

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))

FROZEN = [load(p) for p in (MODEL, UN, NASA, IDENTITY)]

class USPrintDifferences(unittest.TestCase):
    def corrupt(self, i, edit):
        data = copy.deepcopy(FROZEN)
        edit(data[i])
        with self.assertRaises((ValueError, TypeError, KeyError, StopIteration)):
            validate(*data)

    def test_twelve_typed_documentary_connections(self):
        out = validate(*FROZEN)
        self.assertEqual(out["new_documentary_links"], 12)
        self.assertEqual(out["added_instrumental_observations"], 0)
        self.assertEqual(out["active_physical_constraints"], 0)
        self.assertIsNone(out["inferred_rates"])
        self.assertEqual(out["nominal_print_deltas"][1]["published_print_differences"],
                         {"nodal_period_min": "-0.4", "inclination_deg": "-0.10",
                          "apogee_km": "-0.5", "perigee_km": "-41.4"})

    def test_missing_529(self):
        self.corrupt(0, lambda x: x["objects"].pop())

    def test_swap_identity(self):
        self.corrupt(0, lambda x: x["objects"][1].update(norad=529))

    def test_un_528_perigee_mutation(self):
        self.corrupt(1, lambda x: x["docs"][0]["printed_rows"][1].update(
            perigee_km_printed="476.5"))

    def test_nasa_528_period_mutation(self):
        self.corrupt(2, lambda x: x["april_rows"][1].update(nodal_period_min="94.2"))

    def test_different_delta_is_rejected(self):
        self.corrupt(0, lambda x: x["objects"][1]["nominal_deltas"].update(
            perigee_km="-41.3"))

    def test_swapped_nasa_designator(self):
        self.corrupt(2, lambda x: x["april_rows"][1].update(designator="1963-003C"))

    def test_fake_secondary_identity(self):
        self.corrupt(3, lambda x: x["row"].update(catalog_number_printed=527))

    def test_forged_un_sha(self):
        self.corrupt(0, lambda x: x["source_earlier"].update(sha256="0" * 64))

    def test_forged_nasa_pdf_page(self):
        self.corrupt(0, lambda x: x["source_later"].update(
            pdf_page_index_zero_based=7))

    def test_confuse_dates_with_sensor_epoch(self):
        self.corrupt(0, lambda x: x["unknowns"].update(
            observation_epochs_for_each_printed_cell_utc="1963-04-30T14:30:00Z"))

    def test_invent_covariance(self):
        self.corrupt(0, lambda x: x["unknowns"].update(
            measurement_covariance=[0.01]))

    def test_claim_independent_sensors(self):
        self.corrupt(0, lambda x: x["independence"].update(
            new_independent_tracking_sensor_evidences=2))

    def test_nominal_difference_as_physical_derivative(self):
        self.corrupt(0, lambda x: x["independence"].update(
            nominal_change_is_derivative=True))

    def test_promote_lean(self):
        self.corrupt(0, lambda x: x["graph"].update(lean_promoted=True))

    def test_promote_simulation(self):
        self.corrupt(0, lambda x: x["graph"].update(
            simulation_parameters_changed=True))

    def test_no_accidental_second_instrument_family(self):
        self.corrupt(0, lambda x: x["independence"].update(
            un_to_nasa_publications_count_as_two_independent_observations=True))

    def test_bad_pdf_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for filename in ("inf030E.pdf", "19630012128.pdf"):
                (Path(d) / filename).write_bytes(b"%PDF-1.4\ninvented\n")
            with self.assertRaisesRegex(ValueError, "original PDF bytes changed"):
                check_original_pdfs(FROZEN[0], d)

if __name__ == "__main__":
    unittest.main()
