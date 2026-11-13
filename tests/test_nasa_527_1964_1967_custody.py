"""C241-L28 adversarial tests for 527 primary published crosswalk and source bytes."""
import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from tools.nasa_527_1964_1967_custody import ROOT, LEDGER, PARENT, validate, validate_pdfs

DATA = json.loads(LEDGER.read_text(encoding="utf-8"))
P = json.loads(PARENT.read_text(encoding="utf-8"))

class OriginalNASA527(unittest.TestCase):
    def reject(self, source, mutate):
        data, parent = copy.deepcopy(DATA), copy.deepcopy(P)
        mutate(data if source == "data" else parent)
        with self.assertRaises((ValueError, TypeError, KeyError, StopIteration)):
            validate(data, parent)

    def test_four_sources_and_primary_identity(self):
        result = validate(DATA, P)
        self.assertEqual(result["source_ids"],
                         ["19640017911", "19650016819", "19660012484", "19680005210"])
        self.assertEqual(result["crosswalk"], "1963 03A = 527 in 4 original NASA publications")
        self.assertEqual(result["independent_sensor_measurements_added"], 0)
        self.assertIsNone(result["publisher_lag_or_terminal_time"])

    def test_wrong_1964_catalog_id(self):
        self.reject("data", lambda d: d["source_documents"][0]["row"].update(
            catalog_number_printed=528))

    def test_fake_primary_528_identity(self):
        self.reject("data", lambda d: d["crosswalk"].update(
            source_1963_03B_to_528_direct_primary_printed=True))

    def test_fake_primary_529_identity(self):
        self.reject("data", lambda d: d["crosswalk"].update(
            source_1963_03C_to_529_direct_primary_printed=True))

    def test_swapped_1966_ntrs(self):
        self.reject("data", lambda d: d["source_documents"][2].update(ntrs_id="19660012485"))

    def test_wrong_1965_issue(self):
        self.reject("data", lambda d: d["source_documents"][1].update(issue=10))

    def test_wrong_1967_pdf_page(self):
        self.reject("data", lambda d: d["source_documents"][3].update(page_index_zero_based=6))

    def test_wrong_1964_hash(self):
        self.reject("data", lambda d: d["source_documents"][0].update(sha256="0"*64))

    def test_wrong_1965_pdf_bytes(self):
        self.reject("data", lambda d: d["source_documents"][1].update(bytes=123))

    def test_wrong_1966_perigee(self):
        self.reject("data", lambda d: d["source_documents"][2]["row"].update(perigee_km_printed=475))

    def test_wrong_1967_period(self):
        self.reject("data", lambda d: d["source_documents"][3]["row"].update(
            period_minutes_printed="93.6"))

    def test_fake_observation_epoch(self):
        self.reject("data", lambda d: d["source_documents"][0].update(
            instrumental_epoch_utc="1964-05-31T12:00:00Z"))

    def test_fake_sensor_covariance(self):
        self.reject("data", lambda d: d["source_documents"][1].update(measurement_covariance=[1]))

    def test_editorial_change_promoted_to_decay_rate(self):
        self.reject("data", lambda d: d["reported_delta"].update(
            interpretation="MEASURED_PHYSICAL_DRAG"))

    def test_false_independent_measurements(self):
        self.reject("data", lambda d: d["observation_model"].update(
            actual_sensor_observations_added=4))

    def test_lean_prematurely_promoted(self):
        self.reject("data", lambda d: d["limits"].update(lean_constraint_activated=True))

    def test_source_relationship_disconnected(self):
        self.reject("data", lambda d: d["edges"].pop())

    def test_parent_source_identity_modified(self):
        self.reject("parent", lambda d: d["docs"][5].update(ntrs="19640001197"))

    def test_wrong_bytes_rejected_even_with_pdf_magic(self):
        with TemporaryDirectory() as p:
            Path(p, "19640017911.pdf").write_bytes(b"%PDF-1.4\nFORGED\n")
            with self.assertRaisesRegex(ValueError, "changed length"):
                validate_pdfs(DATA, Path(p))

    def test_non_pdf_rejected(self):
        with TemporaryDirectory() as p:
            Path(p, "19640017911.pdf").write_bytes(b"not a pdf")
            with self.assertRaisesRegex(ValueError, "not PDF"):
                validate_pdfs(DATA, Path(p))

if __name__ == "__main__":
    unittest.main()
