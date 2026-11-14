#!/usr/bin/env python3
"""C241-L46: checksum replay, no transfer of 1963-044 timing to 1963-003B."""
import argparse, hashlib, json, pathlib, urllib.request

PATH=pathlib.Path(__file__).resolve().parents[1]/"research/tle_custody/norad_spadats_context_C241-L46.json"
SOURCES=("C241-L46-D07","C241-L46-D08")
EXPECTED_HASHES=("b1d6a37572e6c7ffa806f07f30ae714730a8d17724942638ac591c661bef97fe","65452b827428bdbef37bf96fb915a1411c2798d5a16939d845abe561aa12e13e")
EXPECTED_SIZES=(929016,520901)

def no_dupes(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError("duplicate JSON key: "+key)
        result[key]=value
    return result

def load(path=PATH):
    return json.loads(pathlib.Path(path).read_text(),object_pairs_hook=no_dupes)

def verify_ledger(d):
    if set(d)!={"schema","epistemic_status","lineage","target","sources","next_search"}: raise ValueError("unexpected ledger schema")
    if d["schema"]!="c241-l46-norad-spadats-context-v1" or d["epistemic_status"]!="CONTEXT_ONLY_NOT_ACTIVATED": raise ValueError("incorrect epistemic scope")
    t=d["target"]
    if set(t)!={"norad","designator","observation_utc","station","frame","sigma","decay_hour_utc","reentry_location","activation"}:raise ValueError("target schema")
    if t["norad"]!=528 or t["designator"]!="1963-003B" or t["activation"] is not False or any(t[k] is not None for k in ("observation_utc","station","frame","sigma","decay_hour_utc","reentry_location")):raise ValueError("unsupported 528 constraint")
    if len(d["sources"])!=2:raise ValueError("source count")
    for i,s in enumerate(d["sources"]):
        if set(s)!={"id","url","landing","sha256","bytes","pages","document_date","message","object_ids","launch","findings","decay_window","measurement_528"}:raise ValueError("source schema")
        if s["id"]!=SOURCES[i] or s["sha256"]!=EXPECTED_HASHES[i] or s["bytes"]!=EXPECTED_SIZES[i]:raise ValueError("source lock mismatch")
        if s["object_ids"]!=[687,688] or s["launch"]!="1963-044" or s["measurement_528"] is not None:raise ValueError("incorrect crosswalk")
        if not s["url"].startswith("https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/") or not s["url"].endswith(("07.pdf" if i==0 else "08.pdf")):raise ValueError("source URL")
        if not s["findings"] or any(f["page_index"]<0 or f["page_index"]>=s["pages"] for f in s["findings"]):raise ValueError("page reference")
    if d["sources"][0]["decay_window"] is not None:raise ValueError("earlier source acquired later interval")
    if d["sources"][0]["message"]!="AF IN 20080" or d["sources"][1]["message"]!="AF IN 23784 (corrected copy of AF IN 22976)":raise ValueError("message identity")
    if d["sources"][1]["decay_window"]!={"object_id":688,"date_utc":"1963-11-12","start":"2210Z","end":"2400Z","kind":"REPORTED_INTERVAL_FOR_DIFFERENT_OBJECT_NOT_SIGMA"}:raise ValueError("window misattributed")
    return True

def verify_pdf(src, data):
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-100:]:raise ValueError("invalid PDF")
    if len(data)!=src["bytes"] or hashlib.sha256(data).hexdigest()!=src["sha256"]:raise ValueError("source bytes drifted")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--verify-remote",action="store_true")
    args=p.parse_args()
    d=load();verify_ledger(d)
    if args.verify_remote:
        for s in d["sources"]:
            request=urllib.request.Request(s["url"],headers={"User-Agent":"Conde-custody/1.0"})
            with urllib.request.urlopen(request,timeout=40) as response:verify_pdf(s,response.read())
            print(s["id"],"source checksum PASS")
    print("C241-L46 scope PASS; no NORAD 528 instrumental data promoted")
if __name__=="__main__":main()

