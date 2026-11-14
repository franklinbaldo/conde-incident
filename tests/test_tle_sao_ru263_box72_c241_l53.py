"""Adversarial tests for RU263 Cold Lake box 72 supplement, including Python -O."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_sao_ru263_box72_c241_l53 import audit, read_model, verify_pdf  # noqa: E402


class Box72Tests(unittest.TestCase):
    def setUp(self):
        self.ledger = read_model()

    def reject(self, mutate):
        candidate = copy.deepcopy(self.ledger)
        mutate(candidate)
        with self.assertRaises(ValueError):
            audit(candidate)

    def test_original_addendum_is_valid(self):
        actual = audit(self.ledger)
        self.assertEqual(actual["evidence_id"], "C241-L53")
        self.assertEqual(actual["additional_folders"], 2)
        self.assertEqual(actual["physical_constraints"], 0)

    def test_do_not_change_parent_hash(self):
        self.reject(lambda x: x.update(parent_manifest_sha256="0" * 64))

    def test_do_not_change_parent_id(self):
        self.reject(lambda x: x.update(id="C241-L54"))

    def test_do_not_change_pdf_sha(self):
        self.reject(lambda x: x.update(source_pdf_sha256="0" * 64))

    def test_page_mismatch(self):
        self.reject(lambda x: x["anchors"][0].update(pdf_page_index_zero_based=47))

    def test_wrong_box(self):
        self.reject(lambda x: x["anchors"][0].update(box=67))

    def test_wrong_series(self):
        self.reject(lambda x: x["anchors"][1].update(series=8))

    def test_wrong_heading(self):
        self.reject(lambda x: x["anchors"][1].update(phrase="#130 Inventory and audits, 1964."))

    def test_observation_inferred_from_folder(self):
        self.reject(lambda x: x["anchors"][0].update(scope="Confirmed satellite observation"))

    def test_invented_receipt(self):
        self.reject(lambda x: x.update(spadats_528_transfer_receipt="received"))

    def test_invented_utc(self):
        self.reject(lambda x: x.update(norad_528_observation_utc="1963-11-08T00:00:00Z"))

    def test_invented_independent_sensors(self):
        self.reject(lambda x: x.update(independent_instrumental_observations=2))

    def test_invented_detection(self):
        self.reject(lambda x: x.update(individual_observations_recovered=1))

    def test_invented_physics(self):
        self.reject(lambda x: x.update(physical_constraint_active=True))

    def test_extra_key(self):
        self.reject(lambda x: x.update(sensor_528="Cold Lake"))

    def test_duplicate_anchor(self):
        self.reject(lambda x: x["anchors"].append(copy.deepcopy(x["anchors"][0])))

    def test_invalid_pdf(self):
        with self.assertRaises(ValueError):
            verify_pdf(b"%PDF-1.4\\n")

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "bad.json"
            p.write_text('{"id":"C241-L53","id":"fabricated"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_model(p)


if __name__ == "__main__":
    unittest.main()
