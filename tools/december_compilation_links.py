#!/usr/bin/env python3
"""Source-locked December NASA SSR -> latent *printed* quantities.

The frozen C227 row mistakenly transcribed 89.6 min; the independently
rechecked facsimile in C241-L18 says 89.2. NTRS metadata (C228) and
the NASA table are ONE work, not two independent sensors.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import provenance_graph as pg

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = "public/data/conde-ssr-december-bridge.json"
NASA = "C241-L18:19640005618"
CATALOGUE = "NTRS:19640005618"
PINNED_PDF = "d9504a8641baa65c208e41034e77b0e9b1cc01b4acb2a4f95541bd9e75d3783d"


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("December compilation links: " + reason)


def build(bridge: dict, matrix_rows: list[dict]) -> list[dict]:
    by_occ = {r["occurrence"]: r for r in matrix_rows}
    require(len(by_occ) == 241 and all(x in by_occ for x in ("C227#1", "C228#1")),
            "frozen matrix occurrence inventory changed")
    # Independent witness: matrix row and later facsimile-corrected ledger.
    c227 = by_occ["C227#1"]
    c228 = by_occ["C228#1"]
    require(c227["snapshot_ref"] == pg.matrix_ref("C227#1")
            and c228["snapshot_ref"] == pg.matrix_ref("C228#1")
            and c227["row_sha256"] != c228["row_sha256"], "matrix crosswalk drift")
    require(bridge.get("schema") == "conde.ssr-december-source-bridge/v1"
            and bridge.get("id") == "C241-L18-NOV-DEC-529-ERRATUM"
            and bridge.get("source_family") ==
                "NASA_GODDARD_NORAD_SMITHSONIAN_COMPILED_REPORTS"
            and bridge.get("erratum_matrix_occurrence") == "C227#1"
            and bridge.get("erratum_superseded_printed_min") == "89.6"
            and bridge.get("erratum_verified_printed_min") == "89.2"
            and bridge.get("erratum_state") ==
                "RESOLVED_AS_TRANSCRIPTION_ERRATUM_NOT_INSTRUMENT_VALIDATION"
            and bridge.get("source_editions", [{}])[-1].get("ntrs") == "19640005618"
            and bridge["source_editions"][-1].get("occurrence_id") == NASA
            and bridge["source_editions"][-1].get("pdf_sha256") == PINNED_PDF
            and bridge["source_editions"][-1].get("matrix_context_not_independent_sensor")
                == ["C227#1"], "NASA/NTRS identity or corrected 529 cell drift")
    require(bridge.get("same_institutional_family_not_independent_sensors") is True
            and bridge.get("source_to_instrument_mapping_verified") is False
            and bridge.get("sensor_epochs_utc") is None
            and bridge.get("sensor_covariance") is None
            and bridge.get("active_physical_constraint") is False
            and bridge.get("physical_domain_effect") == "THETA_UNCHANGED"
            and bridge.get("status") == "CONNECTED_PENDING_CALIBRATION"
            and bridge.get("conditional_529_delta_range_min") == ["2.90", "3.10"]
            and bridge.get("conditional_differential_range_min") == ["2.80", "3.20"]
            and bridge.get("lean_theorem") == "post_b_529_reconciled_printed_gap_over_527",
            "source mistakenly promoted to instrument or physics")
    source = bridge["source_editions"][-1]
    require(source["report_published_on"] == "1963-12-31"
            and source["report_as_of_utc_not_sensor_epoch"] == "1963-12-31T12:00:00Z"
            and source["pdf_page_index"] == 6
            and source["printed_page"] == 5
            and source["pdf_bytes"] == 992569
            and source["url"] == "https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf",
            "compilation cutoff, publication or page is not an instrument epoch")
    require(bridge.get("control_529_printed_periods_min") == ["92.2", "89.2"]
            and bridge.get("control_527_printed_periods_min") == ["94.6", "94.6"]
            and bridge.get("control_529_printed_delta_min") == "3.0"
            and bridge.get("conditional_rounding_model") ==
                "nearest_0.1_min_not_instrument_sigma",
            "printed periods or quantization not as independently checked")
    def edge(source_id: str, target: str, relation: str,
             occ: dict, printed: str | None) -> dict:
        return {
            "source": source_id, "target": target, "relation": relation,
            "matrix_occurrence": occ["snapshot_ref"], "matrix_line": occ["matrix_line"],
            "matrix_row_sha256": occ["row_sha256"],
            "same_work_id": "NASA_SSR_VOL3_25_19631231",
            "source_pdf_sha256": PINNED_PDF, "source_pdf_page_index": 6,
            "compiled_report_as_of_utc_not_sensor_epoch": "1963-12-31T12:00:00Z",
            "printed_period_min_not_instrument_observation": printed,
            "instrument_epoch_utc": None, "instrument_covariance": None,
            "independent_sensor": False, "activation": False,
            "physical_domain_effect": "THETA_UNCHANGED",
            "status": "CONNECTED_PENDING_CALIBRATION",
        }
    return [
        edge(NASA, "latent_529_compiled_nodal_period_19631231_min",
             "REPORTS_PRINTED_CELL_WITH_C227_ERRATUM", c227, "89.2"),
        edge(NASA, "latent_527_compiled_nodal_period_19631231_min",
             "CONTROL_PRINTED_CELL_SAME_REPORT", c227, "94.6"),
        edge(CATALOGUE, NASA, "CATALOGUE_OF_SAME_WORK_NOT_SECOND_SENSOR",
             c228, None),
    ]
