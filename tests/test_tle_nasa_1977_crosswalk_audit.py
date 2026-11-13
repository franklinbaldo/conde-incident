"""C241-L32 adversarial tests: source identity is not 1963 sensor data."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.tle_nasa_1977_crosswalk_audit import validate, verify_pdf, LEDGER_PATH

LEDGER = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


class NASA1977Crosswalk(unittest.TestCase):
    def reject(self, mutate):
        d = copy.deepcopy(LEDGER)
        mutate(d)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            validate(d)

    def test_valid_only_candidate_until_visual(self):
        x = validate(LEDGER)
        self.assertEqual(x["catalog_pair"], ["1963 003B", 528])
        self.assertEqual(x["source_kind"],
                         "ORIGINAL_NASA_1977_PUBLICATION_RETROSPECTIVE_CATALOG_NOT_1963_SENSOR")
        self.assertEqual(x["independent_instrumental_observations"], 0)
        self.assertEqual(x["physical_constraints_activated"], 0)

    def test_incorrect_ntrs(self):
        self.reject(lambda x: x["source"].update(ntrs_id="19780009189"))

    def test_incorrect_pdf_sha(self):
        self.reject(lambda x: x["source"].update(pdf_sha256="0" * 64))

    def test_incorrect_pdf_length(self):
        self.reject(lambda x: x["source"].update(pdf_bytes=114))

    def test_incorrect_pub_date(self):
        self.reject(lambda x: x["source"].update(date_published="1963-11-08"))

    def test_relabel_instrument_as_primary(self):
        self.reject(lambda x: x["source"].update(
            document_kind="DIRECT_ORIGINAL_NORAD_SENSOR_OBSERVATION"))

    def test_accidental_527_identity(self):
        self.reject(lambda x: x["row"].update(catalog_number_printed=527))

    def test_guess_time_from_catalog_day(self):
        self.reject(lambda x: x["row"].update(
            reentry_physical_time_utc="1963-11-08T12:00:00Z"))

    def test_guess_location_from_catalog_day(self):
        self.reject(lambda x: x["row"].update(reentry_location="Conde"))

    def test_fabricated_sensor(self):
        self.reject(lambda x: x["row"].update(source_528_sensor_id="SHEMYA"))

    def test_promote_visual_from_ocr(self):
        self.reject(lambda x: x["row"].update(
            identity_match="DIRECT_VISUAL_VERIFIED"))

    def test_invent_historical_visual_page(self):
        self.reject(lambda x: x["source"].update(printed_page=43))

    def test_count_as_independent_observation(self):
        self.reject(lambda x: x["independence"].update(
            independent_528_instrumental_observations_added=1))

    def test_activate_physical_constraint(self):
        self.reject(lambda x: x["graph"].update(
            physical_constraints_activated=1))

    def test_promote_lean_or_simulation(self):
        self.reject(lambda x: x["graph"].update(lean_predicates_activated=1))
        self.reject(lambda x: x["graph"].update(change_to_simulation_parameters=True))

    def test_orphan_1963_dependency(self):
        self.reject(lambda x: x.update(dependencies=[]))

    def test_bad_pdf_bytes_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "spoof.pdf"
            p.write_bytes(b"%PDF-1.7\nfake original")
            with self.assertRaisesRegex(ValueError, "length mismatch"):
                verify_pdf(p)

    def test_wrong_pdf_magic_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "spoof.pdf"
            p.write_bytes(b"not a pdf")
            with self.assertRaisesRegex(ValueError, "not a PDF"):
                verify_pdf(p)


if __name__ == "__main__":
    unittest.main()
