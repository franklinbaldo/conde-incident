"""Original IGRA pressure-temperature observations and dry-gas proxy negative controls."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_igra_recife_dry_density as audit
from audit_igra_recife_window import DAYS, load_original

class RecifeDryDensityTests(unittest.TestCase):
    def test_exact_81_source_levels_and_published_json(self):
        audit.check()
        data = [audit.extract(day) for day in DAYS]
        self.assertEqual([x["source_levels"] for x in data], [29, 26, 26])
        self.assertEqual([x["rh_levels"] for x in data], [10, 6, 16])
        for day, row in zip(DAYS, data):
            self.assertEqual(row["source"]["excerpt_sha256"], DAYS[day][0])
            self.assertIsNone(row["epoch"]["actual_release_utc"])
            self.assertEqual(row["source"]["upstream"], "ncdc6301")

    def test_hand_computed_value(self):
        row = next(x for x in audit.extract("08")["levels"] if x["pressure_hpa"] == 1000)
        self.assertEqual(row["temperature_deg_c"], 26.9)
        self.assertAlmostEqual(row["dry_density_proxy_kg_m3"], 100000/(287.05*300.05), places=8)

    def test_missing_humidity_never_becomes_zero_uncertainty(self):
        for day in DAYS:
            data = audit.extract(day)
            self.assertLess(data["rh_levels"], data["source_levels"])
            self.assertTrue(any(r["reported_rh_percent"] is None for r in data["levels"]))
            link = data["physical_link"]
            self.assertTrue(all(x is None for x in link["uncertainties"].values()))
            for k in ("conde_air_density_estimated", "norad528_thermosphere_estimated", "fragment_drift_estimated"):
                self.assertFalse(link[k])

    def test_invalid_pressure_and_kelvin(self):
        for p, t in ((0, 200), (-1, 200), (100000, -3000)):
            with self.subTest((p, t)), self.assertRaises(ValueError):
                audit.density_proxy(p, t)

    def test_wrong_epoch_upstream_and_truncation_refused(self):
        original=load_original("08")
        for changed in (original+b"wrong extra record",
                        original.replace(b"1963 11 08", b"1963 11 09", 1),
                        original.replace(b"ncdc6301", b"ncdc6100", 1)):
            with self.subTest(changed=changed[:40]), self.assertRaises(ValueError):
                audit.extract("08", changed)

    def test_bogus_temperature_height_pressure_humidity(self):
        raw = load_original("08").decode("ascii").splitlines(keepends=True)
        for start, end, val in ((22,27,"  999"), (16,21,"00000"),
                                (9,15,"101600"), (28,33," 2000")):
            lines = raw.copy()
            lines[2] = lines[2][:start]+val+lines[2][end:]
            with self.subTest(field=start), self.assertRaises(ValueError):
                audit.extract("08", "".join(lines).encode("ascii"))

    def test_pressure_geopotential_order_and_positive_density(self):
        for day in DAYS:
            rows=audit.extract(day)["levels"]
            for x,y in zip(rows,rows[1:]):
                self.assertGreater(x["pressure_hpa"],y["pressure_hpa"])
                self.assertLess(x["geopotential_height_m_asl"],y["geopotential_height_m_asl"])
                self.assertGreater(x["dry_density_proxy_kg_m3"],0)
                self.assertGreater(y["dry_density_proxy_kg_m3"],0)

if __name__=="__main__":
    unittest.main()
