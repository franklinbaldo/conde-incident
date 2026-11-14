#!/usr/bin/env python3
"""C241-P42: pinned CIA FBIS operational source -> three documentary dependencies.

The May 1972 retrospective concerns institutional monitoring, not an
instrumental observation of the Conde event.  Never infer that Panama copied
Tupi, that TEXT verifies a witness, or that an absent Daily Report was silence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public/data/conde-fbis-operational-lineage.json"
SOURCE_URL = ("https://www.govinfo.gov/content/pkg/GOVPUB-PREX3-PURL-gpo254964/"
              "pdf/GOVPUB-PREX3-PURL-gpo254964.pdf")
SOURCE_ID = "CIA-RDP05-01429R000100010001-0"
SOURCE_PDF_SHA256 = "77e3dcb65844a1c2965ba4649bb1b1a35e4e67a6c15d7ac38c6579b50c299f86"
SOURCE_PDF_SIZE = 8_533_908
# (occurrence, frozen row SHA-256, original printed page, PDF zero-based index,
#  documentary variable, what remains unverified).
CLAIMS = (
    ("C212#1", "3caae1476507e1fe41a5dc0f3e38f0e9c03c6fe353dc208d816ee848338c4997",
     54, 55, "fbis_brazil_spoken_radio_monitoring_capacity",
     "No 1963 Tupi reception station, date/time or raw audio located"),
    ("C213#1", "62e676593522977bda733aa3b16ecfda11b6c1267d025c28472211ccfb47cde2",
     69, 70, "fbis_panama_1963_country_coverage",
     "Seventeen countries not enumerated; Brazil and Tupi attribution unproven"),
    ("C214#1", "93b2603a1457f2e344b9f186a45f1ea46d4e70638db1c522fe441f29e086218c",
     5, 6, "fbis_1964_daily_report_editorial_selection",
     "1964 selection rate cannot be assigned to individual 1963 broadcasts"),
)
PAGES = {"C212#1": 54, "C213#1": 69, "C214#1": 5}


def require(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError("FBIS source graph: " + why)


def build(root: Path = ROOT) -> dict:
    raw = (root / pg.MATRIX.relative_to(ROOT)).read_bytes()
    rows = pg.matrix_occurrences(raw)
    by_occ = {r["occurrence"]: r for r in rows}
    require(len(rows) == len(by_occ) == 241, "frozen occurrence cardinality")
    require(pg.MATRIX_BLOB_SHA == "a7978c3a75a153b16ab70118a92c434bba674cb7",
            "unexpected matrix revision")
    edges = []
    for occ, row_sha, page, pdf_index, variable, blocker in CLAIMS:
        r = by_occ[occ]
        require(r["row_sha256"] == row_sha
                and r["matrix_blob_sha1"] == pg.MATRIX_BLOB_SHA,
                "source occurrence drift: " + occ)
        require(r["matrix_line"] == {"C212#1": 948, "C213#1": 949,
                                    "C214#1": 950}[occ],
                "frozen line changed: " + occ)
        if occ == "C212#1":
            require(SOURCE_ID in r["claim_text"] and SOURCE_URL in r["claim_text"]
                    and "maio de 1972" in r["claim_text"], "source link drift")
        else:
            require(str(page) in r["claim_text"] and "C212" in r["claim_text"],
                    "same-document reference absent: " + occ)
        edges.append({
            "matrix_occurrence": r["snapshot_ref"],
            "matrix_line": r["matrix_line"],
            "matrix_row_sha256": row_sha,
            "source_work_id": SOURCE_ID,
            "printed_page": page,
            "pdf_zero_based_index": pdf_index,
            "documentary_variable_id": variable,
            "dependency_type": "INSTITUTIONAL_OPERATIONAL_HISTORY",
            "status": "CONNECTED_PENDING_ATTRIBUTION",
            "unknown_needed_for_attribution": blocker,
            "instrument_epoch_utc": None,
            "independent_instrument_1963": False,
            "tupi_reception_log": None,
            "station_attributed_to_tupi": None,
            "active_physical_constraint": False,
            "activation": False,
            "physical_domain_effect": "THETA_UNCHANGED",
        })
    data = {
        "schema": "conde.fbis-operational-lineage/v1",
        "id": "C241-P42-FBIS-1972-C212-C214",
        "matrix_git_blob_sha1": pg.MATRIX_BLOB_SHA,
        "source": {
            "work_id": SOURCE_ID,
            "url": SOURCE_URL,
            "author": "CIA Historical Staff",
            "title": "Foreign Broadcast Information Service History, Part III: 1957-1967",
            "publication_date": "1972-05",
            "declassification_release_date": "2012-11-01",
            "source_class": "RETROSPECTIVE_PRIMARY_INSTITUTIONAL_HISTORY",
            "source_pdf_sha256": SOURCE_PDF_SHA256,
            "source_pdf_size_bytes": SOURCE_PDF_SIZE,
            "raw_pdf_bytes_replayed_this_run": False,
            "pages_visually_reinspected": [5, 54, 69],
            "source_count": 1,
        },
        "edges": edges,
        "epistemic_limits": {
            "one_CIA_work_not_three_independent_sensors": True,
            "retrospective_1972_not_1963_measurement": True,
            "panama_did_not_prove_tupi_interception": True,
            "1964_editorial_fraction_not_1963_event_probability": True,
            "negative_archive_search_not_negative_historical_event": True,
            "no_1963_tupi_original_audio": True,
            "new_instrumental_observations": 0,
            "new_528_tracking_observations": 0,
            "physical_domain_effect": "THETA_UNCHANGED",
        },
        "counts": {
            "source_works": 1, "frozen_occurrences_linked": 3,
            "documentary_variables": 3, "independent_instrumental_sources": 0,
            "active_orbital_constraints": 0,
        },
    }
    audit(data, rows)
    return data


def audit(data: dict, rows: list[dict]) -> None:
    require(data.get("schema") == "conde.fbis-operational-lineage/v1"
            and data.get("matrix_git_blob_sha1") == pg.MATRIX_BLOB_SHA, "wrong snapshot/schema")
    s = data.get("source", {})
    require(s.get("work_id") == SOURCE_ID and s.get("url") == SOURCE_URL
            and s.get("publication_date") == "1972-05"
            and s.get("source_class") == "RETROSPECTIVE_PRIMARY_INSTITUTIONAL_HISTORY"
            and s.get("source_pdf_sha256") == SOURCE_PDF_SHA256
            and s.get("source_pdf_size_bytes") == SOURCE_PDF_SIZE
            and s.get("raw_pdf_bytes_replayed_this_run") is False
            and s.get("source_count") == 1, "invalid source identity or replay claim")
    by_ref = {r["snapshot_ref"]: r for r in rows}
    edges = data.get("edges", [])
    require(len(edges) == len(CLAIMS), "edge count changed")
    for e, (occ, sha, page, index, variable, blocker) in zip(edges, CLAIMS):
        require(e.get("matrix_occurrence") == pg.matrix_ref(occ)
                and e["matrix_occurrence"] in by_ref
                and e.get("matrix_row_sha256") == sha
                and by_ref[e["matrix_occurrence"]]["row_sha256"] == sha
                and e.get("matrix_line") == by_ref[e["matrix_occurrence"]]["matrix_line"],
                "unqualified/mismatched occurrence: " + occ)
        require(e.get("source_work_id") == SOURCE_ID
                and e.get("printed_page") == page
                and e.get("pdf_zero_based_index") == index
                and e.get("documentary_variable_id") == variable
                and e.get("unknown_needed_for_attribution") == blocker
                and e.get("status") == "CONNECTED_PENDING_ATTRIBUTION",
                "documentary meaning or locator changed: " + occ)
        require(e.get("activation") is False
                and e.get("active_physical_constraint") is False
                and e.get("independent_instrument_1963") is False
                and e.get("instrument_epoch_utc") is None
                and e.get("tupi_reception_log") is None
                and e.get("station_attributed_to_tupi") is None
                and e.get("physical_domain_effect") == "THETA_UNCHANGED",
                "retrospective source promoted to historical measurement: " + occ)
    limits = data.get("epistemic_limits", {})
    require(all(limits.get(k) is True for k in (
        "one_CIA_work_not_three_independent_sensors",
        "retrospective_1972_not_1963_measurement",
        "panama_did_not_prove_tupi_interception",
        "1964_editorial_fraction_not_1963_event_probability",
        "negative_archive_search_not_negative_historical_event",
        "no_1963_tupi_original_audio")), "epistemic limit weakened")
    require(limits.get("new_instrumental_observations") == 0
            and limits.get("new_528_tracking_observations") == 0
            and limits.get("physical_domain_effect") == "THETA_UNCHANGED"
            and data.get("counts") == {
                "source_works": 1, "frozen_occurrences_linked": 3,
                "documentary_variables": 3, "independent_instrumental_sources": 0,
                "active_orbital_constraints": 0,
            }, "false scientific activation or counting")


def verify_source_pdf(path: Path) -> None:
    """Replay the original public PDF bytes; no PDF bytes enter git or the feed.

    The digest proves byte identity only. It does not make the 1972 document
    a 1963 instrumental observation or establish Tupi/Panama attribution.
    """
    require(path.is_file(), "source PDF file missing")
    require(path.stat().st_size == SOURCE_PDF_SIZE, "source PDF byte length mismatch")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        require(stream.read(8).startswith(b"%PDF-"), "source PDF header invalid")
        stream.seek(-128, 2)
        require(b"%%EOF" in stream.read(), "source PDF EOF marker absent")
        stream.seek(0)
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    require(digest.hexdigest() == SOURCE_PDF_SHA256, "source PDF digest mismatch")


def encoded(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--write-site", action="store_true")
    action.add_argument("--check-site", action="store_true")
    ap.add_argument("--source-pdf", type=Path, help="replay pinned CIA PDF bytes locally")
    args = ap.parse_args()
    if args.source_pdf is not None:
        verify_source_pdf(args.source_pdf)
    output = encoded(build())
    require(len(output) < 20_000, "file exceeds normative 20KB")
    if args.write_site:
        OUTPUT.write_bytes(output)
    else:
        require(OUTPUT.is_file() and OUTPUT.read_bytes() == output, "site feed stale")
    print("FBIS_OPERATIONAL_LINEAGE_OK", len(CLAIMS), len(output))


if __name__ == "__main__":
    main()
