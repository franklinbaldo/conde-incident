#!/usr/bin/env python3
"""Link verified NASA Nov/Dec 529 table cells to Lean and latent simulator inputs.

The two reports are compilations, not sensor epochs. No physical parameter is
activated by the printed difference or by resolving transcription C227.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from export_ssr_source_locked_links import render as render_november_bridge
from tle_nasa_ssr_jul_dec_audit import validate as validate_nasa_ledger

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
NOVEMBER = ROOT / "public/data/conde-ssr-source-locked-links.json"
OUT = ROOT / "public/data/conde-ssr-december-bridge.json"


def build(ledger: dict, november: dict) -> dict:
    """Require both source ledgers and the upstream canonical November bridge."""
    audited = validate_nasa_ledger(ledger)
    if november != json.loads(render_november_bridge()):
        raise ValueError("November bridge is stale or has altered source custody")
    if (november.get("active_physical_constraint") is not False
        or november.get("physical_domain_effect") != "THETA_UNCHANGED"
        or november.get("checked_distinct_control_objects") != [527, 529]):
        raise ValueError("November documentary controls promoted into physics")
    nov, dec = ledger["sources"][1:]
    if (nov["ntrs_id"], dec["ntrs_id"]) != ("19640002493", "19640005618"):
        raise ValueError("wrong NASA source editions")
    if (nov["rows"][1]["designator"] != "1963-003C"
        or dec["rows"][1]["designator"] != "1963-003C"):
        raise ValueError("529 identity mismatch")
    nov_c = Decimal(nov["rows"][1]["period_min"])
    dec_c = Decimal(dec["rows"][1]["period_min"])
    nov_a = Decimal(nov["rows"][0]["period_min"])
    dec_a = Decimal(dec["rows"][0]["period_min"])
    if ((nov_c, dec_c, nov_a, dec_a) !=
        (Decimal("92.2"), Decimal("89.2"), Decimal("94.6"), Decimal("94.6"))):
        raise ValueError("NASA table values differ from verified editions")
    if audited["529_nov_dec_printed_delta_min_if_dec_reading_is_89_2"] != "3.0":
        raise ValueError("reconciled printed-period delta lost")
    if (november["canonical_value_min"] != "94.6"
        or november["linked_sources"][1]["pdf_sha256"] != nov["sha256"]):
        raise ValueError("upstream November source lock missing")
    sources = []
    for source, occurrence, context in (
        (nov, "C241-L18:19640002493", ["C183#1", "C199#1"]),
        (dec, "C241-L18:19640005618", ["C227#1"]),
    ):
        sources.append({
            "occurrence_id": occurrence,
            "ntrs": source["ntrs_id"],
            "url": source["pdf_url"],
            "pdf_sha256": source["sha256"],
            "pdf_bytes": source["bytes"],
            "pdf_page_index": source["pdf_page_index"],
            "printed_page": source["printed_page"],
            "report_published_on": source["published"],
            "report_as_of_utc_not_sensor_epoch": source["as_of_utc"],
            "matrix_context_not_independent_sensor": context,
        })
    return {
        "schema": "conde.ssr-december-source-bridge/v1",
        "id": "C241-L18-NOV-DEC-529-ERRATUM",
        "source_ledger": LEDGER.relative_to(ROOT).as_posix(),
        "upstream_bridge": NOVEMBER.relative_to(ROOT).as_posix(),
        "source_family": "NASA_GODDARD_NORAD_SMITHSONIAN_COMPILED_REPORTS",
        "source_editions": sources,
        "same_institutional_family_not_independent_sensors": True,
        "erratum_matrix_occurrence": "C227#1",
        "erratum_superseded_printed_min": "89.6",
        "erratum_verified_printed_min": str(dec_c),
        "erratum_state": dec["transcription_conflict"]["status"],
        "control_529_printed_periods_min": [str(nov_c), str(dec_c)],
        "control_527_printed_periods_min": [str(nov_a), str(dec_a)],
        "control_529_printed_delta_min": str(nov_c - dec_c),
        "control_527_printed_delta_min": str(nov_a - dec_a),
        "conditional_rounding_model": "nearest_0.1_min_not_instrument_sigma",
        "conditional_529_delta_range_min": ["2.90", "3.10"],
        "conditional_527_delta_range_min": ["-0.10", "0.10"],
        "conditional_differential_range_min": ["2.80", "3.20"],
        "lean_contract": "formal/Conde1963/SsrSurvivorIntervals.lean",
        "lean_theorem": "post_b_529_reconciled_printed_gap_over_527",
        "lean_claim_scope": "conditional_printed_table_comparison_only",
        "simulation_bridge": "C241-P10-three-object-relative-trajectories",
        "simulator_latent_parameters": [
            "state_527(t)", "state_529(t)", "atmosphere_shared_1963",
            "ballistic_coefficient_527", "ballistic_coefficient_529",
            "sensor_epoch_each_row", "report_latency_each_row",
            "instrument_covariance", "forward_model_period_convention",
        ],
        "sensor_epochs_utc": None,
        "sensor_covariance": None,
        "source_to_instrument_mapping_verified": False,
        "active_physical_constraint": False,
        "status": "CONNECTED_PENDING_CALIBRATION",
        "physical_domain_effect": "THETA_UNCHANGED",
        "pending": ["sensor_records", "epochs", "reference_frame", "covariance",
                    "ballistic_coefficients", "calibrated_forward_model"],
    }


def render() -> str:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    november = json.loads(NOVEMBER.read_text(encoding="utf-8"))
    return json.dumps(build(ledger, november), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--write-site", action="store_true")
    p.add_argument("--check-site", action="store_true")
    a = p.parse_args()
    payload = render()
    if a.write_site:
        OUT.write_text(payload, encoding="utf-8")
    if a.check_site and OUT.read_text(encoding="utf-8") != payload:
        raise SystemExit("stale NASA December scientific bridge")
    print("C241-L18: 529 November/December printed delta 3.0 min; Θ unchanged")


if __name__ == "__main__":
    main()
