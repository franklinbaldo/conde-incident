#!/usr/bin/env python3
"""Frozen-holdout effective-drag/J2 secondary-catalog screening, NOT a historical orbit."""
import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tools.cross_object_epoch_support import (
    read_pinned_csv, normalize, SOURCE_URL, SOURCE_SHA256, EXPECTED_CSV_SHA256,
)

ROOT=Path(__file__).resolve().parents[1]
SPLIT=ROOT/"research/statistics/raan_chronological_holdout_1963.json"
PRECISION=ROOT/"research/constraints/nasa_528_decay_precision_C197_20261113.json"
IDS=(527,528,529)
GRID_H=(30.,45.,60.,90.,120.)
MU,R,J2=398600.4418,6378.137,0.00108262668
REF_KM=400.
THRESHOLD_KM=120. # conditional, not NASA-recorded interface
START=datetime(1963,11,7,tzinfo=timezone.utc)
END=datetime(1963,11,9,tzinfo=timezone.utc)

def require(ok,why):
    if not ok: raise ValueError(why)

def iso(t):
    return t.isoformat(timespec="microseconds").replace("+00:00","Z")

def elapsed(a,b):
    return (a-b).total_seconds()/86400.

def altitude_proxy(n):
    require(math.isfinite(n) and n>0,"invalid mean motion")
    h=(MU/(2*math.pi*n/86400)**2)**(1/3)-R
    require(math.isfinite(h) and 0<h<10000,"invalid circular-altitude proxy")
    return h

def blocks(raw,manifest):
    require(manifest["schema"]=="conde.raan-chronological-split/v1" and
        manifest["independence_status"]=="SAME_SECONDARY_DOCUMENTARY_LINEAGE_NOT_INDEPENDENT",
        "frozen split/provenance")
    grouped,counts=normalize(raw)
    require([counts[i] for i in IDS]==[21,45,57],"frozen counts")
    out={}
    for sid in IDS:
        by={iso(r["epoch"]):r for r in grouped[sid]}
        membership=manifest["memberships"][str(sid)]
        require(set(membership)=={"fit","validation","evaluation"},"split blocks")
        keys=sum([membership[k] for k in ("fit","validation","evaluation")],[])
        require(len(keys)==len(set(keys))==len(by) and set(keys)==set(by),
                "missing or leaked epoch")
        named={}
        for k in ("fit","validation","evaluation"):
            named[k]=[]
            for stamp in membership[k]:
                r=by[stamp]
                named[k].append({
                    "t":r["epoch"],"rows":r["source_rows"],
                    "h":altitude_proxy(float(r["state"][5])),
                    "raan":float(r["state"][1]),
                    "i":float(r["state"][0]),"e":float(r["state"][2]),
                })
            require(len(named[k])>0 and all(a["t"]<b["t"]
                    for a,b in zip(named[k],named[k][1:])), "bad epoch chronology")
        require(len(named["fit"])>=3 and named["fit"][-1]["t"]<named["validation"][0]["t"] and
            named["validation"][-1]["t"]<named["evaluation"][0]["t"],"future leakage")
        out[sid]=named
    require(sum(len(v) for v in out[528].values())==45,"45 unique epochs")
    return out

def fit(rows,H):
    require(H in GRID_H,"H outside frozen grid")
    a=rows[-1]
    z0=math.exp((a["h"]-REF_KM)/H)
    den=num=0.
    for r in rows:
        t=elapsed(r["t"],a["t"])
        num+=t*(math.exp((r["h"]-REF_KM)/H)-z0)
        den+=t*t
    require(den>0,"empty FIT span")
    k=max(0.,-H*num/den)
    return {"H":H,"k":k,"z0":z0,"anchor":a}

def height_at(m,t,zero_drag=False):
    z=m["z0"]-(0 if zero_drag else m["k"])*t/m["H"]
    if z<=0:return None
    h=REF_KM+m["H"]*math.log(z)
    return h if math.isfinite(h) and h>0 else None

