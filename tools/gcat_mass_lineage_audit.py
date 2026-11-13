#!/usr/bin/env python3
"""Read-only audit of 1963-003 GCAT Mass/DryMass/TotMass semantics.

Secondary catalogue facts are not a direct 528 mass observation and
not enough to pick a correct 1176/1206 kg inventory at separation.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"research/constraints/C241_L39_stage_payload_mass_semantics_20261113.json"
MATRIX=ROOT/"research/evidence_matrix_C001-C238_2026-11-11.md"
AUX=ROOT/"research/tle_custody/gcat_identity_527_529_C241-L13.json"
CAT=ROOT/"research/tle_custody/gcat_full_catalog_lineage_C241-L14.json"

def require(ok,msg):
    if not ok:raise ValueError(msg)

def validate(d,matrix,aux,cat):
    require(d["schema"]=="conde.stage-payload-mass-lineage-1963/v1"
            and d["id"]=="C241-L39-MASS-SEMANICS","ledger schema")
    row=[x for x in matrix.splitlines() if x.startswith("| C61 |")]
    require(len(row)==1 and "~306 kg" in row[0] and "~1176 kg" in row[0]
            and "528/529" in row[0],"C61 legacy input")
    s=d["sources"]
    require(s["definitions"]["url"]=="https://planet4589.org/space/gcat/web/cat/cols.html"
            and "attached" in s["definitions"]["definitions"]["TotMass"],"GCAT mass definitions")
    p=s["payload"]
    a=s["stage"]
    require(p["jcat"]=="S00527" and p["associated_parent"]=="A00324"
            and p["Mass_kg"]==306 and p["TotMass_associated_kg"]==1176
            and p["DryMass_kg"] is None,
            "unverified 527 dry mass or wrong payload mass")
    require(a["jcat"]=="A00324" and a["linked_satcat"]=="00527"
            and a["Mass_kg"]==900 and a["DryMass_kg"]==870
            and a["TotMass_kg"]==0, "stage initial/dry mass changed")
    require(s["secondary_attachment"]["jcat"]=="S00527"
            and "attached" in s["secondary_attachment"]["statement"],"attachment genealogy")
    require(s["earlier_matrix"]["occurrence"]=="C61"
            and s["catalog_identity"]["crosswalk_status"]=="528/529 cataloged as debris, physical pieces and mass unknown",
            "old matrix provenance")
    stage=next(x for x in aux["sources"] if x["id"]=="GCAT_AUX")
    require(stage["record_key"]=="A00324" and stage["catalog_number"]=="00527",
            "stage source lineage changed")
    require(cat["record_id"]=="C241-L14"
            and cat["catalogue_labels"]["00527"]["reported_parent"]=="A00324 Agena B 2313"
            and cat["catalogue_labels"]["00528"]["reported_parent"]=="S00527"
            and cat["catalogue_labels"]["00529"]["reported_parent"]=="S00527",
            "debris parent genealogy changed")
    n=d["nominal_kg"]
    require(n["payload_object_Mass"]==306 and n["stage_Mass"]==900
            and n["stage_DryMass"]==870 and n["TotMass_associated"]==1176
            and n["sum_individual_Mass_payload_plus_stage"]==p["Mass_kg"]+a["Mass_kg"]==1206
            and n["sum_payload_Mass_plus_stage_DryMass"]==p["Mass_kg"]+a["DryMass_kg"]==1176
            and n["difference_mass_at_insertion_sum_minus_totmass"]==1206-1176==30
            and n["difference_stage_Mass_minus_DryMass"]==900-870==30,
            "nominal 30 kg difference or catalog fields changed")
    f=d["findings"]
    require(f["unknown_mass_528_kg"] is None and f["unknown_mass_529_kg"] is None
            and f["physical_mass_inventory_epoch"] is None
            and f["original_vehicle_mass_document"] is None
            and not f["stage_consumed_30_kg_is_observed"]
            and not f["TotMass_equals_sum_dry_confirmed"]
            and not f["TotMass_equals_sum_wet_confirmed"]
            and not f["historical_masses_identified"],"unsupported 528 mass assignment")
    scenarios=d["accounting_scenarios"]
    require([x["id"] for x in scenarios]==["SUM_MASS_INSERTION","TOTMASS_REPORTED","PAYLOAD_PLUS_STAGE_DRY"]
            and [x["nominal_total_kg"] for x in scenarios]==[1206,1176,1176]
            and all(x["validity"]=="CONDITIONAL_UNVERIFIED" for x in scenarios),
            "catalog mass-basis scenarios were promoted")
    model=d["physical_model"]
    require(not model["m527_equals_306_directly"]
            and model["catalog_30_kg_difference_is_not_additional_mass"]
            and not model["X_small_prior_empirical"]
            and model["eps_bound_kg"] is None
            and model["L_bound_kg"] is None and model["X_bound_kg"] is None
            and not model["active_physical_constraint"],"invalid conservation reference")
    mcmc=d["mcmc_bridge"]
    require(mcmc["no_evidence_for_model_weights"]
            and mcmc["no_historical_likelihood_for_306_as_m527"]
            and mcmc["require_latent_payload_stage_retention_at_separation"]
            and not d["historical_posterior_available"]
            and len(d["graph_edges"])==6,"unearned probabilistic evidence")
    return {
        "occurrence":"C61", "catalog_source":"GCAT",
        "payload_kg":306, "stage_wet_kg":900, "stage_dry_kg":870,
        "total_reported_kg":1176, "mass_sum_wet_kg":1206,
        "mass_sum_dry_kg":1176, "unresolved_basis_difference_kg":30,
        "different_source_definitions_are_not_simultaneous_measurements":True,
        "m527_equals_payload_306_proven":False,
        "conditional_scenarios":[x["id"] for x in scenarios],
        "historical_mass_posterior_available":False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    record=json.loads(MODEL.read_text(encoding="utf-8"))
    aux=json.loads(AUX.read_text(encoding="utf-8"))
    cat=json.loads(CAT.read_text(encoding="utf-8"))
    r=validate(record,MATRIX.read_text(encoding="utf-8"),aux,cat)
    out=json.dumps(r,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(out,encoding="utf-8")
    print(out,end="")

if __name__=="__main__":main()
