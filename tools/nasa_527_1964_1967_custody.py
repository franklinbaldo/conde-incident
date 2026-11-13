#!/usr/bin/env python3
"""C241-L28: preserve original NASA-printed 527 crosswalk and 1964-67 orbit columns."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_527_1964_1967_crosswalk_C241-L28.json"
PARENT = ROOT / "research/tle_custody/nasa_ssr_editions_precision_C241-L27.json"
IDS = ["19640017911", "19650016819", "19660012484", "19680005210"]
DATES = ["1964-05-31", "1965-05-15", "1966-02-15", "1967-08-31"]
VOL_ISSUES = [(4, 10), (5, 9), (6, 3), (7, 16)]
PAGES = [(6, 5), (6, 5), (5, 5), (5, 5)]
SIZES = [471961, 759944, 889027, 1154109]
HASHES = [
    "720094637a05182e76aa1189fd15e72ef8b207cb9b94a91cd5bb02786f25b479",
    "c476e42459e13039780076315f03054c774f83a0bbadef5a61d32ba3b88eccf1",
    "4e7829a7b2b105e3c4af9b0fc0db3af64d25a90f8426ab625d84d771fb7589b8",
    "808e8d4bb04d3ae8d1a265fc59c97d1b6152019f9bc8785bececbdfb1d64f29d",
]
ROWS = [
    ("94.5", "81.89", 528, 462),
    ("94.4", "81.89", 524, 460),
    ("94.4", "81.88", 520, 457),
    ("93.7", "81.90", 479, 436),
]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(data, parent):
    require(data.get("schema") == "conde.nasa-527-1964-1967-crosswalk/v1"
            and data.get("id") == "C241-L28"
            and data.get("status") == "PRIMARY_DOCUMENTARY_CROSSWALK_ONLY",
            "wrong schema or claim status")
    rows = data.get("source_documents", [])
    require(len(rows) == 4, "four contemporary NASA documents required")
    for i, row in enumerate(rows):
        rr = row["row"]
        require(row["ntrs_id"] == IDS[i]
                and row["published_on"] == DATES[i]
                and (row["volume"], row["issue"]) == VOL_ISSUES[i]
                and (row["page_index_zero_based"], row["page_printed"]) == PAGES[i]
                and row["url"] == f"https://ntrs.nasa.gov/api/citations/{IDS[i]}/downloads/{IDS[i]}.pdf"
                and row["sha256"] == HASHES[i]
                and row["bytes"] == SIZES[i]
                and row["data_kind"] == "CONTEMPORARY_NASA_GODDARD_CATALOG_NOT_RAW_SENSOR"
                and row["observation_independence_family"] == "NASA_NORAD_SAO_SHARED_COMPILATION",
                f"source/edition/bytes {i} changed")
        require(rr["international_designator_printed"] == "1963 03A"
                and rr["catalog_number_printed"] == 527
                and (rr["period_minutes_printed"], rr["inclination_deg_printed"],
                     rr["apogee_km_printed"], rr["perigee_km_printed"]) == ROWS[i],
                f"printed NASA source row {i} changed")
        require(row["instrumental_epoch_utc"] is None
                and row["sensor_id"] is None
                and row["measurement_covariance"] is None,
                f"made up source-specific sensor precision/epoch {i}")
    cw = data["crosswalk"]
    require(cw["designator"] == "1963 03A" and cw["catalog_number"] == 527
            and cw["direct_primary_printed"]
            and cw["confidence_scope"] == "PRIMARY_PUBLISHED_CATALOG_CROSSWALK_NOT_SENSOR_IDENTITY"
            and not cw["source_1963_03B_to_528_direct_primary_printed"]
            and not cw["source_1963_03C_to_529_direct_primary_printed"],
            "false identity promotion for 528/529")
    q = data["observation_model"]
    require(q["printed_rows_are_fitted_or_compiled_catalog_values"]
            and not q["rows_are_independent_sensor_measures"]
            and q["actual_sensor_observations_added"] == 0
            and q["orbital_error_sigma"] is None
            and q["observation_epoch_utc"] is None, "false instrumental observation")
    parent_rows = parent["docs"]
    require(parent["id"] == "C241-L27"
            and parent["schema"] == "conde.ssr-edition-quantization-sequence/v1"
            and parent["source_family"] == "NASA_GODDARD_NORAD_SAO_COMPILED_SAME_UPSTREAM"
            and parent["independent_sensor_observations_added"] == 0
            and any(r["ntrs"] == "19640001198"
                    and r["published"] == "1963-11-15"
                    and r["objects"] == [527, 529] for r in parent_rows),
            "parent 1963 NASA custody changed")
    expected_edges = [
        ("C241-L27:NASA-1963-527", "C241-L28:NASA-1964-527"),
        ("C241-L28:NASA-1964-527", "C241-L28:NASA-1965-527"),
        ("C241-L28:NASA-1965-527", "C241-L28:NASA-1966-527"),
        ("C241-L28:NASA-1966-527", "C241-L28:NASA-1967-527"),
    ]
    require([(x["from"], x["to"]) for x in data["edges"]] == expected_edges
            and all(x["status"] == "EDITORIAL_LINK_NO_INSTRUMENT_TIME"
                    for x in data["edges"]), "disconnected editorial lineage")
    difference = data["reported_delta"]
    require(difference["first_period_min"] == "94.5"
            and difference["last_period_min"] == "93.7"
            and difference["difference_printed_min"] == "-0.8"
            and difference["elapsed_published_days"] ==
            (dt.date.fromisoformat(DATES[-1]) - dt.date.fromisoformat(DATES[0])).days == 1187
            and difference["interpretation"] ==
            "DIFFERENCE_OF_PUBLISHED_FITTED_CATALOG_VALUES_NOT_DERIVATIVE_NOT_DECAY_PREDICTION",
            "publication delta incorrectly interpreted")
    lim = data["limits"]
    require(not any([lim["physical_reentry_time_known"], lim["measurement_sigma_known"],
                     lim["terminal_position_known"], lim["observational_likelihood_ready"],
                     lim["lean_constraint_activated"], lim["feasible_domain_reduced"]])
            and lim["condenser_inference"] == "NOT_RUN",
            "physical restriction improperly inferred")
    return {
        "crosswalk": "1963 03A = 527 in 4 original NASA publications",
        "source_ids": IDS,
        "printed_period_minutes": [r[0] for r in ROWS],
        "published_delta_minutes_NOT_orbital_decay_rate": "-0.8",
        "publisher_lag_or_terminal_time": None,
        "independent_sensor_measurements_added": 0,
        "physical_constraints_activated": 0,
        "status": "PRIMARY_DOCUMENTARY_CROSSWALK_ONLY",
    }

def validate_pdfs(data, folder):
    for source in data["source_documents"]:
        path = folder / (source["ntrs_id"] + ".pdf")
        raw = path.read_bytes()
        require(raw.startswith(b"%PDF-"), f"{path}: not PDF")
        require(len(raw) == source["bytes"], f"{path}: changed length")
        require(hashlib.sha256(raw).hexdigest() == source["sha256"], f"{path}: changed SHA")
    return len(data["source_documents"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    report = validate(data, parent)
    report["pdfs_verified"] = validate_pdfs(data, args.pdf_dir) if args.pdf_dir else 0
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")

if __name__ == "__main__":
    main()
