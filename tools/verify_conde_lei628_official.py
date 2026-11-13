#!/usr/bin/env python3
"""Verify an official modern transcription, NOT a 1953 printed facsimile."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_lei628_official_1953_20261113.json"
DOC_MAGIC = bytes.fromhex("d0cf11e0a1b11ae1")
SOURCE = "https://www.legislabahia.ba.gov.br/documentos/lei-no-628-de-30-de-dezembro-de-1953"
ATTACHMENT = "https://www.legislabahia.ba.gov.br/sites/default/files/anexos/66400/Lei628.Anexos.doc"
SHA = "dc83e4b4806b9cd758c500b322999ce72814dca68e1cb16fe5900d468e2ea581"


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def plain_html(raw: bytes) -> str:
    collector = TextCollector()
    collector.feed(raw.decode("utf-8"))
    return " ".join(" ".join(collector.parts).split())


def verify_manifest(data: dict) -> list[str]:
    errors = []
    for key, value in (("schema", "conde.legal-archive-transcription/v1"),
                       ("document_id", "CGEO-LEGISBA-L628-1953-01"),
                       ("enacted", "1953-12-30"),
                       ("stated_effective_from", "1954-01-01"),
                       ("stated_effective_until", "1958-12-31")):
        if data.get(key) != value:
            errors.append(key)
    portal = data.get("source_portal", {})
    if portal.get("url") != SOURCE or portal.get("publication_format") != "modern_official_transcription_not_original_diario_fascimile":
        errors.append("portal identity")
    for key, value in (("sample_html_bytes", 135360),
                       ("sample_html_sha256", "83058c6afacdc5d8436c4bf0c7d932ecdbb51b37a8ad20cbe9dfc07d549702a1")):
        if portal.get(key) != value:
            errors.append("sample portal " + key)
    doc = data.get("official_annex_attachment", {})
    for key, value in (("url", ATTACHMENT), ("bytes", 830976),
                       ("sha256", SHA), ("format", "OLE2_MS_WORD"),
                       ("internal_creation_date", "2013-01-07"),
                       ("table_quadro_i_municipality_number", 38),
                       ("table_quadro_i_districts_for_conde", ["Conde"]),
                       ("attachment_is_1953_printed_facsimile", False),
                       ("internal_creation_date_is_1953_publication_proof", False)):
        if doc.get(key) != value:
            errors.append("attachment " + key)
    geo = data.get("annex_vi_portal_transcription", {})
    if (geo.get("heading") != "ANEXO VI"
            or geo.get("neighbours_explicitly_described_in_section") != ["Rio Real", "Jandaira"]
            or geo.get("full_boundary_perimeter_described") is not False
            or geo.get("contains_potential_textual_corruption") is not True):
        errors.append("partial annex VI/uncertainty")
    graph = data.get("constraint_graph", {})
    if graph.get("status") != "CONNECTED_PENDING_DOCUMENTARY_VALIDATION":
        errors.append("graph status")
    for key in ("orbital_constraint_activated", "1963_legal_polygon_proven", "no_intervening_acts_proven"):
        if graph.get(key) is not False:
            errors.append("forbidden historical inference " + key)
    return errors


def verify_doc(raw: bytes, data: dict) -> list[str]:
    doc = data["official_annex_attachment"]
    errors = []
    if len(raw) != doc["bytes"]:
        errors.append("DOC size")
    if hashlib.sha256(raw).hexdigest() != doc["sha256"]:
        errors.append("DOC SHA-256")
    if not raw.startswith(DOC_MAGIC):
        errors.append("DOC OLE2 magic")
    return errors


def verify_html(raw: bytes, data: dict) -> list[str]:
    """Check textual coverage; changed HTML bytes are reported separately."""
    errors = []
    try:
        text = plain_html(raw)
    except UnicodeError:
        return ["portal HTML UTF-8"]
    if "LEI Nº 628 DE 30 DE DEZEMBRO DE 1953" not in text:
        errors.append("law identity")
    if not re.search(r"\bANEXO VI\b", text):
        errors.append("annex VI header")
    title = "MUNICÍPIO DE CONDE LIMITES MUNICIPAIS:"
    end = "MUNICÍPIO DE CONDEÚBA"
    if title not in text or end not in text.split(title, 1)[-1]:
        errors.append("Conde isolated section")
    else:
        section = text.split(title, 1)[1].split(end, 1)[0]
        for term in ("COM O MUNICÍPIO DE RIO REAL:", "COM O MUNICÍPIO DE JANDAÍRA:",
                     *data["annex_vi_portal_transcription"]["landmark_strings"],
                     data["annex_vi_portal_transcription"]["textual_corruption_example"]):
            if term not in section:
                errors.append("missing portal section landmark " + term)
    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=MANIFEST)
    p.add_argument("--annex-doc", type=Path)
    p.add_argument("--portal-html", type=Path)
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = verify_manifest(manifest)
    if args.annex_doc:
        errors.extend(verify_doc(args.annex_doc.read_bytes(), manifest))
    if args.portal_html:
        errors.extend(verify_html(args.portal_html.read_bytes(), manifest))
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: 1953 law / 2013 annex transcription, Conde named edges (1954-1958);"
          " no complete 1963 boundary. Replays: DOC="
          + ("VERIFIED" if args.annex_doc else "NOT_RUN") + " HTML="
          + ("CONTENT_VALID" if args.portal_html else "NOT_RUN"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
