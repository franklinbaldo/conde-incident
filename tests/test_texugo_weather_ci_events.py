"""Prevent duplicate Push+PR weather runs without losing exact-HEAD checks."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github/workflows/historical-space-weather.yml",
    ROOT / ".github/workflows/igra-recife-c151.yml",
)
HEAD = r"${{ github.event.pull_request.head.sha || github.sha }}"


def event_lines(text: str, name: str) -> list[str]:
    lines = text.splitlines()
    header = f"  {name}:"
    if header not in lines:
        raise AssertionError(f"missing workflow event: {name}")
    start = lines.index(header) + 1
    stop = start
    while stop < len(lines):
        line = lines[stop]
        if line and not line.startswith("    "):
            break
        stop += 1
    return [line.strip() for line in lines[start:stop] if line.strip()]


def assert_contract(text: str) -> None:
    push = event_lines(text, "push")
    if push not in (["branches: [main]"], ["branches:", "- main"]):
        raise AssertionError(f"push must only target main: {push!r}")
    if event_lines(text, "pull_request"):
        raise AssertionError("pull_request must be unfiltered")
    if f"ref: {HEAD}" not in text:
        raise AssertionError("checkout must pin the literal source HEAD")
    if "persist-credentials: false" not in text:
        raise AssertionError("checkout must not retain credentials")
    if "git rev-parse HEAD" not in text or f"EXPECTED_SHA: {HEAD}" not in text:
        raise AssertionError("exact-HEAD comparison required")
    if "test_texugo_weather_ci_events.py' -v" not in text:
        raise AssertionError("policy regression must run in the workflow")


class WeatherCIEventPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow_text = [path.read_text(encoding="utf-8") for path in WORKFLOWS]

    def test_both_jobs_are_deduplicated_and_sha_pinned(self):
        for path, text in zip(WORKFLOWS, self.workflow_text):
            with self.subTest(workflow=path.name):
                assert_contract(text)

    def test_branch_push_duplication_is_rejected(self):
        for path, text in zip(WORKFLOWS, self.workflow_text):
            bad = text.replace("branches: [main]", "branches:\n      - main\n      - 'lagarto/**'", 1)
            with self.subTest(workflow=path.name), self.assertRaisesRegex(AssertionError, "push must only target main"):
                assert_contract(bad)

    def test_removed_main_or_pr_would_fail(self):
        for path, text in zip(WORKFLOWS, self.workflow_text):
            for bad in (
                text.replace("branches: [main]", "branches: [lagarto]", 1),
                text.replace("  pull_request:", "  # pull_request:", 1),
            ):
                with self.subTest(workflow=path.name), self.assertRaises(AssertionError):
                    assert_contract(bad)

    def test_missing_exact_head_or_test_step_fails(self):
        for path, text in zip(WORKFLOWS, self.workflow_text):
            for bad in (
                text.replace(f"ref: {HEAD}", "ref: main", 1),
                text.replace("persist-credentials: false", "persist-credentials: true", 1),
                text.replace("git rev-parse HEAD", "git rev-parse main", 1),
                text.replace("test_texugo_weather_ci_events.py' -v", "echo skipped", 1),
            ):
                with self.subTest(workflow=path.name), self.assertRaises(AssertionError):
                    assert_contract(bad)


if __name__ == "__main__":
    unittest.main()
