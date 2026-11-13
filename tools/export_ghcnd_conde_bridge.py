#!/usr/bin/env python3
"""Source-locked GHCN-Daily -> documentary rain candidate -> Lean/latent bridge.

The 11 archived station records are not 11 independent instrument families.
Daily PRCP is not a wind or reentry observation at the incident location.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_ghcnd_conde_rain_1963 import IDS, SHA

ROOT = Path(__file__).resolve().parents[1]
REPORT = "research/meteorology/ghcnd_conde_precip_19631107_09.json"
GRAPH = "research/constraints/ghcnd_conde_precip_19631107_09_edges.json"
OBSERVABLE = "public/data/conde-observable-dependency-links.json"
CARAVELAS = "public/data/conde-isd-caravelas-bridge.json"
OUT = ROOT / "public/data/conde-ghcnd-conde-bridge.json"
SOURCE = "MET-GHCND-CONDE-19631107-09-01"
STATION = "BR048346820"
CONTROL = "BR048340980"
DAYS = ("1963-11-07", "1963-11-08", "1963-11-09")
LATENT = "precipitation_at_incident_site_and_epoch_unknown"
# Canonical semantic fingerprint of the upstream report reconstructed from the
# 11 SHA-pinned .dly files plus ghcnd-stations.txt/inventory/readme.  In
# particular, a .dly digest DOES NOT authenticate station coordinates or
# the station catalogue name. Any legitimate update requires re-running the
# original-source audit and explicitly reviewing this pin.
PINNED_REPORT_CANONICAL_SHA256 = (
    "d3f804349c6753053ec3468a8694e9f097501eacc692e7763b1d6346595da714"
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("GHCNd bridge: " + message)


def build(report: dict, graph: dict, obs: dict, caravelas: dict,
          parent_hashes: dict) -> dict:
    canonical_report = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    require(hashlib.sha256(canonical_report).hexdigest() ==
            PINNED_REPORT_CANONICAL_SHA256,
            "original-source audited GHCNd report differs from approved snapshot")
    require(report["schema"] == "conde.ghcnd-conde-precipitation-1963/v1"
            and report["id"] == SOURCE
            and report["status"] == "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION"
            and report["days"] == list(DAYS)
            and report["archival_family"] == "NOAA/NCEI GHCN-Daily; NOT NOAA/ISD Caravelas"
            and report["source_flag_I_meaning"].startswith("international collection")
            and report["full_source_sha256"] ==
                {k: SHA[k] for k in ("readme.txt", "ghcnd-stations.txt", "ghcnd-inventory.txt")}
            and report["source_document_urls"] ==
                ["https://www.ncei.noaa.gov/pub/data/ghcn/daily/" + p
                 for p in ("readme.txt", "ghcnd-stations.txt", "ghcnd-inventory.txt")],
            "NOAA report, source metadata or archival dates drift")
    require(report["reference"]["kind"] ==
            "modern IBGE 2022 municipality bbox midpoint, not 1963 incident site"
            and report["not_proved"] == {
                "observation_time_within_day": None,
                "historical_instrument_and_collecting_agency": None,
                "1963_station_coordinates_verified": None,
                "station_observation_independence": None,
                "rainfall_at_incident_site": None,
                "contemporary_wind_in_conde": None,
                "atmospheric_transfer_to_orbital_object": None,
                "calibrated_uncertainty": None,
                "active_fall_constraint": None,
            }, "unverified calibration or incident-site rainfall promoted")
    stations = report["stations"]
    by_id = {st["id"]: st for st in stations}
    require(len(stations) == len(IDS) == len(by_id)
            and set(by_id) == set(IDS), "station ID set not source-locked")
    for sid, st in by_id.items():
        require(st["whole_file_sha256"] == SHA[sid + ".dly"]
                and st["archive_url"] ==
                    "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/" + sid + ".dly"
                and len(st["coordinate_lat_lon"]) == 2
                and len(st["daily"]) == 3
                and [r["date"] for r in st["daily"]] == list(DAYS)
                and all(r["source_flag"] == "I"
                        and r["quality_flag"] is None
                        and r["measurement_flag"] is None
                        and len(r["raw_eight_chars"]) == 8
                        and int(r["raw_eight_chars"][:5]) >= 0
                        and int(r["raw_eight_chars"][:5]) / 10 == r["precipitation_mm"]
                        for r in st["daily"]), "pinned station, raw PRCP or flags drift")
    require([r["precipitation_mm"] for r in by_id[STATION]["daily"]] == [0, 3.5, 0]
            and [r["precipitation_mm"] for r in by_id[CONTROL]["daily"]] == [0, 2.4, 0]
            and all(st["daily"][0]["precipitation_mm"] == 0
                    and st["daily"][2]["precipitation_mm"] == 0 for st in stations)
            and all(st["daily"][1]["precipitation_mm"] == 0
                    for sid, st in by_id.items() if sid not in (STATION, CONTROL)),
            "rainfall cells unexpectedly changed")
    require(by_id[STATION]["station"] == "CONDE"
            and by_id[CONTROL]["station"] == "INDIAROBA", "station label swap")
    require(graph["schema"] == "conde.ghcnd-conde-precipitation-edges/v1"
            and graph["id"] == SOURCE.replace("-01", "-EDGES-01")
            and graph["source"] == SOURCE
            and graph["status"] == report["status"]
            and graph["dependencies"] ==
                ["MET-ISD-BAHIA-1963-ARCHIVE-COVERAGE-01",
                 "MET-ISD-19631107-09-CARAVELAS-01",
                 "C149", "C150", "C151"]
            and graph["observation_time_within_day"] is None
            and graph["instrument_error_model"] is None
            and graph["station_coordinates_verified_1963"] is None
            and graph["calibrated_physical_constraint"] is None,
            "dependency/activation graph changed")
    expected = [
        ("GHCNd_11_original_station_files", "daily_PRCP_7_to_9_nov_1963",
         "ARCHIVED_DAILY_PRECIPITATION_NOT_HOURLY"),
        ("GHCNd_Conde_08Nov_3point5mm", "rain_around_Conde_1963",
         "OBSERVED_IN_ARCHIVE_STATION_DATE_ONLY"),
        ("GHCNd_SFLAG_I", "historic_brazilian_station_origin",
         "PENDING_INSTRUMENT_AND_COLLECTION_LINEAGE"),
        ("GHCNd_Conde_daily_PRCP", "meteorology_at_incident_epoch",
         "PENDING_DAILY_CLOCK_AND_LOCATION_ALIGNMENT"),
        ("GHCNd_Conde_daily_PRCP", "wind_drag_or_fall_of_NORAD_527_528_529",
         "NO_TRANSFER_CALIBRATED"),
        ("GHCNd_archival_family", "NOAA_ISD_Caravelas_archival_family",
         "DISTINCT_PRODUCTS_SOURCE_INDEPENDENCE_UNPROVED"),
    ]
    require([(e["from"], e["to"], e["type"]) for e in graph["edges"]] == expected,
            "graph edge omission or unsupported causal inference")
    require(caravelas["source_occurrence_id"] ==
            "MET-ISD-19631107-09-CARAVELAS-01"
            and caravelas["activation"] is False
            and caravelas["simulator_value"] is None
            and caravelas["physical_domain_effect"] == "THETA_UNCHANGED",
            "ISD comparison is not a rainfall measurement or active input")
    refs = [e for e in obs["edges"] if e["source_id"] == "NOAA_IGRA_RECIFE_1963"]
    require(len(refs) == 1
            and refs[0]["matrix_occurrence"].endswith(":C151#1")
            and refs[0]["activation"] is False
            and refs[0]["simulator_value"] is None, "C151 context misidentified")
    return {
        "schema": "conde.ghcnd-conde-scientific-bridge/v1",
        "id": "ABELHA-GHCND-CONDE-DAILY-PRCP-BRIDGE-01",
        "parent_sha256": parent_hashes,
        "source_occurrence_id": SOURCE,
        "source_family": "NOAA_NCEI_GHCN_DAILY",
        "station_source_ids": list(IDS),
        "source_files_sha256": {sid: SHA[sid + ".dly"] for sid in IDS},
        "observations_count": 33,
        "archival_day_labels_not_instant_utc": list(DAYS),
        "station": {
            "id": STATION, "catalogue_name": "CONDE",
            "coordinate_lat_lon_catalogue_not_1963_verified": by_id[STATION]["coordinate_lat_lon"],
            "daily_precipitation_tenths_mm": [0, 35, 0],
            "raw_cells": [d["raw_eight_chars"] for d in by_id[STATION]["daily"]],
        },
        "comparison_station": {
            "id": CONTROL, "catalogue_name": "INDIAROBA",
            "daily_precipitation_tenths_mm": [0, 24, 0],
        },
        "source_flag": "I",
        "source_flag_is_instrument_identity": False,
        "source_dependency_graph": graph["edges"],
        "matrix_context": {
            "occurrence": refs[0]["matrix_occurrence"],
            "row_sha256": refs[0]["row_sha256"],
            "relation": "CONTEXT_ONLY_NO_INDEPENDENCE_CERTIFIED",
        },
        "comparison_isd": caravelas["source_occurrence_id"],
        "comparison_independence": "UNKNOWN_DISTINCT_ARCHIVAL_PRODUCTS",
        "lean_module": "Conde1963.GhcndCondeCandidate",
        "lean_status": "DOCUMENTARY_CANDIDATE_NOT_PHYSICAL_PROOF",
        "observed_variable": "station_daily_precipitation_tenths_mm",
        "simulator_latent_parameter": LATENT,
        "simulator_value": None,
        "station_coordinates_verified_1963": None,
        "rainfall_at_incident_site": None,
        "observation_time_within_day": None,
        "instrument_error_covariance": None,
        "terminal_epoch_528": None,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "independent_instruments_count": None,
    }


def render() -> bytes:
    paths = (REPORT, GRAPH, OBSERVABLE, CARAVELAS)
    raw = [(ROOT / p).read_bytes() for p in paths]
    payload = build(*(json.loads(s) for s in raw),
                    {p: hashlib.sha256(data).hexdigest()
                     for p, data in zip(paths, raw)})
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = render()
    require(len(data) <= 20_000, "output exceeds 20 KB")
    if args.write:
        OUT.write_bytes(data)
    else:
        require(OUT.is_file() and OUT.read_bytes() == data, "stale published bridge")
    print("GHCND_CONDE_BRIDGE_OK", len(data))


if __name__ == "__main__":
    main()
