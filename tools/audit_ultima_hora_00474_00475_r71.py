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


def validate(d: dict, manifest: dict | None = None) -> bool:
    if (d.get("schema"), d.get("id"), d.get("refs_issue"), d.get("scope")) != (
        "conde.newspaper_page_review/v1", "C241-LONTRA-R71", 871, "PANORAMA_MANCHETES_LAYOUT"
    ):
        raise ValueError("incorrect review identity or scope")
    if (d.get("institution"), d.get("collection_id"), d.get("newspaper")) != (
        "Fundação Biblioteca Nacional", "765147", "Última Hora, edição Nordeste (PE)"
    ):
        raise ValueError("incorrect institution")
    method = d["method"]
    if (method.get("full_body_reading"), method.get("ocr_performed"),
        method.get("downloaded_and_hashed_on_ifro")) != (False, False, True):
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
            scope = "CAPA_VERIFICADA_R67" if idx == 0 else "PANORAMA_MANCHETES_LAYOUT"
            if (page.get("status"), page.get("review_scope"), page.get("full_page_body_read"),
                page.get("event_time_literal"), page.get("conde_ba_article_verified"),
                page.get("independent_witness_verified")) != (
                "EXAMINADA", scope, False, None, False, False
            ):
                raise ValueError(f"unsupported source claim {num}/p{idx+1}")
            if page.get("topic_overview") != TOPICS[num][idx]:
                raise ValueError(f"topic changed without source re-review {num}/p{idx+1}")
    context = d["contextual_article"]
    if (context.get("edition"), context.get("pdf_page"), context.get("headline"),
        context.get("orbital_observation"), context.get("local_event_time")) != (
        "00475", 5,
        "URSS no Páreo para Conquista da Lua: 'Polet I' Rasga Caminho Aos 'Vostoks'",
        False, False,
    ):
        raise ValueError("Polet I contextual item reclassified")
    if "sem vínculo documental confirmado" not in context.get("classification", ""):
        raise ValueError("contextual evidence promoted")
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
    for key, value in required.items():
        if key not in result or result[key] != value:
            raise ValueError("epistemic promotion " + key)
    if len(d.get("limitations", [])) < 4:
        raise ValueError("scope limitations removed")
    return True


if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("PASS R71: 18 internal panoramas; no whole-edition negative, hour, witness or orbit")
