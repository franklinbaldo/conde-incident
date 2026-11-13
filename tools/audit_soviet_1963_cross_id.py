#!/usr/bin/env python3
"""Fail-closed Soviet 1963 bibliographic -> NORAD cross-ID bridge; no orbital fit."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATHS = [
    "research/tle_custody/soviet_1963_cross_id_C241-L30.json",
    "research/tle_custody/soviet_1963_bibliographic_holdings_C241-L29.json",
    "research/tle_custody/nasa_527_1964_1967_crosswalk_C241-L28.json",
    "research/tle_custody/catalog_identity_527_529_2026-11-12.json",
]
PINS = {
    "CNII-AA00566856": ("AA00566856", 54342, "da7b7e445ccaf5569bccbb42809f9da471318cebebe6d713ec0deb0a08c31034"),
    "CNII-AA00826990": ("AA00826990", 53364, "0f349be2b3655f29ba1f8a518143ee807d58ba970b507629a5ed1fcf39c8740b"),
}
JOIN_NULLS = (
    "original_soviet_designation", "original_soviet_page",
    "original_soviet_issue_scan_sha256", "original_epoch_utc",
    "original_station", "original_measurement", "original_orbit_elements",
    "frame", "time_standard", "measurement_units", "instrument_sigma",
    "origin_of_orbit_fit", "same_tracking_as_western",
)

def check(condition, message):
    if not condition:
        raise ValueError(message)

def validate(data, upstream, nasa, secondary):
    check(data["schema"] == "conde.soviet-1963-cross-id-readiness/v1"
          and data["id"] == "C241-L30"
          and data["scope"] == "CATALOG_CROSS_IDENTIFICATION_READINESS_NO_ORBITAL_INFERENCE"
          and data["verified_on"] == "2026-11-13", "scope/schema")
    check(data["upstream"] == dict(
        holdings=PATHS[1], nasa_527=PATHS[2], secondary_western=PATHS[3]),
        "upstream lineage")
    check(upstream["schema"] == "conde.soviet_1963_holdings/v1"
          and upstream["id"] == "C241-L29"
          and upstream["level"] == "INSTITUTIONAL_LIBRARY_HOLDINGS_ONLY"
          and upstream["verified_observations"] == 0
          and not upstream["orbital_constraint_activated"], "upstream catalog promotion")
    check(nasa["schema"] == "conde.nasa-527-1964-1967-crosswalk/v1"
          and nasa["id"] == "C241-L28"
          and nasa["crosswalk"]["designator"] == "1963 03A"
          and nasa["crosswalk"]["catalog_number"] == 527
          and nasa["crosswalk"]["direct_primary_printed"]
          and not nasa["crosswalk"]["source_1963_03B_to_528_direct_primary_printed"]
          and not nasa["crosswalk"]["source_1963_03C_to_529_direct_primary_printed"],
          "NASA crosswalk status")
    check(secondary["primary_date_only_record"]["catalog_designator_printed"]
          == "1963 3B"
          and secondary["primary_date_only_record"]["decay_day"]
          == "1963-11-08", "NASA 1963-003B day not pinned")
    holdings = data["holdings"]
    check(len(holdings) == 2 and [s["id"] for s in holdings] ==
          ["C241-L29#1", "C241-L29#2"], "holdings identity")
    for h, original in zip(holdings, upstream["records"]):
        check(h["id"] == original["id"]
              and h["source_url"] == original["url"]
              and h["publication"] == original["journal"]
              and h["year"] == original["year"] == 1963
              and h["issue_numbers"] == original["issues"]
              and h["source_kind"] == "LIBRARY_HTML_HOLDING_NOT_ISSUE_PDF"
              and h["issue_pdf_sha256"] is None
              and h["sensor_measurement_present"] is None
              and not h["issue_pages_seen"]
              and original["issue_pdf_sha256"] is None
              and not original["facsimile_read"]
              and original["primary_observation_527_528_529"] is None,
              "library holding falsely upgraded")
    check(holdings[0]["issue_numbers"] == [32, 33, 34, 35, 36, 37]
          and holdings[1]["issue_numbers"] == [2], "1963 issue list altered")
    checks = data["bibliographic_cross_checks"]
    check(len(checks) == 2 and {c["id"] for c in checks} == set(PINS),
          "CiNii provenance")
    for c in checks:
        identity, size, digest = PINS[c["id"]]
        check(c["url"] == "https://ci.nii.ac.jp/ncid/" + identity
              and c["capture_bytes"] == size
              and c["capture_sha256"] == digest
              and c["capture_http_status"] == 200
              and c["capture_day_utc"] == "2026-11-13"
              and c["pdf_sha256"] is None
              and not c["issue_1963_content_seen"]
              and not c["independent_observation"]
              and not c["same_publication_proven"], "CiNii source mutated or overpromoted")
    c0, c1 = checks
    check(c0["id"] == "CNII-AA00566856"
          and c0["status"] == "LIBRARY_METADATA_ONLY"
          and c0["possible_relation_to"] == "C241-L29#1"
          and "32-59" in c0["holding_example"]
          and "1963-1971" in c0["holding_example"], "CiNii serial match too strong")
    check(c1["id"] == "CNII-AA00826990"
          and c1["status"] == "NO_1963_HOLDING_SHOWN_IN_THIS_CATALOG_VIEW"
          and c1["possible_relation_to"] is None
          and "1961-1962" in c1["holding_example"], "bibliographic absence overstated")
    aliases = data["western_object_aliases"]
    check([o["norad"] for o in aliases] == [527, 528, 529]
          and [o["modern_designator"] for o in aliases] ==
          ["1963-003A", "1963-003B", "1963-003C"], "target/alias mismatch")
    for o in aliases:
        source = secondary["sources"]["itau_" + str(o["norad"])]
        check(source["international_designator"] == o["modern_designator"]
              and source["catalog"] == o["norad"]
              and o["soviet_record_id"] is None, "fabricated Soviet match")
    check(aliases[0]["contemporary_nasa_designator"] == "1963 03A"
          and aliases[0]["western_crosswalk"] == "CONFIRMED_PRIMARY_NASA_CATALOG_ONLY"
          and aliases[0]["western_crosswalk_source"] == "C241-L28"
          and [o["western_crosswalk"] for o in aliases[1:]] ==
          ["PENDING_PRIMARY_NUMBER_MATCH", "PENDING_PRIMARY_NUMBER_MATCH"]
          and aliases[1]["contemporary_nasa_designator"] == "1963 3B",
          "Western primary evidence transferred to another object")
    expected_pairs = {(h["id"], o["norad"], o["modern_designator"])
                      for h in holdings for o in aliases}
    joins = data["candidate_joins"]
    check(len(joins) == 6 and {(j["source_holding_id"],
          j["target_norad"], j["target_designator"]) for j in joins}
          == expected_pairs, "candidate joins missing/duplicate")
    for j in joins:
        check(j["join_status"] == "PENDING_NO_ISSUE_FACSIMILE"
              and all(k in j and j[k] is None for k in JOIN_NULLS)
              and j["independent_sensor_confirmed"] is False
              and j["physical_constraint_active"] is False,
              "unsupported Soviet measurement, sigma or identity")
    check(len(data["required_to_confirm_designation"]) == 3
          and len(data["required_to_use_orbit"]) == 5
          and len(data["rejected_automatic_upgrades"]) == 7,
          "essential evidentiary gates missing")
    result = data["result"]
    check(result == dict(
        contemporary_1963_soviet_527_528_529_instrument_observations_verified=0,
        soviet_fascimiles_inspected=0, source_holding_families=2,
        candidate_joins_pending=6, candidate_joins_confirmed=0,
        independent_measurements_added=0, orbital_constraints_activated=0,
        lean_activated=False, impact_location_claimed=False),
        "a bibliographic lead was promoted to evidence")
    return {
        "source_holdings": len(holdings), "western_aliases": len(aliases),
        "candidate_pairs": len(joins), "original_1963_soviet_measurements": 0,
        "primary_crosswalks_confirmed": ["1963 03A=527 (NASA only)"],
        "unverified_primary_crosswalks": ["1963-003B=528", "1963-003C=529"],
        "orbital_constraints_active": 0,
        "status": "PENDING_PRIMARY_PAGES_AND_SENSOR_EPOCHS"
    }

def replay_cinii(data, directory):
    for c in data["bibliographic_cross_checks"]:
        key = c["id"].split("CNII-")[1]
        payload = (directory / (key + ".html")).read_bytes()
        check(len(payload) == c["capture_bytes"]
              and hashlib.sha256(payload).hexdigest() == c["capture_sha256"],
              "CiNii exact HTML bytes changed: " + key)
        raw = payload.decode("utf-8")
        for token in (["1963-1971", "32-59"] if key == "AA00566856"
                      else ["1961-1962", "1-15"]):
            check(token in raw, "CiNii exact holdings text missing: " + key)
    return True

def read_all():
    return [json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PATHS]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cinii-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = read_all()
    result = validate(*data)
    if args.cinii_dir:
        replay_cinii(data[0], args.cinii_dir)
        result["cinii_html_replay"] = "PASS_EXACT_BYTES"
    else:
        result["cinii_html_replay"] = "NOT_RUN"
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")

if __name__ == "__main__":
    main()
