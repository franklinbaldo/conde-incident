#!/usr/bin/env python3
"""Verify exact bytes of 1964 Soviet yearbook facsimile; no OCR orbital inference."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/soviet_bse1964_1963_003_C241_LONTRA_R48.json"


def verify_pdf(path: Path, expected_bytes: int, expected_sha256: str,
               expected_pages: int = 70, check_page_count: bool = True) -> None:
    sha = hashlib.sha256()
    count = 0
    head = b""
    tail = b""
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            if not head:
                head = chunk[:8]
            tail = (tail + chunk)[-2048:]
            count += len(chunk)
            sha.update(chunk)
    if count != expected_bytes:
        raise ValueError(f"PDF byte-count mismatch: {count} != {expected_bytes}")
    if sha.hexdigest() != expected_sha256:
        raise ValueError("PDF SHA-256 mismatch")
    if not head.startswith(b"%PDF-"):
        raise ValueError("Not a PDF header")
    if b"%%EOF" not in tail:
        raise ValueError("Missing PDF EOF marker")
    if check_page_count:
        result = subprocess.run(["pdfinfo", str(path)], check=True,
                                capture_output=True, text=True, timeout=30)
        match = re.search(r"^Pages:\s*(\d+)\s*$", result.stdout, re.M)
        if not match or int(match.group(1)) != expected_pages:
            raise ValueError("Scanned section must contain exactly 70 PDF pages")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path, help="Original section PDF downloaded from Istmat")
    args = parser.parse_args()
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    c = m["document_custody"]
    verify_pdf(args.pdf, c["pdf_bytes"], c["pdf_sha256"], c["pdf_page_count"])
    print(f"VERIFIED original scanned section: {c['pdf_bytes']} bytes; "
          f"SHA-256 {c['pdf_sha256']}; {c['pdf_page_count']} pages.")
    print("Historical row reading is from visual inspection of printed p.503, "
          "PDF page 7. File integrity alone does NOT certify orbital provenance.")


if __name__ == "__main__":
    main()
