#!/usr/bin/env python3
"""Index existing curated documentary links for scientific consumers.

Joins only verified, separately-versioned feeds. A documentary citation,
catalog entry, or historical municipality proxy is NEVER a measured 528 state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import export_cgeo10_provenance as cgeo
import export_documentary_dependence as depend
import export_norad_context as norad
import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("public/data/conde-scientific-bridges.json")
INPUTS = (
    ("public/data/conde-declared-dependence.json", depend.build),
    ("public/data/conde-norad-context.json", norad.build),
    ("public/data/conde-cgeo10-provenance.json", cgeo.build),
)
MATRIX = pg.MATRIX_BLOB_SHA

def serialize(value: dict) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"

def expect(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("scientific bridge identity/activation check: " + message)

def build(root: Path = ROOT) -> dict:
    feeds = {}
    input_hashes = []
    for path, builder in INPUTS:
        # Rebuild from documented sources and check canonical bytes: not merely
        # self-consistent with an edited/stale site JSON or an invented copy.
        raw = (root / path).read_bytes()
        calculated = serialize(builder(root)).encode()
        expect(raw == calculated, "stale/tampered source feed: " + path)
        feeds[path] = json.loads(raw)
        input_hashes.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest()})
    documentary, radar, geo = (feeds[p] for p, _ in INPUTS)
    expect(documentary["matrix_git_blob_sha1"] == radar["matrix_git_blob_sha1"]
           == geo["matrix_identity"]["frozen_matrix_git_blob_sha1"] == MATRIX,
           "mixed historical matrix snapshots")
    expect(documentary["epistemic_limits"]["independent_physical_observation_count"] is None
           and documentary["epistemic_limits"]["verified_reentry_time"] is None
           and documentary["epistemic_limits"]["verified_reentry_place"] is None,
           "documentary feed promoted to physical evidence")

    citations = documentary["citation_lineages"]
    by_citation = {(r["snapshot_ref"], r["source_id"]): r for r in citations}
    expect(len(by_citation) == len(citations), "duplicate snapshot-qualified citations")
    records = []
    # Preserve an archived *report* as a statement about the report, not an
    # extra physical observation attributed to the transmitting station.
    tupi = by_citation[(pg.matrix_ref("C01#1"), "FBIS_EOP_UAP_D001")]
    expect(tupi["family_id"] == "RADIO_TUPI_FBIS"
           and any(p["upstream_source_id"] == "RADIO_TUPI_19631108"
                   and p["edges"][-1]["kind"] == "transcribes"
                   for p in tupi["declared_upstream_paths"]),
           "FBIS/Rádio Tupi transcription genealogy lost")
    records.append({
        "id": "REPORT_TUPI_FBIS_C01", "kind": "DOCUMENTED_SECONDHAND_REPORT",
        "source_id": "FBIS_EOP_UAP_D001",
        "occurrence_ref": tupi["snapshot_ref"],
        "matrix_line": tupi["matrix_line"], "row_sha256": tupi["row_sha256"],
        "source_family": tupi["family_id"],
        "upstream_source_ids": ["RADIO_TUPI_19631108"],
        "claim_id": "C01#1:TRANSMISSION_REPORTED",
        "hypothesis_link": "H_CONDE_EVENT_REPORTED_NOT_PHYSICALLY_CONFIRMED",
        "lean_status": "DOCUMENTARY_ONLY_NOT_PHYSICAL_PROOF",
        "simulator_parameter": None, "simulator_value": None,
        "activation": False, "independent_physical_observation_count": None,
    })
    # The NASA report and NTRS catalogue are the same work; neither carries
    # a measured terminal time/place. Exact matrix-line hashes travel to Lean.
    by_source = {s["id"]: s for s in json.loads(
        (root / "research/provenance/lineages.json").read_text())["sources"]}
    expect(by_source["NASA_SSR_19631115"]["work_id"] ==
           by_source["NTRS_19640001198"]["work_id"],
           "NASA and NTRS catalog split into two physical works")
    for occ, sid in (("C197#1", "NASA_SSR_19631115"),
                     ("C198#1", "NTRS_19640001198")):
        item = by_citation[(pg.matrix_ref(occ), sid)]
        expect(item["family_id"] == "NORAD_NASA_TRACKING"
               and item["independent_physical_observation_count"] is None,
               "NASA/NORAD work treated as independent sensor")
        if sid == "NTRS_19640001198":
            expect(any(p["upstream_source_id"] == "NASA_SSR_19631115"
                       and p["edges"][-1]["kind"] == "catalogue_of_same_work"
                       for p in item["declared_upstream_paths"]),
                   "NTRS origin relationship lost")
        records.append({
            "id": "NASA_DAY_" + occ.replace("#", "_"),
            "kind": "DATE_ONLY_CATALOG_OR_REPORT",
            "source_id": sid, "occurrence_ref": item["snapshot_ref"],
            "matrix_line": item["matrix_line"], "row_sha256": item["row_sha256"],
            "source_family": item["family_id"],
            "shared_work_id": by_source[sid]["work_id"],
            "claim_id": occ + ":DOCUMENTARY_DATE_ONLY",
            "hypothesis_link": "H_528_REENTRY_EVENT_TIME_UNKNOWN",
            "lean_status": "DAY_ONLY_PREMISE_NO_TERMINAL_TIME",
            "simulator_parameter": "reentry_terminal_timestamp_528",
            "simulator_value": None, "activation": False,
            "independent_physical_observation_count": None,
        })

    expect(radar["epistemic_limits"]["no_source_is_an_observation_of_norad_528"]
           and radar["nasa_norad_policy_bridge"]["actual_528_measurement_upstream"] is None,
           "external NORAD records promoted to 528 observations")
    expect(len(radar["records"]) == 5, "NORAD audit coverage drift")
    norad_groups = radar["declared_documentary_groups"]
    expect(len(norad_groups) == 2
           and {v for g in norad_groups for v in g["source_ids"]}
           == {r["source_id"] for r in radar["records"]
               if r["source_id"] != "MOR-NORAD-1961-AGREEMENT"},
           "repeated/1964 records grouped incorrectly")
    for item in radar["records"]:
        sid = item["source_id"]
        objects = item["object_ids_reported_in_this_document"]
        expect(item["matrix_occurrence_ref"] is None
               and item["original_pdf_sha256"] is None
               and item["physical_528_constraint"] is None
               and item["independent_528_physical_observation_count"] is None
               and item["role"] == "DOCUMENTARY_CONTEXT_NOT_528_MEASUREMENT"
               and 528 not in objects, "NORAD source became false 528 observation: " + sid)
        is_policy = sid == "MOR-NORAD-1961-AGREEMENT"
        expect(is_policy == (item["source_date"] == "1961-01-16"),
               "policy date/context mismatch")
        if "1964-NOV30" in sid:
            expect(item["source_date"] == "1964-11-30"
                   and item["catalogue_date_claim"] == "1963-11-30",
                   "misdated 1964 original promoted to 1963: " + sid)
        records.append({
            "id": item["occurrence_id"], "kind": (
                "POSSIBLE_DATA_EXCHANGE_POLICY_NOT_LINEAGE" if is_policy
                else "NEGATIVE_OBJECT_OR_EPOCH_CONTROL"),
            "source_id": sid, "occurrence_ref": item["occurrence_id"],
            "source_date": item["source_date"],
            "catalogue_date_claim": item["catalogue_date_claim"],
            "source_audit_sha256": radar["source_audit_sha256"],
            "source_locator": item["source_locator"],
            "objects_in_document": objects,
            "claim_id": item["occurrence_id"] + ":DOCUMENTARY_CONTEXT",
            "hypothesis_link": "H_ORIGINAL_528_TIMED_TRACKING_STILL_UNRECOVERED",
            "lean_status": "NOT_ELIGIBLE_FOR_528_PHYSICAL_PREMISE",
            "simulator_parameter": "original_528_instrument_epoch",
            "simulator_value": None, "activation": False,
            "independent_physical_observation_count": None,
        })

    candidate = geo["constraint_candidate"]
    expect(geo["matrix_identity"]["supplemental_not_in_frozen_C001_C238"]
           and geo["matrix_identity"]["frozen_matrix_occurrence_count_delta"] == 0
           and geo["source_id"] == cgeo.SOURCE_ID
           and geo["occurrence_id"] == cgeo.OCCURRENCE_ID
           and geo["source_independence"]["independent_observation_count"] is None
           and candidate["id"] == "CGEO10_CONDE_BA_BOUNDARY_ON_1963_11_08"
           and candidate["activation"] is False
           and candidate["status"] == "CONNECTED_PENDING_CALIBRATION"
           and candidate["lean_status"] == "NOT_PROMOTED"
           and candidate["simulation_status"] == "CANDIDATE_NOT_ACTIVATED"
           and all(candidate[k] is None for k in (
               "boundary_value", "event_position", "horizontal_error_m",
               "geodetic_epoch", "verified_reentry_point", "verified_reentry_time"))
           and len(candidate["required_bridges"]) == 4,
           "CGEO-10 retrospective proxy promoted to 1963 observation")
    records.append({
        "id": "CGEO10_1963_BOUNDARY_LATENT",
        "kind": "CONDITIONAL_CARTOGRAPHIC_BRIDGE",
        "source_id": geo["source_id"], "occurrence_ref": geo["occurrence_id"],
        "source_family": geo["source_independence"]["family"],
        "claim_id": "CGEO-10", "hypothesis_link": candidate["id"],
        "lean_status": candidate["lean_status"],
        "simulator_parameter": "sim_param_legal_boundary_Conde_BA_1963",
        "simulator_value": None, "activation": False,
        "required_bridges": candidate["required_bridges"],
        "independent_physical_observation_count": None,
    })

    expect(len({r["id"] for r in records}) == len(records) == 9,
           "duplicate or missing scientific crosswalk entries")

    # A complete citation inventory is not a complete inventory of physical
    # constraints. Keep every curated source->occurrence edge visible to
    # Polvo/site, including the second C232#1 archival citation. The only
    # existing scientific bridges are the three explicit documentary records
    # above; every other citation remains unassessed, not independent.
    direct = {(r["occurrence_ref"], r["source_id"]): r for r in records
              if r["occurrence_ref"].startswith(pg.MATRIX_SNAPSHOT_ID + ":")}
    expect(len(direct) == 3, "unexpected direct matrix bridge coverage")
    coverage = []
    for item in sorted(citations, key=lambda x: (x["snapshot_ref"], x["source_id"])):
        key = item["snapshot_ref"], item["source_id"]
        bridge = direct.get(key)
        expect(item["matrix_line"] > 0 and len(item["row_sha256"]) == 64
               and item["independent_physical_observation_count"] is None,
               "invalid curated citation identity or physical status")
        coverage.append({
            "occurrence_ref": item["snapshot_ref"],
            "matrix_line": item["matrix_line"],
            "row_sha256": item["row_sha256"],
            "source_id": item["source_id"],
            "source_family": item["family_id"],
            "declared_upstream_source_ids": sorted({
                path["upstream_source_id"]
                for path in item["declared_upstream_paths"]}),
            "bridge_record_id": bridge["id"] if bridge else None,
            "hypothesis_link": bridge["hypothesis_link"] if bridge else None,
            "lean_status": (bridge["lean_status"] if bridge
                            else "DOCUMENTARY_ONLY_NOT_ASSESSED"),
            "simulator_parameter": bridge["simulator_parameter"] if bridge else None,
            # The underlying bridge record already stores its null value;
            # do not duplicate it for every source->occurrence edge.
            "activation": False,
        })
    expect(len(coverage) == documentary["citation_edges"]
           and len({(x["occurrence_ref"], x["source_id"]) for x in coverage})
               == len(coverage)
           and len({x["occurrence_ref"] for x in coverage})
               == documentary["curated_occurrences"]
           and len(coverage) - sum(x["bridge_record_id"] is not None
                                   for x in coverage) == 26,
           "citation coverage does not match curated documentary graph")
    # C232#1 is one matrix occurrence with two *documentary* citations,
    # not two sightings. Preserve their separate source IDs without cloning
    # an observation or silently collapsing one citation.
    c232 = [x for x in coverage if x["occurrence_ref"] == pg.matrix_ref("C232#1")]
    expect(len(c232) == 2 and len({x["source_id"] for x in c232}) == 2
           and len({x["row_sha256"] for x in c232}) == 1
           and all(x["bridge_record_id"] is None for x in c232),
           "C232 two-source documentary identity collapsed/promoted")
    return {
        "schema": "conde.scientific-documentary-bridge-index/v1",
        "matrix_git_blob_sha1": MATRIX,
        "source_feeds_sha256": input_hashes,
        "records": records,
        "citation_coverage": coverage,
        "citation_coverage_counts": {
            "curated_edges": len(coverage),
            "curated_occurrences": documentary["curated_occurrences"],
            "unmapped_occurrences": documentary["unmapped_occurrences"],
            "explicit_documentary_bridges": len(direct),
            "documentary_edges_not_assessed_for_lean": len(coverage) - len(direct),
        },
        "epistemic_limits": {
            "new_528_instrumental_observations": 0,
            "activated_constraints": 0,
            "independent_physical_observation_count": None,
            "verified_reentry_place": None,
            "verified_reentry_time": None,
            "all_links_conditional_or_documentary": True,
        },
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write-site", action="store_true")
    g.add_argument("--check-site", action="store_true")
    args = ap.parse_args()
    data = serialize(build()).encode()
    if len(data) > 20_000:
        raise SystemExit("scientific bridge export exceeds 20,000 bytes")
    path = ROOT / OUTPUT
    if args.write_site:
        path.write_bytes(data)
    elif not path.is_file() or path.read_bytes() != data:
        raise SystemExit("stale scientific bridge export")
    print("SCIENTIFIC_BRIDGE_OK", len(build()["records"]), len(data), "bytes")

if __name__ == "__main__":
    main()
