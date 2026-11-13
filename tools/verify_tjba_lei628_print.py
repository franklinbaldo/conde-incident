"""Check the Conde law 628/1953 page citation and optionally replay the primary PDF."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_tjba_doe_1954 import verify_pdf
MANIFEST = ROOT / "research/archive/conde_lei628_1953_doe_pagelevel_20261113.json"
VOLUME = ROOT / "research/archive/conde_tjba_doe_1954_01_20261113.json"
IDENTITY = {
    "schema": "conde.archival-page-evidence/v1",
    "document_id": "CGEO-TJBA-DOE-1954-01-01-L628-P1-P2",
    "parent_volume_document_id": "CGEO-TJBA-DOE-1954-01-01",
    "issue_date": "1954-01-01",
    "issue_number_as_printed": 3259,
    "printed_pages_with_law": [1, 2],
    "pdf_pages_with_law": [2, 3],
    "law_number": 628,
    "law_sanction_date": "1953-12-30",
    "law_publication_date": "1954-01-01",
    "epistemic_status": "PRIMARY_PRINTED_LAW_PUBLICATION_FACSIMILE_LOCATED",
    "visual_inspection": "DIRECTLY_INSPECTED_JOURNAL_FACSIMILE_PAGES_2_AND_3",
}
STILL_PENDING = (
    "annex_vi_page_identified",
    "anomalous_jandaira_line_checked_against_original",
    "acts_1959_to_1963_exhaustively_checked",
    "legal_boundary_1963_demonstrated",
    "orbital_constraint_activated",
)


def verify_record(d: dict, parent: dict) -> list[str]:
    errors = [f"{key}: identity mismatch" for key, value in IDENTITY.items() if d.get(key) != value]
    errors.extend(f"{key}: premature promotion" for key in STILL_PENDING if d.get(key) is not False)
    if d.get("source_url") != parent.get("download_url"):
        errors.append("parent download URL mismatch")
    for old, new in (("pdf_sha256", "source_pdf_sha256"),
                     ("pdf_bytes", "source_pdf_bytes"),
                     ("pdf_page_objects_count", "source_pdf_pages")):
        if parent.get(old) != d.get(new):
            errors.append(f"parent {old} mismatch")
    if d.get("source_family") != "TJBA_ArchiDoc_digitization_of_Bahia_DOE":
        errors.append("independence family changed")
    if d.get("articles_located") != [1, 2, 3, 4, 5]:
        errors.append("article range changed")
    if len(d.get("printed_placement", [])) != 2:
        errors.append("printed layout anchor missing")
    return errors


def verify_replay(pdf: Path, parent: dict) -> list[str]:
    errors = verify_pdf(pdf, parent)
    if errors:
        return errors
    exe = shutil.which("pdftotext")
    if not exe:
        return ["pdftotext unavailable for page-content replay"]
    excerpts = []
    for page in (2, 3):
        result = subprocess.run([exe, "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
                                capture_output=True, text=True, check=False)
        if result.returncode:
            return [f"pdftotext page {page} failed: exit {result.returncode}"]
        excerpts.append(unicodedata.normalize("NFKD", result.stdout).encode("ascii", "ignore").decode().lower())
    if "divisao territorial administrativa" not in excerpts[0]:
        errors.append("law subject not located in PDF page 2 embedded OCR")
    if not re.search(r"art\.?\s*5\.?\s*.*?revogam", excerpts[1], flags=re.S):
        errors.append("concluding art. 5 not located in PDF page 3 embedded OCR")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, help="optional replay with parent PDF and poppler pdftotext")
    args = parser.parse_args()
    d = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(VOLUME.read_text(encoding="utf-8"))
    errors = verify_record(d, parent)
    if args.pdf:
        errors += verify_replay(args.pdf, parent)
    for err in errors:
        print("FAIL", err)
    if errors:
        return 1
    print("PASS", d["document_id"], "PDF replay" if args.pdf else "citation metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
