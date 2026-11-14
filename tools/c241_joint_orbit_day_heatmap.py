#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy==2.2.6", "scipy==1.15.3"]
# ///
"""C241: SAME-DRAW orbital × NASA Nov8 date likelihood -> 200-km Conde grid.

Exploratory Kepler+secular J2 SUBPOINT, not NORAD/SGP4 truth, atmospheric
entry, ablation or ground impact. Explicit fictitious priors and covariance.
Retain individual time/scenario/location in optional .npy, not just aggregates.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
try:
    from scipy.special import ndtr
except ModuleNotFoundError:
    # Universal CI may test this module before installing optional SciPy.
    # Slow but accurate standard-library fallback; full 1.5m workflow pins SciPy.
    def ndtr(z):
        a=np.asarray(z,dtype=np.float64)
        values=np.fromiter((.5*math.erfc(-float(x)/math.sqrt(2))
                            for x in a.flat),dtype=np.float64,count=a.size)
        return values.reshape(a.shape)

ROOT=Path(__file__).resolve().parents[1]
TLE=ROOT/"research/tle_custody/mirror_528_1963-10-27.tle"
DAY=ROOT/"research/constraints/C241_nov8_two_sided_day_likelihood_2026-11-13.json"
PREVIOUS=ROOT/"research/statistics/c241_528_unweighted_2000km_scenarios.json"
SHA="18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
MU,RE,J2,RS=398600.4418,6378.137,1.08262668e-3,6371.0088
CONDE_LAT,CONDE_LON=-11.8139,-37.6108
EPOCH_MIN=datetime(1963,11,5,tzinfo=timezone.utc).timestamp()
EPOCH_MAX=datetime(1963,11,12,tzinfo=timezone.utc).timestamp()
DAY8=datetime(1963,11,8,tzinfo=timezone.utc).timestamp()
DAY9=datetime(1963,11,9,tzinfo=timezone.utc).timestamp()
PHASE=np.array([0.,90.,180.,270.])
NDOT=np.array([0.,.01373126,.04])
TIME_SIGMAS=(6,12,24)
# phase deg, n-dot rev/day², correlation. ALL deliberately UNCALIBRATED.
ORBIT_SIGMAS={"tight":(25.,.006,0.),
              "middle":(90.,.02,0.),
              "broad":(180.,.05,0.),
              "middle_rho_neg":(90.,.02,-.5),
              "middle_rho_pos":(90.,.02,.5)}
MODES=["baseline"]+[f"orbital_{name}" for name in ORBIT_SIGMAS]+[
    f"temporal_{t}h" for t in TIME_SIGMAS]+[
    f"joint_{name}_{t}h" for name in ORBIT_SIGMAS for t in TIME_SIGMAS]
COLS=["baseline","orbital_middle","temporal_12h","joint_middle_12h"]
DTYPE=np.dtype([("unix_utc_seconds","<f8"),("scenario_id","<i2"),
                ("latitude_deg","<f4"),("longitude_deg","<f4"),
                ("x_east_km","<f4"),("y_north_km","<f4"),
                ("distance_from_conde_km","<f4")])

def require(ok,reason):
    if not ok: raise ValueError(reason)

def load_sources():
    raw=TLE.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==SHA,"TLE SHA changed")
    a,b=raw.decode("ascii").splitlines()
    require(a.startswith("1 00528") and b.startswith("2 00528"),"not NORAD 528")
    day=float(a[20:32])
    epoch=datetime(1963,1,1,tzinfo=timezone.utc)+timedelta(days=day-1)
    state={
      "epoch_unix":epoch.timestamp(),
      "epoch_utc":epoch.isoformat().replace("+00:00","Z"),
      "incl":float(b[8:16]),"node":float(b[17:25]),
      "e":float("0."+b[26:33]),"peri":float(b[34:42]),
      "anomaly":float(b[43:51]),"n0":float(b[52:63]),
      "ndot":2*float(a[33:43])}
    require(abs(state["ndot"]-NDOT[1])<1e-10 and
            80<state["incl"]<85 and 190<state["node"]<210 and
            300<day<301,"unexpected secondary TLE fields")
    c=json.loads(DAY.read_text())
    require(c["id"]=="C241-NOV8-TWO-SIDED-20261113" and
            c["observation"]["reported_decay_day"]=="1963-11-08" and
            c["observation"]["error_sigma_hours"] is None and
            c["observation"]["true_orbital_decay_utc"] is None and
            not c["source_to_simulation_contract"]["historically_calibrated_posterior_available"],
            "NASA day changed or was promoted to physical measurement")
    prev=json.loads(PREVIOUS.read_text())
    require(prev["source"]["tle_sha256"]==SHA and
            prev["source"]["n"]==1_500_000 and
            prev["integrity_constraints"]["baseline_2000km_hits"]==25489 and
            prev["confidence_status"]["phase_sigma_deg"] is None,
            "old aggregate is not the stated frozen exploratory model")
    return state

def likelihood_time(t, sigma_hours):
    require(sigma_hours in TIME_SIGMAS,"time sigma must be explicitly predeclared")
    s=sigma_hours*3600.
    return np.clip(ndtr((DAY9-t)/s)-ndtr((DAY8-t)/s),0.,1.)

def shortest_phase(ids):
    return (PHASE[ids%4]+180)%360-180

def likelihood_orbit(ids,key):
    require(key in ORBIT_SIGMAS,"unknown orbital hypothesis")
    sp,sn,rho=ORBIT_SIGMAS[key]
    x=shortest_phase(ids)/sp
    y=(NDOT[ids//4]-NDOT[1])/sn
    return np.exp(-.5*(x*x-2*rho*x*y+y*y)/(1-rho*rho))

def weights_for_sample(ids,t):
    orbital={key:likelihood_orbit(ids,key) for key in ORBIT_SIGMAS}
    temporal={h:likelihood_time(t,h) for h in TIME_SIGMAS}
    return {"baseline":np.ones(len(ids)),
      **{f"orbital_{k}":v for k,v in orbital.items()},
      **{f"temporal_{h}h":v for h,v in temporal.items()},
      **{f"joint_{k}_{h}h":v*temp for k,v in orbital.items()
         for h,temp in temporal.items()}}

def gmst_rad(t):
    """Approximate Greenwich sidereal angle, UT1=UTC, not historic EOP."""
    jd=t/86400.+2440587.5
    T=(jd-2451545.)/36525.
    deg=280.46061837+360.98564736629*(jd-2451545.)+(
        .000387933*T*T-T*T*T/38710000.)
    return np.deg2rad(np.remainder(deg,360.))

def subpoint(t,ids,state):
    """J2 mean element toy evolution; sampled terminal time is NOT an event."""
    days=(t-state["epoch_unix"])/86400.
    ndot=NDOT[ids//4]
    nmid=state["n0"]+.5*ndot*days
    require(bool(np.all(nmid>0)),"invalid mean motion")
    nrad=nmid*2*math.pi/86400.
    a=(MU/nrad**2)**(1./3.)
    e=state["e"]
    inc=math.radians(state["incl"])
    fact=J2*nrad*(RE/(a*(1-e*e)))**2
    node_dot=-1.5*fact*math.cos(inc)
    peri_dot=.75*fact*(5*math.cos(inc)**2-1)
    mean_corr=.75*fact*math.sqrt(1-e*e)*(3*math.cos(inc)**2-1)
    elapsed=days*86400.
    M=math.radians(state["anomaly"])+2*math.pi*(
        state["n0"]*days+.5*ndot*days**2)+mean_corr*elapsed+np.deg2rad(PHASE[ids%4])
    M=np.remainder(M,2*math.pi)
    ecc=M+e*np.sin(M)
    for _ in range(3):
        ecc-=(ecc-e*np.sin(ecc)-M)/(1-e*np.cos(ecc))
    nu=2*np.arctan2(np.sqrt(1+e)*np.sin(ecc/2),np.sqrt(1-e)*np.cos(ecc/2))
    u=math.radians(state["peri"])+peri_dot*elapsed+nu
    asc=math.radians(state["node"])+node_dot*elapsed
    lat=np.arcsin(np.clip(math.sin(inc)*np.sin(u),-1.,1.))
    inertial_lon=asc+np.arctan2(math.cos(inc)*np.sin(u),np.cos(u))
    lon=np.remainder(inertial_lon-gmst_rad(t)+math.pi,2*math.pi)-math.pi
    return np.rad2deg(lat),np.rad2deg(lon)

def aeqd(lat_deg,lon_deg):
    """Spherical azimuthal equidistant about Conde: x EAST, y NORTH."""
    lat=np.deg2rad(lat_deg)
    lon=np.deg2rad(lon_deg)
    c0=math.radians(CONDE_LAT)
    dl=np.remainder(lon-math.radians(CONDE_LON)+math.pi,2*math.pi)-math.pi
    arg=np.clip(math.sin(c0)*np.sin(lat)+math.cos(c0)*np.cos(lat)*np.cos(dl),-1.,1.)
    arc=np.arccos(arg)
    factor=np.divide(arc,np.sin(arc),out=np.ones_like(arc),
                     where=np.abs(np.sin(arc))>1e-12)
    x=RS*factor*np.cos(lat)*np.sin(dl)
    y=RS*factor*(math.cos(c0)*np.sin(lat)-math.sin(c0)*np.cos(lat)*np.cos(dl))
    return x,y,RS*arc

def compute(n:int,seed:int,batch:int,out:Path,save_draws=False):
    require(isinstance(n,int) and 100<=n<=5_000_000,"draw count 100..5m required")
    require(isinstance(seed,int) and 0<seed<2**32,"seed required")
    require(isinstance(batch,int) and 100<=batch<=200_000,"batch required")
    state=load_sources()
    out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    acc={k:{"all":0.,"sq":0.,"inside":0.,
            "cells":np.zeros(400,dtype=np.float64),
            "count":np.zeros(400,dtype=np.int64)} for k in MODES}
    draws=np.lib.format.open_memmap(
        out/"individual_candidates.npy",mode="w+",dtype=DTYPE,shape=(n,)
    ) if save_draws else None
    for start in range(0,n,batch):
        size=min(batch,n-start)
        sid=rng.integers(0,12,size=size,dtype=np.int16)
        t=EPOCH_MIN+rng.random(size)*(EPOCH_MAX-EPOCH_MIN)
        lat,lon=subpoint(t,sid,state)
        x,y,dist=aeqd(lat,lon)
        keep=(dist<=2000)
        cx=np.floor((x+2000)/200).astype(np.int32)
        cy=np.floor((y+2000)/200).astype(np.int32)
        valid=keep&(cx>=0)&(cx<20)&(cy>=0)&(cy<20)
        flat=(cy*20+cx)[valid]
        for label,w in weights_for_sample(sid,t).items():
            a=acc[label]
            a["all"]+=float(w.sum())
            a["sq"]+=float(w@w)
            a["inside"]+=float(w[keep].sum())
            a["cells"]+=np.bincount(flat,weights=w[valid],minlength=400)
            if label=="baseline":
                a["count"]+=np.bincount(flat,minlength=400)
        if draws is not None:
            sl=slice(start,start+size)
            for name,values in [
                ("unix_utc_seconds",t),("scenario_id",sid),
                ("latitude_deg",lat),("longitude_deg",lon),
                ("x_east_km",x),("y_north_km",y),
                ("distance_from_conde_km",dist)]:
                draws[name][sl]=values
    if draws is not None:
        draws.flush()
        del draws
    summary={name:{
        "probability_within_2000km":a["inside"]/a["all"],
        "percent_within_2000km":100*a["inside"]/a["all"],
        "effective_sample_size":a["all"]**2/a["sq"],
        "global_weight_sum":a["all"],"region_weight_sum":a["inside"],
    } for name,a in acc.items()}
    cells=[]
    for iy in range(20):
        for ix in range(20):
            j=iy*20+ix
            row={"x_center_km_east":ix*200-1900,
                 "y_center_km_north":iy*200-1900,
                 "unweighted_count_inside_circle":int(acc["baseline"]["count"][j])}
            for label in ("baseline","orbital_middle","temporal_12h","joint_middle_12h"):
                a=acc[label]
                row[label+"_global_probability"]=float(a["cells"][j]/a["all"])
                row[label+"_conditional_within_circle"]=float(
                    a["cells"][j]/a["inside"])
            cells.append(row)
    def write_csv(path,rows):
        with (out/path).open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    write_csv("cells_200km.csv",cells)
    for axis,column in (("east_west","x_center_km_east"),("north_south","y_center_km_north")):
        rows=[]
        for x in range(-1900,2000,200):
            chosen=[c for c in cells if c[column]==x]
            row={"band_center_km":x}
            for key in ("unweighted_count_inside_circle",)+tuple(
                k for k in chosen[0] if k.endswith("_global_probability") or
                k.endswith("_conditional_within_circle")):
                row[key]=sum(v[key] for v in chosen)
            rows.append(row)
        write_csv(axis+"_bands.csv",rows)
    report={
        "schema":"conde.c241-joint-orbital-day-scenario-heatmap/v1",
        "id":"C241-JOINT-ORBIT-DAY-20261113",
        "sources":{
            "tle_sha256":SHA,"tle_epoch_utc":state["epoch_utc"],
            "tle_lineage":"SECONDARY_NOT_INSTRUMENTALLY_AUTHENTICATED",
            "NASA_reported_day":"1963-11-08",
            "NASA_event_sigma_hours":None,
            "reference_old_aggregate_percent":1.6992666666666667,
            "old_aggregate_not_reweighted_as_if_individual":True,
        },
        "assumptions":{
            "orbital":"approximate first order J2/Kepler mean element phase",
            "not_SGP4_or_reentry_dynamics":True,
            "time_prior":"UNIFORM_1963-11-05_00Z_to_1963-11-12_00Z",
            "time_sigma_hours":TIME_SIGMAS,
            "orbital_priors":ORBIT_SIGMAS,
            "phase_offsets_deg":PHASE.tolist(),"ndot_rev_day2":NDOT.tolist(),
            "scenario_priors":"UNIFORM_OVER_12_CHOICES",
            "GMST":"UTC_APPROX_UT1_NO_HISTORICAL_EOP",
            "map":"spherical azimuthal equidistant on Conde BA, radius 2000km",
            "cell_km":200,"reference_coordinate":[CONDE_LAT,CONDE_LON],
            "day_label_likelihood":"normal CDF integrated over whole Nov 8 UTC",
            "joint_weight":"PER_DRAW orbital_likelihood*temporal_likelihood",
            "sensor_sigma_historically_calibrated":False,
            "orbital_prior_authenticated":False,
            "fragment_ablation_or_survival_modeled":False,
            "impact_location_modeled":False,
        },
        "sample":{"n":n,"seed":seed,"batch":batch,"saved_individual_draws":save_draws,
                  "draw_dtype":str(DTYPE)},
        "results":summary,
        "representative_heatmap":"joint_middle_12h",
        "denominator":"ALL GLOBAL SUBPOINTS, not just points inside Conde circle",
        "historical_Conde_impact_posterior":None,
        "historical_reentry_probability":None,
        "output_files":["summary.json","cells_200km.csv",
                        "east_west_bands.csv","north_south_bands.csv"]+(
                            ["individual_candidates.npy"] if save_draws else []),
    }
    (out/"summary.json").write_text(json.dumps(report,ensure_ascii=False,
        indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--draws",type=int,default=100_000)
    p.add_argument("--seed",type=int,default=19631108)
    p.add_argument("--batch",type=int,default=50_000)
    p.add_argument("--out-dir",required=True,type=Path)
    p.add_argument("--save-draws",action="store_true")
    a=p.parse_args()
    x=compute(a.draws,a.seed,a.batch,a.out_dir,a.save_draws)
    print(json.dumps({"sample_size":a.draws,
       "unweighted_percent":x["results"]["baseline"]["percent_within_2000km"],
       "orbital_middle_percent":x["results"]["orbital_middle"]["percent_within_2000km"],
       "temporal_12h_percent":x["results"]["temporal_12h"]["percent_within_2000km"],
       "joint_middle_12h_percent":x["results"]["joint_middle_12h"]["percent_within_2000km"],
       "historical_impact":None},sort_keys=True))

if __name__=="__main__":
    main()
