#!/usr/bin/env python3
"""Connect NASA October snapshot and cross-edition date signatures to inactive control parameters."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "C241-L68": ("research/tle_custody/nasa_ssr_omega1_oct15_C241-L68.json",
                  "7276ae156f129e6c650cea1c02f8f470403ddde0b9c72949e476d940301e6ab8"),
    "C241-L67": ("research/tle_custody/nasa_ssr_omega308_date_matches_C241-L67.json",
                  "9f1596e1f8a6767ebf090c100ed45994ddcf0f875acca542a1034abfa8914e31"),
    "C241-L66": ("research/tle_custody/nasa_ssr_omega308_cross_edition_C241-L66.json",
                  "28534ac7a87c5590d4cd1fcc6f49e678f86ba65e6b43d460997037ef15f58d72"),
    "ABELHA-L64-R59": ("public/data/conde-ssr-308-l64-dependency-bridge.json",
                       "f897870189802c840e7423b106d49e829dbc1934efd3b0ac1e0ad60bfec7a04b"),
}
OUT = ROOT / "public/data/conde-omega-snapshot-date-genealogy.json"
OCT_PDF = "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2"
DEC_PDF = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"
RETRO_PDF = "c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8"


def require(ok, msg):
    if not ok:
        raise ValueError("OMEGA date genealogy: " + msg)


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "duplicate JSON key: " + key)
        obj[key] = value
    return obj


def load(root=ROOT):
    data = {}
    for key, (path, sha) in INPUTS.items():
        raw = (root / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "input SHA drift: " + key)
        data[key] = json.loads(raw, object_pairs_hook=unique_pairs)
    return data


def edge(source, target, relation):
    return {"source": source, "target": target, "relation": relation,
            "documentary_only": True, "activation": False}


def build(data):
    octo, matches, ancestor, previous = (data[k] for k in INPUTS)
    require(octo["id"] == "C241-L68" and
            octo["source"]["ntrs_id"] == "19640000428" and
            octo["source"]["pdf_sha256"] == OCT_PDF and
            octo["source"]["publication_date"] == "1963-10-15" and
            octo["source"]["report_as_of_utc"] == "1963-10-15T12:00:00Z" and
            octo["source"]["family"] == "NASA_GSFC_SSR_NORAD_SHARED",
            "October source or publication/cutoff")
    r = octo["row"]
    require(r["table_heading"] == "OBJECTS IN ORBIT" and
            r["section"] == "1962 LAUNCHES" and
            r["printed_name"] == "OMEGA 1" and r["launch_day_month"] == "18 JUN" and
            r["nodal_period_minutes"] == "89.7" and
            r["inclination_degrees"] == "82.15" and
            r["apogee_km"] == 263 and r["perigee_km"] == 254 and
            r["catalog_number_printed"] is None, "October printed row")
    lim = octo["limits"]
    for k in ("row_is_instrumental_observation", "as_of_is_instrumental_epoch",
              "source_independent_of_nasa_1963_1977_catalog_family",
              "physical_survival_at_report_cutoff_proven", "active_constraint_528"):
        require(lim[k] is False, "October epistemic limit " + k)
    for k in ("norad_308_identification_from_this_row", "terminal_event_utc",
              "terminal_sigma_seconds", "sensor", "station", "impact_location"):
        require(lim[k] is None, "October missing measurement " + k)
    require(lim["independent_instrumental_observations_added"] == 0 and
            lim["historical_mcmc"] == "NOT_RUN", "October activation")
    require("C241-L67" in octo["related"] and "C241-L64" in octo["related"],
            "October documentary crosslinks")

    require(matches["id"] == "C241-L67" and ancestor["id"] == "C241-L66" and
            matches["inherited"] == ["C241-L65", "C241-L66"] and
            matches["editions"]["contemporary"]["sha256"] == DEC_PDF and
            matches["editions"]["retrospective"]["sha256"] == RETRO_PDF and
            ancestor["sources"]["contemporary_1963"]["sha256"] == DEC_PDF and
            ancestor["sources"]["retrospective_1977"]["sha256"] == RETRO_PDF and
            matches["editions"]["contemporary"]["catalog_number_printed"] is False and
            matches["editions"]["retrospective"]["catalog_number_printed"] is True,
            "cross-edition custody / catalog ID distinction")
    expected = [("OMEGA 1", "OMEGA 2", 308, "29-30 OCT 63"),
                ("OMEGA 2", "OMEGA 3", 310, "12 JUL 62"),
                ("OMEGA 3", "A-ALPHA 5", 314, "14 JUL 62")]
    contemporary = matches["contemporary_rows"]
    retrospective = matches["retrospective_rows"]
    found = []
    for co, re in zip(contemporary, retrospective):
        require(co["launch"] == re["launch"] == "18 JUN" and
                co["decay"] == re["decay"], "launch/decay signature not equal")
        found.append((co["printed_name"], re["printed_name"],
                      re["catalog_number"], co["decay"]))
    require(found == expected, "three date signatures")
    require(matches["date_signature_matches"] ==
            [{"contemporary_name": co, "retrospective_name": re,
              "retrospective_catalog_number": num} for co, re, num, _ in expected],
            "declared matches differ from printed rows")
    al = ancestor["sources"]["contemporary_1963"]["visually_read_rows"]
    require([(x["designator"], x["launch"], x["decay"]) for x in al] ==
            [(x["printed_name"], x["launch"], x["decay"]) for x in contemporary],
            "ancestor contemporary row drift")
    for k, expected_value in (("date_match_is_instrumental_identity", False),
                               ("edition_independence", "SAME_NASA_GSFC_REPORT_FAMILY"),
                               ("calendar_is_utc_timing_measurement", False),
                               ("terminal_event_utc", None),
                               ("terminal_sigma_seconds", None),
                               ("active_constraint_528", False)):
        require(matches["limits"][k] == expected_value, "date-signature inference " + k)
    require(matches["limits"]["independent_instrumental_measurements"] == 0,
            "date signature sensor promotion")
    require(previous["id"] == "ABELHA-C241-L64-R59-308-CALENDAR-RANGE" and
            previous["observation"]["nasa_printed_norad_id"] is None and
            previous["observation"]["terminal_event_utc"] is None and
            previous["observation"]["terminal_sigma_seconds"] is None and
            previous["physical_domain_effect"] == "THETA_UNCHANGED" and
            previous["activation"] is False, "prior inactive control 308")
    graph = [
        edge("PDF:NTRS-19640000428", "DOC:C241-L68", "OCTOBER_CATALOG_FACSIMILE"),
        edge("DOC:C241-L68", "ROW:OCT63:OMEGA1", "PRINTED_ORBIT_TABLE"),
        edge("ROW:OCT63:OMEGA1", "VALUE:OCT63:CATALOG_ORBIT_ELEMENTS",
             "PUBLISHED_VALUES_NOT_MEASUREMENT"),
        edge("DOC:C241-L68", "CUT:1963-10-15T12Z", "REPORT_EDITORIAL_CUTOFF"),
        edge("CUT:1963-10-15T12Z", "H:CUTOFF_NOT_EPOCH", "NO_INSTRUMENTAL_EPOCH"),
        edge("PDF:NTRS-19640003479", "DOC:C241-L66", "DECEMBER_FACSIMILE"),
        edge("PDF:NTRS-19780009188", "DOC:C241-L66", "RETROSPECTIVE_FACSIMILE"),
        edge("DOC:C241-L66", "DOC:C241-L67", "ANCESTRAL_ROW_DEPENDENCE"),
        edge("DOC:C241-L67", "SIG:DATE:308_310_314", "THREE_MATCHES"),
        edge("SIG:DATE:308_310_314", "H:PRINTED_NAME_CONFLICT",
             "DATE_MATCH_NOT_IDENTITY_PROOF"),
        edge("DOC:C241-L64", "RANGE:1963-10-29_30", "PRINTED_DECAY_DAY_RANGE"),
        edge("RANGE:1963-10-29_30", "LATENT:308:terminal_utc",
             "CALENDAR_RANGE_NOT_SENSOR_TIMESTAMP"),
        edge("H:PRINTED_NAME_CONFLICT", "LATENT:308:identity", "REQUIRES_PRIMARY_CROSSWALK"),
        edge("H:CUTOFF_NOT_EPOCH", "LATENT:308:observation_epoch",
             "REPORT_CUTOFF_NOT_INSTRUMENTAL_EPOCH"),
        edge("VALUE:OCT63:CATALOG_ORBIT_ELEMENTS", "LATENT:308:observation_epoch",
             "EPOCH_CALIBRATION_MISSING"),
        edge("LATENT:308:identity", "LEAN:candidateOmegaControlLink",
             "UNPROVEN_IDENTITY"),
        edge("LATENT:308:terminal_utc", "LEAN:candidateOmegaControlLink",
             "UNAVAILABLE_TERMINAL_UTC"),
        edge("LATENT:308:observation_epoch", "LEAN:candidateOmegaControlLink",
             "UNAVAILABLE_OBSERVATION_EPOCH"),
        edge("LEAN:candidateOmegaControlLink", "PARAM:terminal_error_control_308",
             "NOT_PROMOTED"),
        edge("PARAM:terminal_error_control_308", "PARAM:reentry_528_drag_calibration",
             "NO_CALIBRATED_TRANSFER"),
    ]
    payload = {
        "schema": "conde.omega-snapshot-date-genealogy/v1",
        "id": "ABELHA-C241-L68-L67-L66-L64-OMEGA",
        "sources": [
            {"id": key, "path": path, "sha256": sha}
            for key, (path, sha) in INPUTS.items()
        ],
        "pdfs": [
            {"ntrs_id": "19640000428", "sha256": OCT_PDF, "edition": "1963-10-15"},
            {"ntrs_id": "19640003479", "sha256": DEC_PDF, "edition": "1963-12-15"},
            {"ntrs_id": "19780009188", "sha256": RETRO_PDF, "edition": "1977"},
        ],
        "october_catalogue": {
            "occurrence_id": "C241-L68:OMEGA1", "printed_name": "OMEGA 1",
            "report_as_of_utc": "1963-10-15T12:00:00Z",
            "report_cutoff_is_observation_epoch": False,
            "catalogued_elements": {
                "nodal_period_minutes": "89.7", "inclination_degrees": "82.15",
                "apogee_km": 263, "perigee_km": 254,
            },
            "instrumental_observation_epoch_utc": None,
            "instrument": None, "station": None, "covariance": None,
            "identity_norad_308": None, "independent_measurement": False,
            "physical_survival_at_cutoff_proven": False, "activation": False,
        },
        "date_signatures": [
            {"contemporary_name": co, "retrospective_name": re,
             "retrospective_catalog_number": num,
             "decay_printed": decay, "launch_printed": "18 JUN",
             "identity_grade": "DATE_SIGNATURE_ONLY_NOT_INSTRUMENTALLY_CONFIRMED"}
            for co, re, num, decay in expected
        ],
        "independence": {
            "family": "NASA_GSFC_SSR_NORAD_SHARED",
            "distinct_facsimiles": 3,
            "independent_instrumental_observations_added": 0,
            "number_of_underlying_distinct_sensors": None,
        },
        "graph": graph,
        "latents": [
            {"id": "LATENT:308:identity", "value": None, "activation": False},
            {"id": "LATENT:308:observation_epoch", "value": None, "activation": False},
            {"id": "LATENT:308:terminal_utc", "value": None, "activation": False},
        ],
        "lean_candidates": [
            {"id": "LEAN:candidateOmegaControlLink",
             "status": "CANDIDATE_ONLY_NOT_COMPILED", "activation": False},
        ],
        "simulator_parameters": [
            {"id": "PARAM:terminal_error_control_308", "value": None, "activation": False},
            {"id": "PARAM:reentry_528_drag_calibration", "value": None, "activation": False},
        ],
        "historical_mcmc": "NOT_RUN",
        "new_activated_physical_constraints": 0,
        "physical_domain_effect": "THETA_UNCHANGED",
        "activation": False,
        "next_test": "Obtain a contemporary source explicitly cross-identifying OMEGA 1/2 and NORAD 308; then recover individual epoch, station, instrument and uncertainty.",
    }
    validate(payload)
    return payload


def validate(p):
    require(p["activation"] is False and
            p["physical_domain_effect"] == "THETA_UNCHANGED" and
            p["historical_mcmc"] == "NOT_RUN" and
            p["new_activated_physical_constraints"] == 0,
            "unsupported physics promotion")
    o = p["october_catalogue"]
    require(o["identity_norad_308"] is None and
            o["report_cutoff_is_observation_epoch"] is False and
            o["independent_measurement"] is False and
            o["physical_survival_at_cutoff_proven"] is False and
            o["activation"] is False and
            all(o[k] is None for k in ("instrumental_observation_epoch_utc",
                                       "instrument", "station", "covariance")),
            "fabricated October instrument or identity")
    require(p["independence"]["independent_instrumental_observations_added"] == 0 and
            p["independence"]["number_of_underlying_distinct_sensors"] is None,
            "fabricated independent sensor")
    require([(x["contemporary_name"], x["retrospective_name"],
              x["retrospective_catalog_number"]) for x in p["date_signatures"]] ==
            [("OMEGA 1", "OMEGA 2", 308),
             ("OMEGA 2", "OMEGA 3", 310),
             ("OMEGA 3", "A-ALPHA 5", 314)], "fabricated crosswalk")
    require(all(x["identity_grade"] == "DATE_SIGNATURE_ONLY_NOT_INSTRUMENTALLY_CONFIRMED"
                for x in p["date_signatures"]), "date match promoted")
    for items in ("latents", "simulator_parameters"):
        require(all(x["activation"] is False and x["value"] is None for x in p[items]),
                "latent/parameter promotion")
    require(all(x["activation"] is False and
                x["status"] == "CANDIDATE_ONLY_NOT_COMPILED"
                for x in p["lean_candidates"]), "Lean falsely promoted")
    graph = p["graph"]
    require(len(graph) == 20 and
            len(set((e["source"], e["target"], e["relation"]) for e in graph)) == 20 and
            all(e["documentary_only"] is True and e["activation"] is False
                for e in graph), "missing/duplicate/activated edge")


def render(root=ROOT):
    return (json.dumps(build(load(root)), ensure_ascii=False, sort_keys=True,
                       indent=2) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-site", action="store_true")
    a = parser.parse_args()
    content = render()
    if a.check_site:
        require(OUT.read_bytes() == content, "published bytes differ from audited inputs")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(content)
    print("C241-L68/L67/L66/L64: 20 pending edges; no physical promotion")


if __name__ == "__main__":
    main()
