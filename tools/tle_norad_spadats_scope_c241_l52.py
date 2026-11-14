#!/usr/bin/env python3
"""C241-L52: verify 1963 NORAD camera network history without inventing NORAD 528 tracking."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess

LEDGER = Path(__file__).resolve().parents[1] / "research/tle_custody/norad_1963_spadats_operational_C241-L52.json"
EXPECTED_SOURCE = {
  "url": "https://documents.theblackvault.com/documents/afhistory/norad/%28U%29%201963%20NORAD%20CONAD%20History%20Jul-Dec.pdf",
  "institution": "Headquarters NORAD/CONAD",
  "title": "NORAD/CONAD Historical Summary, July-December 1963",
  "report_date": "1964-05-01",
  "coverage": "1963-07 through 1963-12",
  "holder": "The Black Vault declassified-scan mirror; official NORAD history inventory lists the title",
  "bytes": 7111330,
  "sha256": "eb8682425a393b016642165a9c00b6be8868a27954ddd0e55c40c1e14da425b4",
  "pdf_pages": 122,
  "read_method": "Scanned pages visually inspected, PDF indexes 70/71; hash is of the exact mirrored binary downloaded 2026-11-14"
}
EXPECTED_EVENTS = [
  {
    "id": "JCS_1963_07_17",
    "date": "1963-07-17",
    "pdf_page_index": 70,
    "printed_page": 55,
    "finding": "JCS advised NORAD that the three SAO-operated cameras would not be available under the proposed transfer; requested plan for four USAF-owned cameras plus Cold Lake.",
    "kind": "administrative-plan-decision"
  },
  {
    "id": "JCS_NASA_DATA_REQUEST",
    "date": "1963-07-17",
    "pdf_page_index": 70,
    "printed_page": 55,
    "finding": "JCS requested every effort to have NASA provide Baker-Nunn data to SPADATS; this documents a request, not receipt of any named measurement.",
    "kind": "data-sharing-request"
  },
  {
    "id": "NORAD_REPLAN_1963_09",
    "date": "1963-09",
    "pdf_page_index": 71,
    "printed_page": 56,
    "finding": "NORAD described a revised mutually supporting USAF/RCAF camera subsystem, with SAO camera contributions still to be determined before recommendations.",
    "kind": "planned-system-integration"
  },
  {
    "id": "NAVY_CALIBRATION_1963_10",
    "date": "1963-10",
    "pdf_page_index": 71,
    "printed_page": 56,
    "finding": "NORAD learned that the Navy no longer required Baker-Nunn cameras for SPASUR calibration and JCS approved no further action on this calibration request.",
    "kind": "calibration-plan-change"
  },
  {
    "id": "COLD_LAKE_COMMS_1963_12",
    "date": "1963-12",
    "pdf_page_index": 71,
    "printed_page": 56,
    "finding": "The report states secure communication circuits scheduled for 15 November at Cold Lake had still not been installed by the end of 1963; operational control did not prove direct real-time data feed.",
    "kind": "communications-availability-context"
  }
]
EXPECTED_SCOPE = {
  "instrumental_observation_527": None,
  "instrumental_observation_528": None,
  "instrumental_observation_529": None,
  "station_of_528": None,
  "epoch_528_utc": None,
  "frame_528": None,
  "sigma_528": None,
  "actual_1963_sao_to_spadats_528_transfer": None,
  "independent_instrumental_family_count": None,
  "physical_piece_528": None,
  "decay_hour_528": None,
  "impact_location_528": None,
  "physical_constraint_active": False,
  "graph_state": "CONTEXT_ONLY_NOT_ACTIVATED",
  "orbit_parameters": "THETA_UNCHANGED"
}
EXPECTED_NEXT = "Recover actual 1963 tracking log with NORAD 528/1963-003B, station, UTC timestamp, observable, reference frame, calibration and error; audit actual NSA/NASA/SAO-to-SPADATS data transfers."

def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON field: " + key)
        obj[key] = value
    return obj

def load(path=LEDGER):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

def audit(d):
    if set(d) != {"schema", "evidence_id", "source_kind", "source", "events", "scope", "next_test"}:
        raise ValueError("unexpected top-level fields")
    if d["schema"] != "c241-l52-norad-spadats-operational/v1" or d["evidence_id"] != "C241-L52":
        raise ValueError("provenance identity changed")
    if d["source_kind"] != "CONTEMPORARY_INSTITUTIONAL_SUMMARY_NOT_RAW_TRACKING":
        raise ValueError("an institutional narrative is not raw sensor data")
    if d["source"] != EXPECTED_SOURCE:
        raise ValueError("original source custody altered")
    if d["events"] != EXPECTED_EVENTS:
        raise ValueError("camera plan dates or interpretations altered")
    if d["scope"] != EXPECTED_SCOPE:
        raise ValueError("unsupported instrument, independence, timing or physics inference")
    if d["next_test"] != EXPECTED_NEXT:
        raise ValueError("evidence requirement altered")
    return True

def verify_pdf(data, payload):
    src = data["source"]
    if not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-2048:]:
        raise ValueError("invalid or truncated PDF")
    if len(payload) != src["bytes"]:
        raise ValueError("PDF byte size mismatch")
    if hashlib.sha256(payload).hexdigest() != src["sha256"]:
        raise ValueError("PDF SHA-256 mismatch")
    from pypdf import PdfReader
    if len(PdfReader(io.BytesIO(payload)).pages) != src["pdf_pages"]:
        raise ValueError("PDF page count mismatch")
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-file", type=Path)
    p.add_argument("--verify-remote", action="store_true")
    args = p.parse_args()
    if args.source_file is not None and args.verify_remote:
        p.error("select --source-file or --verify-remote, not both")
    d = load()
    audit(d)
    if args.source_file is not None:
        verify_pdf(d, args.source_file.read_bytes())
    elif args.verify_remote:
        payload = subprocess.run(
            ["curl", "--fail", "--location", "--silent", "--show-error",
             "--retry", "2", "--connect-timeout", "12", "--max-time", "120", d["source"]["url"]],
            check=True, stdout=subprocess.PIPE,
        ).stdout
        verify_pdf(d, payload)
    print("C241-L52: PASS; contemporary camera-network context only; NORAD 528 measurements remain unrecovered")

if __name__ == "__main__":
    main()
