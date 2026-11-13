#!/usr/bin/env python3
"""C241-L22: custody of the printed June 30 NASA orbital table, not sensor TLEs."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

NTRS = "19630012130"
HASH = "8add4b46734e992a213088ef58ba9d58b6385df7b89bb504f79fe8715ec418f3"
BYTES = 274564
LEDGER_FILE = "research/tle_custody/nasa_ssr_jun30_1963_C241-L22.json"
PARENT_GRAPH = "research/constraints/ssr_1963_observable_graph.json"
SOURCE = {
    "ntrs_id": NTRS,
    "citation_url": f"https://ntrs.nasa.gov/citations/{NTRS}",
    "pdf_url": f"https://ntrs.nasa.gov/api/citations/{NTRS}/downloads/{NTRS}.pdf",
    "publication_date": "1963-06-30", "volume": 3, "issue": 13,
    "nasa_tm": "NASA-TM-X-50196", "printed_report": "X-533-63-1",
    "pdf_page_index_zero_based": 12, "pdf_page_one_based": 13, "printed_page": 5,
    "compilation_as_of_utc": "1963-06-30T12:00:00Z",
    "bytes": BYTES, "sha256": HASH,
    "inspection": "VISUAL_FACSIMILE_COVER_CONTEXT_AND_ROTATED_TABLE_PDF_PAGES_1_3_13_2026-11-13",
    "report_compiled_by": ["NASA_GODDARD", "NORAD", "SMITHSONIAN_ASTROPHYSICAL_OBSERVATORY"],
}
ROWS = [
    {"designator": "1963-003A", "norad_crosswalk": 527, "period_min": "94.6", "inclination_deg": "81.89", "apogee_km": 530, "perigee_km": 465},
    {"designator": "1963-003B", "norad_crosswalk": 528, "period_min": "93.7", "inclination_deg": "81.88", "apogee_km": 478, "perigee_km": 423},
    {"designator": "1963-003C", "norad_crosswalk": 529, "period_min": "94.0", "inclination_deg": "81.89", "apogee_km": 512, "perigee_km": 427},
]
DEPS = {
    "april_30": "C241-L16", "july_31": "C241-L18:19630012290",
    "august_15": "C241-L17", "object_crosswalk": "C241-L10",
    "observable_graph_parent": PARENT_GRAPH,
}
UNKNOWNS = (
    "instrumental_epoch_utc", "physical_frame", "tracking_station",
    "measurement_sigma", "instrument_covariance", "original_tle_pair",
    "material_identity_528", "terminal_time", "terminal_location",
)
FLAGS = {
    "source_class": "CONTEMPORARY_PRIMARY_DOCUMENT_COMPILED_ORBITAL_TABLE",
    "independent_sensor_observation": False, "publication_is_element_epoch": False,
    "computed_rate_from_publication_delta": False,
    "graph_status": "CONNECTED_PENDING_CALIBRATION", "lean": "NOT_PROMOTED",
    "physical_domain": "THETA_UNCHANGED", "conde": "INDETERMINATE",
}
FIELDS = {
    "period_min": ("min", "nodal_period_catalogued"),
    "inclination_deg": ("deg", "inclination_catalogued"),
    "apogee_km": ("km", "apogee_altitude_catalogued"),
    "perigee_km": ("km", "perigee_altitude_catalogued"),
}
BRIDGES = ["individual tracking time", "reference frame", "instrumental uncertainty", "dynamical model"]
EDGES = [
    ("C241-L16:1963-04-30", "C241-L22:1963-06-30", "EDITORIAL_SEQUENCE_NOT_INSTRUMENTAL_INTERVAL"),
    ("C241-L22:1963-06-30", "C241-L18:1963-07-31", "EDITORIAL_SEQUENCE_NOT_INSTRUMENTAL_INTERVAL"),
    ("C241-L22:1963-06-30", "C241-L17:1963-08-15", "EDITORIAL_SEQUENCE_NOT_INSTRUMENTAL_INTERVAL"),
    ("C241-L10", "C241-L22", "SECONDARY_OBJECT_CROSSWALK_NOT_PRINTED_IN_1963"),
]


def require(condition, why):
    if not condition:
        raise ValueError(why)


def validate(ledger, graph, april, july_dec, august):
    require(ledger.get("id") == "C241-L22", "wrong occurrence")
    require(ledger.get("source") == SOURCE, "source/page/hash mismatch")
    require(ledger.get("rows") == ROWS, "printed NASA numbers or identity changed")
    require(ledger.get("dependencies") == DEPS, "dependencies disconnected")
    limits = ledger.get("limits", {})
    require(set(limits) == set(UNKNOWNS) | set(FLAGS), "unexpected limits/assumptions")
    require(all(limits.get(k) == v for k, v in FLAGS.items()), "unwarranted scientific promotion")
    require(all(k in limits and limits[k] is None for k in UNKNOWNS), "invented frame, instrument or terminal claim")

    require(graph.get("id") == "C241-L22:OBSERVABLES" and
            graph.get("schema") == "conde.cumulative-constraint-graph-extension/v1" and
            graph.get("parent_graph") == PARENT_GRAPH and
            graph.get("source_ledger") == LEDGER_FILE and
            graph.get("source_family") == "NASA_NORAD_SAO_COMPILED_NOT_AN_INDEPENDENT_SENSOR" and
            graph.get("crosswalk_depends_on") == "C241-L10", "graph source provenance mismatch")
    expected = []
    for row in ROWS:
        obj = row["norad_crosswalk"]
        for key, (unit, op) in FIELDS.items():
            expected.append({
                "id": f"C241-L22:{obj}:{key}", "object_norad": obj,
                "designator": row["designator"], "field": key,
                "printed": row[key], "unit": unit,
                "operator": f"{op}(state_{obj},latent_epoch,frame,force_model)",
                "latent_epoch_utc": None, "frame": None, "measurement_sigma": None,
                "required_bridges": BRIDGES, "admissible_domain_effect": "PENDING_CALIBRATION",
            })
    require(graph.get("observables") == expected, "observables/units/bridges disconnected")
    require([(e.get("from"), e.get("to"), e.get("type")) for e in graph.get("dependency_edges", [])] == EDGES,
            "editorial lineage or crosswalk changed")
    require(graph.get("new_documentary_scalar_fields") == 12 and
            graph.get("independent_instrument_measurements_added") == 0 and
            graph.get("physical_domain_reduced") is False and
            graph.get("lean_promoted") is False, "graph falsely promoted")

    require(april.get("id") == "C241-L16" and
            april.get("april", {}).get("ntrs") == "19630012128" and
            april["april"].get("publication") == "1963-04-30", "April provenance lost")
    ar = april.get("april_rows", [])
    require([r["designator"] for r in ar] == [r["designator"] for r in ROWS] and
            [r["nodal_period_min"] for r in ar] == ["94.6", "94.1", "94.3"], "April controls changed")
    require(july_dec.get("id") == "C241-L18", "July source missing")
    jul = next((r for r in july_dec.get("sources", []) if r.get("ntrs_id") == "19630012290"), {})
    require(jul.get("published") == "1963-07-31" and jul.get("issue") == 15,
            "July edition mismatch")
    jr = jul.get("rows", [])
    require([r["designator"] for r in jr] == [r["designator"] for r in ROWS] and
            [r["period_min"] for r in jr] == ["94.6", "93.6", "93.9"] and
            jr[2].get("perigee_km") == 452, "July errata or controls regressed")
    require(august.get("id") == "C241-L17" and
            august.get("source", {}).get("publication") == "1963-08-15",
            "August provenance mismatched")
    aug = august.get("rows", [])
    require([r["nodal_period_min"] for r in aug] == ["94.6", "93.3", "93.8"],
            "August controls changed")
    period_b = [Decimal(ar[1]["nodal_period_min"]), Decimal(ROWS[1]["period_min"]),
                Decimal(jr[1]["period_min"]), Decimal(aug[1]["nodal_period_min"])]
    publication_deltas = [str(period_b[i+1] - period_b[i]) for i in range(3)]
    return {
        "id": "C241-L22", "source_ntrs": NTRS,
        "documentary_period_528_min": list(map(str, period_b)),
        "publication_deltas_min_NOT_physical_rates": publication_deltas,
        "documentary_scalar_fields_connected": 12,
        "individual_observation_epochs_utc": None,
        "independent_instrument_measurements_added": 0,
        "physical_constraints_activated": 0,
        "conde": "INDETERMINATE",
    }


def audit(ledger, graph, april, july_dec, august, pdf):
    result = validate(ledger, graph, april, july_dec, august)
    require(pdf.startswith(b"%PDF-"), "source is not PDF")
    require(len(pdf) == BYTES and hashlib.sha256(pdf).hexdigest() == HASH,
            "NASA source bytes changed; preserve variant and reinspect before repinning")
    result["pdf_sha256_verified"] = HASH
    result["pdf_bytes_verified"] = len(pdf)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("ledger", "graph", "april", "july-dec", "august", "pdf", "output"):
        p.add_argument(f"--{name}", required=True)
    x = vars(p.parse_args())
    read = lambda name: json.loads(Path(x[name]).read_text(encoding="utf-8"))
    report = audit(read("ledger"), read("graph"), read("april"),
                   read("july_dec"), read("august"), Path(x["pdf"]).read_bytes())
    Path(x["output"]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
