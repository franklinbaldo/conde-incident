"""C241-L15: source-dependent annual *launch* row is not a 528 observation."""
import argparse
import hashlib
import json
from pathlib import Path


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def audit(annual, october, november, pdf_bytes=None):
    p = annual["publication"]
    require(annual["record_id"] == "C241-L15", "wrong record")
    require(p["series"] == "NASA SP-4004" and p["publication_year"] == 1964, "publication")
    require(p["methodology_page_printed"] == 501 and p["row_page_printed"] == 502 and p["row_pdf_page_index_zero_based"] == 509, "page")
    require(p["url"] == "https://www.nasa.gov/wp-content/uploads/2023/04/sp-4004-1963.pdf", "url")
    require(p["transcription_method"] == "VISUAL_REINSPECTION_PINNED_PDF_PAGE_502_2026-11-13", "transcription method")
    require(p["page_image_verified"] is True, "original page not visually validated")
    require(p["sha256"] == "194fdcbc26509fc7ce4ec775aafa4914aa54c57c4617af99d1581790e10ef73d" and p["bytes"] == 18442378, "source hash metadata")
    pdf_status = "NOT_RUN"
    if pdf_bytes is not None:
        require(len(pdf_bytes) == p["bytes"], "PDF size mismatch")
        require(hashlib.sha256(pdf_bytes).hexdigest() == p["sha256"], "PDF SHA mismatch")
        pdf_status = "PASS_BYTES_VISUAL_REVIEW_IS_MANUAL_NOT_REEXECUTED"
    method = annual["methodological_note"]
    require(method["declares_compilation"] is True, "annual book is a compilation")
    require("Satellite Situation Report" in method["orbit_data_source_options"], "declared possible upstream")
    require(method["specific_upstream_for_1963_3"] is None, "specific lineage cannot be assumed")
    require(method["measurement_independence"] == "NOT_ESTABLISHED", "independence")
    row = annual["annual_row_extracted_text"]
    require(row["international_designation_printed"] == "1963-3", "annual launch designation")
    require(row["scope"] == "LAUNCH_GROUP_UNRESOLVED_CHILD", "group-level scope")
    require(row["status_printed"] == "Still in orbit.", "annual status literal")
    require(row["perigee_statute_miles_printed"] == 286 and row["apogee_statute_miles_printed"] == 334, "statute miles not km")
    require(row["name_printed"] == "DOD Spacecraft" and row["vehicle_printed"] == "Thor-Agena D." and row["launch_date_printed"] == "Jan. 16", "visual source identity and launch date")
    require(row["period_minutes_printed"] == "94.6" and row["inclination_deg_printed"] == "81.89", "printed group period and inclination")
    require(row["observation_epoch"] is None, "do not invent observation epoch")
    require(row["child_piece_identifier"] is None and row["visual_transcription_confirmed"] is True, "group image verified but child unknown")
    links = annual["linked_sources"]
    require(links["october_report_id"] == october["record_id"] == "C241-L12", "October source lineage")
    require(links["november_report_id"] == november["record_id"] == "C241-L11", "November source lineage")
    children = {r["printed"] for r in october["catalog_rows"]}
    require(children == {"1963 3A", "1963 3B", "1963 3C"}, "October designations")
    require(links["october_piece_printed"] in children, "October B row")
    require(links["november_piece_printed"] == "1963 3B", "November B row")
    november_source = next(s for s in november["sources"] if s["ntrs_id"] == "19640001198")
    require(november_source["human_table_observation"]["decay_day"] == links["november_decay_day"] == "1963-11-08", "day-only decay")
    guards = annual["inference_guard"]
    for k in ("aggregate_status_is_528_status", "aggregate_date_is_tle_epoch",
              "annual_is_independent_orbital_measurement", "annual_is_primary_instrumental_tle",
              "can_infer_terminal_time_or_place", "legacy_raan_2841520_active", "raan_1985261_primary"):
        require(guards[k] is False, "forbidden inference: " + k)
    for k in ("physical_identity_528", "instrument_sigma", "physical_frame"):
        require(guards[k] is None, "unknown cannot become zero: " + k)
    require(guards["graph_state"] == "CONNECTED_PENDING_CALIBRATION", "graph link")
    require(guards["lean_constraint"] == "NOT_PROMOTED" and guards["conde_outcome"] == "INDETERMINATE", "epistemic status")
    return {
        "occurrence": "C241-L15#1",
        "source_sha256": p["sha256"], "source_bytes": p["bytes"],
        "pdf_integrity": pdf_status,
        "annual_key": "1963-3", "child_key": "1963 3B",
        "same_observation": False,
        "annual_status_assignable_to_528": False,
        "row_printed_page": 502, "group_period_minutes_printed": "94.6",
        "group_launch_date_printed": "Jan. 16",
        "provenance_edge": "NASA_SP4004 -> POSSIBLE_SSR_SOURCE -> OCT_AND_NOV_REPORTS",
        "specific_upstream": None, "visual_verification": "HUMAN_REINSPECTED_PINNED_FACSIMILE_P502_NOT_AUTOMATED_BY_SCRIPT",
        "observational_independence": "NOT_ESTABLISHED",
        "graph_state": "CONNECTED_PENDING_CALIBRATION",
        "conde_outcome": "INDETERMINATE",
    }


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("--ledger", required=True)
    pa.add_argument("--october", required=True)
    pa.add_argument("--november", required=True)
    pa.add_argument("--pdf")
    pa.add_argument("--output")
    args = pa.parse_args()
    def read(path):
        return json.loads(Path(path).read_text(encoding="utf-8"))
    result = audit(read(args.ledger), read(args.october), read(args.november),
                   Path(args.pdf).read_bytes() if args.pdf else None)
    message = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(message, encoding="utf-8")
    else:
        print(message, end="")


if __name__ == "__main__":
    main()
