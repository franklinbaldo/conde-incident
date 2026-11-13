"""CGEO-38: official archive catalogue and IOCS 29 replica real-byte custody."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "geo" / "cgeo38_iocs29_1913_lineage.json"
SIZES = {"map": 2440283, "ds": 1274536, "f4": 2382507}
HASHES = {
    "map": "feaae0eb8534e4f71242c01faa9dbbe71c0f7440b85e5791d8548a46306bb3dd",
    "ds": "f7f15d448f4ae48dd22a091e55c4a1d2e8324c114d42cb5a1dde600393d792a3",
    "f4": "17ef624688aecb8f20a08b447792cb09dddb9de763c45289b28c0a3ddabd9587",
}

def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))

def validate_contract(doc: dict) -> str:
    if (doc.get("schema"), doc.get("id")) != ("conde.geo.iocs29-lineage/v1", "CGEO-38"):
        raise ValueError("contract identity")
    m, i, a, edges, limits = (doc[k] for k in
                             ("map_1913", "itapicuru_1912", "archives", "edges", "limits"))
    if (m["archive_id"], m["publication"], m["printed"], m["series"],
        m["scale"], m["cartographers"]) != (
        "BR AN,RIO DS.0.MAP.5", 29, "1913-10", "I-G", 500000,
        ["Guilherme Lane", "Roberto Miller"]):
        raise ValueError("IOCS publication 29 identity")
    if (m["replica_bytes"], m["replica_sha256"]) != (SIZES["map"], HASHES["map"]):
        raise ValueError("IOCS 29 bytes")
    if m["replica"] != "https://upload.wikimedia.org/wikipedia/commons/5/56/Mapa_parcial_do_estado_da_Bahia.pdf":
        raise ValueError("IOCS 29 replica URL")
    if m["catalogue"] != "https://www.gov.br/arquivonacional/pt-br/servicos/copy_of_instrumentos-de-pesquisa/academia-brasileira-de-letras.pdf":
        raise ValueError("IOCS 29 catalogue")
    if (m["printed_page"], m["pdf_page_zero_index"], m["full_visual_inspection"]) != (9, 8, False):
        raise ValueError("catalogue page or unsupported visual claim")
    if (i["archive_id"], i["publication"], i["printed"], i["series"],
        i["scale"], i["archive_note_date"]) != (
        "BR AN,RIO F4.0.MAP.448", 15, "1912-03", "I-G", 500000, "1917-02-03"):
        raise ValueError("IOCS publication 15 identity")
    if "incluído na publicação nº 29" not in i["archive_note"]:
        raise ValueError("archival genealogy missing")
    if i["catalogue"] != "https://www.gov.br/arquivonacional/pt-br/servicos/copy_of_instrumentos-de-pesquisa/bhering-final-14-fev-13.pdf":
        raise ValueError("IOCS 15 catalogue")
    if (i["printed_page"], i["pdf_page_zero_index"]) != (116, 115):
        raise ValueError("IOCS 15 catalogue page")
    if i["original_map_acquired"] is not False or i["pixel_comparison_proven"] is not False:
        raise ValueError("unverified 1912 source promoted")
    if (a["ds_pdf_size"], a["f4_pdf_size"], a["ds_pdf_sha256"],
        a["f4_pdf_sha256"]) != (SIZES["ds"], SIZES["f4"], HASHES["ds"], HASHES["f4"]):
        raise ValueError("official archives bytes")
    if a["physical_original_inspected"] is not False:
        raise ValueError("physical original not examined")
    expected = [
        ("IOCS-15-1912", "IOCS-29-1913", "ARCHIVAL_ANNOTATION_SAYS_INCLUDED"),
        ("IOCS-29-1913", "CGEO-37", "DECLARED_CARTOGRAPHIC_SOURCE_IN_SOPER_1914"),
        ("CGEO-37", "CGEO-36", "SAME_1914_WORK_DIFFERENT_CUSTODIANS"),
    ]
    if [(x["from"], x["to"], x["relation"]) for x in edges] != expected:
        raise ValueError("lineage mismatch")
    if any(x["pixel_transfer_verified"] is not False for x in edges):
        raise ValueError("unsupported pixel transfer")
    if set(limits) != {"center_1963", "reported_fall", "uncertainty_m",
                       "flight_date", "spatial_coverage_confirmed",
                       "independent_survey", "can_constrain_orbital_reentry"}:
        raise ValueError("unexpected spatial fields")
    if any(limits[k] is not None for k in (
        "center_1963", "reported_fall", "uncertainty_m", "flight_date")):
        raise ValueError("false geometry")
    if any(limits[k] is not False for k in (
        "spatial_coverage_confirmed", "independent_survey",
        "can_constrain_orbital_reentry")):
        raise ValueError("unsupported geometric/orbital inference")
    return "CGEO38_CONTRACT_PASS"

def verify_pdf(path: Path, kind: str) -> str:
    if kind not in HASHES:
        raise ValueError("unknown PDF kind")
    digest = hashlib.sha256()
    n = 0
    prefix, suffix = b"", b""
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            if not prefix:
                prefix = chunk[:8]
            suffix = (suffix + chunk)[-1024:]
            n += len(chunk)
            digest.update(chunk)
    if n != SIZES[kind] or digest.hexdigest() != HASHES[kind]:
        raise ValueError("unexpected PDF size or SHA")
    if not prefix.startswith(b"%PDF-") or b"%%EOF" not in suffix:
        raise ValueError("invalid PDF markers")
    return "CGEO38_" + kind.upper() + "_REAL_BYTES_PASS"

def main() -> None:
    parser = argparse.ArgumentParser()
    for kind in HASHES:
        parser.add_argument("--" + kind, type=Path)
    args = parser.parse_args()
    print(validate_contract(load_contract()))
    for kind in HASHES:
        path = getattr(args, kind)
        if path is not None:
            print(verify_pdf(path, kind))

if __name__ == "__main__":
    main()
