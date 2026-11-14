#!/usr/bin/env python3
"""C241-L59: preserve SAO P-14 timing conventions without inventing NORAD 528 data."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/sao_p14_a1_clock_1963_C241-L59.json"
URL = "https://ntrs.nasa.gov/api/citations/19660001360/downloads/19660001360.pdf"
SHA = "d7140f9b78991d1bb75857ba6a109fb553b80eab16f7dd89c41cc799d9e53980"
BYTES = 6173834
SATELLITES = (
    "Vanguard 2", "Vanguard 3", "Echo 1 Rocket Body", "Explorer 9",
    "Transit 4A", "Injun", "Midas 4", "Telstar 1", "A15 Relay"
)
COUNTS = (545, 276, 960, 1230, 212, 166, 775, 601, 375)


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate(m: dict) -> dict:
    s = m["source"]
    scope = m["observations_scope"]
    meth = m["measurement_method_context_only"]
    w = meth["a1_minus_wwv_seconds"]
    t = m["target_527_528_529"]
    require(m["id"] == "C241-L59" and m["type"] == "HISTORICAL_OPTICAL_TIME_REFERENCE_SCOPE", "wrong ledger type")
    require(s["ntrs_id"] == "19660001360" and s["pdf_url"] == URL, "source id/url mismatch")
    require(s["pdf_bytes"] == BYTES and s["pdf_sha256"] == SHA and s["pdf_pages"] == 128, "source bytes unverified")
    require(s["publication_date"] == "1965-09-03", "publication date drift")
    require(s["pages_zero_based"] == {
        "cover": 0, "table_of_contents": 2, "intro_printed_1": 3,
        "clock_printed_2": 4, "frame_printed_3": 5
    }, "page mapping changed")
    require(tuple(scope["listed_targets"]) == SATELLITES, "printed satellites changed")
    require(tuple(scope["selected_counts"]) == COUNTS, "printed counts changed")
    require(sum(COUNTS) == 5140, "count total is incorrect")
    require(scope["primary_calendar_window"] == ["1963-01-01", "1963-03-31"], "scope widened")
    require(scope["one_series_starts"] == "1962-12-16", "Relay series start changed")
    require(scope["norad_527_528_529_in_list"] is False, "invented listed object")
    require(scope["scope_interpretation"] == "ABSENT_FROM_NAMED_PUBLISHED_SERIES_NOT_ABSENT_FROM_HISTORICAL_SENSORS",
            "negative evidence overclaimed")
    require(meth["time_scale"] == "SMOOTHED_PRELIMINARY_A1_NOT_UTC", "A1 substituted for UTC")
    require(meth["time_emission_reference"] == "WWV_EMITTED", "WWV not authenticated")
    require(w == {
        "mjd_lower_inclusive": 38030.0,
        "mjd_upper_exclusive": 38334.0,
        "reference_mjd": 38030.0,
        "intercept_seconds": 2.292725,
        "slope_seconds_per_day": 0.001118458
    }, "time formula changed")
    require(meth["time_uncertainty_milliseconds_range"] == [0.5, 20.0], "time uncertainty changed")
    require(meth["typical_time_uncertainty_milliseconds"] == 2.0, "typical time uncertainty changed")
    require(meth["assigned_angular_standard_error_arcsec"] == 4.0, "angular context sigma changed")
    require(meth["angular_reference"] == "TOPOCENTRIC_RA_DEC_MEAN_EQUATOR_EQUINOX_1950_NOT_UNIFORM_STAR_CATALOG",
            "angular frame misidentified")
    require(meth["refraction"] == "PARALLACTIC_REFRACTION_NOT_CORRECTED", "refraction changed")
    require(meth["station_geodetic_reference"] == "KAULA_ELLIPSOID_1964", "station datum changed")
    require(len(meth["catalog_rows_include"]) == 8, "catalog fields changed")
    for field in ("raw_observations", "instrumental_epoch_utc", "station", "measurement_error_model", "covariance", "reentry_location"):
        require(t[field] is None, f"target field fabricated: {field}")
    require(t["independent_instrumental_measurements_added"] == 0, "invented target sensor")
    require(t["physical_constraints_activated"] == 0, "premature constraint")
    require(len(m["scientific_policy"]) == 4, "lost scientific caveats")
    return {"id": m["id"], "status": "CONTEXT_ONLY", "listed_satellites": len(SATELLITES),
            "selected_observation_rows": sum(COUNTS), "target_observations": 0, "constraints": 0}


def a1_minus_wwv_seconds(m: dict, mjd: float) -> float:
    """Source's A.1 minus WWV emitted, seconds. NOT an A.1 to UTC conversion."""
    validate(m)
    if isinstance(mjd, bool) or not isinstance(mjd, (int, float)) or not math.isfinite(mjd):
        raise ValueError("MJD must be finite numeric")
    w = m["measurement_method_context_only"]["a1_minus_wwv_seconds"]
    if not (w["mjd_lower_inclusive"] <= mjd < w["mjd_upper_exclusive"]):
        raise ValueError("P-14 clock formula outside 1963-01-01..1963-10-31")
    return w["intercept_seconds"] + w["slope_seconds_per_day"] * (mjd - w["reference_mjd"])


def inspect_pdf(raw: bytes) -> dict:
    """Fail closed on byte identity and the exact facsimile pages (pypdf only here)."""
    require(len(raw) == BYTES and hashlib.sha256(raw).hexdigest() == SHA,
            "source bytes drifted: investigate; never silently replace hash")
    from pypdf import PdfReader

    pdf = PdfReader(io.BytesIO(raw))
    require(len(pdf.pages) == 128, "source pagination changed")
    cover, toc, intro, clock, frame = (
        (pdf.pages[i].extract_text() or "") for i in (0, 2, 3, 4, 5)
    )
    require("P-14" in cover and "September 3" in cover, "wrong cover")
    require(toc.count("Observations of Satellite") == 9, "toc series not nine")
    for name in SATELLITES:
        require(name in toc, f"missing listed target {name}")
    for n in (545, 276, 960, 1230, 212, 166, 775, 601, 375):
        require(f"{n} observa" in intro, f"count missing {n}")
    for token in ("2.292 725", "0.001 118 458", "38,030.0", "A.1"):
        require(token in clock, f"clock source drifted: {token}")
    for token in ("equinox of 1950.0", "parallactic refraction", "Kaula"):
        require(token in frame, f"frame source drifted: {token}")
    require("1963 03B" not in toc and "1963 003B" not in toc, "target unexpectedly in TOC")
    return {"pdf_bytes": len(raw), "sha256": SHA, "pages": len(pdf.pages),
            "scanned_pages": [0, 2, 3, 4, 5], "scope": "9 SELECTED OBJECTS; NOT NORAD 528"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path, help="path to original PDF for strict byte + 5-page replay")
    args = p.parse_args()
    output = validate(load())
    output["sample_a1_minus_wwv_seconds_at_mjd_38030"] = a1_minus_wwv_seconds(load(), 38030.0)
    if args.pdf:
        output["source_replay"] = inspect_pdf(args.pdf.read_bytes())
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
