#!/usr/bin/env python3
"""Compile an explicitly curated documentary lineage onto the frozen C01-C238 matrix.

No automatic inference from URL similarity, a matrix row, checksum, or a
document title is permitted. An unmapped occurrence stays unmapped.
The graph is a citation/custody export, NOT a catalogue of physical sightings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "research/evidence_matrix_C001-C238_2026-11-11.md"
LINEAGES = ROOT / "research/provenance/lineages.json"
SITE = ROOT / "public/data/conde-source-citations.json"
MATRIX_BLOB_SHA = "a7978c3a75a153b16ab70118a92c434bba674cb7"
MATRIX_SNAPSHOT_ID = f"matrix:{MATRIX_BLOB_SHA}"
# Cumulative ledger: a later snapshot merge must not silently erase NARA custody.
REQUIRED_POST_MATRIX_IDS = {"NARA-BB-CONDE-20261112-01"}


def matrix_ref(occurrence: str) -> str:
    """Full content-addressed claim reference; a Cnn ID is never a global key."""
    return f"{MATRIX_SNAPSHOT_ID}:{occurrence}"


def legacy_alias_audit(raw: bytes, root: Path = ROOT) -> dict:
    """Consume Polvo's byte-pinned audit, not a duplicate parser or physical claim."""
    script = root / "formal/scripts/audit_legacy_154.py"
    audit = runpy.run_path(str(script))["audit"]
    report = audit((root / "formal/Conde1963/Evidence.lean").read_bytes(), raw)
    if len(report["claim_aliases_requiring_snapshot_qualified_ids"]) != 8:
        raise ValueError("legacy snapshot alias inventory differs from C144-C151")
    return report


def snapshot_aliases(report: dict, rows: list[dict]) -> list[dict]:
    current_rows = {r["occurrence"]: r for r in rows}
    aliases = []
    for item in report["claim_aliases_requiring_snapshot_qualified_ids"]:
        occurrence = item["old_key"] + "#1"
        current = current_rows[occurrence]
        aliases.append({
            "legacy_ref": (
                f"legacy-154:{report['archived_bytes_sha256']}:{occurrence}"
            ),
            "matrix_ref": current["snapshot_ref"],
            "legacy_claim": item["old_claim"],
            "matrix_claim": item["current_claim"],
            "matrix_line": current["matrix_line"],
            "matrix_row_sha256": current["row_sha256"],
            "equivalent_claim": False,
            "legacy_source_status": report["source_status"],
            "not_a_verified_physical_event": True,
        })
    if [x["matrix_ref"].rsplit(":", 1)[-1] for x in aliases] != [
        f"C{i}#1" for i in range(144, 152)
    ]:
        raise ValueError("snapshot alias list changed")
    return aliases

ROW = re.compile(r"^\|\s*(?:\*\*)?(C[0-9]+)(?:\*\*)?\s*\|")
VALID_RELATIONS = {
    "transcribes", "quotes_uninspected_source", "catalogue_of_same_work",
    "later_issue_same_series", "aggregates_from",
}
CITATION_RELATIONS = {
    "reported_claim", "quotes_uninspected_source", "measured_index",
    "refutes_independence", "catalogued_day", "measured_environment",
    "metadata_limit", "secondary_orbital_elements", "archival_status",
    "conditional_comparison", "archive_metadata", "edition_control",
    "corrects_prior_interpretation", "shared_upstream", "documentary_comparison",
}
# Nothing in this export is evidence of debris, craters, bodies or impact.
FORBIDDEN_PHYSICAL_SCOPE = {"PHYSICAL_IMPACT_CONFIRMED", "OBSERVED_TERMINAL_LOCATION"}
PINNED_GROUPS = {
    "RADIO_TUPI_19631108": "RADIO_TUPI_FBIS",
    "FBIS_EOP_UAP_D001": "RADIO_TUPI_FBIS",
    "NASA_SSR_19631115": "NORAD_NASA_TRACKING",
    "NASA_SSR_19631130": "NORAD_NASA_TRACKING",
    "NTRS_19640001198": "NORAD_NASA_TRACKING",
    "AFSPC_MIRROR_528": "NORAD_NASA_TRACKING",
    "AFSPC_MIRROR_529": "NORAD_NASA_TRACKING",
}
PINNED_EDGE_KINDS = {
    ("FBIS_EOP_UAP_D001", "RADIO_TUPI_19631108"): "transcribes",
    ("NTRS_19640001198", "NASA_SSR_19631115"): "catalogue_of_same_work",
    ("CELESTRAK_SPACE_WEATHER", "GFZ_KP_AP_SERIES"): "aggregates_from",
    ("CELESTRAK_SPACE_WEATHER", "NRC_F107_SERIES"): "aggregates_from",
}


