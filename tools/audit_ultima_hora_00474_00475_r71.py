"""Fail-closed review of the two scoped Última Hora panoramas (11–12 Nov 1963).

This audits the *claims and source metadata* in R71. It does not execute
historical OCR, infer absence in unread columns, or inspect external files.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research/archive/ultima_hora_ne_00474_00475_page_review_R71.json"
MANIFEST = ROOT / "research/archive/ultima_hora_ne_nov1963_C241_LONTRA_R67.json"
EXPECTED = {
    "00474": ("1963-11-11", 4884439, "3d7b9268c1cf45c7700ddf65bfa985c9d17724369d9b0412f9442f4fea87faad"),
    "00475": ("1963-11-12", 5031193, "88859dfbab5e9590614b684121507c7eb54148028a66d1efb9a3269d6444611f"),
}
TOPICS = {
    "00474": [
        "capa verificada em R67", "politica, Olinda e notícias locais",
        "disputa partidária, governo e trabalho", "sociedade, homenagens, cultura e cinema",
        "anúncios classificados", "investigação policial e homicídio em Recife",
        "futebol e resultados da Paraíba", "automobilismo e notícias esportivas",
        "jogos e comentários de futebol", "futebol e fotografia esportiva",
    ],
    "00475": [
        "capa verificada em R67", "reformas, política e funcionalismo",
        "Assembleia, vencimentos e governo", "JK, coligação partidária e política nacional",
        "notícia sobre Polet I e corrida espacial; política externa",
        "investigação policial e crime dos Aflitos",
        "geólogos, petróleo, economia e crônica de Stanislaw Ponte Preta",
        "classificados e serviços", "sociedade, programação de TV, cinema e passatempos",
        "futebol e entrevista esportiva",
    ],
}


# These literal editorial statements are part of the audited interpretation.
# Source hashes validate PDFs, not claims later typed into these free-text fields.
EXPECTED_METHOD = {
    "executor": "Ifro",
    "jatoba": "apenas orquestração, max_memory_mb=128",
    "downloaded_and_hashed_on_ifro": True,
    "visual_review": "18 páginas internas renderizadas a 100 dpi, montagens de três páginas, manchetes e diagramação",
    "pdf_text_extraction": "não usado para inferências negativas (erros de encoding PDFXC30)",
    "ocr_performed": False,
    "full_body_reading": False,
}
EXPECTED_CONTEXT = {
    "edition": "00475",
    "pdf_page": 5,
    "headline": "URSS no Páreo para Conquista da Lua: 'Polet I' Rasga Caminho Aos 'Vostoks'",
    "classification": "notícia espacial geral, sem vínculo documental confirmado com Conde ou medição dos NORAD 527/528/529/637",
    "orbital_observation": False,
    "local_event_time": False,
}
EXPECTED_LIMITATIONS = [
    "As 18 internas de 11–12/11 foram vistas em panoramas; nenhuma coluna foi declarada integralmente lida.",
    "Não se identificou nas manchetes examinadas hora local ou testemunha independente, sem concluir ausência em qualquer edição completa.",
    "A nota sobre Polet I não mede o NORAD 528 e não é confirmação de queda em Conde.",
    "Páginas internas das quatro edições têm capa/panorama conferidos; leitura ampliada das colunas permanece pendente.",
    "Acesso remoto aos jornais baianos A Tarde/Jornal da Bahia continua dependente da fila humana #884 item 2.",
]
TOP_FIELDS = {
    "schema", "id", "refs_issue", "review_date_utc", "scope",
    "institution", "collection_id", "newspaper", "method", "editions",
    "contextual_article", "result", "limitations",
}
EDITION_FIELDS = {
    "edition", "date_printed", "pdf_url", "pdf_sha256", "pdf_bytes",
    "pdf_pages", "original_custody_manifest", "integrity_rechecked_on_ifro", "pages",
}
PAGE_FIELDS = {
    "pdf_page", "status", "review_scope", "topic_overview",
    "event_time_literal", "conde_ba_article_verified",
    "independent_witness_verified", "full_page_body_read",
}


def require_fields(value: dict, keys: set[str], path: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("unexpected fields at " + path)


def validate(d: dict, manifest: dict | None = None) -> bool:
    require_fields(d, TOP_FIELDS, "document")
    if d.get("review_date_utc") != "2026-11-15":
        raise ValueError("review date changed")
    if (d.get("schema"), d.get("id"), d.get("refs_issue"), d.get("scope")) != (
        "conde.newspaper_page_review/v1", "C241-LONTRA-R71", 871, "PANORAMA_MANCHETES_LAYOUT"
    ):
        raise ValueError("incorrect review identity or scope")
    if (d.get("institution"), d.get("collection_id"), d.get("newspaper")) != (
        "Fundação Biblioteca Nacional", "765147", "Última Hora, edição Nordeste (PE)"
    ):
        raise ValueError("incorrect institution")
    method = d["method"]
    if method != EXPECTED_METHOD:
        raise ValueError("unsupported method claim")
    if manifest is None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["id"] != "C241-LONTRA-R67":
        raise ValueError("custody manifest identity")
    by_ed = {x["edition"]: x for x in manifest["issues"]}
    editions = d["editions"]
    if len(editions) != 2 or [x["edition"] for x in editions] != list(EXPECTED):
        raise ValueError("edition count/order")
    for ed in editions:
        require_fields(ed, EDITION_FIELDS, "edition")
        num = ed["edition"]
        date, size, digest = EXPECTED[num]
        url = f"https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_{num}.pdf"
        if (ed.get("date_printed"), ed.get("pdf_bytes"), ed.get("pdf_sha256"),
            ed.get("pdf_pages"), ed.get("pdf_url")) != (date, size, digest, 10, url):
            raise ValueError("incorrect custody " + num)
        parent = by_ed[num]
        if (parent["date"], parent["pdf_bytes"], parent["pdf_sha256"],
            parent["pdf_pages"], parent["pdf_url"]) != (date, size, digest, 10, url):
            raise ValueError("conflict with R67 original custody " + num)
        if ed["original_custody_manifest"] != "research/archive/ultima_hora_ne_nov1963_C241_LONTRA_R67.json":
            raise ValueError("incorrect manifest path")
        if ed["integrity_rechecked_on_ifro"] is not True:
            raise ValueError("binary not verified on executor")
        pages = ed["pages"]
        if len(pages) != 10 or [p["pdf_page"] for p in pages] != list(range(1, 11)):
            raise ValueError("page denominator " + num)
        for idx, page in enumerate(pages):
            require_fields(page, PAGE_FIELDS, f"page {num}/{idx+1}")
            scope = "CAPA_VERIFICADA_R67" if idx == 0 else "PANORAMA_MANCHETES_LAYOUT"
            if (page.get("status"), page.get("review_scope"), page.get("full_page_body_read"),
                page.get("event_time_literal"), page.get("conde_ba_article_verified"),
                page.get("independent_witness_verified")) != (
                "EXAMINADA", scope, False, None, False, False
            ):
                raise ValueError(f"unsupported source claim {num}/p{idx+1}")
            if page.get("topic_overview") != TOPICS[num][idx]:
                raise ValueError(f"topic changed without source re-review {num}/p{idx+1}")
    if d["contextual_article"] != EXPECTED_CONTEXT:
        raise ValueError("contextual item changed without source re-review")
    result = d["result"]
    required = {
        "new_internal_pages_visually_reviewed": 18,
        "total_pages_with_cover_or_panorama_across_four_editions": 48,
        "pages_remaining_for_panorama_of_all_four_editions": 0,
        "confirmed_independent_event_time": None,
        "independent_eyewitness": None,
        "source_chain": "UNDETERMINED",
        "whole_edition_no_article_claim": False,
        "whole_edition_no_time_claim": False,
        "full_columns_review_completed": False,
        "physical_orbital_constraint_added": False,
    }
    require_fields(result, set(required), "result")
    for key, value in required.items():
        if result[key] != value:
            raise ValueError("epistemic promotion " + key)
    if d["limitations"] != EXPECTED_LIMITATIONS:
        raise ValueError("limitations changed without source re-review")
    return True


if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("PASS R71: 18 internal panoramas; no whole-edition negative, hour, witness or orbit")
