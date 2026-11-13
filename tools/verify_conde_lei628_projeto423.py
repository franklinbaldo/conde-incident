"""Check primary legislative precursor custody and guard against premature inference.

Offline by default. Optional --dec-pdf verifies the actual 78 MB ArchiDoc
monthly volume byte-for-byte, not just an invented checksum in metadata.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_lei628_projeto423_legislativo_20261113.json"


def validate(d: dict) -> list[str]:
    errors = []
    if d.get("schema") != "conde.legislative-antecedent-custody/v1":
        errors.append("schema")
    s = d.get("source", {})
    if (s.get("sha256"), s.get("bytes"), s.get("pdf_pages")) != (
        "0c68c64c2d70281375c94918ea6b16107399cfdfa0c6ccb36b5dd933b378f4e9", 78342918, 823
    ):
        errors.append("original source fingerprint")
    if s.get("url") != "https://acervo.tjba.jus.br/ConsultaWeb/downResource?id=dfdig000000000000000000000009008":
        errors.append("source url")
    if s.get("facsimile_retrieved") is not True or s.get("original_physical_master_compared") is not False:
        errors.append("facsimile/master scope")
    e = d.get("located_entry", {})
    if (e.get("issue_date_printed"), e.get("meeting_date_in_heading"), e.get("pdf_page_1_based")) != (
        "1953-12-11", "1953-12-07", 317
    ):
        errors.append("issue/meeting/page chronology")
    if e.get("printed_page_number") is not None:
        errors.append("invented printed pagination")
    if e.get("item_heading") != "Redacao final do Projeto de Lei n. 423":
        errors.append("project number")
    for k in ("visual_page_inspected", "embedded_ocr_used_as_locator_only"):
        if e.get(k) is not True:
            errors.append(k)
    for k in ("new_ocr_performed", "full_annex_vi_on_this_page"):
        if e.get(k) is not False:
            errors.append(k)
    a = d.get("related_enacted_law", {})
    if (a.get("law_number"), a.get("sanction_date"), a.get("published_date"), a.get("printed_law_pdf_pages")) != (
        628, "1953-12-30", "1954-01-01", [2, 3]
    ):
        errors.append("enacted law cross-reference")
    if a.get("relationship_status") != "MATCHING_DRAFT_SUBJECT_AND_ARTICLES_NOT_OFFICIALLY_TRACED_BILL_TO_LAW":
        errors.append("unproven legislative lineage promoted")
    if a.get("draft_is_enacted_law") is not False or a.get("separate_independent_historical_law") is not False:
        errors.append("draft counted as law")
    limits = d.get("research_limits", {})
    for k in ("annex_vi_original_located", "jandaira_passage_checked_in_original", "municipal_boundary_1963_proven", "orbital_constraint_activated"):
        if limits.get(k) is not False:
            errors.append(k)
    if limits.get("relevant_to_conde_as_legal_genealogy_only") is not True:
        errors.append("genealogy scope")
    if not d.get("limitations") or not d.get("next_steps"):
        errors.append("required epistemic caveats")
    return errors


def verify_original(path: Path, s: dict) -> list[str]:
    h = hashlib.sha256()
    count = 0
    with path.open("rb") as f:
        magic = f.read(5)
        f.seek(0)
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
            count += len(block)
        f.seek(max(0, count - 8192))
        end = f.read()
    errors = []
    if magic != b"%PDF-": errors.append("PDF magic")
    if b"%%EOF" not in end: errors.append("PDF EOF")
    if count != s["bytes"] or h.hexdigest() != s["sha256"]: errors.append("PDF length/hash")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=MANIFEST)
    p.add_argument("--dec-pdf", type=Path)
    args = p.parse_args()
    d = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(d)
    if not errors and args.dec_pdf:
        errors += verify_original(args.dec_pdf, d["source"])
    for err in errors:
        print("FAIL", err)
    if errors: return 1
    print("PASS primary 1953 legislative precursor, NOT Annex VI or legal boundary for 1963")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
