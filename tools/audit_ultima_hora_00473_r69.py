"""Fail-closed validation of the scoped 00473 (10 Nov 1963) panorama."""
from __future__ import annotations
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/archive/ultima_hora_ne_00473_page_review_R69.json"
EXPECTED_SHA = "f37e4afa500fe841546a751e562cc799c33c699decb8967b2ae00b45e721e349"


# Visual observations are part of source custody, not free-form prose.
# A change requires a fresh review of the identified original page.
EXPECTED_TOPICS = (
    "capa anteriormente verificada na R67",
    "política de Sergipe e crônica do Recife",
    "governo estadual, trânsito e publicidade",
    "Congresso e finanças públicas",
    "explosão de mina no Japão e notícia espacial geral NASA/Explorer 1",
    "investigação policial no Recife",
    "debate político e publicidade institucional",
    "direitos civis dos negros nos EUA",
    "cultura popular e Bertolt Brecht",
    "classificados e anúncios",
    "rádio, TV e folclore",
    "futebol e esportes",
    "capa de suplemento feminino e moda de verão",
    "culinária e passatempos",
    "chapéus e colunas femininas",
    "cinema e programação cultural",
    "cuidados pessoais e decoração",
    "moda, praia e reportagem social",
)
EXPECTED_CONTEXTUAL_ARTICLE = {
    "pdf_page": 5,
    "headline": "NASA: 'Explorer 1' abrirá caminho aos cosmonautas",
    "classification": "notícia espacial geral, sem relato identificado de Conde/BA ou medição individual do NORAD 528",
    "orbital_observation": False,
}

def validate(d: dict) -> bool:
    if (d.get("schema"), d.get("id"), d.get("refs_issue")) != ("conde.newspaper_page_review/v1", "C241-LONTRA-R69", 871):
        raise ValueError("review identity")
    s = d["source"]
    if (s["collection_id"], s["edition"], s["date_printed"]) != ("765147", "00473", "1963-11-10"):
        raise ValueError("source identity")
    if (s["pdf_sha256"], s["pdf_bytes"], s["pdf_pages"]) != (EXPECTED_SHA, 8298891, 18):
        raise ValueError("binary custody")
    if s["pdf_url"] != "https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00473.pdf":
        raise ValueError("source URL")
    if s["redownload"] is not False or s["integrity_rechecked_on_ifro"] is not True:
        raise ValueError("download/replay")
    if d["method"]["full_body_reading"] is not False or d["method"]["negative_is_page_scoped"] is not False:
        raise ValueError("unsupported full-text conclusion")
    p = d["pages"]
    if len(p) != 18 or [x["pdf_page"] for x in p] != list(range(1, 19)):
        raise ValueError("page sequence")
    for i, x in enumerate(p):
        scope = "CAPA_VERIFICADA_R67" if i == 0 else "PANORAMA_MANCHETES_LAYOUT"
        if (x["status"], x["review_scope"], x["event_time_literal"], x["conde_ba_article_verified"],
            x["independent_witness_verified"], x["full_page_body_read"]) != ("EXAMINADA", scope, None, False, False, False):
            raise ValueError("false page conclusion " + str(i+1))
        if not x["topic_overview"]:
            raise ValueError("page has no scope description")
    if tuple(x["topic_overview"] for x in p) != EXPECTED_TOPICS:
        raise ValueError("changed visual page observation requires source re-review")
    if d["possible_false_positives_not_fully_audited"] is not True:
        raise ValueError("unearned exhaustive audit")
    if d["contextual_article"] != EXPECTED_CONTEXTUAL_ARTICLE:
        raise ValueError("changed contextual article requires source re-review")
    required = {"pages_visually_reviewed":18,"new_internal_pages_reviewed":17,
      "pages_remaining_for_panorama_of_all_four_editions":18,
      "confirmed_independent_event_time":None,"source_chain":"UNDETERMINED",
      "whole_edition_no_article_claim":False,"whole_edition_no_time_claim":False,
      "physical_orbital_constraint_added":False}
    for key, val in required.items():
        if d["result"].get(key, object()) != val:
            raise ValueError("false promotion " + key)
    return True

if __name__ == "__main__":
    assert validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("PASS R69: panorama of 17 pages; no whole-edition negative or orbital claim")
