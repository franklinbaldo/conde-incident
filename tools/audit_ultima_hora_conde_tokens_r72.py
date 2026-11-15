"""Audit a narrowly scoped FBN newspaper text-layer triage (C241-LONTRA-R72).

The pre-existing PDF text layer is an incomplete index, NOT a human reading,
negative finding, event timestamp, eyewitness, nor an orbital observation.
--replay-dir verifies original PDF bytes and reproduces token counts in Ifro.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/archive/ultima_hora_ne_text_layer_triage_R72.json"
EXPECTED_SOURCES = {
    "00472": ("1963-11-09", 10, 5275519, "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece", {"7": 1, "9": 1}),
    "00473": ("1963-11-10", 18, 8298891, "f37e4afa500fe841546a751e562cc799c33c699decb8967b2ae00b45e721e349", {"8": 2}),
    "00474": ("1963-11-11", 10, 4884439, "3d7b9268c1cf45c7700ddf65bfa985c9d17724369d9b0412f9442f4fea87faad", {"3": 2, "5": 1}),
    "00475": ("1963-11-12", 10, 5031193, "88859dfbab5e9590614b684121507c7eb54148028a66d1efb9a3269d6444611f", {"7": 1, "9": 1}),
}
# Each interpretation was checked against the displayed facsimile; not full columns.
EXPECTED_CHECKS = {
    "00472": {
        7: ("TOPONIMO_RECIFE", "Avenida Conde da Boa Vista, Recife (R68)"),
        9: ("TOPONIMO_RECIFE", "Avenida Conde da Boa Vista, Recife (R68)"),
    },
    "00473": {
        8: ("AUTOR_E_FRAGMENTO_OCR", "José Conde em seção de livros; outra ocorrência é fragmento hifenizado de extração, sem referente Conde/BA"),
    },
    "00474": {
        3: ("NOBREZA_E_LOGRADOURO", "conde Marcelo Jacopo em nota; outra ocorrência em referência a rua de anúncio"),
        5: ("CLASSIFICADOS_RECIFE", "Conde da Boa Vista em anúncios classificados do Recife"),
    },
    "00475": {
        7: ("ROTEIRO_RECIFE", "Avenida Conde da Boa Vista em roteiro/anúncio recifense"),
        9: ("PASSATEMPO", "Fruta-de-conde em palavras cruzadas"),
    },
}
EXPECTED_METHOD = {
    "executor": "Ifro; Jatobá somente orquestração com max_memory_mb=128",
    "tool": "pdftotext -layout -f PAGE -l PAGE PDF -",
    "pattern": r"\bconde\b",
    "normalization": "lowercase, Unicode NFD sem diacríticos",
    "pages_text_layer_scanned": 48,
    "new_ocr_performed": False,
    "scope": "triagem lexical das camadas textuais e conferência visual localizada; não leitura integral das colunas",
    "whole_edition_negative_certified": False,
}
EXPECTED_RESULT = {
    "pages_with_exact_token": 7,
    "exact_text_layer_tokens": 9,
    "confirmed_local_event_time": None,
    "whole_edition_negative": False,
    "full_column_reading_completed": False,
    "physical_orbital_constraint_added": False,
}
EXPECTED_LIMITATIONS = [
    "Uma palavra ausente da camada textual não está necessariamente ausente do fac-símile: OCR pré-existente tem falhas de leitura e hifenização.",
    "Classificação dos tokens isolados não substitui inspeção de colunas que não contêm a palavra exata, nem exclui paráfrases do relato.",
    "Os achados em sete páginas não identificam notícia independente sobre Conde/BA; nenhuma hora de evento nem observação individual do NORAD 528/637 foi obtida.",
    "A Tarde e Jornal da Bahia permanecem na fila humana #884 item 2, sem leitura remota integral.",
]
TOP_KEYS = {"schema", "id", "refs_issue", "review_date_utc", "question", "method", "editions", "result", "limitations"}
ED_KEYS = {"edition", "date_printed", "pdf_url", "pdf_sha256", "pdf_bytes", "pdf_pages", "hits_by_pdf_page", "checked_pages"}
CHECK_KEYS = {"pdf_page", "classification", "interpretation", "visual_scope", "event_time_literal", "conde_ba_article_verified", "independent_witness_verified"}
QUESTION = "Triagem do token isolado Conde na camada de texto dos quatro fac-símiles FBN da Última Hora Nordeste, 9–12/11/1963"
VISUAL_SCOPE = "trecho de página inspecionado, sem leitura integral de todas as colunas"


def exact_keys(obj: dict, allowed: set[str], where: str) -> None:
    if not isinstance(obj, dict) or set(obj) != allowed:
        raise ValueError("campos inesperados em " + where)


def validate(doc: dict) -> bool:
    exact_keys(doc, TOP_KEYS, "topo")
    if (doc["schema"], doc["id"], doc["refs_issue"], doc["review_date_utc"], doc["question"]) != (
        "conde.newspaper_text_layer_triage/v1", "C241-LONTRA-R72", 871, "2026-11-15", QUESTION
    ):
        raise ValueError("identidade de fonte/questão modificada")
    if doc["method"] != EXPECTED_METHOD or doc["result"] != EXPECTED_RESULT or doc["limitations"] != EXPECTED_LIMITATIONS:
        raise ValueError("afirmação de método/resultado não revisada")
    editions = doc["editions"]
    if not isinstance(editions, list) or [x.get("edition") for x in editions] != list(EXPECTED_SOURCES):
        raise ValueError("corpus incompleto ou trocado")
    for ed in editions:
        exact_keys(ed, ED_KEYS, "edição")
        number = ed["edition"]
        date, pages, size, digest, hits = EXPECTED_SOURCES[number]
        if (ed["date_printed"], ed["pdf_pages"], ed["pdf_bytes"], ed["pdf_sha256"],
            ed["pdf_url"], ed["hits_by_pdf_page"]) != (
            date, pages, size, digest,
            f"https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_{number}.pdf", hits
        ):
            raise ValueError("custódia/índice divergente em " + number)
        checks = ed["checked_pages"]
        if not isinstance(checks, list) or [x.get("pdf_page") for x in checks] != list(EXPECTED_CHECKS[number]):
            raise ValueError("páginas selecionadas incompletas " + number)
        for entry in checks:
            exact_keys(entry, CHECK_KEYS, "verificação")
            cls, interpretation = EXPECTED_CHECKS[number][entry["pdf_page"]]
            if (entry["classification"], entry["interpretation"], entry["visual_scope"],
                entry["event_time_literal"], entry["conde_ba_article_verified"],
                entry["independent_witness_verified"]) != (
                cls, interpretation, VISUAL_SCOPE, None, False, False
            ):
                raise ValueError("classificação não revisada " + number)
    return True


def replay(pdf_dir: Path) -> dict[str, dict[str, int]]:
    by_edition: dict[str, dict[str, int]] = {}
    for ed, (_, page_count, size, digest, expected_hits) in EXPECTED_SOURCES.items():
        f = pdf_dir / (ed + ".pdf")
        if not f.is_file():
            raise ValueError("original ausente: " + str(f))
        content = f.read_bytes()
        if len(content) != size or hashlib.sha256(content).hexdigest() != digest:
            raise ValueError("SHA/bytes da fonte divergentes: " + ed)
        info = subprocess.run(["pdfinfo", str(f)], check=True, capture_output=True).stdout.decode("utf-8", "replace")
        count = int(next(x.split(":")[1] for x in info.splitlines() if x.startswith("Pages:")))
        if count != page_count:
            raise ValueError("paginação divergente: " + ed)
        hits: dict[str, int] = {}
        for page in range(1, count + 1):
            raw = subprocess.run(
                ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(f), "-"],
                check=True, capture_output=True
            ).stdout.decode("utf-8", "replace").lower()
            normalized = "".join(c for c in unicodedata.normalize("NFD", raw) if not unicodedata.combining(c))
            n = len(re.findall(r"\bconde\b", normalized))
            if n:
                hits[str(page)] = n
        if hits != expected_hits:
            raise ValueError("replay lexical não corresponde: " + ed)
        by_edition[ed] = hits
    return by_edition


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay-dir", type=Path)
    args = parser.parse_args()
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    if args.replay_dir:
        replay(args.replay_dir)
    print("R72: PASS; 7 páginas com hits e 9 tokens textuais; sem negativo de edição")
