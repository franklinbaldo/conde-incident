#!/usr/bin/env python3
"""C241: mass-partition Bayesian sensitivity/MCMC, NEVER a historical posterior.

Four components (527, 528, 529, untracked X) share a conditional inventory
T=1176+epsilon kg. Without a validated historical mass/ballistic likelihood,
there is NO identified most-probable allocation. A Markov chain cannot fix it.

Synthetic-only Gaussian mass observations exercise MCMC and diagnostics;
they are explicitly fictional, not derived from NORAD TLEs or NASA decay dates.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path

try:
    from tools.mass_budget_527_529 import MODEL, MATRIX, IDENTITY, validate
    from tools.gcat_mass_lineage_audit import (MODEL as SEMANTICS_PATH,
        MATRIX as ORIGINAL_MATRIX, AUX, CAT, validate as validate_semantics)
except ModuleNotFoundError as exc:
    if exc.name != "tools":
        raise
    from mass_budget_527_529 import MODEL, MATRIX, IDENTITY, validate
    from gcat_mass_lineage_audit import (MODEL as SEMANTICS_PATH,
        MATRIX as ORIGINAL_MATRIX, AUX, CAT, validate as validate_semantics)

OBJECTS=("527","528","529","X")
PREDECLARED_PRIORS={
    "symmetrical":(1.,1.,1.,1.),
    "residual_small_assumption":(1.,1.,1.,0.25),
    "main_body_large_assumption":(4.,1.,1.,0.25),
}
DEFAULT_SEED=19631108
SOURCE_TOTALS={"SUM_MASS_INSERTION":1206., "TOTMASS_REPORTED":1176.,
               "PAYLOAD_PLUS_STAGE_DRY":1176.}

def require(ok,reason):
    if not ok: raise ValueError(reason)

def read_sources():
    model=json.loads(MODEL.read_text(encoding="utf-8"))
    identity=json.loads(IDENTITY.read_text(encoding="utf-8"))
    validate(model,MATRIX.read_text(encoding="utf-8"),identity)
    require(model["source"]["observed_individual_mass_of_528_kg"] is None
            and model["variables"][3]["value"] is None
            and model["variables"][4]["value"] is None
            and not model["conditional_budget"]["physically_calibrated_historical_constraint"],
            "historical evidence must be independently audited")
    semantics=json.loads(SEMANTICS_PATH.read_text(encoding="utf-8"))
    validate_semantics(semantics,ORIGINAL_MATRIX.read_text(encoding="utf-8"),
                       json.loads(AUX.read_text(encoding="utf-8")),
                       json.loads(CAT.read_text(encoding="utf-8")))
    require({z["id"]:float(z["nominal_total_kg"]) for z in semantics["accounting_scenarios"]} ==
            SOURCE_TOTALS, "GCAT mass-basis sources changed")
    return model,semantics

def prior_profile(alpha, total_kg=1176.):
    require(len(alpha)==4 and all(math.isfinite(x) and x>0 for x in alpha),"invalid Dirichlet prior")
    total=sum(alpha)
    return {key:round(total_kg*x/total,6) for key,x in zip(OBJECTS,alpha)}

def historical_gate(model,semantics):
    return {
        "id":"C241-MASS-MCMC-20261113",
        "inference_status":"HISTORICAL_POSTERIOR_NOT_IDENTIFIED_NOT_RUN",
        "historical_individual_mass_measurements":0,
        "historical_B_with_calibrated_area_density_and_covariance":0,
        "historical_likelihood":None,"posterior_most_probable_allocation":None,
        "historical_mcmc_executed":False,
        "source_C61_total_mass_kg_approx":1176,
        "catalogue_payload_527_component_mass_kg":semantics["sources"]["payload"]["Mass_kg"],
        "catalogue_payload_527_component_dry_mass_kg":semantics["sources"]["payload"]["DryMass_kg"],
        "canonical_source_audit_reference":"C241-L40 / PR #629",
        "catalogue_agena_stage_mass_at_insertion_kg":semantics["sources"]["stage"]["Mass_kg"],
        "catalogue_agena_stage_dry_mass_kg":semantics["sources"]["stage"]["DryMass_kg"],
        "catalogue_mass_basis_conflict_kg":semantics["nominal_kg"]["difference_mass_at_insertion_sum_minus_totmass"],
        "catalogue_mass_scenarios_unresolved":semantics["accounting_scenarios"],
        "mass_of_orbiting_527_composite_is_not_306kg_verified":True,
        "component_306kg_is_not_direct_mass_observation_of_528":True,
        "untracked_X_bound":None,"catalog_error_epsilon_bound":None,
        "prior_sensitivity_only_not_posterior":{
            name:prior_profile(alpha) for name,alpha in PREDECLARED_PRIORS.items()},
        "warning":"These numbers are Dirichlet PRIOR means under hypothetical epsilon=0, not inferred component masses or historical posterior probabilities.",
        "required_evidence":[
            "Physical mass/fragmentation inventory tying reference total to a common epoch",
            "Independent geometry/material/area priors or measured projected-area bounds",
            "Calibrated ballistic or orbital-drag likelihood with atmospheric scale, correlated source errors and actual instrument epochs",
            "A historically justified prior for untracked X and epsilon; cannot assert X is small",
        ],
        "physical_domain_reduced":False,"conde":"INDETERMINATE",
    }

def fractions(y):
    require(len(y)==3 and all(math.isfinite(x) for x in y),"invalid log-ratios")
    values=(*y,0.)
    offset=max(values)
    weights=[math.exp(x-offset) for x in values]
    s=sum(weights)
    return tuple(x/s for x in weights)

def log_target(y,eps,alpha,sigma_total,obs,total_reference_mass_kg=1176.):
    f=fractions(y)
    total=total_reference_mass_kg+eps
    if total<=0 or not math.isfinite(total):
        return -math.inf
    # Correct Jacobian of additive log ratio: sum(alpha_i * log(f_i)).
    value=sum(a*math.log(t) for a,t in zip(alpha,f))
    value-=0.5*(eps/sigma_total)**2
    for item in obs:
        j=OBJECTS.index(item["object"])
        mass=total*f[j]
        if item["kind"]=="mass":
            predicted=mass
            observed=item["mass_kg"]
            sigma=item["sigma_kg"]
        else:
            # Explicit projected Cd*A is a SYNTHETIC assumption; source-backed
            # ballistic B and area calibration do not yet exist for the 528.
            predicted=item["assumed_Cd_area_m2"]/mass
            observed=item["observed_B_m2_kg"]
            sigma=item["sigma_B_m2_kg"]
        value-=0.5*((predicted-observed)/sigma)**2
    return value

def validate_synthetic_fixture(config):
    require(config.get("mode")=="SYNTHETIC_TEST_ONLY","only synthetic likelihood supported")
    require(config.get("mass_basis") in SOURCE_TOTALS, "mass basis must be explicit and hypothetical")
    alpha=config["dirichlet_alpha"]
    prior_profile(alpha)
    sigma=float(config["reference_error_sigma_kg"])
    require(math.isfinite(sigma) and sigma>0,"explicit finite total-mass uncertainty required")
    obs=config["synthetic_mass_observations"]
    require(isinstance(obs,list) and len(obs)>=1,"synthetic calibration observations required")
    for item in obs:
        require(item["object"] in OBJECTS and
                item.get("source_class")=="SYNTHETIC_NOT_HISTORICAL" and
                item.get("kind") in ("mass","ballistic"),
                "missing synthetic-only source labels/type")
        fields=(("mass_kg","sigma_kg") if item["kind"]=="mass" else
                ("observed_B_m2_kg","sigma_B_m2_kg","assumed_Cd_area_m2"))
        require(all(isinstance(item.get(k),(int,float)) and
                    not isinstance(item[k],bool) and
                    math.isfinite(item[k]) and item[k]>0 for k in fields),
                "missing synthetic value, area, source or uncertainty")
    require(len({x["object"] for x in obs})==len(obs),"duplicate/possibly dependent observations")
    return tuple(float(x) for x in alpha),sigma,obs

def one_chain(alpha,sigma,obs,seed,warmup,draws,total_reference_mass_kg=1176.):
    rng=random.Random(seed)
    g=[rng.gammavariate(x,1.) for x in alpha]
    s=sum(g)
    f=[x/s for x in g]
    y=[math.log(f[j]/f[3]) for j in range(3)]
    eps=rng.gauss(0.,sigma)
    lp=log_target(y,eps,alpha,sigma,obs,total_reference_mass_kg)
    kept=[]
    accepted=0
    for it in range(warmup+draws):
        proposal=list(y)
        e=eps
        axis=rng.randrange(4)
        if axis==3:e+=rng.gauss(0.,sigma*.12)
        else:proposal[axis]+=rng.gauss(0.,.25)
        nxt=log_target(proposal,e,alpha,sigma,obs,total_reference_mass_kg)
        if math.log(max(1e-300,rng.random()))<nxt-lp:
            y,eps,lp=proposal,e,nxt
            if it>=warmup:accepted+=1
        if it>=warmup:
            fs=fractions(y)
            masses=[(total_reference_mass_kg+eps)*x for x in fs]
            kept.append({"masses_kg":masses,"epsilon_kg":eps,"log_ratios":list(y)})
    return {"draws":kept,"accepted_fraction":accepted/draws}

def scalar_diagnostics(chains,coordinate):
    # Existing repository reference rank-normalized/folded split-Rhat and ESS,
    # rather than "converged" based solely on low rejection.
    try:
        from tools.raan_chain_diagnostics import _split,_axis
    except ModuleNotFoundError as exc:
        if exc.name != "tools":
            raise
        from raan_chain_diagnostics import _split,_axis
    values=[[draw["masses_kg"][coordinate] for draw in chain["draws"]]
            for chain in chains]
    report=_axis(_split(values))
    return {"rhat_rank_and_folded":round(report.rhat,5),
            "bulk_ess":round(report.bulk_ess,3),
            "tail_ess":round(report.tail_ess,3),
            "meets_reference_numerical_gate":
                (report.rhat<1.01 and report.bulk_ess>=400 and report.tail_ess>=400)}

def quantile(values,p):
    a=sorted(values)
    f=(len(a)-1)*p
    lo=int(f)
    return a[lo]+(a[min(lo+1,len(a)-1)]-a[lo])*(f-lo)

def run_synthetic(config,*,seed=DEFAULT_SEED,warmup=400,draws=600):
    alpha,sigma,obs=validate_synthetic_fixture(config)
    require(isinstance(seed,int) and 1<=seed<2**31
            and 100<=warmup<=5000 and 200<=draws<=2048,
            "unsupported MCMC controls")
    basis=config["mass_basis"]
    total_reference_mass_kg=SOURCE_TOTALS[basis]
    chains=[one_chain(alpha,sigma,obs,seed+10007*j,warmup,draws,total_reference_mass_kg)
            for j in range(4)]
    summary={}
    for j,name in enumerate(OBJECTS):
        values=[d["masses_kg"][j] for c in chains for d in c["draws"]]
        summary[name]={
            "mean_kg":round(sum(values)/len(values),3),
            "q05_kg":round(quantile(values,.05),3),
            "median_kg":round(quantile(values,.5),3),
            "q95_kg":round(quantile(values,.95),3),
            "diagnostic":scalar_diagnostics(chains,j),
        }
    return {
        "id":"C241-MASS-MCMC-SYNTHETIC-ONLY",
        "inference_status":"SYNTHETIC_FIXTURE_NOT_HISTORICAL_POSTERIOR",
        "seed":seed,"chains":len(chains),"warmup":warmup,
        "draws_per_chain":draws,
        "acceptance_fractions":[round(c["accepted_fraction"],4) for c in chains],
        "mass_total_source":f"{basis} = {total_reference_mass_kg} kg nominal + synthetic Gaussian epsilon; not actual 1963 mass",
        "assumed_total_reference_kg":total_reference_mass_kg,
        "basis_is_historically_selected":False,
        "payload_306kg_does_not_equal_m527_composite_observation":True,
        "prior_dirichlet_alpha":alpha,
        "observations_are_invented_for_test":True,
        "mass_summary":summary,
        "historical_masses_inferred":False,
        "physical_domain_reduced":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--synthetic-fixture",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    model,semantics=read_sources()
    report=(run_synthetic(json.loads(args.synthetic_fixture.read_text(encoding="utf-8")))
            if args.synthetic_fixture else historical_gate(model,semantics))
    payload=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    print(payload,end="")

if __name__=="__main__":
    main()
