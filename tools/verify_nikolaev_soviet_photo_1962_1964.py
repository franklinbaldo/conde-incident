#!/usr/bin/env python3
"""Audit 1962/1964 Soviet satellite-photo article locators without inventing 1963 data."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/nikolaev_soviet_photo_1962_1964_C241-L35.json"


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def validate(data, html_bytes=None):
    source = data["source"]
    assert data["schema"] == "conde.archival_periodical_locator/v1"
    assert data["id"] == "C241-L35"
    assert data["epistemic_level"] == "RETROSPECTIVE_BIBLIOGRAPHIC_LOCATOR_ONLY"
    assert source["source_kind"] == "RETROSPECTIVE_INSTITUTIONAL_PUBLICATION_INDEX"
    assert source["http_status"] == 200
    assert source["encoding"] == "windows-1251"
    assert source["bytes"] == 76869
    assert source["sha256"] == "9c26ed15ddea6963e2e2b28ef05278a7419635abd66e9e382dc396748da884f6"
    assert source["original_journal_facsimiles_retrieved"] is False
    assert data["cross_catalogue"]["issues_present_in_holdings"] == [25, 38, 42]
    assert data["cross_catalogue"]["journal_contents_read_from_this_catalogue"] is False
    assert data["requested_target_objects"] == [527, 528, 529]
    assert data["source_is_original_1963_instrumental_record"] is False
    assert data["asserts_1963_publication_absent"] is False
    assert data["target_specific_measurements_retrieved"] == 0
    assert data["orbital_constraint_activated"] is False
    assert data["archive_contacted"] is False
    refs = data["references"]
    assert len(refs) == 3
    assert [(r["year_of_publication"], r["journal_issue"]) for r in refs] == [(1962, 25), (1964, 38), (1964, 42)]
    assert refs[0]["printed_pages"] == "21-22"
    assert all(r["original_issue_read"] is False for r in refs)
    assert all(r["observation_epoch"] is None and r["satellite_identifier"] is None for r in refs)
    assert all(r["target_specific_astrometry_verified"] is False for r in refs)
    if html_bytes is not None:
        assert len(html_bytes) == source["bytes"], "source size changed"
        assert hashlib.sha256(html_bytes).hexdigest() == source["sha256"], "source digest changed"
        parser = TextOnly()
        parser.feed(html_bytes.decode("cp1251"))
        text = " ".join(" ".join(parser.parts).split())
        for token in (
            "1962 Бровенко В.Я.", "Определение оптического центра",
            "248 снимков", "№25", "с.21-22",
            "1964 Ивакина Т.Я., Федорова Р.Т.",
            "1964 Федорова Р.Т.", "Результаты фотографических наблюдений ИСЗ",
            "№38", "№42",
        ):
            assert token in text, "source missing quoted index token: " + token
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, help="original downloaded institution HTML (not committed)")
    args = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, args.html.read_bytes() if args.html else None)
    print("PASS: archival locator without orbital promotion" + ("; CP1251 HTML SHA replay" if args.html else ""))
