"""CGEO-37: verify the ETH Soper 1914 cross-custody evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo37_eth_soper_crosscustody.json"
EXPECTED_SHA = {
    "pdf": "5e0db1bdc45f8d44ddcdc985b28ef2115537d05d7d762fa1c5e0a16256149514",
    "manifest": "1284c8720d0d9647cbba1b1019cb7b4b2e575b966bab1bfd037c0d43298567c2",
    "jpeg": "326d94f7e3b175bf8a60740ca4fb1ca0474cef5d1bce659218f2f590d508a618",
}


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def validate_contract(d: dict) -> str:
    w, e, x, o, lim = (d[k] for k in
                      ("historical_work", "eth_custody", "comparison", "observations", "limits"))
    if (d["schema"], d["id"]) != ("conde.geo.soper-crosscustody/v1", "CGEO-37"):
        raise ValueError("contract identity")
    if (w["printed_year"], w["scale_denominator"], w["author"]) != (1914, 1000000, "Ralph H. Soper"):
        raise ValueError("anachronistic cartography")
    if "publicação n. 29" not in w["reported_cartographic_source"]:
        raise ValueError("missing printed cartographic lineage")
    if (e["call_number"], e["doi"], e["online_since"]) != (
        "K 368018", "https://doi.org/10.3931/e-rara-153583", "2026-09-15"):
        raise ValueError("custodian or dates changed")
    if (e["iiif_manifest_bytes"], e["pdf_bytes"], e["jpeg_bytes"]) != (2703, 2020098, 151507):
        raise ValueError("real file lengths changed")
    if any(e[n] != s for n, s in (
        ("pdf_sha256", EXPECTED_SHA["pdf"]),
        ("iiif_manifest_sha256", EXPECTED_SHA["manifest"]),
        ("jpeg_sha256", EXPECTED_SHA["jpeg"]))):
        raise ValueError("replay SHA changed")
    if (e["canvas_width"], e["canvas_height"], e["jpeg_dimensions_px"]) != (9841, 11142, [1000, 1132]):
        raise ValueError("image dimensions changed")
    if e["iiif_manifest_url"] != "https://www.e-rara.ch/i3f/v20/32574892/manifest":
        raise ValueError("IIIF endpoint changed")
    if e["image_service"] != "https://www.e-rara.ch/i3f/v20/32574893":
        raise ValueError("image service changed")
    if (x["existing_occurrence_id"], x["other_pdf_sha256"]) != (
        "CGEO-36", "66c9646a3a3e15bb6a8525e90c7697d3177d0be979e42c3b599f90241ef0cf33"):
        raise ValueError("wrong comparison")
    if x["same_printed_work_identified"] is not True or any(
        x[k] is not False for k in
        ("same_physical_copy_demonstrated", "pixel_identity_demonstrated",
         "independent_survey_or_1963_observation", "copy_lineage_direction_known")
    ):
        raise ValueError("two scans are not independent observations")
    if o != {
        "printed_toponym_conde": True,
        "printed_toponym_sitio": True,
        "toponyms_are_distinct_on_map": True,
        "topography_has_explicit_multiple_sources": True,
        "geographic_coords_for_toponyms_from_this_work": None,
        "digitization_is_observation_in_1914": False,
        "iiif_canvas_px_are_not_geographic_coords": True,
    }:
        raise ValueError("source observation promoted to geometry")
    if {i["id"] for i in d["dependencies"]} != {"CGEO-36", "CGEO-35", "CGEO-18"}:
        raise ValueError("missing provenance graph edges")
    if set(lim) != {
        "historical_city_center_polygon_1963", "reported_impact_coordinates",
        "dated_flight_or_aerophotogram", "map_to_world_transform",
        "horizontal_uncertainty_m", "can_constrain_orbital_reentry"
    } or any(lim[k] is not None for k in lim if k != "can_constrain_orbital_reentry") or lim["can_constrain_orbital_reentry"] is not False:
        raise ValueError("unsupported 1963 spatial or orbital constraint")
    return "CGEO37_CONTRACT_PASS"


def verify_file(path: Path, expected_bytes: int, expected_sha: str, kind: str) -> str:
    digest = hashlib.sha256()
    size = 0
    prefix = b""
    suffix = b""
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            if not prefix:
                prefix = chunk[:16]
            suffix = (suffix + chunk)[-1024:]
            size += len(chunk)
            digest.update(chunk)
    if size != expected_bytes or digest.hexdigest() != expected_sha:
        raise ValueError(f"{kind} custody failed")
    if kind == "pdf" and (not prefix.startswith(b"%PDF-") or b"%%EOF" not in suffix):
        raise ValueError("not PDF")
    if kind == "jpeg" and (not prefix.startswith(bytes.fromhex("ffd8")) or not suffix.endswith(bytes.fromhex("ffd9"))):
        raise ValueError("not JPEG")
    if kind == "manifest":
        obj = json.loads(path.read_text(encoding="utf-8"))
        canvas = obj["sequences"][0]["canvases"][0]
        image = canvas["images"][0]["resource"]
        if (canvas["width"], canvas["height"], image["service"]["@id"]) != (
            9841, 11142, "https://www.e-rara.ch/i3f/v20/32574893"):
            raise ValueError("incorrect IIIF canvas")
    return "CGEO37_" + kind.upper() + "_REAL_BYTES_PASS"


def main() -> None:
    args = argparse.ArgumentParser()
    for kind in ("pdf", "manifest", "jpeg"):
        args.add_argument("--" + kind, type=Path)
    opt = args.parse_args()
    doc = load_contract()
    print(validate_contract(doc))
    e = doc["eth_custody"]
    for kind, sizekey in (("pdf", "pdf_bytes"), ("manifest", "iiif_manifest_bytes"), ("jpeg", "jpeg_bytes")):
        path = getattr(opt, kind)
        if path is not None:
            print(verify_file(path, e[sizekey], EXPECTED_SHA[kind], kind))


if __name__ == "__main__":
    main()
