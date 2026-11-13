#!/usr/bin/env python3
"""Audit C241 symmetric calendar-day reporting model against NASA C197.
Does not estimate physical time or sigma for the NORAD 528.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"research/constraints/C241_nov8_two_sided_day_likelihood_2026-11-13.json"
NASA=ROOT/"research/constraints/nasa_528_decay_precision_C197_20261113.json"
REQUIRED={
 "src/lib/catalogDayLikelihood.ts",
 "src/lib/monteCarlo.ts",
 "src/components/MonteCarloVisualizer.tsx",
 "tests/catalogDayLikelihood.test.mjs"
}

def require(ok,why):
    if not ok:raise ValueError(why)

def validate(ledger,primary,read):
    require(ledger["schema"]=="conde.norad528-two-sided-calendar-likelihood/v1" and
            ledger["id"]=="C241-NOV8-TWO-SIDED-20261113" and
            ledger["status"]==
                "CONDITIONAL_MODEL_WITH_UNCALIBRATED_GAUSSIAN_REPORTING_ERROR",
            "schema and epistemic status")
    observed=ledger["observation"]
    require(primary["id"]=="C197-PRECISION-20261113" and
            primary["source"]["reported_decay_day"]=="1963-11-08" and
            primary["source"]["sha256"]==observed["source_sha256"] and
            observed["occurrence"]=="C197#1" and
            observed["source_pdf"]==primary["source"]["url"] and
            observed["ntrs"]==primary["source"]["ntrs"] and
            observed["reported_decay_day"]=="1963-11-08" and
            observed["report_published_utc_day"]=="1963-11-15",
            "C197 source mismatch")
    require(all(observed[k] is None for k in (
            "exact_instrumental_last_seen_utc","true_orbital_decay_utc",
            "true_impact_utc","error_sigma_hours")) and
            not observed["day_label_utc_convention_verified"] and
            not observed["physical_deposition_documented"] and
            not primary["conditional_predicate"]["active"] and
            primary["likelihood"]["numeric"] is None,
            "false NASA precision or event time")
    c=ledger["calendar_label_utc_scenario"]
    require(c["start_utc"]=="1963-11-08T00:00:00Z" and
            c["end_exclusive_utc"]=="1963-11-09T00:00:00Z" and
            c["center_utc"]=="1963-11-08T12:00:00Z" and
            c["assumes_calendar_day_is_utc"] and
            not c["calendar_day_utc_assumption_verified"] and
            c["time_error_days_before_and_after_allowed"] and
            not c["hard_exclude_after_nov8"] and
            not c["hard_exclude_before_nov8"],"hard cutoff sneaked into likelihood")
    expected={6:(.0997337838,.8005324324),12:(.1952257889,.6095484222),
              24:(.3156268098,.3687463804)}
    scenarios=ledger["sensitivity_scenarios"]
    require([x["sigma_hours_assumed"] for x in scenarios]==[6,12,24],
            "scenario grid not predeclared")
    for row in scenarios:
        before,during=expected[row["sigma_hours_assumed"]]
        require(abs(row["probability_before_8"]-before)<1e-7 and
                abs(row["probability_during_8"]-during)<1e-7 and
                row["probability_before_8"]==row["probability_after_8"] and
                abs(sum(row[k] for k in (
                    "probability_before_8","probability_during_8","probability_after_8"))-1)<1e-6,
                "wrong two-sided probabilities")
    require(set(ledger["consumers"])==REQUIRED,"missing temporal consumer")
    for path in REQUIRED:read(path)
    require(all(ledger["source_to_simulation_contract"][k] is False for k in (
        "source_provides_historical_sigma",
        "no_implicit_sigma_selection" if False else "historically_calibrated_posterior_available",
        "scenario_weighting_does_not_imply_orbit_correct" if False else "geographic_distance_from_Conde_not_used_as_likelihood") ) is False,
        "invalid inference flags")
    sim=ledger["source_to_simulation_contract"]
    require(sim["no_implicit_sigma_selection"] and
            sim["geographic_distance_from_Conde_not_used_as_likelihood"] and
            sim["scenario_weighting_does_not_imply_orbit_correct"] and
            sim["impact_location_model_required"] and
            sim["reentry_to_surface_delay_model_required"] and
            sim["fragment_survival_ablation_model_required"] and
            not sim["historically_calibrated_posterior_available"],
            "false posterior calibration")
    outcome=ledger["scientific_result"]
    require(outcome["historical_physical_date_probability"]=="NOT_IDENTIFIED" and
            outcome["historical_Conde_impact_posterior"]=="NOT_IDENTIFIED" and
            not outcome["physical_orbital_domain_reduced"],
            "historical inference prematurely promoted")
    return {
        "id":ledger["id"],
        "source_c197_sha256":observed["source_sha256"],
        "scenario_sigmas_hours":[6,12,24],
        "hard_nov9_cutoff":False,
        "historical_sigma":None,
        "source_to_monte_carlo_consumer":True,
        "historical_Conde_impact_posterior":None
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    d=json.loads(LEDGER.read_text(encoding="utf-8"))
    primary=json.loads(NASA.read_text(encoding="utf-8"))
    def read(path):return (ROOT/path).read_text(encoding="utf-8")
    outcome=validate(d,primary,read)
    payload=json.dumps(outcome,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    print(payload,end="")

if __name__=="__main__": main()
