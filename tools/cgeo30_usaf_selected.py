"""Verify official SGB USAF tree selection, not photoindex acquisition."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo30_usaf_selected_node.json"
EXCERPT = ROOT / "research/geo/evidence/cgeo30_usaf_selected_excerpt.html"
PARENT = ROOT / "research/geo/cgeo29_usaf_63_32_photoindex_node.json"
LABEL = "1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def summary(raw: bytes) -> dict:
    text = raw.decode("utf-8", errors="replace")
    selected = re.findall(
        r'<div class="[^"]*\\brtSelected\\b[^"]*">\\s*<span[^>]*></span>'
        r'<img[^>]*><span class="rtIn">(.*?)</span>\\s*</div>',
        text, flags=re.DOTALL,
    )
    if not selected:
        # The official tree uses nested inline elements; allow whitespace but
        # never accept the label merely appearing elsewhere in the tree.
        selected = re.findall(
            r'<div class="rtMid rtSelected">.*?<span class="rtIn">(.*?)</span>\\s*</div>',
            text, flags=re.DOTALL,
        )
    values = re.findall(r'"_selectedValue":"([^"]+)"', text)
    page = re.findall(r'<span id="PagTotalLbl"[^>]*>(.*?)</span>', text)
    image = re.findall(r'<img id="DocumentoImg"[^>]*>', text)
    if len(selected) != 1 or len(values) != 1 or len(page) != 1 or len(image) != 1:
        raise ValueError("selected node, page, or document image missing/ambiguous")
    return {
        "label": unescape(selected[0].strip()),
        "value": values[0],
        "page_counter": unescape(page[0].strip()),
        "img_has_src": re.search(r"\\bsrc\\s*=", image[0], re.I) is not None,
    }


def verify(record: dict, parent: dict, excerpt: bytes) -> str:
    if (record["id"], record["parent"], parent["id"]) != ("CGEO-30", "CGEO-29", "CGEO-29"):
        raise ValueError("wrong family lineage")
    source = record["selection"]
    if (source["event_target"], source["event_argument"], source["node_ordinal_0_based"],
        source["selected_value"], source["literal_label"]) != ("T1", "s679", 679, "680", LABEL):
        raise ValueError("Telerik navigation target changed")
    if record["source"] != parent["official_reader"]["url"]:
        raise ValueError("institutional source changed")
    if (record["municipality"], parent["municipality"]) != (
        {"ibge_code": 2908606, "name": "Conde", "state": "BA"},
        {"ibge_code": 2908606, "name": "Conde", "state": "BA"},
    ):
        raise ValueError("wrong municipality")
    if source["selected_excerpt_sha256"] != sha(excerpt):
        raise ValueError("source-derived excerpt changed")
    if summary(excerpt) != {"label": LABEL, "value": "680", "page_counter": "/1", "img_has_src": False}:
        raise ValueError("source-derived selection did not confirm identity")
    if record["evidence_state"] != "USAF_PHOTOINDEX_NODE_SELECTION_CONFIRMED_IMAGE_NOT_ACQUIRED":
        raise ValueError("evidence level incorrectly promoted")
    if record["image_load_attempt"]["server_selected_value"] != "680":
        raise ValueError("image retry was on another node")
    if (record["image_load_attempt"]["document_image_src_in_server_html"] is not None or
        source["document_image_src_in_server_html"] is not None):
        raise ValueError("image URL was invented")
    if record["export_probe"]["actual_pdf_acquired"] or not record["export_probe"]["content_type"].startswith("text/html"):
        raise ValueError("HTML export was incorrectly classified as PDF")
    limits = record["scientific_limits"]
    for field in ["historical_center_geometry", "event_position_1963", "horizontal_uncertainty_m"]:
        if limits[field] is not None:
            raise ValueError("invented geometry or uncertainty")
    for field in ["date_of_capture_verified", "flight_footprint_verified", "original_photoindex_image_acquired",
                  "individual_frame_acquired", "can_constrain_orbital_reentry"]:
        if limits[field] is not False:
            raise ValueError("image/date/orbit claim unearned")
    if {x["to"] for x in record["graph_edges"]} != {"CGEO-18", "CGEO-28", "CGEO-29"}:
        raise ValueError("cumulative graph connection missing")
    return "USAF_SELECTION_EVIDENCE_REPLAY_PASS"


def verify_original(record: dict, raw: bytes, stage: str) -> str:
    if stage == "selection":
        source = record["selection"]
        expect_len, expect_hash = source["selected_response_bytes"], source["selected_response_sha256"]
    elif stage == "image":
        source = record["image_load_attempt"]
        expect_len, expect_hash = source["response_bytes"], source["response_sha256"]
    else:
        raise ValueError("unknown stage")
    if len(raw) != expect_len or sha(raw) != expect_hash:
        raise ValueError("original HTTP bytes do not match recorded custody")
    if summary(raw) != {"label": LABEL, "value": "680", "page_counter": "/1", "img_has_src": False}:
        raise ValueError("original source does not confirm node selection")
    return f"FULL_OFFICIAL_{stage.upper()}_REPLAY_PASS"


def main() -> None:
    cli = argparse.ArgumentParser()
    cli.add_argument("--selection-html", type=Path)
    cli.add_argument("--image-attempt-html", type=Path)
    args = cli.parse_args()
    r = load(MANIFEST)
    print(verify(r, load(PARENT), EXCERPT.read_bytes()))
    for stage, path in [("selection", args.selection_html), ("image", args.image_attempt_html)]:
        if path is not None:
            print(verify_original(r, path.read_bytes(), stage))


if __name__ == "__main__":
    main()
