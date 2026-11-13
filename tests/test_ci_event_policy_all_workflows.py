"""Fail closed when a GitHub Actions edit revives duplicate PR/branch runs.

No YAML dependency: parse only the workflow `on` event headers and relevant
`push` fields. Unrecognized push syntax is rejected instead of guessed.
"""
from pathlib import Path
import re
import unittest

WORKFLOWS = Path(__file__).resolve().parents[1] / '.github' / 'workflows'
MUST_DUAL = {
    'cumulative-connections.yml',
    'documentary-dependence.yml',
    'documentary-provenance.yml',
    'historical-space-weather.yml',
    'igra-recife-c151.yml',
    'integration-head.yml',
    'lean-core.yml',
    'morcego-a628-dates.yml',
    'morcego-norad-source-audit.yml',
    'morcego-release-policy.yml',
    'morcego-ru478.yml',
    'orbit-energy-budget.yml',
    'orbit-kernel.yml',
    'orbital-reference.yml',
    'pages.yml',
    'physical-observables.yml',
    'polvo-j2-frozen-long.yml',
    'polvo-j2-secondary-raan.yml',
    'polvo-legacy-epoch-crossing.yml',
    'prek.yml',
    'texugo-quadratic-raan.yml',
    'tle-altitude-lineage.yml',
    'tle-cross-catalog-legacy.yml',
    'tle-cross-epoch-availability.yml',
    'tle-drag-lineage.yml',
    'tle-gcat-identity.yml',
    'tle-identity-lineage.yml',
    'tle-literal-layout.yml',
    'tle-mean-motion-secants.yml',
    'tle-nasa-ssr-delta.yml',
    'tle-nasa-ssr-oct15.yml',
    'tle-numeric-precision.yml',
    'tle-raan-continuity.yml',
    'tle-secondary-epochs.yml',
}

# These two universal gates must run for EVERY pull request, regardless of files.
# Other scientific workflows may intentionally select input paths.
MUST_UNFILTERED_PR = {'integration-head.yml', 'prek.yml'}


def event_blocks(source: str) -> dict[str, list[str]]:
    lines = source.splitlines()
    try:
        start = lines.index('on:') + 1
    except ValueError as exc:
        raise AssertionError('missing explicit on: event block') from exc
    events: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[start:]:
        if line and not line[0].isspace() and not line.lstrip().startswith('#'):
            break
        event = re.fullmatch(r'  ([\w-]+):(?:\s*\{\})?\s*', line)
        if event:
            current = event.group(1)
            if current in events:
                raise AssertionError(f'duplicate event {current}')
            events[current] = []
        elif current is not None and line.strip() and not line.lstrip().startswith('#'):
            events[current].append(line)
    if not events:
        raise AssertionError('unknown or inline on: event syntax')
    return events


def assert_workflow_policy(source: str, filename: str) -> bool:
    events = event_blocks(source)
    if 'pull_request' in events and 'pull_request_target' in events:
        raise AssertionError(f'{filename}: pull_request_target duplicates pull_request triggers')
    if 'push' not in events or 'pull_request' not in events:
        return False
    push = events['push']
    # Only branches: [main] / branches: - main; other keys (e.g. paths)
    # are allowed, but tags and branches-ignore are not equivalent.
    values = []
    active_list = None
    for line in push:
        if re.fullmatch(r'    branches:\s*\[\s*[\x27\x22]?main[\x27\x22]?\s*\]', line):
            values.append('main')
            active_list = None
        elif line == '    branches:':
            values.append('multiline')
            active_list = 'branches'
        elif re.match(r'    paths(?:-ignore)?:', line):
            # Paths may be multiline, but their entries are never branch names.
            active_list = 'paths' if line.endswith(':') else None
        elif re.fullmatch(r'      -\s*[\x27\x22]?main[\x27\x22]?\s*', line) and active_list == 'branches':
            if values[-1] != 'multiline':
                raise AssertionError(f'{filename}: duplicate push branch entry')
            values[-1] = 'main'
        elif re.match(r'      - ', line):
            if active_list != 'paths':
                raise AssertionError(f'{filename}: extra push branch or stray list entry: {line.strip()}')
        else:
            raise AssertionError(f'{filename}: unrecognized push trigger: {line.strip()}')
    if values != ['main']:
        raise AssertionError(f'{filename}: push+PR requires exactly main, got {values!r}')
    if filename in MUST_UNFILTERED_PR and any(
        re.match(r'    paths(?:-ignore)?:', line) for line in push
    ):
        raise AssertionError(f'{filename}: universal main push gate may not filter paths')
    if filename in MUST_UNFILTERED_PR and events['pull_request']:
        raise AssertionError(f'{filename}: universal PR gate may not filter paths, branches or event types')
    return True


