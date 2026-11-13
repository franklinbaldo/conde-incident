#!/usr/bin/env python3
"""C241-P16: source-locked additive-bias falsification for NASA SSR 527/528/529.

Measures a *documentary-model* minimax radius, not orbital decay, instrument
accuracy or a physical bound. The four reports are different publications, not
four dated tracking observations; secondary crosswalk C241-L10 is conditional.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGERS = (
    ROOT / "research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json",
    ROOT / "research/tle_custody/nasa_ssr_jun30_1963_C241-L22.json",
    ROOT / "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json",
    ROOT / "research/tle_custody/nasa_ssr_aug15_1963_C241-L17.json",
)
REPORT = ROOT / "research/constraints/C241-P16_ssr_panel_minimax.json"
LEAN = ROOT / "formal/Conde1963/SsrFourEditions.lean"

# Independently expected values, as read in the pinned NASA facsimile ledgers.
# Never silently adapt the proof when a row or document is edited.
EXPECTED = (
    ("1963-04-30", "19630012128", "87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38",
     (9460, 9410, 9430), 5),
    ("1963-06-30", "19630012130", "8add4b46734e992a213088ef58ba9d58b6385df7b89bb504f79fe8715ec418f3",
     (9460, 9370, 9400), 5),
    ("1963-07-31", "19630012290", "9b00bf8323b1de80a34920f73c658f70f766a51632a13473a408679f0e5a03d9",
     (9460, 9360, 9390), 5),
    ("1963-08-15", "19630012289", "4e5cb0205577bc1b0959088db9ca3ae7a05f8de480b5ece9b86c385437636968",
     (9460, 9330, 9380), 5),
)
DESIGNATORS = ("1963-003A", "1963-003B", "1963-003C")
OBJECTS = ("527", "528", "529")
BASE = {"527": 9460, "528": 9370, "529": 9405}
BIAS = [20, 0, 0, -20]
RESIDUAL = {
    "527": [-20, 0, 0, 20],
    "528": [20, 0, -10, -20],
    "529": [5, -5, -15, -5],
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("C241-P16 source-lock: " + message)


def centimin(value: str) -> int:
    need(type(value) is str and bool(value), "period is not a printed string")
    n = Decimal(value)
    need(n.is_finite() and n > 0 and n * 10 == (n * 10).to_integral_value(),
         "period must be a printed tenth minute")
    return int(n * 100)


def audit_ledgers(docs: tuple[dict, ...]) -> tuple[list[dict], dict[str, list[int]]]:
    need(len(docs) == 4, "expected four original ledgers")
    apr, jun, jul, aug = docs
    need(apr.get("id") == "C241-L16" and
         apr.get("limits", {}).get("date_is_orbital_epoch") is False and
         apr.get("limits", {}).get("source_independence") == "NOT_ESTABLISHED" and
         apr.get("limits", {}).get("sigma") is None, "April lineage or epoch")
    need(jun.get("id") == "C241-L22" and
         jun.get("limits", {}).get("publication_is_element_epoch") is False and
         jun.get("limits", {}).get("independent_sensor_observation") is False and
         jun.get("limits", {}).get("measurement_sigma") is None and
         jun.get("limits", {}).get("physical_domain") == "THETA_UNCHANGED",
         "June lineage or physical activation")
    need(jul.get("id") == "C241-L18" and
         jul.get("data_lineage", {}).get("original_instrument_tracking") is False and
         jul.get("data_lineage", {}).get("source_report_reference_time_is_instrument_epoch") is False and
         jul.get("data_lineage", {}).get("measurement_uncertainty_sigma") is None,
         "July lineage or epoch")
    need(aug.get("id") == "C241-L17" and
         aug.get("limits", {}).get("publication_date_is_element_epoch") is False and
         aug.get("limits", {}).get("independent_sensor_observation") is False and
         aug.get("limits", {}).get("measurement_sigma") is None, "August lineage or epoch")

    sources = (apr["april"], jun["source"], jul["sources"][0], aug["source"])
    rows = (apr["april_rows"], jun["rows"], jul["sources"][0]["rows"], aug["rows"])
    dates = (sources[0]["publication"], sources[1]["publication_date"],
             sources[2]["published"], sources[3]["publication"])
    ids = (sources[0]["ntrs"], sources[1]["ntrs_id"],
           sources[2]["ntrs_id"], sources[3]["ntrs_id"])
    periods = {obj: [] for obj in OBJECTS}
    provenance = []
    for i, ((date, ntrs, sha, values, printed_page), src, day, pid, table) in enumerate(
        zip(EXPECTED, sources, dates, ids, rows)
    ):
        need((day, pid, src.get("sha256")) == (date, ntrs, sha),
             f"edition {i} identity/hash mismatch")
        need(len(table) == 3, f"edition {i} not three rows")
        need((src.get("printed_page") == printed_page), f"edition {i} page mismatch")
        for j, (row, designator, expected) in enumerate(zip(table, DESIGNATORS, values)):
            need(row.get("designator") == designator, f"edition {i}: object crosswalk changed")
            if i == 1:
                need(row.get("norad_crosswalk") == int(OBJECTS[j]), "June NORAD crosswalk changed")
            p = centimin(row["nodal_period_min"] if i in (0, 3) else row["period_min"])
            need(p == expected, f"edition {i} object {designator}: printed value altered")
            periods[OBJECTS[j]].append(p)
        provenance.append({
            "publication": date, "ntrs_id": ntrs,
            "document_sha256_claim_from_ledger": sha,
            "printed_page": printed_page, "ledger_path": str(LEDGERS[i].relative_to(ROOT)),
            "ledger_bytes_sha256": hashlib.sha256(LEDGERS[i].read_bytes()).hexdigest(),
            "source_status": "CONTEMPORARY_COMPILED_NASA_TABLE_NOT_RAW_TRACKING",
            "actual_tracking_epoch_utc": None,
        })
    return provenance, periods


def panel_minimum(periods: dict[str, list[int]]) -> int:
    """Lower bound: four residual differences bound change in a pair's gap.

    Valid bound for *any* 3×4 additive two-way fit. Tightness is certified
    separately by an explicit 12-cell witness. It is not a generic LP solver.
    """
    need(set(periods) == set(OBJECTS) and all(len(v) == 4 for v in periods.values()),
         "malformed three-object four-edition panel")
    gap = [periods["527"][i] - periods["528"][i] for i in range(4)]
    return (max(gap) - min(gap) + 3) // 4


def build(docs: tuple[dict, ...]) -> dict:
    provenance, periods = audit_ledgers(docs)
    lower = panel_minimum(periods)
    need(lower == 20, "unexpected lower bound from printed April/August gap")
    for obj in OBJECTS:
        for i, actual in enumerate(periods[obj]):
            e = RESIDUAL[obj][i]
            need(actual == BASE[obj] + BIAS[i] + e, "witness does not reproduce a cell")
            need(abs(e) <= lower, "witness violates minimax budget")
    return {
        "schema": "conde.ssr-three-objects-four-editions-additive-bias/v1",
        "id": "C241-P16",
        "parent_evidence": ["C241-L10", "C241-L16", "C241-L17", "C241-L18", "C241-L22"],
        "parent_graph": "research/constraints/ssr_1963_observable_graph.json",
        "source_documents": provenance,
        "crosswalk": dict(zip(OBJECTS, DESIGNATORS)),
        "unit": "centiminute (0.01 minute)",
        "printed_period_by_object": periods,
        "difference_527_minus_528": [periods["527"][i] - periods["528"][i] for i in range(4)],
        "model": "P[obj,edition] = B[obj] + H[edition] + e[obj,edition], abs(e)<=E",
        "lower_bound_basis": "April/August difference-of-differences for 527 and 528",
        "exact_minimax_centiminute": lower,
        "exact_minimax_seconds": 12,
        "conditional_print_rounding_halfunit_centiminute": 5,
        "ratio_to_print_rounding_halfunit": 4,
        "attaining_witness": {
            "object_baselines_centiminute": BASE,
            "shared_edition_bias_centiminute": BIAS,
            "per_object_edition_residual_centiminute": RESIDUAL,
        },
        "scientific_claim": "0.05-minute per-cell rounding alone falsifies the restricted shared-additive-edition-bias model; 0.20-minute per-cell free residual is necessary and sufficient for these twelve printed cells",
        "uses": ["compiled_period_527", "compiled_period_528", "compiled_period_529",
                 "latent_report_bias", "latent_instrument_epoch_each_cell",
                 "latent_kinematic_state_each_object", "candidate_common_forces"],
        "rejected_edges": [
            "publication_date -> orbital_instrument_epoch",
            "printed_period_gap -> physical_decay_rate",
            "printed_cell_residual -> sensor_sigma",
            "twelve_compiled_cells -> twelve_independent_instrument_observations",
            "documentary_minimax -> physical_theta_reduction",
        ],
        "actual_tracking_epoch_utc": None,
        "tracking_frame": None, "instrument_sigma": None,
        "independent_instrument_samples_added": 0,
        "status": "CONNECTED_PENDING_CALIBRATION",
        "physical_admissible_domain": "THETA_UNCHANGED",
        "historical_conclusion": "INDETERMINATE",
        "lean_file": str(LEAN.relative_to(ROOT)),
    }


def render_lean(r: dict) -> str:
    p = r["printed_period_by_object"]
    w = r["attaining_witness"]
    lines = [
        "import Lean", "",
        "namespace Conde1963.SsrFourEditions", "",
        "/-! C241-P16 documentary model only; 0.01-minute units. Four publication",
        "dates do not specify 12 independent orbital measurements, and this",
        "minimax bound does not restrict any physical state or terminal location. -/", "",
        "/-- April/August 527-minus-528 gaps change from 50 to 130 centimin.",
        "A shared edition bias cancels; four bounded residuals must absorb 80. -/",
        "theorem shared_edition_model_needs_twenty",
        "    (baseA baseB hApr hAug eaApr eaAug ebApr ebAug E : Int)",
        f"    (aApr : {p['527'][0]} = baseA + hApr + eaApr)",
        f"    (aAug : {p['527'][3]} = baseA + hAug + eaAug)",
        f"    (bApr : {p['528'][0]} = baseB + hApr + ebApr)",
        f"    (bAug : {p['528'][3]} = baseB + hAug + ebAug)",
    ]
    for e in ("eaApr", "eaAug", "ebApr", "ebAug"):
        lines.extend([f"    ({e}Lo : -E ≤ {e})", f"    ({e}Hi : {e} ≤ E)"])
    lines += ["    : 20 ≤ E := by", "  omega", "",
              "/-- All twelve cells admit E=20 with one object baseline each and",
              "one shared bias per publication. Thus the lower bound is sharp. -/",
              "theorem all_twelve_cells_attain_twenty :",
              "    ∃ (baseA baseB baseC hApr hJun hJul hAug : Int),"]
    clauses = []
    for j, obj in enumerate(OBJECTS):
        base = ("baseA", "baseB", "baseC")[j]
        for i, h in enumerate(("hApr", "hJun", "hJul", "hAug")):
            e = w["per_object_edition_residual_centiminute"][obj][i]
            clauses.append(f"      ({p[obj][i]} = {base} + {h} + ({e}))")
    lines += [" ∧".join(clauses) + " := by",
              "  refine ⟨9460, 9370, 9405, 20, 0, 0, -20, ?_⟩",
              "  omega", "", "end Conde1963.SsrFourEditions", ""]
    return "\n".join(lines)


def run(check: bool) -> None:
    docs = tuple(json.loads(f.read_text()) for f in LEDGERS)
    report = build(docs)
    blob = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    proof = render_lean(report)
    if check:
        need(REPORT.read_text() == blob and LEAN.read_text() == proof,
             "generated file diverged from source-locked ledgers")
        print("C241-P16 PASS: sharp 20 centimin documentary residual; Theta unchanged")
    else:
        REPORT.write_text(blob)
        LEAN.write_text(proof)
        print("C241-P16 generated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args().check)
