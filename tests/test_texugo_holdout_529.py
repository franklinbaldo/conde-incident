"""Deterministic falsifiers, all SYNTHETIC; not 1963 NORAD observations."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from texugo_holdout_529 import Observation, CUTOFFS, EXPECTED_SHA256, EXPECTED_URL, evaluate, load_audited, parse_csv, require_same_bindings, run


def samples(c527=0.4, c528=0.4, c529=0.4, noisy_target=False):
    base = datetime(1963, 6, 1, tzinfo=timezone.utc)
    result = []
    for sat, curvature in ((527, c527), (528, c528), (529, c529)):
        for day in list(range(0, 151, 10)) + list(range(155, 211, 7)):
            x = (day - 140) / 60
            noise = (0.03 * x * x) if noisy_target and sat == 529 and day <= 140 else 0
            y = 14 + sat / 1000 + 0.03 * x + curvature * x * x + noise
            result.append(Observation(sat, base + timedelta(days=day), y))
    return result


class HoldoutControls(unittest.TestCase):
    def test_joint_improves_when_shared_curvature_is_real_and_target_training_noisy(self):
        base = datetime(1963, 6, 1, tzinfo=timezone.utc)
        rows = []
        for o in samples():
            day = (o.epoch - base).days
            if o.sat != 529 or day > 140:
                rows.append(o)
            elif day in (110, 120, 130, 140):
                noise = {110: 0.0, 120: 0.04, 130: -0.04, 140: 0.02}[day]
                rows.append(Observation(o.sat, o.epoch, o.mean_motion + noise))
        r = evaluate(rows, "1963-10-21")
        self.assertEqual(r["status"], "JOINT_BETTER")
        self.assertGreater(r["holdout_529_count"], 0)

    def test_joint_worsens_when_529_has_different_curvature(self):
        r = evaluate(samples(c527=0.4, c528=0.4, c529=-0.3), "1963-10-21")
        self.assertEqual(r["status"], "BASELINE_BETTER")
        self.assertGreater(r["holdout_rmse_rev_day"]["shared_curvature_527_528_to_529"],
                           r["holdout_rmse_rev_day"]["quadratic_529_only"])

    def test_no_future_529_or_other_future_leakage_into_coefficients(self):
        rows = samples(noisy_target=True)
        old = evaluate(rows, "1963-10-21")
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        contaminated = [Observation(o.sat, o.epoch, o.mean_motion + 1.0) if o.epoch > cutoff else o for o in rows]
        new = evaluate(contaminated, "1963-10-21")
        self.assertEqual(old["coefficients"], new["coefficients"])
        self.assertNotEqual(old["holdout_rmse_rev_day"], new["holdout_rmse_rev_day"])

    def test_refuses_singular_short_or_no_future_holdout(self):
        cutoff = "1963-10-21"
        self.assertEqual(evaluate(samples()[:2], cutoff)["status"], "NOT_RUN")
        all_past = [o for o in samples() if o.epoch < datetime(1963, 10, 20, tzinfo=timezone.utc)]
        self.assertEqual(evaluate(all_past, cutoff)["status"], "NOT_RUN")

    def test_cannot_spoof_provenance_by_manipulating_json_or_csv(self):
        import csv
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            csv_path, audit_path, parquet_path = p / "data.csv", p / "audit.json", p / "source.parquet"
            with csv_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["source_row", "norad_id", "epoch", "mean_motion"])
                writer.writeheader()
                for index, sat in enumerate((527, 528, 529)):
                    writer.writerow({"source_row": index, "norad_id": sat,
                                     "epoch": "1963-10-01T00:00:00Z", "mean_motion": 15.0})
            parquet_path.write_bytes(b"PAR1fabricatedPAR1")
            audit_path.write_text(json.dumps({"source": {"url": EXPECTED_URL, "hashes": {"sha256": "bad"}}}))
            with self.assertRaisesRegex(ValueError, "custódia"):
                load_audited(csv_path, audit_path, parquet_path)
            audit_path.write_text(json.dumps({"source": {"url": EXPECTED_URL,
                                   "hashes": {"sha256": EXPECTED_SHA256, "sha1": "fake"}}, "problems": []}))
            # A plausible audit JSON does NOT authenticate a fake Parquet or an arbitrary CSV.
            with self.assertRaisesRegex(ValueError, "custódia"):
                load_audited(csv_path, audit_path, parquet_path)
            parsed, keys = parse_csv(csv_path)
            self.assertEqual(len(parsed), 3)
            require_same_bindings(keys, list(keys))
            with self.assertRaisesRegex(ValueError, "CSV"):
                require_same_bindings(keys, keys[:-1])  # truncated source or added row
            altered = list(keys)
            altered[1] = (*altered[1][:3], altered[1][3] + 0.01)
            with self.assertRaisesRegex(ValueError, "CSV"):
                require_same_bindings(altered, keys)  # silently changed mean motion
            with csv_path.open("a") as f:
                f.write("2,529,1963-10-01T00:00:00Z,16.0\\n")
            with self.assertRaisesRegex(ValueError, "duplicatas"):
                parse_csv(csv_path)

    def test_even_identical_csv_row_repetition_is_not_source_custody(self):
        row = (1, 529, datetime(1963, 10, 1, tzinfo=timezone.utc), 15.0)
        with self.assertRaisesRegex(ValueError, "CSV"):
            require_same_bindings([row, row], [row])

    def test_no_likelihood_or_geography_in_report(self):
        report = run(samples())
        self.assertTrue(report["no_probability"])
        self.assertEqual(len(report["results"]), len(CUTOFFS))
        self.assertTrue(all("holdout_rmse_rev_day" in item or item["status"] == "NOT_RUN"
                            for item in report["results"]))
        self.assertNotIn("Conde", str(report))


if __name__ == "__main__":
    unittest.main()
