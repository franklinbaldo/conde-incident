"""NASA catalog day C197 source and two-sided temporal scenario adversarial gates."""
import copy
import json
import re
import unittest
from pathlib import Path
from tools.audit_nov8_two_sided_day import validate

ROOT=Path(__file__).resolve().parents[1]
LEDGER=json.loads((ROOT/"research/constraints/C241_nov8_two_sided_day_likelihood_2026-11-13.json").read_text())
NASA=json.loads((ROOT/"research/constraints/nasa_528_decay_precision_C197_20261113.json").read_text())

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

class BilateralDayTests(unittest.TestCase):
    def test_dedicated_replay_triggers_for_all_first_party_inputs(self):
        """A source-only PR must run this dedicated NASA-day replay, not only generic CI."""
        workflow=(ROOT/".github/workflows/c241-nov8-two-sided-date.yml").read_text()
        required={
            ".github/workflows/c241-nov8-two-sided-date.yml",
            "src/lib/catalogDayLikelihood.ts",
            "src/lib/monteCarlo.ts",
            "src/lib/constants.ts",
            "src/lib/astrodynamics.ts",
            "src/types/astrodynamics.ts",
            "src/components/MonteCarloVisualizer.tsx",
            "research/constraints/nasa_528_decay_precision_C197_20261113.json",
            "research/constraints/C241_nov8_two_sided_day_likelihood_2026-11-13.json",
            "research/statistics/C241_nov8_two_sided_day_likelihood_2026-11-13.md",
            "tests/catalogDayLikelihood.test.mjs",
            "tests/catalogDayMonteCarloIntegration.check.mjs",
            "tests/test_nov8_two_sided_day.py",
            "tools/audit_nov8_two_sided_day.py",
            "package.json",
        }
        for event in ("pull_request", "push"):
            section=re.search(r"(?ms)^  "+event+r":\n(.*?)(?=^  [a-z_]+:|^permissions:|\Z)",workflow)
            self.assertIsNotNone(section, f"missing {event} trigger")
            block=re.search(r"(?m)^    paths:\n((?:^      - [^\n]+\n)+)",section.group(1))
            self.assertIsNotNone(block, f"missing {event} path filter")
            listed={line.strip().removeprefix("- ").strip("\"'")
                    for line in block.group(1).splitlines()}
            self.assertFalse(required-listed,
                f"{event} fails to run C241 dedicated replay on source-only changes: "
                f"{sorted(required-listed)}")

    def test_source_locked_default_is_sensitivity_only(self):
        o=validate(LEDGER,NASA,read)
        self.assertEqual(o["scenario_sigmas_hours"],[6,12,24])
        self.assertIsNone(o["historical_sigma"])
        self.assertFalse(o["hard_nov9_cutoff"])
        self.assertIsNone(o["historical_Conde_impact_posterior"])

    def reject(self,which,action):
        a,b=copy.deepcopy(LEDGER),copy.deepcopy(NASA)
        action(a if which=="case" else b)
        with self.assertRaises((ValueError,KeyError,TypeError)):
            validate(a,b,read)

    def test_reject_fabricated_nasa_sigma(self):
        self.reject("case",lambda a:a["observation"].update(error_sigma_hours=6))

    def test_reject_false_impact_time(self):
        self.reject("case",lambda a:a["observation"].update(
            true_impact_utc="1963-11-08T12:00:00Z"))

    def test_reject_missing_symmetric_nov9_tail(self):
        self.reject("case",lambda a:a["calendar_label_utc_scenario"].update(
            hard_exclude_after_nov8=True))

    def test_reject_false_utc_source_assertion(self):
        self.reject("case",lambda a:a["observation"].update(
            day_label_utc_convention_verified=True))

    def test_reject_arbitrary_prior_grid(self):
        self.reject("case",lambda a:a["sensitivity_scenarios"][0].update(
            sigma_hours_assumed=3))

    def test_reject_false_probability_normalization(self):
        self.reject("case",lambda a:a["sensitivity_scenarios"][1].update(
            probability_during_8=0.9))

    def test_reject_historical_probability_activation(self):
        self.reject("case",lambda a:a["scientific_result"].update(
            historical_Conde_impact_posterior=0.12))

    def test_reject_bad_source_sha(self):
        self.reject("case",lambda a:a["observation"].update(source_sha256="0"*64))

    def test_reject_nasa_source_promoted_as_exact_date(self):
        self.reject("nasa",lambda a:a["conditional_predicate"].update(active=True))

    def test_reject_missing_consumer(self):
        self.reject("case",lambda a:a["consumers"].pop())

    def test_reject_unjustified_geographic_likelihood(self):
        self.reject("case",lambda a:a["source_to_simulation_contract"].update(
            geographic_distance_from_Conde_not_used_as_likelihood=False))

if __name__=="__main__":
    unittest.main()
