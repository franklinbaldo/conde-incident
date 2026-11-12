"""Regression checks for the C241-T15 CI trigger footprint (no network)."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/texugo-quadratic-raan.yml"
# Runtime inputs, first-party dependencies, and exercised test suites.
MUST_TRIGGER = {
    ".github/workflows/texugo-quadratic-raan.yml",
    "formal/scripts/audit_secondary_j2_raan.py",
    "research/statistics/raan_527_528_529_1963.json",
    "research/statistics/raan_chronological_holdout_1963.json",
    "research/tle_custody/mirror_528_1963-10-27.tle",
    "tests/test_raan_frozen_j2_holdout.py",
    "tests/test_raan_frozen_trend_holdout.py",
    "tests/test_texugo_quadratic_raan_ablation.py",
    "tools/cross_object_epoch_support.py",
    "tools/raan_chronological_holdout.py",
    "tools/raan_coepoch_audit.py",
    "tools/raan_frozen_j2_holdout.py",
    "tools/raan_frozen_trend_holdout.py",
    "tools/texugo_quadratic_raan_ablation.py",
    "tools/tle_secondary_1963_ledger.py",
}


def event_block(lines: list[str], event: str) -> list[str]:
    header = "  " + event + ":"
    if header not in lines:
        raise AssertionError(f"missing {event} event")
    start = lines.index(header) + 1
    stop = start
    while stop < len(lines) and (lines[stop].startswith("    ") or not lines[stop].strip()):
        stop += 1
    return lines[start:stop]


def watched_paths(block: list[str]) -> set[str]:
    if "    paths:" not in block:
        raise AssertionError("unscoped event creates redundant runs")
    return {row.strip()[2:] for row in block if row.startswith("      - ")}


class TriggerScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lines = WORKFLOW.read_text(encoding="utf-8").splitlines()

    def test_pr_and_main_push_use_same_input_footprint(self):
        pull = watched_paths(event_block(self.lines, "pull_request"))
        push = watched_paths(event_block(self.lines, "push"))
        self.assertEqual(pull, push)
        self.assertTrue(MUST_TRIGGER <= push, sorted(MUST_TRIGGER - push))

    def test_unrelated_ui_changes_do_not_download_scientific_parquet(self):
        push = watched_paths(event_block(self.lines, "push"))
        self.assertNotIn("src/main.tsx", push)
        self.assertNotIn("src/components/Navigation.tsx", push)

    def test_manual_replay_and_exact_head_are_preserved(self):
        text = "\n".join(self.lines)
        self.assertIn("  workflow_dispatch:", text)
        self.assertIn("    branches: [main]", text)
        self.assertIn("EXPECTED_SHA:", text)
        self.assertIn('git rev-parse HEAD', text)
        self.assertIn("test_texugo_ci_trigger_paths.py -v", text)


if __name__ == "__main__":
    unittest.main()
