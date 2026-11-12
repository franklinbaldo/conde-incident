#!/usr/bin/env python3
"""Inventory NCEP's public Office Notes index; never decode observations."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.error
import urllib.request

CATALOG_URL = "https://www.emc.ncep.noaa.gov/officenotes/FullTOC.html"
TARGETS = {
    16: ("Hydrostatic and Wind Check in the ADP Program", "1963"),
    20: ("Upper Air ADP Records Format", "1964"),
    22: ("ADP 3rd Word", "1964"),
    26: ("Structure of the NMC B3 Data Tape", "1968"),
}


class TableReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.current = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.current = []
        if tag == "td" and self.current is not None:
            self.cell = {"text": [], "links": []}
        if tag == "a" and self.cell is not None:
            self.cell["links"].extend(v for k, v in attrs if k == "href")

    def handle_data(self, data):
        if self.cell is not None:
            self.cell["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None and self.current is not None:
            self.current.append({
                "text": " ".join(" ".join(self.cell["text"]).split()),
                "links": self.cell["links"],
            })
            self.cell = None
        if tag == "tr" and self.current is not None:
            self.rows.append(self.current)
            self.current = None


def extract_notes(html: bytes) -> list[dict]:
    reader = TableReader()
    reader.feed(html.decode("utf-8", "replace"))
    notes = []
    found = set()
    for row in reader.rows:
        if len(row) < 4 or not row[0]["text"].isdigit():
            continue
        number = int(row[0]["text"])
        if number not in TARGETS:
            continue
        if number in found:
            raise ValueError(f"duplicate Office Note {number}")
        found.add(number)
        expected_title, expected_year = TARGETS[number]
        if expected_title not in row[3]["text"] or expected_year not in row[1]["text"]:
            raise ValueError(f"unexpected title/year for Office Note {number}")
        links = row[3]["links"]
        if len(links) != 1 or not links[0].endswith(".pdf"):
            raise ValueError(f"expected one PDF catalog link for Office Note {number}")
        notes.append({
            "number": number,
            "year_as_catalogued": row[1]["text"],
            "author_as_catalogued": row[2]["text"],
            "title_as_catalogued": row[3]["text"],
            "pdf_catalog_link": links[0],
            "pdf_downloaded": False,
            "pdf_sha256": None,
        })
    if found != set(TARGETS):
        raise ValueError(f"missing Office Notes {sorted(set(TARGETS) - found)}")
    return sorted(notes, key=lambda n: n["number"])


def probe(url: str) -> dict:
    """HTTP status or network error; never silently promote failed URL to PDF."""
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "Conde-archive-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return {"status": response.status,
                    "content_type": response.headers.get("Content-Type"),
                    "content_length": response.headers.get("Content-Length")}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "error": "HTTP error"}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"status": None, "error": type(exc).__name__,
                "detail": "unavailable endpoint / network error"}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--html", type=Path, help="offline HTML snapshot")
    cli.add_argument("--output", type=Path)
    cli.add_argument("--probe", action="store_true",
                     help="HEAD-check public PDF links; never contact people")
    args = cli.parse_args()
    if args.html:
        raw = args.html.read_bytes()
        status = "OFFLINE_SNAPSHOT"
        last_modified = None
    else:
        req = urllib.request.Request(CATALOG_URL,
                                     headers={"User-Agent": "Conde-archive-audit/1.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read()
            status = response.status
            last_modified = response.headers.get("Last-Modified")
    notes = extract_notes(raw)
    if args.probe:
        for note in notes:
            note["pdf_probe"] = probe(note["pdf_catalog_link"])
    out = {
        "id": "MET-NMC-NCEPON-20261112-01",
        "catalog": {
            "url": CATALOG_URL,
            "http_status": status,
            "byte_length": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "last_modified_header": last_modified,
        },
        "notes": notes,
        "observations_decoded": None,
        "decode_state": "NOT_RUN",
        "linked_pending_bridge": "research/constraints/nmc_y20175_pending_bridge.json",
        "documentation_not_tape": True,
        "physical_constraint": "NOT_ACTIVATED",
    }
    rendered = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
