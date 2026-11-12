#!/usr/bin/env python3
"""Validate legal boundary custody. Never turn 2017 DMS into a 1963 polygon."""
from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/conde_legal_1953_2017.json"
ISO_DMS = re.compile(r"""^-(\d{1,3})° (\d{2})' (\d{2}),(\d{2})"$""")
PDF_SHA = {
    "SEI-BA-EMB-2013-v4n1-p149":
        "e4364fc77070053481184f2c606b9fb18dcd87d5c2da603ec1f7617720fe2c57",
    "BA-ALEBA-LEI-13720-2017-DO-22166":
        "76134441592ebc234dbd3856560ed6375f956f8e126c8ecced5244b9a38d89d9",
}
EDGES = [
    ("I", "Jandaíra", "v_salobrinho_branco", "v_itapicuru_atlantic"),
    ("II", "Oceano Atlântico", "v_itapicuru_atlantic", "v_inhambupe_atlantic"),
    ("III", "Esplanada", "v_inhambupe_atlantic", "v_mangues_itapicuru"),
    ("IV", "Rio Real", "v_mangues_itapicuru", "v_salobrinho_branco"),
]
EXPECTED_CORNER_DMS = {
    "v_salobrinho_branco": ("-11° 39' 45,89\"", "-37° 44' 50,27\""),
    "v_itapicuru_atlantic": ("-11° 44' 27,80\"", "-37° 30' 40,44\""),
    "v_inhambupe_atlantic": ("-12° 05' 54,08\"", "-37° 41' 09,25\""),
    "v_mangues_itapicuru": ("-11° 44' 16,86\"", "-37° 48' 44,48\""),
}


def signed_dms_to_degrees(value: str, limit: int) -> Decimal:
    """Angular conversion for inspection only: datum remains UNKNOWN."""
    m = ISO_DMS.fullmatch(value)
    if m is None:
        raise ValueError("DMS needs signed south/west degrees, minutes and hundredths")
    deg, minute, second, hundredth = map(int, m.groups())
    if deg > limit or minute >= 60 or second >= 60 or (deg == limit and any((minute, second, hundredth))):
        raise ValueError("invalid geographic angular range")
    return -(Decimal(deg) + Decimal(minute) / 60
             + (Decimal(second) + Decimal(hundredth) / 100) / 3600)


