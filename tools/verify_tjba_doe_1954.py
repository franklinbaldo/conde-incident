"""Stream-verify the TJBA January 1954 PDF; never infer legal text from volume custody."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_tjba_doe_1954_01_20261113.json"
EXPECTED = {
    "schema": "conde.archival-volume-custody/v1",
    "document_id": "CGEO-TJBA-DOE-1954-01-01",
    "catalog_node_id": "15747f27fffc00000000000000000023",
    "download_resource_id": "dfdig000000000000000000000009009",
    "pdf_bytes": 124028298,
    "pdf_sha256": "45fb60c544e0115c896706d4265f18b3a7bde551b9134c9bdce36e4c8d0e1237",
    "pdf_magic": "%PDF-1.5",
    "pdf_eof_present": True,
    "pdf_linearized_n": 856,
    "pdf_page_objects_count": 856,
    "archivist_status": "MONTHLY_VOLUME_RETRIEVED_SPECIFIC_LEGAL_PAGES_NOT_INSPECTED",
}
NOT_DEMONSTRATED = (
    "lei_628_1953_text_located_in_this_volume",
    "lei_628_1953_publication_date_proven",
    "annex_vi_text_corrected_against_1953_print",
    "acts_1959_1963_exhaustively_checked",
    "legal_boundary_1963_demonstrated",
    "orbital_constraint_activated",
)
DOWNLOAD_URL = (
    "https://acervo.tjba.jus.br/ConsultaWeb/downResource?"
    "id=dfdig000000000000000000000009009"
)
PAGE_TOKEN = re.compile(rb"/Type\s*/Page(?![A-Za-z])")


def verify_manifest(d: dict) -> list[str]:
    errors = [f"{key}: changed" for key, value in EXPECTED.items() if d.get(key) != value]
    errors += [f"{key}: unverified claim promoted" for key in NOT_DEMONSTRATED if d.get(key) is not False]
    if d.get("download_url") != DOWNLOAD_URL:
        errors.append("download_url changed")
    if d.get("catalog_date_range") != ["1954-01-01", "1954-01-31"]:
        errors.append("catalog period changed")
    if d.get("http_status") != 200 or d.get("mime_type") != "application/pdf":
        errors.append("HTTP/MIME changed")
    if d.get("related_previous_volume_id") != "CGEO-TJBA-DOE-1953-12-01":
        errors.append("December document relation lost")
    if not d.get("next_verification"):
        errors.append("pending visual comparison omitted")
    return errors


def verify_pdf(path: Path, d: dict) -> list[str]:
    h = hashlib.sha256()
    size = 0
    prefix = b""
    suffix = b""
    buffer = b""
    pages = 0
    with path.open("rb") as f:
        while chunk := f.read(65536):
            if not prefix:
                prefix = chunk[:1024]
            suffix = (suffix + chunk)[-256:]
            h.update(chunk)
            size += len(chunk)
            buffer += chunk
            if len(buffer) > 128:
                pages += len(PAGE_TOKEN.findall(buffer[:-128]))
                buffer = buffer[-128:]
    pages += len(PAGE_TOKEN.findall(buffer))
    n = re.search(rb"/Linearized\s+\d+.*?/N\s*(\d+)", prefix, re.DOTALL)
    errors = []
    if size != d["pdf_bytes"]:
        errors.append("size mismatch")
    if h.hexdigest() != d["pdf_sha256"]:
        errors.append("SHA256 mismatch")
    if not prefix.startswith(d["pdf_magic"].encode("ascii")):
        errors.append("PDF magic mismatch")
    if not suffix.rstrip().endswith(b"%%EOF"):
        errors.append("PDF EOF missing")
    if n is None or int(n.group(1)) != d["pdf_linearized_n"]:
        errors.append("linearized /N mismatch")
    if pages != d["pdf_page_objects_count"]:
        errors.append("/Page object count mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    d = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = verify_manifest(d)
    if args.pdf:
        errors.extend(verify_pdf(args.pdf, d))
    for error in errors:
        print("FAIL", error)
    if errors:
        return 1
    print("PASS", d["document_id"], "binary_replay" if args.pdf else "metadata_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
