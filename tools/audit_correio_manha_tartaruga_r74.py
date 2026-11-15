"""C241-R74: preserve a partial 9 Nov Correio da Manhã reading and prevent conflation."""

import argparse
import hashlib
import json
from pathlib import Path

MANIFEST = (Path(__file__).resolve().parents[1] / "research" / "archive" /
            "conde_correio_manha_1963_11_09_C241_TARTARUGA_R74.json")
SOURCE_URL = "https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21657.pdf"
SHA256 = "a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0"
BYTES = 22546215


def require(ok, why):
    if not ok:
        raise ValueError(why)


def validate(doc):
    require(set(doc) == {"schema", "id", "issue", "checked_utc_date", "source", "article", "scope", "notes"}, "root keys")
    require((doc["schema"], doc["id"], doc["issue"]) ==
            ("conde.local_clock_press_custody/v1", "C241-TARTARUGA-R74", 871), "identity")
    source = doc["source"]
    expected_source = {
        "title": "Correio da Manhã", "city": "Rio de Janeiro",
        "edition_date_visual": "1963-11-09", "edition_number_visual": "21.657",
        "collection_edition": "089842/21657", "original_url": SOURCE_URL,
        "format": "application/pdf", "bytes": BYTES, "sha256": SHA256,
        "pdf_page_count": 28, "cover_pdf_page": 1, "article_pdf_page": 5,
        "article_printed_page": 5, "article_title": "OBJETO MISTERIOSO CAI EM RIO DE SP",
        "article_lead_credit": "IGUAPE (Do enviado especial da sucursal SP)",
        "article_status": "ARTICLE_VISUALLY_READ", "full_page_5_read": False,
        "full_edition_read": False,
    }
    require(source == expected_source, "source custody/reading altered")
    article = doc["article"]
    expected_article = {
        "reported_location": "IGUAPE_SP_RIO_PEROPAVA",
        "reported_relative_day_literal": "na tarde do 29 último",
        "inferred_reported_day": "1963-10-29",
        "day_inference_is_not_a_verbatim_date": True,
        "named_reported_witnesses_iguape": ["Ruth de Souza", "Antônio de Souza", "Justino Nunes da Veiga"],
        "named_official_iguape": "Carlos Ariovaldo",
        "conde_eyewitness": None, "conde_event_time_literal": None,
        "conde_event_link_claimed": False,
        "reporting_classification": "IGUAPE_CONTEXT_ONLY_NOT_CONDE",
        "reporter_identity_authenticated": False, "independent_conde_observation": False,
        "orbital_constraint_activated": False,
    }
    require(article == expected_article, "Iguape/Conde article claim altered")
    scope = doc["scope"]
    expected_scope = {
        "cover_verified_date_and_number_only": True,
        "article_read_only_on_page_5": True,
        "all_other_articles_not_certified": True,
        "remaining_pdf_pages_not_fully_reviewed": list(range(1, 29)),
        "correio_10_nov_full_edition_read": False,
        "other_page_negative_not_asserted": True,
        "publication_date_is_not_event_time": True,
    }
    require(scope == expected_scope, "full-reading scope/negative incorrectly promoted")
    require(isinstance(doc["notes"], list) and len(doc["notes"]) == 5, "notes")
    return True


def validate_pdf(path):
    path = Path(path)
    require(path.is_file() and path.stat().st_size == BYTES, "PDF bytes/missing")
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    require(digest.hexdigest() == SHA256, "PDF SHA-256 mismatch")
    with path.open("rb") as f:
        require(f.read(5) == b"%PDF-", "PDF signature")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", type=Path)
    args = p.parse_args()
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")))
    if args.pdf:
        validate_pdf(args.pdf)
    print("C241-R74: PASS (custody and scope; only cover + one article read)")


if __name__ == "__main__":
    main()
