"""Independent source-only CI trigger contract for the G71 scientific replay.

Test the negative mutations too: a check must fail if any imported module,
regression, source note or the replay command disappears from the workflow.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

WORKFLOW = (Path(__file__).resolve().parents[1] /
            '.github/workflows/castor-g71-day-shift-falsifier.yml')
REQUIRED_INPUTS = frozenset({
    'tools/c241_fixed_h_day_shift_G71.py',
    'tools/c241_king_hele_fixed_h_falsifier.py',
    'tools/c241_king_hele_day_holdout.py',
    'tools/c241_637_regime_holdout.py',
    'tests/test_c241_fixed_h_day_shift_G71.py',
    'tests/test_c241_g71_workflow_coverage.py',
    'research/statistics/C241_G71_INDEPENDENT_DAY_SHIFT_FALSIFIER_20261114.md',
    '.github/workflows/castor-g71-day-shift-falsifier.yml',
})
MANDATORY_COMMANDS = (
    "python3 -m unittest discover -s tests -p 'test_c241_fixed_h_day_shift_G71.py' -v",
    "python3 -O -m unittest discover -s tests -p 'test_c241_fixed_h_day_shift_G71.py' -v",
    "python3 -m unittest discover -s tests -p 'test_c241_g71_workflow_coverage.py' -v",
    "python3 -O -m unittest discover -s tests -p 'test_c241_g71_workflow_coverage.py' -v",
    'python3 tools/c241_fixed_h_day_shift_G71.py',
    'sha256sum -c -',
)


def check_contract(source: str) -> None:
    for event in ('pull_request', 'push'):
        block = re.search(r'(?ms)^  ' + event +
                          r':\s*\n(.*?)(?=^  (?:push|pull_request|workflow_dispatch):|^permissions:|^jobs:|\Z)',
                          source)
        if block is None:
            raise ValueError('missing event ' + event)
        paths = set(re.findall(r"(?m)^      - ['\"]?([^'\"\n]+)['\"]?$", block[1]))
        missing = REQUIRED_INPUTS - paths
        if missing:
            raise ValueError('uncovered ' + event + ' inputs: ' + ','.join(sorted(missing)))
    for command in MANDATORY_COMMANDS:
        if source.count(command) != 1:
            raise ValueError('required replay command missing/duplicated: ' + command)
    if 'set -euo pipefail' not in source:
        raise ValueError('missing strict shell')


class G71WorkflowSourceOnlyContract(unittest.TestCase):
    def test_current_workflow(self):
        check_contract(WORKFLOW.read_text(encoding='utf-8'))

    def test_removing_any_single_input_from_each_event_fails(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        for event in ('pull_request', 'push'):
            block = re.search(r'(?ms)^  ' + event +
                              r':\s*\n(.*?)(?=^  (?:push|pull_request|workflow_dispatch):|^permissions:|^jobs:|\Z)',
                              text)
            self.assertIsNotNone(block)
            for path in REQUIRED_INPUTS:
                with self.subTest(event=event, path=path):
                    line = '      - ' + path + '\n'
                    self.assertIn(line, block[1])
                    mutated = text[:block.start(1)] + block[1].replace(line, '', 1) + text[block.end(1):]
                    with self.assertRaisesRegex(ValueError, 'uncovered'):
                        check_contract(mutated)

    def test_replacing_any_required_command_fails(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        for command in MANDATORY_COMMANDS:
            with self.subTest(command=command):
                with self.assertRaisesRegex(ValueError, 'command'):
                    check_contract(text.replace(command, 'echo skipped mandatory replay', 1))


if __name__ == '__main__':
    unittest.main()
