"""Fail closed when a scientific input changes without its specialized replay."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/c241-joint-orbit-day.yml'
INPUTS = {
    'tools/c241_joint_orbit_day_heatmap.py',
    'research/tle_custody/mirror_528_1963-10-27.tle',
    'research/constraints/C241_nov8_two_sided_day_likelihood_2026-11-13.json',
    'research/statistics/c241_528_unweighted_2000km_scenarios.json',
}


class JointReplayTriggers(unittest.TestCase):
    def test_all_direct_inputs_trigger_both_events(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        for event in ('pull_request', 'push'):
            with self.subTest(event=event):
                section = re.search(
                    rf'(?ms)^  {event}:\n(.*?)(?=^  [A-Za-z_]+:|^permissions:|\Z)',
                    workflow,
                )
                self.assertIsNotNone(section, f'No {event} event')
                paths = re.search(r'(?m)^    paths:\n((?:^      - .+\n)+)', section[1])
                self.assertIsNotNone(paths, f'No {event}.paths')
                covered = {line.strip()[2:].strip("'\"") for line in paths[1].splitlines()}
                self.assertFalse(INPUTS - covered,
                                 f'{event} source-only changes skip replay: {sorted(INPUTS-covered)}')


if __name__ == '__main__':
    unittest.main()
