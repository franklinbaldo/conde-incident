"""Verify the actual SGB photoindex image and the narrow roll/line reading."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo45_mi1850_roll58.json"
PARENT = ROOT / "research/geo/cgeo44_mi1850_photoindex.json"
DIGEST = "45d72dff84520bb387d5b8ce7c5a8f4c9361457841341b2c21016e992c0fef79"


def validate(m, p):
    if (m["schema"], m["id"], m["based_on"], p["id"]) != (
        "conde.cgeo.photoindex-flightline/v1", "CGEO-45", "CGEO-44", "CGEO-44"
    ):
        raise ValueError("wrong evidence chain")
    s, old = m["source"], p["source"]
    if (s["url"], s["node"], s["folder"]) != (
        old["url"], old["selected_node"], old["requested_folder"]
    ):
        raise ValueError("different archival node")
    a = p["acquisition"]
    if (s["sha256"], s["bytes"], s["dimensions"]) != (
        DIGEST, a["jpeg_bytes"], a["image_dimensions_pixels"]
    ) or s["sha256"] != a["jpeg_sha256"]:
        raise ValueError("unverified source image")
    i = m["inspection"]
    if i["date"] != "2026-11-14" or i["method"] != "manual visual reading of the hash-verified JPEG; no OCR":
        raise ValueError("method or date changed")
    for position, frame, box in [
        ("upper", "7157", [2940, 970, 3930, 1680]),
        ("lower", "7150", [1650, 3620, 2700, 4340]),
    ]:
        o = i[position]
        if (o["roll"], o["line"], o["printed_frame"], o["crop_pixels"]) != (
            "58", "X-NNI", frame, box
        ):
            raise ValueError("unverified line or endpoint label")
    inset = i["inset"]
    if (inset["title"], inset["area"], inset["hatched_sheet"], inset["crop_pixels"]) != (
        "INDEX TO SHEETS", "9", "6219", [2320, 0, 4000, 450]
    ):
        raise ValueError("unverified inset")
    if i["cartouche_range"] != "1964-1970" or p["printed_metadata"]["date_range_literal"] != "Date 1964-1970":
        raise ValueError("wrong printed date range")
    v = m["limitations"]
    for key in ("intermediate_frames_verified", "original_frames_acquired", "orbital_restriction"):
        if v[key] is not False:
            raise ValueError("unsupported assertion: " + key)
    for key in ("capture_dates", "flight_time", "datum", "georeferenced_footprint",
                "center_conde_1963", "reentry_point"):
        if v[key] is not None:
            raise ValueError("unverified coordinate or date: " + key)
    if "not full-sheet aerial coverage" not in v["scope"] or "does not exclude other campaigns" not in v["scope"]:
        raise ValueError("unsupported coverage assertion")
    if "roll 58" not in m["next_search"]:
        raise ValueError("source follow-up lost")
    return "CGEO45_CONTRACT_PASS"


def verify_image(path, m):
    raw = Path(path).read_bytes()
    if len(raw) != m["source"]["bytes"] or hashlib.sha256(raw).hexdigest() != DIGEST:
        raise ValueError("JPEG bytes not identical to CGEO-44")
    from PIL import Image
    with Image.open(path) as im:
        if im.format != "JPEG" or list(im.size) != m["source"]["dimensions"]:
            raise ValueError("image format/dimensions differ")
    return "CGEO45_JPEG_REPLAY_PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path)
    args = parser.parse_args()
    m = json.loads(MANIFEST.read_text())
    p = json.loads(PARENT.read_text())
    print(validate(m, p))
    if args.image:
        print(verify_image(args.image, m))


if __name__ == "__main__":
    main()
