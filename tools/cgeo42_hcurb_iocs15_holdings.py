"""CGEO-42: artigo de 2014 documenta rota HCUrb, não o mapa original."""
import argparse
import hashlib
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo42_hcurb_iocs15_holdings.json"
EXPECTED_SHA256 = "e92fcfd90536a7b4ddd0dee21af69d4a089938e98989c57fd99fcb42d5096a26"
SOURCE_URL = "https://revistes.ub.edu/index.php/ScriptaNova/article/download/15027/18380"


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def validate_contract(c):
    if (c["schema"], c["id"], c["previous_id"]) != (
        "conde.geo.iocs15-hcurb-holdings/v1", "CGEO-42", "CGEO-41"
    ):
        raise ValueError("contract identity")
    ref = c["reference_document"]
    if (ref["download_url"] != SOURCE_URL
        or ref["document_kind"] != "SECONDARY_SCHOLARLY_HOLDINGS_REPORT"
        or ref["published_on"] != "2014-11-01"
        or ref["pdf_acquired"] is not True
        or ref["pdf_bytes"] != 410611
        or ref["pdf_sha256"] != EXPECTED_SHA256
        or ref["pdf_pages"] != 18
        or ref["table_pdf_page_1based"] != 9):
        raise ValueError("scholarly reference changed")
    h = c["new_holdings_route"]
    if (h["publication_number"] != 15 or h["publication_year"] != 1912
        or h["attributed_engineer"] != "Guilherme Lane"
        or h["scale_denominator"] != 500000
        or h["dimensions_as_reported_cm"] != [69, 82]
        or h["claim_source"] != "2014_RESEARCH_ARTICLE_TABLE"
        or any(h[k] is not False for k in (
            "individual_copy_identified", "individual_copy_digitized",
            "primary_map_acquired"
        ))):
        raise ValueError("misleading HCUrb holding or map claim")
    others = {row["repository"]: row for row in c["comparison"]}
    if set(others) != {"Arquivo Nacional", "Arquivo Histórico do Exército", "Museu da República"}:
        raise ValueError("comparison coverage changed")
    expected = {"Arquivo Nacional": ([64, 89], "BR AN,RIO F4.0.MAP.448"),
                "Arquivo Histórico do Exército": ([87, 67.5], "05.36.334"),
                "Museu da República": (None, "BR RJMRAHI EP-IC-MA")}
    for name, (dimensions, identifier) in expected.items():
        row = others[name]
        if (row["dimensions_as_cataloged_cm"] != dimensions
            or row["identifier"] != identifier
            or row["physical_identity_resolved"] is not False):
            raise ValueError("catalogue comparison embellished")
    lineage = c["lineage"]
    if (lineage["hcurb_is_an_independent_survey"] is not False
        or lineage["comparison_identifies_distinct_editions"] is not False
        or lineage["differences_may_reflect_measurement_orientation_crop_or_copy"] is not True):
        raise ValueError("independence/edition not supported")
    lim = c["limits"]
    nullable = ("iocs15_original_bytes", "iocs15_sha256", "conde_in_map",
                "georeferenced_polygon", "urban_center_1963", "reentry_location",
                "spatial_uncertainty_m")
    if any(lim[k] is not None for k in nullable) or lim["can_constrain_orbital_reentry"] is not False:
        raise ValueError("invalid scientific promotion")
    return "CGEO42_HCURB_HOLDINGS_CONTRACT_PASS"


def verify_pdf(path, c):
    path = Path(path)
    digest = hashlib.sha256()
    size = 0
    head = b""
    tail = b""
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 16), b""):
            if not head:
                head = chunk[:8]
            tail = (tail + chunk)[-1024:]
            digest.update(chunk)
            size += len(chunk)
    ref = c["reference_document"]
    if (not head.startswith(b"%PDF-")
        or b"%%EOF" not in tail
        or size != ref["pdf_bytes"]
        or digest.hexdigest() != ref["pdf_sha256"]):
        raise ValueError("integral scholarly PDF mismatch")
    return "CGEO42_HCURB_2014_PDF_REPLAY_PASS"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    args = parser.parse_args()
    contract = load_contract()
    print(validate_contract(contract))
    if args.pdf is not None:
        print(verify_pdf(args.pdf, contract))
