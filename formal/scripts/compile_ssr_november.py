#!/usr/bin/env python3
"""C241-P11: source-locked 1963 NASA Nov15/30 documentary measurements.

These are table entries, not raw tracking records. Time splits refer only to
publication dates. The November 30 issue is held out for prediction scoring.
"""
from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_nov15_1963_C241-L19.json"
OCTOBER = ROOT / "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"
SURVIVORS = ROOT / "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
REPORT = ROOT / "research/constraints/C241-P11_november_historical_printings.json"
LEAN = ROOT / "formal/Conde1963/SsrNovember.lean"
EXPECTED = {
    "1963-11-15": {
        "ntrs": "19640001198",
        "sha": "0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674",
        "bytes": 327613,
        "rows": {
            "1963-003A": ("94.6", "81.88", 536, 455),
            "1963-003C": ("92.6", "81.87", 420, 376),
        },
    },
    "1963-11-30": {
        "ntrs": "19640002493",
        "sha": "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d",
        "bytes": 1266393,
        "rows": {
            "1963-003A": ("94.6", "81.88", 533, 459),
            "1963-003C": ("92.2", "81.86", 390, 368),
        },
    },
}
FIELDS = {"period_min": 100, "inclination_deg": 100, "apogee_km": 2, "perigee_km": 2}
QUANTA = {"period_min": 10, "inclination_deg": 1, "apogee_km": 2, "perigee_km": 2}
OCT_SHA = "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2"
OCT_EXPECTED_ROWS = {
    "1963-003A": ("94.6", "81.89", "531", "462"),
    "1963-003C": ("93.3", "81.87", "458", "408"),
}


def scaled(value: object, factor: int) -> int:
    d = Decimal(str(value)) * factor
    if not d.is_finite() or d != d.to_integral_value():
        raise ValueError("bad printed precision")
    return int(d)


def normalized_rows(document: dict) -> dict:
    out = {}
    if len(document["rows"]) != 2:
        raise ValueError("unexpected row count")
    for row in document["rows"]:
        key = row["designator"]
        if key in out or key not in ("1963-003A", "1963-003C"):
            raise ValueError("incorrect or duplicate designator")
        out[key] = {f: scaled(row[f], factor) for f, factor in FIELDS.items()}
    return out


