#!/usr/bin/env python3
"""C241-L43 archival SAO finding aid -> pending optical observables (not tracks)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .tle_sao_archive_leads_c241_l43 import check_claims
else:
    from tle_sao_archive_leads_c241_l43 import check_claims

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "research/tle_custody/sao_archival_tracking_leads_C241-L43.json"
LEDGER_SHA256 = "0b00fea9d5a2ed28e4e7bebbf212bd6c94dd6fe1e9e15b0a8a80683adf7d8154"
EAD_SHA256 = "15b9c1a3e513690b0d66eec177a2b6897c373fbfe96cd8925e722765e6229f02"
OUT = ROOT / "public/data/conde-sao-1963-archive-bridge.json"
ENTRY_IDS = ("refIDd1e2142", "refIDd1e2187", "refIDd1e2240", "refIDd1e2360")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("SAO archival bridge: " + reason)


def build(lock: dict, ledger_digest: str) -> dict:
    require(ledger_digest == LEDGER_SHA256, "upstream ledger SHA changed")
    check_claims(lock)
    require(lock["source_sha256"] == EAD_SHA256
            and lock["source_bytes"] == 90490
            and lock["retrieved_at_utc_date"] == "2026-11-13",
            "EAD source custody drift")
    require(lock["original_records_inspected"] is False
            and lock["object_match_verified"] is False
            and lock["instrumental_observations_recovered"] == 0,
            "archive metadata promoted to an observation")
    require(lock["possible_objects"] == [527, 528, 529]
            and lock["instrument_epoch_utc"] is None
            and lock["sensor_or_station"] is None
            and lock["instrument_uncertainty"] is None,
            "invented object measurement")
    require(lock["domain_restrictions_activated"] == 0
            and lock["conde_reentry_location"] == "INDETERMINATE",
            "unjustified orbital narrowing")
    files = {a["id"]: a for a in lock["archive_entries"]}
    require(set(files) == set(ENTRY_IDS), "altered archive entries")
    source = "SIA.FARU0171:EAD:" + EAD_SHA256
    edges = [
        {"from": "C241-L43", "to": source,
         "relation": "CUSTODIED_INSTITUTIONAL_FINDING_AID",
         "independent_observation": False},
    ]
    archive_files = []
    for key in ENTRY_IDS:
        item = files[key]
        node = "SIA.FARU0171:" + key
        archive_files.append({
            "id": node, "archive_id": key, "box": item["box"],
            "title": item["title"], "url": item["url"],
            "document_contents_inspected": False,
            "physical_observables_recovered": 0,
        })
        edges.append({"from": source, "to": node,
                      "relation": "ARCHIVAL_FILE_LEVEL_DESCRIPTION_ONLY",
                      "independent_observation": False})
    # The optical-reports folder is the only direct target candidate; other
    # folders may supply chronology, identification and clock calibration.
    missing_roles = {
        ENTRY_IDS[0]: "ORIGINAL_OPTICAL_RECORD_AND_OBJECT_ID",
        ENTRY_IDS[1]: "OBSERVATION_PIPELINE_PROVENANCE",
        ENTRY_IDS[2]: "TARGET_DESIGNATION_CROSSWALK",
        ENTRY_IDS[3]: "TIME_STANDARD_AND_CLOCK_CALIBRATION",
    }
    for key, role in missing_roles.items():
        edges.append({"from": "SIA.FARU0171:" + key,
                      "to": "pending_sao_1963:" + role,
                      "relation": "LOCATOR_FOR_REQUIRED_ORIGINAL",
                      "independent_observation": False})
    latents = []
    for norad, piece in [(527, "1963-003A"), (528, "1963-003B"),
                         (529, "1963-003C")]:
        candidate = "sao_optical_target_match_" + str(norad)
        edges.append({"from": "SIA.FARU0171:" + ENTRY_IDS[0],
                      "to": candidate,
                      "relation": "SEARCH_CANDIDATE_NOT_TARGET_IDENTIFIED",
                      "independent_observation": False})
        latents.append({
            "object_id": norad, "international_designator": piece,
            "match_verified": False, "candidate_node": candidate,
            "fields": {
                "observation_epoch_utc": None,
                "station_id": None,
                "optical_ra_dec_rad": None,
                "reference_frame": None,
                "angular_covariance_rad2": None,
                "time_calibration_error_seconds": None,
            },
            "activation": False,
            "requires": ["original_1963_optical_report",
                         "explicit_object_designation_crosswalk",
                         "observation_timestamp_and_clock_standard",
                         "station_identity_and_reference_frame",
                         "instrument_calibration_and_covariance"],
        })
    return {
        "schema": "conde.sao-1963-archive-scientific-bridge/v1",
        "id": "ABELHA-C241-L43-SAO-01",
        "source_occurrence": "C241-L43",
        "source_scope": "INSTITUTIONAL_FINDING_AID_NOT_PRIMARY_TRACK",
        "related_context_occurrences": ["C195#1", "C196#1"],
        "related_context_not_independent_evidence": True,
        "input_ledger_path": LEDGER,
        "input_ledger_sha256": ledger_digest,
        "source": {
            "archive_collection": lock["collection_id"],
            "ead_url": lock["source_url"],
            "ead_bytes": lock["source_bytes"],
            "ead_sha256": lock["source_sha256"],
            "hash_scope": "COMPLETE_EAD_XML_NOT_ARCHIVED_REPORT_CONTENT",
            "retrieved_at_utc_date": lock["retrieved_at_utc_date"],
        },
        "archive_files": archive_files,
        "dependency_graph": edges,
        "hypotheses": [
            "H_ARCHIVE_BOX_22_MAY_CONTAIN_1963_OPTICAL_REPORTS",
            "H_ORIGINAL_REPORT_MAY_IDENTIFY_527_528_OR_529",
            "H_CLOCK_FILES_MAY_DOCUMENT_NETWORK_TIMING_NOT_TARGET_TIME",
        ],
        "lean_candidate": "Conde1963.saoOpticalArchiveRoutes",
        "lean_status": "DOCUMENTARY_TYPED_CANDIDATE_NOT_COMPILED_PHYSICAL_THEOREM",
        "candidate_constraint": "IF_REPORT_WITH_OBJECT_EPOCH_FRAME_ERROR_THEN_OPTICAL_OBSERVABLE_CONSTRAINT",
        "candidate_constraint_status": "CONNECTED_PENDING_SOURCE_RETRIEVAL_AND_CALIBRATION",
        "simulator_latent_parameters": latents,
        "independent_instrumental_observations_added": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_falsifier": "Inspect file-level 1963 SAO optical reports and demand target identification, station, UTC epoch, frame and calibrated error; absence in one folder is not global absence",
    }


def render(root: Path = ROOT) -> bytes:
    raw = (root / LEDGER).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == LEDGER_SHA256, "input ledger bytes differ from pinned source")
    record = build(json.loads(raw), digest)
    return (json.dumps(record, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-site", action="store_true")
    parser.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.write_site:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(content)
    elif args.check_site:
        require(OUT.read_bytes() == content, "published output differs from current export")
    else:
        print(content.decode(), end="")


if __name__ == "__main__":
    main()
