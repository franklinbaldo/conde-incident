"""Verify 1963 Soviet observatory catalog holdings, never infer sensor data."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/soviet_1963_bibliographic_holdings_C241-L29.json"


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []

    def handle_data(self, word):
        self.words.append(word)


def issue_row(html, title):
    p = Text()
    p.feed(html)
    words = re.sub(r"\s+", " ", " ".join(p.words))
    index = words.find(title)
    if index < 0:
        return None
    nearby = words[index + len(title):index + len(title) + 250]
    found = re.search(r"\b1963\s+N(\d+)(?:-(\d+))?\b", nearby)
    if not found:
        return None
    start = int(found.group(1))
    end = int(found.group(2) or found.group(1))
    return list(range(start, end + 1)) if start <= end <= start + 50 else None


def validate(data):
    errors = []
    if data.get("schema") != "conde.soviet_1963_holdings/v1":
        errors.append("schema")
    if data.get("level") != "INSTITUTIONAL_LIBRARY_HOLDINGS_ONLY":
        errors.append("level")
    if data.get("verified_observations") != 0:
        errors.append("verified_observations")
    if data.get("orbital_constraint_activated") is not False:
        errors.append("orbital_constraint_activated")
    if data.get("library_contacted") is not False:
        errors.append("library_contacted")
    records = data.get("records", [])
    if len(records) != 2 or len({r.get("journal") for r in records}) != 2:
        errors.append("records")
    for r in records:
        rid = r.get("id", "?")
        if r.get("facsimile_read") is not False or r.get("issue_pdf_sha256") is not None:
            errors.append(rid + ":facsimile")
        if r.get("primary_observation_527_528_529") is not None:
            errors.append(rid + ":measurement")
        if r.get("year") != 1963 or r.get("http_status") != 200:
            errors.append(rid + ":date_or_http")
        if not re.fullmatch(r"[0-9a-f]{64}", str(r.get("sha256", ""))):
            errors.append(rid + ":catalog_sha")
        if not str(r.get("url", "")).startswith("https://mao.kiev.ua/"):
            errors.append(rid + ":url")
    return errors


def replay(data, directory):
    errors = []
    for r in data["records"]:
        raw = (directory / r["file"]).read_bytes()
        if len(raw) != r["bytes"] or hashlib.sha256(raw).hexdigest() != r["sha256"]:
            errors.append(r["id"] + ":catalog_integrity")
        if issue_row(raw.decode("utf-8"), r["journal"]) != r["issues"]:
            errors.append(r["id"] + ":holdings_row")
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html-dir", type=Path)
    a = p.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate(data)
    if a.html_dir:
        errors += replay(data, a.html_dir)
    if errors:
        raise SystemExit("FAIL " + ", ".join(errors))
    print("PASS catalog-only; " + ("exact HTML replay verified" if a.html_dir else "HTML replay NOT RUN"))
    print("No original issues or 527/528/529 observations were recovered.")


if __name__ == "__main__":
    main()
