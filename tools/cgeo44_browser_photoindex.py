"""CGEO-44: acquire the genuine MI-1850 image using real browser state.

An AJAX POST assembled without the Telerik scripts silently loads image 0335.
This workflow requires SAME-RESPONSE browser client state and exact JPEG bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo44_mi1850_photoindex.json"
SOURCE_URL = "https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF&pasta=1850"
LABEL = "1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI"
JPEG_SHA = "45d72dff84520bb387d5b8ce7c5a8f4c9361457841341b2c21016e992c0fef79"
JPEG_SIZE = 957893
DIMENSIONS = [4355, 4350]


def verify_manifest(data: dict) -> str:
    if data.get("schema") != "conde.cgeo.photoindex-acquisition/v1" or data.get("id") != "CGEO-44":
        raise ValueError("wrong contract")
    src = data["source"]
    if (src["url"], src["requested_folder"], src["selected_node"], src["selected_folder_label"]) != (
            SOURCE_URL, "1850", "680", LABEL):
        raise ValueError("source identity changed")
    a = data["acquisition"]
    if (a["jpeg_sha256"], a["jpeg_bytes"], a["image_dimensions_pixels"]) != (JPEG_SHA, JPEG_SIZE, DIMENSIONS):
        raise ValueError("JPEG integrity declaration changed")
    if not (a["independent_sessions_same_jpeg_sha256"] and a["image_bytes_saved_outside_repository"]
            and a["source_cache_path_varies_per_session"] and a["repeat_count"] >= 2):
        raise ValueError("unverified source or improperly stored bytes")
    printed = data["printed_metadata"]
    if printed["date_range_literal"] != "Date 1964-1970" or printed["frame_specific_capture_dates"] is not None:
        raise ValueError("invented frame date")
    if printed["survey_1963_proven"] is not False:
        raise ValueError("post-1963 print does not prove 1963 survey")
    for key, value in (("scale_of_photography_literal", "Scale of Photography 1:60,000"),
                       ("scale_of_index_literal", "Scale of Index 1:180,000"),
                       ("altitude_literal", "ALT. 30,000' ASL")):
        if printed[key] != value:
            raise ValueError("printed legend changed")
    result = data["interpretation"]
    if (not result["index_image_acquired"] or result["individual_original_aerial_frames_acquired"] is not False
            or result["historic_center_conde_1963_geometry"] is not None
            or result["event_reentry_position"] is not None
            or result["orbital_constraint_activated"] is not False):
        raise ValueError("index is not 1963 geometry/orbital proof")
    return "CGEO44_OFFLINE_CONTRACT_PASS"


def verify_response(data: dict, state: dict, url: str, jpeg: bytes, dimensions: list[int],
                    status: int, content_type: str) -> str:
    verify_manifest(data)
    if state.get("folder") != LABEL or str(state.get("selected_value")) != "680":
        raise ValueError("Telerik folder/node mismatch")
    if str(state.get("hidden_pag")) != "680" or not state.get("loaded"):
        raise ValueError("page index or JPEG load wrong")
    src = state.get("img_src")
    if not isinstance(src, str) or not re.fullmatch(
            r"cache/[0-9]+/I0000680-0-0-[0-9]{6}-[0-9]{6}-[0-9]{6}-[0-9]{6}\.JPG", src):
        raise ValueError("image source not tied to node 680")
    if urljoin("https://acervo.sgb.gov.br/DocReader/", src) != url:
        raise ValueError("network JPEG differs from DOM image")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "acervo.sgb.gov.br":
        raise ValueError("wrong JPEG host")
    if status != 200 or content_type.lower().split(";")[0] not in ("image/jpeg", "image/jpg"):
        raise ValueError("wrong JPEG HTTP response")
    if dimensions != DIMENSIONS or len(jpeg) != JPEG_SIZE:
        raise ValueError("wrong dimensions or size")
    if hashlib.sha256(jpeg).hexdigest() != JPEG_SHA:
        raise ValueError("JPEG digest mismatch")
    if jpeg[:3] != b"\xff\xd8\xff":
        raise ValueError("not JPEG")
    return "CGEO44_BROWSER_SOURCE_REPLAY_PASS"


def live_capture(data: dict, output_dir: Path) -> str:
    from playwright.sync_api import sync_playwright
    from PIL import Image

    photos: list[tuple[str, bytes, int, str, list[int]]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get("CGEO44_BROWSER_EXECUTABLE"))
        try:
            context = browser.new_context(viewport={"width": 4700, "height": 4450}, locale="pt-BR")
            page = context.new_page()

            def on_response(r):
                if "/I0000680-" not in r.url:
                    return
                content = r.body()
                picture = Image.open(io.BytesIO(content))
                photos.append((r.url, content, r.status, r.headers.get("content-type", ""), list(picture.size)))

            page.on("response", on_response)
            page.goto(SOURCE_URL, wait_until="domcontentloaded", timeout=65000)
            state = {}
            for _ in range(12):
                page.wait_for_timeout(2000)
                state = page.evaluate("""() => {
                    const tree = window.$find && $find('T1');
                    const node = tree && tree.get_selectedNode();
                    const img = document.getElementById('DocumentoImg');
                    return {
                        folder: document.getElementById('PastaTxt')?.innerText,
                        selected_value: node && node.get_value(),
                        hidden_pag: document.getElementById('hPagFis')?.value,
                        img_src: img?.getAttribute('src'),
                        loaded: img?.complete && img.naturalWidth > 0
                    };
                }""")
                if state.get("loaded") and photos:
                    break
            if len(photos) != 1:
                raise ValueError(f"expected one image response, got {len(photos)}")
            url, raw, status, kind, size = photos[0]
            verdict = verify_response(data, state, url, raw, size, status, kind)
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "cgeo44_mi1850.jpg").write_bytes(raw)
            observation = {
                "source": SOURCE_URL,
                "resource_url": url,
                "client_state": state,
                "image_sha256": hashlib.sha256(raw).hexdigest(),
                "image_bytes": len(raw),
                "dimensions_pixels": size,
                "verdict": verdict
            }
            (output_dir / "cgeo44_capture.json").write_text(
                json.dumps(observation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return verdict
        finally:
            browser.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--output-dir", type=Path, default=Path("/tmp/cgeo44-acquisition"))
    args = p.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(verify_manifest(data))
    if args.live:
        print(live_capture(data, args.output_dir))


if __name__ == "__main__":
    main()
