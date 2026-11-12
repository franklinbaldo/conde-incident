#!/usr/bin/env python3
"""Reproducible source/claim traceability audit for a pinned chapter 07.

Passing CI means that the known editorial defect is faithfully detected.
It is NOT scientific approval and does not authenticate PDFs or impact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen

SCHEMA = "conde.gaviao.chapter07/v1"
GUARDS = (
    "nenhum deles prova que não houve investigação da NASA",
    "Não se deduz",
    "não contém esses recortes",
    "nenhum domínio orbital admissível foi reduzido",
    "não foi estabelecida nesta rodada",
)
CLASSES = {
    "retransmitted-report", "typewritten-annotation", "quoted-secondhand-report",
    "administrative-mark", "documentary-year-anomaly", "bounded-negative",
    "logical-non-implication",
}

def git_blob(text):
    raw = text.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def critical_findings(story):
    findings = []
    if ("hipóteses concorrentes" in story and "H-ARQ" in story and "H-SEG" in story
            and "podem ter produzido registros próprios" in story):
        findings.append("false-exclusive-H-ARQ-H-SEG")
    return findings

def check(story, ledger, verify_blob=True):
    faults = []
    if ledger.get("schema") != SCHEMA:
        faults.append("schema mismatch")
    if ledger.get("story", {}).get("pr") != 44:
        faults.append("wrong article PR")
    if verify_blob and git_blob(story) != ledger.get("story", {}).get("blob_sha"):
        faults.append("pinned Git blob differs")
    if 'chapter: "07"' not in story:
        faults.append("not chapter 07")
    for guard in GUARDS:
        if guard not in story:
            faults.append("missing epistemic guard: " + guard)
    if "**“on November 8, 1964”**" not in story:
        faults.append("1964 subject anomaly must be explicit")
    if "NOT_VERIFIED" not in ledger.get("source_status", ""):
        faults.append("government-vs-mirror byte equivalence not established")
    srcs = ledger.get("sources", [])
    srcmap = {s.get("id"): s for s in srcs}
    if len(srcs) != 3 or set(srcmap) != {"A628", "D001", "FBIS03"}:
        faults.append("three distinct document identifiers required")
    for s in srcs:
        if not s.get("url", "").startswith("https://") or s["url"] not in story:
            faults.append("source URL missing from story: " + str(s.get("id")))
        if s.get("physical_observation") is not False:
            faults.append("facsimile falsely treated as physical observation")
    if srcmap.get("D001", {}).get("chain") != srcmap.get("A628", {}).get("chain"):
        faults.append("two State documents falsely split into independent chains")
    claims = ledger.get("claims", [])
    if len(claims) != 9 or len({c.get("id") for c in claims}) != 9:
        faults.append("claims missing or duplicated")
    for c in claims:
        if c.get("source") not in srcmap:
            faults.append("unresolved source ID: " + str(c.get("id")))
        if not c.get("occurrences"):
            faults.append("matrix occurrence omitted: " + str(c.get("id")))
        if c.get("anchor", "___not_in_story___") not in story:
            faults.append("claim absent from pinned chapter: " + str(c.get("id")))
        if c.get("classification") not in CLASSES:
            faults.append("invalid epistemic classification: " + str(c.get("id")))
    if sorted(critical_findings(story)) != sorted(ledger.get("expected_findings", [])):
        faults.append("editorial finding drift: re-review story and ledger")
    return faults

def pinned_story(info):
    url = ("https://raw.githubusercontent.com/franklinbaldo/conde-incident/"
           + info["sha"] + "/" + info["path"])
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="research/gaviao_chapter07_ledger.json")
    inp = ap.add_mutually_exclusive_group(required=True)
    inp.add_argument("--download", action="store_true")
    inp.add_argument("--story", type=Path)
    args = ap.parse_args()
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    story = pinned_story(ledger["story"]) if args.download else args.story.read_text(encoding="utf-8")
    problems = check(story, ledger)
    for p in problems:
        print("FAIL", p, file=sys.stderr)
    if problems:
        return 1
    print("PASS: source IDs, dependencies, guards and exact pinned story blob")
    print("DOCUMENTED EDITORIAL DEFECT:", ",".join(critical_findings(story)))
    print("NOT an approval or verification of original-PDF byte equality or an orbit.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
