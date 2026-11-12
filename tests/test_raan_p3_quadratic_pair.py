"""Adversarial source/epoch/score checks for the C241-P4 paired ablation."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from raan_p3_quadratic_pair import compare


def fixture():
    p = {"schema": "conde.secondary-fitfield-j2-outoftime/v1",
         "source": {"parquet_sha256": "parquet", "csv_sha256": "csv", "raan_json_sha256": "raan",
                    "split_manifest_sha256": "frozen"},
         "method": {"fit_before_utc": "1963-08-01T00:00:00Z",
                    "domain_reduction": "NONE_NO_PRIMARY_TRACKING_FRAME_OR_SENSOR_ERRORS"},
         "objects": {}}
    q = {"schema": "conde.texugo-quadratic-raan-ablation/v1",
         "source": {"parquet_sha256": "parquet", "csv_sha256": "csv", "raan_json_sha256": "raan",
                    "frozen_split_sha256": "frozen"},
         "design": {"fit_epoch_cutoff": "1963-08-01T00:00:00Z", "physical_domain_reduction": "NONE"},
         "objects": {}}
    t0 = datetime(1963, 7, 31, tzinfo=timezone.utc)
    def iso(t): return t.isoformat().replace("+00:00", "Z")
    for sat, n in (("527", 4), ("528", 8), ("529", 23)):
        pblocks, qblocks = {}, {}
        for block, count in (("validation", 1), ("evaluation", n)):
            details, epochs = [], []
            for j in range(count):
                e = iso(t0 + timedelta(days=(j + (3 if block == "validation" else 70))))
                details.append({"epoch_utc": e, "source_rows": [j+10],
                                "observed_secondary_raan_deg": 100.0, "predicted_raan_deg": 99.0,
                                "signed_residual_deg": 1.0})
                epochs.append({"epoch_utc": e, "quadratic_signed_error_deg": 2.0})
            pblocks[block] = {"n": count, "metrics": {"mae_deg": 1.0}, "details": details}
            qblocks[block] = {"n": count, "models": {"fitonly_quadratic": {"mae_deg": 2.0}},
                              "per_epoch": epochs}
        p["objects"][sat] = {"fit_n": 5, "anchor_epoch_utc": iso(t0), **pblocks}
        q["objects"][sat] = {"fit_n": 5, "last_fit_epoch_utc": iso(t0), **qblocks}
    return p, q


class PairingTests(unittest.TestCase):
    def test_true_same_epoch_comparison(self):
        p, q = fixture()
        out = compare(p, q)
        self.assertEqual([out["objects"][s]["evaluation"]["n"] for s in ("527","528","529")], [4,8,23])
        for sat in ("527", "528", "529"):
            e = out["objects"][sat]["evaluation"]
            self.assertEqual(e["p3_minus_quadratic_mae_deg"], -1)
            self.assertEqual(e["p3_better_epoch_count"], e["n"])
            self.assertTrue(e["p3_beats_quadratic"])
        self.assertEqual(out["physical_domain_change"], "NONE_NOT_CALIBRATED")

    def test_reject_source_fingerprint_mismatch(self):
        for field in ("parquet_sha256", "csv_sha256", "raan_json_sha256", "frozen_split_sha256"):
            p, q = fixture()
            q["source"][field] = "corrupted"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "mismatch"):
                compare(p, q)

    def test_reject_epoch_spoof_and_reorder(self):
        p, q = fixture()
        q["objects"]["529"]["evaluation"]["per_epoch"][0]["epoch_utc"] = "2099-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "paired epoch identity"):
            compare(p, q)
        p, q = fixture()
        p["objects"]["527"]["evaluation"]["details"][1]["epoch_utc"] = p["objects"]["527"]["evaluation"]["details"][0]["epoch_utc"]
        q["objects"]["527"]["evaluation"]["per_epoch"][1]["epoch_utc"] = q["objects"]["527"]["evaluation"]["per_epoch"][0]["epoch_utc"]
        with self.assertRaisesRegex(ValueError, "unordered or repeated"):
            compare(p, q)

    def test_reject_corrupt_residual_and_reported_loss(self):
        p, q = fixture()
        p["objects"]["528"]["evaluation"]["details"][0]["signed_residual_deg"] = 1.5
        with self.assertRaisesRegex(ValueError, "disagrees"):
            compare(p, q)
        p, q = fixture()
        q["objects"]["528"]["evaluation"]["models"]["fitonly_quadratic"]["mae_deg"] = 3
        with self.assertRaisesRegex(ValueError, "MAE mismatch"):
            compare(p, q)

    def test_reject_changed_domain_claim_and_leakage(self):
        p, q = fixture()
        p["method"]["domain_reduction"] = "NEW_FILTER"
        with self.assertRaisesRegex(ValueError, "domain status"):
            compare(p, q)
        p, q = fixture()
        for v in (p["objects"]["527"]["validation"]["details"][0],
                  q["objects"]["527"]["validation"]["per_epoch"][0]):
            v["epoch_utc"] = "1963-07-30T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "leakage"):
            compare(p, q)

    def test_reject_nonfinite_and_count_mutation(self):
        p, q = fixture()
        q["objects"]["527"]["evaluation"]["per_epoch"][0]["quadratic_signed_error_deg"] = float("nan")
        with self.assertRaisesRegex(ValueError, "nonnumeric"):
            compare(p, q)
        p, q = fixture()
        p["objects"]["527"]["evaluation"]["n"] = 2
        with self.assertRaisesRegex(ValueError, "row count"):
            compare(p, q)


if __name__ == "__main__":
    unittest.main()
