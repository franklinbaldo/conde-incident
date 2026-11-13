"""Reviewed, exact shell bodies for mandatory multiline CI steps.

Keep these intentionally explicit: a required command appearing in unreachable
or status-masked code does not prove that a gate actually executes.
"""

MULTILINE = {
    ('integration-head.yml', 'web', 'Assert exact head SHA'): (
        'test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD_SHA"',
        "printf 'Tested source commit: %s\\n' \"$EXPECTED_HEAD_SHA\"",
    ),
    ('integration-head.yml', 'web', 'Execute all Python unittest suites (fail closed)'): (
        'test -n "$(find tests -type f -name \'test_*.py\' -print -quit)"',
        "python3 -m unittest discover -s tests -p 'test_*.py' -v",
    ),
    ('integration-head.yml', 'web', 'Execute present Node regression suites'): (
        'shopt -s nullglob globstar',
        'tests=(scripts/**/*.test.mjs tests/**/*.test.mjs)',
        'if (( ${#tests[@]} )); then',
        'node --test "${tests[@]}"',
        'else',
        'echo "::error::NO_NODE_TEST_FILES: expected Node regression suites in scripts/ or tests/"',
        'exit 1',
        'fi',
    ),
    ('integration-head.yml', 'lean', 'Detect Lean package'): (
        'if [[ -f formal/lean-toolchain && ( -f formal/lakefile.toml || -f formal/lakefile.lean ) ]]; then',
        'echo "available=true" >> "$GITHUB_OUTPUT"',
        'elif [[ -d formal ]]; then',
        'echo "::error::formal/ exists but its Lean toolchain or Lake manifest is missing"',
        'exit 1',
        'else',
        'echo "available=false" >> "$GITHUB_OUTPUT"',
        'echo "NO_LEAN_PACKAGE: no formal/ directory in this commit"',
        'fi',
    ),
}
