"""CGEO-39: Museum holdings are documentary locators, not map pixels."""
import argparse
import hashlib
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo39_ibram_iocs15_holdings.json"
SHA = "2f99bbd2594254ce484b5c905907852eb1b6142f6c44d94913837aeb89edca4f"
LENGTH = 136248

def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))

def validate_contract(c):
    if c["schema"] != "conde.geo.iocs15-museum-holdings/v1" or c["id"] != "CGEO-39" or c["previous_id"] != "CGEO-38":
        raise ValueError("schema, ID or predecessor")
    a = c["archival_collection"]
    if (a["series_code"] != "BR RJMRAHI EP-IC-MA" or
        a["maps_listed"] != 11 or a["physical_items_declared"] != 12 or
        a["duplicates_declared"] != 1 or
        a["physical_items_declared"] - a["duplicates_declared"] != a["maps_listed"]):
        raise ValueError("holdings inventory")
    if a["finding_aid_pdf_bytes"] != LENGTH or a["finding_aid_pdf_sha256"] != SHA or a["page_zero_index"] != 26 or a["printed_page"] != 27:
        raise ValueError("finding aid provenance")
    if not a["catalogue_page"].startswith("https://atom-museurepublica.museus.gov.br/"):
        raise ValueError("archive source")
    if a["includes_literal_title"] != "Mapa da Bacia do Rio Itapicuru (BA)":
        raise ValueError("not the cited holding")
    if any(a[k] for k in ("original_item_inspected","individual_map_digitization_acquired","item_level_accession_known","rights_for_republication_verified")):
        raise ValueError("unproven museum item custody")
    p = c["prior_archive"]
    if p["reference"] != "BR AN,RIO F4.0.MAP.448" or p["publication_number"] != 15 or p["publication_year"] != 1912 or p["scale_denominator"] != 500000:
        raise ValueError("original archive attribution")
    if p["physical_copy_identity_with_ibram"]:
        raise ValueError("copies not individually inspected")
    link=c["link"]
    if link["relation"] != "SAME_TITLE_FAMILY_CANDIDATE_DIFFERENT_CATALOGUES":
        raise ValueError("unsupported lineage")
    if any(link[k] for k in ("cross_custodian_copy_identity_verified","independent_survey_proven","original_1912_image_acquired","pixel_comparison_performed")):
        raise ValueError("prematurely promoted source")
    lim=c["limits"]
    if any(lim[k] is not None for k in ("center_1963","reported_fall","uncertainty_m","flight_date")):
        raise ValueError("fabricated event geometry")
    if lim["spatial_coverage_confirmed"] or lim["can_constrain_orbital_reentry"]:
        raise ValueError("premature geometric/orbital inference")
    return "CGEO39_CONTRACT_PASS"

def verify_finding_aid(path):
    h=hashlib.sha256()
    size=0
    with Path(path).open("rb") as file:
        header=file.read(5)
        if header!=b"%PDF-":
            raise ValueError("not a PDF")
        h.update(header); size+=len(header)
        for block in iter(lambda:file.read(131072),b""):
            h.update(block);size+=len(block)
    if size!=LENGTH or h.hexdigest()!=SHA:
        raise ValueError("official PDF mismatch")
    return "CGEO39_REAL_PDF_REPLAY_PASS"

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--pdf",type=Path)
    args=parser.parse_args()
    print(validate_contract(load_contract()))
    if args.pdf:
        print(verify_finding_aid(args.pdf))
