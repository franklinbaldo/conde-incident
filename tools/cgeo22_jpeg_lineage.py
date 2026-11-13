"""CGEO-22: deterministic JPEG stream comparison for historic Conde galleries."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo22_jpeg_scan_lineage.json"
SOURCES = {
    "blogger_2012": (316900, "b0c17c9bae3a4397d1572b300b26967e703fe1c0bdb05c624819dd34c16abde3"),
    "wordpress_2014": (321338, "233264fed3b4475e6ea3aae5efea521f56fe9a1fc8ee6d9c0c602787653ef154"),
}
SCAN_SHA = "c8f9c79af818e9dbcc0114b01594f7d28695ba8a5029665b4d9c804c5ae76cf4"
SCAN_BYTES = 316379
HEADER_SHA = "3a44659c42cdd41305172f3ddb31968a2643ffec4dcd845e3cde3d76695ad6b8"
APP1_SIZES = (106, 4544)
IMAGE_DIMENSIONS = (1600, 1163)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exif_flags(payload: bytes) -> tuple[int | None, bool, bool]:
    """Inspect orientation, original-capture date and GPS EXIF tags."""
    if not payload.startswith(b"Exif\x00\x00"):
        raise ValueError("APP1 is not EXIF")
    tiff = payload[6:]
    if tiff[:2] not in (b"II", b"MM"):
        raise ValueError("invalid TIFF byte order")
    endian = "<" if tiff[:2] == b"II" else ">"

    def u16(pos: int) -> int:
        return struct.unpack_from(endian + "H", tiff, pos)[0]

    def u32(pos: int) -> int:
        return struct.unpack_from(endian + "I", tiff, pos)[0]

    if u16(2) != 42:
        raise ValueError("invalid TIFF magic")

    def ifd(pos: int) -> dict[int, tuple[int, int, int]]:
        if pos <= 0 or pos + 2 > len(tiff):
            raise ValueError("invalid IFD offset")
        count = u16(pos)
        if pos + 2 + count * 12 + 4 > len(tiff):
            raise ValueError("truncated IFD")
        out = {}
        for j in range(count):
            off = pos + 2 + j * 12
            out[u16(off)] = (u16(off + 2), u32(off + 4), u32(off + 8))
        return out

    main = ifd(u32(4))
    orientation = None
    if 0x0112 in main:
        entry = main[0x0112]
        if entry[:2] != (3, 1):
            raise ValueError("unexpected orientation encoding")
        orientation = entry[2] & 0xffff if endian == "<" else entry[2] >> 16
    exif = ifd(main[0x8769][2]) if 0x8769 in main else {}
    return orientation, 0x9003 in exif, 0x8825 in main


def parse_jpeg(source: bytes) -> dict:
    """Allow one baseline scan; reject extra scans, ambiguous markers and trailing bytes."""
    if not source.startswith(b"\xff\xd8"):
        raise ValueError("missing SOI")
    cursor = 2
    non_exif = bytearray()
    app1 = []
    frame = None
    scan = None
    while cursor < len(source):
        if source[cursor] != 0xff:
            raise ValueError("invalid marker boundary")
        cursor += 1
        while cursor < len(source) and source[cursor] == 0xff:
            cursor += 1
        if cursor >= len(source):
            raise ValueError("truncated marker")
        marker = source[cursor]
        cursor += 1
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            raise ValueError("unexpected standalone marker")
        if cursor + 2 > len(source):
            raise ValueError("truncated segment length")
        length = int.from_bytes(source[cursor:cursor + 2], "big")
        if length < 2 or cursor + length > len(source):
            raise ValueError("invalid segment length")
        segment = source[cursor - 2:cursor + length]
        payload = source[cursor + 2:cursor + length]
        cursor += length
        if marker == 0xE1:
            app1.append(payload)
        else:
            non_exif.extend(segment)
        if marker == 0xC0:
            if len(payload) < 6 or payload[0] != 8:
                raise ValueError("unsupported SOF0")
            frame = (int.from_bytes(payload[3:5], "big"), int.from_bytes(payload[1:3], "big"))
        if marker == 0xDA:
            if frame is None:
                raise ValueError("scan without baseline frame")
            start = cursor
            while cursor + 1 < len(source):
                if source[cursor] != 0xff:
                    cursor += 1
                    continue
                nxt = source[cursor + 1]
                if nxt == 0x00 or 0xD0 <= nxt <= 0xD7:
                    cursor += 2
                    continue
                if nxt != 0xD9:
                    raise ValueError("another scan or marker inside entropy")
                if cursor + 2 != len(source):
                    raise ValueError("trailing bytes after EOI")
                scan = source[start:cursor]
                break
            break
    if scan is None or len(app1) != 1:
        raise ValueError("missing single scan or EXIF")
    orientation, date_original, gps_pointer = exif_flags(app1[0])
    return {
        "dimensions_px": list(frame),
        "non_app1_header_sha256": digest(non_exif),
        "scan_sha256": digest(scan),
        "scan_bytes": len(scan),
        "exif_payload_bytes": len(app1[0]),
        "orientation": orientation,
        "date_original_present": date_original,
        "gps_pointer_present": gps_pointer,
    }


def compare(first: bytes, second: bytes) -> dict:
    a, b = parse_jpeg(first), parse_jpeg(second)
    for name in ("dimensions_px", "non_app1_header_sha256", "scan_sha256", "scan_bytes",
                 "orientation", "date_original_present", "gps_pointer_present"):
        if a[name] != b[name]:
            raise ValueError("image or render-related metadata differs: " + name)
    if a["orientation"] is not None or a["date_original_present"] or a["gps_pointer_present"]:
        raise ValueError("unexpected capture metadata or EXIF orientation")
    if a["exif_payload_bytes"] == b["exif_payload_bytes"]:
        raise ValueError("source EXIF length anomaly")
    return {"first": a, "second": b, "same_encoded_image": True, "same_complete_file": first == second}


def validate_contract(data: dict) -> None:
    if data["schema"] != "conde.gis.jpeg-entropy-lineage/v1" or data["id"] != "CGEO-22":
        raise ValueError("contract mismatch")
    if data["source_family_ids"] != ["CGEO-19", "CGEO-14"]:
        raise ValueError("lost source lineage")
    for name, (size, sha256) in SOURCES.items():
        src = data["sources"][name]
        if (src["byte_size"], src["sha256"]) != (size, sha256) or not src["url"].startswith("https://"):
            raise ValueError("source file identity drift")
    r = data["result"]
    if r["non_app1_header_sha256"] != HEADER_SHA:
        raise ValueError("non-EXIF JPEG header fingerprint drift")
    if (r["scan_sha256"], r["scan_bytes"], r["dimensions_px"], r["exif_payload_bytes"]) != (
            SCAN_SHA, SCAN_BYTES, list(IMAGE_DIMENSIONS), list(APP1_SIZES)):
        raise ValueError("replay fingerprint drift")
    for name in ("same_encoded_image", "identical_non_APP1_JPEG_segments"):
        if r[name] is not True:
            raise ValueError("identity evidence drift")
    for name in ("whole_files_identical", "two_independent_photo_captures",
                 "direction_of_copying_proven", "original_capture_date_proven",
                 "verified_original_negative", "rights_to_redistribute_verified",
                 "other_two_2012_2014_photo_pairs_compared"):
        if r[name] is not False:
            raise ValueError("unsupported source-history assertion: " + name)
    geo = data["geospatial"]
    if geo["can_constrain_orbital_reentry"] is not False:
        raise ValueError("misuse as orbital constraint")
    for name in ("historic_center_1963", "camera_point_1959", "point_of_impact",
                 "crs", "horizontal_uncertainty_m"):
        if geo[name] is not None:
            raise ValueError("fabricated geospatial position: " + name)


def verify(first_path: Path, second_path: Path, contract: dict) -> dict:
    first, second = first_path.read_bytes(), second_path.read_bytes()
    for name, value in (("blogger_2012", first), ("wordpress_2014", second)):
        if (len(value), digest(value)) != SOURCES[name]:
            raise ValueError("original JPEG SHA256 mismatch: " + name)
    result = compare(first, second)
    a, b = result["first"], result["second"]
    if a["non_app1_header_sha256"] != HEADER_SHA:
        raise ValueError("non-EXIF JPEG header fingerprint mismatch")
    if (a["scan_sha256"], a["scan_bytes"], a["dimensions_px"]) != (
            SCAN_SHA, SCAN_BYTES, list(IMAGE_DIMENSIONS)):
        raise ValueError("entropy fingerprint mismatch")
    if (a["exif_payload_bytes"], b["exif_payload_bytes"]) != APP1_SIZES:
        raise ValueError("metadata payload size mismatch")
    validate_contract(contract)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="CGEO-22 JPEG lineage from real source bytes")
    parser.add_argument("--blogger-jpeg", type=Path)
    parser.add_argument("--wordpress-jpeg", type=Path)
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    if (args.blogger_jpeg is None) != (args.wordpress_jpeg is None):
        parser.error("supply both real JPEG files or neither")
    if args.blogger_jpeg:
        replay = verify(args.blogger_jpeg, args.wordpress_jpeg, contract)
        print(json.dumps({"status": "VERIFIED_REAL_BYTES",
                          "scan_sha256": replay["first"]["scan_sha256"],
                          "same_encoded_image": replay["same_encoded_image"],
                          "same_complete_file": replay["same_complete_file"]}))
    else:
        print("CGEO-22 OFFLINE_CONTRACT_PASS; no JPEG download or bytes replayed")


if __name__ == "__main__":
    main()
