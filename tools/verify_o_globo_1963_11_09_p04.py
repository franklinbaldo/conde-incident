#!/usr/bin/env python3
"""Verify custody and epistemic boundaries for O Globo 1963-11-09 page 4."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/archive/conde_o_globo_1963_11_09_p04.json"
EXPECTED_SHA = "7bbd6507e2cf9624315323081cceb3e705b649b53269aa97bcf299bea428b6d8"
EXPECTED_BYTES = 945313


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(f"C241-OGLOBO-19631109-P04: {msg}")


def validate(data: dict, pdf_bytes: bytes | None = None) -> bool:
    require(data["schema"] == "conde.contemporary_newspaper_custody/v1", "schema")
    require(data["id"] == "C241-OGLOBO-19631109-P04", "id")
    src = data["source"]
    require(src["newspaper"] == "O Globo", "newspaper")
    require(src["publication_date"] == "1963-11-09", "publication_date")
    require(src["page"] == 4, "page")
    require(src["bytes"] == EXPECTED_BYTES, "bytes")
    require(src["sha256"] == EXPECTED_SHA, "sha256")
    require(src["visually_inspected"] is True, "visually_inspected")

    art = data["article"]
    require("NÃO HÁ NOTÍCIAS OFICIAIS" in art["headline_verbatim"], "headline")
    require("Eduardo Machado" in art["text_verbatim"], "Observatorio Nacional quote")
    require("Comando da II Zona Aérea" in art["text_verbatim"], "II Zona Aerea lead")
    require("até ontem à tarde" in art["text_verbatim"], "afternoon 8 Nov temporal cue")
    require(art["reported_event_clock"] is None, "must not invent event clock")
    require(art["eyewitness_name"] is None, "must not invent eyewitness")

    bridge = data["cumulative_graph_bridge"]
    require(bridge["status"] == "CONNECTED_PENDING_CALIBRATION", "bridge status")
    require(bridge["physical_constraints_activated"] == 0, "zero physical constraints")

    lim = data["limits"]
    for key in (
        "proves_physical_sphere_or_impact",
        "proves_satellite_reentry",
        "proves_ii_zona_aerea_dispatch_occurred",
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
    print("C241-OGLOBO-19631109-P04: custody and epistemic boundaries PASS")


if __name__ == "__main__":
    main()
