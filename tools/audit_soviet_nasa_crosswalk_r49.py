#!/usr/bin/env python3
"""Audit documentary numeric overlap without asserting sensor independence."""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "research" / "tle_custody"
CROSS = R / "soviet_nasa_crosswalk_C241_LONTRA_R49.json"


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def audit(cross, bse, nasa):
    require(cross["id"] == "C241-LONTRA-R49", "Wrong case")
    s = cross["sources"]
    require(s["soviet"]["ledger_id"] == bse["id"], "Wrong Soviet ledger")
    require(s["nasa"]["ledger_id"] == nasa["id"], "Wrong NASA ledger")
    require(s["soviet"]["print_page"] == bse["work"]["printed_page"] == 503,
            "Soviet page mismatch")
    require(s["soviet"]["pdf_page_one_based"] == bse["work"]["section_pdf_page_one_based"] == 7,
            "Soviet PDF page mismatch")
    require(s["soviet"]["printed_norad"] is None and
            bse["printed_table_row"]["norad_identifier_printed"] is None,
            "Unproven Soviet identity")
    require(s["soviet"]["publication_year"] == bse["work"]["publication_year"] == 1964,
            "Retrospective publication year mismatch")
    candidates = [x for x in nasa["sources"] if x["ntrs_id"] == s["nasa"]["ntrs_id"]]
    require(len(candidates) == 1, "Wrong NASA issue")
    report = candidates[0]
    for k in ("published", "as_of_utc"):
        require(s["nasa"][k] == report[k], "NASA issue date mismatch")
    require(s["nasa"]["print_page"] == report["printed_page"] == 5, "NASA print page mismatch")
    require(s["nasa"]["pdf_page_one_based"] == report["pdf_page_index"] + 1 == 7,
            "NASA PDF page mismatch")
    rows = [x for x in report["rows"] if x["designator"] == s["nasa"]["row_designator"]]
    require(len(rows) == 1 and rows[0]["designator"] == "1963-003A",
            "Do not conflate A with B/C")
    row, printed = rows[0], bse["printed_table_row"]
    fields = cross["comparison"]
    for name in ("perigee_km", "apogee_km"):
        pair = fields[name]
        require(pair["soviet"] == printed[name + "_printed"] and
                pair["nasa"] == row[name] and
                pair["soviet"] == pair["nasa"] and
                pair["match"] == "EXACT_IN_PRINT", "Wrong altitude match: " + name)
    for name, bse_key, nasa_key, delta in (
        ("period_min", "period_minutes_printed", "period_min", "0.06"),
        ("inclination_deg", "inclination_degrees_printed", "inclination_deg", "0.01")
    ):
        pair = fields[name]
        a, b = Decimal(str(pair["soviet"])), Decimal(str(pair["nasa"]))
        require(a == Decimal(str(printed[bse_key])) and b == Decimal(str(row[nasa_key])),
                "Wrong source field: " + name)
        diff_key = "absolute_difference_min" if name == "period_min" else "absolute_difference_deg"
        require(abs(a-b) == Decimal(delta) == Decimal(pair[diff_key]),
                "Wrong difference: " + name)
    require(Decimal(str(fields["period_min"]["soviet"])).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP) !=
        Decimal(str(fields["period_min"]["nasa"])),
        "Period is NOT a simple one-decimal rounding")
    require(fields["period_min"]["nasa_one_decimal_rounding_of_soviet"] is False,
            "False rounding equivalence")
    i = cross["interpretation"]
    for key in ("same_1963_003A_identity_confirmed_by_soviet_table",
                "direct_soviet_copy_from_this_nasa_issue_proven",
                "independent_soviet_sensor_or_time_utc_proven"):
        require(i[key] is False, "False documentary certainty: " + key)
    require(i["numeric_similarity_supports_crosswalk_candidate"] is True,
            "Numeric similarity erased")
    require(i["soviet_table_names_western_periodicals"] is True and
            bse["source_genealogy"]["independent_tracking_source_proven"] is False,
            "Historical source genealogy compromised")
    require(i["new_per_object_tracking_measurements"] == 0 and
            i["new_physical_constraints_activated"] == 0 and
            cross["external_archive_contact_sent"] is False,
            "Improper orbital activation or contact")
    return "PAIR_MATCH_BUT_PROVENANCE_UNRESOLVED"


def load():
    cross = json.loads(CROSS.read_text(encoding="utf-8"))
    bse = json.loads((ROOT / cross["sources"]["soviet"]["path"]).read_text(encoding="utf-8"))
    nasa = json.loads((ROOT / cross["sources"]["nasa"]["path"]).read_text(encoding="utf-8"))
    return cross, bse, nasa


if __name__ == "__main__":
    print(audit(*load()))
