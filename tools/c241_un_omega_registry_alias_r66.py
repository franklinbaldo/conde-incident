#!/usr/bin/env python3
"""C241 R66: UN Omega registry transcription roles, not identity or time calibration."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path

SCHEMA = "conde.c241.un-omega-registration-leads.r66/v1"
EXPECTED_ROWS = [
    {"table":"A1","cospar_1962":"1962 Omega 1","launch_day":"1962-06-18",
     "role":"MAIN_REGISTERED_OBJECT","period_min":92.4,"perigee_km":367,
     "apogee_km":408,"inclination_deg":82.1,"un_document":"A/AC.105/INF.013"},
    {"table":"B1","cospar_1962":"1962 Omega 2","launch_day":"1962-06-18",
     "role":"FRAGMENT","un_document":"A/AC.105/INF.013"},
    {"table":"B1","cospar_1962":"1962 Omega 3","launch_day":"1962-06-18",
     "role":"FRAGMENT","un_document":"A/AC.105/INF.013"},
    {"table":"A3","cospar_1962":"1962 Omega 1","field_heading":"Decay before",
     "reported_before_date":"1963-10-31",
     "date_type":"REGISTER_CUTOFF_NOT_EVENT_TIMESTAMP",
     "un_document":"A/AC.105/INF.054"},
]
EXPECTED_SOURCES = {
    "a1":"https://planet4589.org/space/un/un_taba.html",
    "a3":"https://planet4589.org/space/un/un_taba3.html",
    "b1":"https://planet4589.org/space/un/un_tabb1.html",
    "nasa_1963":"https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=17",
    "un_registration_first":"A/AC.105/INF.013",
    "un_reporting_later":"A/AC.105/INF.054",
    "original_un_document_scans_verified":False,
    "instrumental_independence_from_nasa_catalog_verified":False,
}
EXPECTED_NASA = {
    "name":"OMEGA 1","launch_day":"1962-06-18",
    "printed_decay_days":["1963-10-29","1963-10-30"],
    "norad_id_printed":None,"utc_convention_established":False,
}
EXPECTED_BOUNDS = {
    "direct_un_to_norad_308_crosswalk":False,
    "un_report_contains_terminal_sensor_time":False,
    "independent_terminal_holdouts_added":0,
    "terminal_sigma_hours":None,"terminal_instant_utc":None,
    "identity_probability":None,"active_constraint_528":False,
    "impact_geography":None,"historical_mcmc":"NOT_RUN",
}

def assess(record: dict) -> dict:
    """Reject provenance/semantic promotion; return conditional calendar comparison."""
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        raise ValueError("schema mismatch")
    if record.get("evidence_class") != "SECONDARY_TRANSCRIPTION_OF_UN_REGISTRY_NOT_PRIMARY_SCAN":
        raise ValueError("source promoted to primary")
    if record.get("sources") != EXPECTED_SOURCES:
        raise ValueError("source custody or independence changed")
    if record.get("transcribed_rows") != EXPECTED_ROWS:
        raise ValueError("UN transcript/role/cutoff mismatch")
    if record.get("nasa_1963_row") != EXPECTED_NASA:
        raise ValueError("NASA name/date/UTC convention drift")
    if record.get("boundaries") != EXPECTED_BOUNDS:
        raise ValueError("prohibited inference promotion")
    # These are printed calendar labels, not sampled orbital timestamps.
    cutoff = date.fromisoformat(EXPECTED_ROWS[3]["reported_before_date"])
    days = [date.fromisoformat(x) for x in EXPECTED_NASA["printed_decay_days"]]
    if len(days) != 2 or not days[0] < days[1] < cutoff:
        raise ValueError("calendar ordering drift")
    return {
        "schema":"conde.c241.un-omega-alias-audit.r66/v1",
        "un_source_status":"SECONDARY_COMPILATION_PRIMARY_DOCUMENT_PENDING",
        "registration_roles":{"1962 Omega 1":"MAIN_REGISTERED_OBJECT",
                              "1962 Omega 2":"FRAGMENT","1962 Omega 3":"FRAGMENT"},
        "un_omega1_initial_orbit":{
            "period_min":92.4,"perigee_km":367,"apogee_km":408,"inclination_deg":82.1,
            "epoch_instrumental_utc":None},
        "un_omega1_decay_report":{"field_heading":"Decay before",
            "cutoff_calendar_day":"1963-10-31","event_utc_time":None},
        "nasa_1963":{"printed_name":"OMEGA 1","printed_decay_days":[x.isoformat() for x in days],
                     "norad_id_printed":None},
        "nominal_calendar_labels_consistent":True,
        "date_alignment_is_calibrated_utc_interval":False,
        "same_name_implies_same_object_across_editions":False,
        "independent_terminal_holdouts_added":0,
        "identity_probability":None,
        "terminal_sigma_hours":None,
        "historical_mcmc":"NOT_RUN",
        "active_constraint_528":False,
        "impact_geography":None,
        "next_discriminant":"Obtain facsimile A/AC.105/INF.054 and direct NORAD crosswalk with sensor, epoch and UTC convention",
    }

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--record",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    x=assess(json.loads(args.record.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("R66: UN Omega role gate; zero calibrated terminal observations")

if __name__ == "__main__":
    main()
