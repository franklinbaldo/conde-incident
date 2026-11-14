"""CGEO-57: fail-closed tests survive python -O."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cgeo57", ROOT / "tools/cgeo57_nara_temporal.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestCGEO57(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(m.SOURCE.read_text(encoding="utf-8"))
        self.parent = json.loads(m.PARENT.read_text(encoding="utf-8"))

    def reject(self, change, parent=False):
        data = copy.deepcopy(self.parent if parent else self.data)
        change(data)
        with self.assertRaises(ValueError):
            m.validate(self.data, data) if parent else m.validate(data, self.parent)

    def test_contract(self):
        self.assertEqual(m.validate(self.data, self.parent), 4)

    def test_no_1956_masquerade(self):
        self.reject(lambda d: d["scans"][0].update(flight_date_reading="5 OCT 56"))

    def test_not_prepared_in_1942(self):
        self.reject(lambda d: d["scans"][0].update(preparation_date_iso="1942-09-27"))

    def test_fake_preparation_date(self):
        self.reject(lambda d: d["scans"][2].update(preparation_date_reading="6 OCT 42"))

    def test_no_identified_preparer(self):
        self.reject(lambda d: d["scans"][1].update(prepared_by_name="Jane Doe"))

    def test_no_flight_time(self):
        self.reject(lambda d: d["limits"].update(photo_capture_utc="1942-09-27T11:00Z"))

    def test_no_spot(self):
        self.reject(lambda d: d["limits"].update(verified_spot_number="125370"))

    def test_no_film_can(self):
        self.reject(lambda d: d["limits"].update(film_can="ON000000"))

    def test_no_geometry(self):
        self.reject(lambda d: d["limits"].update(georeferenced_frame_footprint=[]))

    def test_no_conde_center(self):
        self.reject(lambda d: d["limits"].update(conde_1963_center=[0, 0]))

    def test_no_fall(self):
        self.reject(lambda d: d["limits"].update(fall_location=[0, 0]))

    def test_no_orbit_promotion(self):
        self.reject(lambda d: d["limits"].update(orbital_constraint_activated=True))

    def test_no_photo_count(self):
        self.reject(lambda d: d["counts"].update(original_film_frames_acquired=4))

    def test_no_new_independent_sources(self):
        self.reject(lambda d: d["counts"].update(original_overlay_jpegs_referenced=8))

    def test_source_hash_dependency(self):
        self.reject(lambda d: d["scans"][0].update(sha256="f" * 64), parent=True)

    def test_source_bytes_dependency(self):
        self.reject(lambda d: d["scans"][0].update(bytes=2), parent=True)

    def test_source_op_dependency(self):
        self.reject(lambda d: d["scans"][0].update(op_file_no="999999"), parent=True)

    def test_missing_source(self):
        self.reject(lambda d: d["scans"].pop(), parent=True)

    def test_duplicate_sheet(self):
        self.reject(lambda d: d["scans"][1].update(sheet="00247"))

    def test_source_lineage(self):
        self.reject(lambda d: d.update(parent="CGEO-54"))


if __name__ == "__main__":
    unittest.main()
