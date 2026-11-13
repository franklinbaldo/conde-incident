"""C241-P9: adversarial tests for three NASA printed-period intervals."""
import copy
import json
from pathlib import Path
import unittest

from formal.scripts.compile_ssr_three_editions import compile_report, render_lean

ROOT = Path(__file__).resolve().parents[2]
APR, AUG, OCT = [
    json.loads((ROOT / p).read_text()) for p in (
        "research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json",
        "research/tle_custody/nasa_ssr_aug15_1963_C241-L17.json",
        "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json",
    )
]


class TestThreeEditions(unittest.TestCase):
    def test_strict_ranking_only_of_printed_fields(self):
        r = compile_report(APR, AUG, OCT)
        self.assertEqual(
            [x["apr_minus_aug"] for x in r["objects"]],
            [[-10, 10], [70, 90], [40, 60]],
        )
        self.assertEqual(
            [x["aug_minus_oct"] for x in r["objects"]],
            [[-10, 10], [80, 100], [40, 60]],
        )
        self.assertEqual(
            [x["apr_minus_oct_shared_aug_eliminated"] for x in r["objects"]],
            [[-10, 10], [160, 180], [90, 110]],
        )
        self.assertTrue(all(r["conditional_robust_printed_rank"].values()))
        self.assertEqual(r["physical_domain_change"], "NONE")
        self.assertTrue(all(x["instrumental_epochs_utc"] is None
                            and x["physical_decay_rate"] is None
                            for x in r["objects"]))
        self.assertIn("period_b_three_printings", render_lean(r))
        self.assertIn("printed_aug_oct_b_gt_c", render_lean(r))

    def test_august_mutation_fails_closed(self):
        for i in range(3):
            altered = copy.deepcopy(AUG)
            altered["rows"][i]["nodal_period_min"] = "99.9"
            with self.subTest(row=i), self.assertRaises(ValueError):
                compile_report(APR, altered, OCT)

    def test_unwarranted_august_epoch_and_error_fail_closed(self):
        for key, value in (
            ("publication_date_is_element_epoch", True),
            ("rate_from_publication_interval", True),
            ("measurement_sigma", 0.01),
            ("terminal_time", "1963-11-08T00:00Z"),
        ):
            altered = copy.deepcopy(AUG)
            altered["limits"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compile_report(APR, altered, OCT)

    def test_publication_identity_and_hash_mutations_fail_closed(self):
        for field, value in (("sha256", "0" * 64), ("data_as_of", "1200Z AUG 14 1963")):
            altered = copy.deepcopy(AUG)
            altered["source"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                compile_report(APR, altered, OCT)

    def test_lean_artifact_not_uncoupled_from_json(self):
        source = ROOT / "research/constraints/C241-P9_ssr_three_edition_intervals.json"
        generated = ROOT / "formal/Conde1963/SsrThreeEditions.lean"
        self.assertEqual(json.loads(source.read_text()), compile_report(APR, AUG, OCT))
        self.assertEqual(generated.read_text(), render_lean(compile_report(APR, AUG, OCT)))


if __name__ == "__main__":
    unittest.main()
