#!/usr/bin/env python3
"""Join recovered 1964 ON20 manual with undecoded 1963 Y20175, without backdating."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = "research/meteorology/ncep_on20_wayback_custody_20261112.json"
PAGES = "research/meteorology/ncep_on20_page_audit_20261112.json"
TAPE = "research/constraints/nmc_y20175_pending_bridge.json"
OUTPUT = "public/data/conde-on20-layout-link.json"


def check(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError("NMC 1963 layout transfer not proven: " + explanation)


def build_from_data(manual: dict, page: dict, tape: dict) -> dict:
    capture = manual["preservation"]
    check(manual["id"] == "MET-NMC-NCEPON-20261112-02"
          and manual["linked_catalog_id"] == "MET-NMC-NCEPON-20261112-01"
          and manual["note_number"] == 20 and manual["published_year"] == 1964
          and manual["epistemic_status"] == "PDF_BYTES_RETRIEVED_CONTENT_NOT_YET_TRANSCRIBED"
          and manual["applicability_to_1963"] == "NOT_ESTABLISHED"
          and manual["physical_constraint"] == "NOT_ACTIVATED",
          "historical manual year, origin, or scope changed")
    check(capture["http_status"] == 200
          and capture["content_type"] == "application/pdf"
          and capture["byte_length"] == 932414
          and capture["sha256"] == "656984ac58ff1632e39b0f62ac80003785ddea0a0de32dfb19c8c612067aabbe"
          and capture["capture_utc"] == "2022-01-19T07:53:33Z"
          and capture["replay_url"].startswith("https://web.archive.org/web/20220119075333id_/"),
          "Wayback custody locator or audited PDF bytes changed")
    check(page["related"] == manual["id"]
          and page["pdf_sha256"] == capture["sha256"]
          and page["pdf_bytes"] == capture["byte_length"]
          and page["page_tree_count"] == capture["page_object_count"] == 23,
          "page inventory not pinned to preserved bytes")
    check(manual["page_visual_inspection"] == "NOT_RUN"
          and manual["revision_beginning_page_12"] == "CATALOG_CLAIM_NOT_VISUALLY_VERIFIED"
          and manual["tape_decoded"] is False and manual["station_day_matches"] is None,
          "unread 1964 pages cannot establish active 1963 field format")
    check(tape["schema"] == "conde.pending-nmc-wind-bridge/v1"
          and tape["inventory_id"] == "MET-NMC-20261112-09"
          and tape["physical_domain"] == "UNCHANGED_NO_ACTIVE_CONSTRAINT"
          and tape["numeric_observations_generated"] == 0
          and tape["source_independence"] == "UNKNOWN_NO_DECODE"
          and len(tape["candidate_queries"]) == 9
          and all(q["query_status"] == "NOT_DECODED_NOT_OBSERVED" for q in tape["candidate_queries"]),
          "Y20175 observations or decoder were silently promoted")
    required = tape["required_evidence_to_activate"]
    check("validated_1963_CRAY_RPTOUT_ON20_decoder" in required
          and "actual_station_day_hits_with_source_offsets_and_qc" in required
          and "validated_transfer_to_Conde_and_reentry_state" in required,
          "downstream physical calibration prerequisites removed")
    return {
        "schema": "conde.on20-historical-layout-candidate/v1",
        "id": "C241-L14-NMC-ON20-LAYOUT",
        "lineage": [
            {"from": manual["linked_catalog_id"], "to": manual["id"],
             "kind": "bibliographic_catalogue_to_wayback_facsimile"},
            {"from": manual["id"], "to": "1963_ON20_LAYOUT_UNVERIFIED",
             "kind": "manual_from_1964_not_verified_for_1963"},
            {"from": "1963_ON20_LAYOUT_UNVERIFIED", "to": tape["inventory_id"],
             "kind": "conditional_decoder_prerequisite_not_observation"},
        ],
        "manual_source_path": MANUAL,
        "page_audit_path": PAGES,
        "manual_publication_year": manual["published_year"],
        "wayback_capture_utc": capture["capture_utc"],
        "wayback_url": capture["replay_url"],
        "wayback_pdf_sha256": capture["sha256"],
        "wayback_pdf_bytes": capture["byte_length"],
        "page_visual_inspection": manual["page_visual_inspection"],
        "revision_on_page_12": manual["revision_beginning_page_12"],
        "validated_1963_layout_reference": None,
        "tape_source_id": tape["inventory_id"],
        "tape_sha256": tape["archive_sha256"],
        "target_matrix_context": tape["matrix_context_ref"],
        "candidate_parameter": tape["candidate_latent_parameter"],
        "required_before_activation": required,
        "decoded_station_day_matches": None,
        "numerical_wind_observations": 0,
        "independent_instrument_count": None,
        "active_physical_constraint": False,
    }


def build(root: Path = ROOT) -> dict:
    data = [json.loads((root / path).read_text(encoding="utf-8"))
            for path in (MANUAL, PAGES, TAPE)]
    return build_from_data(*data)


def encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    args = p.parse_args()
    data = encode(build())
    path = ROOT / OUTPUT
    if args.check:
        check(path.read_bytes() == data, "published ON20 bridge is stale")
    else:
        path.write_bytes(data)
    print("ON20_LINK", len(data), "bytes", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
