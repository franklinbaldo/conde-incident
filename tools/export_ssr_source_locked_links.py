#!/usr/bin/env python3
"""Source-locked NASA SSR canonical bridge; never rewrite the frozen 38-kB graph.

Published table values are not instrument observations, and the 527/529
control rows cannot be converted into NORAD 528's terminal state.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "formal/scripts"))
from check_cumulative_connections import validate  # noqa: E402

LEGACY = ROOT / "research/constraints/ssr_1963_observable_graph.json"
NOV15 = ROOT / "research/tle_custody/nasa_ssr_nov15_1963_C241-L19.json"
NOV30 = ROOT / "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
OUT = ROOT / "public/data/conde-ssr-source-locked-links.json"
HOUSE = ROOT / "research/tle_custody/congressional_ssr_chain_C241-L20.json"
HOUSE_SPEC = {
    "id": "C241-L20#1",
    "url": "https://www.govinfo.gov/content/pkg/SERIALSET-12667_05_00-002-0197-0000/pdf/SERIALSET-12667_05_00-002-0197-0000.pdf",
    "sha": "a08b4c505a37c09d1eb9c33ed14cc56228fd5e67f7ec1645f38554310bd60ca0",
    "bytes": 9297493,
    "report_date": "1965-03-22",
    "agreement_date": "1961-11-07",
}
HOUSE_LINKS = {
    ("NASA_NORAD_SAO_COMPUTATION", "NASA_GSFC_SSR_PUBLICATION",
     "COMPILATION_WITH_MULTIPLE_CONTRIBUTORS", 7),
    ("NORAD_SPADATS_CATALOG", "NASA_GSFC",
     "PERIODIC_UNCLASSIFIED_CATALOG_TRANSMISSION", 14),
    ("NAVSPASUR", "NASA_GSFC",
     "DIRECT_UNCLASSIFIED_ORBITAL_DATA_AUTHORIZED", 14),
    ("NORAD_SPADATS_SENSORS", "NASA_GSFC",
     "SENSOR_DATA_BY_REQUEST_FOR_NASA_TRACKING_RESPONSIBILITY", 14),
}

SOURCE = {
    "1963-11-15": {
        "id": "C241-L19#1", "ntrs": "19640001198",
        "sha": "0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674",
        "pdf_bytes": 327613,
    },
    "1963-11-30": {
        "id": "C241-L18:19640002493", "ntrs": "19640002493",
        "sha": "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d",
        "pdf_bytes": 1266393,
    },
}
DESIGNATORS = {"1963-003A": 527, "1963-003C": 529}
FIELDS = {
    "nodal_period": ("period_min", "min"),
    "inclination": ("inclination_deg", "deg"),
    "apogee": ("apogee_km", "km"),
    "perigee": ("perigee_km", "km"),
}
CELL = "SSR-1963-11-30-NORAD527-nodal_period"
DELTA = "SSR-PUBLICATIONS-DELTA-527-nodal_period"


def _documents(nov15: dict, nov30: dict) -> dict:
    if nov15.get("id") != "C241-L19" or nov30.get("id") != "C241-L18":
        raise ValueError("NASA custodian identity mismatch")
    if len(nov15.get("documents", [])) != 1:
        raise ValueError("November 15 custodian count mismatch")
    try:
        d15 = nov15["documents"][0]
        d30 = next(d for d in nov30["sources"] if d["ntrs_id"] == SOURCE["1963-11-30"]["ntrs"])
    except (KeyError, StopIteration, TypeError) as exc:
        raise ValueError("November 30 source not uniquely traceable") from exc
    if sum(d["ntrs_id"] == SOURCE["1963-11-30"]["ntrs"] for d in nov30["sources"]) != 1:
        raise ValueError("duplicate November 30 edition")
    result = {}
    for date, doc, sha_key, size_key, ntrs_key, pdf_key, pg_key, date_key in [
        ("1963-11-15", d15, "sha256", "bytes", "ntrs", "pdf", "page_index", "date"),
        ("1963-11-30", d30, "sha256", "bytes", "ntrs_id", "pdf_url", "pdf_page_index", "published"),
    ]:
        spec = SOURCE[date]
        canonical_pdf = (f"https://ntrs.nasa.gov/api/citations/{spec['ntrs']}"
                         f"/downloads/{spec['ntrs']}.pdf")
        if (doc[sha_key], doc[size_key], doc[ntrs_key], doc[pdf_key],
            doc[pg_key], doc["printed_page"], doc[date_key]) != (
            spec["sha"], spec["pdf_bytes"], spec["ntrs"], canonical_pdf, 6, 5, date
        ):
            raise ValueError(f"NASA {date} custody, digest, edition, or page mismatch")
        if len(doc["rows"]) != 2:
            raise ValueError(f"NASA {date} must have exactly two control rows")
        rows = {}
        for item in doc["rows"]:
            key = item["designator"]
            if key not in DESIGNATORS or key in rows:
                raise ValueError("duplicate or foreign NORAD designator")
            rows[key] = item
        if set(rows) != set(DESIGNATORS):
            raise ValueError("incomplete 527/529 controls")
        result[date] = (doc, rows)
    if d30["as_of_utc"] != "1963-11-30T12:00:00Z":
        raise ValueError("published-as-of metadata modified")
    return result


def validate_institutional_chain(source: dict) -> dict:
    """Retrospective documentary ancestry, NEVER a 1963 observation."""
    if (
        source.get("id") != HOUSE_SPEC["id"]
        or source.get("url") != HOUSE_SPEC["url"]
        or source.get("pdf_sha256") != HOUSE_SPEC["sha"]
        or source.get("pdf_bytes") != HOUSE_SPEC["bytes"]
        or source.get("report_published_on") != HOUSE_SPEC["report_date"]
        or source.get("historical_agreement_on") != HOUSE_SPEC["agreement_date"]
        or source.get("printed_pages") != [7, 14]
        or source.get("pdf_page_indices") != [12, 19]
        or source.get("source_type") != "primary_institutional_record_reprinted_in_1965"
        or source.get("source_scope") != "INSTITUTIONAL_DATA_FLOW_NOT_OBJECT_MEASUREMENT"
    ):
        raise ValueError("congressional report custody or date mismatch")
    rows = source.get("transcribed_links")
    if not isinstance(rows, list) or len(rows) != len(HOUSE_LINKS):
        raise ValueError("incomplete or duplicate institutional provenance links")
    expected_link_fields = {"from", "to", "relation", "printed_page"}
    if any(set(r) != expected_link_fields for r in rows):
        raise ValueError("unknown institutional link field or missing required field")
    keys = [(r["from"], r["to"], r["relation"], r["printed_page"]) for r in rows]
    if len(set(keys)) != len(keys) or set(keys) != HOUSE_LINKS:
        raise ValueError("altered institutional provenance relationship")
    occurrences = source.get("relevant_occurrences", [])
    if (not isinstance(occurrences, list)
            or len(occurrences) != 4 or len(set(occurrences)) != 4):
        raise ValueError("duplicate institutional occurrence or incomplete references")
    if (
        source.get("per_object_527_528_529_input_lineage_verified") is not False
        or source.get("observation_epoch_utc") is not None
        or source.get("instrument_covariance") is not None
        or source.get("activation") != "DOCUMENTARY_DEPENDENCY_ONLY"
        or source.get("physical_domain_effect") != "THETA_UNCHANGED"
        or set(source.get("relevant_occurrences", [])) !=
        {"C179#1", "C197#1", "C241-L19#1", "C241-L18:19640002493"}
    ):
        raise ValueError("unverified institutional report promoted into sensor evidence")
    return {
        "occurrence_id": source["id"],
        "source_url": source["url"],
        "source_sha256": source["pdf_sha256"],
        "source_bytes": source["pdf_bytes"],
        "report_published_on": source["report_published_on"],
        "agreement_on": source["historical_agreement_on"],
        "relevant_occurrences": source["relevant_occurrences"],
        "institutional_links": rows,
        "per_object_input_lineage": None,
        "sensor_observation_epoch_utc": None,
        "instrument_covariance": None,
        "physical_constraint_activated": False,
        "status": "CONNECTED_PENDING_CALIBRATION",
        "physical_domain_effect": "THETA_UNCHANGED",
    }


def build(nov15: dict, nov30: dict, graph: dict, house: dict) -> dict:
    chain = validate_institutional_chain(house)
    docs = _documents(nov15, nov30)
    # Existing validator checks all 22 connected observations, eight edges,
    # frozen raw 94.8 error, and corrected public handoff 94.6 / delta zero.
    handoff = validate(graph)
    rows = {o["observation"]: o for o in handoff["observations"]}
    if len(rows) != 22:
        raise ValueError("duplicate or missing observable row")
    records = []
    for date, (doc, controls) in docs.items():
        for designator, norad in DESIGNATORS.items():
            for observable, (field, unit) in FIELDS.items():
                row_id = f"SSR-{date}-NORAD{norad}-{observable}"
                row = rows.get(row_id)
                if row is None:
                    raise ValueError("missing canonical NASA observation " + row_id)
                ledger_value = Decimal(str(controls[designator][field]))
                if not ledger_value.is_finite():
                    raise ValueError("non-finite ledger value")
                if (row["source"] != f"NASA-SSR-{date}" or
                    row["reported_unit"] != unit or
                    Decimal(str(row["reported_value"])) != ledger_value or
                    row["observed_at_utc"] is not None or
                    row["measurement_error"] is not None or
                    row["status"] != "CANDIDATE_NOT_ACTIVATED"):
                    raise ValueError("NASA ledger/handoff mismatch: " + row_id)
                records.append((row_id, date, norad, observable, ledger_value, unit))
    if len(records) != 16:
        raise ValueError("lost NASA source-linked cells")
    cell = rows[CELL]
    if Decimal(str(cell["reported_value"])) != Decimal("94.6"):
        raise ValueError("94.8 must not reach the canonical handoff")
    if Decimal(str(cell["canonical_value"])) != Decimal("5676"):
        raise ValueError("wrong canonical seconds")
    deltas = [x for x in handoff["derived_connections"] if x["id"] == DELTA]
    if len(deltas) != 1 or Decimal(str(deltas[0]["derived_arithmetic"])) != Decimal("0"):
        raise ValueError("legacy +0.2 min must not reach the canonical handoff")
    if deltas[0]["status"] != "CONNECTED_PENDING_EPOCH_AND_COVARIANCE":
        raise ValueError("published delta promoted into physical time derivative")
    if handoff["constraints_activated"] != 0:
        raise ValueError("source-table values cannot activate physics")
    return {
        "schema": "conde.ssr-source-locked-links/v1",
        "id": "C241-L18-L19-LEGACY527-NOV30",
        "legacy_graph_path": LEGACY.relative_to(ROOT).as_posix(),
        "legacy_row_id": CELL,
        "legacy_blob_preserved": True,
        "legacy_transcription_value_rejected_min": "94.8",
        "canonical_value_min": "94.6",
        "canonical_value_seconds": "5676",
        "documentary_delta_id": DELTA,
        "documentary_delta_min": "0.0",
        "linked_sources": [
            {
                "occurrence_id": SOURCE[date]["id"],
                "published_on": date,
                "document_ntrs": SOURCE[date]["ntrs"],
                "pdf_page_index": 6,
                "printed_page": 5,
                "pdf_sha256": SOURCE[date]["sha"],
                "pdf_bytes": SOURCE[date]["pdf_bytes"],
                "matrix_context": ["C197#1", "C198#1"] if date == "1963-11-15" else ["C183#1", "C199#1"],
                "relationship": "different_editions_same_tracking_family_not_independent_sensors",
            }
            for date in ("1963-11-15", "1963-11-30")
        ],
        "checked_control_cells": len(records),
        "checked_distinct_control_objects": [527, 529],
        "source_family": "NASA_GODDARD_COMPILED_FROM_TRACKING",
        "institutional_provenance": chain,
        "linked_lean_contract": "formal/Conde1963/SsrNovember.lean",
        "lean_claim_scope": "conditional_printed_number_arithmetic_only",
        "simulator_parameter": cell["model_variable"],
        "simulator_observation_epoch_parameter": "t_observed_527_1963-11-30",
        "simulator_observation_epoch_utc": None,
        "simulator_instrument_error": None,
        "simulator_calibrated_value": None,
        "active_physical_constraint": False,
        "status": "CONNECTED_PENDING_CALIBRATION",
        "pending": [
            "original_sensor_records", "observation_epoch_utc",
            "reference_frame", "instrument_covariance", "calibrated_forward_model",
        ],
        "physical_domain_effect": "THETA_UNCHANGED",
    }


def render() -> str:
    graph = json.loads(LEGACY.read_text(encoding="utf-8"))
    a = json.loads(NOV15.read_text(encoding="utf-8"))
    b = json.loads(NOV30.read_text(encoding="utf-8"))
    house = json.loads(HOUSE.read_text(encoding="utf-8"))
    return json.dumps(build(a, b, graph, house), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--write-site", action="store_true")
    p.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    payload = render()
    if args.write_site:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(payload, encoding="utf-8")
    if args.check_site and OUT.read_text(encoding="utf-8") != payload:
        raise SystemExit("stale SSR source-linked bridge: regenerate site artifact")
    print("C241-L18/L19: 16 cells checked; 527 Nov30 94.6 min; physical activation false")


if __name__ == "__main__":
    main()
