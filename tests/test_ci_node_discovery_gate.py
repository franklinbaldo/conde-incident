"""G45: exercise the integration Node gate, including a zero-suite checkout."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/integration-head.yml"


def node_step():
    content = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        r"(?m)^      - name: Execute present Node regression suites\n"
        r"        shell: bash\n        run: \|\n((?:          .*\n|\n)+)",
        content,
    )
    if not match:
        raise AssertionError("Node regression step missing or structure changed")
    return "\n".join(line[10:] for line in match.group(1).splitlines()) + "\n"


class NodeDiscoveryGate(unittest.TestCase):
    def execute(self, with_suite):
        with tempfile.TemporaryDirectory(prefix="g45-node-discovery-") as temp:
            root = Path(temp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            marker = root / "node-executed.txt"
            node = bin_dir / "node"
            node.write_text('#!/bin/sh\nprintf "%s\\n" "$*" > "$G45_NODE_MARKER"\n')
            node.chmod(0o755)
            if with_suite:
                suite = root / "tests" / "smoke.test.mjs"
                suite.parent.mkdir()
                suite.write_text("// positive synthetic suite\n")
            env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
                   "G45_NODE_MARKER": str(marker)}
            result = subprocess.run(["bash", "-e", "-c", node_step()], cwd=root,
                                    env=env, text=True, capture_output=True, check=False)
            return result, marker.read_text() if marker.exists() else None

    def test_zero_discovered_node_suites_must_fail_closed(self):
        result, invoked = self.execute(with_suite=False)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIsNone(invoked)

    def test_one_discovered_node_suite_executes_node(self):
        result, invoked = self.execute(with_suite=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(invoked, "--test tests/smoke.test.mjs\n")


if __name__ == "__main__":
    unittest.main()
