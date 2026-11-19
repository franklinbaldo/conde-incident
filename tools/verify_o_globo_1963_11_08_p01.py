#!/usr/bin/env python3
"""Verify custody and epistemic boundaries for O Globo 1963-11-08 page 1."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_o_globo_1963_11_08_p01.json"
EXPECTED_SHA = "16d8712c7021f1c88abf081cf264cd7f810c9b7962bb74dd8d3d0bf0ea55f06d"
EXPECTED_BYTES = 885117


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(f"C241-OGLOBO-19631108-P01: {msg}")


def validate(data: dict, pdf_bytes: bytes | None = None) -> bool:
    require(data["schema"] == "conde.contemporary_newspaper_custody/v1", "schema")
    require(data["id"] == "C241-OGLOBO-19631108-P01", "id")
    src = data["source"]
    require(src["newspaper"] == "O Globo", "newspaper")
    require(src["publication_date"] == "1963-11-08", "publication_date")
    require(src["issue_number"] == "11.506", "issue_number")
    require(src["page"] == 1, "page")
    require(src["bytes"] == EXPECTED_BYTES, "bytes")
    require(src["sha256"] == EXPECTED_SHA, "sha256")
    require(src["visually_inspected"] is True, "visually_inspected")

    art = data["article"]
    require("Grande Globo Metálico" in art["headline_verbatim"], "headline")
    require("município de Conde" in art["text_verbatim"], "body Conde")
    require("quatro metros de profundidade" in art["text_verbatim"], "body 4m")
    require(art["reported_event_clock"] is None, "must not invent event clock")
    require(art["eyewitness_name"] is None, "must not invent eyewitness")

    bridge = data["cumulative_graph_bridge"]
    require(bridge["status"] == "CONNECTED_PENDING_CALIBRATION", "bridge status")
    require(bridge["press_closing_time_utc"] is None, "must not invent closing time")
    require(bridge["physical_constraints_activated"] == 0, "zero physical constraints")

    lim = data["limits"]
    for key in (
        "proves_physical_sphere_or_impact",
        "proves_satellite_reentry",
        "proves_independence_from_salvador_wire",
        "outreach_sent",
    ):
        require(lim[key] is False, f"limits.{key}")

    if pdf_bytes is not None:
        require(len(pdf_bytes) == EXPECTED_BYTES, "PDF byte length mismatch")
        require(hashlib.sha256(pdf_bytes).hexdigest() == EXPECTED_SHA, "PDF sha256 mismatch")
        require(pdf_bytes.startswith(b"%PDF-"), "PDF magic header")

    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Optional local PDF to hash-verify")
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pdf_bytes = args.pdf.read_bytes() if args.pdf else None
    validate(data, pdf_bytes)
    print("C241-OGLOBO-19631108-P01: custody and epistemic boundaries PASS")


if __name__ == "__main__":
    main()
