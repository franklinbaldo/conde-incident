#!/usr/bin/env python3
"""Source-locked two-body dimensional screen of NASA 1963 SSR printed cells.

This is an adversarial comparison of published fields, NOT an orbit determination.
A large discrepancy can reflect non-coeval elements, their convention, or an
editorial error.  Report reference time is not an instrumental measurement epoch.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
OUTPUT = ROOT / "research/constraints/CASTOR-G37_ssr_crossfield_screen.json"
MU = 398600.4418  # km^3/s^2, conventional Earth GM
RADIUS = 6378.137  # km, conventional equatorial radius
PDF_LOCKS = {
    "19630012290": "9b00bf8323b1de80a34920f73c658f70f766a51632a13473a408679f0e5a03d9",
    "19640002493": "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d",
    "19640005618": "d9504a8641baa65c208e41034e77b0e9b1cc01b4acb2a4f95541bd9e75d3783d",
}
DESIGNATORS = {"1963-003A", "1963-003B", "1963-003C"}


def period_min(mean_altitude_km: float) -> float:
    a = RADIUS + mean_altitude_km
    if not (math.isfinite(a) and a > RADIUS):
        raise ValueError("invalid positive orbital altitude")
    return 2 * math.pi * math.sqrt(a ** 3 / MU) / 60


def build(ledger: dict) -> dict:
    if ledger.get("id") != "C241-L18":
        raise ValueError("unexpected NASA ledger identity")
    sources = ledger.get("sources")
    if not isinstance(sources, list) or len(sources) != len(PDF_LOCKS):
        raise ValueError("expected three source editions")
    cells: list[dict] = []
    keys: set[tuple[str, str]] = set()
    for source in sources:
        ntrs = source.get("ntrs_id")
        if ntrs not in PDF_LOCKS or source.get("sha256") != PDF_LOCKS[ntrs]:
            raise ValueError("source hash or NTRS identity changed")
        if not re.fullmatch(r"1963-\d\d-\d\d", source.get("published", "")):
            raise ValueError("publication date missing")
        if source.get("pdf_page_index") != 6 or source.get("printed_page") != 5:
            raise ValueError("source page anchor changed")
        rows = source.get("rows")
        if not isinstance(rows, list) or not rows:
            raise ValueError("source rows missing")
        for row in rows:
            des = row.get("designator")
            key = (ntrs, des)
            if des not in DESIGNATORS or key in keys:
                raise ValueError("duplicate or unknown designator")
            keys.add(key)
            apo = row.get("apogee_km")
            peri = row.get("perigee_km")
            printed = row.get("period_min")
            if (type(apo) is not int or type(peri) is not int or
                not (0 < peri <= apo) or not isinstance(printed, str) or
                not re.fullmatch(r"\d{2,3}\.\d", printed)):
                raise ValueError("unexpected printed precision or altitude")
            period = float(printed)
            if not (80 < period < 200):
                raise ValueError("unexpected printed period")
            mean_alt = (apo + peri) / 2
            predicted = period_min(mean_alt)
            difference_sec = 60 * (period - predicted)
            # Printed half-unit quantization. This is NOT an uncertainty model.
            bounds_sec = [
                60 * ((period - 0.05) - period_min(mean_alt + 0.5)),
                60 * ((period + 0.05) - period_min(mean_alt - 0.5)),
            ]
            if bounds_sec[0] > bounds_sec[1]:
                raise ValueError("wrong interval ordering")
            min_abs = 0 if bounds_sec[0] <= 0 <= bounds_sec[1] else min(map(abs, bounds_sec))
            cells.append({
                "id": f"C241-L18:{ntrs}:{des}",
                "object": des,
                "source_ntrs": ntrs,
                "pdf_sha256": PDF_LOCKS[ntrs],
                "pdf_page_index": 6,
                "publication_date_NOT_sensor_epoch": source["published"],
                "printed_period_min": period,
                "printed_apogee_km": apo,
                "printed_perigee_km": peri,
                "two_body_same_epoch_HYPOTHESIS_period_min": round(predicted, 9),
                "printed_minus_two_body_seconds": round(difference_sec, 6),
                "printing_only_bounds_seconds_NOT_sigma": [round(v, 6) for v in bounds_sec],
                "large_offset_over_30s_SCREEN_ONLY": min_abs > 30,
                "sensor_epoch_utc": None,
                "instrumental_sigma": None,
                "calibrated_orbit_constraint": False,
            })
    if len(cells) != 7:
        raise ValueError("missing compiled NASA row")
    selected = [c for c in cells if c["source_ntrs"] == "19640005618"]
    a = next(c for c in selected if c["object"] == "1963-003A")
    c = next(c for c in selected if c["object"] == "1963-003C")
    if ((a["printed_period_min"], a["printed_apogee_km"], a["printed_perigee_km"]) !=
        (94.6, 530, 461) or
        (c["printed_period_min"], c["printed_apogee_km"], c["printed_perigee_km"]) !=
        (89.2, 335, 333)):
        raise ValueError("NASA Dec 31 page cells changed")
    return {
        "schema": "conde.ssr-crossfield-conditional-screen/v1",
        "id": "CASTOR-G37-DEC31-SSR-CROSSFIELD",
        "epistemic_status": "COMPUTATIONAL_CONDITIONAL_SCREEN_NOT_HISTORICAL_OBSERVATION",
        "sources": [{
            "ntrs": s["ntrs_id"], "pdf_sha256": PDF_LOCKS[s["ntrs_id"]],
            "pdf_url": s["pdf_url"], "pdf_page_index": 6,
            "published_NOT_observed": s["published"],
        } for s in sources],
        "source_ledger": "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json",
        "physical_model": "T=2*pi*sqrt((R+(apogee+perigee)/2)^3/mu); two-body, coincident osculating elements ASSUMED for this screening check only",
        "constants": {"earth_mu_km3_s2": MU, "earth_radius_km": RADIUS},
        "printing_precision_only": {"period_min_plusminus": 0.05, "altitude_km_plusminus": 0.5},
        "cells": cells,
        "dec31_529_vs_527_printed_diagnostic": {
            "object_529": c["id"], "object_527": a["id"],
            "529_printed_minus_model_seconds": c["printed_minus_two_body_seconds"],
            "527_printed_minus_model_seconds": a["printed_minus_two_body_seconds"],
            "529_printing_only_interval_seconds": c["printing_only_bounds_seconds_NOT_sigma"],
            "529_large_offset_flag": c["large_offset_over_30s_SCREEN_ONLY"],
            "facsimile_529_period_min": 89.2,
            "prior_C227_transcription_min": 89.6,
            "erratum_origin": "C241-L18 visual facsimile recheck; 89.6 was a transcription error",
        },
        "scientific_interpretation": {
            "large_crossfield_residual_proves_nasa_wrong": False,
            "same_sensor_epoch_and_element_convention_established": False,
            "candidate_explanations_not_discriminated": [
                "mixed instrument epochs or update latencies within compiled columns",
                "nodal versus osculating period convention or elements",
                "other compiled-field inconsistency",
            ],
            "fit_directly_to_1963_trajectory": False,
            "recorded_original_instrument_observations": 0,
            "historical_holdout": "NOT_RUN",
            "active_domain_reduction": False,
            "impact_on_conde": "NOT_DETERMINED",
            "required_next_evidence": [
                "original observed UTC epochs per field",
                "orbit-element and period conventions",
                "instrument calibration and source genealogy",
                "uncertainty/covariance and independent station data",
            ],
        },
    }


def render(ledger: dict) -> str:
    return json.dumps(build(ledger), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = ap.parse_args()
    content = render(json.loads(SOURCE.read_text(encoding="utf-8")))
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
    elif OUTPUT.read_text(encoding="utf-8") != content:
        raise SystemExit("G37 diagnostic drift")
    print("G37: seven SSR source cells audited; no instrumental holdout activated")


if __name__ == "__main__":
    main()
