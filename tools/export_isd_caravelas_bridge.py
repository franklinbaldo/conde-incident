#!/usr/bin/env python3
"""Source-locked Caravelas ISD -> pending Conde atmosphere/Lean/simulator bridge.

One digital archive and 72 *rows*, not 72 independent instruments or Conde winds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_isd_caravelas_1963 import (
    SOURCE_SHA256, WINDOW_SHA256, check as check_isd,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = "research/meteorology/isd_caravelas_19631107_09.json"
GRAPH = "research/constraints/isd_caravelas_surface_1963.json"
NMC = "research/constraints/nmc_y20175_pending_bridge.json"
OBSERVABLE = "public/data/conde-observable-dependency-links.json"
OUT = ROOT / "public/data/conde-isd-caravelas-bridge.json"
SOURCE = "MET-ISD-19631107-09-CARAVELAS-01"
LATENT = "wind_field_nov_1963_with_altitude_time_and_position"


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("Caravelas bridge: " + reason)


def build(report: dict, graph: dict, nmc: dict, observables: dict,
          parent_hashes: dict) -> dict:
    source, station, quality = report["source"], report["station"], report["quality"]
    require(report["schema"] == "conde.isd-caravelas-hourly-1963/v1"
            and station["usaf"] == "834970" and station["wban"] == "99999"
            and station["position_epoch_in_1963_verified"] is None
            and source["full_gzip_sha256"] == SOURCE_SHA256
            and source["excerpt_sha256"] == WINDOW_SHA256
            and source["excerpt_rows"] == 72
            and report["observation_interval_utc"] ==
                ["1963-11-07T00:00:00Z", "1963-11-09T23:00:00Z"]
            and list(report["daily"]) == ["1963-11-07", "1963-11-08", "1963-11-09"]
            and [r["rows"] for r in report["daily"].values()] == [24, 24, 24],
            "source/window identity or coverage drift")
    require(quality["is_digital_qc_code_1"] is True
            and quality["qc_1_is_not_calibrated_instrument_error"] is True
            and quality["instrument_identity_1963"] is None
            and quality["measurement_uncertainty"] is None
            and quality["station_specific_transfer_uncertainty_to_conde"] is None
            and report["interpretation"]["numeric_constraint_on_conde"] is None,
            "digitization QC is not calibrated instrument uncertainty")
    require(graph["schema"] == "conde.historical-surface-pending-bridge/v1"
            and graph["id"] == SOURCE
            and graph["source"]["full_gzip_sha256"] == SOURCE_SHA256
            and graph["source"]["excerpt_sha256"] == WINDOW_SHA256
            and graph["source"]["url"] == source["url"]
            and graph["source"]["independence_family"] ==
                "NOAA_NCEI_ISD_DIGITIZED_SURFACE_OBSERVATIONS"
            and graph["observation"]["rows"] == 72
            and graph["observation"]["station_usaf"] == station["usaf"]
            and graph["observation"]["station_wban"] == station["wban"]
            and graph["observation"]["station_position_in_1963"] is None
            and graph["observation"]["measurement_method_in_1963"] is None
            and graph["status"] == "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION"
            and graph["active_conde_constraint"] is None
            and graph["uncertainty_m_s"] is None
            and graph["instrument_covariance"] is None,
            "custody, station or activation changed")
    expected_edges = [
        (SOURCE, "Caravelas_surface_wind_at_hour_t", "OBSERVES_DIGITIZED"),
        ("Caravelas_surface_wind_at_hour_t", "Conde_surface_wind_at_hour_t",
         "PENDING_SPATIAL_TRANSFER"),
        ("Conde_surface_wind_at_hour_t", "Conde_entry_drag_or_fall_location",
         "PENDING_TRAJECTORY_AND_ALTITUDE_MODEL"),
        (SOURCE, "C149-C151 Recife IGRA sounding family",
         "CONTEXT_NOT_INDEPENDENCE_CERTIFIED"),
    ]
    require([(e["from"], e["to"], e["type"]) for e in graph["edges"]] ==
            expected_edges, "missing, inverted or promoted dependency")
    require(nmc["schema"] == "conde.pending-nmc-wind-bridge/v1"
            and nmc["candidate_latent_parameter"] == LATENT
            and nmc["comparison_source"] == "NOAA_IGRA_RECIFE_1963"
            and nmc["physical_domain"] == "UNCHANGED_NO_ACTIVE_CONSTRAINT"
            and nmc["source_independence"] == "UNKNOWN_NO_DECODE"
            and nmc["numeric_observations_generated"] == 0,
            "contextual NCAR lineage is not an independent holdout")
    matches = [e for e in observables["edges"]
               if e["source_id"] == "NOAA_IGRA_RECIFE_1963"]
    require(len(matches) == 1, "Recife source ambiguity")
    context = matches[0]
    require(context["matrix_occurrence"] == nmc["matrix_context_ref"]
            and context["row_sha256"] == nmc["matrix_context_row_sha256"]
            and context["latent_parameter_id"] == LATENT
            and context["activation"] is False
            and context["simulator_value"] is None,
            "wrong C151 snapshot or false physical transfer")
    return {
        "schema": "conde.isd-caravelas-provenance-bridge/v1",
        "id": "ABELHA-G36-CARAVELAS-SURFACE-CONTEXT",
        "parents_sha256": parent_hashes,
        "source_occurrence_id": SOURCE,
        "source_url": source["url"],
        "source_family": graph["source"]["independence_family"],
        "full_gzip_sha256": SOURCE_SHA256,
        "excerpt_sha256": WINDOW_SHA256,
        "observations_at_caravelas": 72,
        "utc_interval": report["observation_interval_utc"],
        "station_id": {"usaf": station["usaf"], "wban": station["wban"]},
        "graph_edges": graph["edges"],
        "comparison_context": {
            "source_id": "NOAA_IGRA_RECIFE_1963",
            "matrix_ref": context["matrix_occurrence"],
            "row_sha256": context["row_sha256"],
            "relationship": "CONTEXT_ONLY_NO_INDEPENDENCE_CERTIFIED",
        },
        "lean_module": "Conde1963.CaravelasCandidate",
        "lean_status": "DOCUMENTARY_CANDIDATE_NOT_PHYSICAL_PROOF",
        "simulator_latent_parameter": LATENT,
        "simulator_value": None,
        "station_position_epoch_1963": None,
        "instrument_error_covariance": None,
        "spatial_transfer_to_conde": None,
        "terminal_epoch_528": None,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "independent_physical_source_count": None,
    }


def render() -> bytes:
    paths = [REPORT, GRAPH, NMC, OBSERVABLE]
    parents = {p: (ROOT / p).read_bytes() for p in paths}
    # Re-parse all 72 archived raw ISD rows, not just the derived JSON.
    check_isd()
    data = build(*(json.loads(parents[p]) for p in paths),
                 {p: hashlib.sha256(parents[p]).hexdigest() for p in paths})
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = render()
    if len(raw) > 20_000:
        raise ValueError("Caravelas bridge exceeds 20 KB")
    if args.write:
        OUT.write_bytes(raw)
    elif not OUT.exists() or OUT.read_bytes() != raw:
        raise ValueError("Caravelas bridge export is stale")
    print("CARAVELAS_BRIDGE_OK", len(raw))


if __name__ == "__main__":
    main()