def raan_at(m,days,zero_drag=False):
    require(days>=0,"no backward J2 evaluation")
    anchor=m["anchor"]
    steps=max(1,math.ceil(days*4))
    step=days/steps
    delta=0.
    for j in range(steps):
        h=height_at(m,(j+.5)*step,zero_drag)
        if h is None:return None
        a=R+h
        rate=-1.5*J2*math.sqrt(MU/a**3)*(R/a)**2*math.cos(math.radians(anchor["i"]))/(1-anchor["e"]**2)**2
        delta+=math.degrees(rate*step*86400)
    return (anchor["raan"]+delta)%360

def evaluate(rows,m,zero_drag=False):
    ah,ar=[],[]
    for row in rows:
        t=elapsed(row["t"],m["anchor"]["t"])
        require(t>0,"holdout before FIT")
        h=height_at(m,t,zero_drag)
        r=raan_at(m,t,zero_drag)
        if h is not None and r is not None:
            ah.append(abs(h-row["h"]))
            ar.append(abs((row["raan"]-r+180)%360-180))
    return {
        "n":len(rows),"predicted_n":len(ah),
        "height_proxy_mae_km":round(sum(ah)/len(ah),6) if ah else None,
        "raan_mae_deg":round(sum(ar)/len(ar),6) if ar else None,
        "instrumentally_independent_holdout":False,
    }

def crossing(m):
    if m["k"]<=0:return None
    target=math.exp((THRESHOLD_KM-REF_KM)/m["H"])
    t=m["H"]*(m["z0"]-target)/m["k"]
    return m["anchor"]["t"]+timedelta(days=t) if math.isfinite(t) and t>=0 else None


def plane_angle_deg(i1, raan1, i2, raan2):
    """Angle between orbital plane normals; NOT physical distance of satellites."""
    require(all(math.isfinite(v) for v in (i1,raan1,i2,raan2))
            and 0<=i1<=180 and 0<=i2<=180,"invalid orbital plane")
    a,b=math.radians(i1),math.radians(i2)
    cospsi=math.cos(a)*math.cos(b)+math.sin(a)*math.sin(b)*math.cos(math.radians(raan1-raan2))
    return math.degrees(math.acos(max(-1.,min(1.,cospsi))))

def angular_pair_diagnostics(blocks,models,max_offset_hours=72):
    """Asynchronous catalog pairs. Never label as coepoch geometry or NASA sigma."""
    require(max_offset_hours==72,"pairing window is a query, not error")
    result={}
    for sid in (527,529):
        records=[]
        for target in blocks[528]["evaluation"]:
            peer=min(blocks[sid]["evaluation"],key=lambda r:
                     (abs((r["t"]-target["t"]).total_seconds()),r["t"]))
            delta=abs((peer["t"]-target["t"]).total_seconds())/3600.
            if delta>max_offset_hours:continue
            a,b=models[528],models[sid]
            ra=raan_at(a,elapsed(target["t"],a["anchor"]["t"]))
            rb=raan_at(b,elapsed(peer["t"],b["anchor"]["t"]))
            if ra is None or rb is None:continue
            obs=plane_angle_deg(target["i"],target["raan"],peer["i"],peer["raan"])
            pred=plane_angle_deg(a["anchor"]["i"],ra,b["anchor"]["i"],rb)
            ra_obs=(target["raan"]-peer["raan"]+180)%360-180
            ra_pred=(ra-rb+180)%360-180
            records.append({
                "target_epoch_utc":iso(target["t"]),
                "sibling_epoch_utc":iso(peer["t"]),
                "epoch_offset_hours_NOT_sigma":round(delta,6),
                "source_rows_528":target["rows"],
                "source_rows_sibling":peer["rows"],
                "observed_asynchronous_plane_angle_deg":round(obs,6),
                "modeled_asynchronous_plane_angle_deg":round(pred,6),
                "plane_angle_absolute_residual_deg":round(abs(obs-pred),6),
                "raan_contrast_absolute_residual_deg":round(
                    abs((ra_obs-ra_pred+180)%360-180),6),
            })
        result[str(sid)]={
            "pair_count":len(records),
            "max_time_offset_hours_NOT_sigma":max_offset_hours,
            "plane_angle_mae_deg":round(sum(x["plane_angle_absolute_residual_deg"]
                for x in records)/len(records),6) if records else None,
            "raan_contrast_mae_deg":round(sum(x["raan_contrast_absolute_residual_deg"]
                for x in records)/len(records),6) if records else None,
            "records":records,
            "coepoch_or_independent_sensor_measurement":False,
            "historical_angular_sigma_deg":None,
            "hard_angular_cap_active":False,
        }
    return result

