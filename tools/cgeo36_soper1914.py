"""CGEO-36: 1914 Soper map custody and anti-anachronism checks."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo36_soper_1914_conde_sitio.json"
PDF_SHA = "66c9646a3a3e15bb6a8525e90c7697d3177d0be979e42c3b599f90241ef0cf33"
JPG_SHA = "172b519c2f89cc0f17341ce0e41887701987b25fa3c2d08d3814ead3ca4a7fbb"

def read():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))

def verify_contract(d):
    s, v, h, lim = d["source"], d["inspected_derivative"], d["historical_inference"], d["limits"]
    if (d["schema"], d["id"], d["date_checked"]) != ("conde.geo.early-cartographic-toponyms/v1","CGEO-36","2026-11-13"):
        raise ValueError("wrong identity")
    if (s["publication"], s["printed_scale_denominator"], s["archival_accession"]) != ("1914-07",1000000,"BR RJANRIO DS.0.MAP.28"):
        raise ValueError("changed historical source")
    if (s["pdf_bytes"],s["pdf_sha256"],s["pdf_pages"],s["listed_scan_dimensions_px"]) != (1383563,PDF_SHA,1,[3977,4475]):
        raise ValueError("wrong PDF custody")
    if not s["pdf_url"].startswith("https://upload.wikimedia.org/wikipedia/commons/d/d4/Mapa_do_estado_"):
        raise ValueError("unknown PDF endpoint")
    if (v["bytes"],v["sha256"],v["size_px"],v["image_region_xyxy_px"]) != (967413,JPG_SHA,[1920,2161],[750,1110,1250,1510]):
        raise ValueError("changed visual derivative")
    if (v["visible_labels"],v["position_is_image_space_only"],v["manual_reading_without_ocr"],v["separate_named_localities_not_centers"]) != (["Conde","Sítio"],True,True,True):
        raise ValueError("promoted unverified place")
    if "page1-1920px-" not in v["url"] or not v["url"].endswith(".pdf.jpg"):
        raise ValueError("wrong visual endpoint")
    if h != {"pre_1963_printed_map":True,"independent_of_1954_cartographic_survey":None,"modern_sitio_do_conde_identity_demonstrated":False,"city_centre_1963_identified":False,"reported_fall_location_1963_identified":False,"new_observation_of_1963":False}:
        raise ValueError("anachronistic historical inference")
    if set(lim) != {"historical_city_center_polygon_1963","reported_impact_coordinates","map_to_world_transform","horizontal_uncertainty_m","historical_bridge_to_1963","can_constrain_orbital_reentry"}:
        raise ValueError("missing limitation")
    if any(lim[x] is not None for x in lim if x != "can_constrain_orbital_reentry") or lim["can_constrain_orbital_reentry"] is not False:
        raise ValueError("invented geometry or orbital filter")
    if d["bibliographic_crosscheck"]["independently_verified_pixel_identity"] is not False:
        raise ValueError("cross-custodian pixel identity not verified")
    if {(x["to"],x["kind"]) for x in d["graph_links"]} != {
        ("CGEO-18","EARLIER_LOCALITY_LABEL_NOT_FALL_POSITION"),
        ("CGEO-20","CONDE_AND_SITIO_SEPARATE_LABELS_NO_1963_IDENTITY"),
        ("CGEO-35","EARLIER_PRINTED_MAP_DIFFERENT_SHEET_NO_SHARED_SURVEY_PROVEN")}:
        raise ValueError("source genealogy changed")
    return "CGEO36_CONTRACT_PASS"

def verify_asset(path: Path, expected_size: int, expected_sha: str, fmt: str) -> str:
    sha=hashlib.sha256()
    size=0
    first=b""
    tail=b""
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024 * 64),b""):
            if not first:
                first=b[:16]
            tail=(tail+b)[-1024:]
            size+=len(b)
            sha.update(b)
    if size != expected_size or sha.hexdigest() != expected_sha:
        raise ValueError("wrong bytes or SHA256")
    if fmt=="pdf" and (not first.startswith(b"%PDF-") or b"%%EOF" not in tail):
        raise ValueError("not a PDF")
    if fmt=="jpg" and (not first.startswith(bytes.fromhex("ffd8")) or not tail.endswith(bytes.fromhex("ffd9"))):
        raise ValueError("not a JPEG")
    return f"CGEO36_{fmt.upper()}_REAL_BYTES_PASS"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pdf",type=Path)
    parser.add_argument("--thumb",type=Path)
    args=parser.parse_args()
    d=read()
    print(verify_contract(d))
    if args.pdf:
        print(verify_asset(args.pdf,d["source"]["pdf_bytes"],PDF_SHA,"pdf"))
    if args.thumb:
        print(verify_asset(args.thumb,d["inspected_derivative"]["bytes"],JPG_SHA,"jpg"))

if __name__=="__main__": main()