def matrix_occurrences(raw: bytes) -> list[dict]:
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != MATRIX_BLOB_SHA:
        raise ValueError("matrix snapshot differs from pinned git blob; audit before updating")
    counts = Counter()
    entries = []
    for line_no, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        match = ROW.match(line)
        if not match:
            continue
        label = match.group(1)
        counts[label] += 1
        claim_cell = line.split("|", 3)[2].strip()
        if not claim_cell:
            raise ValueError(f"blank matrix claim at line {line_no}")
        entries.append({
            "occurrence": f"{label}#{counts[label]}",
            "snapshot_ref": matrix_ref(f"{label}#{counts[label]}"),
            "label": label,
            "index": counts[label],
            "matrix_line": line_no,
            "claim_text": claim_cell,
            "row_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
            "matrix_blob_sha1": blob,
        })
    if len(entries) != 241 or len(counts) != 238:
        raise ValueError("matrix occurrence inventory differs from 241 rows / 238 labels")
    expected_labels = {f"C{i:02d}" for i in range(1, 10)} | {f"C{i}" for i in range(10, 239)}
    if set(counts) != expected_labels or {
        label: n for label, n in counts.items() if n != 1
    } != {"C44": 2, "C45": 2, "C46": 2}:
        raise ValueError("ID set or C44-C46 collision inventory changed")
    if len({e["occurrence"] for e in entries}) != len(entries):
        raise ValueError("ambiguous source occurrence identity")
    return entries


