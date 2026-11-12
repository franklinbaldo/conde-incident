"""CGEO-11: IBGE 1991-base cartographic lineage; fail closed for 1963."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/ibge_1872_1991_methodology_2026-11-12.json"
CGEO10 = ROOT / "research/geo/conde_ibge_1960_world_polyconic.json"
SCHEMA = "conde.gis.ibge-retrospective-lineage/v1"
PDF_SHA = "5886a4a481f51299818082beb5fb43d7deda60f4d2ad09a31eb598579d6e0fab"
PDF_BYTES = 15484
PDF_URL = (
    "https://geoftp.ibge.gov.br/metodos_e_outros_documentos_de_referencia/"
    "outros_documentos_tecnicos/municipios_1872_1991_documentacao/"
    "Evolucao_da_divisao_territorial_do_Brasil_1872%20a%202010_apresentacao_do_conteudo_digital.pdf"
)
EDGE_KINDS = {
    "DOCUMENTS_PRODUCT_WIDE_CONSTRUCTION_METHOD",
    "REPORTED_CARTOGRAPHIC_DERIVATION_NOT_AN_INDEPENDENT_1960_SURVEY",
    "IDENTIFIES_SOURCE_POLYGON_AND_NOMINAL_YEAR",
    "NOT_A_VALIDATED_TEMPORAL_OR_PRECISION_BRIDGE",
}


def validate(path: Path = CONTRACT, cgeo10_path: Path = CGEO10) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    source = data.get("documentary_evidence", {})
    method = data.get("official_methodology", {})
    graph = data.get("dependency_graph", {})
    export = data.get("castor_export", {})
    if data.get("schema") != SCHEMA or data.get("id") != "CGEO-11":
        raise ValueError("CGEO-11 identity or schema changed")
    if not (source.get("classification") == "OFFICIAL_PRIMARY_METHOD_STATEMENT"
            and source.get("publisher") == "IBGE"
            and source.get("pdf_url") == PDF_URL
            and source.get("pdf_sha256") == PDF_SHA
            and source.get("pdf_size_bytes") == PDF_BYTES
            and source.get("page_1_based") == 1
            and source.get("page_inspection") == "VISUALLY_INSPECTED_PAGE_1_AND_BINARY_VERIFIED"):
        raise ValueError("Official IBGE method source custody altered")
    if not (method.get("base_mesh_nominal_year") == 1991
            and method.get("nominal_year_of_derived_conde_record") == 1960
            and method.get("source_geometry_record_id") == "CGEO-10"
            and method.get("cartographic_precision_claimed") is False
            and method.get("numeric_horizontal_accuracy_m") is None
            and method.get("independence_from_1991_topology") is False
            and method.get("does_not_establish_geodetic_epoch_of_1960_survey") is True
            and method.get("does_not_establish_1963_legal_perimeter") is True):
        raise ValueError("Historical mesh product lineage or accuracy misrepresented")
    edges = graph.get("edges", [])
    if {edge.get("kind") for edge in edges} != EDGE_KINDS or len(edges) != 4:
        raise ValueError("CGEO-11 dependency graph incomplete")
    if not (any(edge.get("source") == "IBGE_1991_MESH_BASE"
                and edge.get("target") == "CONDE_RETROSPECTIVE_1960"
                for edge in edges)
            and any(edge.get("target") == "LEGAL_BOUNDARY_CONDE_1963_LATENT"
                    and edge.get("kind") == "NOT_A_VALIDATED_TEMPORAL_OR_PRECISION_BRIDGE"
                    for edge in edges)):
        raise ValueError("Missing 1991 derivation or unsafe 1963 temporal bridge")
    ref = json.loads(cgeo10_path.read_text(encoding="utf-8"))
    if not (ref.get("id") == "CGEO-10"
            and ref.get("source", {}).get("nominal_map_year") == 1960
            and ref.get("municipality", {}).get("ibge_code") == "2908606"
            and ref.get("historical_1963", {}).get("can_constrain_reentry") is False
            and ref.get("historical_1963", {}).get("legal_boundary_for_date") is None):
        raise ValueError("CGEO-10 changed: cannot import 1960 mesh as 1963 evidence")
    nulls = (
        "polygon_coordinates_in_this_record", "legal_boundary_for_1963",
        "event_point_1963", "position_uncertainty_m", "point_membership_1963"
    )
    if (export.get("reference_polygon_id") != "CGEO-10"
            or any(export.get(key) is not None for key in nulls)
            or any(export.get(key) is not False for key in (
                "can_use_as_survey_grade_polygon",
                "can_filter_1963_reentry_positions",
                "can_compute_1963_location_probability"
            ))
            or export.get("reference_year_is_nominal") is not True):
        raise ValueError("Forbidden precise polygon, coordinate or reentry inference")
    return data


def evaluate(day: str, data: dict) -> dict:
    date.fromisoformat(day)
    export = data["castor_export"]
    return {
        "id": "CGEO-11",
        "requested_date": day,
        "base_mesh_year": data["official_methodology"]["base_mesh_nominal_year"],
        "nominal_year": data["official_methodology"]["nominal_year_of_derived_conde_record"],
        "point_membership": export["point_membership_1963"],
        "legal_boundary_for_1963": export["legal_boundary_for_1963"],
        "positional_accuracy_m": export["position_uncertainty_m"],
        "can_filter_1963_reentry_positions": False,
        "can_compute_1963_location_probability": False,
        "status": export["status"],
    }


def verify_pdf(path: Path, data: dict) -> None:
    raw = path.read_bytes()
    if len(raw) != data["documentary_evidence"]["pdf_size_bytes"]:
        raise ValueError("IBGE methodology PDF length mismatch")
    if hashlib.sha256(raw).hexdigest() != data["documentary_evidence"]["pdf_sha256"]:
        raise ValueError("IBGE methodology PDF SHA256 mismatch")
    if not raw.startswith(b"%PDF"):
        raise ValueError("IBGE methodology payload not PDF")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default="1963-11-08")
    parser.add_argument("--verify-pdf", type=Path)
    args = parser.parse_args()
    data = validate()
    if args.verify_pdf:
        verify_pdf(args.verify_pdf, data)
    print(json.dumps(evaluate(args.date, data), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
