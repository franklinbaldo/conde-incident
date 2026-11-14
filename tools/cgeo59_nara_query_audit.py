#!/usr/bin/env python3
"""CGEO-59: audit frozen catalog searches and optionally replay live NARA JSON."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/geo/cgeo59_nara_cross_square_query.json"
IDS = ("op125374_23017", "op125370_23017", "constrained_conde", "nonsense_negative")
SEARCHES = (
    '125374 "2-3017"', '125370 "2-3017"',
    '125374 "2-3017" 11S037W',
    '125374 "2-3017" impossible_zzz_2026',
)
COMMON = ("46716637", "46716645", "46716877")
SQUARE = re.compile(r"Overlay indexes for degree square (\d\dS\d{3}W)\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(ok: bool, label: str) -> None:
    if not ok:
        raise ValueError(label)


def validate(data: dict) -> dict:
    require(isinstance(data, dict), "manifest object")
    require(data.get("schema") == "conde.cgeo.nara-combined-catalog-lookup/v1", "schema")
    require(data.get("id") == "CGEO-59", "id")
    require(data.get("endpoint") == "https://catalog.archives.gov/proxy/v3/records/search", "endpoint")
    queries = data.get("queries")
    require(isinstance(queries, list) and len(queries) == 4, "four searches")
    require(tuple(q.get("id") for q in queries) == IDS, "query ids")
    require(tuple(q.get("q") for q in queries) == SEARCHES, "query text")
    sets, squares, distractors = [], {}, set()
    for query in queries:
        require(query.get("limit") == 20 and query.get("http_status") == 200, "request metadata")
        require(type(query.get("body_bytes")) is int and query["body_bytes"] > 1000, "response bytes")
        digest = query.get("sha256")
        require(isinstance(digest, str) and SHA256.fullmatch(digest) is not None, "response hash")
        results = query.get("results")
        require(isinstance(results, list) and len(results) == query.get("total_hits"), "result count")
        ids = set()
        for rec in results:
            require(isinstance(rec, dict), "result object")
            naid, title = rec.get("naid"), rec.get("title")
            require(isinstance(naid, str) and naid.isdigit() and naid not in ids, "unique NAID")
            require(rec.get("level") == "fileUnit", "result level")
            require(isinstance(title, str) and bool(title), "result title")
            ids.add(naid)
            m = SQUARE.fullmatch(title)
            if m:
                require(naid not in squares or squares[naid] == m.group(1), "NAID/square conflict")
                squares[naid] = m.group(1)
            else:
                distractors.add(naid)
        sets.append(ids)
    require(len(sets[0]) == 11 and len(sets[1]) == 7, "primary search counts")
    require(sets[2] == {"46716637"}, "Conde-specific control")
    require(not sets[3], "impossible control")
    require(tuple(sorted(sets[0] & sets[1])) == COMMON, "shared index units")
    derived = data.get("derived")
    require(isinstance(derived, dict), "derived record")
    calculated = [
        {"naid": naid, "degree_square": square}
        for naid, square in sorted(squares.items(), key=lambda x: x[1])
    ]
    require(derived.get("candidate_overlay_file_units") == calculated, "catalog candidates")
    require(derived.get("candidate_count") == 11 and len(squares) == 11, "11 squares")
    require(derived.get("common_naids_between_primary_queries") == list(COMMON), "intersection")
    require(set(derived.get("unrelated_file_units", [])) == distractors, "distractors")
    require(derived.get("catalog_indexing_not_same_flight_proof") is True, "no flight proof")
    limits = data.get("limits")
    require(isinstance(limits, dict), "limits")
    require(limits.get("original_aerial_photograms_acquired") == 0, "no original frames")
    for key in (
        "spot_number", "film_can", "verified_flight_identity",
        "verified_photographic_coverage", "historical_urban_center_1963",
        "reported_fall_location",
    ):
        require(key in limits and limits[key] is None, "must remain null: " + key)
    require(limits.get("orbital_constraint_activated") is False, "no orbital constraint")
    require(limits.get("contact_sent") is False, "no archive contact")
    return {"queries": len(queries), "squares": len(squares), "distractors": len(distractors)}


def replay(data: dict) -> None:
    for query in data["queries"]:
        url = data["endpoint"] + "?" + urllib.parse.urlencode({"q": query["q"], "limit": 20})
        req = urllib.request.Request(
            url, headers={"Accept": "application/json", "User-Agent": "Conde-geo-custody/1.0"}
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            require(resp.status == 200, "HTTP status")
            require(resp.headers.get("Content-Type", "").lower().startswith("application/json"), "MIME")
            raw = resp.read(2_000_001)
        require(len(raw) <= 2_000_000, "JSON size")
        observed = json.loads(raw)["body"]["hits"]
        require(observed["total"]["value"] == query["total_hits"], "hit count drift")
        actual = sorted(
            (str(h["_id"]), h["_source"]["record"]["levelOfDescription"],
             h["_source"]["record"]["title"])
            for h in observed["hits"]
        )
        expected = sorted(
            (r["naid"], r["level"], r["title"]) for r in query["results"]
        )
        require(actual == expected, "membership or title drift")
        digest = hashlib.sha256(raw).hexdigest()
        print(
            "LIVE", query["id"], "hits", len(actual), "bytes", len(raw),
            "sha256", digest, "snapshot_digest_equal", digest == query["sha256"],
            flush=True,
        )


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    print("CGEO59_OFFLINE", validate(data), flush=True)
    if "--live" in sys.argv[1:]:
        replay(data)


if __name__ == "__main__":
    main()
