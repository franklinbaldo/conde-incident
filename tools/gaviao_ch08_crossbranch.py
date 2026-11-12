#!/usr/bin/env python3
"""Independent bounded audit of chapter 08 against two code revisions."""
import argparse
import hashlib
from itertools import product
from urllib.request import urlopen

OWNER_REPO = "franklinbaldo/conde-incident"
STORY = (
    "b91cf9641820f47fb9e7e75c76d6123f4988b1ad",
    "stories/2026-11-12-o-veredito-que-os-dados-nao-deram.md",
    "61e4d07f10441b5ec5e6d56758cc85ffdf18766c",
)
BEFORE = (
    "c84cce85e51252f9e589a851950385aea008e951",
    "src/components/ExecutiveSummary.tsx",
    "5eee17e3ff05da5fcbaf6e0bb0b2a3384991d834",
)
AFTER = (
    "115e58693a64d23789e1f75f50146105f114b3be",
    "src/components/ExecutiveSummary.tsx",
    "7629820680d0ea5d128adc3a97260dd64166b1f7",
)
NASA = "https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10"
FBIS = "https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf"
OLD_ASSERTIONS = (
    "VEREDITO ASTRODINÂMICO & DOCUMENTAL",
    "19:48 UTC (Rev 14)",
    "~0,0062%",
    "Boato Fabricado",
)
STORY_GUARDS = (
    'chapter: "08"',
    "não foi demonstrado como publicado",
    "não é uma probabilidade histórica demonstrada",
    "não uma prova nova em Lean 4.35.0",
    "não reduz por si só nenhum intervalo físico admissível",
    "não duas testemunhas de um único impacto",
    "não prova que o rastreamento cessou historicamente",
    "C197–C201", "C01–C02", "C241-T3", "PR #24", "PR #43", "PR #37",
)

def git_blob(text):
    raw = text.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()

def url_for(ref):
    return f"https://raw.githubusercontent.com/{OWNER_REPO}/{ref[0]}/{ref[1]}"

def load_pinned(ref):
    with urlopen(url_for(ref), timeout=30) as response:
        raw = response.read()
    return raw.decode("utf-8")

def possibilities():
    """Four logical countermodels; NOT historical observations or probabilities."""
    return tuple((True, True, impact, same_event)
                 for impact, same_event in product((False, True), repeat=2))

def audit(story, before, after, check_blobs=False):
    errors = []
    if check_blobs:
        for name, data, expected in (
            ("story", story, STORY[2]), ("before", before, BEFORE[2]),
            ("after", after, AFTER[2]),
        ):
            if git_blob(data) != expected:
                errors.append(f"{name}: pinned Git blob mismatch")
    for phrase in OLD_ASSERTIONS:
        if phrase not in before:
            errors.append("historical before-quote missing: " + phrase)
        if phrase in after:
            errors.append("obsolete assertion still in new summary: " + phrase)
    if "Resultado: indeterminado." not in after:
        errors.append("corrected summary does not say indeterminado")
    if "not a verdict" not in after:
        errors.append("English corrected summary lacks non-verdict caveat")
    for key, value in (("NASA image page", NASA), ("FBIS image", FBIS),
                       ("old source permalink", BEFORE[0]),
                       ("new source permalink", AFTER[0])):
        if value not in story:
            errors.append("missing story source: " + key)
    for phrase in STORY_GUARDS:
        if phrase not in story:
            errors.append("required bounded story claim missing: " + phrase)
    for forbidden in ("NASA comprovou impacto", "queda comprovada em Conde",
                      "hora terminal verificada 19:48", "publicação da correção confirmada"):
        if forbidden.casefold() in story.casefold():
            errors.append("unverified positive claim: " + forbidden)
    if "NOTED - NO ACTION" not in story:
        errors.append("previous chapter context missing")
    if len(possibilities()) != 4 or len({row[2] for row in possibilities()}) != 2:
        errors.append("logical countermodels incomplete")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pinned", action="store_true", required=True)
    args = parser.parse_args()
    assert args.pinned
    story, before, after = [load_pinned(ref) for ref in (STORY, BEFORE, AFTER)]
    errors = audit(story, before, after, check_blobs=True)
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: chapter08 exact Git blob, two independent source-code blobs, editorial boundaries")
    print("COUNTERMODELS:", len(possibilities()), "logical alternatives; no posterior or physical simulation")
    print("NOT_VERIFIED: origin integrity, terminal position, physical Lean premises, publication")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
