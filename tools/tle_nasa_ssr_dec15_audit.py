#!/usr/bin/env python3
"""C241-L21: a December NASA compilation is not a dated sensor measurement."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

PIN = ("d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f", 958927)
SOURCE = {
    "ntrs_id": "19640003479",
    "citation_url": "https://ntrs.nasa.gov/citations/19640003479",
    "pdf_url": "https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf",
    "publication_date": "1963-12-15",
    "volume": 3, "issue": 24, "nasa_tm": "NASA-TM-X-51375",
    "printed_report": "X-533-63-1",
    "pdf_page_index_zero_based": 6, "pdf_page_one_based": 7, "printed_page": 5,
    "compilation_as_of_utc": "1963-12-15T12:00:00Z",
    "bytes": PIN[1], "sha256": PIN[0],
    "inspection": "VISUAL_FACSIMILE_COVER_AND_TABLE_PDF_PAGES_2_AND_7_2026-11-13",
    "report_compiled_by": [
        "NASA_GODDARD", "NORAD", "SMITHSONIAN_ASTROPHYSICAL_OBSERVATORY"]
}
ROWS = [
    {"designator": "1963-003A", "norad_crosswalk": 527,
     "period_min": "94.6", "inclination_deg": "81.88", "apogee_km": 532,
     "perigee_km": 459},
    {"designator": "1963-003C", "norad_crosswalk": 529,
     "period_min": "91.6", "inclination_deg": "81.87", "apogee_km": 352,
     "perigee_km": 347},
]
DEPENDENCIES = {
    "nov15": "C241-L19", "nov30": "C241-L18:19640002493",
    "dec31": "C241-L18:19640005618", "object_crosswalk": "C241-L10",
    "institutional_provenance": "C241-L20#1", "catalog_decay_day": "C197#1",
    "observable_graph_parent": "research/constraints/ssr_1963_observable_graph.json",
}
UNKNOWN = (
    "instrumental_epoch_utc", "physical_frame", "tracking_station",
    "measurement_sigma", "instrument_covariance", "original_tle_pair",
    "material_identity_528", "terminal_time", "terminal_location"
)
EXPECTED_EDGES = [
    ("C241-L19:1963-11-15", "C241-L21:1963-12-15"),
    ("C241-L18:1963-11-30", "C241-L21:1963-12-15"),
    ("C241-L21:1963-12-15", "C241-L18:1963-12-31"),
    ("C241-L20#1", "C241-L21"),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(ledger, graph, nov15, jul_dec):
    require(ledger.get("id") == "C241-L21", "wrong evidence occurrence")
    require(ledger.get("source") == SOURCE, "unverified source/pages/hash")
    require(ledger.get("rows") == ROWS, "NASA table transcription mismatch")
    require(ledger.get("not_listed_in_objects_in_orbit") == ["1963-003B"],
            "incorrect absence scope")
    require(ledger.get("absence_meaning") ==
            "NOT_A_NEW_TERMINAL_OBSERVATION_AND_NOT_PROOF_OF_OBJECT_IDENTITY",
            "absence falsely used as a physical observation")
    require(ledger.get("dependencies") == DEPENDENCIES, "missing provenance edges")
    limits = ledger["limits"]
    expected_flags = {
        "source_class": "CONTEMPORARY_PRIMARY_DOCUMENT_COMPILED_ORBITAL_TABLE",
        "independent_sensor_observation": False,
        "publication_is_element_epoch": False,
        "computed_rate_from_publication_delta": False,
        "graph_status": "CONNECTED_PENDING_CALIBRATION",
        "lean": "NOT_PROMOTED", "physical_domain": "THETA_UNCHANGED",
        "conde": "INDETERMINATE",
    }
    require(all(limits.get(k) == v for k, v in expected_flags.items()),
            "unjustified scientific promotion")
    require(all(k in limits and limits[k] is None for k in UNKNOWN),
            "invented instrument, frame, precision or terminal location")
    require(set(limits) == set(expected_flags) | set(UNKNOWN),
            "unknown science assumption inserted")
    require(graph.get("id") == "C241-L21:OBSERVABLES" and
            graph.get("schema") == "conde.cumulative-constraint-graph-extension/v1" and
            graph.get("parent_graph") == DEPENDENCIES["observable_graph_parent"] and
            graph.get("source_ledger") ==
            "research/tle_custody/nasa_ssr_dec15_1963_C241-L21.json" and
            graph.get("source_family") ==
            "NASA_NORAD_SAO_COMPILED_NOT_AN_INDEPENDENT_SENSOR" and
            graph.get("crosswalk_depends_on") == "C241-L10",
            "observable graph provenance mismatch")
    require(len(graph.get("observables", [])) == 2 and
            len(graph.get("other_printed_fields", [])) == 2,
            "incomplete graph objects")
    for obs, row, aux in zip(graph["observables"], ROWS,
                             graph["other_printed_fields"]):
        obj = row["norad_crosswalk"]
        require(
            obs.get("id") == f"C241-L21:{obj}:period" and
            obs.get("object_norad") == obj and
            obs.get("printed") == row["period_min"] and obs.get("unit") == "min" and
            obs.get("operator") ==
            f"nodal_period_catalogued(state_{obj},latent_epoch,frame,force_model)" and
            obs.get("latent_epoch_utc") is None and obs.get("frame") is None and
            obs.get("measurement_sigma") is None and
            obs.get("required_bridges") == [
                "individual tracking time", "reference frame",
                "instrumental uncertainty", "dynamical model"] and
            obs.get("admissible_domain_effect") == "PENDING_CALIBRATION",
            "observable graph has missing bridge or invented epoch")
        require(aux == {
            "object_norad": obj, "inclination_deg": row["inclination_deg"],
            "apogee_km": row["apogee_km"], "perigee_km": row["perigee_km"]},
            "non-period observables not connected")
    require(
        [(e.get("from"), e.get("to")) for e in graph["dependency_edges"]] ==
        EXPECTED_EDGES and
        all(e.get("type") in (
            "EDITORIAL_SEQUENCE_NOT_INSTRUMENTAL_INTERVAL",
            "INSTITUTIONAL_COMPILATION_LINEAGE_ONLY")
            for e in graph["dependency_edges"]) and
        graph.get("independent_instrument_measurements_added") == 0 and
        graph.get("physical_domain_reduced") is False and
        graph.get("lean_promoted") is False,
        "graph was promoted or disconnected")
    require(nov15.get("id") == "C241-L19" and
            len(nov15.get("documents", [])) == 1 and
            nov15["documents"][0]["ntrs"] == "19640001198" and
            nov15["documents"][0]["date"] == "1963-11-15",
            "November 15 chain changed")
    require(jul_dec.get("id") == "C241-L18", "historical endpoints missing")
    by_id = {doc["ntrs_id"]: doc for doc in jul_dec["sources"]}
    require("19640002493" in by_id and "19640005618" in by_id,
            "November 30/December 31 source missing")
    nov30, dec31 = by_id["19640002493"], by_id["19640005618"]
    require((nov30["published"], nov30["issue"], dec31["published"],
             dec31["issue"]) ==
            ("1963-11-30", 23, "1963-12-31", 25),
            "historical edition sequence changed")
    require(dec31.get("transcription_conflict", {}).get("status") ==
            "RESOLVED_AS_TRANSCRIPTION_ERRATUM_NOT_INSTRUMENT_VALIDATION",
            "December 31 value is still disputed")
    editions = [nov15["documents"][0], nov30, ledger, dec31]
    seq = []
    for designator, obj in (("1963-003A", 527), ("1963-003C", 529)):
        values = []
        for edition in editions:
            row = next((x for x in edition["rows"]
                        if x["designator"] == designator), None)
            require(row is not None, "object missing in predecessor/successor")
            values.append(Decimal(row.get("period_min", "")))
        require(values == (
            [Decimal("94.6")] * 4 if obj == 527 else
            [Decimal(x) for x in ("92.6", "92.2", "91.6", "89.2")]),
            "historical period chain conflicts with examined facsimile")
        seq.append({
            "object_norad": obj, "designator": designator,
            "publications_not_sensor_epochs": [
                "1963-11-15", "1963-11-30", "1963-12-15", "1963-12-31"],
            "printed_nodal_period_min": [str(v) for v in values],
            "published_deltas_min_NOT_physical_rates": [
                str(values[i+1] - values[i]) for i in range(3)],
            "individual_observation_epochs_utc": None,
            "instrument_error_model": None,
        })
    return seq


def audit(ledger, graph, nov15, jul_dec, pdf):
    seq = validate(ledger, graph, nov15, jul_dec)
    require(pdf.startswith(b"%PDF-"), "not PDF")
    require((hashlib.sha256(pdf).hexdigest(), len(pdf)) == PIN,
            "source bytes changed; preserve variant and reinspect")
    return {
        "occurrence": "C241-L21",
        "source_pdf_sha256": PIN[0], "source_pdf_bytes": PIN[1],
        "source_ntrs": "19640003479",
        "series": seq,
        "physical_constraints_activated": 0,
        "compiled_source_observations_connected": 2,
        "independent_instrument_measurements_added": 0,
        "pdf_pixels_reviewed_in_CI": False,
        "conde": "INDETERMINATE",
    }


def main():
    p = argparse.ArgumentParser()
    for key in ("ledger", "graph", "nov15", "jul_dec", "pdf", "output"):
        p.add_argument("--" + key.replace("_", "-"), type=Path, required=True)
    args = p.parse_args()
    sources = [
        json.loads(getattr(args, key).read_text(encoding="utf-8"))
        for key in ("ledger", "graph", "nov15", "jul_dec")]
    result = audit(*sources, args.pdf.read_bytes())
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("C241-L21: NASA Dec 15 edition connected; instrument epoch/sigma NOT_FOUND")


if __name__ == "__main__":
    main()
