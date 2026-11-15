"""C241-G86: custody and anti-overclaim checks for Última Hora RJ."""
import argparse
import hashlib
import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/archive/ultima_hora_rj_1963_11_09_10_C241_CASTOR_G86.json"
SHA256 = "320aeb075b99fc6f2884904d9e1aa801b9d3f6be2b131ded30093caaaa6ce352"
BYTES = 10778040
URL = "https://hemeroteca-pdf.bn.gov.br/386030/per386030_1963_04200.pdf"

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(doc):
    require(doc["schema"] == "conde.local_clock_press_custody/v1", "schema")
    require(doc["id"] == "C241-CASTOR-G86" and doc["issue"] == 871, "identity")
    s = doc["source"]
    require(s["collection"] == "386030" and s["edition"] == "04200", "collection")
    require(s["date_from_cover"] == "1963-11-09" and s["day_from_cover"] == "sábado", "cover")
    require((s["original_url"], s["pdf_bytes"], s["sha256"], s["pdf_page_count"]) == (URL, BYTES, SHA256, 16), "pdf custody")
    a = doc["adjacent_catalog"]
    require(a["friday_edition"] == "04199" and a["monday_edition"] == "04201", "adjacency")
    require(a["monday_date_from_cover"] == "1963-11-11" and a["monday_sha256"] == "b7ce4a3437633fe712fc49df6a0b1f86289912360830b9c979afea1ffa8bd134", "Monday custody")
    require(a["nov10_regular_edition"] == "NOT_LOCATED_BETWEEN_ADJACENT_CATALOG_ENTRIES", "10 Nov unverified")
    require(a["nov10_special_edition"] == "NOT_ESTABLISHED" and a["nov10_full_edition_read"] is False and a["absence_proven_all_issues"] is False, "10 Nov unsupported negative")
    c=doc["coverage"]
    require(c["all_pages_seen_as_panorama"] is True and c["full_columns_read"] is False and c["full_issue_negative_certified"] is False, "scope")
    require(c["locally_verified_independent_conde_event_time"] is None and c["independent_eyewitness_verified"] is False and c["ocr_only_negative_used"] is False, "event evidence")
    pages=c["pages"]
    require(len(pages)==16 and [p["pdf_page"] for p in pages]==list(range(1,17)), "pages count and order")
    for p in pages:
        require(p["visual_inspection"]=="FULL_PAGE_PANORAMA_AT_1450PX", "panorama")
        require(p["small_text_legibility"]=="PARTIAL" and p["column_by_column_complete"] is False and p["whole_page_negative_certified"] is False, "no false page negative")
        require(p["conde_event_time_observed"] is None, "invented time")
    i=doc["interpretation"]
    require(i=={"transmission_clock_fbis":"UNRESOLVED","event_clock":"UNDETERMINED","orbit_exclusion_licensed":False,"active_constraint":False,"impact_probability":None,"theta_changed":False}, "unlicensed orbital inference")
    require(all(not x["relevant_event_witness"] for x in doc["related_headlines"]), "article-to-witness conflation")
    return True

def validate_pdf(path):
    p=Path(path)
    require(p.is_file() and p.stat().st_size==BYTES,"PDF size/missing")
    digest=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            digest.update(chunk)
    require(digest.hexdigest()==SHA256, "PDF SHA-256 mismatch")
    with p.open("rb") as f:require(f.read(5)==b"%PDF-", "PDF magic")
    return True

def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--pdf", type=Path)
    args=arg.parse_args()
    validate(json.loads(MANIFEST.read_text(encoding="utf8")))
    if args.pdf:validate_pdf(args.pdf)
    print("G86 PASS: verified source custody and partial-reading limits")

if __name__=="__main__":
    main()
