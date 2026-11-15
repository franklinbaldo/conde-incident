#!/usr/bin/env python3
"""C241-P48: conditional FBIS wire-clock branches, not a timestamp of impact.

The 8 Nov 1963 Tupi header supplies a time of a *reported broadcast*.
Its time zone and the footer code are not independently authenticated.
No source from this same Tupi/FBIS lineage may be used as an independent
calibration of the clock. See Conde #886.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/constraints/fbis_1963_clock_branches.json"
MANIFEST = ROOT / "research/constraints/fbis_1963_clock_anchors.json"

HEADER = "RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2330 8 NOV 63 W"
FOOTER = "9 NOV 111A RWS/GY"
FBIS_SHA256 = "63654bcd90c0515f30e31ed511a12a05f170ff4470e3d8a6f40fca12012a1adb"
FBIS_URL = ("https://media.ondisclosure.org/web/official-uap/pursue/"
            "release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-"
            "Incident_November-13-1963.pdf")
DECREE_URL = ("https://www2.camara.leg.br/legin/fed/decret/1960-1969/"
              "decreto-52700-18-outubro-1963-393059-publicacaooriginal-1-pe.html")
# Legal time: Rio (then Guanabara) had +60 min special time on 8 Nov.
# Bahia was not subject to Decreto 52.700 during that interval.
RIO_UTC_OFFSET_MINUTES = -120
BAHIA_UTC_OFFSET_MINUTES = -180
# A CONDITIONAL geometric plane crossing at a MODERN CAMERA PROXY in #892.
# Not the event time and not even a measurement of the object's orbital phase.
PLANE_CROSSING_BAHIA = "1963-11-08T20:44:00"
THRESHOLD = 10
MAX_ANCHOR_DIFF_MINUTES = 5
# The complete station/clock line, not only the printed HHMM, defines a
# transmission occurrence. Two scans of one wire never count as two anchors.
FULL_WIRE_HEADER = re.compile(
    r"RIO DE JANEIRO RADIO (?P<station>[A-Z0-9 .-]+) IN [A-Z]+ "
    r"(?P<clock>\d{4} \d{1,2} NOV 63) W"
)


def demand(test: bool, why: str) -> None:
    if not test:
        raise ValueError("C241-P48: " + why)


def stamp_from_header(header: str = HEADER) -> datetime:
    match = re.fullmatch(
        r"RIO DE JANEIRO RADIO TUPI IN PORTUGUESE "
        r"(\d{2})(\d{2}) (\d{1,2}) NOV 63 W", header
    )
    demand(match is not None, "unexpected FBIS heading; refuse to guess")
    hour, minute, day = map(int, match.groups())
    return datetime(1963, 11, day, hour, minute)


def as_utc(local: datetime, offset_minutes: int) -> datetime:
    return (local - timedelta(minutes=offset_minutes)).replace(tzinfo=timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.isoformat(timespec="minutes").replace("+00:00", "Z")


def anchor_clock_pair(row: dict) -> tuple[datetime, datetime]:
    """Validate date/time for every putative anchor, even before quorum."""
    header = row["header_local_text"]
    match = re.fullmatch(r"(\d{2})(\d{2}) (\d{1,2}) NOV 63", header)
    demand(match is not None, "clock anchor outside preregistered format")
    hour, minute, day = map(int, match.groups())
    try:
        local = datetime(1963, 11, day, hour, minute)
    except ValueError as exc:
        raise ValueError("C241-P48: invalid November clock anchor") from exc

    stamp = row["external_broadcast_utc"]
    demand(bool(re.fullmatch(
        r"1963-(?:11-\d{2}|12-01)T\d{2}:\d{2}Z", stamp)),
        "external UTC must be November, or December 1 rollover")
    try:
        external = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("C241-P48: invalid independent UTC time") from exc
    demand(external < datetime(1963, 12, 1, 2, 5, tzinfo=timezone.utc),
           "external UTC beyond possible November DST rollover")
    return local, external


def anchors_from_manifest(data: dict) -> list:
    demand(data.get("schema") == "conde.fbis-clock-anchors/v1",
           "manifest schema invalid")
    rows = data.get("independent_anchors")
    demand(isinstance(rows, list), "anchors must be a list")
    used = set()
    used_occurrences = set()
    used_broadcasts = set()
    for row in rows:
        demand(isinstance(row, dict), "anchor must be an object")
        for name in ("item_id", "fbis_document_url", "fbis_sha256",
                     "fbis_page", "independent_source_url",
                     "independent_source_sha256", "independent_page",
                     "fbis_heading_verbatim", "header_local_text",
                     "external_broadcast_utc",
                     "independence_rationale"):
            demand(isinstance(row.get(name), str) and bool(row[name].strip()),
                   "missing anchor field " + name)
        for name in ("fbis_sha256", "independent_source_sha256"):
            demand(bool(re.fullmatch("[0-9a-f]{64}", row[name])),
                   "anchor digest is not SHA-256")
        for name in ("fbis_page", "independent_page"):
            demand(bool(re.fullmatch(r"[1-9][0-9]*", row[name])),
                   "anchor has no positive page index: " + name)
        demand(row["item_id"] not in used, "duplicate FBIS item")
        used.add(row["item_id"])
        occurrence = (row["fbis_sha256"], row["fbis_page"],
                      row["header_local_text"])
        demand(occurrence not in used_occurrences,
               "duplicate FBIS occurrence under another item ID")
        used_occurrences.add(occurrence)
        heading = FULL_WIRE_HEADER.fullmatch(row["fbis_heading_verbatim"])
        demand(heading is not None,
               "full original heading must identify a Rio radio station")
        demand(heading.group("clock") == row["header_local_text"],
               "FBIS date/time differs between full heading and clock field")
        broadcast = (heading.group("station").strip(), heading.group("clock"))
        demand(broadcast not in used_broadcasts,
               "same broadcast reissued under a different FBIS facsimile")
        used_broadcasts.add(broadcast)
        anchor_clock_pair(row)
        demand(row["independent_source_sha256"] != row["fbis_sha256"],
               "self-confirming FBIS source")
        demand(row["fbis_document_url"] != row["independent_source_url"],
               "same source cannot supply independent broadcast time")
        demand(len(row["independence_rationale"]) >= 25,
               "independence must be explained")
    # A cited external reference cannot secretly be a different FBIS item
    # inside this very calibration corpus. Pairwise own-row checks miss this.
    fbis_digests = {row["fbis_sha256"] for row in rows}
    fbis_urls = {row["fbis_document_url"] for row in rows}
    for row in rows:
        demand(row["independent_source_sha256"] not in fbis_digests
               and row["independent_source_url"] not in fbis_urls,
               "independent source is another FBIS facsimile")
    return rows


def qualification(anchors: list) -> dict:
    """Predeclared conservative rule. Unknown/contradictory items yield no vote.

    Qualification needs independent 1963 records *of the same broadcasts*.
    Source identity is checked above; human source review remains mandatory.
    An external timestamp cannot be inferred from the FBIS heading itself.
    """
    parsed = [anchor_clock_pair(row) for row in anchors]
    count = len(anchors)
    if count < THRESHOLD:
        return {"status": "UNRESOLVED", "qualifying_anchors": count,
                "reason": "LESS_THAN_10_INDEPENDENT_TIME_ANCHORS"}
    votes = {"GMT": 0, "RIO_LOCAL": 0, "INCONCLUSIVE": 0}
    for naive, independent_utc in parsed:
        # Every anchor was parsed even when fewer than ten are available.
        # Dec 1 UTC is legal for a late-November Guanabara broadcast.
        distances = {
            "GMT": abs((as_utc(naive, 0) - independent_utc).total_seconds()) / 60,
            "RIO_LOCAL": abs((as_utc(naive, RIO_UTC_OFFSET_MINUTES)
                              - independent_utc).total_seconds()) / 60,
        }
        matched = [key for key, value in distances.items()
                   if value <= MAX_ANCHOR_DIFF_MINUTES]
        votes[matched[0] if len(matched) == 1 else "INCONCLUSIVE"] += 1
    winners = [key for key in ("GMT", "RIO_LOCAL") if votes[key] == count]
    return {"status": winners[0] if len(winners) == 1 else "UNRESOLVED",
            "qualifying_anchors": count, "votes": votes,
            "reason": "ALL_ANCHORS_AGREE" if winners else "CONFLICT_OR_AMBIGUITY",
            "independence_requires_manual_review": True}


def build(manifest: dict) -> dict:
    anchors = anchors_from_manifest(manifest)
    decision = qualification(anchors)
    header_local = stamp_from_header()
    # Purely conditional readings, without selecting either hypothesis.
    utc_gmt = as_utc(header_local, 0)
    utc_rio = as_utc(header_local, RIO_UTC_OFFSET_MINUTES)
    crossing_utc = as_utc(datetime.fromisoformat(PLANE_CROSSING_BAHIA),
                          BAHIA_UTC_OFFSET_MINUTES)

    def branch(label: str, utc: datetime) -> dict:
        in_bahia = utc + timedelta(minutes=BAHIA_UTC_OFFSET_MINUTES)
        delta_minutes = int((crossing_utc - utc).total_seconds() / 60)
        return {
            "broadcast_utc_if_assumption_holds": iso_utc(utc),
            "broadcast_bahia_civil_if_assumption_holds":
                in_bahia.strftime("%Y-%m-%dT%H:%M"),
            "reported_event_latest_possible_utc_if_report_precedes_broadcast":
                iso_utc(utc),
            "condition": label,
            "plane_crossing_nominal_minutes_after_broadcast": delta_minutes,
            "plane_crossing_nominal_order":
                "AFTER" if delta_minutes > 0 else
                "BEFORE" if delta_minutes < 0 else "EQUAL",
            "plane_crossing_is_measured_event": False,
            "orbit_exclusion_licensed": False,
        }

    return {
        "schema": "conde.fbis-clock-branches/v1",
        "project_issue": 886,
        "verification_status": decision["status"],
        "source": {
            "fbis_header_verbatim": HEADER,
            "fbis_footer_verbatim_unparsed": FOOTER,
            "facsimile_url": FBIS_URL,
            "facsimile_sha256": FBIS_SHA256,
            "same_broadcast_lineage_as_C01": True,
            "reported_phenomenon_time": None,
            "footer_clock_meaning": None,
            "header_timezone_verified": False,
        },
        "civil_time_basis": {
            "decree": "Decreto 52.700 de 18/10/1963, art. 1",
            "official_original_text": DECREE_URL,
            "guanabara_utc_offset_on_1963_11_08_minutes": RIO_UTC_OFFSET_MINUTES,
            "bahia_utc_offset_on_1963_11_08_minutes": BAHIA_UTC_OFFSET_MINUTES,
            "guaranteed_by_decree": "Guanabara special time; Bahia excluded",
        },
        "anchor_rule": {
            "preregistered_before_anchor_collection": True,
            "required_independent_1963_items": THRESHOLD,
            "maximum_clock_difference_minutes": MAX_ANCHOR_DIFF_MINUTES,
            "choice": "Unanimity of 10+ independently time-anchored broadcasts",
            "other_cities_or_eras": "OUTSIDE_SCOPE",
            "recorded_independent_anchors": len(anchors),
            "decision": decision,
        },
        "conditional_branches": {
            "GMT": branch("2330 interpreted as GMT", utc_gmt),
            "RIO_LOCAL": branch("2330 interpreted as Rio/Guanabara local DST", utc_rio),
            "OTHER_UNVERIFIED": {
                "broadcast_utc_if_assumption_holds": None,
                "broadcast_bahia_civil_if_assumption_holds": None,
                "reported_event_latest_possible_utc_if_report_precedes_broadcast": None,
                "orbit_exclusion_licensed": False,
            },
        },
        "modern_proxy_plane_comparison": {
            "reference": "C241-PLANE-20261114 / Conde PR #892",
            "object": "NORAD 528",
            "geometry": "CGEO15-CAMERA-01 modern 2022 proxy, not Conde 1963",
            "date": "1963-11-08",
            "crossing_bahia_nominal": PLANE_CROSSING_BAHIA,
            "crossing_utc_nominal": iso_utc(crossing_utc),
            "not_a_dynamically_fitted_orbit": True,
        },
        "limits": {
            "event_could_precede_report_by_unknown_interval": True,
            "actual_broadcast_time_not_independently_verified": True,
            "footer_111A_is_not_parsed_as_a_timestamp": True,
            "new_1963_independent_broadcast_anchors": len(anchors),
            "new_instrumental_orbital_measurements": 0,
            "active_physical_lean_predicates": 0,
            "physical_domain_effect": "THETA_UNCHANGED",
        },
    }


def render() -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return json.dumps(build(manifest), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="compare committed JSON exactly against rebuilt JSON")
    args = parser.parse_args()
    body = render()
    if args.check:
        demand(OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == body,
               "committed branch matrix differs from source/anchors")
        print("FBIS_CLOCK_BRANCHES_CHECK_PASS")
    else:
        OUTPUT.write_text(body, encoding="utf-8")
        print(str(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
