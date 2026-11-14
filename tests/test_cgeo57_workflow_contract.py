"""CGEO-57: independent guard for source-only events and actual live replay.

No dependency on PyYAML's YAML 1.1 "on" implicit boolean coercion.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/cgeo57-nara-temporal.yml"
PARENT = "research/geo/cgeo56_nara_sortie_cross_square.json"
REQUIRED = {
    PARENT,
    "research/geo/cgeo57_nara_overlay_preparation_dates.json",
    "research/geo/CGEO57_NARA_1956_PREPARATION_DATES.md",
    "tools/cgeo57_nara_temporal.py",
    "tests/test_cgeo57_nara_temporal.py",
    "tests/test_cgeo57_workflow_contract.py",
    ".github/workflows/cgeo57-nara-temporal.yml",
}


def check(doc: str) -> None:
    for event in ("pull_request", "push"):
        match = re.search(
            rf"(?ms)^  {event}:\n(.*?)(?=^  (?:pull_request|push):|^permissions:)",
            doc,
        )
        if not match:
            raise ValueError(f"missing {event}")
        path_section = re.search(r"(?m)^    paths:\n((?:      - .*\n)+)", match.group(1))
        if not path_section:
            raise ValueError(f"missing paths in {event}")
        actual = set(re.findall(r"(?m)^      - '([^']+)'$", path_section.group(1)))
        missing = REQUIRED - actual
        if missing:
            raise ValueError(f"{event} source-only paths not covered: {sorted(missing)}")
    expected_commands = (
        "python3 tools/cgeo57_nara_temporal.py",
        "python3 -m unittest discover -s tests -p 'test_cgeo57_nara_temporal.py' -v",
        "python3 -O -m unittest discover -s tests -p 'test_cgeo57_nara_temporal.py' -v",
        "python3 -m unittest discover -s tests -p 'test_cgeo57_workflow_contract.py' -v",
        "python3 -O -m unittest discover -s tests -p 'test_cgeo57_workflow_contract.py' -v",
    )
    actual_step = re.search(
        r"(?m)^      - name: Validate lineage and adversarial tests\n"
        r"        run: \|\n((?:          .*\n)+)",
        doc,
    )
    if not actual_step or tuple(
        line.strip() for line in actual_step.group(1).splitlines()
    ) != expected_commands:
        raise ValueError("CGEO-57 validation commands not reachable and exact")
    live_step = (
        "      - name: Live NARA four-JPEG source replay\n"
        "        run: python3 tools/cgeo57_nara_temporal.py --live\n"
    )
    if live_step not in doc:
        raise ValueError("CGEO-57 four-JPEG live replay not mandatory")



class TestCgeo57Workflow(unittest.TestCase):
    def setUp(self):
        self.doc = WORKFLOW.read_text(encoding="utf-8")

    def test_baseline(self):
        check(self.doc)

    def test_source_only_mutants(self):
        for event in ("pull_request", "push"):
            section = self.doc.split(f"  {event}:\n", 1)[1].split(
                "  push:\n" if event == "pull_request" else "permissions:", 1
            )[0]
            self.assertIn(f"      - '{PARENT}'", section)
            mutant = self.doc.replace(section, section.replace(f"      - '{PARENT}'\n", ""))
            with self.subTest(event=event), self.assertRaises(ValueError):
                check(mutant)

    def test_noop_live_replay_mutant(self):
        original = "run: python3 tools/cgeo57_nara_temporal.py --live"
        self.assertIn(original, self.doc)
        with self.assertRaises(ValueError):
            check(self.doc.replace(original, "run: echo skipped"))

    def test_early_exit_mutant(self):
        target = "          python3 tools/cgeo57_nara_temporal.py\n"
        self.assertIn(target, self.doc)
        mutant = self.doc.replace(target, "          exit 0\n"+target, 1)
        with self.assertRaises(ValueError):
            check(mutant)

    def test_missing_optimized_test_mutant(self):
        original = "          python3 -O -m unittest discover -s tests -p 'test_cgeo57_nara_temporal.py' -v"
        self.assertIn(original, self.doc)
        with self.assertRaises(ValueError):
            check(self.doc.replace(original, "          echo skipping optimized tests"))


if __name__ == "__main__":
    unittest.main()
