#!/usr/bin/env python3
"""R60: UN Omega registration roles and "Decay before" as inactive provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.c241_un_omega_registry_alias_r66 import assess
SOURCES = {
    "UN-R66": (
        "research/tle_custody/c241_un_omega_registry_leads_r66.json",
        "66215c3f63c1bf52394afa8dacf6cc86ecc77166bc001d80d1ac08027903f3f3",
    ),
    "NASA-OMEGA-R58": (
        "public/data/conde-omega-snapshot-date-genealogy.json",
        "bfeba1fa6d39c0847b34487728f5d740475976f32dcb12f51c145ca2253905d2",
    ),
}
OUTPUT = "public/data/conde-un-omega-alias-dependency.json"
LATENT_NAMES = ("source_crosswalk", "event_utc", "sensor_lineage",
                "terminal_sigma", "registration_role")
PARAMETERS = ("PARAM:terminal_error_control_308", "PARAM:reentry_528_drag_calibration")


def require(ok, message):
    if not ok:
        raise ValueError("R60 UN Omega bridge: " + message)


def unique_keys(pairs):
    obj = {}
    for key, val in pairs:
        require(key not in obj, "duplicate JSON key: " + key)
        obj[key] = val
    return obj


def load(root=ROOT):
    out = {}
    for key, (path, sha) in SOURCES.items():
        content = (root / path).read_bytes()
        require(hashlib.sha256(content).hexdigest() == sha, "SHA drift: " + key)
        out[key] = json.loads(content, object_pairs_hook=unique_keys)
    return out


def edge(src, dst, relation):
    return {"source": src, "target": dst, "relation": relation,
            "documentary_only": True, "activation": False}


def build(data):
    un, nasa = data["UN-R66"], data["NASA-OMEGA-R58"]
    audited = assess(un)
    require(audited["un_source_status"] ==
            "SECONDARY_COMPILATION_PRIMARY_DOCUMENT_PENDING", "UN original status")
    require(audited["un_omega1_decay_report"]["field_heading"] == "Decay before" and
            audited["un_omega1_decay_report"]["cutoff_calendar_day"] == "1963-10-31" and
            audited["un_omega1_decay_report"]["event_utc_time"] is None,
            "calendar cutoff promoted to timestamp")
    require(audited["registration_roles"] == {
        "1962 Omega 1": "MAIN_REGISTERED_OBJECT",
        "1962 Omega 2": "FRAGMENT", "1962 Omega 3": "FRAGMENT",
    }, "fragment aliases or primary role")
    require(audited["same_name_implies_same_object_across_editions"] is False and
            audited["date_alignment_is_calibrated_utc_interval"] is False and
            audited["independent_terminal_holdouts_added"] == 0 and
            audited["identity_probability"] is None and
            audited["terminal_sigma_hours"] is None and
            audited["active_constraint_528"] is False and
            audited["historical_mcmc"] == "NOT_RUN", "false physical promotion")
    require(nasa["schema"] == "conde.omega-snapshot-date-genealogy/v1" and
            nasa["id"] == "ABELHA-C241-L68-L67-L66-L64-OMEGA" and
            nasa["activation"] is False and
            nasa["physical_domain_effect"] == "THETA_UNCHANGED" and
            nasa["historical_mcmc"] == "NOT_RUN" and
            nasa["new_activated_physical_constraints"] == 0,
            "previous NASA scientific bridge mutated")
    require(nasa["october_catalogue"]["report_cutoff_is_observation_epoch"] is False and
            nasa["october_catalogue"]["identity_norad_308"] is None and
            nasa["october_catalogue"]["activation"] is False and
            len(nasa["date_signatures"]) == 3 and
            nasa["date_signatures"][0]["contemporary_name"] == "OMEGA 1" and
            nasa["date_signatures"][0]["retrospective_catalog_number"] == 308 and
            all(p["value"] is None and p["activation"] is False
                for p in nasa["simulator_parameters"]),
            "NASA date signatures mistaken for measured identity")
    require(un["sources"]["original_un_document_scans_verified"] is False and
            un["sources"]["instrumental_independence_from_nasa_catalog_verified"] is False,
            "unverified original or sensor independence")
    links = [
        ("TABLE:UN:A1", "ENTRY:1962-OMEGA1", "MAIN_REGISTRATION"),
        ("TABLE:UN:B1", "ENTRY:1962-OMEGA2", "REGISTERED_FRAGMENT"),
        ("TABLE:UN:B1", "ENTRY:1962-OMEGA3", "REGISTERED_FRAGMENT"),
        ("ENTRY:1962-OMEGA2", "H:ROLE_NOT_ORBIT_ID", "FRAGMENT_NOT_SENSOR"),
        ("ENTRY:1962-OMEGA3", "H:ROLE_NOT_ORBIT_ID", "FRAGMENT_NOT_SENSOR"),
        ("ENTRY:1962-OMEGA1", "DOC:UN-INF013", "TRANSCRIBED_REFERENCE_ONLY"),
        ("DOC:UN-INF013", "H:ORIGINAL_UN_PENDING", "FACSIMILE_NOT_RECOVERED"),
        ("TABLE:UN:A3", "DOC:UN-INF054", "REGISTERED_DECAY_REFERENCE"),
        ("DOC:UN-INF054", "CUT:BEFORE-1963-10-31", "DECAY_BEFORE_HEADING"),
        ("CUT:BEFORE-1963-10-31", "H:NOT_TERMINAL_UTC", "CALENDAR_NOT_UTC"),
        ("DOC:C241-L64", "RANGE:NASA-1963-10-29_30", "NASA_PRINTED_DAYS"),
        ("RANGE:NASA-1963-10-29_30", "H:NOT_TERMINAL_UTC",
         "DAY_LABELS_NOT_SENSOR_TIME"),
        ("DOC:C241-L67", "SIGNATURE:NASA-308", "RETROSPECTIVE_DATE_SIGNATURE"),
        ("SIGNATURE:NASA-308", "H:NO_UN_TO_NORAD", "MATCH_NOT_DIRECT_CROSSWALK"),
        ("ENTRY:1962-OMEGA1", "H:NO_UN_TO_NORAD", "NAME_NOT_DIRECT_CROSSWALK"),
        ("H:ORIGINAL_UN_PENDING", "LATENT:UN:source_crosswalk", "RAW_UN_SCAN_MISSING"),
        ("H:NO_UN_TO_NORAD", "LATENT:UN:source_crosswalk", "NORAD_ID_MISSING"),
        ("H:NOT_TERMINAL_UTC", "LATENT:UN:event_utc", "UTC_OBSERVATION_MISSING"),
        ("H:ROLE_NOT_ORBIT_ID", "LATENT:UN:registration_role", "ALIAS_ROLE_UNRESOLVED"),
        ("H:ORIGINAL_UN_PENDING", "LATENT:UN:sensor_lineage",
         "INSTRUMENT_INDEPENDENCE_MISSING"),
        ("H:NOT_TERMINAL_UTC", "LATENT:UN:terminal_sigma", "TIMING_ERROR_MISSING"),
        ("LATENT:UN:source_crosswalk", "LEAN:candidateUnOmegaControlIdentity",
         "MISSING_IDENTITY_PREMISE"),
        ("LATENT:UN:event_utc", "LEAN:candidateUnOmegaControlIdentity",
         "MISSING_EVENT_TIME"),
        ("LATENT:UN:sensor_lineage", "LEAN:candidateUnOmegaControlIdentity",
         "MISSING_INDEPENDENCE"),
        ("LATENT:UN:terminal_sigma", "LEAN:candidateUnOmegaControlIdentity",
         "MISSING_ERROR"),
        ("LATENT:UN:registration_role", "LEAN:candidateUnOmegaControlIdentity",
         "MISSING_ROLE_RESOLUTION"),
        ("LEAN:candidateUnOmegaControlIdentity", PARAMETERS[0],
         "NOT_PROMOTED"),
        (PARAMETERS[0], PARAMETERS[1], "NO_CALIBRATED_TRANSFER"),
    ]
    graph = [edge(*triple) for triple in links]
    payload = {
        "schema": "conde.documentary-scientific-bridge/v1",
        "id": "C241-ABELHA-R60-UN-OMEGA",
        "occurrence_ids": ["C241-R66-UN-OMEGA-REGISTRY",
                           "C241-L64", "C241-L67", "C241-L68"],
        "source_family": "UN_SECONDARY_REGISTRY_TRANSCRIPTION_WITH_NASA_SHARED_CATALOG_CONTEXT",
        "sources": [
            {"id": key, "path": path, "sha256": sha,
             "role": "SECONDARY_UN_TRANSCRIPTION" if key == "UN-R66"
                     else "EXISTING_NASA_GENEALOGY"}
            for key, (path, sha) in SOURCES.items()
        ],
        "original_un_document_scans_verified": False,
        "un_document_identifiers": ["A/AC.105/INF.013", "A/AC.105/INF.054"],
        "reported_roles": audited["registration_roles"],
        "calendar_comparison": {
            "un_heading": "Decay before",
            "un_calendar_cutoff": "1963-10-31",
            "nasa_printed_days": ["1963-10-29", "1963-10-30"],
            "nominal_labels_compatible": True,
            "converted_terminal_utc": None,
            "calendar_label_is_calibrated_utc": False,
            "crosswalk_norad_308": None,
            "independent_sensor_observations_from_comparison": 0,
        },
        "matrix_C001_C238_unchanged": True,
        "graph": graph, "delta_links": len(graph),
        "latents": [{"id": "LATENT:UN:" + name, "value": None,
                     "activation": False} for name in LATENT_NAMES],
        "lean_candidate": {
            "id": "candidateUnOmegaControlIdentity",
            "status": "NOT_PROMOTED", "compiled_theorem_claimed": False,
            "missing_premises": list(LATENT_NAMES),
        },
        "simulator_parameters": [
            {"id": param, "value": None, "activation": False} for param in PARAMETERS
        ],
        "new_independent_terminal_measurements": 0,
        "historical_independent_528_measurements_known": None,
        "historical_mcmc": "NOT_RUN",
        "delta_orbital_constraints": 0,
        "physical_domain_effect": "THETA_UNCHANGED",
        "activation": False,
        "next_test": ("Recover original A/AC.105/INF.013 and INF.054 and a "
                      "contemporaneous UN-NORAD crosswalk with sensor log, "
                      "station, UTC convention, reference frame and uncertainty."),
    }
    validate(payload)
    return payload


def validate(payload):
    require(payload["delta_links"] == 28 and
            len(payload["graph"]) == 28 and
            len({(e["source"], e["target"], e["relation"])
                 for e in payload["graph"]}) == 28 and
            all(e["documentary_only"] is True and e["activation"] is False
                for e in payload["graph"]), "graph promoted or duplicate")
    require(payload["activation"] is False and
            payload["physical_domain_effect"] == "THETA_UNCHANGED" and
            payload["delta_orbital_constraints"] == 0 and
            payload["new_independent_terminal_measurements"] == 0 and
            payload["historical_independent_528_measurements_known"] is None and
            payload["historical_mcmc"] == "NOT_RUN",
            "invented physical constraint")
    require(payload["original_un_document_scans_verified"] is False and
            payload["calendar_comparison"]["converted_terminal_utc"] is None and
            payload["calendar_comparison"]["crosswalk_norad_308"] is None and
            payload["calendar_comparison"]["calendar_label_is_calibrated_utc"] is False and
            payload["calendar_comparison"]["independent_sensor_observations_from_comparison"] == 0,
            "temporal or identity promotion")
    require(payload["lean_candidate"]["status"] == "NOT_PROMOTED" and
            payload["lean_candidate"]["compiled_theorem_claimed"] is False and
            payload["lean_candidate"]["missing_premises"] == list(LATENT_NAMES) and
            all(x["value"] is None and x["activation"] is False
                for x in payload["latents"] + payload["simulator_parameters"]),
            "latent or Lean promoted")


def render(root=ROOT):
    return (json.dumps(build(load(root)), indent=2,
                       sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    data = render()
    out = ROOT / OUTPUT
    if args.check_site:
        require(out.read_bytes() == data, "published bytes differ from source")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    print("R60: 28 documentary links, 5 null latents; no 528 promotion")


if __name__ == "__main__":
    main()
