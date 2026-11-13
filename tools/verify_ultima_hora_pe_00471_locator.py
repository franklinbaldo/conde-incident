"""Validate the scoped FBN edition locator without promoting uninspected text."""
from __future__ import annotations
import argparse
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/ultima_hora_pe_00471_1963_locator_20261113.json"
PDF = "https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf"
CATALOG = "https://memoria.bn.gov.br/DocReader/765147/5339"
PRIOR_CATALOG = "https://memoria.bn.gov.br/DocReader/765147/5756"
PAGE8_CANDIDATE = "https://memoria.bn.gov.br/DocReader/765147/5346"

def validate(d: dict) -> list[str]:
    errors = []
    fixed = {
        "schema": "conde.archive-locator-negative/v1",
        "id": "DOC-UH-PE-1963-00471-LOCATOR",
        "publication": "Ultima Hora (PE) - 1962 a 1964",
        "year": 1963, "edition": "00471",
        "requested_printed_page": 8,
        "requested_date": "1963-11-08",
        "catalog_url": CATALOG,
        "earlier_catalog_url": PRIOR_CATALOG,
        "earlier_catalog_selected_edition": "00507",
        "docreader_selected_edition": "00471",
        "docreader_first_physical_id": 5339,
        "docreader_last_physical_id": 5346,
        "docreader_requested_page8_candidate_id": 5346,
        "docreader_requested_page8_candidate_url": PAGE8_CANDIDATE,
        "docreader_html_http_status": 200,
        "docreader_page8_raster_retrieved": False,
        "docreader_physical_ids_are_not_printed_pages": True,
        "catalog_identifier": "765147",
        "pdf_exact_url": PDF,
        "pdf_head_status": 403,
        "archive_cdx_result": [],
    }
    for key, expected in fixed.items():
        if d.get(key) != expected:
            errors.append(key)
    for key in ("pdf_sha256", "pdf_size_bytes", "page_image_sha256"):
        if d.get(key, "MISSING") is not None:
            errors.append(key + ":unsupported-by-bytes")
    for key in (
        "original_text_verified", "page_8_inspected",
        "four_metre_hole_verified", "orbital_constraint_activated",
    ):
        if d.get(key) is not False:
            errors.append(key + ":not-evidenced")
    scope = str(d.get("archive_cdx_scope", ""))
    if "not universal absence" not in scope or "EXACT" not in scope:
        errors.append("cdx-negative-scope")
    if "unverified" not in str(d.get("claim_limitation", "")):
        errors.append("unverified-secondary-reading")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("checked_utc_date", ""))):
        errors.append("checked-date")
    deps = d.get("dependencies")
    if not isinstance(deps, list) or set(deps) != {
        "franklinbaldo/lontra#6", "franklinbaldo/conde-incident#494"
    }:
        errors.append("dependencies")
    return errors

def selected_edition(html_text: str) -> str | None:
    """Read selected DocReader folder, not an edition merely in the sidebar list."""
    m = re.search(r'<span id="PastaTxt" title="[^"]*Edição (\d{5})"', html_text)
    return m.group(1) if m else None


def live_check(d: dict, opener=urllib.request.urlopen) -> dict:
    """Explicit optional replay; HTTP 403 and empty CDX may change over time."""
    result = {}
    for label, url, method in (
        ("pdf", d["pdf_exact_url"], "HEAD"),
        ("cdx", d["archive_cdx_exact_url"], "GET"),
    ):
        req = urllib.request.Request(url, method=method, headers={
            "User-Agent": "CondeArchiveLedger/1.0"
        })
        try:
            with opener(req, timeout=20) as resp:
                result[label + "_http"] = resp.status
                if label == "cdx":
                    result["cdx_result"] = json.loads(resp.read(1024 * 1024))
        except urllib.error.HTTPError as e:
            result[label + "_http"] = e.code
        except Exception as e:
            result[label + "_error"] = str(e)[:200]
    for label, url in (
        ("docreader_first", d["catalog_url"]),
        ("docreader_last", d["docreader_requested_page8_candidate_url"]),
        ("docreader_old", d["earlier_catalog_url"]),
    ):
        req = urllib.request.Request(url, headers={"User-Agent": "CondeArchiveLedger/1.0"})
        try:
            with opener(req, timeout=20) as resp:
                result[label + "_http"] = resp.status
                result[label + "_selected"] = selected_edition(
                    resp.read(400_000).decode("utf-8", errors="replace")
                )
        except Exception as e:
            result[label + "_error"] = str(e)[:200]
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    d = json.loads(args.manifest.read_text(encoding="utf8"))
    errors = validate(d)
    if args.live:
        print(json.dumps(live_check(d), indent=2))
    if errors:
        print("FAIL: " + ", ".join(errors))
        return 1
    print("PASS: located only in FBN index; page 8 unverified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
