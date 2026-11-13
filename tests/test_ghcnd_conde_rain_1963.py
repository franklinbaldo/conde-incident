"""Controls on a distinct archival source, using original NOAA station bytes."""
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
S = importlib.util.spec_from_file_location("ghcnd_audit", ROOT / "tools/audit_ghcnd_conde_rain_1963.py")
audit = importlib.util.module_from_spec(S)
S.loader.exec_module(audit)


class GHCNdCondeRainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get("GHCND_SOURCE_DIR"):
            raise unittest.SkipTest("Original NOAA files are provided by the dedicated pinned-source workflow")
        cls.root = Path(os.environ["GHCND_SOURCE_DIR"])
        cls.conde = (cls.root / "BR048346820.dly").read_bytes()

    def test_full_originals_and_exact_reproducibility(self):
        result = audit.audit(self.root)
        expected = json.loads((ROOT / "research/meteorology/ghcnd_conde_precip_19631107_09.json").read_text())
        self.assertEqual(result, expected)
        self.assertEqual(len(result["stations"]), 11)
        self.assertEqual(sum(len(st["daily"]) for st in result["stations"]),33)

    def test_conde_record_is_daily_not_wind(self):
        result = audit.audit(self.root)
        conde = result["stations"][0]
        self.assertEqual((conde["id"], conde["station"]), ("BR048346820", "CONDE"))
        self.assertEqual([x["precipitation_mm"] for x in conde["daily"]], [0.0,3.5,0.0])
        self.assertEqual([x["source_flag"] for x in conde["daily"]], ["I"]*3)
        self.assertEqual([x["quality_flag"] for x in conde["daily"]], [None]*3)
        self.assertIsNone(result["not_proved"]["observation_time_within_day"])
        self.assertIsNone(result["not_proved"]["active_fall_constraint"])

    def test_nearby_indiaroba_2point4_other_nine_zero_on_nov8(self):
        stations = audit.audit(self.root)["stations"]
        rainy = {s["station"]:s["daily"][1]["precipitation_mm"] for s in stations if s["daily"][1]["precipitation_mm"]>0}
        self.assertEqual(rainy,{"CONDE":3.5,"INDIAROBA":2.4})
        self.assertTrue(all(s["daily"][0]["precipitation_mm"]==0 and s["daily"][2]["precipitation_mm"]==0 for s in stations))

    def test_byte_change_is_detected_by_full_sha(self):
        self.assertNotEqual(audit.sha256(self.conde.replace(b"196311PRCP",b"196312PRCP",1)),audit.SHA["BR048346820.dly"])

    def test_1963_month_absent_rejected(self):
        corrupted=self.conde.replace(b"196311PRCP",b"196310PRCP",1)
        self.assertNotEqual(corrupted,self.conde)
        with self.assertRaisesRegex(ValueError,"exactly one"):
            audit.parse_november(corrupted,"BR048346820")

    def test_wrong_station_id_rejected(self):
        with self.assertRaisesRegex(ValueError,"layout / station"):
            audit.parse_november(self.conde,"BR999999999")

    def test_quality_flag_corruption_rejected(self):
        records=self.conde.splitlines()
        n=next(i for i,r in enumerate(records) if r[11:21]==b"196311PRCP")
        row=bytearray(records[n]);offset=21+7*8;row[offset+6]=ord("X")
        records[n]=bytes(row)
        with self.assertRaisesRegex(ValueError,"absent or flagged"):
            audit.parse_november(b"\n".join(records),"BR048346820")

    def test_missing_value_rejected(self):
        records=self.conde.splitlines()
        n=next(i for i,r in enumerate(records) if r[11:21]==b"196311PRCP")
        row=bytearray(records[n]);offset=21+7*8;row[offset:offset+5]=b"-9999"
        records[n]=bytes(row)
        with self.assertRaisesRegex(ValueError,"absent or flagged"):
            audit.parse_november(b"\n".join(records),"BR048346820")

    def test_lineage_not_instrument_or_independence(self):
        result=audit.audit(self.root)
        self.assertTrue(all(v is None for v in result["not_proved"].values()))
        self.assertEqual(result["status"],"CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION")
        self.assertTrue(all(x["source_flag"]=="I" for st in result["stations"] for x in st["daily"]))

if __name__=="__main__":unittest.main()
