#!/usr/bin/env python3
"""C241-L56: auditable PARL/Cold Lake distinction from an already-custodied PDF."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "research/tle_custody/norad_parl_cold_lake_addendum_C241-L56.json"
PARENT = ROOT / "research/tle_custody/norad_1963_spadats_operational_C241-L52.json"
PARENT_SHA = "59de53b50a29c23c5d286b59b72591ee51efb055081f9fd57c29fe3aea8154eb"
PDF_SHA = "eb8682425a393b016642165a9c00b6be8868a27954ddd0e55c40c1e14da425b4"
URL = "https://documents.theblackvault.com/documents/afhistory/norad/%28U%29%201963%20NORAD%20CONAD%20History%20Jul-Dec.pdf"
ROWS = [
    ("COLD_LAKE_CONTROL",70,55,
     "RCAF ADC put the camera at Cold Lake under the operational control of CINCNORAD",
     "Institutional control of Cold Lake optical camera by end-1962, not proof of 528 measurements"),
    ("PRINCE_ALBERT_PART_TIME",72,57,
     "supplied information to SPADATS on a part-time basis",
     "PARL radar supplied some information to SPADATS, unspecified target and clock"),
    ("PRINCE_ALBERT_JAN1964",72,57,
     "PARL was still providing information to SPADATS",
     "Report's January 1964 administrative status, not a 1963 individual observation or uninterrupted service")
]
SCOPE = dict.fromkeys(("named_527","named_528","named_529","utc_528","station_of_528",
                       "frame_528","sigma_528","data_receipt_528","independent_sensors_528",
                       "decay_hour_528","fall_location_528"))
SCOPE.update(physical_constraint_active=False,theta="THETA_UNCHANGED")
EXPECTED = {
    "schema":"conde.c241-l56-parl-feed/v1","id":"C241-L56","parent_id":"C241-L52",
    "parent_sha256":PARENT_SHA,"source_url":URL,"source_sha256":PDF_SHA,
    "source_bytes":7111330,"source_pages":122,
    "source_independence":"SAME_BINARY_AS_C241-L52_NOT_NEW_SOURCE_OR_SENSOR",
    "anchors":[{"id":i,"pdf_page_zero_based":p,"printed_page":q,"phrase":s,"scope":v}
               for i,p,q,s,v in ROWS],
    "distinction":"PARL at Prince Albert: DRB radar; Cold Lake: RCAF Baker-Nunn optical camera. Site reports are not independent 528 measurements.",
    "scope":SCOPE
}

def pairs_unique(pairs):
    result={}
    for k,v in pairs:
        if k in result: raise ValueError("duplicated JSON field")
        result[k]=v
    return result

def load(path=MODEL):
    return json.loads(Path(path).read_text("utf8"),object_pairs_hook=pairs_unique)

def audit(obj,parent=PARENT):
    if obj!=EXPECTED: raise ValueError("unsupported changed custody or inferred orbit")
    if hashlib.sha256(Path(parent).read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("source parent changed")
    return {"anchors":3,"physics":0}

def verify_pdf(raw):
    if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-2048:]:
        raise ValueError("invalid PDF signature/trailer")
    if len(raw)!=7111330 or hashlib.sha256(raw).hexdigest()!=PDF_SHA:
        raise ValueError("PDF bytes changed")
    from pypdf import PdfReader
    if len(PdfReader(io.BytesIO(raw)).pages)!=122: raise ValueError("pages changed")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-file",type=Path)
    p.add_argument("--live",action="store_true")
    args=p.parse_args()
    if args.live and args.source_file: p.error("only one mode")
    audit(load())
    if args.source_file: verify_pdf(args.source_file.read_bytes())
    if args.live:
        with urlopen(Request(URL,headers={"User-Agent":"Mozilla/5.0"}),timeout=100) as f:
            verify_pdf(f.read())
    print("C241-L56 PASS: PARL system-level data, no NORAD 528 observation")
if __name__=="__main__": main()
