#!/usr/bin/env python3
"""Connect original 1963 UN registrations to a *pending* orbital-status model.

The registration is governmental catalogue reporting, not a station observation.
Its administrative cutoffs are not sensor or decay epochs. The custody ledger
belongs to Tartaruga; no authoritative source row is modified here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UN = "research/tle_custody/un_1963_registration_C241-L33.json"
NASA = "research/tle_custody/nasa_ssr_dec1977_528_identity_C241-L32.json"
PRECISION = "research/constraints/nasa_528_decay_precision_C197_20261113.json"
OUT = ROOT / "public/data/conde-un-1963-status-bridge.json"
# Exact facsimile digests and lengths from Tartaruga's visually audited ledger.
PDF_ANCHORS = (
    ("30", "fbee0e928a2d81e62c97c102eef70d4f4931dd500372a4bf735bd8891c6188b8", 189499, "2400Z 31 JANUARY 1963", "1963-03-13"),
    ("53", "1439a1c1ec49b3922bb7f86e4b868b8ab8a1c9e34e34803b78c1aea2c541c84c", 850470, "2400Z 15 NOVEMBER 1963", "1963-12-31"),
    ("54", "8a67ca12769e935877429125a6d446f4e04189698d0e356536f588fef507acf4", 377974, "2400Z 31 OCTOBER 1963", "1963-12-31"),
    ("55", "2f69e814a277e3a5fae8b27db8f7566f39a401a8089f1287dbea65d47b94cbcd", 286501, "2400Z 15 OCTOBER 1963", "1963-12-31"),
)
EXPECTED_ROWS = (
    ("1963-3-A", 527, "94.7", "81.97", "518.6", "479.5"),
    ("1963-3-B", 528, "94.5", "81.97", "505.5", "476.4"),
    ("1963-3-C", 529, "94.7", "81.97", "525.5", "476.4"),
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("UN1963 scientific bridge: " + reason)


def build(un: dict, nasa: dict, precision: dict, hashes: dict) -> dict:
    require(un["schema"] == "conde.c241-l33-un-1963-registration/v1"
            and un["id"] == "C241-L33" and len(un["docs"]) == 4,
            "wrong UN ledger identity or cardinality")
    docs = un["docs"]
    for d, (num, sha, size, cutoff, day) in zip(docs, PDF_ANCHORS):
        require(d["number"] == num and d["url"] == f"https://www.unoosa.org/documents/pdf/inf{int(num):03d}E.pdf"
                and d["sha256"] == sha and d["bytes"] == size
                and d["report_cutoff_printed"] == cutoff
                and d["document_day"] == day and d["pdf_pages"] == 2
                and d["relevant_pdf_page_index"] == 1
                and d["visual_check"] == "MANUAL_IMAGE_INSPECTION_2026-11-13",
                "original facsimile, cutoff, date or inspected page altered")
    require(docs[0]["kind"] == "JAN31_FULL_NEW_REGISTRATION"
            and docs[1]["kind"] == "NOV15_INCREMENTS_AND_DELETIONS"
            and docs[2]["kind"] == "OCT31_INCREMENT_ONLY_CONTROL"
            and docs[3]["kind"] == "OCT15_INCREMENT_ONLY_CONTROL",
            "full registrations and incremental deletions are different")
    rows = docs[0]["printed_rows"]
    require(len(rows) == 3, "registration must have three target rows")
    for r, (designator, norad, period, inclination, apogee, perigee) in zip(rows, EXPECTED_ROWS):
        require((r["printed_designator"], r["norad_from_nasa_1977"],
                 r["nodal_period_min_printed"], r["inclination_deg_printed"],
                 r["apogee_km_printed"], r["perigee_km_printed"]) ==
                (designator, norad, period, inclination, apogee, perigee)
                and r["launch_day"] == "1963-01-16"
                and r["launch_vehicle"] == "THOR AGENA",
                "published element or retrospective object mapping changed")
    require(docs[1]["printed_no_longer_in_orbit"] == ["1963-3B", "1963-35A"]
            and docs[2]["printed_no_longer_in_orbit"] == ["1962 Omega 1"]
            and docs[3]["printed_no_longer_in_orbit"] == ["1963-37A"]
            and docs[2]["contains_1963_3B_in_deletions"] is False
            and docs[3]["contains_1963_3B_in_deletions"] is False,
            "status or incremental controls modified")
    require(un["source_role"] == "ORIGINAL_US_GOVERNMENT_REGISTRATION_TO_UN_NOT_INDEPENDENT_SENSOR",
            "UN reporting is not a distinct radar")
    inter = un["interpretation"]
    require(inter["identity_crosswalk_source"] == NASA
            and inter["nasa_source_occurrence"] == "C197#1"
            and inter["printed_event_date_nasa_1963"] == "1963-11-08"
            and inter["un_cutoff_is_sensor_epoch"] is False
            and inter["un_cutoff_is_verified_decay_time"] is False
            and inter["conditional_physical_interval_activated"] is False
            and inter["controls_54_55_constrain_survival"] is False
            and inter["independent_sensor_observations_added"] == 0
            and inter["physical_constraints_activated"] == 0
            and inter["lean_activated"] is False
            and all(inter[k] is None for k in (
                "historical_sensor_528", "observation_epoch_528",
                "state_fit_covariance_528", "decay_time_uncertainty_528",
                "raw_line1_line2_528")), "administrative assertion was promoted to physics")
    graph = un["graph_extension"]
    require(graph["parent"] == PRECISION
            and NASA in graph["requires"]
            and len(graph["edges"]) == 6
            and graph["physical_domain_reduced"] is False
            and graph["simulation_run"] is False,
            "custodian dependency graph changed")
    require(nasa["record_id"] == "C241-L32"
            and nasa["source"]["pdf_sha256"] ==
            "c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8"
            and nasa["row"]["catalog_number_printed"] == 528
            and nasa["row"]["international_designator_printed"] == "1963 003B"
            and nasa["row"]["identity_match"] == "DIRECT_VISUAL_VERIFIED"
            and nasa["row"]["source_528_sensor_id"] is None
            and [r["catalog_number_printed"] for r in nasa["control_rows"]] == [527, 529],
            "1977 primary retrospective crosswalk no longer matches")
    require(precision["id"] == "C197-PRECISION-20261113"
            and precision["source"]["occurrence"] == "C197#1"
            and precision["source"]["reported_decay_day"] == "1963-11-08"
            and precision["source"]["raw_sensor_observation"] is False
            and precision["conditional_predicate"]["active"] is False
            and precision["unknowns"]["physical_terminal_utc"] is None,
            "NASA catalog day is not a calibrated event")
    # This builds *model dependencies*, never a fabricated observation epoch.
    measurements = [{
        "source_id": "C241-L33:UN-INF30", "source_pdf_sha256": docs[0]["sha256"],
        "printed_designator": row["printed_designator"],
        "norad_via_retrospective_c241_l32": row["norad_from_nasa_1977"],
        "report_cutoff_printed": docs[0]["report_cutoff_printed"],
        "publication_day": docs[0]["document_day"], "instrument_epoch_utc": None,
        "source_kind": "GOVERNMENT_REGISTRATION_COMPILED_ELEMENTS",
        "reported_elements": {"nodal_period_min": row["nodal_period_min_printed"],
                              "inclination_deg": row["inclination_deg_printed"],
                              "apogee_km": row["apogee_km_printed"],
                              "perigee_km": row["perigee_km_printed"]},
        "simulator_observable": "catalogued_period_inclination_apogee_perigee",
        "pending": ["source_orbit_fit", "instrument_epoch", "reference_frame",
                    "catalogue_rounding_model", "instrument_covariance"],
        "activation": False,
    } for row in rows]
    connections = [dict(edge) for edge in graph["edges"]]
    connections.extend([
        {"from": "UN-INF30-JAN31", "to": "latent_1963_528_state_epoch",
         "type": "COMPILED_ORBITAL_ELEMENTS_REQUIRE_EPOCH_AND_FIT", "activation": False},
        {"from": "UN-INF53-NOV15", "to": "latent_528_true_terminal_time",
         "type": "REPORTED_STATUS_REQUIRES_CATALOG_REPORTING_MODEL", "activation": False},
        {"from": "C197#1", "to": "latent_528_true_terminal_time",
         "type": "REPORTED_NASA_DAY_REQUIRES_DECAY_DATE_ERROR_MODEL", "activation": False},
        {"from": "latent_528_true_terminal_time", "to": "simulator_terminal_event_528",
         "type": "FORWARD_MODEL_NOT_CALIBRATED", "activation": False},
    ])
    return {
        "schema": "conde.un-1963-status-scientific-bridge/v1",
        "id": "ABELHA-UN-C241-L33-01", "parent_sha256": hashes,
        "custodial_occurrence": "C241-L33",
        "matrix_occurrence": "C197#1",
        "source_documents": [{"id": f"UN-INF{d['number']}", "url": d["url"],
                              "sha256": d["sha256"], "bytes": d["bytes"],
                              "pdf_page_index": d["relevant_pdf_page_index"],
                              "report_cutoff_printed": d["report_cutoff_printed"],
                              "publication_day": d["document_day"],
                              "document_kind": d["kind"]} for d in docs],
        "catalogued_elements": measurements,
        "documentary_status_528": {
            "original_designator": "1963-3B", "norad_from_c241_l32": 528,
            "reported_not_in_orbit_by": docs[1]["report_cutoff_printed"],
            "report_publication_day": docs[1]["document_day"],
            "nasa_catalogued_decay_day": "1963-11-08",
            "reporting_independence": "UNKNOWN_POSSIBLY_SHARED_NASA_NORAD_UPSTREAM",
            "actual_terminal_time_utc": None, "actual_event_location": None,
            "sensor_epoch_utc": None, "sensor_covariance": None,
            "status": "DOCUMENTARY_REPORT_PENDING_CALIBRATION",
        },
        "control_absence_is_negative_observation": False,
        "source_dependency_graph": connections,
        "lean_module": "Conde1963.UnRegistrationCandidate",
        "lean_definition": "Conde1963.un1963RegistrationElements",
        "lean_status": "TYPED_DOCUMENTARY_CANDIDATE_NO_PHYSICAL_THEOREM",
        "simulator_latent_parameters": [
            {"name": "state_epoch_528_utc", "value": None, "active": False},
            {"name": "true_terminal_time_528_utc", "value": None, "active": False},
            {"name": "reporting_date_error_528_seconds", "value": None, "active": False},
            {"name": "fit_covariance_528", "value": None, "active": False},
        ],
        "independent_instrument_observations_added": 0,
        "activation": False, "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Locate original 528 station track and the rule mapping SPADATS decay events to UN cutoffs",
    }


def render() -> bytes:
    files = (UN, NASA, PRECISION)
    raw = [(ROOT / file).read_bytes() for file in files]
    hashes = {file: hashlib.sha256(data).hexdigest() for file, data in zip(files, raw)}
    return (json.dumps(build(*(json.loads(data) for data in raw), hashes),
                       indent=2, ensure_ascii=False) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = render()
    require(len(data) <= 20_000, "published JSON exceeds 20 KB")
    if args.write:
        OUT.write_bytes(data)
    else:
        require(OUT.read_bytes() == data, "published output stale")
    print("UN_1963_STATUS_BRIDGE_OK", len(data))


if __name__ == "__main__":
    main()