def validate_lineages(config: dict, rows: list[dict], root: Path = ROOT) -> None:
    if config.get("schema") != "conde.source-lineages/v1":
        raise ValueError("unrecognized lineage schema")
    if not all(isinstance(config.get(key), list) and config[key] for key in
               ("families", "sources", "dependencies", "citations", "contracts")):
        raise ValueError("required curated graph sections missing")
    families = {e["id"]: e for e in config["families"]}
    sources = {e["id"]: e for e in config["sources"]}
    occurrences = {r["occurrence"] for r in rows}
    if len(families) != len(config["families"]) or len(sources) != len(config["sources"]):
        raise ValueError("duplicate source/family ID")
    for src in config["sources"]:
        if src["family"] not in families:
            raise ValueError("source with missing family " + src["id"])
        if not src.get("work_id") or not src.get("status") or not src.get("locator"):
            raise ValueError("source missing work/status/locator " + src["id"])
        url = src.get("url")
        if url is not None and (not isinstance(url, str) or not url.startswith("https://")):
            raise ValueError("source needs HTTPS citation URL or null " + src["id"])
    for sid, family in PINNED_GROUPS.items():
        if sid not in sources or sources[sid]["family"] != family:
            raise ValueError("lineage grouping regression: " + sid)
    if sources["NTRS_19640001198"]["work_id"] != sources["NASA_SSR_19631115"]["work_id"]:
        raise ValueError("catalogue page cannot masquerade as an independent document")

    seen_edges, adj = set(), defaultdict(list)
    for edge in config["dependencies"]:
        key = edge["from"], edge["to"]
        if key in seen_edges or key[0] == key[1] or any(x not in sources for x in key):
            raise ValueError("duplicate/self/orphan dependency edge " + repr(key))
        seen_edges.add(key)
        if edge["kind"] not in VALID_RELATIONS:
            raise ValueError("unknown documentary relation: " + edge["kind"])
        adj[key[0]].append(key[1])
    for pair, kind in PINNED_EDGE_KINDS.items():
        if pair not in seen_edges or next(e for e in config["dependencies"]
                                          if (e["from"], e["to"]) == pair)["kind"] != kind:
            raise ValueError("critical dependence erased: " + repr(pair))
    # Check only directed declared dependencies, never assume sources independent
    # merely because a dependency edge was not yet documented.
    color = {}
    def visit(node: str) -> None:
        if color.get(node) == 1:
            raise ValueError("cycle in documentary lineage at " + node)
        if color.get(node) == 2:
            return
        color[node] = 1
        for parent in adj[node]:
            visit(parent)
        color[node] = 2
    for sid in sources:
        visit(sid)

    seen_citations = set()
    by_occurrence = defaultdict(list)
    for link in config["citations"]:
        occurrence, source = link["occurrence"], link["source_id"]
        key = occurrence, source
        if occurrence not in occurrences or source not in sources or key in seen_citations:
            raise ValueError("orphan/duplicate/ambiguous citation " + repr(key))
        seen_citations.add(key)
        if link.get("snapshot_ref") != matrix_ref(occurrence):
            raise ValueError("citation snapshot mismatch or missing: " + occurrence)
        by_occurrence[occurrence].append(link)
        if link["relation"] not in CITATION_RELATIONS:
            raise ValueError("undocumented citation relation " + link["relation"])
        if (link["scope"] in FORBIDDEN_PHYSICAL_SCOPE or
            not link["scope"] or link.get("physically_verified") is True):
            raise ValueError("physical observation promoted by a citation " + occurrence)
    if ([(x["source_id"], x["relation"]) for x in by_occurrence["C197#1"]] !=
        [("NASA_SSR_19631115", "catalogued_day")]):
        raise ValueError("NASA 8 NOV 63 must be source-identified as catalogued DAY only")
    if [(x["source_id"], x["relation"]) for x in by_occurrence["C198#1"]] != [
        ("NTRS_19640001198", "archive_metadata")
    ]:
        raise ValueError("NASA NTRS catalogue record must not become independent sensor")
    for label in ("C01#1", "C02#1", "C03#1"):
        if {x["source_id"] for x in by_occurrence[label]} != {"FBIS_EOP_UAP_D001"}:
            raise ValueError("Tupi/FBIS derivative record may not become independent witness")
    if {x["source_id"] for x in by_occurrence["C179#1"]} != {"AFSPC_MIRROR_528"}:
        raise ValueError("unverified mirror cannot be asserted as original tracking")

    # Post-snapshot source occurrences are append-only typed addenda. They must not
    # rewrite or renumber the 241 frozen rows and cannot imply physical corroboration.
    addenda = config.get("post_matrix_occurrences", [])
    if not isinstance(addenda, list):
        raise ValueError("post_matrix_occurrences must be an array")
    seen_addenda = set()
    for update in addenda:
        uid = update.get("id")
        if not isinstance(uid, str) or not uid or uid in seen_addenda or uid in occurrences:
            raise ValueError("duplicate or missing post-matrix occurrence ID")
        seen_addenda.add(uid)
        if update.get("source_id") not in sources or update.get("quoted_source_id") not in sources:
            raise ValueError("post-matrix occurrence orphan source " + uid)
        if ((update["source_id"], update["quoted_source_id"]) not in seen_edges
                or any(edge["kind"] != "quotes_uninspected_source"
                       for edge in config["dependencies"]
                       if (edge["from"], edge["to"]) ==
                       (update["source_id"], update["quoted_source_id"]))):
            raise ValueError("post-matrix source has no explicit uninspected quotation edge " + uid)
        related = update.get("related_matrix_occurrences")
        if not isinstance(related, list) or not related or len(related) != len(set(related)) or (
                set(related) - occurrences):
            raise ValueError("post-matrix occurrence has missing/duplicate/unknown matrix links " + uid)
        if update.get("status") != "CONNECTED_PENDING_DOCUMENTARY_VERIFICATION" or (
                update.get("observation_type") != "DOCUMENTARY_CITATION_NOT_PHYSICAL_OBSERVATION"):
            raise ValueError("post-matrix must remain pending documentary evidence " + uid)
        if (update.get("newspaper_page") is not None or
            update.get("newspaper_edition") is not None or
            update.get("newspaper_publication_time") is not None or
            update.get("journalistic_source_independence") != "UNRESOLVED" or
            update.get("physical_constraint") is not None):
            raise ValueError("unverified newspaper or physical assumption introduced " + uid)
        if not re.fullmatch("[0-9a-f]{64}", update.get("image_sha256", "")):
            raise ValueError("post-matrix digital object missing SHA-256 " + uid)
        report = Path(update.get("report_path", ""))
        if not report.parts or report.is_absolute() or ".." in report.parts or (
                not (root / report).is_file()):
            raise ValueError("post-matrix report missing or unsafe " + uid)

    if not REQUIRED_POST_MATRIX_IDS.issubset(seen_addenda):
        raise ValueError("required cumulative post-matrix documentary occurrence erased")

    contract_ids = set()
    for item in config["contracts"]:
        if not item["id"] or item["id"] in contract_ids:
            raise ValueError("contract missing/duplicate id")
        contract_ids.add(item["id"])
        path = Path(item["path"])
        if path.is_absolute() or ".." in path.parts or not (root / path).is_file():
            raise ValueError("contract missing or path escapes checkout: " + str(path))
        if any(occ not in occurrences for occ in item["occurrences"]):
            raise ValueError("contract has unindexed evidence occurrence")
        if item.get("snapshot_refs") != [
            matrix_ref(occ) for occ in item["occurrences"]
        ]:
            raise ValueError("contract snapshot mismatch or missing: " + item["id"])
        if item["status"] in FORBIDDEN_PHYSICAL_SCOPE:
            raise ValueError("contract overclaims physical corroboration")


