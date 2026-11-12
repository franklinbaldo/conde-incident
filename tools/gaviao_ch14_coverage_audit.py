#!/usr/bin/env python3
"""Independent C243-T13 catalog coverage. Not a physical orbit reconstruction."""
import argparse, json, math
from pathlib import Path
from gaviao_ch13_recency_audit import load_pinned, validated_rows

EXPECTED = {
    "persistence": (53, 0.0264153715, 0.0269039352),
    "secant_2": (52, 0.0141676275, 0.0109350675),
    "ols_3": (51, 0.0145442475, 0.0145442475),
}
def forecast(past, future):
    if not past or not past[-1][0] < future:
        raise ValueError("no strictly prior history")
    preds={"persistence":past[-1][1]}
    if len(past)>=2:
        (t0,y0),(t1,y1)=past[-2:]
        dt=(t1-t0).total_seconds()
        future_dt=(future-t1).total_seconds()
        if dt<=0 or future_dt<=0:
            raise ValueError("invalid secant chronology")
        preds["secant_2"]=y1+(y1-y0)*future_dt/dt
    if len(past)>=3:
        t_ref=past[-1][0]
        x=[(t-t_ref).total_seconds()/86400 for t,_ in past[-3:]]
        y=[v for _,v in past[-3:]]
        mx,my=math.fsum(x)/3,math.fsum(y)/3
        ss=math.fsum((v-mx)**2 for v in x)
        if ss<=0:
            raise ValueError("degenerate epochs")
        slope=math.fsum((a-mx)*(b-my) for a,b in zip(x,y))/ss
        preds["ols_3"]=my+slope*((future-t_ref).total_seconds()/86400-mx)
    if not all(math.isfinite(v) for v in preds.values()):
        raise ValueError("nonfinite prediction")
    return preds

def rmse(rows):
    return math.sqrt(math.fsum(row["error"]**2 for row in rows)/len(rows)) if rows else None

def audit(rows):
    groups=validated_rows(rows)
    target=groups[529]
    own={k:[] for k in EXPECTED}
    joint={k:[] for k in EXPECTED}
    details=[]
    for i in range(1,len(target)):
        epoch,actual=target[i]
        preds=forecast(target[:i],epoch)
        donors={str(s):sum(t<=target[i-1][0] for t,_ in groups[s]) for s in (527,528)}
        eligible=i>=3 and all(v>=3 for v in donors.values())
        row={"epoch":epoch.isoformat(),"past_529":i,"donor_counts":donors,
             "joint":eligible,"forecasts":preds,"errors":{}}
        for name,estimate in preds.items():
            error=actual-estimate
            if not math.isfinite(error):
                raise ValueError("nonfinite error")
            record={"epoch":epoch.isoformat(),"error":error}
            own[name].append(record)
            row["errors"][name]=error
            if eligible:
                joint[name].append(record)
        if eligible and len(preds)!=3:
            raise ValueError("joint eligibility lacks model")
        details.append(row)
    common={r["epoch"] for r in joint["ols_3"]}
    if any({r["epoch"] for r in joint[k]}!=common for k in EXPECTED):
        raise ValueError("nonpaired joint support")
    extra={k:[r for r in own[k] if r["epoch"] not in common] for k in EXPECTED}
    sec_sse=math.fsum(r["error"]**2 for r in own["secant_2"])
    single=extra["secant_2"][0] if len(extra["secant_2"])==1 else None
    influence=None
    if single and sec_sse>0 and rmse(joint["secant_2"])>0:
        influence={"epoch":single["epoch"],"signed_residual_rev_day":single["error"],
                   "absolute_residual_rev_day":abs(single["error"]),
                   "share_of_52_secant_SSE":single["error"]**2/sec_sse,
                   "rmse_growth_percent":100*(rmse(own["secant_2"])/rmse(joint["secant_2"])-1),
                   "SSE_identity_error":sec_sse-
                        math.fsum(r["error"]**2 for r in joint["secant_2"])-single["error"]**2}
    return {"record":"C243-T13-G14","unique_epochs":{str(k):len(v) for k,v in groups.items()},
            "candidate_count":len(details),"joint_count":len(common),
            "counts":{k:len(own[k]) for k in EXPECTED},
            "own_rmse":{k:rmse(own[k]) for k in EXPECTED},
            "joint_rmse":{k:rmse(joint[k]) for k in EXPECTED},
            "extra_epochs":{k:[r["epoch"] for r in extra[k]] for k in EXPECTED},
            "single_extra_influence":influence,
            "independence":"SINGLE_SECONDARY_MIRROR","posthoc":True,
            "lean_physical_premise":"NOT_ESTABLISHED","physical_domain_reduced":False,
            "terminal_simulation":"NOT_RUN","conde":"INDETERMINATE","details":details}

def verify(result):
    if result["unique_epochs"]["529"]!=54 or result["candidate_count"]!=53 or result["joint_count"]!=51:
        raise ValueError("catalog target count mismatch")
    for name,(count,own,joint) in EXPECTED.items():
        if result["counts"][name]!=count:
            raise ValueError("coverage mismatch "+name)
        if abs(result["own_rmse"][name]-own)>5e-7:
            raise ValueError("own RMSE mismatch "+name)
        if abs(result["joint_rmse"][name]-joint)>5e-7:
            raise ValueError("paired RMSE mismatch "+name)
    e=result["extra_epochs"]
    if ([x[:10] for x in e["persistence"]] != ["1963-01-18","1963-02-07"]
        or [x[:10] for x in e["secant_2"]] != ["1963-02-07"] or e["ols_3"]):
        raise ValueError("extra catalog epochs mismatch")
    if any(r["past_529"]>=3 and not r["joint"] for r in result["details"]):
        raise ValueError("unexpected donor censorship")
    v=result["single_extra_influence"]
    if not v or abs(v["SSE_identity_error"])>1e-11:
        raise ValueError("single epoch SSE attribution failed")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--parquet",type=Path,required=True)
    p.add_argument("--download",action="store_true")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=audit(load_pinned(args.parquet,args.download))
    verify(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="details"},indent=2,sort_keys=True))
if __name__=="__main__":
    main()
