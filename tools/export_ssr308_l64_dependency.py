#!/usr/bin/env python3
"""Source-locked C241-L64 NASA calendar range -> R59 control -> inactive Lean/Theta."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L64 = "research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json"
L64_SHA = "c7f66c31e40a833bd52c2ec6943247fd507705a141d2ff5116131a82d936dbe4"
R59 = "public/data/conde-terminal-control-r59-scientific-bridge.json"
R59_SHA = "00824c60d9489a8c5c7d8691635d47237a273e1284392a4bcc45cc3c72ee1611"
OUTPUT = ROOT / "public/data/conde-ssr-308-l64-dependency-bridge.json"
PDF_SHA = "d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f"


def require(condition, why):
    if not condition:
        raise ValueError("C241-L64/R59 bridge: " + why)


def source_json(root, rel, digest):
    body = (root / rel).read_bytes()
    require(hashlib.sha256(body).hexdigest() == digest, "source SHA drift " + rel)
    return json.loads(body, object_pairs_hook=reject_duplicate_keys)


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate source JSON key " + key)
        result[key] = value
    return result


def load(root=ROOT):
    return source_json(root, L64, L64_SHA), source_json(root, R59, R59_SHA)


def edge(a, b, relation):
    return {"source": a, "target": b, "relation": relation,
            "documentary_only": True, "activation": False}


def build(l64, r59):
    require(l64["id"] == "C241-L64", "custody occurrence")
    src, row, ident = l64["source"], l64["original_row"], l64["identity"]
    require(src["ntrs_id"] == "19640003479" and
            src["publication"] == "1963-12-15" and
            src["printed_page"] == 15 and
            src["pdf_sha256"] == PDF_SHA and
            src["pdf_bytes"] == 958927 and
            src["individual_instrumental_observation"] is False,
            "NASA source and custody")
    require(row["printed_designator"] == "A OMEGA 1" and
            row["decay_printed"] == "29-30 OCT 63" and
            row["calendar_range_start"] == "1963-10-29" and
            row["calendar_range_end"] == "1963-10-30" and
            row["interpretation"] == "PUBLISHED_CALENDAR_RANGE_NOT_UTC_EVENT",
            "printed NASA calendar range")
    for name in ("printed_norad_id", "terminal_utc", "utc_interval",
                 "sensor", "station", "original_observation", "sigma_seconds"):
        require(row[name] is None, "unobserved NASA field " + name)
    require(ident["secondary_norad_id"] == 308 and
            ident["secondary_cospar"] == "1962-024A" and
            ident["identity_status"] == "SECONDARY_CROSSWALK_PENDING_PRIMARY_NORAD_ID" and
            ident["nasa_explicitly_prints_308"] is False, "crosswalk grade")
    require(l64["inference"]["independent_original_sensor_observations_added"] == 0 and
            l64["inference"]["hard_constraints_528_added"] == 0, "L64 physical claim")
    require(r59["id"] == "ABELHA-C241-CERVO-R59-TERMINAL-CONTROLS" and
            r59["activation"] is False and
            r59["physical_domain_effect"] == "THETA_UNCHANGED", "R59 parent")
    candidates = [x for x in r59["observations"] if x["norad_id"] == 308]
    require(len(candidates) == 1, "R59 308 multiplicity")
    lead = candidates[0]
    require(lead["id"] == "R59:NORAD:308" and
            lead["role"] == "CANDIDATE" and
            lead["reported_calendar_day"] == "1963-10-30" and
            lead["day_evidence_grade"] == "SECONDARY_DECAY_DAY_LEAD" and
            lead["terminal_event_utc"] is None and
            lead["terminal_sigma_seconds"] is None and
            lead["activation"] is False, "R59 single-day lead")
    payload = {
        "schema": "conde.c241-l64-r59-calendar-dependency/v1",
        "id": "ABELHA-C241-L64-R59-308-CALENDAR-RANGE",
        "sources": [
            {"id": "C241-L64", "path": L64, "sha256": L64_SHA,
             "pdf_sha256": PDF_SHA, "pdf_bytes": 958927,
             "publication_date": src["publication"], "printed_page": 15},
            {"id": "ABELHA-C241-CERVO-R59-TERMINAL-CONTROLS", "path": R59,
             "sha256": R59_SHA, "grade": "SECONDARY_ARCHIVE_SEARCH_NOT_CALIBRATED"},
        ],
        "observation": {
            "id": "C241-L64:OMEGA1", "printed_identifier": row["printed_designator"],
            "printed_calendar_range": [row["calendar_range_start"],
                                       row["calendar_range_end"]],
            "secondary_norad_id": ident["secondary_norad_id"],
            "secondary_cospar": ident["secondary_cospar"],
            "identity_grade": ident["identity_status"],
            "nasa_printed_norad_id": None,
            "r59_secondary_calendar_day": lead["reported_calendar_day"],
            "range_is_instrumental_utc": False,
            "terminal_event_utc": None, "terminal_sigma_seconds": None,
            "station": None, "sensor": None, "reference_frame": None,
            "independent_instrumental_lineages": None, "activation": False,
        },
        "graph": [
            edge("DOC:NTRS-19640003479", "PDF:NASA-SSR-V3N24-P15", "METADATA_LOCATES_FACSIMILE"),
            edge("PDF:NASA-SSR-V3N24-P15", "DOC:C241-L64", "CUSTODIED_PDF_SHA256"),
            edge("DOC:C241-L64", "ROW:NASA-OMEGA1-1963", "PRINTS_29_TO_30_OCT_1963"),
            edge("ROW:NASA-OMEGA1-1963", "H:CALENDAR_RANGE_NOT_UTC", "PUBLICATION_NOT_SENSOR"),
            edge("SRC:KEEPTRACK-308", "CROSSWALK:NORAD-308-OMEGA1", "SECONDARY_IDENTITY_ONLY"),
            edge("CROSSWALK:NORAD-308-OMEGA1", "H:308_IDENTITY_PENDING_PRIMARY", "NASA_ROW_HAS_NO_NORAD"),
            edge("DOC:R59-LEDGER", "LEAD:NORAD:308", "SECONDARY_SINGLE_DAY_30_OCT"),
            edge("LEAD:NORAD:308", "H:R59_DAY_NOT_UTC", "SECONDARY_DAY_NOT_TERMINAL_INSTANT"),
            edge("H:CALENDAR_RANGE_NOT_UTC", "LATENT:NORAD:308:terminal_utc", "UTC_AND_ERROR_UNAVAILABLE"),
            edge("H:308_IDENTITY_PENDING_PRIMARY", "LATENT:NORAD:308:terminal_utc", "IDENTITY_LINK_UNCALIBRATED"),
            edge("H:R59_DAY_NOT_UTC", "LATENT:NORAD:308:terminal_utc", "SOURCE_DEPENDENCE_UNRESOLVED"),
            edge("LATENT:NORAD:308:terminal_utc", "LEAN:candidateTerminalControlEvidence",
                 "ONLY_CONDITIONAL_CALENDAR_INFORMATION"),
            edge("LEAN:candidateTerminalControlEvidence", "PARAM:terminal_error_control_308",
                 "NO_INSTRUMENTAL_TERMINAL_EVENT_OR_SIGMA"),
            edge("PARAM:terminal_error_control_308", "PARAM:reentry_528_drag_calibration",
                 "NO_EMPIRICAL_TRANSFER_TO_528"),
        ],
        "lean_candidates": [
            {"id": "LEAN:candidateTerminalControlEvidence",
             "status": "CANDIDATE_ONLY_NOT_COMPILED", "activation": False},
        ],
        "simulator_parameters": [
            {"id": "PARAM:terminal_error_control_308", "value": None, "activation": False},
            {"id": "PARAM:reentry_528_drag_calibration", "value": None, "activation": False},
        ],
        "new_independent_instrumental_observations": 0,
        "new_activated_physical_constraints": 0,
        "historical_mcmc": "NOT_RUN",
        "physical_domain_effect": "THETA_UNCHANGED",
        "activation": False,
        "next_falsifiable_test": "Locate an original identified observation or terminal report tying Omega 1 to NORAD 308, with clock scale, instrument, frame, event definition and uncertainty.",
    }
    validate(payload)
    return payload


def validate(payload):
    o = payload["observation"]
    require(o["printed_calendar_range"] == ["1963-10-29", "1963-10-30"] and
            o["r59_secondary_calendar_day"] == "1963-10-30", "date ranges")
    require(o["secondary_norad_id"] == 308 and
            o["nasa_printed_norad_id"] is None and
            o["identity_grade"] == "SECONDARY_CROSSWALK_PENDING_PRIMARY_NORAD_ID",
            "identity promotion")
    for key in ("terminal_event_utc", "terminal_sigma_seconds", "station", "sensor",
                "reference_frame", "independent_instrumental_lineages"):
        require(o[key] is None, "fabricated measurement " + key)
    require(o["range_is_instrumental_utc"] is False and o["activation"] is False,
            "range promoted to UTC")
    require(payload["activation"] is False and
            payload["physical_domain_effect"] == "THETA_UNCHANGED" and
            payload["new_independent_instrumental_observations"] == 0 and
            payload["new_activated_physical_constraints"] == 0 and
            payload["historical_mcmc"] == "NOT_RUN", "physical activation")
    require(all(x["value"] is None and x["activation"] is False
                for x in payload["simulator_parameters"]), "parameter activation")
    require(all(x["activation"] is False for x in payload["lean_candidates"]), "Lean activation")
    graph = payload["graph"]
    require(len(graph) == 14 and
            len({(x["source"], x["target"], x["relation"]) for x in graph}) == 14,
            "duplicate or missing dependency edge")
    require(all(x["documentary_only"] is True and x["activation"] is False
                for x in graph), "graph physical promotion")


def render(root=ROOT):
    return (json.dumps(build(*load(root)), sort_keys=True, indent=2,
                       ensure_ascii=False) + "\n").encode("utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-site", action="store_true")
    args = ap.parse_args()
    content = render()
    if args.check_site:
        require(OUTPUT.read_bytes() == content, "published JSON differs from audited sources")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(content)
    print("C241-L64/R59 308 dependency: 14 documentary edges, 0 physical promotions")


if __name__ == "__main__":
    main()
