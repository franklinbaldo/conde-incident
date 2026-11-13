"""Adversarial checks using the two real NOAA source bytes, not invented observations."""
import importlib.util
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("archive", ROOT / "tools/audit_isd_bahia_coastal_1963_archive.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class NOAAIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all(os.environ.get(key) for key in ("NOAA_ISD_HISTORY", "NOAA_ISD_INDEX_1963")):
            # The dedicated source-pinned NOAA workflow downloads original bytes.
            # Global offline unittest discovery does not fetch arbitrary network data.
            raise unittest.SkipTest("NOAA source inputs are staged by the dedicated source-pinned workflow")
        cls.history = Path(os.environ["NOAA_ISD_HISTORY"]).read_bytes()
        cls.index = Path(os.environ["NOAA_ISD_INDEX_1963"]).read_bytes()

    def test_expected_full_source_and_coverage(self):
        out = audit.audit(self.history, self.index)
        self.assertEqual(out["directory_gz_count"], 5577)
        self.assertEqual(out["catalogue_br_country_code_with_1963_in_year_bounds"], 129)
        self.assertEqual(out["matching_1963_files"], 10)
        self.assertEqual(out["matched_within_500km"], 0)
        self.assertEqual(out["matched_within_800km"], 1)
        self.assertEqual(out["matched_nearest_first"][0]["file"], "834970-99999-1963.gz")

    def test_nearest_catalogue_stations_are_missing_from_directory(self):
        out = audit.audit(self.history, self.index)
        nearest = out["catalogue_nearest_12"]
        self.assertEqual(nearest[0]["file"], "830960-99999-1963.gz")
        self.assertEqual(nearest[0]["annual_file_listed"], False)
        self.assertEqual(nearest[1]["annual_file_listed"], False)
        self.assertEqual(nearest[2]["annual_file_listed"], False)

    def test_changed_index_digest_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit(self.history, self.index.replace(b'834970-99999-1963.gz', b'834971-99999-1963.gz', 1))

    def test_changed_station_history_digest_rejected(self):
        with self.assertRaises(ValueError):
            audit.audit(self.history + b'\n', self.index)

    def test_duplicate_name_in_index_rejected(self):
        row = b'<a href="834970-99999-1963.gz">duplicate</a>\n'
        with self.assertRaises(ValueError):
            audit.parse_index(self.index + row)

    def test_1963_catalogue_year_bounds_are_not_observation_proof(self):
        rows = audit.catalogue_candidates(self.history)
        by_key = {r["file"]: r for r in rows}
        self.assertIn("830960-99999-1963.gz", by_key)
        self.assertNotIn("830960-99999-1963.gz", audit.parse_index(self.index))

    def test_geodesic_reference_matches_prior_igra_regional_work(self):
        ref = __import__("json").loads((ROOT / "research/meteorology/igra_bahia_regional_1963.json").read_text())["reference"]["lat_lon"]
        self.assertEqual(ref, list(audit.CONDE_REF))

    def test_no_invented_observation_or_calibrated_transfer(self):
        out = audit.audit(self.history, self.index)
        self.assertTrue(all(v is None for v in out["not_proved"].values()))
        self.assertEqual(out["status"], "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION")


if __name__ == "__main__":
    unittest.main()
