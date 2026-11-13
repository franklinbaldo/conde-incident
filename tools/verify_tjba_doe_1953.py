"""Custody gate for TJBA ArchiDoc December 1953 DOE (not a legal transcription)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_tjba_doe_1953_12_20261113.json"
EXPECTED = {
    "schema": "conde.archival-volume-custody/v1",
    "document_id": "CGEO-TJBA-DOE-1953-12-01",
    "catalog_node_id": "15747f27e5bd40000000000000000023",
    "download_resource_id": "dfdig000000000000000000000009008",
    "pdf_bytes": 78342918,
    "pdf_sha256": "0c68c64c2d70281375c94918ea6b16107399cfdfa0c6ccb36b5dd933b378f4e9",
    "pdf_magic": "%PDF-1.5",
    "pdf_eof_present": True,
    "pdf_linearized_n": 823,
    "pdf_pages_tree_count": 823,
    "pdf_page_objects_count": 823,
    "archivist_status": "MONTHLY_VOLUME_RETRIEVED_SPECIFIC_LEGAL_PAGES_NOT_INSPECTED",
}
MUST_REMAIN_FALSE = (
    "lei_628_1953_text_located_in_this_volume",
    "lei_628_1953_publication_date_proven",
    "annex_vi_text_corrected_against_1953_print",
    "acts_1959_1963_exhaustively_checked",
    "legal_boundary_1963_demonstrated",
    "orbital_constraint_activated",
)


def verify_manifest(data: dict) -> list[str]:
    """Pin the source identity and block undocumented historical promotion."""
    errors: list[str] = []
    for key, value in EXPECTED.items():
        if data.get(key) != value:
            errors.append(f"{key}: expected {value!r}")
    for key in MUST_REMAIN_FALSE:
        if data.get(key) is not False:
            errors.append(f"{key}: unverified conclusion must remain false")
    if data.get("http_status") != 200 or data.get("mime_type") != "application/pdf":
        errors.append("source response HTTP/MIME not preserved")
    if data.get("catalog_date_range") != ["1953-12-01", "1953-12-31"]:
        errors.append("month scope changed")
    url = data.get("download_url", "")
    if url != ("https://acervo.tjba.jus.br/ConsultaWeb/downResource?"
               "id=dfdig000000000000000000000009008"):
        errors.append("download URL altered")
    if not isinstance(data.get("next_verification"), list) or not data["next_verification"]:
        errors.append("unresolved document work omitted")
    return errors


def verify_pdf(path: Path, data: dict) -> list[str]:
    """Replay binary integrity, streaming instead of buffering the 78 MB PDF."""
    digest = hashlib.sha256()
    size = 0
    prefix = b""
    suffix = b""
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            if not prefix:
                prefix = chunk[:8]
            suffix = (suffix + chunk)[-1024:]
            digest.update(chunk)
            size += len(chunk)
    errors = []
    if size != data["pdf_bytes"]:
        errors.append(f"byte-count mismatch: {size}")
    if digest.hexdigest() != data["pdf_sha256"]:
        errors.append("SHA-256 mismatch")
    if prefix != data["pdf_magic"].encode("ascii"):
        errors.append("PDF magic mismatch")
    if not suffix.rstrip().endswith(b"%%EOF"):
        errors.append("PDF EOF missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pdf", type=Path, help="downloaded PDF for full byte replay")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = verify_manifest(data)
    if args.pdf:
        errors.extend(verify_pdf(args.pdf, data))
    for error in errors:
        print("FAIL", error)
    if errors:
        return 1
    print("PASS", data["document_id"], "binary_replay" if args.pdf else "metadata_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
