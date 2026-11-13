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
    require(p["page_printed"] == 501, "page")
    require(p["url"] == "https://www.nasa.gov/wp-content/uploads/2023/04/sp-4004-1963.pdf", "url")
    require(p["transcription_method"] == "OFFICIAL_PDF_EXTRACTED_TEXT_NOT_VISUALLY_REINSPECTED", "transcription method")
    require(p["page_image_verified"] is False, "no visual validation performed")
    require(len(p["sha256"]) == 64 and p["bytes"] > 0, "source hash metadata")
    pdf_status = "NOT_RUN"
    if pdf_bytes is not None:
        require(len(pdf_bytes) == p["bytes"], "PDF size mismatch")
        require(hashlib.sha256(pdf_bytes).hexdigest() == p["sha256"], "PDF SHA mismatch")
        pdf_status = "PASS_BYTES_ONLY_NOT_VISUAL"
    method = annual["methodological_note"]
    require(method["declares_compilation"] is True, "annual book is a compilation")
    require("Satellite Situation Report" in method["orbit_data_source_options"], "declared possible upstream")
    require(method["specific_upstream_for_1963_3"] is None, "specific lineage cannot be assumed")
    require(method["measurement_independence"] == "NOT_ESTABLISHED", "independence")
    row = annual["annual_row_extracted_text"]
    require(row["international_designation_printed"] == "1963-3", "annual launch designation")
    require(row["scope"] == "LAUNCH_GROUP_UNRESOLVED_CHILD", "group-level scope")
    require(row["status_printed"] == "Still in orbit.", "annual status literal")
    require(row["perigee_statute_miles_printed"] == 286, "statute miles not km")
    require(row["period_minutes_printed"] is None and row["observation_epoch"] is None, "do not invent orbital data")
    require(row["child_piece_identifier"] is None and row["visual_transcription_confirmed"] is False, "unverified child assignment")
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
        "provenance_edge": "NASA_SP4004 -> POSSIBLE_SSR_SOURCE -> OCT_AND_NOV_REPORTS",
        "specific_upstream": None, "visual_verification": "NOT_RUN",
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
