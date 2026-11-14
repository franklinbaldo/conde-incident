"""G62: IERS replay must run for source-only changes in optical light time."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/iers-eop-1963.yml'
REQUIRED = {
    'tools/iers_1963_optical_lighttime.py',
    'tools/iers_1963_optical_lighttime_jacobian.py',
    'research/constraints/iers_1963_optical_lighttime_G60.md',
    'research/constraints/iers_1963_optical_retarded_covariance_G61.md',
    'tests/test_iers_1963_workflow_paths.py',
    'tests/test_iers_1963_lighttime_accel.py',
    'research/constraints/iers_1963_acceleration_sensitivity_G63.md',
}


def event_paths(source, event):
    """Read only top-level event path selectors, not mentions in job steps."""
    paths = set()
    selected = False
    in_paths = False
    for line in source.splitlines():
        if line.startswith('  ') and not line.startswith('    '):
            selected = line == f'  {event}:'
            in_paths = False
        elif selected and line == '    paths:':
            in_paths = True
        elif selected and in_paths and line.startswith('      - '):
            paths.add(line[len('      - '):].strip().strip("\"'"))
        elif selected and in_paths and not line.startswith('      '):
            in_paths = False
    return paths


def assert_replay_paths(source):
    for event in ('pull_request', 'push'):
        missing = REQUIRED - event_paths(source, event)
        if missing:
            raise AssertionError(f'{event}: missing source-only trigger paths: {sorted(missing)}')
    if "python3 -m unittest discover -s tests -p 'test_iers_1963_optical.py' -v" not in source:
        raise AssertionError('Original IERS optical test replay command missing')
    if "python3 -m unittest discover -s tests -p 'test_iers_1963_lighttime_accel.py' -v" not in source:
        raise AssertionError('G63 acceleration sensitivity regression must execute')
    if "python3 -O -m unittest discover -s tests -p 'test_iers_1963_lighttime_accel.py' -v" not in source:
        raise AssertionError('G63 accelerated regression must also execute with -O')
    if "python3 -m unittest discover -s tests -p 'test_iers_1963_workflow_paths.py' -v" not in source:
        raise AssertionError('Source-only trigger regression must execute')


class IERSWorkflowSourceOnly(unittest.TestCase):
    def test_both_event_filters_cover_optical_lighttime_sources(self):
        assert_replay_paths(WORKFLOW.read_text(encoding='utf-8'))

    def test_mutants_fail_for_each_event_and_file(self):
        source = WORKFLOW.read_text(encoding='utf-8')
        assert_replay_paths(source)
        for event in ('pull_request', 'push'):
            for relative in REQUIRED:
                # Delete a trigger from only one event, retaining all other triggers.
                sections = source.split(f'  {event}:', 1)
                self.assertEqual(len(sections), 2)
                head, tail = sections
                tail = tail.replace('      - '+relative+'\n', '', 1)
                self.assertNotEqual(source, head + f'  {event}:' + tail)
                with self.subTest(event=event, file=relative):
                    with self.assertRaisesRegex(AssertionError, event):
                        assert_replay_paths(head + f'  {event}:' + tail)


if __name__ == '__main__':
    unittest.main()
