#!/usr/bin/env python3
"""Audit scanned 1958 IBGE Conde-BA pages and reproducible derivative crop hashes.

Default mode checks manifest semantics offline. --pdf independently replays the
original full-file SHA256, page count, metadata and eight grayscale PNG crops.
A crop hash is NOT the hash of a historic photograph or source JPEG.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "research/geo/ibge_1958_conde_photo_custody.json"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_manifest(data: dict) -> int:
    assert data["schema"] == "conde.ibge1958-conde-facsimile-custody/v1"
    assert data["id"] == "LON-IBGE1958-CONDE-01"
    source = data["source"]
    assert source["institution"] == "IBGE" and source["print_year"] == 1958
    assert source["pdf_size_bytes"] == 72579243
    assert source["pdf_page_count"] == 398
    assert SHA_RE.fullmatch(source["pdf_sha256"])
    assert source["source_url"].startswith("https://biblioteca.ibge.gov.br/")
    assert [(p["pdf_page"], p["printed_page"]) for p in source["inspected_pages"]] == [
        (180, 185), (181, 186), (182, 187), (183, 188)]
    photos = data["photos"]
    assert data["photo_count"] == len(photos) == 8
    assert len({p["id"] for p in photos}) == 8
    expected_counts = {181: 3, 182: 3, 183: 2}
    actual_counts = {page: sum(p["pdf_page"] == page for p in photos) for page in expected_counts}
    assert actual_counts == expected_counts
    assert data["method"]["visual_inspection"]
    for p in photos:
        assert p["printed_page"] - p["pdf_page"] == 5
        assert p["pdf_page"] in expected_counts
        assert len(p["caption_visually_inspected"]) >= 12
        assert p["caption_transcription"] == "normalized from facsimile"
        assert all(p[k] is None for k in ("capture_date", "photographer", "individual_camera_location"))
        assert p["georeferenced"] is False
        assert SHA_RE.fullmatch(p["crop_png_sha256"])
        x0, y0, x1, y1 = p["rect_pt"]
        assert 0 <= x0 < x1 <= 675 and 0 <= y0 < y1 <= 961
        assert p["render_size_px"] == [2 * (x1 - x0), 2 * (y1 - y0)]
    limits = data["epistemic_limits"]
    for key in ("document_date_is_photo_date", "photos_are_1963_observations",
                "can_locate_historic_buildings_precisely", "can_constrain_reentry"):
        assert limits[key] is False
    assert limits["status"] == "VISUALLY_VERIFIED_PHOTO_CAPTIONS_NO_GEOREFERENCE"
    return len(photos)


def sha256_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            count += len(chunk)
            digest.update(chunk)
    return count, digest.hexdigest()


def replay_pdf(data: dict, path: Path) -> list[str]:
    # Deliberate optional dependency: offline unit tests need no PDF or PyMuPDF.
    import fitz
    assert fitz.VersionBind == "1.26.7", "Pin PyMuPDF for byte-identical derivative PNGs"
    source = data["source"]
    size, checksum = sha256_file(path)
    assert (size, checksum) == (source["pdf_size_bytes"], source["pdf_sha256"])
    with fitz.open(path) as document:
        assert document.page_count == source["pdf_page_count"]
        assert document.metadata["creationDate"] == source["pdf_creation_metadata"]
        assert document.metadata["modDate"] == source["pdf_modification_metadata"]
        matches = []
        for p in data["photos"]:
            page = document[p["pdf_page"] - 1]
            assert page.rect.width >= 670 and page.rect.height >= 950
            assert len(page.get_images(full=True)) == 1  # one scanned page image
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2), clip=fitz.Rect(p["rect_pt"]),
                colorspace=fitz.csGRAY, alpha=False)
            assert [pixmap.width, pixmap.height] == p["render_size_px"]
            digest = hashlib.sha256(pixmap.tobytes(output="png")).hexdigest()
            assert digest == p["crop_png_sha256"], p["id"] + ": crop bytes mismatch"
            matches.append(p["id"])
    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--pdf", type=Path, help="full original IBGE PDF for replay")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    count = validate_manifest(data)
    result = {"manifest": "PASS", "photos": count, "pdf_replay": "NOT_RUN"}
    if args.pdf:
        result["photos_replayed"] = replay_pdf(data, args.pdf)
        result["pdf_replay"] = "PASS"
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
