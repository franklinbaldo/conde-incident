#!/usr/bin/env python3
"""C241-L18: verify NASA 1963 table transcriptions and separate publication from tracking."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

PINS = [
    ("19630012290", "1963-07-31", 15, "1963-07-31T12:00:00Z", 252826,
     "9b00bf8323b1de80a34920f73c658f70f766a51632a13473a408679f0e5a03d9",
     [("1963-003A", "94.6", "81.88", 537, 458),
      ("1963-003B", "93.6", "81.88", 463, 415),
      ("1963-003C", "93.9", "81.88", 498, 425)]),
    ("19640002493", "1963-11-30", 23, "1963-11-30T12:00:00Z", 1266393,
     "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d",
     [("1963-003A", "94.6", "81.88", 533, 459),
      ("1963-003C", "92.2", "81.86", 390, 368)]),
    ("19640005618", "1963-12-31", 25, "1963-12-31T12:00:00Z", 992569,
     "d9504a8641baa65c208e41034e77b0e9b1cc01b4acb2a4f95541bd9e75d3783d",
     [("1963-003A", "94.6", "81.89", 530, 461),
      ("1963-003C", "89.2", "81.82", 335, 333)]),
]


def validate(ledger):
    if ledger["id"] != "C241-L18" or ledger["identity_crosswalk"] != "C241-L10":
        raise ValueError("wrong identity")
    if len(ledger["sources"]) != len(PINS):
        raise ValueError("wrong source count")
    for source, (ident, pub, number, as_of, size, sha, expected) in zip(ledger["sources"], PINS):
        if (source["ntrs_id"], source["published"], source["issue"],
                source["as_of_utc"], source["volume"], source["pdf_page_index"],
                source["printed_page"], source["bytes"], source["sha256"]) != (
                    ident, pub, number, as_of, 3, 6, 5, size, sha):
            raise ValueError("source provenance changed")
        if source["pdf_url"] != (
                f"https://ntrs.nasa.gov/api/citations/{ident}/downloads/{ident}.pdf"):
            raise ValueError("source link mismatched")
        rows = source["rows"]
        if len(rows) != len(expected):
            raise ValueError("source rows altered")
        for row, intended in zip(rows, expected):
            if tuple(row[k] for k in ("designator", "period_min", "inclination_deg",
                                      "apogee_km", "perigee_km")) != intended:
                raise ValueError("transcription changed")
            if (not isinstance(row["apogee_km"], int) or
                not isinstance(row["perigee_km"], int) or
                row["perigee_km"] > row["apogee_km"]):
                raise ValueError("implausible printed altitude")
    conflict = ledger["sources"][2]["transcription_conflict"]
    if (conflict["matrix_occurrence"] != "C227" or
        conflict["prior_reported_period_min"] != "89.6" or
        conflict["facsimile_current_read_period_min"] != "89.2" or
        conflict["status"] != "OPEN_REQUIRES_INDEPENDENT_REVIEW" or
        conflict["eligible_for_calibrated_physical_fit"] is not False):
        raise ValueError("unresolved conflicting readings must stay explicit")
    lim = ledger["data_lineage"]
    if (lim["original_instrument_tracking"] is not False or
        lim["shared_institutional_compiler"] != "NASA_GODDARD_NORAD_SMITHSONIAN" or
        lim["independent_sensor_samples"] != 0 or
        lim["source_report_reference_time_is_instrument_epoch"] is not False or
        lim["additional_rows_are_distinct_compilation_snapshots_not_new_independent_sensors"] is not True or
        lim["b_decay_day"] != "1963-11-08" or
        lim["b_absence_in_postdecay_in_orbit_tables"] is not True or
        lim["inference_on_conde"] != "INDETERMINATE"):
        raise ValueError("incorrect historical inference")
    for key in ("measurement_uncertainty_sigma", "instrument_station",
                "primary_tle", "historical_frame", "relative_orbital_phase"):
        if lim[key] is not None:
            raise ValueError("invented instrument data")
    physics = ledger["use_as_constraint"]
    if (physics["activation"] != "CANDIDATE_NOT_ACTIVATED" or
        physics["independent_density_constraint_proven"] is not False or
        physics["quantified_uncertainty_reduction"] != "NOT_EVALUABLE" or
        physics["bridge"] != "C241-P10-three-object-relative-trajectories" or
        physics["lean_numeric_use"] != "DOCUMENTARY_INTERVAL_ONLY_CONDITIONAL_ON_UNRESOLVED_DEC31_TRANSCRIPTION"):
        raise ValueError("premature activation")
    jul, nov, dec = ledger["sources"]
    delta_c = Decimal(nov["rows"][1]["period_min"]) - Decimal(dec["rows"][1]["period_min"])
    assert delta_c == Decimal("3.0")
    return {
        "record_id": "C241-L18",
        "distinct_source_editions": 3,
        "independent_instrument_measurements_found": 0,
        "july_b_period_min_printed": jul["rows"][1]["period_min"],
        "survivor_527_nov_dec_periods": [nov["rows"][0]["period_min"], dec["rows"][0]["period_min"]],
        "survivor_529_nov_dec_current_facsimile_readings": [
            nov["rows"][1]["period_min"], dec["rows"][1]["period_min"]],
        "529_nov_dec_printed_delta_min_if_dec_reading_is_89_2": str(delta_c),
        "529_nov_dec_conservative_delta_min_with_unresolved_89_2_or_89_6_and_tenth_rounding": ["2.50", "3.10"],
        "new_physical_orbit_epochs_proven": 0,
        "physical_domain_reduced": False,
        "conde_outcome": "INDETERMINATE",
    }


def audit(ledger, pdf_bytes_by_ntrs):
    report = validate(ledger)
    for ident, _, _, _, size, sha, _ in PINS:
        raw = pdf_bytes_by_ntrs[ident]
        if not raw.startswith(b"%PDF-"):
            raise ValueError("source is not PDF")
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != sha:
            raise ValueError(f"NASA source bytes changed: {ident}")
    report["source_integrity_checked"] = True
    report["pdf_pixels_reinspected_by_ci"] = False
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--pdf-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    ledger = json.loads(a.ledger.read_text())
    bytes_by_id = {ident: (a.pdf_dir / (ident + ".pdf")).read_bytes()
                   for ident, *_ in PINS}
    report = audit(ledger, bytes_by_id)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("C241-L18: 3 pinned NASA reports PASS; sensor epochs and Conde impact NOT_ESTABLISHED")


if __name__ == "__main__":
    main()
