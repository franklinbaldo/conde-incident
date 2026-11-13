"""Adversarial controls for indispensable CI steps (G40)."""
from pathlib import Path
import re
import unittest

from test_ci_event_policy_all_workflows import assert_workflow_policy

WORKFLOWS = Path(__file__).resolve().parents[1] / '.github' / 'workflows'


class UniversalStepIntegrity(unittest.TestCase):
    def test_universal_critical_step_bypass_is_rejected(self):
        # A required *job* may succeed while its one required test step is
        # silently skipped, tolerated or replaced by an inert command.
        cases = (
            ('prek.yml', 'Run prek hooks over all tracked files',
             'run: uvx --from prek==0.5.10 prek run --all-files'),
            ('integration-head.yml', 'TypeScript check', 'run: bun run lint'),
            ('integration-head.yml', 'Build Vite frontend', 'run: bun run build'),
            ('integration-head.yml', 'Execute all Python unittest suites (fail closed)',
             "python3 -m unittest discover -s tests -p 'test_*.py' -v"),
            ('integration-head.yml', 'Compile conditional proofs', 'run: lake build'),
        )
        for name, label, required in cases:
            source = (WORKFLOWS / name).read_text(encoding='utf-8')
            self.assertTrue(assert_workflow_policy(source, name))
            marker = f'      - name: {label}\n'
            self.assertIn(marker, source)
            for injection in ('        if: false\n', '        continue-on-error: true\n'):
                # Lean compile has a legitimate conditional; an injected
                # second condition must be rejected rather than shadowed.
                mutant = source.replace(marker, marker + injection, 1)
                with self.subTest(name=name, step=label, bypass=injection.strip()):
                    with self.assertRaisesRegex(AssertionError, 'universal step'):
                        assert_workflow_policy(mutant, name)
            # The display name cannot serve as evidence that the command ran.
            mutant = source.replace(required, 'run: echo gate-disabled', 1)
            with self.subTest(name=name, step=label, bypass='command removed'):
                with self.assertRaisesRegex(AssertionError, 'universal step'):
                    assert_workflow_policy(mutant, name)
            # Removing a required step entirely must also fail the gate.
            start = source.index(marker)
            later = re.search(r'(?m)^      - (?:name|uses):', source[start + len(marker):])
            mutant = source[:start] + (source[start + len(marker) + later.start():] if later else '')
            with self.subTest(name=name, step=label, bypass='step removed'):
                with self.assertRaisesRegex(AssertionError, 'universal step'):
                    assert_workflow_policy(mutant, name)

    def test_multiline_commands_cannot_hide_tolerated_failure(self):
        # A required command with an appended success clause can pass by text
        # prefix matching while the actual test fails and the step stays green.
        original = (WORKFLOWS / 'integration-head.yml').read_text(encoding='utf-8')
        self.assertTrue(assert_workflow_policy(original, 'integration-head.yml'))
        for command in (
            'test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"',
            "python3 -m unittest discover -s tests -p 'test_*.py' -v",
            'node --test "${tests[@]}"',
        ):
            for bypass in (' || true', ' ; true', ' || :'):
                mutant = original.replace(command, command + bypass, 1)
                with self.subTest(command=command, bypass=bypass):
                    self.assertNotEqual(mutant, original)
                    with self.assertRaisesRegex(AssertionError, 'universal step command'):
                        assert_workflow_policy(mutant, 'integration-head.yml')

    def test_universal_steps_reject_early_success_and_shell_replacement(self):
        original = (WORKFLOWS / 'integration-head.yml').read_text(encoding='utf-8')
        self.assertTrue(assert_workflow_policy(original, 'integration-head.yml'))
        mutants = {
            'lint exits before running': original.replace(
                'run: bun run lint', 'run: |\n          exit 0\n          bun run lint', 1),
            'Python exits before running': original.replace(
                "          python3 -m unittest discover -s tests -p 'test_*.py' -v",
                "          exit 0\n          python3 -m unittest discover -s tests -p 'test_*.py' -v", 1),
            'node uses no-op shell': original.replace(
                '      - name: Execute present Node regression suites\n        shell: bash\n',
                '      - name: Execute present Node regression suites\n'
                '        shell: bash -c "true" {0}\n', 1),
            'lint uses no-op shell': original.replace(
                '      - name: TypeScript check\n        run:',
                '      - name: TypeScript check\n        shell: bash -c "true" {0}\n        run:', 1),
            'job changes default shell': original.replace(
                '  web:\n    runs-on:',
                '  web:\n    defaults:\n      run:\n        shell: bash -c "true" {0}\n    runs-on:', 1),
            'workflow changes default shell': original.replace(
                'jobs:\n',
                'defaults:\n  run:\n    shell: bash -c "true" {0}\njobs:\n', 1),
            'node skips when conditional lies': original.replace(
                '          if (( ${#tests[@]} )); then',
                '          if false; then', 1),
        }
        for label, mutant in mutants.items():
            with self.subTest(bypass=label):
                self.assertNotEqual(mutant, original)
                with self.assertRaisesRegex(AssertionError, 'universal step'):
                    assert_workflow_policy(mutant, 'integration-head.yml')


if __name__ == '__main__':
    unittest.main()
