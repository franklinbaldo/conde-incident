#!/usr/bin/env python3
"""Audit 1963 NASA Satellite Situation Report index coverage, not orbits."""
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
LEDGER = BASE / "research/tle_custody/ntrs_ssr_1963_index_C241-L25.json"
QUERY = {"q": "Satellite Situation Report", "page": {"size": 200, "from": 0}}
API = "https://ntrs.nasa.gov/api/citations/search"
ISSUES = {
    19630012113: (2, "NTRS_TITLE"),
    19630012127: (8, "C241-L23"),
    19630012128: (9, "C241-L16"),
    19630012130: (13, "C241-L22"),
    19630012290: (15, "C241-L18"),
    19630012289: (16, "C241-L17"),
    19640000428: (20, "C241-L12_FACSIMILE"),
    19640001198: (22, "C241-L11"),
    19640002493: (23, "C241-L18"),
    19640003479: (24, "C241-L21"),
    19640005618: (25, "C241-L18_FACSIMILE"),
}


def fetch():
    req = urllib.request.Request(
        API, data=json.dumps(QUERY).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=40) as response:
        raw = response.read()
    payload = json.loads(raw)
    stats = payload["stats"]
    rows = payload["results"]
    if (not isinstance(stats["total"], int) or
            stats["total"] > QUERY["page"]["size"] or
            stats["total"] != len(rows)):
        raise ValueError("partial page: cannot make negative index finding")
    return rows, {"response_sha256": hashlib.sha256(raw).hexdigest(),
                  "response_bytes": len(raw), "total": stats["total"]}


def published_1963(row):
    dates = {str(x.get("publicationDate", ""))[:10]
             for x in row.get("publications", [])
             if str(x.get("publicationDate", "")).startswith("1963-")}
    if len(dates) > 1:
        raise ValueError("conflicting publication dates")
    return next(iter(dates), None)


def project(row):
    published = published_1963(row)
    if not published:
        raise ValueError("not a publication dated 1963")
    return {
        "ntrs_id": row["id"], "published_on": published,
        "title_as_indexed": row["title"],
        "report_numbers_as_indexed": row.get("otherReportNumbers", []),
    }


def index_21(row):
    haystack = [str(row.get("title", ""))]
    haystack += [str(x) for x in row.get("otherReportNumbers", [])]
    return any(re.search(r"\bvol(?:ume)?\.?\s*3\b.{0,15}\bno\.?\s*21\b", text, re.I)
               for text in haystack)


def analyze(rows, ledger, metadata=None):
    if ledger.get("id") != "C241-L25" or ledger.get("query") != QUERY:
        raise ValueError("index query not source-locked")
    original = ledger.get("known_records", [])
    locked = {r["ntrs_id"]: r for r in original}
    if len(original) != len(ISSUES) or set(locked) != set(ISSUES):
        raise ValueError("missing or duplicated anchor")
    for id_, (issue, origin) in ISSUES.items():
        r = locked[id_]
        if (r.get("issue_number_from_project") != issue or
                r.get("issue_number_provenance") != origin):
            raise ValueError("source crosswalk altered")
    published = [r for r in rows if published_1963(r)]
    actual = {r["id"]: r for r in published}
    if len(actual) != len(published):
        raise ValueError("duplicate source ID")
    for id_ in ISSUES:
        if id_ not in actual:
            raise ValueError(f"anchor absent from current search: {id_}")
        computed = project(actual[id_])
        if computed != {k: locked[id_][k] for k in computed}:
            raise ValueError(f"NASA metadata changed for {id_}, inspect source")
    candidates = sorted(r["id"] for r in published if index_21(r))
    return {
        "id": "C241-L25", "status": "NASA_NTRS_INDEX_METADATA_ONLY",
        "known_source_ids": sorted(ISSUES),
        "known_issue_numbers": sorted({v[0] for v in ISSUES.values()}),
        "additional_1963_record_ids_need_review": sorted(set(actual) - set(ISSUES)),
        "issue_21_candidate_ids": candidates,
        "issue_21_status": "POSSIBLE_INDEX_MATCH_NEEDS_FACSIMILE" if candidates
                           else "NOT_LOCATED_IN_THIS_QUERY",
        "index_search_does_not_prove_absence": True,
        "instrumental_observations": 0,
        "physical_constraints_activated": 0,
        "publication_date_is_instrument_epoch": False,
        "conde": "INDETERMINATE",
        "live_query_total": (metadata or {}).get("total"),
        "live_query_sha256": (metadata or {}).get("response_sha256"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if args.live:
        rows, meta = fetch()
    else:
        rows = [{
            "id": x["ntrs_id"], "title": x["title_as_indexed"],
            "otherReportNumbers": x["report_numbers_as_indexed"],
            "publications": [{"publicationDate": x["published_on"] + "T00:00:00Z"}],
        } for x in ledger["known_records"]]
        meta = {}
    result = analyze(rows, ledger, meta)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

