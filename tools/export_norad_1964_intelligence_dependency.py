#!/usr/bin/env python3
"""Source-locked NORAD 1964 apparent de-orbit context, not calibration for 1963."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L65 = "research/tle_custody/norad_wir_cosmos34_1964_C241-L65.json"
L65_SHA = "79744efefc2b84320102c998786f316f70a30d0d56bd1e38575b38d25fff17c7"
L64 = "public/data/conde-ssr-308-l64-dependency-bridge.json"
L64_SHA = "f897870189802c840e7423b106d49e829dbc1934efd3b0ac1e0ad60bfec7a04b"
PDF_SHA = "2063f4f8d9082c55990dd4be91b8eb096333143230b6f726639fc58bef7251c5"
OUTPUT = ROOT / "public/data/conde-norad-1964-apparent-deorbit-dependency.json"


def require(ok, reason):
    if not ok:
        raise ValueError("C241-L65 scientific bridge: " + reason)


def unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, "duplicate JSON key: " + k)
        result[k] = v
    return result


def source(root, path, sha):
    data = (root / path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == sha, "source SHA drift: " + path)
    return json.loads(data, object_pairs_hook=unique_pairs)


def load(root=ROOT):
    return source(root, L65, L65_SHA), source(root, L64, L64_SHA)


def edge(src, dst, relation):
    return {"source": src, "target": dst, "relation": relation,
            "documentary_only": True, "activation": False}


def build(l65, l64):
    require(l65["id"] == "C241-L65" and
            l65["kind"] == "NORAD_1964_INTELLIGENCE_DEORBIT_WINDOW_CONTEXT_ONLY",
            "occurrence identity")
    s, r, i = l65["source"], l65["report"], l65["interpretation"]
    require(s["publisher"] == "North American Air Defense Command (NORAD)" and
            s["publication"] == "Weekly Intelligence Review 29/64" and
            s["published_on"] == "1964-07-17" and
            s["source_class"] == "ORIGINAL_NORAD_REPORT_RELEASED_BY_NARA_ISCAP" and
            s["url"] == "https://www.archives.gov/files/declassification/iscap/pdf/2009-068-doc35.pdf" and
            s["pdf_sha256"] == PDF_SHA and s["pdf_bytes"] == 30133149 and
            s["pdf_pages"] == 10 and s["pdf_page_one_indexed"] == 4 and
            s["printed_page"] == 6, "NORAD original and custody")
    require(r["object_name_as_printed"] == "Cosmos 34" and
            r["event_date"] == "1964-07-09" and
            r["event_printed"] == "apparently de-orbited sometime between 0931-0936Z, 9 July" and
            r["start_as_printed"] == "0931Z" and
            r["end_as_printed"] == "0936Z" and
            type(r["printed_interval_minutes"]) is int and
            r["printed_interval_minutes"] == 5 and
            r["qualifier"] == "apparently" and
            r["described_revolution"] == 127, "printed 1964 narrative")
    for k in ("sensor", "instrument_observation_id", "observation_epoch",
              "estimation_method", "time_uncertainty_sigma_seconds"):
        require(r[k] is None, "source lacks measured " + k)
    require(i["evidence_type"] == "NORAD_INTELLIGENCE_ASSESSMENT_NOT_SENSOR_LOG" and
            i["event_type"] == "APPARENT_DEORBIT_NOT_NATURAL_DECAY_CALIBRATION" and
            i["same_event_as_1963_norad_308"] is False and
            i["same_event_as_1963_norad_528"] is False and
            i["permits_five_minute_sigma_for_528"] is False and
            i["permits_utc_terminal_point_for_528"] is False and
            i["original_independent_measurements_528"] == 0 and
            i["activated_orbital_constraints_528"] == 0, "narrative cannot calibrate 528")
    require(l64["id"] == "ABELHA-C241-L64-R59-308-CALENDAR-RANGE" and
            l64["sources"][0]["id"] == "C241-L64" and
            l64["observation"]["id"] == "C241-L64:OMEGA1" and
            l64["observation"]["secondary_norad_id"] == 308 and
            l64["observation"]["nasa_printed_norad_id"] is None and
            l64["observation"]["terminal_event_utc"] is None and
            l64["observation"]["terminal_sigma_seconds"] is None and
            l64["activation"] is False and
            l64["physical_domain_effect"] == "THETA_UNCHANGED" and
            l64["new_independent_instrumental_observations"] == 0,
            "1963 control is only a secondary crosswalk with no terminal clock")
    p = {
        "schema": "conde.c241-l65-intelligence-clock-dependency/v1",
        "id": "ABELHA-C241-L65-R59-NORAD-1964-CLOCK-CONTEXT",
        "sources": [
            {"id": "C241-L65", "path": L65, "sha256": L65_SHA,
             "pdf_sha256": PDF_SHA, "pdf_page": 4, "printed_page": 6,
             "published_on": "1964-07-17", "grade": "NORAD_PRIMARY_INTELLIGENCE_ASSESSMENT"},
            {"id": "ABELHA-C241-L64-R59-308-CALENDAR-RANGE",
             "path": L64, "sha256": L64_SHA,
             "grade": "SECONDARY_308_IDENTITY_NOT_INSTRUMENTAL_UTC"},
        ],
        "records": [
            {"id": "C241-L65:COSMOS34", "printed_object": "Cosmos 34",
             "printed_event_day": "1964-07-09",
             "printed_z_window": ["0931Z", "0936Z"],
             "printed_nominal_width_minutes": 5, "qualifier": "apparently",
             "event_kind": "INTELLIGENCE_APPARENT_DEORBIT",
             "instrumental_terminal_measurement": False,
             "station": None, "sensor": None, "instrument_observation_id": None,
             "estimation_method": None, "calibrated_sigma_seconds": None,
             "independent_instrumental_lineages": None, "activation": False},
            {"id": "C241-L64:OMEGA1", "printed_event_range":
             ["1963-10-29", "1963-10-30"], "secondary_norad_id": 308,
             "primary_norad_identity": None, "terminal_utc": None,
             "calibrated_sigma_seconds": None, "activation": False},
        ],
        "graph": [
            edge("DOC:NARA-ISCAP-2009-068-35", "PDF:NORAD-WIR-29-64-P6", "PRESERVES_FACSIMILE"),
            edge("PDF:NORAD-WIR-29-64-P6", "DOC:C241-L65", "PRINTED_PAGE_AND_HASH"),
            edge("DOC:C241-L65", "ROW:COSMOS34-1964", "PRINTS_1964_Z_WINDOW"),
            edge("ROW:COSMOS34-1964", "H:1964_APPARENT_DEORBIT", "QUALIFIED_INTELLIGENCE_ASSESSMENT"),
            edge("H:1964_APPARENT_DEORBIT", "LATENT:COSMOS34:terminal_sensor", "NO_SENSOR_LOG_IDENTIFIED"),
            edge("H:1964_APPARENT_DEORBIT", "LATENT:COSMOS34:clock_error_sigma", "NO_STATISTICAL_ERROR_IN_REPORT"),
            edge("DOC:C241-L64", "ROW:OMEGA1-1963", "PRINTS_1963_CALENDAR_RANGE"),
            edge("ROW:OMEGA1-1963", "H:308_SECONDARY_IDENTITY", "CROSSWALK_NOT_IN_NASA_ROW"),
            edge("H:308_SECONDARY_IDENTITY", "LATENT:NORAD:308:terminal_utc", "ORIGINAL_IDENTITY_AND_EPOCH_MISSING"),
            edge("LATENT:COSMOS34:clock_error_sigma", "H:NO_TRANSFER_1964_TO_1963", "DIFFERENT_OBJECT_YEAR_AND_EVENT_TYPE"),
            edge("LATENT:NORAD:308:terminal_utc", "H:NO_TRANSFER_1964_TO_1963", "NO_COMMON_INSTRUMENTAL_CALIBRATION"),
            edge("H:NO_TRANSFER_1964_TO_1963", "LEAN:candidateNoCalibrationTransfer", "PREMISE_NOT_PHYSICAL_PROOF"),
            edge("LEAN:candidateNoCalibrationTransfer", "PARAM:terminal_error_control_308", "NOT_IDENTIFIED"),
            edge("LEAN:candidateNoCalibrationTransfer", "PARAM:terminal_sigma_528", "NOT_IDENTIFIED"),
            edge("PARAM:terminal_error_control_308", "PARAM:reentry_528_drag_calibration", "NO_EMPIRICAL_CALIBRATION"),
        ],
        "lean_candidates": [
            {"id": "LEAN:candidateNoCalibrationTransfer",
             "status": "CANDIDATE_ONLY_NOT_COMPILED",
             "activation": False, "premises_empirically_authenticated": False},
        ],
        "simulator_parameters": [
            {"id": "PARAM:terminal_error_control_308", "value": None, "activation": False},
            {"id": "PARAM:terminal_sigma_528", "value": None, "activation": False},
            {"id": "PARAM:reentry_528_drag_calibration", "value": None, "activation": False},
        ],
        "new_independent_instrumental_observations_528": 0,
        "new_activated_physical_constraints_528": 0,
        "independence_between_1963_and_1964_sensor_data": "UNKNOWN_NO_SENSOR_LINEAGE",
        "physical_domain_effect": "THETA_UNCHANGED",
        "historical_mcmc": "NOT_RUN",
        "activation": False,
        "next_falsifiable_test": "Recover identified 1963 NORAD 528 or 308 sensor messages specifying event semantics, clock scale, station, calibration and an empirically justified uncertainty; do not transfer the 1964 five-minute printed interval.",
    }
    validate(p)
    return p


def validate(p):
    require(p["schema"] == "conde.c241-l65-intelligence-clock-dependency/v1" and
            p["id"] == "ABELHA-C241-L65-R59-NORAD-1964-CLOCK-CONTEXT",
            "contract identity")
    require(p["sources"][0]["id"] == "C241-L65" and
            p["sources"][0]["sha256"] == L65_SHA and
            p["sources"][1]["sha256"] == L64_SHA, "source linkage")
    a, b = p["records"]
    require(a["id"] == "C241-L65:COSMOS34" and
            a["printed_event_day"] == "1964-07-09" and
            a["printed_z_window"] == ["0931Z", "0936Z"] and
            type(a["printed_nominal_width_minutes"]) is int and
            a["printed_nominal_width_minutes"] == 5 and
            a["qualifier"] == "apparently" and
            a["event_kind"] == "INTELLIGENCE_APPARENT_DEORBIT" and
            a["instrumental_terminal_measurement"] is False, "printed window")
    for k in ("station", "sensor", "instrument_observation_id",
              "estimation_method", "calibrated_sigma_seconds",
              "independent_instrumental_lineages"):
        require(a[k] is None, "fabricated instrument field " + k)
    require(b["id"] == "C241-L64:OMEGA1" and
            b["printed_event_range"] == ["1963-10-29", "1963-10-30"] and
            b["secondary_norad_id"] == 308 and
            b["primary_norad_identity"] is None and
            b["terminal_utc"] is None and
            b["calibrated_sigma_seconds"] is None, "secondary 308 inference")
    require(all(x["activation"] is False for x in p["records"]) and
            p["activation"] is False and
            p["physical_domain_effect"] == "THETA_UNCHANGED" and
            p["historical_mcmc"] == "NOT_RUN" and
            p["new_independent_instrumental_observations_528"] == 0 and
            p["new_activated_physical_constraints_528"] == 0 and
            p["independence_between_1963_and_1964_sensor_data"] == "UNKNOWN_NO_SENSOR_LINEAGE",
            "no new physics")
    require(len(p["lean_candidates"]) == 1 and
            p["lean_candidates"][0]["status"] == "CANDIDATE_ONLY_NOT_COMPILED" and
            p["lean_candidates"][0]["activation"] is False and
            p["lean_candidates"][0]["premises_empirically_authenticated"] is False,
            "Lean activation")
    require(len(p["simulator_parameters"]) == 3 and
            all(x["value"] is None and x["activation"] is False
                for x in p["simulator_parameters"]), "simulator promotion")
    graph = p["graph"]
    require(len(graph) == 15 and len({(x["source"], x["target"], x["relation"])
                                     for x in graph}) == 15, "missing or duplicated edge")
    require(all(x["documentary_only"] is True and x["activation"] is False
                for x in graph), "graph promotion")
    pairs = {(x["source"], x["target"]) for x in graph}
    require(("DOC:C241-L65", "ROW:COSMOS34-1964") in pairs and
            ("H:NO_TRANSFER_1964_TO_1963", "LEAN:candidateNoCalibrationTransfer") in pairs and
            ("LEAN:candidateNoCalibrationTransfer", "PARAM:terminal_sigma_528") in pairs,
            "required graph paths")


def render(root=ROOT):
    return (json.dumps(build(*load(root)), ensure_ascii=False,
                       indent=2, sort_keys=True) + "\n").encode("utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-site", action="store_true")
    args = ap.parse_args()
    data = render()
    if args.check_site:
        require(OUTPUT.read_bytes() == data, "site JSON differs from source")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
    print("C241-L65: 15 documentary edges; 0 new 528 observations; inactive Lean/Theta")


if __name__ == "__main__":
    main()
