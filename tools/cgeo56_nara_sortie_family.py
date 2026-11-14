#!/usr/bin/env python3
"""CGEO-56: source-hash and cross-square header joins with explicit unknowns."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = Path(__file__).resolve().parents[1] / "research/geo/cgeo56_nara_sortie_cross_square.json"
BASE = "https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-"
ROWS = {
 "00248": ("11S037W",2519162,"21016e6c141d5ac495893e13bc9a4b01bbf992e596416054fd0c03c164f3d2a0","125374","ROLL 601 2-3017","7, 14, 18, 20 SEP 42",True),
 "00431": ("12S037W",2487325,"b4422aad1d0ca1a53dbb762c20e653cb34c42785abcd4e162e3f943300c6227d","125374","ROLL 601 2-3017","7, 14, 18, 20 SEP 42",True),
 "00247": ("11S037W",2497049,"b671f0378e2b57502f616be5aaa57ae45041048aa576bbf04c6eed9a6843a404","125370","ROLL 502 2-3017","27 SEP 42",False),
 "00432": ("12S037W",2420414,"fcd14c0cd438c40e4ce6733c896869d12e8899e31d2cf9c5cb62ce03ba4af6b9","125370","ROLL 502 2-3017","27 SEP 42",False),
}
NOTES = {"00248":"ROLL 1 / ROLL 2","00431":"ROLL 4","00247":"ROLL 1 / ROLL 2","00432":"ROLL 2"}
PAIRS = (("125374",("00248","00431"),"ROLL 601 2-3017","7, 14, 18, 20 SEP 42"),
         ("125370",("00247","00432"),"ROLL 502 2-3017","27 SEP 42"))
NULLS = ("verified_spot_number","negative_can","individual_exposure_utc",
         "roll_to_exposure_mapping","footprint_georeferenced",
         "conde_1963_city_center","alleged_fall_location")

def need(expr, why):
    if not expr: raise ValueError(why)

def validate(d):
    need((d.get("schema"),d.get("id"),d.get("parent")) ==
         ("conde.cgeo.nara-flight-header-pairs/v1","CGEO-56","CGEO-55"),"lineage")
    need(d.get("source") == "NARA RG373, series 306062, microfilm M1765, reel 317, file units 46716637 and 46716877","source")
    need(d.get("method") == "Human reading of full-resolution original JPEG headers and plotting symbols; no OCR; no georeferencing","method")
    scans=d.get("scans")
    need(isinstance(scans,list) and [s.get("sheet") for s in scans]==list(ROWS),"scans/order")
    for s in scans:
        k=s["sheet"]; sq,size,sha,op,org,date,frame=ROWS[k]
        need(tuple(s.get(f) for f in ("square","bytes","sha256","op_file_no",
              "orgn_sortie_reading","header_date_reading","frame_label_16_visible")) ==
             (sq,size,sha,op,org,date,frame),"header or custody "+k)
        need(s.get("header_reading_status")=="provisional","certainty "+k)
        need(s.get("additional_visible_note")==NOTES[k],"roll annotation "+k)
    pairs=d.get("pairs")
    need(isinstance(pairs,list) and len(pairs)==2,"pairs")
    for pair,(op,sheets,org,date) in zip(pairs,PAIRS):
        need((pair.get("op_file_no"),pair.get("sheets"),
              pair.get("shared_orgn_sortie_reading"),pair.get("shared_date_header_reading")) ==
             (op,list(sheets),org,date),"pair identity")
        need(pair.get("interpretation") ==
             "multi-field same-flight-family candidate, not a validated common photo or spot","overclaim")
        need(all(next(s for s in scans if s["sheet"]==k)["op_file_no"]==op
                 for k in sheets),"cross-square source mismatch")
        need(len({next(s for s in scans if s["sheet"]==k)["square"] for k in sheets})==2,"not cross-square")
    need(d.get("cross_sheet_frame_label_example")=={
        "frame_label":"16","sheets":["00248","00431"],
        "meaning":"same written number in different index sheets; does not establish an identical photographic frame or physical film roll"},"reused frame label overclaim")
    need(d.get("counts")=={"header_records":4,"multi_field_cross_square_pairs":2,
         "original_individual_aerial_photographs_acquired":0,
         "demonstrated_1963_ground_control_points":0},"counts")
    lim=d.get("limits",{})
    need(all(k in lim and lim[k] is None for k in NULLS),"unproven bridge")
    need(lim.get("orbital_constraint_activated") is False,"false orbital constraint")
    return len(scans)

def live():
    for k,(_,size,sha,*rest) in ROWS.items():
        with urlopen(Request(BASE+k+".jpg",headers={"User-Agent":"Conde-CGEO56/1.0"}),timeout=90) as r:
            need(r.status==200,"HTTP "+k)
            need(r.headers.get("Content-Type","").split(";")[0].strip().lower() in
                 ("image/jpeg","image/jpg","application/octet-stream"),"MIME "+k)
            data=r.read(size+1)
        need(len(data)==size,"bytes "+k)
        need(data[:3]==b"\\xff\\xd8\\xff" and data[-2:]==b"\\xff\\xd9","JPEG boundaries "+k)
        need(hashlib.sha256(data).hexdigest()==sha,"SHA256 "+k)
        print("CGEO56_JPEG_PASS",k,len(data),sha)
    print("CGEO56_NARA_ALL_FOUR_PASS")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--live",action="store_true")
    args=parser.parse_args()
    print("CGEO56_CONTRACT_PASS",validate(json.loads(SOURCE.read_text(encoding="utf8"))))
    if args.live: live()