class EntireWorkflowEventPolicy(unittest.TestCase):
    def test_every_workflow_prevents_branch_push_duplication(self):
        files = sorted([*WORKFLOWS.glob('*.yml'), *WORKFLOWS.glob('*.yaml')])
        self.assertTrue(MUST_DUAL <= {p.name for p in files})
        protected = 0
        for path in files:
            with self.subTest(workflow=path.name):
                valid_dual = assert_workflow_policy(path.read_text(encoding='utf-8'), path.name)
                protected += bool(valid_dual)
                if path.name in MUST_DUAL:
                    self.assertTrue(valid_dual, 'existing PR+main gate cannot silently lose one event')
        self.assertGreaterEqual(protected, len(MUST_DUAL))

    def test_adversarial_trigger_mutations(self):
        for name in ('integration-head.yml', 'historical-space-weather.yml', 'tle-secondary-epochs.yml'):
            original = (WORKFLOWS / name).read_text(encoding='utf-8')
            self.assertTrue(assert_workflow_policy(original, name))
            cases = (
                original.replace('branches: [main]', 'branches: [main, animal/test]', 1),
                original.replace('branches: [main]', 'branches: [animal/test]', 1),
                original.replace('branches: [main]', 'branches-ignore: [main]', 1),
                original.replace('  pull_request:', '  # pull_request:', 1),
                original.replace('branches: [main]', 'branches: [main, lagarto/**]', 1),
            )
            for i, mutant in enumerate(cases):
                with self.subTest(workflow=name, attack=i):
                    self.assertNotEqual(mutant, original, 'fixture must actually mutate')
                    with self.assertRaises(AssertionError):
                        self.assertTrue(assert_workflow_policy(mutant, name))

    def test_universal_pr_gates_are_unfiltered_and_reject_negative_controls(self):
        self.assertTrue(MUST_UNFILTERED_PR <= MUST_DUAL)
        for name in sorted(MUST_UNFILTERED_PR):
            original = (WORKFLOWS / name).read_text(encoding='utf-8')
            self.assertTrue(assert_workflow_policy(original, name))
            for restriction in (
                'paths: [docs/**]',
                'paths-ignore: [tests/**]',
                'branches: [main]',
                'branches-ignore: [main]',
                'types: [opened]',
            ):
                mutant = original.replace('  pull_request:\n', f'  pull_request:\n    {restriction}\n', 1)
                with self.subTest(workflow=name, restriction=restriction):
                    self.assertNotEqual(mutant, original, 'negative control must mutate')
                    with self.assertRaisesRegex(AssertionError, 'universal PR gate'):
                        assert_workflow_policy(mutant, name)

    def test_universal_main_push_gates_are_unfiltered(self):
        for name in sorted(MUST_UNFILTERED_PR):
            original = (WORKFLOWS / name).read_text(encoding='utf-8')
            self.assertTrue(assert_workflow_policy(original, name))
            for restriction in (
                'paths: ["docs/**"]',
                'paths-ignore: ["tests/**"]',
                'paths:\n      - "docs/**"',
                'paths-ignore:\n      - "tests/**"',
            ):
                mutant = original.replace(
                    '    branches: [main]\n',
                    '    branches: [main]\n    ' + restriction + '\n',
                    1,
                )
                with self.subTest(workflow=name, restriction=restriction):
                    self.assertNotEqual(mutant, original)
                    with self.assertRaisesRegex(AssertionError, 'universal main push gate'):
                        assert_workflow_policy(mutant, name)

    def test_multiline_branches_do_not_hide_extra_push_targets(self):
        name = 'integration-head.yml'
        original = (WORKFLOWS / name).read_text(encoding='utf-8')
        self.assertIn('branches: [main]', original)
        for replacement in (
            'branches:\n      - main\n      - animal/**',
            'branches:\n      - animal/**\n      - main',
            'branches:\n      - main\n      - main',
            'branches: [main]\n      - animal/**',
        ):
            mutant = original.replace('branches: [main]', replacement, 1)
            with self.subTest(replacement=replacement):
                with self.assertRaises(AssertionError):
                    assert_workflow_policy(mutant, name)
        for replacement in (
            'branches:\n      - main',
            'branches:\n      - main\n    paths:\n      - \"tests/**\"',
        ):
            valid = original.replace('branches: [main]', replacement, 1)
            with self.subTest(valid=replacement):
                # Selective scientific workflows may filter push paths; universal gates cannot.
                policy_name = ('historical-space-weather.yml' if '    paths:' in replacement else name)
                self.assertTrue(assert_workflow_policy(valid, policy_name))

    def test_pr_target_cannot_duplicate_normal_pr_event(self):
        for name in ('integration-head.yml', 'prek.yml', 'historical-space-weather.yml'):
            original = (WORKFLOWS / name).read_text(encoding='utf-8')
            self.assertTrue(assert_workflow_policy(original, name))
            for extra in ('  pull_request_target:\n', '  pull_request_target: {}\n'):
                mutant = original.replace('  pull_request:\n', '  pull_request:\n' + extra, 1)
                with self.subTest(workflow=name, extra=extra):
                    self.assertNotEqual(mutant, original)
                    with self.assertRaisesRegex(AssertionError, 'pull_request_target'):
                        assert_workflow_policy(mutant, name)

    def test_one_event_only_is_not_falsely_classified_as_double(self):
        single = 'name: replay\non:\n  workflow_dispatch:\njobs:\n  run:\n    runs-on: ubuntu-latest\n'
        self.assertFalse(assert_workflow_policy(single, 'replay.yml'))


if __name__ == '__main__':
    unittest.main()
