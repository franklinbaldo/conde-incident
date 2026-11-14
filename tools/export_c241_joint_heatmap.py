#!/usr/bin/env python3
"""Export a small loss-bounded 20x20 heatmap for Rust SSG/static readers.

All values are integer fixed-point probabilities to avoid 20KB file sprawl.
The source is Python's per-trajectory J2+NASA-day scenario model, NOT
historical fragment-impact locations.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

SCALE=1e-10
LABELS=("baseline","orbital_middle","temporal_12h","joint_middle_12h")

def encode(summary:dict, rows:list[dict]) -> dict:
    assert summary["schema"]=="conde.c241-joint-orbital-day-scenario-heatmap/v1"
    assert summary["sample"]["n"]==1_500_000
    assert summary["historical_Conde_impact_posterior"] is None
    assert len(rows)==400
    encoded={}
    for label in LABELS:
        vals=[int(round(float(r[label+"_global_probability"])/SCALE)) for r in rows]
        assert all(v>=0 for v in vals)
        reconstructed=sum(vals)*SCALE
        expected=summary["results"][label]["probability_within_2000km"]
        assert abs(reconstructed-expected)<2e-8
        encoded[label]=vals
    return {
        "schema":"conde.static-joint-orbit-day-heatmap/v1",
        "experiment_id":summary["id"],
        "title":"C241 NORAD 528 | same-draw J2/day-label scenario",
        "source":"SECONDARY_TLE_PLUS_NASA_C197_DAY_LABEL",
        "source_not_instrumentally_independent":True,
        "n":summary["sample"]["n"],
        "random_seed":summary["sample"]["seed"],
        "coordinate_system":"SPHERICAL_AZIMUTHAL_EQUIDISTANT_ABOUT_CONDE_BA",
        "center_lat_lon_deg":[-11.8139,-37.6108],
        "grid":{"side_cells":20,"cell_km":200,
                "x_east_centers_km":list(range(-1900,2000,200)),
                "y_north_centers_km":list(range(-1900,2000,200)),
                "flattening":"row-major: south to north, west to east",
                "radius_of_interest_km":2000},
        "probability_unit":SCALE,
        "denominator":"all global subpoints, including outside circle",
        "within_2000km_probability":{
            k:summary["results"][k]["probability_within_2000km"] for k in LABELS},
        "maps_fixed_point_global_probability":encoded,
        "temporal_sigma_hours_assumed":12,
        "orbital_sigma_hypothesis":"middle",
        "historical_impact_posterior":None,
        "physical_reentry_propagated":False,
        "fragment_survival_or_ablation_calculated":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--cells",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    summary=json.loads(a.summary.read_text())
    with a.cells.open(newline="") as f:
        cells=list(csv.DictReader(f))
    result=encode(summary,cells)
    data=json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
    assert len(data.encode("utf-8"))<20_000, "static-data file limit"
    if a.check:
        assert a.output.read_text(encoding="utf-8")==data, "committed heatmap drift"
        print("C241 static site heatmap parity PASS")
    else:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(data,encoding="utf-8")
        print("C241 site heatmap generated, bytes="+str(len(data.encode("utf-8"))))

if __name__=="__main__":
    main()
