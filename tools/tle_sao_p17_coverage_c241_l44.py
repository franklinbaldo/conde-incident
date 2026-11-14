#!/usr/bin/env python3
"""C241-L44: scope-lock the SAO P-17 catalogue; never infer unseen measurements."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[1]
LEDGER = BASE / "research/tle_custody/sao_p17_oct_dec_1963_scope_C241-L44.json"
EXPECTED = (
    "1959 Alpha 1", "1959 Eta 1", "1960 Iota 2",
    "1961 Omicron 1", "1961 Omicron 2", "1961 Alpha Delta 1",
    "1962 Alpha Epsilon 1", "1962 Beta Mu 1", "1962 Beta Upsilon 1",
    "1963 13A", "1963 26A",
)
TARGETS = ("1963-003A", "1963-003B", "1963-003C")
SHA256 = "6b77e832e4273f7781cb61bfea7d38685c99d63e2f6b370a76d0b28a225ddf86"
BYTES = 10988993
URL = "https://ntrs.nasa.gov/api/citations/19680020675/downloads/19680020675.pdf"

def read_ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))

def check(model):
    source = model["source"]
    require = lambda condition, message: condition or (_ for _ in ()).throw(ValueError(message))
    require(model["id"] == "C241-L44", "wrong evidence id")
    require(model["type"] == "HISTORICAL_CATALOG_SCOPE_AUDIT", "wrong type")
    require(source["ntrs_id"] == "19680020675" and source["url"] == URL, "wrong NTRS source")
    require(source["sha256"] == SHA256 and source["bytes"] == BYTES, "uncertified bytes")
    require(source["pages"] == 176, "page count changed")
    require(source["published"] == "1968-05-14", "report date changed")
    require(source["observations_interval"] == ["1963-10-01","1963-12-31"], "coverage changed")
    require(tuple(model["included_designations"]) == EXPECTED, "printed scope changed")
    require(model["included_counts"] == [425,562,937,181,133,2246,524,1041,158,612,364], "counts changed")
    require(tuple(model["researched_objects"]) == TARGETS, "target identities changed")
    require(not set(TARGETS) & set(model["included_designations"]), "unexpected matched target")
    require(model["observed_targets_in_this_publication"] == [], "fabricated observation")
    require(model["inference"] == "SELECTIVE_PUBLISHED_CATALOG_EXCLUDES_TARGETS_NOT_ALL_OBSERVATIONS", "false global negative")
    for key in ("station_for_527_528_529","epoch_utc_for_527_528_529",
                "raw_measurements_for_527_528_529","orbital_covariance_for_527_528_529"):
        require(model[key] is None, "fabricated target datum: "+key)
    require(model["independent_target_measurements_recovered"] == 0, "invented sensor")
    require(model["physical_constraints_activated"] == 0, "premature physical constraint")
    require(model["conde_impact_location"] == "INDETERMINATE", "fabricated impact")
    require(model["context_not_target_sigma"]["position_rms_for_printed_rows_arcsec"] == 4, "context sigma changed")
    require(model["time_reference"].startswith("Smoothed preliminary A.1"), "A.1/UTC confusion")
    return {"id":model["id"],"status":"PASS_SCOPE_ONLY","included_satellites":len(EXPECTED),"528_observations":0,"physical_constraints":0}

def live_check(pdf):
    if len(pdf) != BYTES or hashlib.sha256(pdf).hexdigest() != SHA256:
        raise ValueError("PDF bytes/sha mismatch: investigate source drift, do not silently update")
    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(pdf)).pages
    if len(pages) != 176:
        raise ValueError("PDF page count mismatch")
    toc = pages[2].extract_text() or ""
    overview = pages[5].extract_text() or ""
    method = pages[6].extract_text() or ""
    if toc.count("Observations of Satellite") != 11:
        raise ValueError("TOC item count mismatch")
    for s in ("1959 Alpha 1","1963 13A","1963 26A"):
        if s not in toc: raise ValueError("TOC missing "+s)
    for s in ("425 observations","364 observations"):
        if s not in overview: raise ValueError("intro count missing "+s)
    for s in ("smoothed preliminary A. 1","1950. 0","station number","observation number"):
        if s not in method: raise ValueError("method missing "+s)
    if any(s in toc for s in ("1963 03A","1963 03B","1963 03C")):
        raise ValueError("target in printed TOC: investigate before reporting")
    return {"pdf_pages":len(pages),"source_hash":SHA256,"scoped_objects":11,"target_observations_extracted":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--live",action="store_true")
    args=p.parse_args()
    output=check(read_ledger())
    if args.live:
        req=Request(URL,headers={"User-Agent":"Conde1963-Research-Custody/1.0"})
        with urlopen(req,timeout=45) as response: pdf=response.read(20_000_000)
        output["live"]=live_check(pdf)
    print(json.dumps(output,sort_keys=True))
if __name__=="__main__": main()
