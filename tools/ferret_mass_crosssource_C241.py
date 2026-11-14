#!/usr/bin/env python3
"""C241: keep Ferret 1500-kg secondary listings out of historical mass likelihood."""
import json
import re
from pathlib import Path

from tools.mass_identifiability_C241 import catalog_is_not_mass_inventory, rank, scenario_rows

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/ferret_1500_crosssource_C241.json"
GCAT = ROOT / "research/tle_custody/gcat_mass_semantics_C241-L40.json"


def audit(secondary=None, gcat=None):
    if secondary is None:
        secondary = json.loads(LEDGER.read_text(encoding="utf-8"))
    if gcat is None:
        gcat = json.loads(GCAT.read_text(encoding="utf-8"))
    catalog_is_not_mass_inventory(gcat)
    c = secondary["captured_page"]
    g = secondary["catalog_comparison"]
    i = secondary["interpretation"]
    entries = secondary["entries"]
    if not (
        secondary["schema"] == "conde.c241-ferret-mass-crosssource/v1"
        and secondary["id"] == "C241-CERVO-FERRET1500-20261114"
        and secondary["observation_kind"] == "MODERN_SECONDARY_LISTING_NOT_INSTRUMENTAL_MASS_MEASUREMENT"
        and secondary["astronautix_family"] == "ASTRONAUTIX_MARK_WADE_SECONDARY"
        and c["url"] == "https://astronautix.com/f/ferret.html"
        and c["bytes"] == 53630
        and re.fullmatch(r"[0-9a-f]{64}", c["sha256"])
        and c["sha256"] == "70fa299371bad0efd27ce920ea05bac60be38412521d9a6a3ead3162aaa20b63"
        and c["retrieval_utc_date"] == "2026-11-14"
        and g["ledger"] == "research/tle_custody/gcat_mass_semantics_C241-L40.json"
        and g["family"] == "GCAT_SECONDARY"
        and g["object"] == "S00527"
        and g["mass_kg"] == gcat["rows"]["S00527"]["mass_kg"] == 306
        and g["total_mass_kg"] == gcat["rows"]["S00527"]["total_mass_kg"] == 1176
        and g["launch_payload_plus_stage_mass_kg"] == (
            gcat["rows"]["S00527"]["mass_kg"] + gcat["rows"]["A00324"]["mass_kg"]
        ) == 1206
        and g["mass_528_kg"] is None and g["mass_529_kg"] is None
    ):
        raise ValueError("Source custody, mission identity, or GCAT comparison drift")
    if not (
        len(entries) == 3
        and [(x["norad"], x["reported_mass_kg"]) for x in entries]
        == [(242, 1500), (308, 1500), (527, 1500)]
        and entries[2]["cospar"] == "1963-003A"
        and entries[2]["upper_stage"] == "2313"
        and all(x["reported_mass_kg"] == 1500 for x in entries)
    ):
        raise ValueError("Repeated class-listing or OPS identity changed")
    if not (
        i["printed_1500_meaning"] == "UNRESOLVED_CLASS_OR_LAUNCH_CONFIG_VALUE"
        and i["repeated_same_value_across_three_missions"] is True
        and i["independent_instrument_or_engineering_measurement"] is False
        and i["independence_from_gcat_source_family"] is None
        and i["attribution_to_528_kg"] is None
        and i["common_mass_epoch_with_gcat"] is False
        and i["source_supports_separation_inventory"] is False
        and i["source_supports_1500_as_measured_mass_of_527"] is False
        and i["numerical_differences_are_physical_losses"] is False
        and i["historical_constraint_active"] is False
        and i["historical_mass_posterior"] is None
        and i["historical_mcmc"] == "NOT_RUN"
        and i["geographical_domain_reduction"] is False
        and i["historical_rank_of_527_528_529_X"] == 0
        and i["conditional_rank_if_authenticated_closed_inventory"] == 1
    ):
        raise ValueError("Uncalibrated source promoted to historical constraint")
    diff_tot = entries[2]["reported_mass_kg"] - g["total_mass_kg"]
    diff_launch = entries[2]["reported_mass_kg"] - g["launch_payload_plus_stage_mass_kg"]
    if not (
        diff_tot == i["nominal_difference_from_gcat_totmass_kg"] == 324
        and diff_launch == i["nominal_difference_from_payload_plus_stage_mass_kg"] == 294
        and rank([]) == 0
        and rank(scenario_rows(inventory_assumed=True)) == 1
    ):
        raise ValueError("Nominal comparisons or identifiability rank changed")
    return {
        "source_id": secondary["id"],
        "family_count_not_independent_measurements": 1,
        "repeated_nominal_ferret_mass_kg": 1500,
        "comparison_totmass_kg": g["total_mass_kg"],
        "comparison_nominal_kg": diff_tot,
        "comparison_launch_components_nominal_kg": diff_launch,
        "historical_partition_mass_rank": 0,
        "hypothetical_authenticated_inventory_rank": 1,
        "historical_constraint_active": False,
        "historical_mass_posterior": None,
        "historical_mcmc": "NOT_RUN",
        "geographical_domain_reduction": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
