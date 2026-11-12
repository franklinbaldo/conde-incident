"""CGEO-09: validate 1944/1953 documentary chronology; never emit 1963 GIS geometry."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/conde_1944_1953_temporal_bridge.json"
SOURCES = ("BA-DEC-12978-1944-ANNEX2-LXXIII", "BA-LEI-628-1953-TEXT", "BA-SEPLAN-SEI-2013-06-26")
HYDRONYMS = (
    "oceano Atlantico / foz do rio Itapicuru",
    "rio Itapicuru / foz do rio Pirangi",
    "rio Pirangi / foz do riacho da Baixa da Vitorina",
    "riacho da Baixa da Vitorina / nascente",
    "nascente do riacho das Pedras",
    "marco a margem do riacho Caranguejo do rio Branco",
)
MISSING = (
    "authentic_1944_legal_annex_and_relevant_errata",
    "authentic_1953_legal_annex_and_relevant_errata",
    "relevant_1959_1963_intervening_acts_and_continuity",
    "spatial_anchor_datum_georeferencing_and_error",
    "event_position_and_reference_frame",
)


def read_contract(path: Path = CONTRACT) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "conde.gis.historical-statutes-bridge/v1":
        raise ValueError("unexpected schema")
    if data.get("id") != "CGEO-09" or data.get("event_date") != "1963-11-08":
        raise ValueError("changed identifier or date")
    if data.get("jurisdiction") != {"name": "Conde", "state": "BA", "ibge_code": "2908606"}:
        raise ValueError("Conde BA identity cannot be changed")
    sources = data.get("sources", [])
    if tuple(s.get("id") for s in sources) != SOURCES:
        raise ValueError("source chain altered")
    if any(s.get("original_facsimile_inspected") is not False
           or s.get("original_publication_pdf_sha256", "missing") is not None
           for s in sources):
        raise ValueError("no primary facsimile or source hash has been verified")
    if (sources[0].get("inspection") != "SEARCH_INDEXED_TRANSCRIPTION_ONLY"
            or sources[1].get("inspection") != "SEARCH_INDEXED_TRANSCRIPTION_ONLY"
            or sources[2].get("inspection") != "SEARCH_INDEXED_OFFICIAL_PUBLICATION"):
        raise ValueError("source inspection status unsupported")
    law = sources[1]
    if (law.get("stated_division_period_start") != "1954-01-01"
            or law.get("stated_division_period_end") != "1958-12-31"
            or law.get("annexes_present_in_republication") is not False
            or law.get("period_after_1958_legal_continuity_proven") is not False):
        raise ValueError("1953 scope or absent annex provenance altered")
    if not (date.fromisoformat(law["stated_division_period_start"])
            <= date.fromisoformat(law["stated_division_period_end"])
            < date.fromisoformat(data["event_date"])):
        raise ValueError("1953 stated term must precede the incident")
    topo = data.get("boundary_1944_topology", {})
    if (topo.get("source_id") != SOURCES[0]
            or tuple(topo.get("route_order_hydronyms", [])) != HYDRONYMS
            or topo.get("named_jurisdiction_in_heading") != "Jandaira"
            or topo.get("adjacent_jurisdiction_in_section") != "Conde"):
        raise ValueError("topological textual transcription modified")
    for field in ("coordinates", "coordinate_datum", "coordinate_epoch",
                  "positional_accuracy_m", "geometry"):
        if topo.get(field, "missing") is not None:
            raise ValueError("unverified geometry/datum not allowed: " + field)
    if (topo.get("transcription_only") is not True
            or topo.get("all_intermediate_vertices_available") is not False
            or topo.get("georeferencing_authorized") is not False):
        raise ValueError("cannot upgrade description to a complete georeferenced boundary")
    bridge = data.get("legal_1944_1953_bridge", {})
    if (bridge.get("law_source_id") != SOURCES[1]
            or bridge.get("linked_source_id") != SOURCES[0]
            or bridge.get("provision") != "art. 2"
            or bridge.get("exact_short_excerpt") != "Continuam em vigor os dispositivos do Decreto n. 12.978"
            or bridge.get("explicit_preservation_in_1953") is not True
            or bridge.get("modified_by_1953_and_annexes") is not True
            or bridge.get("annexes_ii_vi_inspected") is not False
            or bridge.get("conde_jandaira_segment_identity_proven") is not False
            or bridge.get("continuing_unchanged_until_1963_proven") is not False
            or bridge.get("legal_scope_for_1963", "missing") is not None
            or bridge.get("boundary_geometry_for_1963", "missing") is not None
            or bridge.get("graph_status") != "CONNECTED_PENDING_1953_ANNEX_ALTERATIONS_AND_LATER_ACTS"):
        raise ValueError("unverified 1944-to-1953 legal carryover promotion")
    graph = data.get("dependency_graph", {})
    if (graph.get("prior_ids") != ["C24", "CGEO-05", "CGEO-06", "CGEO-08"]
            or graph.get("requires_for_event_date") != list(MISSING)
            or graph.get("boundary_1963", "missing") is not None
            or graph.get("can_constrain_orbital_reentry_1963") is not False
            or graph.get("new_geometric_constraint_activated") is not False
            or graph.get("status") != "CONNECTED_PENDING_PRIMARY_ANNEX_CONTINUITY_AND_GEOREFERENCE"):
        raise ValueError("missing historical bridge must remain explicit")
    carryovers = [link for link in graph.get("links", [])
                  if link.get("type") == "EXPLICIT_ART2_NORMATIVE_CARRYOVER_WITH_1953_MODIFICATIONS"]
    if (len(carryovers) != 1 or carryovers[0].get("source_id") != SOURCES[1]
            or carryovers[0].get("target") != SOURCES[0]
            or "1963" not in carryovers[0].get("scope", "")):
        raise ValueError("normative carryover graph edge missing")
    if set(link["source_id"] for link in graph.get("links", [])) != set(SOURCES) | {"BA-ALEBA-LEI-13720-2017-DO-22166"}:
        raise ValueError("provenance lineage incomplete")
    return data


def evaluate(day: str, data: dict) -> dict:
    target = date.fromisoformat(day)
    law = data["sources"][1]
    end = date.fromisoformat(law["stated_division_period_end"])
    if target > end:
        status = "AFTER_EXPLICIT_1953_DIVISION_PERIOD_CONTINUITY_UNVERIFIED"
    elif target >= date.fromisoformat(law["stated_division_period_start"]):
        status = "WITHIN_STATED_1953_DIVISION_PERIOD_ANNEX_UNVERIFIED"
    else:
        status = "BEFORE_STATED_1953_DIVISION_PERIOD"
    return {
        "schema": "conde.gis.historical-statutes-evaluation/v1",
        "requested_date": target.isoformat(),
        "stated_1953_division_period_end": end.isoformat(),
        "temporal_status": status,
        "1944_statute_carryover_in_1953": data["legal_1944_1953_bridge"]["graph_status"],
        "legal_boundary_for_date": None,
        "point_membership": None,
        "coordinate_reference_system": None,
        "can_constrain_reentry": False,
        "pending": data["dependency_graph"]["requires_for_event_date"]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default="1963-11-08")
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.date, read_contract(args.contract)),
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
