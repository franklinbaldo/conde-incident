"""All checkout-based checks must compare HEAD to the triggering event SHA.

Keep this static audit small and fail closed for unsupported verification syntax:
textual mentions of `git rev-parse HEAD` are not assertions.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / '.github' / 'workflows'
PR_SHA = '${{ github.event.pull_request.head.sha || github.sha }}'
RUN_SHA = '${{ github.sha }}'
STEP_START = re.compile(r'(?m)^      - ')
CHECKOUT_USE = re.compile(r"(?m)^(?:uses| {8}uses): [\"']?actions/checkout@[^\n]+")
REF = re.compile(r'(?m)^          ref: (.+)$')



def _is_unconditional_guard(step: str, assertion: str, expected: str) -> bool:
    """Accept a SHA guard only if no preceding shell command can skip it.

    This is intentionally a small allowlist, not a general shell interpreter.
    Unknown commands before the guard require explicit audit of the workflow.
    """
    run = re.search(r'(?m)^        run: (.*)$', step)
    if not run:
        return False
    head = run.group(1).strip()
    if head in ('|', '|-', '>'):
        commands = [line.strip() for line in step[run.end():].splitlines()
                    if line.strip() and not line.lstrip().startswith('#')]
    else:
        commands = [head]
    if assertion not in commands:
        return False
    allowed_before = {
        'set -euo pipefail',
        'actual="$(git rev-parse HEAD)"',
        f'expected="{expected}"',
        'echo "audited_source_head=$actual"',
        'echo "audited_head=$actual"',
    }
    return all(line in allowed_before for line in commands[:commands.index(assertion)])


def _is_exact_assertion(step: str, expected: str) -> bool:
    """Recognize a mandatory, fail-closed comparison in the next CI step."""
    # A conditional or tolerated assertion is not a gate, even if its shell
    # command contains a byte-for-byte exact SHA comparison.
    if re.search(r'(?m)^        (?:if|continue-on-error)\s*:', step):
        return False
    commands = {line.strip() for line in step.splitlines()
                if line.strip() and not line.lstrip().startswith('#')}
    commands |= {line.removeprefix('run: ').strip() for line in commands if line.startswith('run: ')}
    head = '$(git rev-parse HEAD)'
    if f'test "{head}" = "{expected}"' in commands:
        return _is_unconditional_guard(step, f'test "{head}" = "{expected}"', expected)

    # `env: EXPECTED_SHA: ${{ ... }}` plus a shell comparison.
    if re.search(r'(?m)^        env:\s*$', step):
        for var, value in re.findall(r'(?m)^          ([A-Z][A-Z0-9_]*):\s*(.+)$', step):
            if value.strip() == expected and f'test "{head}" = "${var}"' in commands:
                return _is_unconditional_guard(step, f'test "{head}" = "${var}"', expected)

    # Explicit shell assignments, used by the historical TLE workflows.
    if (f'actual="{head}"' in commands
            and f'expected="{expected}"' in commands
            and 'test "$actual" = "$expected"' in commands):
        return _is_unconditional_guard(step, 'test "$actual" = "$expected"', expected)
    return False


def check_checkout_sha(source: str, name: str) -> int:
    expected = PR_SHA if re.search(r'(?m)^  pull_request:', source) else RUN_SHA
    # Split on YAML step boundaries, not merely `- uses:`. GitHub Actions
    # permits `name:` or `id:` before `uses:` inside a checkout step.
    steps = STEP_START.split(source)[1:]
    count = 0
    for pos, checkout in enumerate(steps):
        if not CHECKOUT_USE.search(checkout):
            continue
        count += 1
        refs = REF.findall(checkout)
        if refs != [expected]:
            raise AssertionError(f'{name}: checkout must pin {expected}, got {refs!r}')
        if pos + 1 >= len(steps):
            raise AssertionError(f'{name}: checkout has no following SHA assertion step')
        next_step = steps[pos + 1]
        if not _is_exact_assertion(next_step, expected):
            raise AssertionError(f'{name}: missing executable exact SHA assertion immediately after checkout')
    return count


class ExactCheckoutPolicy(unittest.TestCase):
    def test_every_checkout_pins_event_sha_and_asserts_it(self):
        files = sorted([*ROOT.glob('*.yml'), *ROOT.glob('*.yaml')])
        self.assertTrue(files)
        count = 0
        for path in files:
            with self.subTest(workflow=path.name):
                count += check_checkout_sha(path.read_text(encoding='utf-8'), path.name)
        self.assertGreaterEqual(count, 35)

    def test_ibge_live_replay_controls(self):
        name = 'ibge-source-live.yml'
        source = (ROOT / name).read_text(encoding='utf-8')
        self.assertEqual(check_checkout_sha(source, name), 1)
        for mutant in (
            source.replace(f'ref: {RUN_SHA}', 'ref: main', 1),
            source.replace(f'ref: {RUN_SHA}\n', '', 1),
            source.replace('git rev-parse HEAD', 'git rev-parse BASE', 1),
        ):
            with self.subTest(mutant=mutant != source):
                self.assertNotEqual(mutant, source)
                with self.assertRaises(AssertionError):
                    check_checkout_sha(mutant, name)

    def test_sha_must_be_compared_not_just_printed(self):
        cases = {
            'integration-head.yml': ('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"',
                                     'echo "$(git rev-parse HEAD)"'),
            'tle-altitude-lineage.yml': ('test "$actual" = "$expected"',
                                        'echo "$actual"'),
            'tle-gcat-identity.yml': (
                'test "$(git rev-parse HEAD)" = "' + PR_SHA + '"',
                'echo "$(git rev-parse HEAD)"'),
        }
        for name, (old, new) in cases.items():
            source = (ROOT / name).read_text(encoding='utf-8')
            self.assertGreater(check_checkout_sha(source, name), 0)
            self.assertIn(old, source)
            for replacement in (new, '# ' + old):
                mutant = source.replace(old, replacement, 1)
                with self.subTest(workflow=name, change=replacement):
                    self.assertNotEqual(mutant, source)
                    with self.assertRaisesRegex(AssertionError, 'exact SHA assertion'):
                        check_checkout_sha(mutant, name)

    def test_named_checkout_cannot_escape_sha_guard(self):
        name = 'integration-head.yml'
        source = (ROOT / name).read_text(encoding='utf-8')
        self.assertEqual(check_checkout_sha(source, name), 2)
        original = '      - uses: actions/checkout@v4\n'
        self.assertIn(original, source)
        for initial in ('name: Checkout source', 'id: checkout_source'):
            named = source.replace(
                original,
                f'      - {initial}\n        uses: actions/checkout@v4\n', 1,
            )
            with self.subTest(initial=initial):
                # Naming a checkout must not make it invisible to the audit.
                self.assertEqual(check_checkout_sha(named, name), 2)
                broken = named.replace(f'ref: {PR_SHA}', 'ref: main', 1)
                self.assertNotEqual(broken, named)
                with self.assertRaisesRegex(AssertionError, 'checkout must pin'):
                    check_checkout_sha(broken, name)

    def test_sha_assertion_cannot_be_skipped_or_ignored(self):
        for name, marker in (
            ('integration-head.yml', '      - name: Assert exact head SHA\n'),
            ('prek.yml', '      - name: Assert exact source SHA\n'),
        ):
            original = (ROOT / name).read_text(encoding='utf-8')
            self.assertGreater(check_checkout_sha(original, name), 0)
            for bypass in ('        if: ${{ false }}\n',
                           '        continue-on-error: true\n'):
                mutant = original.replace(marker, marker + bypass, 1)
                with self.subTest(workflow=name, bypass=bypass):
                    self.assertNotEqual(mutant, original)
                    with self.assertRaisesRegex(AssertionError, 'SHA assertion'):
                        check_checkout_sha(mutant, name)

    def test_sha_guard_must_not_be_bypassed_by_prior_shell_commands(self):
        name = 'integration-head.yml'
        source = (ROOT / name).read_text(encoding='utf-8')
        guard = '          test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"\n'
        self.assertIn(guard, source)
        # Default bash -e does not help after an unconditional exit or when
        # errexit is disabled before the guard. A false if-branch skips it.
        for before, after in (
            ('          exit 0\n', ''),
            ('          if false; then\n', '          fi\n'),
            ('          set +e\n', ''),
        ):
            mutant = source.replace(guard, before + guard + after, 1)
            with self.subTest(bypass=before.strip()):
                self.assertNotEqual(mutant, source)
                with self.assertRaisesRegex(AssertionError, 'exact SHA assertion'):
                    check_checkout_sha(mutant, name)

    def test_expected_value_and_per_checkout_proximity_are_required(self):
        name = 'integration-head.yml'
        source = (ROOT / name).read_text(encoding='utf-8')
        self.assertEqual(check_checkout_sha(source, name), 2)
        for mutant in (
            source.replace(f'EXPECTED_HEAD_SHA: {PR_SHA}', f'EXPECTED_HEAD_SHA: {RUN_SHA}', 1),
            source.replace('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"',
                           'echo "$(git rev-parse HEAD)"\n      - name: Late fake check\n'
                           '        run: test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"', 1),
            source.replace('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"',
                           'echo "$(git rev-parse HEAD)"', 1),
        ):
            with self.subTest(change=mutant != source):
                self.assertNotEqual(mutant, source)
                with self.assertRaisesRegex(AssertionError, 'exact SHA assertion'):
                    check_checkout_sha(mutant, name)


if __name__ == '__main__':
    unittest.main()
