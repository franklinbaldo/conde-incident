#!/usr/bin/env python3
"""Run native OKF parser over all new/changed Markdown, freezing legacy blobs.

The historical source corpus is kept intact. Its 94 Markdown files are
recorded by Git object hash, not silently ignored; modifying one requires
making it valid OKF. The migration backlog remains explicit and auditable.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "config/legacy-nonokf-markdown.json"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    frozen = {entry["path"]: entry["git_blob_sha"]
              for entry in baseline["legacy_markdown"]}
    markdown = [raw.decode("utf-8")
                for raw in git("ls-files", "-z").split(b"\0")
                if raw and raw.decode("utf-8").endswith(".md")]
    with tempfile.TemporaryDirectory(prefix="conde-okf-") as temp:
        stage = Path(temp)
        changed = []
        for relative in markdown:
            path = ROOT / relative
            if not path.is_file():
                continue
            sha = git("hash-object", "--", relative).decode().strip()
            if frozen.get(relative) == sha:
                continue
            dest = stage / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
            changed.append(relative)
        for spec in (ROOT / ".okf/specs").glob("*.md"):
            dest = stage / ".okf/specs" / spec.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(spec, dest)
        print(f"OKF_SCOPE: {len(changed)} new/modified Markdown file(s); "
              f"{len(markdown) - len(changed)} frozen legacy file(s)")
        command = ["uvx", "--from", "okf-parser==0.48.2", "okf-parser",
                   "check", str(stage), "--require-spec",
                   ".okf/specs/{slug}.md", "--normative-spec"]
        return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