def validate(ledger: dict, october: dict, survivors: dict) -> dict:
    if ledger["id"] != "C241-L19" or len(ledger["documents"]) != 1:
        raise ValueError("November 15 ledger identity")
    nov15 = ledger["documents"][0]
    expected15 = EXPECTED["1963-11-15"]
    if (nov15["date"], nov15["ntrs"], nov15["sha256"],
        nov15["bytes"], nov15["page_index"], nov15["printed_page"],
        nov15["number"]) != (
        "1963-11-15", expected15["ntrs"], expected15["sha"],
        expected15["bytes"], 6, 5, 22):
        raise ValueError("Nov15 metadata, page or SHA mismatch")
    if nov15["pdf"] != (f"https://ntrs.nasa.gov/api/citations/"
                        f"{nov15['ntrs']}/downloads/{nov15['ntrs']}.pdf"):
        raise ValueError("non-canonical November 15 URL")
    docs = {"1963-11-15": normalized_rows(nov15)}
    for key, vals in expected15["rows"].items():
        row = next(r for r in nov15["rows"] if r["designator"] == key)
        if tuple(str(row[f]) for f in FIELDS) != tuple(map(str, vals)):
            raise ValueError("November 15 visual facsimile transcription mismatch")
    if any(ledger["limits"][k] for k in (
        "publication_date_is_observation_epoch", "instrumental_epoch_known",
        "individual_sensor_known", "covariance_known", "nasa_original_tle_pair",
        "physical_constraint_activated")):
        raise ValueError("unjustified November 15 sensor observation")
    if survivors["id"] != "C241-L18" or len(survivors["sources"]) != 3:
        raise ValueError("must use Tartaruga C241-L18, not a duplicate November 30 ledger")
    if survivors["data_lineage"]["original_instrument_tracking"]:
        raise ValueError("compiled NASA tables are not sensor raw data")
    nov30 = next((x for x in survivors["sources"] if x["published"] == "1963-11-30"), None)
    if nov30 is None:
        raise ValueError("Nov30 table missing from C241-L18")
    expected30 = EXPECTED["1963-11-30"]
    if (nov30["ntrs_id"], nov30["sha256"], nov30["bytes"],
            nov30["pdf_page_index"], nov30["printed_page"], nov30["issue"]) != (
            expected30["ntrs"], expected30["sha"], expected30["bytes"], 6, 5, 23):
        raise ValueError("Nov30 C241-L18 metadata, SHA or issue mismatch")
    if nov30["pdf_url"] != (f"https://ntrs.nasa.gov/api/citations/"
                            f"{nov30['ntrs_id']}/downloads/{nov30['ntrs_id']}.pdf"):
        raise ValueError("non-canonical November 30 URL")
    docs["1963-11-30"] = normalized_rows(nov30)
    for key, vals in expected30["rows"].items():
        row = next(r for r in nov30["rows"] if r["designator"] == key)
        if tuple(str(row[f]) for f in FIELDS) != tuple(map(str, vals)):
            raise ValueError("November 30 visual facsimile transcription mismatch")
    if (october["record_id"] != "C241-L12"
            or october["source"]["sha256"] != OCT_SHA
            or october["source"]["publication_date"] != "1963-10-15"):
        raise ValueError("October provenance is not the pinned ledger")
    october_rows = {}
    for row in october["catalog_rows"]:
        if row["international_designator"] in OCT_EXPECTED_ROWS:
            actual = tuple(str(row[f]) for f in (
                "nodal_period_min_printed", "inclination_deg_printed",
                "apogee_km_printed", "perigee_km_printed"))
            if actual != OCT_EXPECTED_ROWS[row["international_designator"]]:
                raise ValueError("October primary facsimile row mutated")
            october_rows[row["international_designator"]] = {
                f: scaled(row[{"period_min": "nodal_period_min_printed",
                               "inclination_deg": "inclination_deg_printed",
                               "apogee_km": "apogee_km_printed",
                               "perigee_km": "perigee_km_printed"}[f]], factor)
                for f, factor in FIELDS.items()
            }
    if len(october_rows) != 2:
        raise ValueError("October objects missing")
    return {"1963-10-15": october_rows, **docs}


def compile_report(ledger: dict, october: dict, survivors: dict) -> dict:
    series = validate(ledger, october, survivors)
    keys = ("1963-10-15", "1963-11-15", "1963-11-30")
    days = [(date.fromisoformat(keys[i+1]) -
             date.fromisoformat(keys[i])).days for i in (0, 1)]
    assert days == [31, 15]
    objects = []
    for key in ("1963-003A", "1963-003C"):
        rows = [series[k][key] for k in keys]
        diffs = {}
        for f, quantum in QUANTA.items():
            intervals = []
            for left, right in ((0, 1), (1, 2)):
                center = rows[left][f] - rows[right][f]
                intervals.append([center-quantum, center+quantum])
            diffs[f] = intervals
        # November 30 is never an input to either forecast.
        holdout = {}
        for f in ("period_min", "apogee_km"):
            p0, p1, actual = [row[f] for row in rows]
            predicted = (p1*days[0] + (p1-p0)*days[1]) / days[0]
            holdout[f] = {
                "persist_last_error": abs(p1-actual) / FIELDS[f],
                "linear_from_oct15_nov15_error": abs(predicted-actual) / FIELDS[f],
            }
        objects.append({
            "designator": key,
            "printed_values_scaled": rows,
            "oct15_minus_nov15_and_nov15_minus_nov30_bounds": diffs,
            "nov30_publication_holdout": holdout,
        })
    a, c = objects
    # C 529 (3C) robust Nov15->Nov30 decline in period and apogee,
    # and larger than A 527's conditional rounding intervals.
    expected_rank = {
        f: c["oct15_minus_nov15_and_nov15_minus_nov30_bounds"][f][1][0] >
           a["oct15_minus_nov15_and_nov15_minus_nov30_bounds"][f][1][1]
        for f in ("period_min", "apogee_km")
    }
    if not all(expected_rank.values()):
        raise ValueError("falsified November documentary ranking")
    return {
        "id": "C241-P11",
        "source_ids": ["C241-L12", "C241-L19#1", "C241-L18:19640002493", "C197#1"],
        "publication_dates": list(keys),
        "source_sha256": [OCT_SHA]+[EXPECTED[k]["sha"] for k in keys[1:]],
        "quantization_assumption": "nearest printed 0.1 min; 0.01 degree; 1 km, not sensor sigma",
        "quantization_units": {
            "period_min": "centiminute",
            "inclination_deg": "centidegree",
            "apogee_km": "half-kilometer",
            "perigee_km": "half-kilometer",
        },
        "difference_intervals_are_publication_table_only": True,
        "evaluation_holdout": "November 30 unobserved by predictors; October 15 and November 15 define fit",
        "holdout_dates_are_publication_dates_not_tracking_epochs": True,
        "same_compilation_not_independent_sensors": True,
        "norad_528_period_in_november": "NOT_IN_ORBIT_TABLE_DECAY_LISTED_08_NOV_C197",
        "physical_admissible_domain_change": "NONE",
        "instrumental_validation": "NOT_RUN_NO_ORIGINAL_SENSOR_EPOCH_FRAME_COVARIANCE",
        "objects": objects,
        "conditional_november_3c_gt_3a_drop": expected_rank,
        "source_graph_legacy_conflict": "Nov30 3A=94.6, not 94.8 in old ssr_1963_observable_graph.json",
    }


