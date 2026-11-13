"""Check SGB's real ASP.NET AJAX image-panel response without claiming image acquisition."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo31_usaf_ajax_delta.json"
EXCERPT = ROOT / "research/geo/evidence/cgeo31_ajax_document_panel.html"
PARENT = ROOT / "research/geo/cgeo30_usaf_selected_node.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_document_panel(response: bytes) -> bytes:
    """Extract a length-framed actual AJAX update, not similar text elsewhere."""
    if not response.startswith(b"1|#||4|"):
        raise ValueError("not a recognized ASP.NET AJAX response")
    matches = list(re.finditer(rb"\|([0-9]+)\|updatePanel\|DocumentoUpdatePanel\|", response))
    if len(matches) != 1:
        raise ValueError("missing/ambiguous official update panel")
    m = matches[0]
    length = int(m.group(1))
    start = m.end()
    end = start + length
    if length < 1 or end >= len(response) or response[end:end + 1] != b"|":
        raise ValueError("truncated or malformed length-framed panel")
    return response[start:end]


def verify(record: dict, parent: dict, excerpt: bytes) -> str:
    if (record["id"], record["parent"], parent["id"]) != ("CGEO-31", "CGEO-30", "CGEO-30"):
        raise ValueError("invalid lineage")
    if record["source"] != parent["source"] or record["municipality"] != parent["municipality"]:
        raise ValueError("incorrect source or municipality")
    req = record["request"]
    if (req["same_session_after_t1_selection"], req["selected_tree_event"],
        req["image_event_target"], req["script_manager_field"],
        req["async_post"], req["x_microsoftajax_header"], req["hPagFis"]) != (
        True, "s679", "CarregaImagemHiddenButton", "DocumentoUpdatePanel|CarregaImagemHiddenButton",
        True, "Delta=true", "1",
    ):
        raise ValueError("not the executed AJAX image request")
    r = record["response"]
    if (r["http_status"], r["content_type"], r["body_bytes"], r["body_sha256"]) != (
        200, "text/plain; charset=utf-8", 9024,
        "3e4d49a20fbcffef0ca57aa05bdbe23620dcfa0bb5a238a16899e9bc83938644",
    ):
        raise ValueError("response provenance changed")
    if (r["update_panel_id"], r["update_panel_declared_length"], r["excerpt_bytes"],
        r["excerpt_sha256"]) != (
        "DocumentoUpdatePanel", 2752, len(excerpt), digest(excerpt),
    ):
        raise ValueError("panel excerpt failed custody")
    if r["excerpt_sha256"] != "23c72cf7fb3cbdb7e4c715434e0ecfd3d1d32c45deb2e82b9555443bf247f8fb":
        raise ValueError("non-original excerpt")
    imgs = re.findall(rb'<img\s+id=["\']DocumentoImg["\'][^>]*>', excerpt)
    if len(imgs) != 1 or re.search(rb"\bsrc\s*=", imgs[0], re.I):
        raise ValueError("image tag missing or contains an acquired URL")
    if (r["doc_image_element_count"], r["doc_image_src"], r["image_bytes_acquired"]) != (1, None, False):
        raise ValueError("image acquisition falsely claimed")
    if record["evidence_state"] != "ASYNC_IMAGE_PANEL_RETURNED_WITHOUT_IMAGE_URL":
        raise ValueError("evidence status promoted")
    lim = record["scientific_limits"]
    if any(lim[k] is not False for k in ["original_photoindex_image_acquired", "flight_date_verified",
                                        "footprint_verified", "can_constrain_orbital_reentry"]):
        raise ValueError("unearned archival or orbital claim")
    if any(lim[k] is not None for k in ["historical_center_geometry", "reentry_position", "horizontal_uncertainty_m"]):
        raise ValueError("invented coordinate or spatial uncertainty")
    if {x["to"] for x in record["graph_edges"]} != {"CGEO-18", "CGEO-29", "CGEO-30"}:
        raise ValueError("missing graph lineage")
    return "CGEO31_ASYNC_PANEL_EXCERPT_PASS"


def verify_full(raw: bytes, record: dict, excerpt: bytes) -> str:
    r = record["response"]
    if len(raw) != r["body_bytes"] or digest(raw) != r["body_sha256"]:
        raise ValueError("raw response not acquired original")
    if extract_document_panel(raw) != excerpt:
        raise ValueError("panel does not match original AJAX payload")
    return "CGEO31_FULL_AJAX_REPLAY_PASS"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--original-ajax", type=Path)
    args = p.parse_args()
    record, excerpt = load(MANIFEST), EXCERPT.read_bytes()
    print(verify(record, load(PARENT), excerpt))
    if args.original_ajax:
        print(verify_full(args.original_ajax.read_bytes(), record, excerpt))


if __name__ == "__main__":
    main()
