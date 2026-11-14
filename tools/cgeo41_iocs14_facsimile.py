"""CGEO-41: custódia do mapa IOCS nº 14; não substituir o original nº 15."""
import argparse
import hashlib
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo41_iocs14_facsimile.json"
EXPECTED_SHA256 = "f0ca966501154833d8fd011b4e00c5e50a9c148b20233f3578dc94706c10340f"
EXPECTED_SHA1 = "3920fdc7e8db516af62eb8f60ac2089ed5c55646"
URL = "https://upload.wikimedia.org/wikipedia/commons/6/6c/Mapa_de_parte_dos_Estados_de_Pernambuco%2C_Piau%C3%AD_e_Bahia_1912.pdf"


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def validate_contract(c):
    if (c["schema"], c["id"], c["previous_id"]) != (
        "conde.geo.iocs14-facsimile-custody/v1", "CGEO-41", "CGEO-40"
    ):
        raise ValueError("contract identity")
    s = c["source"]
    if (
        s["publication_number"] != 14 or s["series"] != "1-G"
        or s["nominal_date"] != "1912-03" or s["nominal_scale"] != "1:500000"
        or s["original_archive"] != "Arquivo Nacional"
        or s["original_accession"] != "BR RJANRIO DS.0.MAP.22"
        or s["source_kind"] != "DIGITIZED_MAP_FACSIMILE"
        or s["download_url"] != URL or s["pdf_acquired"] is not True
        or s["pdf_bytes"] != 1803202 or s["pdf_sha256"] != EXPECTED_SHA256
        or s["pdf_sha1"] != EXPECTED_SHA1 or s["pages"] != 1
        or s["source_raster_dimensions_px"] != [4870, 4868]
        or s["pdf_digitization_metadata_date"] != "2018-07-17"
        or s["wikimedia_upload_date"] != "2021-10-14"
        or s["visual_cartographic_inspection_completed"] is not False
        or s["selected_conde_footprint_verified"] is not False
    ):
        raise ValueError("source, checksum or epoch changed")
    l = c["lineage"]
    if (
        l["iocs15"]["publication_number"] != 15
        or l["iocs15"]["archive_accession"] != "BR AN,RIO F4.0.MAP.448"
        or l["iocs15"]["facsimile_acquired"] is not False
        or l["iocs29"]["publication_number"] != 29
        or l["iocs29"]["archive_accession"] != "BR RJANRIO DS.0.MAP.5"
        or l["relation_to_iocs15"] != "DISTINCT_PUBLICATIONS_SAME_INSTITUTION_NOT_PROVEN_INDEPENDENT_SURVEYS"
        or l["relation_to_iocs29"] != "DOCUMENTARY_GENEALOGY_NOT_DEMONSTRATED"
        or l["direct_cartographic_reuse_proven"] is not False
        or l["independent_observations_proven"] is not False
    ):
        raise ValueError("documentary lineage invented")
    lim = c["limits"]
    unknowns = (
        "conde_present_on_map", "coverage_of_conde", "datum",
        "georeferenced_bounds", "center_1963", "reported_fall_location",
        "reported_fall_uncertainty_m"
    )
    if any(lim[key] is not None for key in unknowns):
        raise ValueError("unproven spatial or temporal assertion")
    if lim["can_constrain_orbital_reentry"] is not False:
        raise ValueError("unproven orbital constraint")
    return "CGEO41_DOCUMENT_CUSTODY_CONTRACT_PASS"


def verify_pdf(path, contract):
    content = Path(path).read_bytes()
    if not content.startswith(b"%PDF-") or not content.rstrip().endswith(b"%%EOF"):
        raise ValueError("not a complete PDF")
    s = contract["source"]
    if (len(content) != s["pdf_bytes"]
        or hashlib.sha256(content).hexdigest() != s["pdf_sha256"]
        or hashlib.sha1(content).hexdigest() != s["pdf_sha1"]):
        raise ValueError("integral PDF mismatch")
    return "CGEO41_ORIGINAL_IOCS14_PDF_REPLAY_PASS"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path)
    args = p.parse_args()
    c = load_contract()
    print(validate_contract(c))
    if args.pdf:
        print(verify_pdf(args.pdf, c))
