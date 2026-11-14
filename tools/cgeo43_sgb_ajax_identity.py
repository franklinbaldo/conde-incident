"""CGEO-43: reject image evidence when SGB AJAX silently changes folder.

No online or historical-source claims from this validator: it checks pinned, source-
derived excerpts and fail-closed image identity. Raw HTTP bodies and JPEG are kept
outside Git because of size and redistribution rights.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo43_sgb_ajax_folder_identity.json"
EXACT_DEFAULT_LABEL = "0335 Projeto USAF 63-32 - área A: SA.22-X-B-V"
EXACT_JPEG_SHA = "21acae03404dae880b40c69565c841bf7a3cdf1dc392c11bfe1cbe83828a4bd0"


def parse_excerpt(data: bytes) -> dict[str, str | bool]:
    text = data.decode("utf-8")
    if text.count("\n") != 3:
        raise ValueError("expected exactly three pinned observation lines")
    matches = {}
    for key in ("PastaTxt", "_selectedValue", "DocumentoImg"):
        found = re.findall(r"^" + re.escape(key) + r": (.+)$", text, re.M)
        if len(found) != 1:
            raise ValueError(f"missing or ambiguous {key}")
        matches[key] = found[0]
    if not re.fullmatch(r"[0-9]+", matches["_selectedValue"]):
        raise ValueError("non-numeric selected value")
    tag = matches["DocumentoImg"]
    if not re.fullmatch(r'<img id="DocumentoImg"[^<>]*/>', tag):
        raise ValueError("wrong image tag")
    matches["has_src"] = re.search(r"\bsrc\s*=", tag) is not None
    return matches


def compare_pair(before: dict, after: dict) -> bool:
    """Return true only when the AJAX folder really matches the selected folder."""
    if before["has_src"]:
        raise ValueError("selected GET is not the expected source state")
    if not after["has_src"]:
        return False
    return (before["PastaTxt"] == after["PastaTxt"]
            and before["_selectedValue"] == after["_selectedValue"])


def verify(manifest: dict, loader) -> str:
    if manifest["id"] != "CGEO-43" or len(manifest["probes"]) != 2:
        raise ValueError("wrong contract or incomplete controls")
    if manifest["source"] != "https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF":
        raise ValueError("untrusted source")
    img = manifest["image_response_observed"]
    if img["sha256"] != EXACT_JPEG_SHA or not img["same_digest_across_two_requests"]:
        raise ValueError("unexpected cached image")
    if img["attribution"] != "FOLDER_0335_ONLY" or img["original_source_photoindex_Mi1850_acquired"] is not False:
        raise ValueError("unearned image attribution")
    if manifest["historical_center_geometry"] is not None or manifest["event_position_1963"] is not None:
        raise ValueError("invented historical geometry")
    if manifest["can_constrain_orbital_reentry"] is not False:
        raise ValueError("unearned orbital inference")
    for probe in manifest["probes"]:
        parts = []
        for name in ("pre_selection", "ajax"):
            entry = probe[name]
            raw = loader(entry["file"])
            if hashlib.sha256(raw).hexdigest() != entry["excerpt_sha256"]:
                raise ValueError("source-derived excerpt SHA mismatch")
            parsed = parse_excerpt(raw)
            if parsed["PastaTxt"] != entry["label"] or parsed["_selectedValue"] != entry["value"]:
                raise ValueError("response identity differs from manifest")
            parts.append(parsed)
        before, after = parts
        if probe["requested_pasta"] not in ("1850", "1851"):
            raise ValueError("unexpected independent control")
        if not before["PastaTxt"].startswith(probe["requested_pasta"] + " Projeto USAF 63-32"):
            raise ValueError("GET selected the wrong folder")
        if after["PastaTxt"] != EXACT_DEFAULT_LABEL or after["_selectedValue"] != "1":
            raise ValueError("documented fallback not reproduced")
        if compare_pair(before, after):
            raise ValueError("unsafe image attribution falsely succeeded")
    return "CGEO43_FALLBACK_FALSE_ATTRIBUTION_BLOCKED"


def main() -> None:
    obj = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(verify(obj, lambda path: (ROOT / path).read_bytes()))


if __name__ == "__main__":
    main()
