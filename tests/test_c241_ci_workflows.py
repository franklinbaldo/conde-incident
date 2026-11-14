"""CI trigger and source-byte replay contracts for both C241 catalogue holdouts.

A synthetic source-only change must select the specialized workflow.
The SHA test uses tiny local bytes, never historical orbits.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WF_12 = ROOT / ".github/workflows/c241-12day-secondary-holdout.yml"
WF_637 = ROOT / ".github/workflows/c241-637-regime-holdout.yml"
HISTORICAL_PARQUET_SHA = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"


def paths_for(workflow: str, event: str) -> set[str]:
    """Extract one simple YAML event paths block without a YAML dependency."""
    lines = workflow.splitlines()
    head = "  " + event + ":"
    if head not in lines:
        raise AssertionError(f"{event} must be a top-level workflow event")
    start = lines.index(head) + 1
    paths = set()
    inside = False
    for line in lines[start:]:
        if not line or line.startswith("#"):
            continue
        if not line.startswith("  ") or (line.startswith("  ") and not line.startswith("    ")):
            break
        if line == "    paths:":
            inside = True
        elif inside and line.startswith("      - "):
            paths.add(line.removeprefix("      - ").strip().strip("'\""))
        elif inside and line.startswith("    "):
            break
    if not paths:
        raise AssertionError(f"{event} missing nonempty paths filter")
    return paths


class C241ReplayWorkflowContracts(unittest.TestCase):
    def test_source_only_changes_trigger_12day_replay_in_both_events(self):
        wf = WF_12.read_text("utf-8")
        needed = {
            "tools/c241_12day_secondary_holdout.py",
            "tools/tle_secondary_1963_ledger.py",
            "research/tle_custody/mirror_528_1963-10-27.tle",
            "research/statistics/c241_12day_secondary_holdout_20261114.json",
        }
        for event in ("pull_request", "push"):
            with self.subTest(event=event):
                self.assertFalse(needed - paths_for(wf, event),
                                 f"{event} does not trigger source-only replay")

    def test_637_replay_has_pr_and_main_push_triggers(self):
        wf = WF_637.read_text("utf-8")
        needed = {
            "tools/c241_637_regime_holdout.py",
            "tests/test_c241_637_regime_holdout.py",
            "research/statistics/c241_637_regime_holdout_20261114.json",
        }
        for event in ("pull_request", "push"):
            with self.subTest(event=event):
                self.assertFalse(needed - paths_for(wf, event))
        self.assertIn("    branches: [main]", wf)

    def test_637_digest_shell_line_accepts_real_bytes_and_rejects_mutation(self):
        wf = WF_637.read_text("utf-8")
        commands = [line.strip() for line in wf.splitlines() if "| sha256sum -c -" in line]
        self.assertEqual(len(commands), 1, "missing or ambiguous SHA validation command")
        shell = commands[0]
        self.assertIn(HISTORICAL_PARQUET_SHA, shell)
        self.assertIn("$RUNNER_TEMP/tle_1963.parquet", shell)
        parsed = subprocess.run(["bash", "-n"], input=shell + "\n", text=True,
                                capture_output=True, check=False)
        self.assertEqual(parsed.returncode, 0, parsed.stderr)
        fixture = b"SYNTHETIC_BLOB_FOR_SHA_GATE_ONLY"
        synthetic_hash = hashlib.sha256(fixture).hexdigest()
        command = shell.replace(HISTORICAL_PARQUET_SHA, synthetic_hash)
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "tle_1963.parquet"
            archive.write_bytes(fixture)
            env = {**os.environ, "RUNNER_TEMP": directory}
            def verify():
                return subprocess.run(["bash", "-e", "-u", "-o", "pipefail", "-c", command],
                                      env=env, capture_output=True, text=True, check=False)
            good = verify()
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            archive.write_bytes(fixture + b"tampered")
            bad = verify()
            self.assertNotEqual(bad.returncode, 0, "altered binary passed SHA replay")


if __name__ == "__main__":
    unittest.main()
