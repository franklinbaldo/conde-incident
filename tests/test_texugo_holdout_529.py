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



class RollingOriginNegativeControls(unittest.TestCase):
    """All samples below are synthetic, never historical TLE observations."""

    def test_each_target_scored_once_and_simple_persistence_compared(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        s = samples()
        r = rolling_origin_diagnostics(s)
        n = sum(x.sat == 529 for x in s)
        self.assertEqual(r["status"], "EVALUATED_RETROSPECTIVE_PREQUENTIAL")
        self.assertEqual(r["candidate_targets"], n - 1)
        self.assertEqual(r["scored_distinct_targets"], n - 3)
        evaluated = [x for x in r["steps"] if x["status"] != "NOT_RUN"]
        self.assertEqual(len({x["target_epoch_utc"] for x in evaluated}), len(evaluated))
        self.assertTrue(all(x["origin_epoch_utc"] < x["target_epoch_utc"] for x in evaluated))
        self.assertTrue(all(x["horizon_days"] > 0 for x in evaluated))
        self.assertLess(r["pooled_rmse_rev_day"]["quadratic_529_only"], 1e-7)
        self.assertLess(r["pooled_rmse_rev_day"]["shared_curvature_527_528_to_529"], 1e-7)
        self.assertGreater(r["pooled_rmse_rev_day"]["persistence_529_last_epoch"], 0)
        self.assertFalse(r["independent_replications_established"])
        self.assertFalse(r["prospective_validation_established"])

    def test_mismatched_donor_curvatures_lose_to_quadratic(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        r = rolling_origin_diagnostics(samples(c527=-0.4, c528=-0.4, c529=0.4))
        self.assertLess(r["pooled_rmse_rev_day"]["quadratic_529_only"],
                        r["pooled_rmse_rev_day"]["shared_curvature_527_528_to_529"])
        self.assertGreater(r["joint_vs_quadratic_one_step_counts"]["BASELINE_BETTER"], 0)

    def test_future_target_cannot_enter_its_own_forecast(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        s = samples(c527=0.2, c528=0.4, c529=0.3)
        changed = sorted(x.epoch for x in s if x.sat == 529)[9]
        altered = [Observation(x.sat, x.epoch,
                   x.mean_motion + 3 if x.sat == 529 and x.epoch == changed
                   else x.mean_motion) for x in s]
        a, b = rolling_origin_diagnostics(s), rolling_origin_diagnostics(altered)
        early = lambda r: [x for x in r["steps"] if x["target_epoch_utc"] < changed.isoformat()]
        self.assertEqual(early(a), early(b))
        one = lambda r: next(x for x in r["steps"] if x["target_epoch_utc"] == changed.isoformat())
        self.assertEqual(one(a)["predicted_rev_day"], one(b)["predicted_rev_day"])
        self.assertNotEqual(one(a)["error_rev_day"], one(b)["error_rev_day"])

    def test_insufficient_input_and_duplicate_target_are_not_hidden(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        rows = [Observation(s, utc("1963-01-01T00:00:00Z"), 15) for s in (527, 528, 529)]
        rows.append(Observation(529, utc("1963-02-01T00:00:00Z"), 15.2))
        r = rolling_origin_diagnostics(rows)
        self.assertEqual(r["status"], "NOT_RUN")
        self.assertEqual(r["scored_distinct_targets"], 0)
        self.assertIsNone(r["pooled_rmse_rev_day"])
        self.assertEqual(r["skipped_targets"], 1)
        with self.assertRaisesRegex(ValueError, "duplicadas"):
            rolling_origin_diagnostics(rows + [rows[-1]])



class RollingTailSensitivityControls(unittest.TestCase):
    """All constructed observations/errors are SYNTHETIC, not NORAD 1963 data."""

    def test_reconstructs_paired_score_and_medians_without_extra_holdout(self):
        from texugo_holdout_529 import rolling_tail_sensitivity_diagnostics
        rolling = run(samples())["rolling_origin_holdout"]
        report = rolling_tail_sensitivity_diagnostics(rolling)
        self.assertEqual(report["status"], "EVALUATED_POST_HOC_PAIRED_DELETIONS")
        self.assertEqual(report["scored_distinct_target_epochs"],
                         rolling["scored_distinct_targets"])
        self.assertEqual(report["single_scored_target_deletion"]["evaluated"],
                         rolling["scored_distinct_targets"])
        self.assertEqual(report["forward_28_day_scored_target_block_deletion"]["calendar_anchors"],
                         rolling["scored_distinct_targets"])
        self.assertEqual(set(report["model_mae_rev_day"]),
                         set(rolling["pooled_rmse_rev_day"]))
        self.assertFalse(report["independent_replications_established"])
        self.assertFalse(report["training_refit_performed"])
        self.assertTrue(report["no_probability"])

    def test_one_extreme_target_can_flip_pairwise_rmse_and_calendar_block(self):
        # Quadratic loses pooled (one huge mistake), but wins after one target
        # is removed. The joint model wins pooled and loses in a 28-day deletion.
        from texugo_holdout_529 import rolling_tail_sensitivity_diagnostics
        values = [("1963-01-01T00:00:00Z", 10.0, 0.0),
                  ("1963-01-15T00:00:00Z", 0.0, 1.0),
                  ("1963-02-01T00:00:00Z", 0.0, 1.0),
                  ("1963-02-15T00:00:00Z", 0.0, 1.0)]
        steps = [{
            "status": "EVALUATED_RETROSPECTIVE_PREQUENTIAL",
            "target_epoch_utc": epoch, "horizon_days": 1.0,
            "error_rev_day": {
                "quadratic_529_only": base,
                "shared_curvature_527_528_to_529": joint,
                "persistence_529_last_epoch": 0.0}
        } for epoch, base, joint in values]
        rolling = {"steps": steps, "scored_distinct_targets": 4,
                   "pooled_rmse_rev_day": {
                       "quadratic_529_only": 5.0,
                       "shared_curvature_527_528_to_529": (3 / 4) ** 0.5,
                       "persistence_529_last_epoch": 0.0}}
        result = rolling_tail_sensitivity_diagnostics(rolling)
        self.assertEqual(result["original_joint_vs_quadratic"], "JOINT_BETTER")
        self.assertEqual(result["single_scored_target_deletion"]["ranking_changes"], 1)
        self.assertGreaterEqual(
            result["forward_28_day_scored_target_block_deletion"]["ranking_changes"], 1)
        self.assertEqual(result["largest_one_target_sse_fraction_by_model"]["quadratic_529_only"], 1.0)
        self.assertEqual(
            result["top_three_absolute_paired_sse_contributors"][0]["target_epoch_utc"],
            "1963-01-01T00:00:00+00:00")

    def test_not_run_and_duplicate_or_malformed_scores_fail_closed(self):
        from texugo_holdout_529 import rolling_tail_sensitivity_diagnostics
        blank = {"steps": [{"status": "NOT_RUN"}], "scored_distinct_targets": 0,
                 "pooled_rmse_rev_day": None}
        self.assertEqual(rolling_tail_sensitivity_diagnostics(blank)["status"], "NOT_RUN")
        rolling = run(samples())["rolling_origin_holdout"]
        valid = next(step for step in rolling["steps"] if step["status"] != "NOT_RUN")
        duplicate = {**rolling, "steps": [valid, valid], "scored_distinct_targets": 2}
        with self.assertRaisesRegex(ValueError, "duplicated"):
            rolling_tail_sensitivity_diagnostics(duplicate)
        broken = {**rolling, "steps": [
            {**valid, "error_rev_day": {**valid["error_rev_day"],
                 "quadratic_529_only": float("nan")}}], "scored_distinct_targets": 1}
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            rolling_tail_sensitivity_diagnostics(broken)
        malformed = {**rolling, "pooled_rmse_rev_day": {
            **rolling["pooled_rmse_rev_day"], "quadratic_529_only": 10.0}}
        with self.assertRaisesRegex(ValueError, "inconsistent pooled"):
            rolling_tail_sensitivity_diagnostics(malformed)


class RecentTrendNegativeControls(unittest.TestCase):
    """C243-T12: constructed series only; not historical observations."""

    def test_fixed_local_controls_share_targets_and_fit_exact_linear_history(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        report = rolling_origin_diagnostics(samples(c527=0.0, c528=0.0, c529=0.0))
        names = ("recency_529_two_point_secant", "recency_529_three_point_linear")
        self.assertEqual(report["recency_controls"]["past_529_epoch_counts"], [2, 3])
        self.assertTrue(report["recency_controls"]["scored_on_identical_targets"])
        self.assertEqual(report["scored_distinct_targets"],
                         sum(x["status"] != "NOT_RUN" for x in report["steps"]))
        for name in names:
            self.assertLess(report["pooled_rmse_rev_day"][name], 1e-7)
        for step in report["steps"]:
            if step["status"] != "NOT_RUN":
                self.assertTrue(all(name in step["error_rev_day"] for name in names))
                self.assertEqual(set(step["predicted_rev_day"]),
                                 set(report["pooled_rmse_rev_day"]))

    def test_target_future_cannot_enter_its_own_recent_trend_forecast(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        rows = samples(c527=0.2, c528=0.4, c529=0.3)
        when = sorted(x.epoch for x in rows if x.sat == 529)[10]
        modified = [Observation(x.sat, x.epoch, x.mean_motion + 6.0)
                    if x.sat == 529 and x.epoch == when else x for x in rows]
        old, new = rolling_origin_diagnostics(rows), rolling_origin_diagnostics(modified)
        find = lambda r: next(s for s in r["steps"]
                             if s["target_epoch_utc"] == when.isoformat())
        for model in ("recency_529_two_point_secant", "recency_529_three_point_linear"):
            self.assertEqual(find(old)["predicted_rev_day"][model],
                             find(new)["predicted_rev_day"][model])
            self.assertNotEqual(find(old)["error_rev_day"][model],
                                find(new)["error_rev_day"][model])

    def test_synthetic_change_in_slope_can_favor_recent_trend(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        base = datetime(1963, 6, 1, tzinfo=timezone.utc)
        altered = [
            Observation(o.sat, o.epoch, o.mean_motion +
                        (0.2 * max(0, (o.epoch - base).days - 120) / 60
                         if o.sat == 529 else 0))
            for o in samples(c527=0.4, c528=0.4, c529=0.0)
        ]
        report = rolling_origin_diagnostics(altered)
        self.assertLess(report["pooled_rmse_rev_day"]["recency_529_two_point_secant"],
                        report["pooled_rmse_rev_day"]["quadratic_529_only"])

    def test_synthetic_alternating_noise_can_make_secant_worse_than_persistence(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        ordered = sorted((o for o in samples() if o.sat == 529), key=lambda o: o.epoch)
        order = {o.epoch: i for i, o in enumerate(ordered)}
        altered = [Observation(o.sat, o.epoch, o.mean_motion +
                   (0.1 if order[o.epoch] % 2 == 0 else -0.1))
                   if o.sat == 529 else o for o in samples()]
        report = rolling_origin_diagnostics(altered)
        self.assertGreater(report["pooled_rmse_rev_day"]["recency_529_two_point_secant"],
                           report["pooled_rmse_rev_day"]["persistence_529_last_epoch"])

    def test_insufficient_training_stays_not_run_for_all_model_families(self):
        from texugo_holdout_529 import rolling_origin_diagnostics
        early = sorted((o for o in samples() if o.sat == 529), key=lambda o: o.epoch)[:3]
        rows = [o for o in samples() if o.sat != 529] + early
        report = rolling_origin_diagnostics(rows)
        self.assertEqual(report["status"], "NOT_RUN")
        self.assertEqual(report["scored_distinct_targets"], 0)
        self.assertIsNone(report["pooled_rmse_rev_day"])



class DonorFreeCoverageFalsifiers(unittest.TestCase):
    """C243-T13: all constructed NORAD-like observations are SYNTHETIC."""

    def test_target_only_models_score_their_own_eligible_origins(self):
        from texugo_holdout_529 import donor_free_coverage_diagnostics, rolling_origin_diagnostics
        rows = samples()
        rolling = rolling_origin_diagnostics(rows)
        audit = donor_free_coverage_diagnostics(rows, rolling)
        n = len([o for o in rows if o.sat == 529])
        self.assertEqual(audit["candidate_next_epochs"], n - 1)
        self.assertEqual(audit["target_only_scored_counts"],
                         {"persistence_529_last_epoch": n - 1,
                          "recency_529_two_point_secant": n - 2,
                          "recency_529_three_point_linear": n - 3})
        self.assertEqual(audit["joint_protocol_scored_count"],
                         rolling["scored_distinct_targets"])
        self.assertEqual(audit["on_joint_protocol_targets_rmse_rev_day"],
                         {k: rolling["pooled_rmse_rev_day"][k]
                          for k in audit["minimum_past_target_epochs"]})
        self.assertFalse(audit["uses_527_or_528"])
        self.assertTrue(audit["no_probability"])

    def test_absent_donors_do_not_censor_target_only_forecasts(self):
        from texugo_holdout_529 import donor_free_coverage_diagnostics, rolling_origin_diagnostics
        rows = [o for o in samples() if o.sat == 529] + [
            o for s in (527, 528)
            for o in sorted((x for x in samples() if x.sat == s), key=lambda x: x.epoch)[:2]]
        rolling = rolling_origin_diagnostics(rows)
        self.assertEqual(rolling["status"], "NOT_RUN")
        audit = donor_free_coverage_diagnostics(rows, rolling)
        n = len([o for o in rows if o.sat == 529])
        self.assertEqual(audit["joint_protocol_scored_count"], 0)
        self.assertEqual(audit["target_only_scored_counts"]["recency_529_three_point_linear"], n - 3)
        self.assertEqual(len(audit["additional_epochs_without_joint_protocol"]
                             ["recency_529_two_point_secant"]), n - 2)

    def test_target_value_cannot_leak_into_its_own_forecast(self):
        from texugo_holdout_529 import donor_free_coverage_diagnostics, rolling_origin_diagnostics
        rows = samples()
        when = sorted(o.epoch for o in rows if o.sat == 529)[7]
        altered = [Observation(o.sat, o.epoch, o.mean_motion + 1)
                   if o.sat == 529 and o.epoch == when else o for o in rows]
        def at_target(observations):
            result = donor_free_coverage_diagnostics(
                observations, rolling_origin_diagnostics(observations))
            return next(x for x in result["steps"] if x["target_epoch_utc"] == when.isoformat())
        before, after = at_target(rows), at_target(altered)
        for name in before["models"]:
            self.assertEqual(before["models"][name]["prediction_rev_day"],
                             after["models"][name]["prediction_rev_day"])
            self.assertNotEqual(before["models"][name]["error_rev_day"],
                                after["models"][name]["error_rev_day"])

    def test_tampered_rolling_inventory_and_duplicates_fail_closed(self):
        from texugo_holdout_529 import donor_free_coverage_diagnostics, rolling_origin_diagnostics
        rows = samples()
        rolling = rolling_origin_diagnostics(rows)
        with self.assertRaisesRegex(ValueError, "chronology mismatch"):
            donor_free_coverage_diagnostics(rows, {
                **rolling, "steps": [{**rolling["steps"][0], "target_epoch_utc": "1963-01-01T00:00:00+00:00"}]
                + rolling["steps"][1:]})
        with self.assertRaisesRegex(ValueError, "paired prediction mismatch"):
            scored = next(i for i, s in enumerate(rolling["steps"]) if s["status"] != "NOT_RUN")
            changed = [dict(s) for s in rolling["steps"]]
            changed[scored]["predicted_rev_day"] = {
                **changed[scored]["predicted_rev_day"],
                "recency_529_two_point_secant": 999.0}
            donor_free_coverage_diagnostics(rows, {**rolling, "steps": changed})
        with self.assertRaisesRegex(ValueError, "duplicate 529"):
            donor_free_coverage_diagnostics(rows + [
                next(o for o in rows if o.sat == 529)], rolling)

    def test_empty_target_returns_not_run_without_fabricating_scores(self):
        from texugo_holdout_529 import donor_free_coverage_diagnostics, rolling_origin_diagnostics
        rows = [Observation(529, utc("1963-06-01T00:00:00Z"), 14.0)]
        audit = donor_free_coverage_diagnostics(rows, rolling_origin_diagnostics(rows))
        self.assertEqual(audit["status"], "NOT_RUN")
        self.assertIsNone(audit["target_only_rmse_rev_day"]["persistence_529_last_epoch"])



if __name__ == "__main__":
    unittest.main()
