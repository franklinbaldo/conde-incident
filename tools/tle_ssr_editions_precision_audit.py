#!/usr/bin/env python3
"""C241-L27: source-pinned NASA SSR edition sequence, NOT sensor observations.

Collate compiled table lines from nine already-audited editions. Do not infer
measurement epochs, error distributions, orbital derivatives or reentry times.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "research/tle_custody/nasa_ssr_editions_precision_C241-L27.json"
DECAY = "research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json"
NAMES = {
    "1963-003A": 527,
    "1963-003B": 528,
    "1963-003C": 529,
}
FIELDS = ("nodal_period_min", "inclination_deg", "apogee_km", "perigee_km")


def check(predicate, problem):
    if not predicate:
        raise ValueError(problem)


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def select(source, selector):
    if selector == "april":
        return source["april"], source["april_rows"], "april"
    if selector == "source":
        return source["source"], source.get("rows", source.get("catalog_rows")), "source"
    if selector.startswith("sources[") and selector.endswith("]"):
        index = int(selector[8:-1])
        item = source["sources"][index]
        return item, item["rows"], "sources"
    if selector == "documents[0]":
        item = source["documents"][0]
        return item, item["rows"], "documents"
    raise ValueError("unknown source selector")


def source_metadata(item, selector, container):
    if selector == "april":
        return (item["ntrs"], item["publication"], 9,
                item["pdf_page_index_zero_based"], item["printed_page"],
                item["sha256"], item["url"])
    if selector == "documents[0]":
        return (item["ntrs"], item["date"], item["number"],
                item["page_index"], item["printed_page"],
                item["sha256"], item["pdf"])
    if container == "sources":
        return (item["ntrs_id"], item["published"], item["issue"],
                item["pdf_page_index"], item["printed_page"],
                item["sha256"], item["pdf_url"])
    if "publication_date" in item:
        # October C241-L12, and June/December C241-L21
        return (item["ntrs_id"], item["publication_date"],
                item.get("issue", item.get("number")),
                item.get("pdf_page_index_zero_based", item.get("page_index_zero_based")),
                item.get("printed_page", item.get("page_printed")),
                item["sha256"], item["pdf_url"])
    return (item["ntrs_id"], item["publication"], item["number"],
            item["pdf_page_index_zero_based"], item["printed_page"],
            item["sha256"], item["pdf_url"])


def normalize_row(row):
    designation = row.get("designator", row.get("international_designator"))
    check(designation in NAMES, "unexpected international designator")
    if "nodal_period_min" in row:
        period = row["nodal_period_min"]
    elif "nodal_period_min_printed" in row:
        period = row["nodal_period_min_printed"]
    else:
        period = row["period_min"]
    inclination = row.get("inclination_deg", row.get("inclination_deg_printed"))
    apogee = row.get("apogee_km", row.get("apogee_km_printed"))
    perigee = row.get("perigee_km", row.get("perigee_km_printed"))
    check(type(period) is str and type(inclination) is str, "decimal print lost")
    check(type(apogee) is int and type(perigee) is int, "integer print lost")
    check(Decimal(period) > 0 and Decimal(inclination) > 0
          and apogee >= perigee > 0, "invalid printed orbit")
    check(Decimal(period).as_tuple().exponent == -1
          and Decimal(inclination).as_tuple().exponent == -2,
          "decimal print resolution changed")
    return designation, period, inclination, apogee, perigee


def validate(model, ledgers, decay):
    check(model["schema"] == "conde.ssr-edition-quantization-sequence/v1"
          and model["id"] == "C241-L27", "wrong model")
    check(model["source_family"] == "NASA_GODDARD_NORAD_SAO_COMPILED_SAME_UPSTREAM"
          and model["independent_sensor_observations_added"] == 0
          and model["independent_source_family_count"] == 1,
          "independent source overcount")
    check(model["secondary_norad_crosswalk"] == NAMES
          and model["quantization_status"] ==
          "PRINTED_DECIMAL_RESOLUTION_ONLY_NEAREST_ROUNDING_NOT_VERIFIED"
          and model["nominal_half_steps_if_nearest_rounding"] == {
              "period_min": "0.05", "inclination_deg": "0.005",
              "apogee_km": "0.5", "perigee_km": "0.5"}
          and not model["nominal_half_steps_are_sensor_sigma"]
          and not model["printed_as_of_is_tracking_epoch"]
          and not model["publication_gap_is_tracking_interval"]
          and not model["report_rounding_rule_verified"],
          "printing digits promoted to instrumental accuracy")
    for field in ("raw_instrument_528_time", "raw_instrument_528_sensor",
                  "raw_instrument_528_sigma"):
        check(model[field] is None, "invented sensor record for 528")
    original = decay["sources"][0]
    check(original["ntrs_id"] == "19640001198"
          and original["human_table_observation"]["object_printed"] == "1963 3B"
          and original["human_table_observation"]["decay_day"] ==
          model["guarded_facts"]["nov15_3b_decay_day"] == "1963-11-08",
          "decay day cross-ledger mismatch")
    docs = model["docs"]
    check(len(docs) == 9 and len({d["ntrs"] for d in docs}) == 9
          and len({(d["published"], d["issue"]) for d in docs}) == 9
          and [d["published"] for d in docs] ==
          sorted(d["published"] for d in docs), "missing/duplicate edition")
    rows = []
    for doc in docs:
        ledger = ledgers[doc["ledger"]]
        source, raw_rows, selector_kind = select(ledger, doc["selector"])
        got = source_metadata(source, doc["selector"], selector_kind)
        expected_url = (
            "https://ntrs.nasa.gov/api/citations/"
            + doc["ntrs"] + "/downloads/" + doc["ntrs"] + ".pdf"
        )
        check(got == (doc["ntrs"], doc["published"], doc["issue"],
                      doc["pdf_page_index"], doc["printed_page"],
                      doc["pdf_sha256"], expected_url),
              "document metadata or SHA changed: " + doc["ntrs"])
        expected_objects = doc["objects"]
        parsed = [normalize_row(row) for row in raw_rows]
        check([NAMES[row[0]] for row in parsed] == expected_objects
              and len(set(row[0] for row in parsed)) == len(parsed),
              "row count/order or object membership changed: " + doc["ntrs"])
        for designation, period, inclination, apogee, perigee in parsed:
            rows.append({
                "source_ntrs": doc["ntrs"],
                "source_ledger": doc["ledger"],
                "source_sha256": doc["pdf_sha256"],
                "publication_day_NOT_sensor_epoch": doc["published"],
                "report_issue": doc["issue"],
                "norad_id_secondary_crosswalk": NAMES[designation],
                "designator_as_normalized": designation,
                "printed": {
                    "nodal_period_min": period,
                    "inclination_deg": inclination,
                    "apogee_km": apogee,
                    "perigee_km": perigee,
                },
                "instrument_observation_epoch": None,
                "instrument_sensor": None,
                "instrument_sigma": None,
                "forward_operator": "SSR_compiled_orbit(state,latent_epoch,convention,fit)",
                "status": "CONNECTED_PENDING_CALIBRATION",
                "printed_precision_is_instrument_accuracy": False,
            })
    check(len(rows) == 23, "unexpected source row count")
    counts = Counter(r["norad_id_secondary_crosswalk"] for r in rows)
    check(counts == {527: 9, 528: 5, 529: 9},
          "documentary membership mismatch")
    july = next(r for r in rows
                if r["source_ntrs"] == "19630012290"
                and r["norad_id_secondary_crosswalk"] == 529)
    december = next(r for r in rows
                    if r["source_ntrs"] == "19640005618"
                    and r["norad_id_secondary_crosswalk"] == 529)
    check(july["printed"]["perigee_km"] ==
          model["guarded_facts"]["july_3c_perigee_km"] == 452,
          "July 3C erratum regressed 452->425")
    check(december["printed"]["nodal_period_min"] ==
          model["guarded_facts"]["dec31_3c_period_min"] == "89.2",
          "December 3C erratum regressed 89.2->89.6")
    check(max(r["publication_day_NOT_sensor_epoch"] for r in rows
              if r["norad_id_secondary_crosswalk"] == 528) ==
          "1963-10-15"
          and model["guarded_facts"]["oct15_last_3b_compiled_listing"],
          "528 documentary last-in-orbit row changed")
    check(model["guarded_facts"]["nov15_3b_in_objects_in_orbit"] is False
          and model["guarded_facts"]["oct27_secondary_mirror_epoch_not_in_ssr"],
          "secondary epoch or catalog absence improperly promoted")
    graph = model["graph"]
    check(graph["parent"] == "research/constraints/ssr_1963_observable_graph.json"
          and graph["new_editorial_sequence_edges"] == 8
          and graph["physical_constraints_active"] == 0
          and not graph["uncertainty_domain_reduced"]
          and not graph["lean_promoted"]
          and graph["link_status"] == "CONNECTED_PENDING_CALIBRATION",
          "invalid physical activation")
    return {
        "record_id": model["id"],
        "distinct_compiled_NASA_editions": len(docs),
        "linked_compiled_rows": len(rows),
        "rows_per_object_NORAD_secondary_crosswalk": dict(sorted(counts.items())),
        "instrumental_observations_added": 0,
        "reporting_family": model["source_family"],
        "nominal_half_steps_only_if_nearest_rounding": model["nominal_half_steps_if_nearest_rounding"],
        "precision_is_not_sensor_sigma": True,
        "physical_constraints_active": 0,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    model = read(MODEL)
    ledgers = {d["ledger"]: read(d["ledger"]) for d in model["docs"]}
    result = validate(model, ledgers, read(DECAY))
    output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(json.dumps({k: v for k, v in result.items() if k != "rows"},
                         ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
