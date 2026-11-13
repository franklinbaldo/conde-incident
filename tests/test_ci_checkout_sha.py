"""All checkout-based checks must execute the explicit event source SHA."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / '.github' / 'workflows'
PR_SHA = '${{ github.event.pull_request.head.sha || github.sha }}'
RUN_SHA = '${{ github.sha }}'
CHECKOUT = re.compile(r'(?m)^      - uses: actions/checkout@[^\n]+\n')
REF = re.compile(r'(?m)^          ref: (.+)$')


def check_checkout_sha(source: str, name: str) -> int:
    expected = PR_SHA if re.search(r'(?m)^  pull_request:', source) else RUN_SHA
    matches = list(CHECKOUT.finditer(source))
    for match in matches:
        step = source[match.end():].split('      - ', 1)[0]
        refs = REF.findall(step)
        if refs != [expected]:
            raise AssertionError(f'{name}: checkout must pin {expected}, got {refs!r}')
        if 'git rev-parse HEAD' not in source:
            raise AssertionError(f'{name}: missing SHA assertion')
        if name == 'ibge-source-live.yml':
            if (f'          EXPECTED_SHA: {RUN_SHA}' not in source
                    or '        run: test "$(git rev-parse HEAD)" = "$EXPECTED_SHA"' not in source):
                raise AssertionError(f'{name}: live replay must compare checkout HEAD with event SHA')
    return len(matches)


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


if __name__ == '__main__':
    unittest.main()
