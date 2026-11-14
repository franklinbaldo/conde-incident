"""Contract for the UI Chromium smoke test's source-only event coverage.

The browser tests may pass on a PR yet silently not run if their own source
changes or when a selected UI change is merged. This is a structural contract,
not a claim that browser assertions themselves were executed.
"""
from __future__ import annotations

import fnmatch
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ui-keyboard-smoke.yml"
REQUIRED_INPUTS = (
    ".github/workflows/ui-keyboard-smoke.yml",
    "tests/test_ui_keyboard_trigger_contract.py",
    "scripts/prepare-ssg.mjs",
    "scripts/enable-article-frames.mjs",
    "ssg.toml",
)


def event_paths(text: str, event: str) -> tuple[str, ...]:
    """Parse a deliberately small event.paths subset of the workflow."""
    match = re.search(r"(?m)^  " + re.escape(event) + r":\s*$", text)
    if not match:
        raise AssertionError(f"{event} is absent")
    tail = text[match.end() :]
    next_event = re.search(r"(?m)^  [a-z_]+:", tail)
    block = tail[: next_event.start()] if next_event else tail
    if event == "push" and not re.search(r"(?m)^    branches:\s*\[main\]", block):
        raise AssertionError("push must target main")
    if not re.search(r"(?m)^    paths:\s*$", block):
        raise AssertionError(f"{event}.paths is absent")
    return tuple(re.findall(r"(?m)^      - '([^']+)'\s*$", block))


def required_paths(text: str) -> set[str]:
    # Extract only actual node tests/...mjs calls in YAML run steps.
    # Tests mentioned solely in event filters must not satisfy discovery.
    executed = re.findall(r"(?m)^        run:\s*node\s+(?:--test\s+)?(tests/[\w./-]+\.mjs)\s*$", text)
    if not executed:
        raise AssertionError("no browser smoke entrypoints found")
    return set(executed) | set(REQUIRED_INPUTS)


def assert_covered(text: str) -> None:
    expected = required_paths(text)
    for event in ("pull_request", "push"):
        patterns = event_paths(text, event)
        missing = sorted(
            path for path in expected
            if not any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)
        )
        if missing:
            raise AssertionError(f"{event}: source-only changes not covered: {missing}")


class UIKeyboardTriggerContractTest(unittest.TestCase):
    def test_all_smoke_entrypoints_and_direct_inputs_trigger_on_pr_and_main(self):
        assert_covered(WORKFLOW.read_text())

    def test_missing_push_is_rejected(self):
        original = WORKFLOW.read_text()
        mutated = original.replace("  push:\n    branches: [main]\n", "  obsolete_push:\n    branches: [main]\n", 1)
        self.assertNotEqual(mutated, original)
        with self.assertRaisesRegex(AssertionError, "push is absent"):
            assert_covered(mutated)

    def test_source_only_mutation_is_rejected(self):
        original = WORKFLOW.read_text()
        needle = "      - 'tests/ssg_mobile_heading_smoke.mjs'\n"
        self.assertIn(needle, original)
        mutated = original.replace(needle, "", 1)
        with self.assertRaisesRegex(AssertionError, "source-only changes"):
            assert_covered(mutated)


if __name__ == "__main__":
    unittest.main()