def render_lean(report: dict) -> str:
    a, c = report["objects"]
    out = [
        "import Lean", "",
        "namespace Conde1963.SsrNovember", "",
        "/-! Source-linked NASA 1963 3A / 3C November printed fields.",
        "Integer units: centiminutes for nodal periods, half-kilometers for apogee.",
        "Intervals assume nearest last printed digit; neither instrument sigma",
        "nor a claim about NORAD 528's terminal orbit. -/", "",
    ]
    for field, fslug in (("period_min", "period"), ("apogee_km", "apogee")):
        row_a = a["printed_values_scaled"]
        row_c = c["printed_values_scaled"]
        x1, x2 = row_c[1][field], row_c[2][field]
        y1, y2 = row_a[1][field], row_a[2][field]
        half = QUANTA[field]//2
        bound_c = c["oct15_minus_nov15_and_nov15_minus_nov30_bounds"][field][1]
        bound_a = a["oct15_minus_nov15_and_nov15_minus_nov30_bounds"][field][1]
        out.extend([
            f"/-- 3C Nov15->Nov30 {fslug} drop exceeds 3A,",
            "    only if published values are nearest-digit rounded. -/",
            f"theorem printed_november_{fslug}_3c_gt_3a",
            "    (c15 c30 a15 a30 : Int)",
            f"    (hc15lo : {x1-half} ≤ c15) (hc15hi : c15 ≤ {x1+half})",
            f"    (hc30lo : {x2-half} ≤ c30) (hc30hi : c30 ≤ {x2+half})",
            f"    (ha15lo : {y1-half} ≤ a15) (ha15hi : a15 ≤ {y1+half})",
            f"    (ha30lo : {y2-half} ≤ a30) (ha30hi : a30 ≤ {y2+half}) :",
            f"    ({bound_c[0]} ≤ c15 - c30 ∧ c15 - c30 ≤ {bound_c[1]}) ∧",
            f"    ({bound_a[0]} ≤ a15 - a30 ∧ a15 - a30 ≤ {bound_a[1]}) ∧",
            "    (a15 - a30 < c15 - c30) := by",
            "  omega", "",
        ])
    return "\n".join(out + ["end Conde1963.SsrNovember", ""])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = compile_report(json.loads(LEDGER.read_text()), json.loads(OCTOBER.read_text()), json.loads(SURVIVORS.read_text()))
    encoded = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    lean = render_lean(report)
    if args.check:
        if REPORT.read_text() != encoded or LEAN.read_text() != lean:
            raise SystemExit("C241-P11 generated artifact drift")
    else:
        REPORT.write_text(encoded)
        LEAN.write_text(lean)
    print("C241-P11: November table data, 2 objects, 2 publications, 4 fields, 2 holdout forecasts PASS")


if __name__ == "__main__":
    main()
