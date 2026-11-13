"""C241-L23: reject invented disappearance, sensor data and provenance changes."""
import copy
import json
import unittest
from pathlib import Path
from tools.tle_nasa_ssr_apr10_audit import ROOT, LEDGER, GRAPH, APRIL, validate, audit

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

LEDGER_DATA = read(LEDGER)
GRAPH_DATA = read(GRAPH)
APRIL_DATA = read(APRIL)

class AprilListingGap(unittest.TestCase):
    def test_bridge_is_documentary_only(self):
        result = validate(LEDGER_DATA, GRAPH_DATA, APRIL_DATA)
        self.assertEqual(result["edition_8_not_listed"], ["1963 3A", "1963 3B", "1963 3C"])
        self.assertEqual(result["independent_instrument_measurements_added"], 0)
        self.assertEqual(result["physical_constraints_activated"], 0)

    def test_mutations_refused(self):
        modifications = [
            (0, lambda x: x["source"].update(ntrs_id="19630012128")),
            (0, lambda x: x["source"].update(sha256="0" * 64)),
            (0, lambda x: x["source"].update(bytes=0)),
            (0, lambda x: x["source"].update(pdf_pages=15)),
            (0, lambda x: x["source"].update(issue=9)),
            (0, lambda x: x["source"].update(compilation_as_of_utc="1963-04-10T00:00:00Z")),
            (0, lambda x: x["source"].update(in_orbit_pdf_pages_one_based=[7])),
            (0, lambda x: x["negative_listing"]["missing_designators"].pop()),
            (0, lambda x: x["negative_listing"].update(interpretation="SATELLITES_ABSENT_FROM_ORBIT")),
            (0, lambda x: x["negative_listing"].update(present_controls=[])),
            (0, lambda x: x["negative_listing"].update(basis="OCR_ONLY")),
            (0, lambda x: x["subsequent_listing"].update(elapsed_publication_days=10)),
            (0, lambda x: x["subsequent_listing"].update(pdf_page_one_based=13)),
            (0, lambda x: x["limits"].update(physical_absence_inferred=True)),
            (0, lambda x: x["limits"].update(listing_is_tracking_event=True)),
            (0, lambda x: x["limits"].update(reference_frame="TEME")),
            (0, lambda x: x["limits"].update(instrument_uncertainty=0.001)),
            (0, lambda x: x["limits"].update(terminal_location="Conde")),
            (0, lambda x: x["limits"].update(independent_instrument_measurements_added=3)),
            (1, lambda x: x["records"][1].update(april_10_listed=True)),
            (1, lambda x: x["records"][1].update(measurement_epoch_utc="1963-04-10T14:30Z")),
            (1, lambda x: x["records"].pop()),
            (1, lambda x: x["dependency_edges"].pop()),
            (1, lambda x: x.update(physical_domain_reduced=True)),
            (2, lambda x: x["april"].update(ntrs="19630012127")),
            (2, lambda x: x["april_rows"][1].update(nodal_period_min="93.6")),
        ]
        for i, (target, mutation) in enumerate(modifications):
            with self.subTest(i=i):
                items = [copy.deepcopy(y) for y in (LEDGER_DATA, GRAPH_DATA, APRIL_DATA)]
                mutation(items[target])
                with self.assertRaises((ValueError, KeyError)):
                    validate(*items)

    def test_non_pdf(self):
        with self.assertRaisesRegex(ValueError, "not PDF"):
            audit(LEDGER_DATA, GRAPH_DATA, APRIL_DATA, b"not pdf")

    def test_fake_pdf(self):
        with self.assertRaisesRegex(ValueError, "source bytes changed"):
            audit(LEDGER_DATA, GRAPH_DATA, APRIL_DATA, b"%PDF-1.4 fake")

if __name__ == "__main__":
    unittest.main()
