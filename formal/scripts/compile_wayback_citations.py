#!/usr/bin/env python3
"""Compile the audited WB-01 custody graph into typed Lean documentary links.

No snapshot is treated as a sensor or as a historical event timestamp.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import export_wayback_citation_links as upstream  # noqa: E402

SOURCE = ROOT / upstream.OUTPUT
DEPENDENCE = ROOT / upstream.DEPENDENCE
TARGET = ROOT / "formal/Conde1963/WaybackCitations.lean"
REF = re.compile(r"matrix:([0-9a-f]{40}):C(\d+)#([1-9]\d*)\Z")
HEX = re.compile(r"[a-f0-9]{64}\Z")
CDX = re.compile(r"[A-Z2-7]{32}\Z")
EXPECTED = {"C197#1": "NASA_SSR_19631115", "C198#1": "NTRS_19640001198"}


def require(ok: bool, problem: str) -> None:
    if not ok:
        raise ValueError("WB-01 Lean: " + problem)


def quote(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def opt(s: str | None) -> str:
    return "none" if s is None else "some " + quote(s)


def validate(data: dict, document: dict) -> tuple[list[dict], list[dict], list[dict]]:
    require(data.get("schema") == "conde.wayback-citation-links/v1", "schema")
    require(document["matrix_git_blob_sha1"] == data["matrix_git_blob_sha1"], "matrix snapshot")
    require(data["counts"] == {
        "documentary_works": 3, "verified_archived_copies": 5,
        "nasa_legacy_capture_timestamps": 3,
        "nasa_legacy_distinct_pdf_payloads": 1,
        "negative_exact_url_lookups": 1, "matrix_occurrences_linked": 2,
        "supplementary_refs_not_matrix": 3,
        "independent_physical_observations_added": 0,
    }, "unexpected cardinalities/observations")
    require(all(data["epistemic_limits"].get(flag) is True for flag in (
        "NASA_NTRS_same_work_not_two_independent_sensors",
        "CDX_digest_is_base32_sha1_not_sha256",
        "negative_exact_lookup_does_not_prove_absence_at_other_urls",
        "no_active_lean_constraint", "no_simulator_parameter_activated",
        "legacy_capture_identity_is_manifest_validated_not_live_replayed_here",
    )), "epistemic scope changed")
    nodes = data["nodes"]
    by_id = {n["id"]: n for n in nodes}
    require(len(nodes) == len(by_id), "duplicate node ID")
    sources = [n for n in nodes if n["kind"] == "DOCUMENTARY_SOURCE"]
    captures = [n for n in nodes if n["kind"] == "VERIFIED_ARCHIVAL_COPY"]
    matrix = [n for n in nodes if n["kind"] == "FROZEN_MATRIX_CITATION"]
    supp = [n for n in nodes if n["kind"] == "SUPPLEMENTARY_SOURCE_REF_NOT_MATRIX"]
    negatives = [n for n in nodes if n["kind"] == "NEGATIVE_EXACT_URL_LOOKUP"]
    payloads = [n for n in nodes if n["kind"] == "ONE_ARCHIVED_DOCUMENT_PAYLOAD"]
    require((len(sources), len(captures), len(matrix), len(supp), len(negatives), len(payloads))
            == (3, 5, 2, 3, 1, 1), "source/citation census")
    payload = payloads[0]
    require(payload["id"] == "WB-NASA-SSR-19631115:PDF-SHA256:" + upstream.NASA_BYTES_SHA256
            and payload["sha256"] == upstream.NASA_BYTES_SHA256
            and payload["bytes"] == 327613
            and payload["distinct_documentary_payload_count"] == 1
            and payload["new_physical_observations"] == 0,
            "legacy NASA unique PDF payload")
    require({n["id"] for n in sources} == set(upstream.EXPECTED), "source identity")
    for s in sources:
        expected_status, family, url, refs = upstream.EXPECTED[s["id"]]
        require(s["capture_status"] == expected_status
                and s["source_family"] == family
                and s["original_url"] == url
                and s["source_refs"] == list(refs)
                and s["new_physical_observations"] == 0,
                "document/source identity")
    old_captures = [c for c in captures if ":LEGACY-CAPTURE:" in c["id"]]
    regular = [c for c in captures if ":CAPTURE:" in c["id"] and c not in old_captures]
    require(len(old_captures) == 3 and len(regular) == 2, "legacy PDF copies census")
    known_legacy = {"20150217133001", "20170228144859", "20170302093149"}
    for c in captures:
        sep = ":LEGACY-CAPTURE:" if c in old_captures else ":CAPTURE:"
        p = c["id"].split(sep)
        require(len(p) == 2 and p[0] in upstream.EXPECTED, "capture source")
        when = datetime.strptime(p[1], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        original = (c["cdx_original_url"] if c in old_captures
                    else upstream.EXPECTED[p[0]][2])
        require(c["capture_utc"] == when.isoformat().replace("+00:00", "Z")
                and c["archived_url"] == "https://web.archive.org/web/" + p[1] + "id_/" + original
                and c["retrieved_bytes_length"] > 0
                and HEX.fullmatch(c["retrieved_bytes_sha256"]) is not None
                and CDX.fullmatch(c["cdx_digest_base32_sha1"]) is not None
                and c["new_physical_observations"] == 0,
                "Wayback capture / PDF integrity")
        if c in old_captures:
            require(p[0] == "WB-NASA-SSR-19631115"
                    and p[1] in known_legacy
                    and original.endswith("/archive/nasa/casi.ntrs.nasa.gov/19640001198.pdf")
                    and c["retrieved_bytes_sha256"] == upstream.NASA_BYTES_SHA256
                    and c["retrieved_bytes_length"] == payload["bytes"]
                    and c["cdx_digest_base32_sha1"] == "I2EGWPNOUYBQW3TJASLYO5JASEALQJSK",
                    "legacy Wayback aliases changed or invented independent bytes")
        else:
            require(upstream.EXPECTED[p[0]][0] == "VERIFIED_REPLAY"
                    and c["http_status"] == 200 and c["mime"] == "application/pdf"
                    and (c["retrieved_bytes_sha256"], c["cdx_digest_base32_sha1"])
                       == upstream.EXPECTED_CAPTURE_HASHES[p[0]],
                    "Wayback capture / PDF integrity")
    require({c["id"].split(":LEGACY-CAPTURE:")[1] for c in old_captures} == known_legacy,
            "missing or duplicate NASA legacy capture")
    for n in negatives:
        require(n["id"] == "WB-NASA-SSR-19631115:EXACT_URL_LOOKUP"
                and n["scope"] == "EXACT_URL_ONLY_NOT_ABSENCE_OF_WORK"
                and n["capture_utc"] is None
                and n["query_url"] == upstream.EXPECTED["WB-NASA-SSR-19631115"][2],
                "negative lookup promoted into historical absence")
    declared = {(c["snapshot_ref"].rsplit(":", 1)[-1], c["source_id"]): c
                for c in document["citation_lineages"]}
    require(len(declared) == len(document["citation_lineages"]), "duplicate matrix citation")
    by_label = {}
    for c in matrix:
        match = REF.fullmatch(c["snapshot_ref"])
        require(match is not None and match.group(1) == data["matrix_git_blob_sha1"],
                "unfrozen matrix reference")
        label = "C" + match.group(2) + "#" + match.group(3)
        require(label in EXPECTED and c["source_id"] == EXPECTED[label]
                and c["id"] == "WB-NASA-SSR-19631115:REF:" + label,
                "C197/C198 citation mismatch")
        old = declared[(label, EXPECTED[label])]
        require(old["row_sha256"] == c["row_sha256"]
                and old["snapshot_ref"] == c["snapshot_ref"]
                and old["family_id"] == "NORAD_NASA_TRACKING"
                and old["independent_physical_observation_count"] is None,
                "unverified matrix row or sensor independence")
        require(c["lean_status"] == "DAY_ONLY_PREMISE_NO_TERMINAL_TIME"
                and c["hypothesis"] == "H_528_REENTRY_EVENT_TIME_UNKNOWN"
                and c["simulator_parameter"] == "reentry_terminal_timestamp_528"
                and c["simulator_value"] is None and c["activation"] is False
                and c["new_physical_observations"] == 0,
                "historical event time invented/parameter activated")
        by_label[label] = (c, old)
    require(set(by_label) == set(EXPECTED), "citation labels missing")
    # A catalogue record and the underlying NASA SSR identify the SAME work.
    # work_id is present in the canonical source-citations feed and Lean Documentary.
    source_feed = json.loads((ROOT / "public/data/conde-source-citations.json").read_text())
    feed_rows = source_feed.get("records")
    require(isinstance(feed_rows, list), "canonical source-citation feed shape")
    for label, (c, old) in by_label.items():
        matching = [r for r in feed_rows if r.get("source_id") == c["source_id"]
                    and r.get("snapshot_ref") == c["snapshot_ref"]]
        require(len(matching) == 1 and matching[0]["work_id"] == "NASA_SSR_VOL3_22",
                "C197/C198 cease to identify the same original NASA work")
    ntrs = by_label["C198#1"][1]["declared_upstream_paths"]
    require(len(ntrs) == 1 and ntrs[0]["upstream_source_id"] == EXPECTED["C197#1"],
            "NTRS catalogue lineage changed")
    require(all(x["matrix_snapshot_ref"] is None and x["simulator_value"] is None
                and x["simulator_parameter"] is None and x["activation"] is False
                and x["lean_status"] == "NOT_ASSESSED_NO_OBJECT_528_MEASUREMENT"
                for x in supp), "supplementary source promoted to measurement")
    expected_edges = {(e["from"], e["to"], e["kind"]) for e in data["edges"]}
    required_edges = {
        ("WB-NASA-SSR-19631115:EXACT_URL_LOOKUP", "WB-NASA-SSR-19631115",
         "NO_EXACT_CAPTURE_IN_QUERIED_INDEX"),
        ("WB-NASA-SSR-19631115:REF:C198#1", "WB-NASA-SSR-19631115:REF:C197#1",
         "NTRS_CATALOG_OF_SAME_NASA_WORK_NOT_INDEPENDENT"),
    }
    required_edges |= {(s["id"], n["id"], "DOC_SOURCE_TO_SNAPSHOT_CITATION")
                       for s in sources for n in matrix
                       if s["id"] == "WB-NASA-SSR-19631115"}
    required_edges |= {(n["id"], n["id"].split(":CAPTURE:")[0],
                        "PRESERVED_COPY_NOT_SECOND_OBSERVATION") for n in captures
                       if ":LEGACY-CAPTURE:" not in n["id"]}
    payload_id = "WB-NASA-SSR-19631115:PDF-SHA256:" + upstream.NASA_BYTES_SHA256
    required_edges.add((payload_id, "WB-NASA-SSR-19631115",
                        "SAME_SSR_WORK_NOT_NEW_INSTRUMENT"))
    required_edges |= {(n["id"], payload_id, "SAME_BYTES_NOT_INDEPENDENT_ARCHIVAL_WITNESS")
                       for n in captures if ":LEGACY-CAPTURE:" in n["id"]}
    required_edges |= {(n["id"].split(":REF:")[0], n["id"], "DOCUMENTARY_CONTEXT_ONLY")
                       for n in supp}
    require(len(data["edges"]) == len(required_edges) == 13
            and expected_edges == required_edges
            and all(e[0] in by_id and e[1] in by_id for e in expected_edges),
            "stale/missing graph edge or changed relation")
    return sources, captures, [by_label[label][0] for label in EXPECTED]


def assemble(data: dict, document: dict) -> str:
    sources, captures, matrix = validate(data, document)
    captures_by_source = {c["id"].split(":CAPTURE:")[0]: c for c in captures
                          if ":LEGACY-CAPTURE:" not in c["id"]}
    refs = [n for n in data["nodes"] if n["kind"] == "SUPPLEMENTARY_SOURCE_REF_NOT_MATRIX"]
    edge_names = {
        "NO_EXACT_CAPTURE_IN_QUERIED_INDEX": "exactUrlNotInIndex",
        "DOC_SOURCE_TO_SNAPSHOT_CITATION": "sourceToMatrixCitation",
        "PRESERVED_COPY_NOT_SECOND_OBSERVATION": "archivedCopyOf",
        "DOCUMENTARY_CONTEXT_ONLY": "supplementaryContext",
        "NTRS_CATALOG_OF_SAME_NASA_WORK_NOT_INDEPENDENT": "ntrsCatalogueSameWork",
        "SAME_SSR_WORK_NOT_NEW_INSTRUMENT": "sameOriginalWork",
        "SAME_BYTES_NOT_INDEPENDENT_ARCHIVAL_WITNESS": "identicalPdfBytes",
    }
    edges = ["  { fromId := " + quote(edge["from"]) + ", toId := "
             + quote(edge["to"]) + ", kind := ." + edge_names[edge["kind"]] + " }"
             for edge in data["edges"]]
    extras = ["  { sourceRef := " + quote(n["source_ref"])
              + ", matrixRef := none, activated := false }" for n in refs]
    archive_copies = []
    for n in captures:
        source_id = n["id"].split(":LEGACY-CAPTURE:")[0] if ":LEGACY-CAPTURE:" in n["id"] else n["id"].split(":CAPTURE:")[0]
        archive_copies.append("  { captureId := " + quote(n["id"])
                              + ", sourceId := " + quote(source_id)
                              + ", capturedUtc := " + quote(n["capture_utc"])
                              + ", originalUrl := " + quote(n.get("cdx_original_url", upstream.EXPECTED[source_id][2]))
                              + ", archivedUrl := " + quote(n["archived_url"])
                              + ", pdfSha256 := " + quote(n["retrieved_bytes_sha256"])
                              + ", cdxSha1Base32 := " + quote(n["cdx_digest_base32_sha1"])
                              + " }")
    works = []
    for src in sources:
        captured = captures_by_source.get(src["id"])
        works.append("  { sourceId := " + quote(src["id"])
                     + ", sourceFamily := " + quote(src["source_family"])
                     + ", captureStatus := ." + ("verifiedReplay" if captured else "exactUrlNotInIndex")
                     + ", publicationDate := " + opt(src["publication_date"])
                     + ", originalUrl := " + quote(src["original_url"])
                     + ", archivedUrl := " + opt(captured["archived_url"] if captured else None)
                     + ", capturedUtc := " + opt(captured["capture_utc"] if captured else None)
                     + ", cdxSha1Base32 := " + opt(captured["cdx_digest_base32_sha1"] if captured else None)
                     + ", pdfSha256 := " + opt(captured["retrieved_bytes_sha256"] if captured else None)
                     + " }")
    citations = []
    for c in matrix:
        m = REF.fullmatch(c["snapshot_ref"])
        assert m
        citations.append("  { matrixRef := { snapshot := " + quote(m.group(1))
                         + ", label := " + m.group(2) + ", variant := " + m.group(3) + " }"
                         + ", sourceId := " + quote(c["source_id"])
                         + ", workId := \"NASA_SSR_VOL3_22\""
                         + ", rowSha256 := " + quote(c["row_sha256"])
                         + ", hypothesis := " + quote(c["hypothesis"])
                         + ", simulatorParameter := " + quote(c["simulator_parameter"])
                         + ", eventTimeUtc := none, activated := false }")
    return '''import Conde1963.Documentary

/-!
WB-01: two exact Wayback PDF captures and one exact-URL negative lookup.
Generated from the Abelha crosswalk and Lontra provenance; SHA-256 is for
replayed PDF bytes, CDX Base32 SHA-1 is a distinct digest, capture time is
NOT a 1963 event time. C197#1 and C198#1 refer to one NASA SSR work.
No historical 528 sensor, terminal timestamp, probability or active constraint.
Generated by formal/scripts/compile_wayback_citations.py; do not hand edit.
-/

namespace Conde1963

inductive WaybackCaptureStatus where
  | verifiedReplay
  | exactUrlNotInIndex
  deriving Repr, BEq

inductive WaybackEdgeKind where
  | exactUrlNotInIndex
  | sourceToMatrixCitation
  | archivedCopyOf
  | supplementaryContext
  | ntrsCatalogueSameWork
  | sameOriginalWork
  | identicalPdfBytes
  deriving Repr, BEq

structure WaybackEvidenceEdge where
  fromId : String
  toId : String
  kind : WaybackEdgeKind
  deriving Repr

structure WaybackSourceRef where
  sourceRef : String
  matrixRef : Option MatrixRef
  activated : Bool
  deriving Repr

structure WaybackWork where
  sourceId : String
  sourceFamily : String
  captureStatus : WaybackCaptureStatus
  publicationDate : Option String
  originalUrl : String
  archivedUrl : Option String
  capturedUtc : Option String
  cdxSha1Base32 : Option String
  pdfSha256 : Option String
  deriving Repr

structure WaybackArchiveCopy where
  captureId : String
  sourceId : String
  capturedUtc : String
  originalUrl : String
  archivedUrl : String
  pdfSha256 : String
  cdxSha1Base32 : String
  deriving Repr

structure WaybackDayOnlyCitation where
  matrixRef : MatrixRef
  sourceId : String
  workId : String
  rowSha256 : String
  hypothesis : String
  simulatorParameter : String
  eventTimeUtc : Option String
  activated : Bool
  deriving Repr

-- Preserved copies are not additional sensors.
def waybackWorks : Array WaybackWork := #[
''' + ",\n".join(works) + '''
]

-- These five replay records reduce to three source works. NASA's three
-- older-URL captures share one actual payload (SHA-256), not three sensors.
def waybackArchiveCopies : Array WaybackArchiveCopy := #[
''' + ",\n".join(archive_copies) + '''
]

-- Exactly two frozen citation occurrences for one NASA volume; no event time.
def waybackDayOnlyCitations : Array WaybackDayOnlyCitation := #[
''' + ",\n".join(citations) + '''
]

-- These archival references are NOT Cnn matrix occurrences.
def waybackSupplementaryRefs : Array WaybackSourceRef := #[
''' + ",\n".join(extras) + '''
]

-- Preserve the typed differences among custody, citations and catalogues.
def waybackEvidenceEdges : Array WaybackEvidenceEdge := #[
''' + ",\n".join(edges) + '''
]

end Conde1963
'''



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    opts = parser.add_mutually_exclusive_group(required=True)
    opts.add_argument("--check", action="store_true")
    opts.add_argument("--write", action="store_true")
    mode = parser.parse_args()
    source_bytes = SOURCE.read_bytes()
    data = json.loads(source_bytes)
    require(source_bytes == upstream.encode(upstream.build()), "upstream export is stale")
    document = json.loads(DEPENDENCE.read_bytes())
    lean = assemble(data, document)
    require(len(lean.encode("utf-8")) < 20_000, "Lean output exceeds 20K")
    if mode.check:
        require(TARGET.read_text(encoding="utf-8") == lean, "generated Lean is stale")
    else:
        TARGET.write_text(lean, encoding="utf-8")
    print("WAYBACK_LEAN", len(lean.encode("utf-8")), "bytes", "3 works", "2 citations")


if __name__ == "__main__":
    main()
