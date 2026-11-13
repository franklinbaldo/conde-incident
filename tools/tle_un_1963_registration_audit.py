#!/usr/bin/env python3
"""C241-L33: audited UN archival registry bridge; no time-of-impact inference."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "research/tle_custody/un_1963_registration_C241-L33.json"
NASA77 = "research/tle_custody/nasa_ssr_dec1977_528_identity_C241-L32.json"
NASA63 = "research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json"

SOURCES = {
    "30": (189499,"fbee0e928a2d81e62c97c102eef70d4f4931dd500372a4bf735bd8891c6188b8","1963-03-13","1963-03-12","2400Z 31 JANUARY 1963"),
    "53": (850470,"1439a1c1ec49b3922bb7f86e4b868b8ab8a1c9e34e34803b78c1aea2c541c84c","1963-12-31","1963-12-20","2400Z 15 NOVEMBER 1963"),
    "54": (377974,"8a67ca12769e935877429125a6d446f4e04189698d0e356536f588fef507acf4","1963-12-31","1963-12-20","2400Z 31 OCTOBER 1963"),
    "55": (286501,"2f69e814a277e3a5fae8b27db8f7566f39a401a8089f1287dbea65d47b94cbcd","1963-12-31","1963-12-20","2400Z 15 OCTOBER 1963"),
}
ROWS = [
    ("1963-3-A",527,"A","94.7","81.97","518.6","479.5"),
    ("1963-3-B",528,"D","94.5","81.97","505.5","476.4"),
    ("1963-3-C",529,"D","94.7","81.97","525.5","476.4"),
]

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def validate(m, nasa77, nasa63):
    need(m["schema"]=="conde.c241-l33-un-1963-registration/v1" and m["id"]=="C241-L33","schema/id")
    need(m["source_role"]=="ORIGINAL_US_GOVERNMENT_REGISTRATION_TO_UN_NOT_INDEPENDENT_SENSOR", "source grade")
    docs=m["docs"]
    need([d["number"] for d in docs]==["30","53","54","55"],"source completeness/order")
    for d in docs:
        b,h,day,letter,cutoff = SOURCES[d["number"]]
        need(d["url"]==f"https://www.unoosa.org/documents/pdf/inf{d['number']}E.pdf"
             and d["bytes"]==b and d["sha256"]==h
             and d["document_day"]==day and d["letter_day"]==letter
             and d["report_cutoff_printed"]==cutoff
             and d["relevant_pdf_page_index"]==1 and d["pdf_pages"]==2
             and d["visual_check"]=="MANUAL_IMAGE_INSPECTION_2026-11-13",
             f"source/byte/cutoff mismatch INF{d['number']}")
    jan=docs[0]
    need(jan["kind"]=="JAN31_FULL_NEW_REGISTRATION" and len(jan["printed_rows"])==3,
         "initial UN registration")
    for row,pin in zip(jan["printed_rows"],ROWS):
        designator,norad,cat,period,inc,apo,peri=pin
        need(row["printed_designator"]==designator
             and row["norad_from_nasa_1977"]==norad
             and row["category"]==cat
             and row["launch_vehicle"]=="THOR AGENA"
             and row["launch_day"]=="1963-01-16"
             and row["nodal_period_min_printed"]==period
             and row["inclination_deg_printed"]==inc
             and row["apogee_km_printed"]==apo
             and row["perigee_km_printed"]==peri,
             "UN Jan31 printed cell altered")
    nov=docs[1]
    need(nov["kind"]=="NOV15_INCREMENTS_AND_DELETIONS"
         and nov["printed_no_longer_in_orbit"]==["1963-3B","1963-35A"],
         "UN Nov15 reported status")
    need(docs[2]["kind"]=="OCT31_INCREMENT_ONLY_CONTROL"
         and docs[2]["printed_no_longer_in_orbit"]==["1962 Omega 1"]
         and docs[2]["contains_1963_3B_in_deletions"] is False
         and docs[3]["kind"]=="OCT15_INCREMENT_ONLY_CONTROL"
         and docs[3]["printed_no_longer_in_orbit"]==["1963-37A"]
         and docs[3]["contains_1963_3B_in_deletions"] is False,
         "incremental-control omission wrongly promoted")
    need(nasa77["row"]["international_designator_printed"]=="1963 003B"
         and nasa77["row"]["catalog_number_printed"]==528
         and nasa77["row"]["identity_match"]=="DIRECT_VISUAL_VERIFIED"
         and [(c["international_designator_printed"],c["catalog_number_printed"])
              for c in nasa77["control_rows"]]==[("1963 003A",527),("1963 003C",529)],
         "retrospective NORAD crosswalk changed")
    need(nasa63["sources"][0]["human_table_observation"]["object_printed"]=="1963 3B"
         and nasa63["sources"][0]["human_table_observation"]["decay_day"]=="1963-11-08",
         "NASA Nov15 catalog-day connection changed")
    x=m["interpretation"]; g=m["graph_extension"]
    need(x["identity_crosswalk_source"]==NASA77
         and x["nasa_source_occurrence"]=="C197#1"
         and x["printed_event_date_nasa_1963"]=="1963-11-08"
         and x["jan31_state_528"]=="REGISTERED_IN_ORBIT_AT_JAN31_ADMINISTRATIVE_CUTOFF"
         and x["nov15_state_528"]=="REPORTED_NO_LONGER_IN_ORBIT_BY_NOV15_ADMINISTRATIVE_CUTOFF",
         "crosswalk or status model")
    need(x["un_cutoff_is_sensor_epoch"] is False
         and x["un_cutoff_is_verified_decay_time"] is False
         and x["conditional_physical_interval_activated"] is False
         and x["controls_54_55_constrain_survival"] is False
         and x["publication_order_is_cutoff_order"] is False
         and all(x[k] is None for k in
           ("historical_sensor_528","observation_epoch_528","state_fit_covariance_528",
            "decay_time_uncertainty_528","raw_line1_line2_528"))
         and x["physical_constraints_activated"]==0
         and x["independent_sensor_observations_added"]==0
         and x["lean_activated"] is False,
         "unverified physical constraint or sensor inferred")
    need(g["parent"]=="research/constraints/nasa_528_decay_precision_C197_20261113.json"
         and g["requires"]==[NASA77,NASA63]
         and len(g["edges"])==6
         and all(edge["activation"] in
             ("DOCUMENTARY_ONLY","NO_NEGATIVE_SENSOR_EVIDENCE","CATALOGUE_BRIDGE",
              "NO_INDEPENDENT_MEASUREMENT") for edge in g["edges"])
         and g["physical_domain_reduced"] is False
         and g["simulation_run"] is False,
         "wrong graph status")
    return {
        "source_count":len(docs), "jan31_registered_objects":[527,528,529],
        "528_period_jan31_printed_minutes":"94.5",
        "nov15_528_no_longer_in_orbit_reported":True,
        "nasa_reported_decay_day":"1963-11-08",
        "independent_sensor_observations_added":0,
        "physical_constraints_activated":0,
        "cumulative_edges":6, "status":"DOCUMENTARY_STATUS_BRIDGE_ONLY",
    }

def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def check_pdf_bytes(model, pdf_directory):
    for d in model["docs"]:
        path=Path(pdf_directory)/f"inf{d['number']}E.pdf"
        raw=path.read_bytes()
        need(raw.startswith(b"%PDF-"),"not a PDF")
        need(len(raw)==d["bytes"] and hashlib.sha256(raw).hexdigest()==d["sha256"],
             f"UN official PDF bytes changed: INF{d['number']}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf-dir")
    p.add_argument("--output")
    args=p.parse_args()
    m=read(MODEL)
    report=validate(m,read(NASA77),read(NASA63))
    if args.pdf_dir:
        check_pdf_bytes(m,args.pdf_dir)
        report["pdf_sources_byte_verified"]=4
    out=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output: Path(args.output).write_text(out,encoding="utf-8")
    print(out,end="")

if __name__=="__main__":
    main()
