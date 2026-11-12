#!/usr/bin/env python3
"""Bounded audit of chapter 07 fixed text. Passing != confirming impact."""
from itertools import product
from pathlib import Path
import argparse
import hashlib
from urllib.request import urlopen

COMMIT = "bd17c4f4402a72f34490e6e8b9d2a62084728f90"
BLOB = "92da679de5e4c2eb68af46b73580e5c34b48dc7a"
PATH = "stories/2026-11-12-o-carimbo-que-dizia-sem-providencias.md"
SOURCES = {
    "FBIS03": "https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf",
    "D001": "https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf",
    "A628": "https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf",
}
REQUIRED = {
    "chapter": 'chapter: "07"',
    "a628_nov24": "**1963 NOV 24**",
    "a628_nov26": "**INTERNATIONAL SCIENTIFIC AFFAIRS / NOV 26 1963**",
    "local_mark": "**NOTED - NO ACTION**",
    "old_subject_typo": "**“on November 8, 1964”**",
    "coexistence": "**As duas situações podem ter acontecido ao mesmo tempo.**",
    "local_vs_external": "**dois eixos de verificação independentes**",
    "receipt_only": "Um **recibo de entrada** da NASA ou da Defesa confirmaria apenas que a informação chegou",
    "followup_distinction": "Um **registro de diligência, relatório técnico ou resposta datada**",
    "physical_axis": "**H-EVE**",
    "bounded_negative": "não uma prova de inatividade universal",
    "unverified_hash": "equivalência byte a byte com a URL governamental de origem **não foi estabelecida",
    "no_orbital_reduction": "**nenhum domínio orbital admissível foi reduzido**",
}
REFS = ("C01", "C02", "C03", "C05", "C06", "C08", "C09", "C10",
        "C15", "C16", "C165", "AX-STATE-20261111-01",
        "AX-STATE-20261111-02", "AX-STATE-20261111-03")

def admissible_worlds():
    """Logical options, never observed or given statistical weights.

    The sole premise here is that the examined State copy bears its note.
    NASA receipt, NASA follow-up and physical impact remain unconstrained.
    """
    return tuple((True, receipt, followup, impact)
                 for receipt, followup, impact in product((False, True), repeat=3))

def blob_of(text):
    raw = text.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def audit(story, pinned=True):
    errors = []
    if pinned and blob_of(story) != BLOB:
        errors.append("story Git blob does not match independently reviewed revision")
    for k, snippet in REQUIRED.items():
        if snippet not in story:
            errors.append("required bounded claim missing: " + k)
    for k, url in SOURCES.items():
        if url not in story:
            errors.append("primary image URL missing: " + k)
    for ref in REFS:
        if ref not in story:
            errors.append("cumulative ID omitted: " + ref)
    if "hipóteses concorrentes" in story and "H-ARQ" in story and "H-SEG" in story:
        errors.append("G07-B1 false-exclusive administrative axes")
    return errors

def get_pinned():
    url = "https://raw.githubusercontent.com/franklinbaldo/conde-incident/" + COMMIT + "/" + PATH
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--pinned", action="store_true")
    g.add_argument("--story", type=Path)
    args = p.parse_args()
    content = get_pinned() if args.pinned else args.story.read_text(encoding="utf-8")
    errors = audit(content)
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: SHA-pinned story, three image sources, claim anchors and matrix IDs")
    print("Logical alternatives:", len(admissible_worlds()), "without empirical posterior")
    print("NOT_VERIFIED: government image byte equivalence, agency activity, impact, Lean or orbital inference")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
