#!/usr/bin/env python3
"""C241: evidence-aware quadratic penalties for Python Monte Carlo and heatmaps.

Source confidence is NOT a numerical sigma. Every sigma/correlation must be
independently calibrated or explicitly labelled a scenario assumption.
This module NEVER emits a historical posterior from the 1963 catalogue.

Replays frozen 12-scenario Conde 2000-km groundtrack summary with Gaussian
penalties for phase/n-dot deviations. Its synthetic sigmas are design choices,
not NORAD 1963 tracking precision; result is SENSITIVITY, not impact probability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"research/statistics/c241_528_unweighted_2000km_scenarios.json"
SCHEMA="conde.c241-confidence-weighted-geography/v1"
# SHA-256 of canonical JSON for the full audited frozen input snapshot.
# This is local artifact integrity, NOT independent authentication of 1963 sources.
FROZEN_INPUT_CANONICAL_SHA256="45ab7d423aa9a17664e18d6c4a422f3b71c8765fbff45d61ff445294b3edb5c0"

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def shortest_angle(delta_deg: float) -> float:
    require(math.isfinite(delta_deg),"angular residual must be finite")
    return (delta_deg+180.)%360.-180.

def cholesky(correlation: list[list[float]]) -> list[list[float]]:
    """Fail closed on non-symmetric/non-SPD correlation assumptions."""
    n=len(correlation)
    require(1<=n<=64 and all(len(row)==n for row in correlation),
            "square correlation matrix required")
    for i in range(n):
        for j in range(n):
            require(math.isfinite(correlation[i][j]) and
                    abs(correlation[i][j]-correlation[j][i])<1e-12,
                    "symmetric finite correlation required")
        require(abs(correlation[i][i]-1.)<1e-12,"correlation diagonal must be 1")
    L=[[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            residual=correlation[i][j]-sum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                require(residual>1e-12,"correlation must be strictly positive definite")
                L[i][j]=math.sqrt(residual)
            else:
                L[i][j]=residual/L[j][j]
    return L

@dataclass(frozen=True)
class Residual:
    occurrence: str
    lineage: str
    quantity: str
    unit: str
    observed: float
    predicted: float
    sigma: float | None
    precision_status: str  # CALIBRATED or ASSUMED_SCENARIO
    sigma_provenance: str | None
    angular: bool = False

def gaussian_penalty(
    residuals: list[Residual],
    correlation: list[list[float]] | None = None,
) -> dict:
    """Returns -log relative likelihood = 1/2 * r' Sigma^-1 r.

    Must NOT multiply correlated records as independent without an EXPLICIT
    correlation choice. 'Calibrated' means the source identifies the error,
    not merely that the measurement comes from a trusted organization.
    """
    require(bool(residuals),"at least one residual required")
    require(all(x.lineage==residuals[0].lineage for x in residuals),
            "mixed lineage: score separate audited blocks with a justified joint model")
    require(len({x.occurrence for x in residuals})==len(residuals),
            "duplicate evidence occurrence must not count twice")
    vector=[]
    for x in residuals:
        require(x.precision_status in {"CALIBRATED","ASSUMED_SCENARIO"},
                "precision status must be explicit")
        require(x.sigma is not None and math.isfinite(x.sigma) and x.sigma>0,
                "missing/invalid sigma must not receive a default")
        require(bool(x.sigma_provenance) and x.sigma_provenance.strip()!="",
                "sigma provenance or scenario rationale required")
        require(math.isfinite(x.observed) and math.isfinite(x.predicted),
                "finite observations and model outputs required")
        delta=(shortest_angle(x.predicted-x.observed) if x.angular
               else x.predicted-x.observed)
        vector.append(delta/x.sigma)
    if len(vector)>1:
        require(correlation is not None,"dependent evidence requires declared correlation")
    if correlation is None:
        correlation=[[1.]]
    L=cholesky(correlation)
    require(len(L)==len(vector),"correlation dimension mismatch")
    z=[]
    for i in range(len(vector)):
        z.append((vector[i]-sum(L[i][j]*z[j] for j in range(i)))/L[i][i])
    q=math.fsum(v*v for v in z)
    return {
        "penalty":.5*q,
        "relative_weight":math.exp(-.5*q),
        "calibrated":all(x.precision_status=="CALIBRATED" for x in residuals),
        "confidence_grade_alone_not_numeric_sigma":True,
        "records":len(residuals),
        "lineage":residuals[0].lineage,
    }

def validate_frozen_report(report: dict) -> None:
    require(report.get("schema")==SCHEMA and
            report["source"]["sha256_of_original_1500000_draw_report"]==
               "c6c32f55fbc2afd3c60c6f109ce8f5d4c979eb195600b0fc51ead400a0f8824d",
            "frozen original 1.5m draw report identity changed")
    source=report["source"]
    require(source["tle_sha256"]==
            "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
            and source["n"]==1500000
            and source["classification"]=="SYNTHETIC_SECULAR_J2_GROUNDTRACK_NOT_IMPACT"
            and not source["independent_primary_observation"],"TLE provenance promoted")
    rows=report["scenarios"]
    require(len(rows)==12 and
            len({(x["ndot_rev_day2"],x["phase_offset_deg"]) for x in rows})==12,
            "frozen 12 scenarios")
    require(set(x["ndot_rev_day2"] for x in rows)=={0.,.01373126,.04}
            and set(x["phase_offset_deg"] for x in rows)=={0.,90.,180.,270.},
            "initial 12 design values replaced")
    require(sum(x["draws"] for x in rows)==1500000
            and all(0<=x["within_2000km"]<=x["draws"] for x in rows),
            "draw counts invalid")
    require(sum(x["within_2000km"] for x in rows)==25489,
            "original 2000km estimate mutated")
    require(report["confidence_status"]["phase_sigma_deg"] is None and
            report["confidence_status"]["ndot_sigma_rev_day2"] is None and
            report["confidence_status"]["error_correlation"] is None and
            report["confidence_status"]["historical_impact_posterior"] is None,
            "unverified errors silently calibrated")
    canonical=json.dumps(report,sort_keys=True,separators=(",",":"),
                         ensure_ascii=True,allow_nan=False).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest()==FROZEN_INPUT_CANONICAL_SHA256,
            "frozen input payload diverged from audited snapshot")

def weight_frozen_scenarios(
    report: dict, *, phase_sigma_deg: float | None,
    ndot_sigma_rev_day2: float | None, rho: float | None,
) -> dict:
    validate_frozen_report(report)
    require(phase_sigma_deg is not None and ndot_sigma_rev_day2 is not None
            and rho is not None,"all three uncertainty hypotheses must be explicit")
    require(math.isfinite(phase_sigma_deg) and 0<phase_sigma_deg<=360
            and math.isfinite(ndot_sigma_rev_day2) and
            0<ndot_sigma_rev_day2<=1,"invalid sensitivity scales")
    require(math.isfinite(rho) and abs(rho)<1,"correlation must be a strict scenario")
    rows=report["scenarios"]
    den=num=den2=0.
    weighted=[]
    for row in rows:
        residuals=[
            Residual("C241-SCENARIO-PHASE","SAME_SECONDARY_TLE_LINEAGE",
                     "phase_offset","degree",0.,row["phase_offset_deg"],
                     phase_sigma_deg,"ASSUMED_SCENARIO",
                     "user scenario, not historical measured TLE phase accuracy",True),
            Residual("C241-SCENARIO-NDOT","SAME_SECONDARY_TLE_LINEAGE",
                     "ndot_rev_day2","rev/day2",.01373126,row["ndot_rev_day2"],
                     ndot_sigma_rev_day2,"ASSUMED_SCENARIO",
                     "user scenario, not a measured 1963 acceleration"),
        ]
        score=gaussian_penalty(residuals,[[1.,rho],[rho,1.]])
        w=score["relative_weight"]
        count=row["draws"]
        den+=count*w
        num+=row["within_2000km"]*w
        den2+=count*w*w
        weighted.append({
            "ndot_rev_day2":row["ndot_rev_day2"],
            "phase_offset_deg":row["phase_offset_deg"],
            "normalized_relative_weight_vs_max":w,
            "penalty":score["penalty"],
            "n_draws":count,
        })
    require(den>0 and den2>0,"zero effective weight")
    return {
        "status":"ASSUMED_PRIOR_SENSITIVITY_NOT_HISTORICAL_POSTERIOR",
        "phase_sigma_deg_assumed":phase_sigma_deg,
        "ndot_sigma_rev_day2_assumed":ndot_sigma_rev_day2,
        "rho_assumed_same_secondary_lineage":rho,
        "weighted_p_terminal_subsatellite_within_2000km":num/den,
        "weighted_percent":100*num/den,
        "effective_sample_size":den*den/den2,
        "probability_of_ground_impact":None,
        "ablation_survival_probability":None,
        "historical_sigma_calibrated":False,
        "scenario_weights":weighted,
    }

def report_all(report: dict) -> dict:
    validate_frozen_report(report)
    cases=[
        ("tight_hypothesis",25.,.006,0.),
        ("intermediate_hypothesis",90.,.02,0.),
        ("broad_hypothesis",180.,.05,0.),
        ("intermediate_neg_correlation",90.,.02,-.5),
        ("intermediate_pos_correlation",90.,.02,.5),
    ]
    sensitivity={}
    for label,sigma_phase,sigma_ndot,rho in cases:
        out=weight_frozen_scenarios(report,phase_sigma_deg=sigma_phase,
                                    ndot_sigma_rev_day2=sigma_ndot,rho=rho)
        sensitivity[label]={k:v for k,v in out.items() if k!="scenario_weights"}
    return {
        "id":"C241-MC-CONFIDENCE-WEIGHTS-20261113",
        "source":"SECONDARY_TLE_J2_SYNTHETIC_1_5M_SAMPLES",
        "baseline_equal_draw_percent":100*sum(x["within_2000km"] for x in report["scenarios"])/1500000,
        "sensitivity":sensitivity,
        "confidence_source_grade_does_not_supply_sigma":True,
        "uncertainty_correlation_not_identified":True,
        "Nasa_8_nov_classification_not_physical_time_sigma":True,
        "physical_masses_and_ablation_not_inferred":True,
        "historical_posterior":None,
        "impact_probability":None,
        "map_of_historical_impact":"NOT_IDENTIFIED",
    }

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=INPUT)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    output=report_all(json.loads(a.input.read_text(encoding="utf-8")))
    payload=json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(payload,encoding="utf-8")
    print(payload,end="")

if __name__=="__main__":main()
