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
REQUIRED_SMOKE_ENTRYPOINTS = (
    "tests/ui_keyboard_smoke.mjs",
    "tests/ui_mobile_sections_smoke.mjs",
    "tests/ui_documentary_archive_smoke.mjs",
    "tests/ui_map_reflow_smoke.mjs",
    "tests/ui_montecarlo_reflow_smoke.mjs",
    "tests/ui_lab_chunk_failure_smoke.mjs",
    "tests/lab_python_export_failure_smoke.mjs",
    "tests/ui_python_modal_touch_smoke.mjs",
    "tests/caderno_reflow_smoke.mjs",
    "tests/ssg_search_dialog_smoke.mjs",
    "tests/ssg_mobile_heading_smoke.mjs",
    "tests/editorial_journey_smoke.mjs",
    "tests/ssg_simulacoes_bridge_smoke.mjs",
    "tests/ssg_tle_syntax_smoke.mjs",
    "tests/ssg_tle_code_scroll_smoke.mjs",
    "tests/ssg_source_lookup_smoke.mjs",
)

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
    missing_steps = sorted(set(REQUIRED_SMOKE_ENTRYPOINTS) - set(executed))
    if missing_steps:
        raise AssertionError(f"mandatory browser smoke executions missing: {missing_steps}")
    duplicates = sorted(path for path in REQUIRED_SMOKE_ENTRYPOINTS if executed.count(path) != 1)
    if duplicates:
        raise AssertionError(f"mandatory smoke executions must occur once: {duplicates}")
    # A successful workflow with a skipped or tolerated browser step is not a gate.
    for block in re.split(r"(?m)^      - (?=(?:name|uses):)", text):
        run = re.search(r"(?m)^        run: node (tests/[\w./-]+\.mjs)\s*$", block)
        if not run or run.group(1) not in REQUIRED_SMOKE_ENTRYPOINTS:
            continue
        if re.search(r"(?m)^        (?:if|continue-on-error|shell):", block):
            raise AssertionError(f"mandatory browser smoke step is conditional or tolerant: {run.group(1)}")
    job_header = text.partition("    steps:")[0]
    if re.search(r"(?m)^    (?:if|continue-on-error):", job_header):
        raise AssertionError("browser smoke job must not be conditional or tolerant")
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


    def test_required_browser_command_cannot_be_replaced_by_noop(self):
        original = WORKFLOW.read_text()
        needle = "        run: node tests/ui_keyboard_smoke.mjs"
        self.assertIn(needle, original)
        mutated = original.replace(needle, "        run: echo skipped keyboard smoke", 1)
        with self.assertRaisesRegex(AssertionError, "mandatory browser smoke executions missing"):
            assert_covered(mutated)

    def test_required_browser_command_cannot_ignore_failure(self):
        original = WORKFLOW.read_text()
        needle = "        run: node tests/ui_keyboard_smoke.mjs"
        self.assertIn(needle, original)
        mutated = original.replace(needle, "        continue-on-error: true\n" + needle, 1)
        with self.assertRaisesRegex(AssertionError, "conditional or tolerant"):
            assert_covered(mutated)

    def test_required_browser_command_cannot_be_skipped_by_condition(self):
        original = WORKFLOW.read_text()
        needle = "        run: node tests/ui_keyboard_smoke.mjs"
        self.assertIn(needle, original)
        mutated = original.replace(needle, "        if: false\n" + needle, 1)
        with self.assertRaisesRegex(AssertionError, "conditional or tolerant"):
            assert_covered(mutated)

    def test_job_level_if_false_is_rejected(self):
        original = WORKFLOW.read_text()
        needle = "  ui-keyboard:\n    runs-on: ubuntu-24.04"
        self.assertIn(needle, original)
        mutated = original.replace(needle, "  ui-keyboard:\n    if: false\n    runs-on: ubuntu-24.04", 1)
        with self.assertRaisesRegex(AssertionError, "job must not be conditional"):
            assert_covered(mutated)


if __name__ == "__main__":
    unittest.main()

