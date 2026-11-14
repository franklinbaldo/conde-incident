"""Independent CI contract for SHA-pinned orbital-plane artifact replay.

An existing green YAML does not prove a source-only change will trigger the gate.
The contract includes adversarial omissions in both PR and main-push filters.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/c241-conditional-plane-windows.yml"
sys.path.insert(0, str(ROOT / "tools"))
from c241_637_regime_holdout import SOURCE_SHA256, SOURCE_URL  # noqa: E402

REQUIRED_PATHS = (
    ".github/workflows/c241-conditional-plane-windows.yml",
    "tools/c241_conditional_plane_windows.py",
    "tools/c241_637_regime_holdout.py",
    "tests/test_c241_conditional_plane_windows.py",
    "tests/test_c241_plane_replay_workflow.py",
    "research/geo/cgeo15_vila_matriz_2022_camera_points.json",
    "research/geo/conde_ibge_2022_sirgas2000.json",
    "research/geo/cgeo20_centro_vila_2020.json",
    "research/statistics/C241_CONDITIONAL_PLANE_WINDOWS_20261114.md",
    "research/statistics/c241_plane_*.json",
)
TEST_PATTERN = "test_c241_conditional_plane_windows.py"
POLICY_PATTERN = "test_c241_plane_replay_workflow.py"
REPLAY = (
    'python3 tools/c241_conditional_plane_windows.py --parquet '
    '"$RUNNER_TEMP/tle_1963.parquet" --repo . '
    '--output-dir research/statistics --check'
)


def validate(text: str) -> None:
    """Refuse a gate that can go green without a source, test or byte replay."""
    for event in ("pull_request", "push"):
        match = re.search(
            rf"(?ms)^  {event}:\n(.*?)(?=^  (?:pull_request|push|workflow_dispatch):|^permissions:)",
            text,
        )
        if match is None or "    paths:\n" not in match.group(1):
            raise ValueError(f"{event}: missing path filter")
        paths = set(re.findall(r"(?m)^      - '([^']+)'$", match.group(1)))
        for path in REQUIRED_PATHS:
            if path not in paths:
                raise ValueError(f"{event}: missing trigger {path}")
    if "    branches: [main]" not in text:
        raise ValueError("missing main push")
    sha = '${{ github.event.pull_request.head.sha || github.sha }}'
    if text.count(sha) < 2 or 'test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"' not in text:
        raise ValueError("missing exact checkout evidence")
    if "persist-credentials: false" not in text:
        raise ValueError("checkout credentials persist")
    for pattern in (TEST_PATTERN, POLICY_PATTERN):
        for command in (
            f"python3 -m unittest discover -s tests -p '{pattern}' -v",
            f"python3 -O -m unittest discover -s tests -p '{pattern}' -v",
        ):
            if not re.search(r"(?m)^          " + re.escape(command) + r"$", text):
                raise ValueError("missing actual normal/-O test " + command)
    if SOURCE_URL not in text or SOURCE_SHA256 not in text:
        raise ValueError("source not pinned to imported digest/url")
    if not re.search(r"(?m)^          echo '[0-9a-f]{64}' .* \| sha256sum -c -$", text):
        raise ValueError("missing actual original-bytes SHA gate")
    if not re.search(r"(?m)^          " + re.escape(REPLAY) + r"$", text):
        raise ValueError("no byte-for-byte check of all tracked outputs")
    for bypass in ("continue-on-error: true", "|| true", "exit 0", "if: false"):
        if bypass in text:
            raise ValueError("workflow bypass " + bypass)


class ReplayWorkflowContract(unittest.TestCase):
    def test_positive(self):
        validate(WORKFLOW.read_text(encoding="utf-8"))

    def test_source_only_mutants_both_events(self):
        original = WORKFLOW.read_text(encoding="utf-8")
        for path in REQUIRED_PATHS:
            entry = f"      - '{path}'\n"
            self.assertEqual(original.count(entry), 2, path)
            for occurrence in (0, 1):
                with self.subTest(path=path, event=occurrence):
                    start = (original.find(entry) if occurrence == 0 else original.rfind(entry))
                    mutated = original[:start] + original[start + len(entry):]
                    with self.assertRaisesRegex(ValueError, "missing trigger"):
                        validate(mutated)

    def test_missing_execution_and_false_green_mutants(self):
        original = WORKFLOW.read_text(encoding="utf-8")
        for old, new in (
            (REPLAY, "echo skipped replay"),
            ("sha256sum -c -", "cat"),
            ("python3 -O -m unittest discover -s tests -p '" + TEST_PATTERN + "' -v", "echo skipped"),
            ("python3 -m unittest discover -s tests -p '" + POLICY_PATTERN + "' -v", "echo skipped"),
            ("persist-credentials: false", "persist-credentials: true"),
            ("    branches: [main]", "    branches: [preview]"),
        ):
            with self.subTest(mutant=old):
                self.assertIn(old, original)
                with self.assertRaises(ValueError):
                    validate(original.replace(old, new, 1))
        for bypass in ("|| true", "continue-on-error: true"):
            with self.subTest(bypass=bypass):
                with self.assertRaisesRegex(ValueError, "bypass"):
                    validate(original + "\n" + bypass)


if __name__ == "__main__":
    unittest.main()
