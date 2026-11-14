"""Audit Smithsonian RU398 finding-aid source without source promotion."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/tle_custody/smithsonian_ru398_stl_index_C241_LONTRA_R55.json"
SHA="fa53dca4b1a819e45700dd88fc0858e0299ff0cc7a0e28f2364686de05eb5436"
ENTRIES=[
 (63,6,"TRW Space Log, Index, Volumes 1-5, undated","index_not_fascicle"),
 (63,8,"Soviet Space Log, 1957-1967, A Space Publication","separate_publication_not_soviet_sensor")
]

def audit(d):
    if d.get("id")!="C241-LONTRA-R55" or d.get("evidence_class")!="INSTITUTIONAL_FINDING_AID_PHYSICAL_LOCATORS":
        raise ValueError("record identity")
    if "C241-LONTRA-R52" not in d.get("predecessors",[]): raise ValueError("missing lineage")
    s=d.get("source",{})
    for k,v in {
        "institution":"Smithsonian Institution Archives",
        "pdf_url":"https://sirismm.si.edu/EADpdfs/SIA.FARU0398.pdf",
        "http_status":200,"mime":"application/pdf",
        "downloaded_bytes":233242,"sha256":SHA,"magic_and_eof":True,
        "printed_page":61,"pdf_page_one_based":63,"page_visually_checked":True,
        "finding_aid_integral_retrieved":True,"archival_folder_contents_retrieved":False
    }.items():
        if s.get(k)!=v:raise ValueError("invalid source "+k)
    ls=d.get("locators")
    if not isinstance(ls,list) or len(ls)!=2:raise ValueError("locator count")
    for x,expected in zip(ls,ENTRIES):
        if (x.get("box"),x.get("folder"),x.get("description"),x.get("material"))!=expected:
            raise ValueError("incorrect physical locator")
        if x.get("folder_item_read") is not False:raise ValueError("folder unread")
    c=d.get("conclusions",{})
    expected={
      "locators_found":2,"stl_vol3_no4_original_retrieved":False,
      "stl_vol3_no4_listed_within_index_confirmed":False,
      "stl_original_unit_legend_read":False,
      "soviet_log_1963_primary_observations_confirmed":False,
      "new_norad_527_528_529_measurements":0,
      "new_independent_sensors":0,
      "activated_orbital_constraints":0,
      "institutional_contacts_sent":0
    }
    if c!=expected:raise ValueError("unsupported epistemic promotion")
    return True

def replay(path):
    b=Path(path).read_bytes()
    return len(b)==233242 and b.startswith(b"%PDF-") and b.rstrip().endswith(b"%%EOF") and hashlib.sha256(b).hexdigest()==SHA

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path, required=True, help="original Smithsonian RU398 PDF; mandatory for custody gate")
    a=p.parse_args()
    audit(json.loads(SOURCE.read_text(encoding="utf-8")))
    if not replay(a.pdf):p.error("finding aid PDF mismatch")
    print("R55 OK: original finding aid PDF hash and size verified; physical folders not opened")
