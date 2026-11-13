#!/usr/bin/env python3
"""C241-L29/L30 catalogue holdings -> candidate graph -> Lean/latent inputs.

Bibliographic listings cannot become tracking observations or active orbital
constraints. Upstream custodians own the original ledgers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDINGS = "research/tle_custody/soviet_1963_bibliographic_holdings_C241-L29.json"
CROSS = "research/tle_custody/soviet_1963_cross_id_C241-L30.json"
NASA = "research/tle_custody/nasa_527_1964_1967_crosswalk_C241-L28.json"
OUT = ROOT / "public/data/conde-soviet-catalogue-bridge.json"
IDS = ("C241-L29#1", "C241-L29#2")
OBJECTS = (527, 528, 529)
MISSING = ("original_soviet_designation", "original_soviet_page",
           "original_soviet_issue_scan_sha256", "original_epoch_utc",
           "original_station", "original_measurement",
           "original_orbit_elements", "frame", "time_standard",
           "measurement_units", "instrument_sigma", "origin_of_orbit_fit",
           "same_tracking_as_western")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("Soviet catalogue bridge: " + message)


def build(hold: dict, cross: dict, nasa: dict, parent_hashes: dict) -> dict:
    require(hold["schema"] == "conde.soviet_1963_holdings/v1"
            and hold["id"] == "C241-L29"
            and hold["verified_observations"] == 0
            and hold["orbital_constraint_activated"] is False,
            "holdings are not observational records")
    rows = hold["records"]
    require(len(rows) == 2 and [x["id"] for x in rows] == list(IDS)
            and len({x["url"] for x in rows}) == 2,
            "two distinct institutional catalogue listings required")
    for row in rows:
        require(row["year"] == 1963 and row["http_status"] == 200
                and row["facsimile_read"] is False
                and row["issue_pdf_sha256"] is None
                and row["primary_observation_527_528_529"] is None
                and len(row["sha256"]) == 64
                and row["bytes"] > 0, "invalid holdings evidence level")
    require(cross["schema"] == "conde.soviet-1963-cross-id-readiness/v1"
            and cross["id"] == "C241-L30"
            and cross["upstream"]["holdings"] == HOLDINGS
            and cross["upstream"]["nasa_527"] == NASA,
            "cross-identification lineage mismatch")
    checks = cross["bibliographic_cross_checks"]
    require(len(checks) == 2
            and {c["id"] for c in checks} ==
            {"CNII-AA00566856", "CNII-AA00826990"},
            "unexpected CiNii candidates")
    for check in checks:
        require(check["status"] in (
                    "LIBRARY_METADATA_ONLY",
                    "NO_1963_HOLDING_SHOWN_IN_THIS_CATALOG_VIEW")
                and check["pdf_sha256"] is None
                and check["issue_1963_content_seen"] is False
                and check["independent_observation"] is False
                and check["same_publication_proven"] is False
                and len(check["capture_sha256"]) == 64
                and check["capture_bytes"] > 0,
                "CiNii metadata falsely promoted")
    require(cross["western_object_aliases"][0]["western_crosswalk"]
            == "CONFIRMED_PRIMARY_NASA_CATALOG_ONLY"
            and cross["western_object_aliases"][0]["western_crosswalk_source"]
            == "C241-L28"
            and [r["norad"] for r in cross["western_object_aliases"]]
            == list(OBJECTS)
            and all(r["soviet_record_id"] is None
                    for r in cross["western_object_aliases"])
            and all(r["western_crosswalk"] == "PENDING_PRIMARY_NUMBER_MATCH"
                    for r in cross["western_object_aliases"][1:]),
            "NASA 527 is not a Soviet 528/529 cross-identification")
    require(nasa["schema"] == "conde.nasa-527-1964-1967-crosswalk/v1"
            and nasa["id"] == "C241-L28"
            and nasa["status"] == "PRIMARY_DOCUMENTARY_CROSSWALK_ONLY"
            and len(nasa["source_documents"]) >= 1
            and all(doc["row"]["catalog_number_printed"] == 527
                    and doc["row"]["international_designator_printed"] == "1963 03A"
                    for doc in nasa["source_documents"]),
            "primary NASA documentary number crosswalk absent")
    joins = cross["candidate_joins"]
    require(len(joins) == 6
            and {(j["source_holding_id"], j["target_norad"])
                 for j in joins} == {(s, n) for s in IDS for n in OBJECTS},
            "incomplete or duplicated six-way retrieval candidates")
    for join in joins:
        require(join["join_status"] == "PENDING_NO_ISSUE_FACSIMILE"
                and all(join[k] is None for k in MISSING)
                and join["independent_sensor_confirmed"] is False
                and join["physical_constraint_active"] is False,
                "a candidate was upgraded without primary measurements")
    counts = cross["result"]
    require(counts["candidate_joins_pending"] == 6
            and counts["candidate_joins_confirmed"] == 0
            and counts["contemporary_1963_soviet_527_528_529_instrument_observations_verified"] == 0
            and counts["independent_measurements_added"] == 0
            and counts["orbital_constraints_activated"] == 0
            and counts["lean_activated"] is False,
            "published counts conflict with missing instrumental evidence")
    graph = []
    for record in rows:
        graph.append({
            "from": record["id"], "to": "C241-L30",
            "type": "BIBLIOGRAPHIC_HOLDING_NOT_MEASUREMENT",
            "source_url": record["url"],
            "html_sha256": record["sha256"],
            "issue_numbers": record["issues"],
            "issue_page": None,
        })
    for check in checks:
        graph.append({
            "from": check["id"], "to": check["possible_relation_to"],
            "type": ("UNCONFIRMED_TITLE_SIMILARITY"
                     if check["possible_relation_to"]
                     else "NO_DOCUMENTED_MATCH"),
            "source_url": check["url"],
            "html_sha256": check["capture_sha256"],
            "issue_page": None,
        })
    for join in joins:
        graph.append({
            "from": join["source_holding_id"],
            "to": f"NORAD_{join['target_norad']}_latent_track",
            "type": "RETRIEVAL_CANDIDATE_NOT_IDENTIFIED_TRACK",
            "original_page": None,
            "observing_epoch_utc": None,
            "instrument_sigma": None,
            "activation": False,
        })
    return {
        "schema": "conde.soviet-catalogue-scientific-bridge/v1",
        "id": "ABELHA-SOVIET-C241-L29-L30-01",
        "parent_sha256": parent_hashes,
        "source_occurrences": list(IDS),
        "bibliographic_catalogue_ids": [c["id"] for c in checks],
        "nasa_documentary_crosswalk": "C241-L28:527=1963 03A",
        "source_relation": "TWO_TITLES_HOLDINGS_NOT_INDEPENDENT_TRACKING",
        "evidence_level": "BIBLIOGRAPHIC_METADATA_NOT_INSTRUMENTAL",
        "candidate_join_count": 6,
        "source_dependency_graph": graph,
        "lean_module": "Conde1963.SovietCatalogueCandidate",
        "lean_status": "TYPED_RETRIEVAL_CANDIDATE_NOT_PHYSICAL_THEOREM",
        "simulator_latent_parameters": [
            {"name": f"soviet_1963_independent_track_{n}_unknown",
             "norad": n, "value": None, "active": False}
            for n in OBJECTS
        ],
        "temporal_alignment": None,
        "instrument_covariance": None,
        "original_facsimile_sha256": None,
        "independent_observations": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": cross["next_test"],
    }


def render() -> bytes:
    paths = (HOLDINGS, CROSS, NASA)
    raw = [(ROOT / p).read_bytes() for p in paths]
    payload = build(*(json.loads(b) for b in raw),
                    {p: hashlib.sha256(b).hexdigest()
                     for p, b in zip(paths, raw)})
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = render()
    require(len(payload) <= 20_000, "oversized published JSON")
    if args.write:
        OUT.write_bytes(payload)
    else:
        require(OUT.read_bytes() == payload, "published JSON is stale")
    print("SOVIET_CATALOGUE_BRIDGE_OK", len(payload))


if __name__ == "__main__":
    main()
