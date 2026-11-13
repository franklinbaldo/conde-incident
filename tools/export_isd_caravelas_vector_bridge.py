#!/usr/bin/env python3
"""Source-locked derived Caravelas wind vectors -> typed Lean -> inactive simulator input.

The three daily aggregates derive from one NOAA/ISD station window; they are
neither independent sensors nor measurements at Conde or at orbital altitude.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_isd_caravelas_vectors_1963 import check as check_vectors

ROOT = Path(__file__).resolve().parents[1]
VECTORS = "research/meteorology/isd_caravelas_vectors_1963.json"
EDGES = "research/constraints/isd_caravelas_vector_edges_1963.json"
SURFACE = "public/data/conde-isd-caravelas-bridge.json"
OUT = ROOT / "public/data/conde-isd-caravelas-vectors-bridge.json"
LEAN = ROOT / "formal/Conde1963/CaravelasCandidate.lean"
SOURCE = "MET-ISD-19631107-09-CARAVELAS-01"
VECTOR_ID = "MET-ISD-CARAVELAS-WIND-VECTORS-19631107-09"
LATENT = "wind_field_nov_1963_with_altitude_time_and_position"
BEGIN = "-- ABELHA_CARAVELAS_VECTOR_CANDIDATE_BEGIN"
END = "-- ABELHA_CARAVELAS_VECTOR_CANDIDATE_END"
DATES = ["1963-11-07", "1963-11-08", "1963-11-09"]
SOURCE_SHA = "c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05"
WINDOW_SHA = "c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("Caravelas vector bridge: " + message)


def build(vectors: dict, edges: dict, surface: dict, hashes: dict) -> dict:
    i = vectors["input"]
    require(vectors["schema"] == "conde.isd-caravelas-surface-wind-vectors/v1"
            and i["station"] == "834970-99999"
            and i["archive_gz_sha256"] == SOURCE_SHA
            and i["window_sha256"] == WINDOW_SHA
            and i["nominal_dates_utc"] == DATES
            and i["same_instrument_family_for_all_hours"] is True,
            "source hash, station, window, or independence drift")
    c = vectors["convention"]
    require(c["wind_direction"] == "meteorological FROM"
            and c["u_eastward"] == "-speed*sin(direction)"
            and c["v_northward"] == "-speed*cos(direction)"
            and c["zero_wind_bearing_not_physical"] is True
            and c["speed_weighted_resultant_is_not_instrument_uncertainty"] is True,
            "component convention or calibration drift")
    require(edges["id"] == VECTOR_ID
            and edges["source"] == SOURCE
            and edges["schema"] == "conde.meteorological-derived-vector/v1"
            and edges["dependencies"] ==
                ["MET-ISD-CARAVELAS-POSITION-DISCREPANCY-1963-01",
                 "NOAA_ISD_834970_99999_1963"]
            and [(e["from"], e["to"], e["type"]) for e in edges["edges"]] == [
                ("Caravelas_hourly_speed_and_direction", "Caravelas_surface_hourly_u_v", "SOURCE_DERIVED"),
                ("Caravelas_surface_hourly_u_v", "Caravelas_daily_vector_means", "AGGREGATION_NOT_INDEPENDENT_OBSERVATIONS"),
                ("Caravelas_daily_vector_means", "Conde_surface_wind", "TRANSFER_PENDING_CALIBRATION")],
            "source graph or dependency has been silently changed")
    require(edges["station_site_1963_authenticated"] is False
            and edges["instrument_sigma_m_s"] is None
            and edges["geographic_transfer_function"] is None
            and edges["active_conde_constraint"] is None
            and edges["status"] == "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION",
            "pending source graph promoted without calibration")
    require(surface["source_occurrence_id"] == SOURCE
            and surface["full_gzip_sha256"] == SOURCE_SHA
            and surface["excerpt_sha256"] == WINDOW_SHA
            and surface["observations_at_caravelas"] == 72
            and surface["station_id"] == {"usaf": "834970", "wban": "99999"}
            and surface["activation"] is False
            and surface["simulator_value"] is None
            and surface["spatial_transfer_to_conde"] is None
            and surface["terminal_epoch_528"] is None
            and surface["lean_module"] == "Conde1963.CaravelasCandidate"
            and surface["simulator_latent_parameter"] == LATENT,
            "previously authenticated Caravelas bridge changed")
    meaning = vectors["interpretation"]
    require(meaning["classification"] == "DERIVED_VECTORS_SAME_ARCHIVED_SURFACE_STATION"
            and meaning["status"] == edges["status"]
            and meaning["uncertainty_of_hourly_u_v"] is None
            and meaning["transfer_to_conde_calibrated"] is False
            and meaning["numeric_constraint_on_conde_or_trajectory"] is None,
            "uncertainty or numerical transfer falsely certified")
    require(list(vectors["days"]) == DATES, "lost or unexpected UTC date")
    days = []
    for day in DATES:
        v = vectors["days"][day]
        require(v["rows"] == 24 and 0 <= v["calm_rows"] <= 24
                and v["scalar_speed_mean_m_s"] >= 0
                and v["mean_vector_magnitude_m_s"] <= v["scalar_speed_mean_m_s"] + 0.002
                and -v["scalar_speed_mean_m_s"] <= v["mean_eastward_u_m_s"] <= v["scalar_speed_mean_m_s"]
                and -v["scalar_speed_mean_m_s"] <= v["mean_northward_v_m_s"] <= v["scalar_speed_mean_m_s"],
                "invalid vector aggregation/unit range")
        days.append({"date_utc": day, "station_hours": v["rows"],
                     "calm_hours": v["calm_rows"],
                     "u_millimetres_per_second": round(v["mean_eastward_u_m_s"] * 1000),
                     "v_millimetres_per_second": round(v["mean_northward_v_m_s"] * 1000),
                     "scalar_speed_millimetres_per_second": round(v["scalar_speed_mean_m_s"] * 1000)})
    require(sum(d["station_hours"] for d in days) == 72, "wrong archive coverage")
    return {
        "schema": "conde.isd-caravelas-derived-vector-scientific-bridge/v1",
        "id": "ABELHA-G39-CARAVELAS-DERIVED-VECTORS",
        "parents_sha256": hashes,
        "derived_occurrence_id": VECTOR_ID,
        "original_occurrence_id": SOURCE,
        "source_url": surface["source_url"],
        "source_family": surface["source_family"],
        "full_gzip_sha256": SOURCE_SHA,
        "window_sha256": WINDOW_SHA,
        "archive_rows": 72,
        "independent_instrument_families": 1,
        "independent_daily_measurements": False,
        "vector_convention": "meteorological FROM; eastward u=-s*sin(theta); northward v=-s*cos(theta)",
        "derived_days": days,
        "graph_edges": [
            {"from": SOURCE, "to": "Caravelas_hourly_speed_and_direction", "type": "RECORDED_BY"},
            *edges["edges"],
            {"from": "Caravelas_daily_vector_means", "to": "Conde1963.caravelasDailyVectors", "type": "LEAN_TYPED_DERIVATION"},
            {"from": "Conde1963.caravelasDailyVectors", "to": LATENT, "type": "PENDING_3D_TEMPORAL_SPATIAL_TRANSFER"},
        ],
        "lean_module": "Conde1963.CaravelasCandidate",
        "lean_declaration": "Conde1963.caravelasDailyVectors",
        "lean_status": "TYPED_DOCUMENTARY_DERIVATION_NOT_PHYSICAL_PROOF",
        "simulator_latent_parameter": LATENT,
        "simulator_value": None,
        "instrument_uncertainty": None,
        "station_position_epoch_1963": None,
        "spatial_transfer_to_conde": None,
        "vertical_transfer_to_528": None,
        "terminal_epoch_528": None,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
    }


def lean_block(data: dict) -> str:
    rows = data["derived_days"]
    records = []
    for d in rows:
        records.append(
            '  { dateUTC := "' + d["date_utc"] + '"\n'
            '    stationHours := ' + str(d["station_hours"]) + '\n'
            '    calmHours := ' + str(d["calm_hours"]) + '\n'
            '    uMillimetresPerSecond := ' + str(d["u_millimetres_per_second"]) + '\n'
            '    vMillimetresPerSecond := ' + str(d["v_millimetres_per_second"]) + '\n'
            '    scalarSpeedMillimetresPerSecond := ' + str(d["scalar_speed_millimetres_per_second"]) + ' }')
    return (BEGIN + '\n'
        '/-! Three derived daily means from ONE archived NOAA station, not three\n'
        'independent observations and not a measurement at Conde. The units\n'
        'are signed millimetres per second (not uncertainties). -/\n'
        'namespace Conde1963\n'
        'structure ArchivedDailyWindVector where\n'
        '  dateUTC : String\n  stationHours : Nat\n  calmHours : Nat\n'
        '  uMillimetresPerSecond : Int\n  vMillimetresPerSecond : Int\n'
        '  scalarSpeedMillimetresPerSecond : Nat\n'
        '  deriving Repr\n\n'
        'def caravelasDailyVectors : List ArchivedDailyWindVector :=\n[\n'
        + ',\n'.join(records) + '\n]\n'
        'end Conde1963\n' + END + '\n')


def render() -> tuple[bytes, str]:
    paths = [VECTORS, EDGES, SURFACE]
    src = {p: (ROOT / p).read_bytes() for p in paths}
    # Recovers all 72 pinned NOAA records to check that derived numbers are exact.
    check_vectors()
    data = build(*(json.loads(src[p]) for p in paths),
                 {p: hashlib.sha256(src[p]).hexdigest() for p in paths})
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode(), lean_block(data)


def main() -> None:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()
    raw, block = render()
    require(len(raw) < 20_000, "oversized export")
    lean = LEAN.read_text()
    if args.write:
        if BEGIN in lean:
            lean = lean.split(BEGIN)[0].rstrip() + "\n\n"
        OUT.write_bytes(raw)
        LEAN.write_text(lean.rstrip() + "\n\n" + block)
    else:
        require(OUT.exists() and OUT.read_bytes() == raw, "stale site export")
        require(lean.endswith(block) and len(LEAN.read_bytes()) <= 20_000,
                "Lean derived source is stale or oversized")
    print("CARAVELAS_VECTOR_BRIDGE_OK", len(raw))


if __name__ == "__main__":
    main()
