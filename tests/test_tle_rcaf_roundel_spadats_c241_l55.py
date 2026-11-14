"""Negative controls for Roundel custody, repeated with python -O."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tle_rcaf_roundel_spadats_c241_l55 import audit, read_model, verify_pdf  # noqa: E402


class RcafRoundelTests(unittest.TestCase):
    def setUp(self):
        self.model = read_model()

    def reject(self, callback):
        changed = copy.deepcopy(self.model)
        callback(changed)
        with self.assertRaises(ValueError):
            audit(changed)

    def test_valid_context_only(self):
        self.assertEqual(audit(self.model)["physical_constraints"], 0)

    def test_source_hash_drift(self):
        self.reject(lambda d: d["source"].update(sha256="0" * 64))

    def test_source_page_drift(self):
        self.reject(lambda d: d["source"].update(pdf_page_index_zero_based=5))

    def test_source_date_promoted_to_instant(self):
        self.reject(lambda d: d["source"].update(publication_date_precision="DAY"))

    def test_pdf_createtime_as_original_publication(self):
        self.reject(lambda d: d["source"].update(scan_pdf_creation_date="1963-09-01"))

    def test_source_wrong_camera(self):
        self.reject(lambda d: d["anchors"][0].update(text="Baker-Nunn observations of NORAD 528"))

    def test_source_claim_promoted_to_instrumental_observation(self):
        self.reject(lambda d: d["anchors"][0].update(kind="NAMED_INSTRUMENTAL_OBSERVATION"))

    def test_add_second_appearance_as_independent_sensor(self):
        self.reject(lambda d: d["independence"].update(independent_instrumental_observations_recovered=1))

    def test_claim_receipt_of_528(self):
        self.reject(lambda d: d.update(norad_528_transmission_receipt="received"))

    def test_claim_station_of_528(self):
        self.reject(lambda d: d.update(norad_528_observation_station="Cold Lake"))

    def test_invent_sigma(self):
        self.reject(lambda d: d.update(norad_528_sensor_sigma=0.001))

    def test_invent_utc(self):
        self.reject(lambda d: d.update(norad_528_observation_utc="1963-11-08T00:00:00Z"))

    def test_photo_location_unfounded(self):
        self.reject(lambda d: d["anchors"][2].update(evidentiary_scope="The photo proves Cold Lake."))

    def test_invent_impact(self):
        self.reject(lambda d: d.update(impact_at_conde="CONFIRMED"))

    def test_activate_physics(self):
        self.reject(lambda d: d.update(physical_constraint_active=True))

    def test_extra_field(self):
        self.reject(lambda d: d.update(camera_528="Cold Lake"))

    def test_duplicate_anchor(self):
        self.reject(lambda d: d["anchors"].append(copy.deepcopy(d["anchors"][0])))

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "dup.json"
            p.write_text('{"evidence_id": "C241-L55", "evidence_id": "fake"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_model(p)

    def test_reject_non_pdf_bytes(self):
        with self.assertRaises(ValueError):
            verify_pdf(b"this is not a PDF", self.model)


if __name__ == "__main__":
    unittest.main()
