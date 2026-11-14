#!/usr/bin/env python3
"""Audit modern metadata for 527; never transfer it to 528."""
import json
import math
from pathlib import Path
from tools.mass_identifiability_C241 import catalog_is_not_mass_inventory

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/ftv2313_gmspazio_secondary_C241.json"
GCAT = ROOT / "research/tle_custody/gcat_mass_semantics_C241-L40.json"


def audit(ledger=None, gcat=None):
    if ledger is None:
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if gcat is None:
        gcat = json.loads(GCAT.read_text(encoding="utf-8"))
    catalog_is_not_mass_inventory(gcat)
    s, obj = ledger["source"], ledger["listing"]
    g, status = ledger["gcat_comparison"], ledger["interpretation"]
    if not (
        ledger["schema"] == "conde.c241-ftv2313-secondary-geometry/v1"
        and ledger["id"] == "C241-CERVO-FTV2313-L49"
        and s == {
            "url": "https://findyourobject.gmspazio.com/en/en/obj/14/699/ftv-2313.aspx",
            "consulted_utc_date": "2026-11-14",
            "retrieval": "WEB_TEXT_INDEXED",
            "binary_sha256": None,
            "binary_verification": "NOT_VERIFIED_TLS_CERTIFICATE_ERROR",
            "publisher_lineage_from_gcat": None,
        }
        and obj == {
            "name": "FTV 2313", "norad": 527, "cospar": "1963-003A",
            "mass_label": "Mass (kg)", "mass_kg": 1176, "shape": "Cyl + Irr",
            "diameter_m": 1.5, "height_m": 7.99,
            "lifetime_label": "6 - 10 days",
            "narrative_operational_duration": "two days after battery failure",
        }
        and g["source_ledger"] == "research/tle_custody/gcat_mass_semantics_C241-L40.json"
        and g["object"] == "S00527"
        and g["field"] == "TotMass"
        and g["value_kg"] == gcat["rows"]["S00527"]["total_mass_kg"] == 1176
        and g["same_field_semantics_verified"] is False
        and g["same_physical_epoch_verified"] is False
        and status == {
            "dimensions_are_528_dimensions": False,
            "geometry_is_verified_exact_cylinder": False,
            "mass_is_independent_instrumental_measurement": False,
            "source_independence_from_gcat_established": False,
            "secondary_1176_is_a_closed_inventory_527_528_529": False,
            "physical_lifetime_6_to_10_days_of_527_established": False,
            "operational_lifetime_is_orbital_reentry_lifetime": False,
            "historical_mass_rank_increase": 0,
            "historical_mcmc": "NOT_RUN",
            "posterior_mass_528_kg": None,
            "geographic_domain_reduction": False,
        }
    ):
        raise ValueError("Unverified metadata promoted to physical measurement")
    d, length = obj["diameter_m"], obj["height_m"]
    # Ideal circular cylinder only: A(theta)=cap*abs(cos)+side*abs(sin).
    cap, side = math.pi * d * d / 4, d * length
    peak = math.hypot(cap, side)
    if not (0 < cap < side < peak):
        raise ValueError("Hypothetical cylinder geometry drift")
    return {
        "source_id": ledger["id"], "object_for_listing": 527,
        "hypothetical_geometry_only": True,
        "end_on_area_m2": cap, "side_on_area_m2": side,
        "max_orientation_area_m2": peak,
        "max_to_end_area_ratio": peak / cap,
        "historical_528_area_m2": None,
        "independent_mass_observations_added": 0,
        "historical_mcmc": "NOT_RUN",
        "geographic_domain_reduction": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
