#!/usr/bin/env python3
"""C241-L17: three NASA publications, never three instrumental epochs."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

try:
    from tools.tle_nasa_ssr_apr_oct_audit import validate as validate_apr_oct
except ModuleNotFoundError:
    from tle_nasa_ssr_apr_oct_audit import validate as validate_apr_oct

PIN = ("4e5cb0205577bc1b0959088db9ca3ae7a05f8de480b5ece9b86c385437636968", 252639)
SOURCE = ("19630012289", "1963-08-15", 3, 16, "X-533-63-1",
          "NASA-TM-X-50364", 6, 7, 5, "1200Z AUG 15 1963")
EXPECTED = [
    ("1963-003A", "1963 3A", "94.6", "81.88", 537, 458),
    ("1963-003B", "1963 3B", "93.3", "81.87", 455, 412),
    ("1963-003C", "1963 3C", "93.8", "81.89", 493, 422),
]
UNKNOWN = ("physical_frame", "measurement_sigma", "observing_station",
           "original_tle_pair", "raan_deg", "material_identity_528",
           "terminal_time", "terminal_location")


def validate(august, april, october):
    if august["id"] != "C241-L17":
        raise ValueError("wrong occurrence ID")
    s = august["source"]
    identity = (s["ntrs_id"], s["publication"], s["volume"], s["number"],
                s["printed_report_number"], s["nasa_tm"],
                s["pdf_page_index_zero_based"], s["pdf_page_one_based"],
                s["printed_page"], s["data_as_of"])
    if identity != SOURCE:
        raise ValueError("unverified August report identity/page")
    if (s["citation_url"], s["pdf_url"], s["sha256"], s["bytes"]) != (
            "https://ntrs.nasa.gov/citations/19630012289",
            "https://ntrs.nasa.gov/api/citations/19630012289/downloads/19630012289.pdf",
            *PIN):
        raise ValueError("unverified August file provenance")
    if s["ntrs_metadata_title"] != "Saatellite Situation Report":
        raise ValueError("do not silently correct original metadata typo")
    if s["inspection"] != "VISUAL_FACSIMILE_PDF_PAGE_7_ON_2026-11-13":
        raise ValueError("visual inspection provenance changed")
    links = august["dependencies"]
    if links != {
            "april": "research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json",
            "october": "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json",
            "object_id_crosswalk": "C241-L10", "november_decay_day": "C241-L11"}:
        raise ValueError("incorrect dependencies")
    lim = august["limits"]
    if (lim["source_class"] != "PRIMARY_CONTEMPORARY_DOCUMENT_NOT_INSTRUMENTAL_TLE"
            or lim["same_institutional_compilation"] is not True
            or lim["independent_sensor_observation"] is not False
            or lim["publication_date_is_element_epoch"] is not False
            or lim["rate_from_publication_interval"] is not False
            or lim["issue_21"] != "NOT_RECOVERED"
            or lim["graph"] != "CONNECTED_PENDING_CALIBRATION"
            or lim["lean"] != "NOT_PROMOTED"
            or lim["conde"] != "INDETERMINATE"):
        raise ValueError("unjustified scientific claim")
    if any(lim[key] is not None for key in UNKNOWN):
        raise ValueError("invented historical sensor/frame/TLE/terminal metadata")
    april_october = validate_apr_oct(april, october)
    if len(august["rows"]) != 3 or len(april_october) != 3:
        raise ValueError("expected exactly three historical objects")
    output = []
    for row, early, late, exp in zip(
            august["rows"], april["april_rows"], october["catalog_rows"], EXPECTED):
        got = (row["designator"], row["printed"], row["nodal_period_min"],
               row["inclination_deg"], row["apogee_km"], row["perigee_km"])
        if got != exp or row["source"] != "US" or row["launch"] != "1963-01-16":
            raise ValueError("August visual transcription mismatch")
        if (early["designator"] != row["designator"]
                or late["international_designator"] != row["designator"]):
            raise ValueError("cross-edition designator mismatch")
        if any(type(row[k]) is not int for k in ("apogee_km", "perigee_km")):
            raise ValueError("printed altitude must be integer km")
        if not 0 < row["perigee_km"] <= row["apogee_km"]:
            raise ValueError("invalid altitude")
        a = Decimal(early["nodal_period_min"])
        b = Decimal(row["nodal_period_min"])
        c = Decimal(late["nodal_period_min_printed"])
        output.append({
            "designator": row["designator"],
            "publication_dates_not_element_epochs": [
                april["april"]["publication"], s["publication"],
                october["source"]["publication_date"]],
            "printed_period_min": [str(a), str(b), str(c)],
            "publication_step_delta_min_not_physical_rate": [str(b - a), str(c - b)],
            "printed_apogee_km": [early["apogee_km"], row["apogee_km"],
                                  late["apogee_km_printed"]],
            "printed_perigee_km": [early["perigee_km"], row["perigee_km"],
                                   late["perigee_km_printed"]],
            "epoch_of_elements": None,
            "independent_sensor_observation": False
        })
    return output


def audit(august, april, october, pdf):
    rows = validate(august, april, october)
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("not a PDF file")
    if (hashlib.sha256(pdf).hexdigest(), len(pdf)) != PIN:
        raise ValueError("NASA PDF bytes/hash mismatch")
    return {"record_id": "C241-L17", "rows": rows, "august_pdf_sha256": PIN[0],
            "august_pdf_bytes": PIN[1], "pdf_pixels_verified_in_CI": False,
            "instrumental_tle_found": False, "physical_domain_reduced": False,
            "conde_outcome": "INDETERMINATE"}


def main():
    p = argparse.ArgumentParser()
    for name in ("august", "april", "october", "pdf", "output"):
        p.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args()
    result = audit(*[
        json.loads(getattr(a, key).read_text(encoding="utf8"))
        for key in ("august", "april", "october")
    ], a.pdf.read_bytes())
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("C241-L17: August primary documentary rows verified; original TLE NOT_FOUND")


if __name__ == "__main__":
    main()
