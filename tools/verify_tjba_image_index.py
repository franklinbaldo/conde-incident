"""Check archival viewer's separate-image index without confusing it with PDF pages."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_tjba_image_index_20261113.json"
ARCHIVE = ROOT / "research/archive"
DOC_FILES = {
    "CGEO-TJBA-DOE-1953-12-01": "conde_tjba_doe_1953_12_20261113.json",
    "CGEO-TJBA-DOE-1954-01-01": "conde_tjba_doe_1954_01_20261113.json",
}
NODE = re.compile(r"^[a-f0-9]{32}$")


def validate(record: dict, sources: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    if record.get("schema") != "conde.archidoc-image-viewer-negative/v1":
        errors.append("schema")
    docs = record.get("documents")
    if not isinstance(docs, list) or len(docs) != len(DOC_FILES):
        return errors + ["document-count"]
    ids = {d.get("document_id") for d in docs if isinstance(d, dict)}
    if ids != set(DOC_FILES):
        errors.append("document-ids")
    for doc in docs:
        if not isinstance(doc, dict):
            errors.append("document-object")
            continue
        identifier = doc.get("document_id")
        source = sources.get(identifier)
        if source is None:
            continue
        node = doc.get("catalog_node_id")
        if not isinstance(node, str) or not NODE.fullmatch(node):
            errors.append("node-format")
        if node != source.get("catalog_node_id"):
            errors.append(f"{identifier}:node")
        if doc.get("pdf_resource_id") != source.get("download_resource_id"):
            errors.append(f"{identifier}:resource")
        if doc.get("pdf_pages_preserved_separately") != source.get("pdf_page_objects_count"):
            errors.append(f"{identifier}:pdf-pages")
        if doc.get("viewer_total_value") != 0 or doc.get("images_json_response") != []:
            errors.append(f"{identifier}:image-index")
        if doc.get("status") != "NO_SEPARATE_PAGE_IMAGES_IN_THIS_VIEWER_NODE":
            errors.append(f"{identifier}:status")
    for flag in (
        "law_628_1953_page_found",
        "law_628_1953_publication_date_proven",
        "legal_boundary_1963_demonstrated",
        "orbital_constraint_activated",
    ):
        if record.get(flag) is not False:
            errors.append(f"{flag}:not-evidenced")
    if "does not mean" not in str(record.get("epistemic_scope", "")):
        errors.append("missing-page-absence-limitation")
    return errors


def live_check(doc: dict, opener=urllib.request.urlopen) -> list[str]:
    node = doc["catalog_node_id"]
    base = "https://acervo.tjba.jus.br/ConsultaWeb/"
    errors = []
    html_url = f"{base}showImagenes?id={node}&ini=1"
    images_url = f"{base}assets/json/imagenes.json?id={node}&idNodoImagen={node}&ini=1"
    for label, url in (("viewer", html_url), ("images", images_url)):
        request = urllib.request.Request(url, headers={"User-Agent": "CondeArchivalAudit/1.0"})
        with opener(request, timeout=20) as response:
            data = response.read(524288)
            if label == "viewer":
                matched = re.search(rb'id="total"\s+value="(\d+)"', data)
                if not matched or int(matched.group(1)) != doc["viewer_total_value"]:
                    errors.append(f"{node}:viewer-count-changed")
            else:
                if json.loads(data) != doc["images_json_response"]:
                    errors.append(f"{node}:images-changed")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--live", action="store_true", help="Replay exact public HTTP endpoints")
    args = parser.parse_args()
    record = json.loads(args.manifest.read_text(encoding="utf-8"))
    sources = {
        key: json.loads((ARCHIVE / filename).read_text(encoding="utf-8"))
        for key, filename in DOC_FILES.items()
    }
    errors = validate(record, sources)
    if args.live and not errors:
        for doc in record["documents"]:
            try:
                errors.extend(live_check(doc))
            except (OSError, ValueError) as exc:
                errors.append(f"{doc['document_id']}:unavailable:{type(exc).__name__}")
    for error in errors:
        print("FAIL", error)
    if errors:
        return 1
    print("PASS", "viewer_replayed" if args.live else "metadata_only",
          "image-index-empty != PDF-page-absent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
