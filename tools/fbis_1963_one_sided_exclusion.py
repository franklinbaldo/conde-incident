#!/usr/bin/env python3
"""C241-P50: preregistered one-sided FBIS event chronology; not a clock fit."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/constraints/fbis_1963_one_sided_manifest.json"
OUTPUT = ROOT / "research/constraints/fbis_1963_one_sided_exclusion.json"
SCHEMA = "conde.fbis-one-sided-event-exclusion/v1"
MAX_SLACK_MINUTES = 5

# Frozen independently of the yet-uncollected FBIS candidate headings.
EVENTS = (
    ("JFK_SHOTS", "1963-11-22T18:30Z",
     "reports that shots were fired at Kennedy",
     "https://www.archives.gov/research/jfk/warren-commission-report/chapter-1"),
    ("JFK_PRONOUNCED_DEAD", "1963-11-22T19:00Z",
     "reports Kennedy pronounced dead, not just shooting",
     "https://www.whitehouse.gov/jfk-files/"),
    ("LBJ_OATH", "1963-11-22T20:38Z",
     "reports Johnson already sworn in, not an intended oath",
     "https://www.whitehouse.gov/jfk-files/"),
)
HEADER = re.compile(
    r"RIO DE JANEIRO RADIO [A-Z0-9 /.-]+ IN [A-Z]+ "
    r"(\d{2})(\d{2}) 22 NOV 63 W"
)
DIGEST = re.compile(r"[0-9a-f]{64}")


def demand(test: bool, message: str) -> None:
    if not test:
        raise ValueError("C241-P50: " + message)


def utc_stamp(value: str) -> datetime:
    demand(bool(re.fullmatch(r"1963-11-22T\d{2}:\d{2}Z", value)),
           "event timestamp outside frozen date/format")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_utc(value: datetime) -> str:
    return value.isoformat(timespec="minutes").replace("+00:00", "Z")


def parse_heading(value: str) -> datetime:
    demand(isinstance(value, str), "FBIS heading must be literal text")
    match = HEADER.fullmatch(value)
    demand(match is not None, "not a 22 Nov 1963 Rio radio wire heading")
    hour, minute = map(int, match.groups())
    try:
        return datetime(1963, 11, 22, hour, minute, tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError("C241-P50: invalid FBIS heading time") from exc


def validate(manifest: dict) -> list[dict]:
    demand(isinstance(manifest, dict) and manifest.get("schema") == SCHEMA,
           "unexpected manifest schema")
    demand(manifest.get("preregistered_date") == "2026-11-14",
           "preregistration date changed")
    demand(manifest.get("scope") == "RIO_DE_JANEIRO_RADIO_1963_11_22",
           "vetted city/date scope changed")
    demand(type(manifest.get("guard_minutes")) is int
           and manifest["guard_minutes"] == MAX_SLACK_MINUTES,
           "one-sided slack changed after preregistration")
    events = manifest.get("events")
    demand(isinstance(events, list) and len(events) == len(EVENTS),
           "frozen event set has changed")
    for row, (key, stamp, claim, url) in zip(events, EVENTS):
        demand(isinstance(row, dict) and row.get("id") == key
               and row.get("event_utc") == stamp
               and row.get("required_claim") == claim
               and row.get("source_url") == url
               and row.get("source_digest_sha256") is None,
               "frozen event source/time/claim changed")
        utc_stamp(stamp)
    rows = manifest.get("observed_fbis_items")
    demand(isinstance(rows, list), "observed_fbis_items must be a list")
    seen_ids, seen_occurrences = set(), set()
    for row in rows:
        demand(isinstance(row, dict), "item must be an object")
        for key in ("item_id", "fbis_facsimile_url", "fbis_sha256",
                    "fbis_header", "fbis_report_quote", "event_id",
                    "matching_rationale", "fbis_source_type"):
            demand(isinstance(row.get(key), str) and row[key].strip(),
                   "missing field " + key)
        demand(row["fbis_source_type"] == "ORIGINAL_1963_WIRE_FACSIMILE",
               "cannot substitute secondary broadcast account")
        demand(row.get("visually_checked") is True,
               "visual inspection not affirmed")
        demand(row["fbis_facsimile_url"].startswith("https://"),
               "FBIS source URL must be HTTPS")
        demand(bool(DIGEST.fullmatch(row["fbis_sha256"])),
               "facsimile SHA-256 malformed")
        demand(type(row.get("fbis_page")) is int and row["fbis_page"] >= 1,
               "positive FBIS PDF page required")
        demand(len(row["fbis_report_quote"].strip()) >= 20,
               "verbatim event mention absent/too short")
        demand(len(row["matching_rationale"].strip()) >= 30,
               "event matching rationale absent/too short")
        demand(row["event_id"] in {x[0] for x in EVENTS},
               "event not preregistered")
        parse_heading(row["fbis_header"])
        demand(row["item_id"] not in seen_ids, "duplicate item ID")
        seen_ids.add(row["item_id"])
        occurrence = (row["fbis_sha256"], row["fbis_page"],
                      row["fbis_header"])
        demand(occurrence not in seen_occurrences,
               "same FBIS occurrence relabeled as another observation")
        seen_occurrences.add(occurrence)
    return rows


def classify(row: dict) -> dict:
    observed = parse_heading(row["fbis_header"])
    event = next(e for e in EVENTS if e[0] == row["event_id"])
    event_utc = utc_stamp(event[1])
    conditional_utc = {
        "GMT": observed,
        "RIO_LOCAL": observed + timedelta(minutes=120),
    }
    excluded = [k for k, t in conditional_utc.items()
                if t + timedelta(minutes=MAX_SLACK_MINUTES) < event_utc]
    return {
        "item_id": row["item_id"],
        "event_id": row["event_id"],
        "event_utc": event[1],
        "fbis_sha256": row["fbis_sha256"],
        "fbis_page": row["fbis_page"],
        "header_literal": row["fbis_header"],
        "candidate_broadcast_utc": {
            key: format_utc(time) for key, time in conditional_utc.items()
        },
        "chronologically_excluded": excluded,
        "not_excluded_not_confirmed": [
            key for key in conditional_utc if key not in excluded
        ],
        "source_match_needs_human_authentication": True,
    }


def build(manifest: dict) -> dict:
    observations = [classify(row) for row in validate(manifest)]
    vetoed = {branch for row in observations
              for branch in row["chronologically_excluded"]}
    if not observations:
        status = "UNRESOLVED_NO_ITEMS"
    elif len(vetoed) == 2:
        status = "INCONSISTENT_SOURCE_OR_CLOCK_ASSUMPTIONS"
    elif len(vetoed) == 1:
        status = "ONE_SIDED_EXCLUSION_ONLY"
    else:
        status = "UNRESOLVED_NO_BRANCH_EXCLUDED"
    return {
        "schema": "conde.fbis-one-sided-exclusion-result/v1",
        "issue": 886,
        "preregistration": "C241-P50, 2026-11-14, separate from P48",
        "scope": manifest["scope"],
        "independent_same_broadcast_anchors_p48": 0,
        "events_from_external_chronology_not_fbis_clocks": [
            {"id": key, "utc": stamp, "url": url, "source_sha256": None}
            for key, stamp, _claim, url in EVENTS
        ],
        "observed_fbis_count": len(observations),
        "status": status,
        "vetoed_assumptions": sorted(vetoed),
        "non_vetoed_not_confirmed": [
            b for b in ("GMT", "RIO_LOCAL") if b not in vetoed
        ],
        "items": observations,
        "limits": {
            "header_clock_calibrated": False,
            "footer_111A_decoded": False,
            "timestamp_of_1963_conde_event": None,
            "source_semantics_not_machine_authenticated": True,
            "active_physical_lean_predicates": 0,
            "physical_domain_effect": "THETA_UNCHANGED",
        },
    }


def render() -> str:
    return json.dumps(build(json.loads(MANIFEST.read_text(encoding="utf-8"))),
                      indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = render()
    if args.check:
        demand(OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == value,
               "committed output does not match frozen sources")
        print("FBIS_ONE_SIDED_CHECK_PASS")
    else:
        OUTPUT.write_text(value, encoding="utf-8")
        print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