def read_contract(path: Path = CONTRACT) -> dict:
    j = json.loads(path.read_text(encoding="utf-8"))
    if j.get("schema") != "conde.gis.legal-boundary-custody/v1":
        raise ValueError("wrong legal contract schema")
    if j.get("jurisdiction") != {"municipality": "Conde", "state": "BA", "ibge_code": "2908606"}:
        raise ValueError("wrong municipality identity")
    sources = j.get("sources", [])
    if len(sources) != 2 or {s.get("id") for s in sources} != set(PDF_SHA):
        raise ValueError("expected two documentary sources")
    for s in sources:
        if s.get("pdf_sha256") != PDF_SHA[s["id"]] or s.get("pdf_bytes", 0) <= 0:
            raise ValueError("source checksum/size mismatch")
        if not s.get("url", "").startswith("https://") or not s.get("occurrence"):
            raise ValueError("source URL or occurrence missing")
    history = j["historical_1953_reference"]
    if (history.get("original_1953_annex_checked") is not False or
        history.get("intervening_changes_through_1963_checked") is not False or
        history.get("valid_geometry_on_1963_11_08") is not None):
        raise ValueError("1953 original and 1963 spatial validity remain unproven")
    legal = j["legal_2017"]
    if (legal["effective_on"] != "2017-04-28" or legal["published_on"] != "2017-04-28" or
        legal["source_id"] != "BA-ALEBA-LEI-13720-2017-DO-22166"):
        raise ValueError("2017 legal date/source mismatch")
    for field in ("coordinate_reference_system", "coordinate_datum", "coordinate_epoch",
                  "published_positional_accuracy_m", "control_point_georeferencing"):
        if legal.get(field, "MISSING") is not None:
            raise ValueError("unverified 2017 CRS/datum/accuracy must be null: " + field)
    if (legal.get("retroprojection_to_1963_authorized") is not False or
        legal.get("mapping_to_EPSG_4674_authorized") is not False or
        legal.get("complete_described_boundary_reconstructed") is not False or
        legal.get("textual_boundary_only") is not True):
        raise ValueError("a legal memorial is not a verified 1963 GIS polygon")
    if set(v["id"] for v in legal["vertices"]) != set(EXPECTED_CORNER_DMS):
        raise ValueError("legal end-vertex identity changed")
    if len(legal["vertices"]) != 4:
        raise ValueError("duplicate legal corner")
    for v in legal["vertices"]:
        expected = EXPECTED_CORNER_DMS[v["id"]]
        if (v.get("latitude_dms"), v.get("longitude_dms")) != expected:
            raise ValueError("unreviewed original 2017 DMS alteration")
        lat = signed_dms_to_degrees(v["latitude_dms"], 90)
        lon = signed_dms_to_degrees(v["longitude_dms"], 180)
        if not (Decimal(-13) < lat < Decimal(-11) and Decimal(-39) < lon < Decimal(-37)):
            raise ValueError("2017 memorial controls outside Conde region")
    legs = legal.get("legs", [])
    if [(e["paragraph"], e["adjacent_unit"], e["from"], e["to"])
            for e in legs] != EDGES:
        raise ValueError("four 2017 law sections and their order must be preserved")
    for leg in legs:
        if leg.get("intermediate_controls_omitted") is not True:
            raise ValueError("cannot silently treat endpoints as complete geometry")
    if any(legs[n]["to"] != legs[(n + 1) % 4]["from"] for n in range(4)):
        raise ValueError("textual boundary nodes do not join")
    graph = j["constraint_graph"]
    if (graph.get("link_status") != "CONNECTED_PENDING_HISTORICAL_CUSTODY" or
        graph.get("activated_spatial_constraint") is not False or
        graph.get("can_constrain_reentry_1963") is not False or
        graph.get("latent_variables", [])[0].get("value", "MISSING") is not None):
        raise ValueError("geography cannot constrain 1963 without original limits")
    return j


def date_eligibility(value: str, contract: dict) -> dict:
    """Return documentary eligibility, never geometric containment or landing."""
    d = date.fromisoformat(value)
    law = date.fromisoformat(contract["legal_2017"]["effective_on"])
    if d < law:
        status = "UNRESOLVED_NO_1963_BOUNDARY" if d.year == 1963 else "LATER_STATUTE_NOT_APPLICABLE"
    else:
        status = "POST_2017_MEMORIAL_NO_GEODETIC_REGISTRATION_OR_CURRENTNESS_CHECK"
    return {
        "requested_date": d.isoformat(),
        "legal_2017_effective_on": law.isoformat(),
        "temporal_status": status,
        "boundary_polygon_for_date": None,
        "coordinates_datum": None,
        "can_test_point_in_1963_municipality": False,
        "can_constrain_reentry_1963": False,
        "pending": contract["constraint_graph"]["missing"],
    }


def verify_pdf_file(contract: dict, source_id: str, path: Path) -> dict:
    source = next((s for s in contract["sources"] if s["id"] == source_id), None)
    if source is None:
        raise ValueError("unknown source ID")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != source["pdf_sha256"] or path.stat().st_size != source["pdf_bytes"]:
        raise ValueError("original PDF differs from pinned source checksum/size")
    return {"source_id": source_id, "sha256": digest, "bytes": source["pdf_bytes"],
            "verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default="1963-11-08", help="YYYY-MM-DD; not an observation time")
    parser.add_argument("--verify-pdf", type=Path)
    parser.add_argument("--source-id", choices=sorted(PDF_SHA))
    parser.add_argument("--input", type=Path, default=CONTRACT)
    args = parser.parse_args()
    contract = read_contract(args.input)
    out = {"schema": "conde.gis.legal-boundary-evaluation/v1",
           **date_eligibility(args.date, contract)}
    if args.verify_pdf:
        if args.source_id is None:
            parser.error("--verify-pdf requires --source-id")
        out["pdf_custody"] = verify_pdf_file(contract, args.source_id, args.verify_pdf)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
