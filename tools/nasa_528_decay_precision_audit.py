#!/usr/bin/env python3
"""Verify source-linked NASA 528 decay-day precision metadata without inferring a terminal time."""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "research/constraints/nasa_528_decay_precision_C197_20261113.json",
    "research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json",
    "research/constraints/morcego_norad_1963_radar_source_audit.json",
    "research/statistics/raan_catalog_day_missingness_C241.json",
]
PIN = "0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674"
UNKNOWNS = (
    "last_528_sensor_epoch_utc", "station_and_sensor", "frame",
    "range_sigma_m", "angle_sigma_deg", "orbit_covariance",
    "forecast_sigma_seconds", "date_classification_sigma_seconds",
    "report_latency_seconds", "day_time_standard", "physical_terminal_utc",
    "determination_method",
)

def check(value, message):
    if not value:
        raise ValueError(message)

def validate(model, nasa, norad, coverage):
    check(model["schema"] == "conde.nasa-528-decay-precision/v1"
          and model["id"] == "C197-PRECISION-20261113"
          and model["status"] == "CONNECTED_PENDING_CALIBRATION",
          "bridge schema/id/status")
    source = nasa["sources"][0]
    row = source["human_table_observation"]
    m = model["source"]
    check((m["occurrence"], m["support"], m["ntrs"]) ==
          ("C197#1", "C241-L11", "19640001198"), "occurrence or NTRS")
    check(m["url"] == source["url"]
          and m["sha256"] == source["sha256"] == PIN
          and m["pdf_page_index"] == source["page_index_zero_based"] == 9
          and m["printed_page"] == source["page_printed"] == 8
          and m["printed_object"] == row["object_printed"] == "1963 3B"
          and m["reported_decay_day"] == row["decay_day"] == "1963-11-08"
          and m["published_day"] == source["publication_date"] == "1963-11-15",
          "source bytes/cells or dates changed")
    check(m["norad_crosswalk_secondary"] == 528
          and m["source_family"] == "NASA_GODDARD_NORAD_SHARED_COMPILATION"
          and not m["raw_sensor_observation"], "source misclassified")
    d0 = dt.date.fromisoformat(m["reported_decay_day"])
    d1 = dt.date.fromisoformat(m["published_day"])
    check((d1 - d0).days == model["reported_to_publication_calendar_days"] == 7,
          "report day mismatch")
    check(model["date_label_resolution"] == "CALENDAR_DAY_NOT_EVENT_ACCURACY",
          "calendar granularity misused as precision")
    check(set(model["unknowns"]) == set(UNKNOWNS)
          and all(model["unknowns"][k] is None for k in UNKNOWNS),
          "an unknown was made into a numeric precision or terminal epoch")
    d = model["precision_dimensions"]
    check([x["kind"] for x in d] ==
          ["sensor_range_angle", "orbit_fit_covariance", "decay_forecast_error",
           "catalog_date_classification_error"]
          and all(x["value"] is None and x["units"] is None
                  and x["status"] == "UNKNOWN_FOR_528" for x in d),
          "precision layers collapsed")
    check(model["conditional_methods"] ==
          ["DIRECT_OBSERVATION", "FORECAST", "COMBINED_OR_ADMINISTRATIVE"]
          and model["method_selected"] is None, "undocumented determination method")
    p = model["conditional_predicate"]
    check(p["start_utc"] == "1963-11-08T00:00:00Z"
          and p["end_exclusive_utc"] == "1963-11-09T00:00:00Z"
          and not p["active"] and not p["assumption_verified"],
          "conditional UTC-day restriction promoted")
    comp = model["comparator"]
    original = next(o for o in norad["occurrences"]
                    if o["id"] == "MOR-NOR-20261112-03")
    check(original["source_id"] == comp["source_document"] ==
          "MOR-NORAD-1963-NOV14"
          and comp["source_occurrence"] == original["id"]
          and comp["spadats_id"] == 688
          and comp["window_start_utc"] == "1963-11-12T22:10:00Z"
          and comp["window_end_utc"] == "1963-11-13T00:00:00Z"
          and not comp["same_as_object_528"]
          and not comp["precision_transfer_allowed"] and not comp["window_is_sigma"],
          "SPADATS 688 capability transferred to 528")
    l = model["likelihood"]
    check(l["numeric"] is None and not l["parameters_fitted"], "invented likelihood")
    g = model["graph"]
    check(g["parent"] == "research/constraints/ssr_1963_observable_graph.json"
          and g["dependencies"] == PATHS[1:]
          and len(g["edges"]) == 5
          and g["new_independent_sensor_observations"] == 0
          and g["physical_constraints_active"] == 0
          and not g["domain_reduced"] and not g["lean_activated"]
          and not g["simulator_calibrated"],
          "graph incorrectly promoted or disconnected")
    check(coverage["objects"]["528"]["catalog_status_day"] == "1963-11-08"
          and not coverage["objects"]["528"]["status_day_is_observed_terminal_time"]
          and not coverage["objects"]["528"]["status_day_is_observed_non_detection_time"]
          and coverage["inference_gates"]["historical_missingness_likelihood"] ==
          "NOT_IDENTIFIED", "coverage inferred as detection")
    return {
        "source": m["ntrs"], "catalog_day": m["reported_decay_day"],
        "report_day_gap_calendar_days_NOT_operational_latency": 7,
        "528_timing_sigma_seconds": None, "true_terminal_time_528": None,
        "capability_comparator": "SPADATS688_NOT_528",
        "connected_edges": 5, "physical_constraints_active": 0,
        "status": model["status"],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    values = [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PATHS]
    report = json.dumps(validate(*values), indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    print(report, end="")

if __name__ == "__main__":
    main()
