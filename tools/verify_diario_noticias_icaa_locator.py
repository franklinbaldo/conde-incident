"""Cross-check 1963 ICAA holding against an older, similarly named FBN collection.

Offline by default: catalog metadata is not a facsimile or evidence of Conde.
An optional live check only verifies the scope label of the FBN index.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/diario_noticias_salvador_1963_icaa_1110862_locator.json"

def validate(d: dict) -> list[str]:
    e = []
    if d.get("schema") != "conde.archival-holdings-disambiguation/v1":
        e.append("schema")
    c = d.get("catalog", {})
    b = d.get("similarly_named_fbn_docreader", {})
    t = d.get("research_target", {})
    i = d.get("independence", {})
    if (c.get("record_id"), c.get("url")) != ("1110862", "https://icaa.mfah.org/s/en/item/1110862"):
        e.append("ICAA identity")
    if (c.get("title"), c.get("date"), c.get("printed_page")) != ("Arte popular", "1963-11-05", 2):
        e.append("ICAA bibliographic identity")
    if (c.get("journal"), c.get("journal_city"), c.get("digitized_item_located_at")) != (
        "Diário de Notícias", "Salvador", "Fundação Biblioteca Nacional"
    ):
        e.append("ICAA holding provenance")
    if c.get("direct_jatoba_http_status") != 403 or c.get("direct_jatoba_response_kind") != "access_interstitial_not_facsimile":
        e.append("direct access event")
    if c.get("newspaper_image_retrieved") is not False or c.get("newspaper_image_sha256") is not None:
        e.append("unread ICAA item promoted")
    if (b.get("collection_id"), b.get("declared_year_range"), b.get("http_status")) != ("098167", [1876, 1909], 200):
        e.append("wrong FBN catalog")
    if b.get("url") != "https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=098167&pagfis=95":
        e.append("FBN URL")
    if b.get("covers_target_1963") is not False or b.get("not_equivalent_to_icaa_digitized_item") is not True:
        e.append("false FBN catalog equivalence")
    if b.get("html_image_element_counts_as_facsimile") is not False:
        e.append("HTML incorrectly promoted to image")
    if t.get("target_dates") != ["1963-11-08", "1963-11-09"]:
        e.append("target dates")
    if any(t.get(k) is not False for k in ("target_editions_located", "target_article_read", "text_corroboration_of_conde_event")):
        e.append("newspaper not recovered")
    if t.get("newspaper_pdf_sha256") is not None:
        e.append("fabricated newspaper digest")
    if i.get("catalog_article_is_about_conde") is not False or i.get("independent_conde_observation_added") is not False:
        e.append("false independent observation")
    if i.get("orbital_constraint_activated") is not False:
        e.append("false orbital constraint")
    if not d.get("limitations"):
        e.append("missing limitations")
    return e

def verify_fbn_live(d: dict) -> list[str]:
    b = d["similarly_named_fbn_docreader"]
    req = Request(b["url"], headers={"User-Agent": "Mozilla/5.0 (archival catalog audit)"})
    try:
        with urlopen(req, timeout=25) as rsp:
            body = rsp.read(2_000_000).decode("utf-8", errors="replace")
            if rsp.status != 200:
                return [f"FBN HTTP {rsp.status}"]
        if not re.search(r"Diario de Noticias \(BA\)\s*-\s*1876 a 1909", body, flags=re.I):
            return ["FBN scope label not located"]
    except Exception as exc:
        return [f"FBN unavailable: {type(exc).__name__}"]
    return []

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--live-fbn", action="store_true")
    args = ap.parse_args()
    d = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(d)
    if not errors and args.live_fbn:
        errors += verify_fbn_live(d)
    for error in errors:
        print("FAIL", error)
    if errors:
        return 1
    print("PASS bibliographic crossholding; 1963 newspaper facsimile NOT_RETRIEVED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
