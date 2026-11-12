"""UWM map legend: preserve printed projection family and prohibit 1963 GIS invention."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conde_historical_legend import PARENT, check_derivative, export, read_record

class HistoricalMapLegendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = read_record()

    def changed(self, edits):
        altered = copy.deepcopy(self.rec)
        edits(altered)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        p = Path(temp.name) / "altered.json"
        p.write_text(json.dumps(altered, ensure_ascii=False), encoding="utf-8")
        return p

    def test_same_primary_source_as_lontra_not_new_survey(self):
        self.assertTrue(self.rec["same_underlying_source_not_new_independent_survey"])
        self.assertEqual(self.rec["parent_occurrence_id"], "ARCH-UWM-ARACAJU-SE-10814-20261112")

    def test_printed_polyconic_does_not_establish_epsg_or_datum(self):
        g = self.rec["cartographic_interpretation"]
        self.assertEqual(g["projection_family_printed"], "POLYCONIC")
        self.assertIsNone(g["crs_authority"])
        self.assertIsNone(g["datum"])
        self.assertIsNone(g["projection_full_parameters"])

    def test_no_municipal_legend_symbol_and_toponym_not_polygon(self):
        lit = self.rec["literal_readings"]
        self.assertEqual(lit["legend_boundary_classes_observed"],
                         ["Internacional", "Interestadual", "Marco de fronteira"])
        self.assertFalse(lit["municipal_boundary_class_in_inspected_legend"])
        self.assertTrue(lit["toponym_conde_visible"])
        self.assertFalse(self.rec["cartographic_interpretation"]["city_label_conde_is_municipal_perimeter"])

    def test_1963_export_never_activates_historical_constraint(self):
        out = export("1963-11-08", self.rec)
        self.assertIsNone(out["historical_municipal_boundary_polygon"])
        self.assertIsNone(out["event_spatial_membership"])
        self.assertFalse(out["can_constrain_reentry_1963"])
        self.assertEqual(out["status"], "CONNECTED_PENDING_CALIBRATION")
        self.assertEqual(out["sheet_projection_family"], "POLYCONIC")
        self.assertIsNone(out["sheet_datum"])
        with self.assertRaises(ValueError):
            export("1963-11-99", self.rec)

    def test_projected_epsg_fabrication_refused(self):
        p = self.changed(lambda c: c["cartographic_interpretation"].update({"crs_authority": "EPSG:4674"}))
        with self.assertRaisesRegex(ValueError, "unproven"):
            read_record(p, PARENT)

    def test_fake_boundary_refused(self):
        p = self.changed(lambda c: c["castor_contract"].update({
            "historical_municipal_boundary_polygon": [[[-37.6, -11.8]]]
        }))
        with self.assertRaisesRegex(ValueError, "fabricated"):
            read_record(p, PARENT)

    def test_fake_reentry_constraint_refused(self):
        p = self.changed(lambda c: c["castor_contract"].update({"can_constrain_reentry_1963": True}))
        with self.assertRaisesRegex(ValueError, "unproven"):
            read_record(p, PARENT)

    def test_fabricated_municipal_symbol_refused(self):
        p = self.changed(lambda c: c["literal_readings"].update({"municipal_boundary_class_in_inspected_legend": True}))
        with self.assertRaisesRegex(ValueError, "not observed"):
            read_record(p, PARENT)

    def test_iiif_digest_can_verify_download_but_not_original_jp2(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "fake.jpg"
            f.write_bytes(b"not a UWM JPEG")
            with self.assertRaisesRegex(ValueError, "checksum"):
                check_derivative(self.rec, "legend_limits", f)
            self.assertFalse(self.rec["source"]["original_jp2_verified_in_this_review"])
            self.assertIsNone(self.rec["source"]["original_jp2_sha256"])

if __name__ == "__main__":
    unittest.main()
