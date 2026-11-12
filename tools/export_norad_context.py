#!/usr/bin/env python3
"""Read Morcego's NORAD audit as documentary context, never 528 orbital observations.

The source audit retains custody of the underlying documents; this exporter
only binds source IDs/occurrence IDs to a snapshot-qualified NASA comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path("research/constraints/morcego_norad_1963_radar_source_audit.json")
OUTPUT = Path("public/data/conde-norad-context.json")
CITATIONS = Path("public/data/conde-source-citations.json")
LINEAGES = Path("research/provenance/lineages.json")

# Explicit object attribution, audited separately from ordinary text tokens:
# number 528 may appear in a *negative* claim and must NEVER be inferred as
# an observed object. The first 1964 file names no validated catalog object.
EXPECTED = {
    "MOR-NORAD-1961-AGREEMENT": ("1961-01-16", "NASA_DOD_1961_DATA_SHARING_POLICY", (), "MOR-NOR-20261112-01", None),
    "MOR-NORAD-1963-NOV12": ("1963-11-12", "NORAD_SPADATS_1963_SPUTNIK46", (687, 688), "MOR-NOR-20261112-02", None),
    "MOR-NORAD-1963-NOV14": ("1963-11-14", "NORAD_SPADATS_1963_SPUTNIK46", (688,), "MOR-NOR-20261112-03", None),
    "MOR-NORAD-1964-NOV30-09": ("1964-11-30", "NORAD_SPADATS_1964_SPUTNIK83", (), "MOR-NOR-20261112-04", "1963-11-30"),
    "MOR-NORAD-1964-NOV30-10": ("1964-11-30", "NORAD_SPADATS_1964_SPUTNIK83", (943,), "MOR-NOR-20261112-05", "1963-11-30"),
}

def serialize(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

def build(root: Path = ROOT) -> dict:
    source_bytes = (root / AUDIT).read_bytes()
    audit = json.loads(source_bytes)
    if audit.get("schema") != "conde.morcego-norad-1963-radar-document-audit/v1":
        raise ValueError("NORAD audit schema mismatch")
    if audit.get("november_1963_528_observation_found") is not False:
        raise ValueError("NORAD 528 observation must not be inferred from unrelated documents")
    if audit.get("original_sha256_status") != "UNAVAILABLE_EXTERNAL_PDF_BYTES_IN_RUNTIME":
        raise ValueError("original PDFs were not independently hashed by Morcego")
    sources = audit["sources"]
    occurrences = audit["occurrences"]
    if (len(sources) != len(EXPECTED)
            or {x["id"] for x in sources} != set(EXPECTED)
            or len(occurrences) != len(EXPECTED)
            or len({x["id"] for x in occurrences}) != len(occurrences)):
        raise ValueError("NORAD source or occurrence IDs missing/ambiguous")
    sources_by_id = {s["id"]: s for s in sources}
    source_occurrences = {x["source_id"]: x for x in occurrences}
    if len(source_occurrences) != len(EXPECTED):
        raise ValueError("NORAD duplicate source-to-occurrence attribution")
    records = []
    for sid, (date, lineage, object_ids, occurrence_id, catalog_date) in EXPECTED.items():
        src = sources_by_id[sid]
        occ = source_occurrences[sid]
        if (src.get("document_date") != date or src.get("lineage") != lineage
                or src.get("catalog_date_claim") != catalog_date
                or occ.get("id") != occurrence_id):
            raise ValueError("NORAD source ID / date / lineage / occurrence drift: " + sid)
        if (src.get("original_document_verified") != "SCREENSHOT_AND_TEXT"
                or src.get("original_pdf_sha256") is not None
                or occ.get("physical_constraint_active") is not False
                or not src.get("url", "").startswith("https://")):
            raise ValueError("NORAD verification/physical-boundary drift: " + sid)
        # Check that every positive object attribution is supported in the
        # audit's own scope; a bare "528" negative does not grant 528 status.
        if any(str(n) not in src["scope"] for n in object_ids):
            raise ValueError("NORAD object attribution absent from source scope: " + sid)
        if 528 in object_ids:
            raise ValueError("unrelated NORAD audit promoted to 528 observation")
        if "1964" in sid and (date[:4] != "1964" or catalog_date != "1963-11-30"):
            raise ValueError("1964 original confused with 1963 web metadata")
        records.append({
            "source_id": sid,
            "occurrence_id": occurrence_id,
            "source_date": date,
            "catalogue_date_claim": catalog_date,
            "source_url": src["url"],
            "source_locator": occ["anchor"],
            "documentary_claim": occ["claim"],
            "document_lineage": lineage,
            "object_ids_reported_in_this_document": list(object_ids),
            "original_pdf_sha256": None,
            "source_verification_as_reported_by_morcego": src["original_document_verified"],
            "role": "DOCUMENTARY_CONTEXT_NOT_528_MEASUREMENT",
            "matrix_occurrence_ref": None,
            "independent_528_physical_observation_count": None,
            "physical_528_constraint": None,
        })
    config = json.loads((root / LINEAGES).read_text())
    citation_feed = json.loads((root / CITATIONS).read_text())
    by_source = {s["id"]: s for s in config["sources"]}
    deps = {(e["from"], e["to"], e["kind"]) for e in config["dependencies"]}
    for pair in [
        ("NTRS_19640001198", "NASA_SSR_19631115", "catalogue_of_same_work"),
        ("FBIS_EOP_UAP_D001", "RADIO_TUPI_19631108", "transcribes"),
    ]:
        if pair not in deps:
            raise ValueError("critical independent-counting guard missing: " + repr(pair))
    if (by_source["NTRS_19640001198"]["work_id"]
            != by_source["NASA_SSR_19631115"]["work_id"]):
        raise ValueError("NASA original and NTRS catalogue must remain one work")
    if (by_source["NASA_SSR_19631115"]["family"] != "NORAD_NASA_TRACKING"
            or by_source["FBIS_EOP_UAP_D001"]["family"] != "RADIO_TUPI_FBIS"):
        raise ValueError("NASA/NORAD or FBIS/Tupi family drift")

    contextual = []
    for occurrence, sid in [("C197#1", "NASA_SSR_19631115"), ("C198#1", "NTRS_19640001198")]:
        ref = pg.matrix_ref(occurrence)
        match = [x for x in citation_feed["records"]
                 if x["snapshot_ref"] == ref and x["source_id"] == sid]
        if len(match) != 1 or match[0].get("row_sha256") is None:
            raise ValueError("unverified snapshot-qualified NASA comparison " + occurrence)
        x = match[0]
        contextual.append({
            "snapshot_ref": ref, "source_id": sid,
            "matrix_line": x["matrix_line"], "row_sha256": x["row_sha256"],
            "relationship": "CONTEXTUAL_COMPARISON_NOT_MORCEGO_528_OBSERVATION",
        })
    return {
        "schema": "conde.norad-documentary-context/v1",
        "source_audit_path": AUDIT.as_posix(),
        "source_audit_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "matrix_git_blob_sha1": pg.MATRIX_BLOB_SHA,
        "matrix_snapshot_id": pg.MATRIX_SNAPSHOT_ID,
        "records": records,
        "declared_documentary_groups": [
            {"source_ids": ["MOR-NORAD-1963-NOV12", "MOR-NORAD-1963-NOV14"],
             "relation": "SAME_SPUTNIK46_REPORTING_FAMILY_NOT_INDEPENDENT_528_WITNESSES"},
            {"source_ids": ["MOR-NORAD-1964-NOV30-09", "MOR-NORAD-1964-NOV30-10"],
             "relation": "SAME_SPUTNIK83_1964_REPORTING_FAMILY_NOT_1963"},
        ],
        "nasa_norad_policy_bridge": {
            "source_id": "MOR-NORAD-1961-AGREEMENT",
            "relation": "DATA_EXCHANGE_POSSIBLE_NOT_PROOF_OF_MEASUREMENT_LINEAGE",
            "contextual_matrix_citations": contextual,
            "actual_528_measurement_upstream": None,
        },
        "epistemic_limits": {
            "document_authenticity_independently_rechecked_by_abelha": False,
            "no_source_is_an_observation_of_norad_528": True,
            "no_new_528_trajectory_or_decay_bound": True,
            "unknown_independent_physical_observation_count": None,
            "do_not_merge_mor_nor_ids_with_Cnn_matrix_occurrences": True,
        },
    }

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write-site", action="store_true")
    g.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    data = serialize(build())
    if len(data.encode("utf-8")) > 20_000:
        raise ValueError("NORAD context export over 20KB")
    if args.write_site:
        (ROOT / OUTPUT).write_text(data, encoding="utf-8")
    elif not (ROOT / OUTPUT).is_file() or (ROOT / OUTPUT).read_text() != data:
        raise SystemExit("NORAD context export stale: run --write-site")
    print("NORAD_CONTEXT_OK", len(build()["records"]), "records", len(data.encode()), "bytes")

if __name__ == "__main__":
    main()
