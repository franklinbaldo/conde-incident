"""CGEO-13: validate SPU catalogue records; never infer a 1963 legal boundary."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo13_spu_mme_1985_catalogue.json"
EXPECTED = (
    ("BR-SPU-SPUNET-2020200296040", "Conde", 100000, "Reg6345_0006", "329573"),
    ("BR-SPU-REG6341-0002", "Jandaira", 50000, "Reg6341_0002", "329444"),
)


def validate_contract(data: dict) -> dict:
    if (data.get("schema") != "conde.gis.spu-mme-1985-catalogue/v1"
            or data.get("id") != "CGEO-13"
            or data.get("event_date") != "1963-11-08"
            or data.get("source_family") != "IBGE_MME_MAPS_SPU_ARCHIVE"):
        raise ValueError("catalogue identity changed")
    records = data.get("records")
    if not isinstance(records, list) or len(records) != 2:
        raise ValueError("exactly two archived catalogue occurrences are required")
    for record, (source_id, name, scale, register, item) in zip(records, EXPECTED):
        if (record.get("id") != source_id
                or record.get("municipality") != name
                or record.get("state") != "BA"
                or record.get("scale_denominator") != scale
                or record.get("catalogued_year") != 1985
                or record.get("revision_month") != "1985-09"):
            raise ValueError("archival catalogue occurrence changed")
        for key in ("original_date", "pdf_sha256", "geodetic_datum",
                    "verified_crs", "geometry", "positional_accuracy_m"):
            if record.get(key, "MISSING") is not None:
                raise ValueError("unverified data promoted: " + key)
        if (record.get("access_status") != "CATALOGUE_READ_PDF_NOT_ACQUIRED"
                or record.get("facsimile_inspected") is not False
                or record.get("document_type") != "IBGE MME map / SPU archival copy"
                or record.get("custodian") != "SPU-RJ"):
            raise ValueError("source access or independence promoted")
        if (not record.get("catalog_url", "").startswith("https://memoria-spu.gestao.gov.br/")
                or not record.get("pdf_url", "").startswith("https://memoria-spu.gestao.gov.br/")
                or register not in record.get("scan_marker", "")
                or register not in record.get("pdf_url", "")
                or item not in record.get("pdf_url", "")):
            raise ValueError("SPU archival locator modified")
        if "UTM" not in record.get("catalogued_utm_text", ""):
            raise ValueError("catalogued projection clue removed")
        if date.fromisoformat(record["revision_month"] + "-01") <= date.fromisoformat(data["event_date"]):
            raise ValueError("1985 revision should postdate 1963 event")
    if "Conde" not in records[1].get("catalogue_mentions", []) or "Jandaira" not in records[0].get("catalogue_mentions", []):
        raise ValueError("archival cross references altered")
    if "MMC 70" not in records[0].get("extra_base", ""):
        raise ValueError("1970 complement dependency omitted")
    graph = data.get("dependency_graph", {})
    if (graph.get("prior_ids") != ["CGEO-09", "CGEO-10", "CGEO-11", "CGEO-12"]
            or graph.get("same_ibge_family_not_independent_surveys") is not True
            or graph.get("postdates_event") is not True
            or graph.get("can_constrain_reentry") is not False):
        raise ValueError("false independence or historical constraint")
    for key in ("legal_boundary_1963", "datum", "georeferencing_error_m", "point_of_reentry"):
        if graph.get(key, "MISSING") is not None:
            raise ValueError("unverified historical geospatial state: " + key)
    expected_links = (
        (EXPECTED[0][0], "MME_1985_MAP_FAMILY", "CATALOGUED_ARCHIVAL_COPY"),
        (EXPECTED[1][0], "MME_1985_MAP_FAMILY", "CATALOGUED_ARCHIVAL_COPY"),
        ("MME_1985_MAP_FAMILY", "1963_LEGAL_BOUNDARY_LATENT",
         "POST_EVENT_WITH_FACSIMILE_AND_LEGAL_BRIDGE_MISSING"),
    )
    if tuple((link.get("from"), link.get("to"), link.get("type"))
             for link in graph.get("links", [])) != expected_links:
        raise ValueError("SPU archival dependency graph altered")
    return data


def evaluate(day: str, data: dict) -> dict:
    validate_contract(data)
    requested = date.fromisoformat(day)
    return {
        "schema": "conde.gis.spu-mme-1985-evaluation/v1",
        "requested_date": requested.isoformat(),
        "catalogue_occurrences": [r["id"] for r in data["records"]],
        "map_revisions_postdate_requested_date": all(
            date.fromisoformat(r["revision_month"] + "-01") > requested
            for r in data["records"]
        ),
        "source_status": "CATALOGUES_READ_FACSIMILES_NOT_ACQUIRED",
        "geodetic_datum": None,
        "legal_boundary_for_requested_date": None,
        "event_point_membership": None,
        "can_constrain_orbital_reentry": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--date", default="1963-11-08")
    parser.add_argument("--check", action="store_true",
                        help="validate the catalogue and provenance constraints")
    args = parser.parse_args()
    data = validate_contract(json.loads(args.contract.read_text(encoding="utf-8")))
    print(json.dumps(evaluate(args.date, data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