def build(config: dict, raw: bytes, root: Path = ROOT) -> tuple[dict, dict]:
    records = matrix_occurrences(raw)
    validate_lineages(config, records, root)
    # The old 154-row Lean library is preserved locally, not authenticated.
    # Do not join documentary rows on recycled Cnn labels.
    legacy_report = legacy_alias_audit(raw, root)
    alias_conflicts = snapshot_aliases(legacy_report, records)
    source_by_id = {s["id"]: s for s in config["sources"]}
    by_occurrence: dict[str, list[dict]] = defaultdict(list)
    export = []
    for cite in config["citations"]:
        src = source_by_id[cite["source_id"]]
        row = next(r for r in records if r["occurrence"] == cite["occurrence"])
        record = {
            "occurrence": row["occurrence"],
            "snapshot_ref": row["snapshot_ref"],
            "matrix_line": row["matrix_line"],
            "row_sha256": row["row_sha256"],
            "claim_text": row["claim_text"],
            "source_id": src["id"],
            "source_family": src["family"],
            "work_id": src["work_id"],
            "citation_url": src["url"],
            "locator": src["locator"],
            "source_status": src["status"],
            "relation": cite["relation"],
            "scope": cite["scope"],
            "not_a_verified_conde_physical_event": True,
        }
        by_occurrence[row["occurrence"]].append({
            "source_id": src["id"], "relation": cite["relation"], "scope": cite["scope"],
            "snapshot_ref": row["snapshot_ref"]
        })
        export.append(record)
    mapped_count = len(by_occurrence)
    # Preserve every row, including the three ambiguous labels whose occurrences
    # have unrelated meanings; unmapped entries stay explicitly unmapped.
    for row in records:
        row["citations"] = by_occurrence[row["occurrence"]]
        row["citation_status"] = "CURATED" if row["citations"] else "UNMAPPED_NOT_CLEARED"
    citations = {
        "schema": "conde.source-citations/v1",
        "matrix_git_blob_sha1": MATRIX_BLOB_SHA,
        "matrix_snapshot_id": MATRIX_SNAPSHOT_ID,
        "legacy_alias_conflicts": [{
            "legacy_ref": a["legacy_ref"],
            "matrix_ref": a["matrix_ref"],
            "equivalent_claim": False,
            "legacy_source_status": a["legacy_source_status"],
        } for a in alias_conflicts],
        "total_matrix_occurrences": len(records),
        "curated_occurrences": mapped_count,
        "unmapped_occurrences": len(records) - mapped_count,
        "records": sorted(export, key=lambda x: (x["matrix_line"], x["source_id"])),
    }
    graph = {
        "schema": "conde.documentary-provenance-graph/v1",
        "matrix_git_blob_sha1": MATRIX_BLOB_SHA,
        "matrix_snapshot_id": MATRIX_SNAPSHOT_ID,
        "legacy_snapshot_status": legacy_report["source_status"],
        "legacy_alias_conflicts": alias_conflicts,
        "limits": {
            "inference": "documentary_only; sources not inferred from free text",
            "independent_physical_tracking_count": None,
            "verified_reentry_time_utc": None,
            "verified_reentry_location": None,
            "verified_Conde_impact": False,
            "unmapped_does_not_mean_absent": True,
        },
        "families": config["families"],
        "sources": config["sources"],
        "source_dependencies": config["dependencies"],
        "matrix_occurrences": records,
        "post_matrix_occurrences": [
            {**item, "related_matrix_snapshot_refs": [
                matrix_ref(occ) for occ in item["related_matrix_occurrences"]
            ]} for item in config.get("post_matrix_occurrences", [])
        ],
        "contracts": config["contracts"],
        "citation_summary": {
            "matrix_occurrences": len(records),
            "curated_occurrences": mapped_count,
            "curated_citation_edges": len(export),
            "unmapped_occurrences": len(records) - mapped_count,
        },
    }
    return graph, citations


def serialize(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write full provenance graph JSON")
    parser.add_argument("--citations", type=Path, help="write curated source-ID-occurrence JSON")
    parser.add_argument("--write-site", action="store_true", help="refresh versioned site feed")
    parser.add_argument("--check-site", action="store_true", help="assert site feed matches source")
    args = parser.parse_args()
    if args.write_site and args.check_site:
        parser.error("--write-site and --check-site are incompatible")
    graph, cites = build(json.loads(LINEAGES.read_text()), MATRIX.read_bytes())
    for path, object_ in ((args.output, graph), (args.citations, cites)):
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(serialize(object_), encoding="utf-8")
    if args.write_site:
        SITE.parent.mkdir(parents=True, exist_ok=True)
        SITE.write_text(serialize(cites), encoding="utf-8")
    if args.check_site and (not SITE.is_file() or SITE.read_text() != serialize(cites)):
        raise SystemExit("stale site source-citation feed: run python3 tools/provenance_graph.py --write-site")
    print(json.dumps({"matrix_occurrences": len(graph["matrix_occurrences"]),
                      **graph["citation_summary"], "site_verified": args.check_site}))


if __name__ == "__main__":
    main()
