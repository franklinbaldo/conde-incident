"""G72: fail-closed proof that the STL epoch bridge runs on source-only edits."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/c241-stl-unit-crosscheck-r53.yml"
REQUIRED = (
    "research/tle_custody/stl_space_log_nasa_r51.json",
    "research/statistics/C241_stl_printed_pair_coherence.json",
    "public/data/conde-stl-mile-subtype-bridge.json",
    "public/data/conde-stl-space-log-dependency-bridge.json",
    "public/data/conde-soviet-nasa-dependency-bridge.json",
    "public/data/conde-stl-epoch-independence-bridge.json",
    "research/tle_custody/stl_unit_crosscheck_C241_LONTRA_R53.json",
    "research/tle_custody/soviet_nasa_crosswalk_C241_LONTRA_R49.json",
    "research/tle_custody/soviet_bse1964_1963_003_C241_LONTRA_R48.json",
    "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json",
    "tools/audit_stl_space_log_r51.py",
    "tools/audit_stl_unit_crosscheck_r53.py",
    "tools/audit_soviet_nasa_crosswalk_r49.py",
    "tools/export_soviet_nasa_dependency_bridge.py",
    "tools/export_stl_r51_dependency_bridge.py",
    "tools/export_stl_mile_subtype_bridge.py",
    "tools/export_stl_epoch_independence_bridge.py",
    "tests/test_stl_epoch_independence_bridge.py",
    "tests/test_gaviao_g72_stl_epoch_gate.py",
)
SCRIPT = (
    "set -euo pipefail\n"
    "python3 -m unittest discover -s tests -p test_stl_epoch_independence_bridge.py -v\n"
    "python3 -O -m unittest discover -s tests -p test_stl_epoch_independence_bridge.py -v\n"
    "python3 -m unittest discover -s tests -p test_gaviao_g72_stl_epoch_gate.py -v\n"
    "python3 tools/export_stl_epoch_independence_bridge.py --check-site\n"
)


def event_block(source: str, event: str) -> tuple[int, int, str]:
    match = re.search(r"(?m)^  " + re.escape(event) + r":\s*$", source)
    if match is None:
        raise AssertionError("missing event: " + event)
    following = re.search(r"(?m)^  (?:pull_request|push|workflow_dispatch):\s*$", source[match.end():])
    end = match.end() + following.start() if following else source.find("\npermissions:", match.end())
    if end < 0:
        raise AssertionError("event block terminator missing: " + event)
    return match.start(), end, source[match.start():end]


def verify(source: str) -> None:
    if re.search(r"(?m)^(?:defaults:|    defaults:)\s*$", source):
        raise AssertionError("custom shell defaults can bypass scripts")
    for event in ("pull_request", "push"):
        _, _, block = event_block(source, event)
        if "    paths-ignore:" in block:
            raise AssertionError("unexpected paths-ignore")
        match = re.search(r"(?m)^    paths:\s*$", block)
        if match is None:
            raise AssertionError("missing path selection: " + event)
        actual = re.findall(r"(?m)^      - ([^\s#]+)\s*$", block[match.end():])
        if len(actual) != len(set(actual)):
            raise AssertionError("duplicate trigger paths: " + event)
        if not set(REQUIRED).issubset(actual):
            raise AssertionError(event + " is missing " + repr(set(REQUIRED) - set(actual)))
    step = re.search(
        r"(?m)^      - name: Check STL epoch bridge without sensor promotion\n"
        r"        run: \|\n((?:          [^\n]*\n)+)",
        source,
    )
    if step is None:
        raise AssertionError("missing mandatory replay step")
    body = "".join(line[10:] for line in step.group(1).splitlines(keepends=True))
    if body != SCRIPT:
        raise AssertionError("mandatory step changed, skipped or reordered")
    after = source[step.end():]
    until_next = after.split("\n      - name:", 1)[0]
    if re.search(r"(?m)^        (?:if:|shell:|continue-on-error:)", until_next):
        raise AssertionError("replay step could be skipped or tolerated")
    if "if: false" in source or "continue-on-error: true" in source:
        raise AssertionError("replay may be skipped or tolerated")


class GateG72(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = WORKFLOW.read_text(encoding="utf-8")

    def test_selected_and_executed(self):
        verify(self.original)

    def test_each_source_only_trigger_is_indispensable(self):
        for event in ("pull_request", "push"):
            for path in REQUIRED:
                with self.subTest(event=event, path=path):
                    start, end, block = event_block(self.original, event)
                    line = "      - " + path + "\n"
                    self.assertIn(line, block)
                    mutant = self.original[:start] + block.replace(line, "", 1) + self.original[end:]
                    with self.assertRaises(AssertionError):
                        verify(mutant)

    def test_replay_command_and_guard_mutants_rejected(self):
        for line in SCRIPT.splitlines()[1:]:
            with self.subTest(line=line):
                mutant = self.original.replace("          " + line + "\n", "          echo bypass\n", 1)
                with self.assertRaises(AssertionError):
                    verify(mutant)
        for snippet in ("        continue-on-error: true\n", "        if: false\n"):
            with self.subTest(snippet=snippet):
                mutant = self.original.replace("        run: |\n", snippet + "        run: |\n", 1)
                with self.assertRaises(AssertionError):
                    verify(mutant)


if __name__ == "__main__":
    unittest.main()
