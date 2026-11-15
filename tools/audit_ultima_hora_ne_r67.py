"""Audit specific FBN PDF identity and forbid broad negatives from front-page readings."""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/archive/ultima_hora_ne_nov1963_C241_LONTRA_R67.json"
EXPECTED = [
    ("1963-11-09", "00472", 10, 5275519, "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece"),
    ("1963-11-10", "00473", 18, 8298891, "f37e4afa500fe841546a751e562cc799c33c699decb8967b2ae00b45e721e349"),
    ("1963-11-11", "00474", 10, 4884439, "3d7b9268c1cf45c7700ddf65bfa985c9d17724369d9b0412f9442f4fea87faad"),
    ("1963-11-12", "00475", 10, 5031193, "88859dfbab5e9590614b684121507c7eb54148028a66d1efb9a3269d6444611f"),
]


def validate(d: dict) -> bool:
    if d.get("schema") != "conde.newspaper_issue_custody/v1" or d.get("id") != "C241-LONTRA-R67" or d.get("project_issue") != 871:
        raise ValueError("wrong manifest/issue")
    c = d["collection"]
    if c["collection_id"] != "765147" or c["catalog_url"] != "https://bndigital.bn.gov.br/acervo-digital/ultima-hora/765147":
        raise ValueError("collection identity")
    if len(d["issues"]) != 4:
        raise ValueError("missing or added dates")
    for i, (date, edition, pages, size, digest) in enumerate(EXPECTED):
        row = d["issues"][i]
        expected = {
            "date": date, "edition": edition, "pdf_pages": pages,
            "pdf_bytes": size, "pdf_sha256": digest, "pdfinfo_version": "1.4",
            "pdf_eof_verified": True, "front_page_date_read_visually": True,
            "pdf_url": f"https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_{edition}.pdf",
            "front_page_status": "LIDO_SEM_HORA", "front_page_status_scope": "PAGE_1_ONLY",
            "other_pages_fully_read": False, "edition_wide_negative_claim": False,
            "condereport_hour_quoted": None, "condereport_site_quoted": None,
            "reporter_independence": "UNDETERMINED",
        }
        for key, expected_value in expected.items():
            if row.get(key, object()) != expected_value:
                raise ValueError(f"unsupported assertion {edition}/{key}")
    a = d["atarde"]
    if a["online_access_state"] != "INACESSIVEL" or a["claim_not_digitized"] is not False or a["scans_read"] is not False or a["exact_issues_confirmed"] is not False:
        raise ValueError("A Tarde access or digitization misrepresented")
    if a["digitization_period"] != "1912-1999" or a["dates"] != [f"1963-11-{x:02d}" for x in range(8, 13)]:
        raise ValueError("A Tarde coverage")
    j = d["jornal_bahia"]
    if j["date"] != "1963-11-11" or j["issue_confirmed"] is not False or j["original_scan_read"] is not False or j["fbc_homonym_not_same_newspaper"] is not True:
        raise ValueError("Jornal da Bahia caveat")
    expected_limits = {
        "hour_local_event_found": False, "front_page_no_event_time_not_full_issue_search": True,
        "all_original_pages_visually_read": False, "independent_witness_verified": False,
        "physical_orbital_constraint_added": False, "no_external_contacts": True,
        "cloud_build_run": False, "cloud_build_status": "BLOCKED_IAM",
        "archive_pdfs_committed_to_git": False,
    }
    for key, val in expected_limits.items():
        if d["limitations"].get(key) != val:
            raise ValueError("false scientific promotion " + key)
    return True


def main() -> None:
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")))
    print("PASS C241-LONTRA-R67: four PDFs pinned; cover-only reading; no invented event time")


if __name__ == "__main__":
    main()
