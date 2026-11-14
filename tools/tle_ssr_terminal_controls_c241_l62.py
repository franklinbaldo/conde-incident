#!/usr/bin/env python3
"""C241-L62: verify NASA SSR catalogue-day controls, never fabricate UTC terminal times."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_terminal_controls_C241-L62.json"
PIN = "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d"
NULL_FIELDS = ("terminal_utc","terminal_interval_utc","station","frame","measurement_error","original_instrument_log")
PINNED = ((292,"1962 SIGMA 1","1962-018A","15 MAY","26 NOV 63","1963-11-26"),(565,"1963 9B","1963-009B","3 APR","24 NOV 63","1963-11-24"))

def reject_duplicates(pairs):
    d = {}
    for k,v in pairs:
        if k in d:
            raise ValueError(f"duplicate JSON key: {k}")
        d[k]=v
    return d

def load(path=LEDGER):
    return json.loads(Path(path).read_text(encoding="utf-8"),object_pairs_hook=reject_duplicates)

def validate(data):
    if data.get("id") != "C241-L62": raise ValueError("ledger identity")
    s=data.get("source",{})
    for key,val in {
        "ntrs_id":"19640002493","publication_date":"1963-11-30",
        "pdf_bytes":1266393,"pdf_sha256":PIN,"pdf_page_index":9,
        "printed_page":8,"time_resolution":"CALENDAR_DAY_ONLY",
        "compiled_data_is_independent_instrumental_observation":False,
        "same_pdf_as_existing_C241_L18":True,
    }.items():
        if type(s.get(key)) is not type(val) or s.get(key)!=val: raise ValueError(f"source {key}")
    if s.get("pdf_url")!="https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf": raise ValueError("source URL")
    if "DECAYED OBJECTS LIST" not in s.get("heading",""): raise ValueError("heading")
    rows=data.get("controls",[])
    if len(rows)!=2: raise ValueError("control count")
    for row,pin in zip(rows,PINNED):
        num,printed,modern,launch,day,normalized=pin
        for key,val in {"norad_id":num,"printed_designation":printed,
                        "modern_designator":modern,"printed_launch":launch,
                        "printed_source":"US","printed_decay_day":day,
                        "catalog_decay_date":normalized,
                        "kind":"CONTEMPORARY_COMPILED_CATALOG_DAY"}.items():
            if type(row.get(key)) is not type(val) or row.get(key)!=val:
                raise ValueError(f"control {num}: {key}")
        if row.get("secondary_crosswalk_url")!=f"https://keeptrack.space/satellite/{num}":
            raise ValueError("crosswalk source")
        for key in NULL_FIELDS:
            if key not in row or row[key] is not None: raise ValueError(f"fabricated {key}")
    pending=data.get("unresolved",[])
    if len(pending)!=2 or [x.get("norad_id") for x in pending]!=[308,668]:
        raise ValueError("unresolved set")
    for row in pending:
        if row.get("primary_terminal_time_status")!="NOT_RECOVERED" or row.get("terminal_utc") is not None:
            raise ValueError("unresolved promoted to measurement")
    if data.get("inference")!={"independent_sensor_count_added":0,"terminal_timestamp_measurements_added":0,
                                "physical_domain_effect":"NONE","NORAD_528_constraints_added":0}:
        raise ValueError("inference physically promoted")
    return True

def verify_pdf(path):
    b=Path(path).read_bytes()
    if len(b)!=1266393 or hashlib.sha256(b).hexdigest()!=PIN:
        raise ValueError("original PDF bytes/hash drift")
    if not b.startswith(b"%PDF-"):raise ValueError("not PDF")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",type=Path)
    args=p.parse_args()
    validate(load())
    if args.pdf: verify_pdf(args.pdf)
    print("C241-L62 VERIFIED: 2 catalogue days, 0 terminal UTC, 0 instrument records")

if __name__=="__main__":
    main()
