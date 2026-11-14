#!/usr/bin/env python3
"""C241-L61: verify P-17 1963 WWV->A.1 piecewise convention without fabricating UTC/528 data."""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
LEDGER = BASE / "research/tle_custody/sao_p17_nov_clock_C241-L61.json"
SHA = "6b77e832e4273f7781cb61bfea7d38685c99d63e2f6b370a76d0b28a225ddf86"
SIZE = 10988993
MJD_START, MJD_CUT, MJD_END = Decimal("38030"), Decimal("38334"), Decimal("38395")
RATE = Decimal("0.001118458")
FIRST, SECOND = Decimal("2.292725"), Decimal("2.392725")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def a1_minus_wwv(mjd):
    """Seconds in published P-17 convention. NOT a UTC transformation."""
    if isinstance(mjd, bool) or isinstance(mjd, float):
        raise ValueError("MJD must be exact decimal, int or string")
    try:
        t = Decimal(str(mjd))
    except InvalidOperation as exc:
        raise ValueError("invalid MJD") from exc
    require(t.is_finite() and MJD_START <= t < MJD_END, "MJD outside printed P-17 interval")
    intercept = FIRST if t < MJD_CUT else SECOND
    return intercept + RATE * (t - MJD_START)

def check(data):
    require(data["id"] == "C241-L61" and data["type"] == "HistoricalClockConvention", "unexpected id/type")
    src = data["source"]
    require(src["ntrs"] == "19680020675" and src["sha256"] == SHA, "source identity drift")
    require(src["pdf_bytes"] == SIZE and src["pdf_pages"] == 176, "source byte/page drift")
    require(src["prior_manifest"].endswith("C241-L44.json"), "missing original manifest")
    require(src["visual_pages"] == [
       {"pdf_page_1based":7,"printed_page":3,"claim":"ramos temporais e frame FK4 1950.0"},
       {"pdf_page_1based":9,"printed_page":5,"claim":"estacoes e coordenadas em SAO Standard Earth"}],
       "page provenance changed")
    m = data["model"]
    require(m["time_scale_output"] == "smoothed preliminary A.1", "wrong time scale")
    require(m["time_scale_input"] == "WWV emitted" and m["unit"] == "seconds", "wrong input/units")
    require(m["mjd_reference"] == "38030.0" and m["slope_seconds_per_day"] == str(RATE), "wrong slope/reference")
    require([ (x["start_mjd"],x["end_mjd_exclusive"],x["intercept_seconds"]) for x in m["branches"]] ==
       [("38030.0","38334.0","2.292725"),("38334.0","38395.0","2.392725")], "invalid segment bounds/offsets")
    require(m["boundary_mjd"] == "38334.0" and m["intercept_difference_seconds"] == "0.100000", "invalid boundary delta")
    require(m["observed_target_528"] is False and m["utc_conversion_proven"] is False, "invented measurement/UTC")
    require(data["target_in_p17_published_sample"] is False and data["source_family"] == "SAO_PHOTOREDUCTION_PUBLICATIONS", "scope/family drift")
    require(data["geodetic_reference"].startswith("SAO Standard Earth"), "geodesy scope drift")
    require(data["station_table_context"] == [
       {"station_id":9008,"site":"Shiraz, Iran","x_Mm":"3.376882","y_Mm":"4.403985","z_Mm":"3.136254"},
       {"station_id":9114,"site":"Cold Lake, Canada","x_Mm":"-1.264846","y_Mm":"-3.466880","z_Mm":"5.185464"}], "station table mutation")
    for field in ("input_528_observation","station_for_528","epoch_utc_528","covariance_528"):
        require(data[field] is None, "invented 528 observation: "+field)
    require(data["independent_528_observations_added"] == 0, "invented independent sensor")
    require(data["hard_constraints_activated"] == 0 and data["physical_model_modified"] is False, "premature physics")
    require(data["status"] == "CONTEXT_CLOCK_CONVENTION_ONLY_NOT_APPLIED_TO_528", "scope promotion")
    require(a1_minus_wwv("38341.0") == Decimal("2.740565438"), "wrong 8 November convention")
    return {"status":"PASS_SOURCE_LOCKED_CONTEXT_ONLY","boundary":"1963-11-01","time_scale":"A.1 minus WWV, not UTC","activated_528_constraints":0}

def verify_pdf(path):
    content = Path(path).read_bytes()
    require(len(content) == SIZE and hashlib.sha256(content).hexdigest() == SHA, "original PDF bytes/hash mismatch")
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    require(len(reader.pages) == 176, "PDF page count mismatch")
    page3 = (reader.pages[6].extract_text() or "").lower()
    page5 = (reader.pages[8].extract_text() or "").lower()
    require("wwv" in page3 and "1963" in page3 and "1950" in page3, "clock page missing")
    require("shiraz" in page5 and "cold lake" in page5, "station table missing")
    return {"pdf_bytes":len(content),"sha256":SHA,"pdf_pages":len(reader.pages),"page3":"PASS","page5":"PASS"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path)
    p.add_argument("--mjd")
    args=p.parse_args()
    out=check(json.loads(LEDGER.read_text(encoding="utf-8")))
    if args.pdf: out["original_pdf"]=verify_pdf(args.pdf)
    if args.mjd is not None: out["a1_minus_wwv_seconds"]=str(a1_minus_wwv(args.mjd))
    print(json.dumps(out,sort_keys=True,ensure_ascii=False))
if __name__ == "__main__": main()
