"""Negative controls for genealogical, chronological and geographic inference."""
import copy
import tempfile
import unittest
from pathlib import Path
from tools.cgeo38_iocs29_lineage import load_contract, validate_contract, verify_pdf

class CGEO38Tests(unittest.TestCase):
    def setUp(self):
        self.doc = load_contract()

    def reject(self, change):
        doc = copy.deepcopy(self.doc)
        change(doc)
        with self.assertRaises(ValueError):
            validate_contract(doc)

    def test_reference(self):
        self.assertEqual(validate_contract(self.doc), "CGEO38_CONTRACT_PASS")

    def test_1913_identification(self):
        self.reject(lambda d: d["map_1913"].update(publication=15))
        self.reject(lambda d: d["map_1913"].update(printed="1963-11"))
        self.reject(lambda d: d["map_1913"].update(replica_sha256="0"*64))

    def test_1912_annotation_is_not_image_comparison(self):
        self.reject(lambda d: d["itapicuru_1912"].update(original_map_acquired=True))
        self.reject(lambda d: d["itapicuru_1912"].update(pixel_comparison_proven=True))
        self.reject(lambda d: d["itapicuru_1912"].update(archive_note_date="1963-11-08"))
        self.reject(lambda d: d["edges"][0].update(pixel_transfer_verified=True))

    def test_graph_cannot_drop_intermediate_map(self):
        self.reject(lambda d: d["edges"].pop(1))
        self.reject(lambda d: d["edges"][1].update(to="CGEO-36"))

    def test_not_an_independent_1963_observation(self):
        self.reject(lambda d: d["limits"].update(independent_survey=True))
        self.reject(lambda d: d["limits"].update(flight_date="1963-11-08"))

    def test_no_orbital_or_city_center_promotion(self):
        self.reject(lambda d: d["limits"].update(center_1963=[-37,-12]))
        self.reject(lambda d: d["limits"].update(reported_fall=[-37,-12]))
        self.reject(lambda d: d["limits"].update(uncertainty_m=0))
        self.reject(lambda d: d["limits"].update(can_constrain_orbital_reentry=True))
        self.reject(lambda d: d["limits"].update(spatial_coverage_confirmed=True))

    def test_custody_cannot_be_faked(self):
        self.reject(lambda d: d["archives"].update(ds_pdf_sha256="0"*64))
        self.reject(lambda d: d["archives"].update(physical_original_inspected=True))
        self.reject(lambda d: d["map_1913"].update(full_visual_inspection=True))

    def test_no_false_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            wrong = Path(directory) / "fake.pdf"
            wrong.write_bytes(b"%PDF-1.4\n%%EOF")
            for kind in ("map", "ds", "f4"):
                with self.assertRaises(ValueError):
                    verify_pdf(wrong, kind)
        with self.assertRaises(FileNotFoundError):
            verify_pdf(Path("/nonexistent/cgeo38.pdf"), "map")

if __name__ == "__main__":
    unittest.main()