def compute(raw,manifest,precision):
    require(precision["id"]=="C197-PRECISION-20261113" and
        precision["source"]["reported_decay_day"]=="1963-11-08" and
        precision["unknowns"]["physical_terminal_utc"] is None and
        not precision["conditional_predicate"]["active"],"NASA time precision invented")
    data=blocks(raw,manifest)
    tested={}
    for H in GRID_H:
        obj={}
        for sid in IDS:
            m=fit(data[sid]["fit"],H)
            obj[str(sid)]={
                "validation":evaluate(data[sid]["validation"],m),
                "no_drag_validation":evaluate(data[sid]["validation"],m,True),
            }
        good=all(obj[str(sid)]["validation"]["predicted_n"]==len(data[sid]["validation"])
                 for sid in IDS)
        tested[str(int(H))]={
            "eligible":good,
            "equal_object_validation_mae_km":round(sum(
                obj[str(sid)]["validation"]["height_proxy_mae_km"] for sid in IDS
                )/3,6) if good else None,
            "objects":obj,
        }
    candidates=[(v["equal_object_validation_mae_km"],int(k))
                for k,v in tested.items() if v["eligible"]]
    chosen=min(candidates)[1] if candidates else None
    objects={}
    models={sid:fit(data[sid]["fit"],float(chosen)) for sid in IDS} if chosen is not None else {}
    for sid in IDS:
        if chosen is None:
            objects[str(sid)]={"status":"NO_ELIGIBLE_MODEL"}
            continue
        m=fit(data[sid]["fit"],float(chosen))
        terminal=crossing(m) if sid==528 else None
        objects[str(sid)]={
            "fit_epoch_count":len(data[sid]["fit"]),
            "validation_epoch_count":len(data[sid]["validation"]),
            "evaluation":evaluate(data[sid]["evaluation"],m),
            "no_drag_evaluation":evaluate(data[sid]["evaluation"],m,True),
            "effective_k_km_per_day_at_400km":round(m["k"],9),
            "anchor_utc":iso(m["anchor"]["t"]),
            "assumed_threshold_crossing_utc":iso(terminal) if terminal else None,
            "crosses_within_Nov7_to_Nov9_scenario":
                START<=terminal<END if terminal else False,
        }
    return {
        "id":"C241-528-EFFECTIVE-DECAY-20261113",
        "source":{"url":SOURCE_URL,"parquet_sha256":SOURCE_SHA256,
                  "csv_sha256":EXPECTED_CSV_SHA256,"kind":"SECONDARY_ONE_LINEAGE"},
        "method":"CIRCULAR_KEPLER_PROXY_AND_SECULAR_J2_RAAN_PLUS_EFFECTIVE_EXPONENTIAL_HEIGHT_LOSS",
        "physical_fragment_size_required":False,
        "k_is_CdA_over_m":False,
        "H_grid_km_NOT_measured":list(GRID_H),
        "H_chosen_using_validation_only":chosen,
        "evaluation_used_for_selection":False,
        "candidate_models":tested,"objects":objects,
        "angular_evaluation_asynchronous":angular_pair_diagnostics(data,models) if models else {},
        "angular_model_drift_allowed":True,
        "angular_separation_is_not_satellite_distance":True,
        "nasa_norad_constant_angular_sigma":None,
        "terminal_scenario":{"start_utc":iso(START),"end_exclusive_utc":iso(END),
            "assumed_threshold_km":THRESHOLD_KM,"source_proves_window":False,
            "physical_constraint_active":False},
        "historical_fit_authenticated":False,"physical_domain_reduced":False,
        "no_primary_TLE_or_sensor_sigma":True,"conde":"INDETERMINATE",
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    out=compute(read_pinned_csv(a.csv),
                json.loads(SPLIT.read_text()),
                json.loads(PRECISION.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"H_selected":out["H_chosen_using_validation_only"],
        "528":out["objects"]["528"],"historical_domain_reduced":False}))

if __name__=="__main__":
    main()
