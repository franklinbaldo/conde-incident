#!/usr/bin/env python3
"""Source-locked audit of conditional C241 mass constraints across consumers.

No claim about historical 1963 mass, size, area, drag or posterior is promoted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"research/constraints/C241_mass_crossmodel_routing_2026-11-13.json"
SOURCE=ROOT/"research/constraints/C241_mass_budget_residual_2026-11-13.json"
MATRIX=ROOT/"research/evidence_matrix_C001-C238_2026-11-11.md"

def require(ok,why):
    if not ok:raise ValueError(why)

def validate(data,source,matrix,file_reader):
    require(data["schema"]=="conde.c241-shared-mass-model-routing/v1"
            and data["id"]=="C241-MASS-CROSSMODEL-20261113"
            and data["status"]=="CONDITIONAL_MODEL_COUPLING_NO_HISTORICAL_POSTERIOR",
            "routing identity")
    line=[s for s in matrix.splitlines() if s.startswith("| C61 |")]
    require(len(line)==1 and "~306 kg" in line[0] and "~1176 kg" in line[0],
            "C61 secondary catalogue provenance")
    require(source["id"]=="C241-MASS-X-20261113"
            and source["source"]["associated_total_mass_kg_approx"]==1176
            and source["source"]["observed_individual_mass_of_528_kg"] is None
            and not source["conditional_budget"]["physically_calibrated_historical_constraint"]
            and not source["conditional_budget"]["closed_three_body_equation_activated"]
            and source["conditional_derived_bounds"]["E_kg"] is None
            and source["conditional_derived_bounds"]["R_kg"] is None,
            "unverified budget promoted as measured mass")
    src=data["source"]
    require(src["primary_matrix_occurrence"]=="C61"
            and src["committed_budget"]==
              "research/constraints/C241_mass_budget_residual_2026-11-13.json"
            and src["reviewed_catalogue_source"].endswith("/pull/629")
            and src["named_reference_total_kg_approx"]==1176
            and src["payload_527_component_mass_kg"]==306
            and src["payload_527_dry_mass_kg"]==306
            and src["agena_stage_mass_kg"]==900
            and src["agena_stage_dry_mass_kg"]==870
            and src["separate_insertion_mass_sum_kg"]==1206
            and src["individual_528_mass_kg"] is None
            and src["individual_529_mass_kg"] is None
            and src["catalogue_uncertainty_kg"] is None
            and src["initial_mass_accounting_epoch"] is None
            and not src["mass_related_sources_independent_sensors"],
            "catalogue mass definitions/lineage changed")
    c=data["scenario_contract"]
    require(c["type"]=="conde.conditional-three-object-mass/v1"
            and c["adapter"]=="src/lib/orbitMassConstraints.ts"
            and c["must_explicitly_choose_mass_basis"]
            and c["mass_bases_kg"]=={
                "GCAT_TOTMASS_1176":1176,
                "PAYLOAD_PLUS_STAGE_DRY_1176":1176,
                "PAYLOAD_PLUS_STAGE_AT_INSERTION_1206":1206}
            and c["posterior_prior_from_306kg"] is None
            and c["unconditional_individual_mass_bound_kg"] is None
            and not c["historical_activation"],
            "conditional accounting promoted to hard historical limits")
    require(len(c["unknowns"])>=10 and len(c["equations"])==5,
            "unconnected unknowns or drag equation")
    records=data["consumers"]
    require(len(records)==12 and len({r["id"] for r in records})==12,
            "missing/duplicated consumer registry")
    expected={
      "cartesian-j2-drag":"src/lib/orbitPhysics.ts",
      "source-declared-msise-density":"src/lib/orbitSpaceWeatherAdapter.ts",
      "inverse-ballistic":"src/lib/inverseSolver.ts",
      "exploratory-monte-carlo":"src/lib/monteCarlo.ts",
      "scalar-j2-drag-proxy":"tools/norad528_effective_drag_screen.py",
      "bayesian-mass-partition":"https://github.com/franklinbaldo/conde-incident/pull/634",
      "equivalent-fragment-dimensions":"src/lib/orbitMassConstraints.ts",
      "angular-sibling-orbit-geometry":
        "research/tle_custody/evidence_matrix_C241-orbital-screen_2026-11-13.md",
      "atmosphere-sensitivity-legacy-ui":"src/components/AtmosphereSensitivity.tsx",
      "fragment-survival-and-deposition":"research/ORBIT_ENERGY_BUDGET.md",
      "mass-budget-and-X":"tools/mass_budget_527_529.py",
      "mass-budget-lean":"formal/Conde1963/MassBudget527529.lean"
    }
    require({r["id"]:r["path"] for r in records}==expected,
            "known mass-related model consumers omitted/changed")
    require(all(r["historical_constraint_active"] is False for r in records),
            "unearned historical mass inference")
    for record in records:
        path=record["path"]
        require(isinstance(record["effect"],str) and len(record["effect"])>12,
                "consumer effect must be explicit")
        if path.startswith("https://github.com/"):
            require(record["id"]=="bayesian-mass-partition",
                    "non-repository consumer must be named PR")
        else:
            file_reader(path)
    markers={
      "src/lib/orbitMassConstraints.ts":[
        "auditMassBudgetScenario","atmosphereForMassScenario",
        "conditionalProjectedAreaEnvelope","historicalConstraintActive: false",
        "GCAT_MASS_FIELDS"],
      "src/lib/orbitSpaceWeatherAdapter.ts":["makeConditionalMassBudgetMsiseAtmosphere",
          "ballisticFromMassScenario"],
      "src/lib/inverseSolver.ts":["conditionalBallisticCompatibility","massOptions"],
      "src/lib/monteCarlo.ts":["ballisticFromMassScenario","conditionalMassScenario"],
      "src/lib/orbitPhysics.ts":["cdAreaOverMassM2Kg"],
    }
    for path,tokens in markers.items():
        body=file_reader(path)
        require(all(t in body for t in tokens),
                "mass constraint consumer missing actual adapter: "+path)
    inv=data["invariants"]
    require(inv["all_consumer_historical_mass_constraints_active"]==0
            and inv["legacy_RAAN_2841520_not_rescued_by_mass"]
            and inv["GCAT_306_is_not_entire_527_physical_mass"]
            and inv["X_not_assumed_small"]
            and inv["no_posterior_from_nominal_mass_alone"]
            and inv["no_1963_object_size_inferred"]
            and inv["terminal_date_does_not_calibrate_B_without_time_error"]
            and inv["source_reconciliation_required_before_hard_mass_filter"],
            "scientific activation gates bypassed")
    return {
      "id":data["id"],
      "consumers_catalogued":len(records),
      "conditional_bridges_implemented":4,
      "historical_mass_constraints_activated":0,
      "physical_historical_mass_range_kg":None,
      "historical_mcmc_posterior":None,
      "source_reconciliation":"C241-L40/PR629_PENDING",
      "new_angular_precision_from_mass":False,
      "interpretation":"CONDITIONAL_CROSSMODEL_EVIDENCE_GRAPH_ONLY"
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path)
    args=a.parse_args()
    def read(path):return (ROOT/path).read_text(encoding="utf-8")
    result=validate(json.loads(MODEL.read_text(encoding="utf-8")),
        json.loads(SOURCE.read_text(encoding="utf-8")),
        MATRIX.read_text(encoding="utf-8"),read)
    output=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output,encoding="utf-8")
    print(output,end="")

if __name__=="__main__": main()
