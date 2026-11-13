"""CGEO-33: preserve the epistemic gap between map index and airborne image footprint."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/geo/cgeo33_sei_history.json"
PARENTS = (
    ROOT / "research/geo/cgeo25_esplanada_edition_lineage.json",
    ROOT / "research/geo/cgeo26_pet53d_1961_aerial_locator.json",
    ROOT / "research/geo/cgeo32_dnocs213_1961_mi1850.json",
)
EXPECTED_SHA = "267f1f30775f8a44b1c5ab17ce1bf25d303713530d006c0302e4854760fa0865"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(d, parents):
    def require(ok, why):
        if not ok:
            raise ValueError(why)
    require(d["id"] == "CGEO-33" and d["schema"] == "conde.gis.cartographic-historiography/v1", "identity")
    require(d["municipality"] == {"name": "Conde", "state": "BA", "ibge_code": 2908606}, "municipality")
    s = d["source"]
    require(s["publisher"] == "SEI Bahia / CECAR" and s["year"] == 2025, "source and publication year")
    require(s["printed_pages"] == [69,70] and s["section"] == "5.1 Histórico", "page scope")
    require(s["url"].startswith("https://www.ba.gov.br/sei/"), "official document URL")
    require(s["pdf_bytes"] == 12278693 and s["pdf_sha256"] == EXPECTED_SHA, "real PDF integrity")
    require(s["pdf_integral_bytes_acquired"] is True and s["source_text_read"] is True, "acquisition status")
    require(s["visual_pages_rendered"] is False and s["source_type"] == "INSTITUTIONAL_RETROSPECTIVE_2025_NOT_CONTEMPORANEOUS_1963", "no invented visual or contemporaneous provenance")
    ib, ba, pet = d["archival_claims"]
    require(ib["id"] == "IBGE_250K" and ib["printed_page"] == 69 and ib["scale_denominator"] == 250000, "250k source")
    require(ib["production_years"] == ["1949-1952", "1956"] and ib["sheets_reported"] == 31 and ib["coverage_complete"] is False, "250k period or completeness")
    require(ib["conde_sheet_identified"] is None and ib["urban_center_1963_located"] is False, "no Conde map yet")
    require(ba["id"] == "BA_100K" and ba["multiple_agencies_and_editions"] is True and ba["esplanada_edition_before_november_1963_confirmed"] is False, "coexisting editions")
    require(pet["id"] == "PETROBRAS_25K" and pet["printed_page"] == 70 and pet["scale_denominator"] == 25000, "Petrobras source")
    require(pet["nominal_decade"] == "1960s" and pet["first_mapping_sheet_cut"] == "FREE", "first mapping temporal distinction")
    require(pet["second_mapping_year"] == 1998 and pet["second_mapping_partial_sheets"] is True, "1998 edition extent")
    require(pet["actual_1961_photo_footprint"] is None and pet["project_53d_same_program_confirmed"] is None, "original acquisition unknown")
    byid = {p["id"]:p for p in parents}
    require({"CGEO-25","CGEO-26","CGEO-32"} <= set(byid), "parent lineage missing")
    require(byid["CGEO-26"]["catalogue_occurrence"]["observed_entry"]["sheet_mi"] == 1850, "53D MI")
    require(byid["CGEO-32"]["new_locator"]["sheet_mi"] == 1850, "DNOCS MI")
    l = d["interpretive_limits"]
    require(l["ica_pre1963_250k_sheet_covers_conde"] is None, "old map not located")
    require(l["old_250k_sheet_is_urban_precision"] is False, "map scale precision")
    require(l["first_1960s_sheet_cuts_prove_conde_coverage"] is False and l["post1998_partial_sheet_proves_1961_footprint"] is False, "time-leak")
    require(l["project_53d_identified_with_regional_petrobras_program"] is None, "program matching")
    for x in ["historical_center_1963","municipal_boundary_1963","reported_fall_location","uncertainty_m"]:
        require(l[x] is None, "fabricated geometry: "+x)
    require(l["new_orbital_constraint"] is False and l["can_constrain_orbital_reentry"] is False and l["source_is_independent_1963_observation"] is False, "scientific grade")
    require({e["to"] for e in d["dependencies"]} == {"CGEO-18","CGEO-24","CGEO-25","CGEO-26","CGEO-32"}, "cumulative graph")
    return "CGEO33_REAL_PDF_PROVENANCE_CONTRACT_PASS"


def verify_pdf(path, d):
    raw = path.read_bytes()
    if len(raw) != d["source"]["pdf_bytes"] or hashlib.sha256(raw).hexdigest() != EXPECTED_SHA:
        raise ValueError("PDF bytes changed from official downloaded version")
    if not raw.startswith(b"%PDF"):
        raise ValueError("invalid PDF signature")
    return "CGEO33_REAL_PDF_SHA256_REPLAY_PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    d = read(SOURCE)
    print(verify(d, [read(p) for p in PARENTS]))
    if args.pdf:
        print(verify_pdf(args.pdf, d))


if __name__ == "__main__":
    main()
