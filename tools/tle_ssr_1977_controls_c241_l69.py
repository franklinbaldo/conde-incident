#!/usr/bin/env python3
"""C241-L69: NASA 1977 retrospective crosswalk of 292/565, not timed decay data."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/nasa_ssr_1977_controls_292_565_C241-L69.json"
SOURCE = json.loads("{\"ntrs_id\":\"19780009188\",\"title\":\"NASA Goddard Satellite Situation Report, Volume 17, Number 6\",\"report_number\":\"NASA-TM-79345\",\"publication_date\":\"1977-12-31\",\"url\":\"https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf\",\"sha256\":\"c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8\",\"bytes\":11563410,\"pages\":115,\"publication_kind\":\"ORIGINAL_NASA_1977_RETROSPECTIVE_CATALOG\",\"already_custodied_in\":\"C241-L32\",\"new_independent_tracking_source\":false}")
ROWS = json.loads("[{\"norad_id\":292,\"source_printed_designation\":\"SIGMA 1\",\"publication_1963_designation\":\"1962 SIGMA 1\",\"catalogue_era\":\"1962 LAUNCHES\",\"launch_printed\":\"15 MAY\",\"decay_printed\":\"26 NOV 63\",\"published_date\":\"1963-11-26\",\"pdf_page_index_zero_based\":45,\"pdf_page_number_one_based\":46,\"printed_page\":\"-42-\",\"catalog_number_and_name_same_row\":true,\"terminal_utc\":null,\"sensor\":null,\"station\":null,\"covariance\":null,\"temporal_sigma_seconds\":null},{\"norad_id\":565,\"source_printed_designation\":\"1963 009B\",\"publication_1963_designation\":\"1963 9B\",\"catalogue_era\":\"1963 LAUNCHES\",\"launch_printed\":\"3 APR\",\"decay_printed\":\"24 NOV 63\",\"published_date\":\"1963-11-24\",\"pdf_page_index_zero_based\":47,\"pdf_page_number_one_based\":48,\"printed_page\":\"-44-\",\"catalog_number_and_name_same_row\":true,\"terminal_utc\":null,\"sensor\":null,\"station\":null,\"covariance\":null,\"temporal_sigma_seconds\":null}]")
LIMITS = json.loads("{\"identity_status\":\"PRIMARY_RETROSPECTIVE_CATALOG_CROSSWALK\",\"comparison_1963_record\":\"C241-L62\",\"original_1963_instrument_identification\":false,\"independent_tracking_observations_added\":0,\"terminal_time_measurements_added\":0,\"norad_528_hard_constraints_added\":0,\"conde_impact_confirmed\":false,\"dating_precision\":\"PUBLISHED_DAY_NOT_TIMED_EVENT\",\"possible_shared_upstream_data\":\"NASA_NORAD_SAO_UNRESOLVED\",\"source_norad_number_printed_in_1963\":false}")
PURPOSE = "Upgrade NORAD 292/565 catalogue crosswalk from secondary lookup to original NASA 1977 retrospective table without creating a 1963 instrument measurement."

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicated JSON key: " + key)
        result[key] = value
    return result

def load(path=LEDGER):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

def validate(data):
    if type(data) is not dict or set(data) != {"record_id", "purpose", "source", "rows", "limits"}:
        raise ValueError("unexpected ledger schema")
    if data["record_id"] != "C241-L69" or data["purpose"] != PURPOSE:
        raise ValueError("wrong ledger ID or purpose")
    if type(data["source"]) is not dict or data["source"] != SOURCE:
        raise ValueError("NASA source provenance altered")
    if type(data["rows"]) is not list or data["rows"] != ROWS:
        raise ValueError("printed identities/pages changed or terminal data invented")
    if type(data["limits"]) is not dict or data["limits"] != LIMITS:
        raise ValueError("crosswalk promoted to physical evidence")
    for row in data["rows"]:
        if not row["catalog_number_and_name_same_row"] or any(row[k] is not None for k in
            ("terminal_utc", "sensor", "station", "covariance", "temporal_sigma_seconds")):
            raise ValueError("nonexistent instrumental observation")
    return True

def verify_pdf(path):
    digest = hashlib.sha256()
    count = 0
    with Path(path).open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise ValueError("not PDF")
        stream.seek(0)
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
            count += len(chunk)
    if count != SOURCE["bytes"] or digest.hexdigest() != SOURCE["sha256"]:
        raise ValueError("wrong NASA PDF variant")
    return True

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path)
    options = parser.parse_args()
    validate(load())
    if options.pdf:
        verify_pdf(options.pdf)
    print("C241-L69 PASS: 1977 NASA SIGMA 1=292 and 1963 009B=565; no sensor/UTC/528.")

if __name__ == "__main__":
    main()
