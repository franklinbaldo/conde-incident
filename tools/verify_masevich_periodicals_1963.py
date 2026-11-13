#!/usr/bin/env python3
"""Verify contemporary Soviet-periodical pointers without treating them as astrometry."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/masevich_periodicals_1963_C241-L34.json"

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []
    def handle_data(self, data):
        self.words.append(data)

def _verify_asset(payload, expected, image=False):
    assert len(payload) == expected["bytes"], "byte length mismatch"
    assert hashlib.sha256(payload).hexdigest() == expected["sha256"], "hash mismatch"
    if image:
        assert payload[:4] == b"RIFF" and payload[8:12] == b"WEBP", "not WebP"
        assert int.from_bytes(payload[4:8], "little") + 8 == len(payload), "WebP RIFF size mismatch"

def validate(data, html=None, page006=None, page007=None):
    assert data["schema"] == "conde.contemporary_bibliographic_locator/v1"
    assert data["id"] == "C241-L34"
    assert data["as_of"] == "2026-11-13"
    assert data["target_objects"] == [527, 528, 529]
    s = data["source"]
    assert s["kind"] == "CONTEMPORARY_1963_PRINT_PREFACE_THIRD_PARTY_SCAN"
    assert s["russian_preface_date"] == "1963-02"
    assert s["russian_edition_year"] == 1963
    assert "third-party" in s["imprint_status"].lower()
    assert s["source_authentication"] == "THIRD_PARTY_PAGE_IMAGES_VISUALLY_INSPECTED_NOT_MASTER_AUTHENTICATED"
    assert s["landing_http_status"] == 200
    assert s["landing_html_bytes"] > 0 and len(s["landing_html_sha256"]) == 64
    pages = s["images"]
    assert len(pages) == 2
    assert [p["viewer_page"] for p in pages] == [6, 7]
    assert [p["printed_page"] for p in pages] == [None, 6]
    assert [p["format"] for p in pages] == ["WebP", "WebP"]
    assert all(p["width"] == 957 and p["height"] == 1500 and p["http_status"] == 200 for p in pages)
    assert all(p["bytes"] > 0 and len(p["sha256"]) == 64 and p["url"].startswith("https://djvu.online/jpg2/") for p in pages)
    assert [p["title"] for p in data["bibliography"]] == [
        "Искусственные спутники Земли",
        "Бюллетень станций оптических наблюдений искусственных спутников",
    ]
    assert all(p["catalog_or_original_volume_retrieved"] is False for p in data["bibliography"])
    l = data["interpretive_limits"]
    for k in ("february_1963_preface_does_not_cover_november_1963", "no_facsimile_of_bulletin_issue_retrieved",
              "contemporaneous_editorial_reference_only", "publication_independence_not_established"):
        assert l[k] is True, k
    for k in ("station_ephemeris_or_tle_record_found", "independent_physical_observation",
              "orbital_constraint_activated", "archive_contacted"):
        assert l[k] is False, k
    assert l["target_specific_primary_measurements"] == 0
    assert l["observed_objects_identified_in_pages"] == []
    assert data["epistemic_level"] == "1963_CONTEMPORARY_BIBLIOGRAPHIC_REFERENCE_ONLY"
    if html is not None:
        expected = {"bytes":s["landing_html_bytes"], "sha256":s["landing_html_sha256"]}
        _verify_asset(html,expected)
        parser = TextOnly()
        parser.feed(html.decode("utf-8"))
        plain = " ".join(" ".join(parser.words).split())
        for term in ("Масевич", "Февраль", "1963", "Бюллетень станций", "совет АН СССР"):
            assert term in plain, f"HTML lacks indexed term: {term}"
    if page006 is not None:
        _verify_asset(page006, pages[0], image=True)
    if page007 is not None:
        _verify_asset(page007, pages[1], image=True)
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path)
    ap.add_argument("--page006", type=Path)
    ap.add_argument("--page007", type=Path)
    args = ap.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, args.html.read_bytes() if args.html else None,
             args.page006.read_bytes() if args.page006 else None,
             args.page007.read_bytes() if args.page007 else None)
    print("PASS: 1963 bibliography custody and no orbital promotion"
          + ("; original downloaded bytes replayed" if all((args.html,args.page006,args.page007)) else ""))
