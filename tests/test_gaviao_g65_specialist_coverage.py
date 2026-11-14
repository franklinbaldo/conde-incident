"""G65: ensure documentary replays run when their direct source changes.

The controls verify YAML's top-level selectors, not incidental text in jobs.
They do not pretend to execute GitHub Actions or authenticate primary sources.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SHARED = 'tests/test_gaviao_g65_specialist_coverage.py'
CHECKS = {
    '.github/workflows/c241-stl-pair-coherence.yml': {
        'research/tle_custody/stl_space_log_nasa_r51.json',
        'tools/audit_stl_space_log_r51.py',
        'tests/test_stl_space_log_r51.py',
        'tools/stl_printed_pair_coherence_C241.py',
        'tests/test_stl_printed_pair_coherence_C241.py',
        SHARED,
    },
    '.github/workflows/cgeo49-nara-headers.yml': {
        'research/geo/cgeo47_nara_m1765_conde_pre1963.json',
        'research/geo/cgeo49_nara_header_crosssheet.json',
        'tools/cgeo49_nara_headers.py',
        'tests/test_cgeo49_nara_headers.py',
        SHARED,
    },
}


def paths_for(source: str, event: str) -> set[str]:
    """Read top-level `on.<event>.paths`; an event mentioned elsewhere is inert."""
    found = set()
    selected = in_paths = False
    for line in source.splitlines():
        if line.startswith('  ') and not line.startswith('    '):
            selected = line.strip() == event + ':'
            in_paths = False
        elif selected and line == '    paths:':
            in_paths = True
        elif selected and in_paths and line.startswith('      - '):
            found.add(line[8:].strip().strip("'\""))
        elif selected and in_paths and not line.startswith('      '):
            in_paths = False
    return found


def check(source: str, workflow: str) -> None:
    required = CHECKS[workflow]
    for event in ('pull_request', 'push'):
        missing = required - paths_for(source, event)
        if missing:
            raise AssertionError(f'{workflow} {event}: missing {sorted(missing)}')
    command = "python3 -m unittest discover -s tests -p 'test_gaviao_g65_specialist_coverage.py' -v"
    if command not in source:
        raise AssertionError(f'{workflow}: G65 regression not executed')


class SpecializedWorkflowCoverage(unittest.TestCase):
    def test_source_only_paths_and_execution(self):
        for workflow in CHECKS:
            with self.subTest(workflow=workflow):
                check((ROOT / workflow).read_text(), workflow)

    def test_single_path_mutants_fail_for_both_events(self):
        for workflow, required in CHECKS.items():
            source = (ROOT / workflow).read_text()
            check(source, workflow)
            for event in ('pull_request', 'push'):
                before, event_and_after = source.split(f'  {event}:', 1)
                for path in required:
                    # Restrict mutation to the selected YAML event block.
                    lines = event_and_after.splitlines(keepends=True)
                    boundary = next((i for i, line in enumerate(lines)
                                     if line.startswith("  ") and not line.startswith("    ")), len(lines))
                    positions = [i for i, line in enumerate(lines[:boundary])
                                 if line.strip().strip('- ').strip("'\"") == path]
                    self.assertEqual(len(positions), 1, (workflow, event, path))
                    del lines[positions[0]]
                    mutated = before + f'  {event}:' + ''.join(lines)
                    with self.subTest(workflow=workflow, event=event, path=path):
                        with self.assertRaisesRegex(AssertionError, event):
                            check(mutated, workflow)

    def test_suppressing_required_regression_fails(self):
        for workflow in CHECKS:
            source = (ROOT / workflow).read_text()
            check(source, workflow)
            mutant = source.replace("python3 -m unittest discover -s tests -p 'test_gaviao_g65_specialist_coverage.py' -v", 'echo ignored', 1)
            with self.subTest(workflow=workflow), self.assertRaisesRegex(AssertionError, 'not executed'):
                check(mutant, workflow)


if __name__ == '__main__':
    unittest.main()
