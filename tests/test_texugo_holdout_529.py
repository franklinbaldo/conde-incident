"""Deterministic falsifiers, all SYNTHETIC; not 1963 NORAD observations."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from texugo_holdout_529 import Observation, CUTOFFS, EXPECTED_SHA256, EXPECTED_URL, evaluate, load_audited, parse_csv, require_same_bindings, rmse, run, utc


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
    def test_rmse_rejects_unpaired_empty_or_nonfinite_scores(self):
        # SYNTHETIC counterexample: old zip-based score returned a false zero
        # when the high-error last observation had no prediction.
        self.assertAlmostEqual(rmse([0.0, 2.0], [0.0, 4.0]), 2 ** 0.5)
        cases = (
            ([], []),
            ([0.0, 10.0], [0.0]),
            ([0.0], [0.0, 1.0]),
            ([0.0, float("nan")], [0.0, 0.0]),
            ([0.0, 1.0], [0.0, float("inf")]),
        )
        for truth, predictions in cases:
            with self.subTest(truth=truth, predicted=predictions):
                with self.assertRaisesRegex(ValueError, "RMSE"):
                    rmse(truth, predictions)

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
                f.write("2,529,1963-10-01T00:00:00Z,16.0" + chr(10))
            with self.assertRaisesRegex(ValueError, "duplicatas"):
                parse_csv(csv_path)

    def test_even_identical_csv_row_repetition_is_not_source_custody(self):
        row = (1, 529, datetime(1963, 10, 1, tzinfo=timezone.utc), 15.0)
        with self.assertRaisesRegex(ValueError, "CSV"):
            require_same_bindings([row, row], [row])

    def test_donor_ablation_detects_one_good_one_bad_donor(self):
        # SYNTHETIC: 527 shares 529 curvature while 528 has opposite curvature.
        # The equal-weight joint curvature is consequently worse than 527 alone.
        result = evaluate(samples(c527=0.4, c528=-0.4, c529=0.4), "1963-10-21")
        error = result["holdout_rmse_rev_day"]
        self.assertLess(error["transfer_527_only"],
                        error["shared_curvature_527_528_to_529"])
        self.assertFalse(result["posthoc_ablations"]["joint_beats_both_individual_donors"])

    def test_linear_control_falsifies_spurious_donor_curvature(self):
        # SYNTHETIC: 529 is exactly linear, both donors curve quadratically.
        result = evaluate(samples(c527=0.4, c528=0.4, c529=0.0), "1963-10-21")
        error = result["holdout_rmse_rev_day"]
        self.assertLess(error["linear_529_only"], error["shared_curvature_527_528_to_529"])
        self.assertFalse(result["posthoc_ablations"]["joint_beats_linear_529"])

    def test_posthoc_models_inherit_strict_temporal_blinding(self):
        rows = samples(c527=0.2, c528=0.4, c529=0.3)
        before = evaluate(rows, "1963-10-21")
        cutoff = datetime(1963, 10, 21, 23, 59, 59, tzinfo=timezone.utc)
        modified = [Observation(o.sat, o.epoch, o.mean_motion + 7.0)
                    if o.epoch > cutoff else o for o in rows]
        after = evaluate(modified, "1963-10-21")
        self.assertEqual(before["coefficients"], after["coefficients"])
        self.assertNotEqual(before["holdout_rmse_rev_day"], after["holdout_rmse_rev_day"])

    def test_overlapping_holdouts_are_not_independent_replications(self):
        # SYNTHETIC counterexample: future target epochs are nested by cutoff.
        from texugo_holdout_529 import overlap_diagnostics
        start = datetime(1963, 8, 30, tzinfo=timezone.utc)
        observations = [Observation(529, start + timedelta(days=d), 15.0)
                        for d in (0, 2, 30, 50, 70)]
        results = [{"cutoff_utc_end_of_day": day, "status": "TIE"} for day in CUTOFFS]
        report = overlap_diagnostics(observations, results)
        self.assertEqual(list(report["future_epochs_per_cutoff"].values()), [4, 3, 2, 1])
        self.assertEqual(report["total_scored_epoch_occurrences"], 10)
        self.assertEqual(report["distinct_future_epochs"], 4)
        self.assertEqual(report["reused_epoch_occurrences"], 6)
        self.assertEqual(report["epochs_shared_by_all_evaluated_cutoffs"], 1)
        self.assertEqual(report["pairwise_overlap_counts"]["1963-08-31|1963-10-21"], 1)
        self.assertFalse(report["independent_replications_established"])
        results[1]["status"] = "NOT_RUN"
        report = overlap_diagnostics(observations, results)
        self.assertEqual(report["total_scored_epoch_occurrences"], 7)
        self.assertEqual(report["distinct_future_epochs"], 4)
        self.assertEqual(overlap_diagnostics(observations, [])["status"], "NOT_RUN")


    def test_disjoint_horizons_score_every_future_epoch_once(self):
        # SYNTHETIC quadratic observations, no 1963 NORAD claim.
        report = run(samples())
        disjoint = report["disjoint_holdout"]
        self.assertEqual(disjoint["status"], "EVALUATED_POST_HOC")
        self.assertEqual(disjoint["available_unique_future_epochs"],
                         report["holdout_overlap"]["distinct_future_epochs"])
        self.assertEqual(disjoint["scored_unique_future_epochs"],
                         disjoint["available_unique_future_epochs"])
        epochs = [epoch for segment in disjoint["segments"]
                  for epoch in segment["future_epochs_utc"]]
        self.assertEqual(len(epochs), len(set(epochs)))
        self.assertEqual(len(epochs), disjoint["scored_unique_future_epochs"])
        self.assertLess(disjoint["pooled_rmse_rev_day"]["quadratic_529_only"], 1e-8)
        self.assertFalse(disjoint["independent_replications_established"])

    def test_disjoint_pooled_rmse_weights_epochs_not_windows_and_keeps_not_run(self):
        # SYNTHETIC four observations, each in a distinct temporal interval.
        from texugo_holdout_529 import disjoint_horizon_diagnostics
        target = [
            Observation(529, utc(timestamp), value)
            for timestamp, value in (
                ("1963-09-01T00:00:00Z", 1.0),
                ("1963-10-01T00:00:00Z", 2.0),
                ("1963-10-15T00:00:00Z", 3.0),
                ("1963-11-01T00:00:00Z", 4.0),
            )
        ]
        coefficients = {"quadratic_529_only": [0.0],
                        "shared_curvature_527_528_to_529": [5.0]}
        results = [{"cutoff_utc_end_of_day": day, "status": "TIE",
                    "coefficients": coefficients} for day in CUTOFFS]
        report = disjoint_horizon_diagnostics(target, results)
        self.assertEqual([s["future_count"] for s in report["segments"]], [1, 1, 1, 1])
        self.assertEqual(report["scored_unique_future_epochs"], 4)
        self.assertAlmostEqual(report["pooled_rmse_rev_day"]["quadratic_529_only"],
                               (30 / 4) ** 0.5)
        self.assertEqual(len({epoch for part in report["segments"]
                              for epoch in part["future_epochs_utc"]}), 4)
        results[1]["status"] = "NOT_RUN"
        incomplete = disjoint_horizon_diagnostics(target, results)
        self.assertEqual(incomplete["scored_unique_future_epochs"], 3)
        self.assertEqual(incomplete["unscored_unique_future_epochs"], 1)
        self.assertEqual(incomplete["segments"][1]["status"], "NOT_RUN")
        self.assertAlmostEqual(incomplete["pooled_rmse_rev_day"]["quadratic_529_only"],
                               (1 + 9 + 16) ** 0.5 / 3 ** 0.5)
        with self.assertRaisesRegex(ValueError, "duplicadas"):
            disjoint_horizon_diagnostics(target + [target[0]], results)
        with self.assertRaisesRegex(ValueError, "repetidos"):
            disjoint_horizon_diagnostics(target, results + [results[0]])

    def test_no_likelihood_or_geography_in_report(self):
        report = run(samples())
        self.assertTrue(report["no_probability"])
        self.assertEqual(len(report["results"]), len(CUTOFFS))
        self.assertTrue(all("holdout_rmse_rev_day" in item or item["status"] == "NOT_RUN"
                            for item in report["results"]))
        self.assertNotIn("Conde", str(report))


if __name__ == "__main__":
    unittest.main()
