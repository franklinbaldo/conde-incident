"""Fail-closed archival audit: date of printing is not the date of reported event."""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/tle_custody/polish_1963_q4_print_cutoff_C241_LONTRA_R66.json"


def validate(d: dict) -> bool:
    if d.get("id") != "C241-LONTRA-R66" or d.get("schema") != "conde.archival_editorial_cutoff/v1":
        raise ValueError("identity/schema")
    s = d["source"]
    expected_source = {
        "volume": "XI", "issue": 4, "year": 1963,
        "issue_cover_months": "October–December 1963",
        "pdf_url": "https://www.urania.edu.pl/sites/default/files/archiwum/postepy_astronomii_1963_04.pdf",
        "pdf_bytes": 5014393, "pdf_sha256": "d83044a1bcbb43b8448614adf7778e8ee811776925160b7bc86840c4da3084c2",
        "pdf_pages": 76, "colophon_pdf_page_one_based": 2,
        "editorial_print_handoff_date": "1963-10-12", "printing_completed_month": "1963-10",
        "visual_page_checked": True, "binary_integrity": "FULL_PDF_IFRO_SHA256_AND_PDFINFO",
    }
    for k, v in expected_source.items():
        if s.get(k) != v:
            raise ValueError("altered source: " + k)
    c = d["chronology"]
    for k, v in {
        "investigated_report_date": "1963-11-07",
        "printing_completed_before_report": True,
        "scope": "PRINTED_Q4_1963_ISSUE_ONLY",
    }.items():
        if c.get(k) != v:
            raise ValueError("unsupported chronology: " + k)
    # Derived date check, independent of flag alone.
    if s["printing_completed_month"] >= c["investigated_report_date"][:7]:
        raise ValueError("printing not strictly earlier than report month")
    b = d["limits"]
    for k, v in {
        "original_1963_satellite_station_log_recovered": False,
        "norad_527_528_529_rows": [],
        "independent_observations_recovered": 0,
        "new_orbital_constraints": 0,
        "all_other_polish_journals_excluded": False,
        "all_station_logs_excluded": False,
        "later_errata_checked": False,
        "contacts_sent": False,
    }.items():
        if k not in b or b[k] != v:
            raise ValueError("false evidentiary promotion: " + k)
    return True


def main() -> None:
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")))
    print("PASS C241-LONTRA-R66: October print cutoff, no fabricated November observation")


if __name__ == "__main__":
    main()
