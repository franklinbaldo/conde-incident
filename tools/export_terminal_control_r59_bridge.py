#!/usr/bin/env python3
"""Connect Cervo R59 terminal-control archive leads to inactive Lean/Theta contracts.

This graph is a source-selection *crosswalk*, not reentry-time calibration.
The Parquet's 1963 epochs are one secondary lineage, not sensor replicates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import c241_1963_terminal_control_screen as screen

LEDGER = "research/statistics/C241_1963_TERMINAL_CONTROL_SCREEN_20261114.md"
LEDGER_SHA = "8495e42842f429b143bb1339ed24f25c25b81b8f6dd13c50bd1f990330c552ab"
AUDITOR = "tools/c241_1963_terminal_control_screen.py"
AUDITOR_SHA = "f2bb01247800837929462327d38471e0831a66fab0537f454ed64ed748005342"
OUTPUT = ROOT / "public/data/conde-terminal-control-r59-scientific-bridge.json"
NEW_CANDIDATES = (292, 308, 565, 668)
CONTROLS = (637, 688)
TARGET = 528
EPOCH_COUNTS = {292: 53, 308: 52, 565: 31, 668: 10, 637: 25, 688: 1, 528: 45}


def require(condition, why):
    if not condition:
        raise ValueError("R59 terminal-control bridge: " + why)


def pinned(root, path, sha):
    body = (root / path).read_bytes()
    require(hashlib.sha256(body).hexdigest() == sha, "source SHA drift: " + path)
    return body


def load(root=ROOT):
    ledger = pinned(root, LEDGER, LEDGER_SHA).decode("utf-8")
    auditor = pinned(root, AUDITOR, AUDITOR_SHA).decode("utf-8")
    require("C241-1963-TERMINAL-CONTROLS-R59" in ledger, "ledger experiment ID")
    require("SECONDARY_ARCHIVE_SEARCH_NOT_CALIBRATED" in ledger, "ledger status")
    require("ONE_SECONDARY_SPACE_TRACK_MIRROR" in auditor, "auditor lineage")
    return ledger, auditor


def edge(a, b, relation):
    return {"source": a, "target": b, "relation": relation,
            "activation": False, "documentary_only": True}


def build(ledger, auditor):
    require("C241-1963-TERMINAL-CONTROLS-R59" in ledger, "experiment ID")
    require("SECONDARY_ARCHIVE_SEARCH_NOT_CALIBRATED" in ledger, "status")
    require("ONE_SECONDARY_SPACE_TRACK_MIRROR" in auditor, "lineage")
    require(set(screen.CASES) == set(EPOCH_COUNTS), "source candidate set")
    require(screen.EXPECTED_DISTINCT == EPOCH_COUNTS, "source epoch counts")
    require(screen.EXPECTED_RAW == EPOCH_COUNTS, "source raw row counts")
    require(tuple(v for v in (292, 308, 565, 668) if screen.CASES[v][3] == "CANDIDATE")
            == NEW_CANDIDATES, "candidate identity")
    require(screen.SOURCE_SHA256 ==
            "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09",
            "Parquet SHA identity")

    observations = []
    graph = [
        edge("DOC:R59-LEDGER", "SRC:SPACE-TRACK-1963-PARQUET", "DECLARED_ONE_SECONDARY_LINEAGE"),
        edge("DOC:R59-LEDGER", "CODE:R59-AUDITOR", "AUDIT_GENERATED_FROM_PINNED_INPUT"),
        edge("SRC:SPACE-TRACK-1963-PARQUET", "H:CATALOGUE_SECANT_NOT_TERMINAL_HOLDOUT",
             "CATALOGUE_EPOCHS_NOT_INSTRUMENT_MEASUREMENTS"),
    ]
    for sid in NEW_CANDIDATES + CONTROLS + (TARGET,):
        day, url, grade, role = screen.CASES[sid]
        require(role in ("CANDIDATE", "KNOWN_CONTROL", "INCOMPLETE_CONTROL",
                         "TARGET_NOT_CONTROL"), "role")
        require(role == ("CANDIDATE" if sid in NEW_CANDIDATES else
                         "TARGET_NOT_CONTROL" if sid == TARGET else
                         "KNOWN_CONTROL" if sid == 637 else "INCOMPLETE_CONTROL"),
                "role mapping")
        if sid in NEW_CANDIDATES:
            require(grade == "SECONDARY_DECAY_DAY_LEAD", "unverified source grade")
        prefix = "NORAD:" + str(sid)
        observations.append({
            "id": "R59:" + prefix, "norad_id": sid, "role": role,
            "catalogue_epochs_1963": EPOCH_COUNTS[sid],
            "source_url": url, "reported_calendar_day": day,
            "day_evidence_grade": grade,
            "date_as_instrumental_utc": None,
            "independent_instrumental_lineages": None,
            "terminal_event_utc": None,
            "terminal_sigma_seconds": None,
            "instrument_station": None, "reference_frame": None,
            "terminal_phenomenon_definition": None,
            "archive_search_only": True, "activation": False})
        graph.extend((
            edge("SRC:SPACE-TRACK-1963-PARQUET", "CAT:" + prefix,
                 "ONE_SECONDARY_CATALOGUE_CONTAINS_EPOCHS"),
            edge("DOC:R59-LEDGER", "LEAD:" + prefix,
                 "CALENDAR_DAY_WITH_GRADE_" + grade),
            edge("CAT:" + prefix, "LATENT:" + prefix + ":observation_lineage",
                 "TRACKING_SENSOR_AND_INDEPENDENCE_UNKNOWN"),
            edge("LEAD:" + prefix, "LATENT:" + prefix + ":terminal_utc",
                 "EVENT_TIME_AND_SOURCE_CONVENTION_UNVERIFIED"),
            edge("LATENT:" + prefix + ":terminal_utc",
                 "LEAN:candidateTerminalControlEvidence",
                 "MISSING_TERMINAL_EVENT_CALIBRATION"),
            edge("LATENT:" + prefix + ":observation_lineage",
                 "LEAN:candidateCatalogueSecantCalibration",
                 "SECONDARY_CATALOGUE_NOT_A_HOLDOUT"),
        ))
        if sid in NEW_CANDIDATES:
            graph.append(edge("LEAN:candidateTerminalControlEvidence",
                              "PARAM:terminal_error_control_" + str(sid),
                              "NO_TIME_SIGMA_OR_INDEPENDENT_TERMINAL_DATA"))
    graph.append(edge("LEAN:candidateCatalogueSecantCalibration",
                      "PARAM:reentry_528_drag_calibration",
                      "NO_TRANSFER_FROM_UNCALIBRATED_CONTROLS"))
    payload = {
        "schema": "conde.c241-r59-terminal-control-bridge/v1",
        "id": "ABELHA-C241-CERVO-R59-TERMINAL-CONTROLS",
        "input_sources": [
            {"id": "C241-1963-TERMINAL-CONTROLS-R59", "path": LEDGER, "sha256": LEDGER_SHA,
             "role": "documented_retrospective_screen"},
            {"id": "CODE:R59-AUDITOR", "path": AUDITOR, "sha256": AUDITOR_SHA,
             "role": "deterministic_secondary_catalogue_screen"},
            {"id": "SRC:SPACE-TRACK-1963-PARQUET", "url": screen.SOURCE_URL,
             "sha256": screen.SOURCE_SHA256,
             "role": "single_secondary_catalogue_lineage_not_independent_sensors"},
        ],
        "observations": observations,
        "archive_search_order": list(NEW_CANDIDATES),
        "design": "RETROSPECTIVE_ARCHIVE_TRIAGE_NOT_PROSPECTIVE_HOLDOUT",
        "hypotheses": ["H:CATALOGUE_SECANT_NOT_TERMINAL_HOLDOUT",
                       "H:INDEPENDENT_TERMINAL_CALIBRATION_MISSING"],
        "graph": graph,
        "lean_candidates": ["candidateTerminalControlEvidence",
                            "candidateCatalogueSecantCalibration"],
        "lean_status": "CANDIDATE_ONLY_NOT_COMPILED",
        "latents": [{"id": "LATENT:NORAD:" + str(sid) + ":" + field,
                     "value": None, "activation": False}
                    for sid in NEW_CANDIDATES + CONTROLS + (TARGET,)
                    for field in ("terminal_utc", "observation_lineage")],
        "simulator_parameters": [
            {"id": "PARAM:terminal_error_control_" + str(sid),
             "value": None, "activation": False} for sid in NEW_CANDIDATES
        ] + [{"id": "PARAM:reentry_528_drag_calibration",
              "value": None, "activation": False}],
        "catalogue_epochs_new_candidates_total": 146,
        "catalogue_epochs_are_independent_instrumental_observations": False,
        "new_independent_instrumental_observations": 0,
        "new_activated_physical_constraints": 0,
        "activation": False, "physical_domain_effect": "THETA_UNCHANGED",
        "historical_mcmc": "NOT_RUN",
        "next_falsifiable_test": "Retrieve identified instrument-level terminal events with UTC, station, frame and error for each control, then pre-register a holdout before comparing predictions.",
    }
    validate(payload)
    return payload


def validate(payload):
    require(payload["activation"] is False and
            payload["physical_domain_effect"] == "THETA_UNCHANGED", "physical promotion")
    require(payload["new_independent_instrumental_observations"] == 0 and
            payload["new_activated_physical_constraints"] == 0 and
            payload["historical_mcmc"] == "NOT_RUN", "independent observation promotion")
    require(payload["catalogue_epochs_are_independent_instrumental_observations"] is False,
            "catalogue replication")
    require(payload["archive_search_order"] == list(NEW_CANDIDATES), "archive ranking")
    require(payload["catalogue_epochs_new_candidates_total"] == 146, "epoch total")
    require(len(payload["observations"]) == 7, "seven objects")
    require({v["norad_id"] for v in payload["observations"]} == set(EPOCH_COUNTS),
            "object identifiers")
    for obj in payload["observations"]:
        sid = obj["norad_id"]
        require(obj["catalogue_epochs_1963"] == EPOCH_COUNTS[sid], "epoch checksum")
        for name in ("date_as_instrumental_utc", "independent_instrumental_lineages",
                     "terminal_event_utc", "terminal_sigma_seconds",
                     "instrument_station", "reference_frame", "terminal_phenomenon_definition"):
            require(obj[name] is None, "unobserved field was promoted: " + name)
        require(obj["activation"] is False and obj["archive_search_only"] is True,
                "object activated")
    for item in payload["latents"] + payload["simulator_parameters"]:
        require(item["value"] is None and item["activation"] is False, "latent activated")
    require(len(payload["graph"]) == len({(x["source"], x["target"], x["relation"])
                                         for x in payload["graph"]}), "duplicate graph edge")
    require(all(e["activation"] is False and e["documentary_only"] is True
                for e in payload["graph"]), "graph activation")


def render(root=ROOT):
    return (json.dumps(build(*load(root)), ensure_ascii=False, indent=2,
                       sort_keys=True) + "\n").encode("utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-site", action="store_true")
    args = ap.parse_args()
    expected = render()
    if args.check_site:
        require(OUTPUT.read_bytes() == expected, "published JSON drift")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(expected)
    print("R59 documentary bridge:", len(json.loads(expected)["graph"]),
          "edges; 0 new instrument observations; Theta unchanged")


if __name__ == "__main__":
    main()
