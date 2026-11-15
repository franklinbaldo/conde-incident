"""C241-R72: audit an original newspaper article without inventing an event hour.

The fixed expectations refer to the visually inspected FBN facsimile page 8;
the script checks *custody claims*, not scientific truth.
"""
import argparse
import hashlib
import json
from pathlib import Path

MANIFEST = (Path(__file__).resolve().parents[1] / "research" / "archive" /
            "conde_correio_manha_1963_11_10_C241_TARTARUGA_R72.json")
SOURCE_URL = "https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21658.pdf"
SHA256 = "75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3"
BYTES = 62742698


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(doc):
    require(doc["schema"] == "conde.local_clock_press_custody/v1", "schema")
    require(doc["id"] == "C241-TARTARUGA-R72" and doc["issue"] == 871, "identity")
    source = doc["source"]
    reporting = doc["reporting"]
    limits = doc["limitations"]
    for k, expected in {
        "title": "Correio da Manhã",
        "date": "1963-11-10",
        "edition_collection": "089842/21658",
        "original_url": SOURCE_URL,
        "format": "application/pdf",
        "bytes": BYTES,
        "sha256": SHA256,
        "pdf_page_count": 97,
        "original_pdf_page": 8,
        "printed_page": 8,
        "article_title": "PRECIPITAÇÃO DE OBJETOS CONTINUA",
        "article_scope": "PAGE_8_UPPER_LEFT_TWO_COLUMNS",
        "visually_read": True,
        "reading_status": "LIDO_SEM_HORA",
        "reading_status_scope": "ONLY_ARTICLE_NOT_FULL_EDITION",
        "byline": None,
    }.items():
        require(source[k] == expected, f"source.{k}")

    for k, expected in {
        "event_local_clock": None,
        "event_utc_clock": None,
        "eyewitness_name": None,
        "direct_independent_event_observation": False,
        "newspaper_title_outside_diarios_associados": "CORREIO_DA_MANHA",
        "article_source_independence": "UNDETERMINED",
        "official_original_denials_recovered": False,
        "attributed_skeptical_assessment": "OBSERVATORIO_NACIONAL",
        "article_position": "NO_SPECIFIC_TIME_OF_CONDE_FALL",
    }.items():
        require(reporting[k] == expected, f"reporting.{k}")
    require(reporting["attributed_denials"] ==
            ["FAB_SERVICO_BUSCAS_SALVAMENTO", "BAHIA_GOVERNMENT"],
            "reported denials must stay attributions")
    require(reporting["other_localities_not_conde"] ==
            ["IGUAPE_SAO_PAULO", "OFF_CALIFORNIA_COAST"],
            "do not conflate localities")
    for k, expected in {
        "event_time_confirmed": False,
        "direct_witness_confirmed": False,
        "orbital_constraint_activated": False,
        "pdf_other_pages_exhaustively_read": False,
        "article_proves_nonoccurrence": False,
        "no_external_contact": True,
    }.items():
        require(limits[k] == expected, f"limitations.{k}")
    return True


def validate_pdf(path):
    path = Path(path)
    require(path.is_file(), "PDF missing")
    require(path.stat().st_size == BYTES, "PDF byte length mismatch")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    require(digest.hexdigest() == SHA256, "PDF digest mismatch")
    require(path.read_bytes()[:5] == b"%PDF-", "PDF signature mismatch")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, help="FBN full original facsimile to rehash")
    args = parser.parse_args()
    record = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(record)
    if args.pdf:
        validate_pdf(args.pdf)
    print("C241-R72: PASS (custody and claim boundaries; historical claims not proven)")


if __name__ == "__main__":
    main()
