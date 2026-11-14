"""Audit CiNii serial holdings without promoting catalogue entries to orbital data."""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import urllib.request

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/japan_bulletin32_issues_C241_LONTRA_R62.json"
URL = "https://ci.nii.ac.jp/ncid/AA00566856"
HASH = "da7b7e445ccaf5569bccbb42809f9da471318cebebe6d713ec0deb0a08c31034"
COVERAGE = {
    "kyoto": ("32-59", (32, 33, 34, 35, 36, 37)),
    "naoj": ("1-53, 56-59", (32, 33, 34, 35, 36, 37)),
    "mizusawa": ("32-52, 53(1), 54-59", (32, 33, 34, 35, 36, 37)),
    "nipr": ("3-6, 9-13, 19-20, 23-33, 36-39, 41-46, 49-54, 56", (32, 33, 36, 37)),
    "tohoku": ("32-59", (32, 33, 34, 35, 36, 37)),
}


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, text):
        self.parts.append(text)


def validate(data):
    if data.get("id") != "C241-LONTRA-R62" or data.get("evidence_class") != "NATIONAL_AGGREGATE_HOLDINGS_NOT_FACSIMILE":
        raise ValueError("evidence type changed")
    p = data.get("provenance", {})
    for k, value in {"url": URL, "ncid": "AA00566856", "retrieval_status": 200,
                     "retrieved_html_bytes": 54342, "html_sha256": HASH}.items():
        if p.get(k) != value:
            raise ValueError("catalogue identity or snapshot custody changed: " + k)
    if p.get("exact_title_nii") != "Бюллетень Станции оптического наблюдения искусственных спутников Земли":
        raise ValueError("CiNii title altered")
    if p.get("exact_title_kyiv") != "Бюллетень станций оптического наблюдения ИСЗ":
        raise ValueError("Kyiv title altered")
    if p.get("equivalence_status") != "UNRESOLVED_TITLE_VARIANT_CHECK_ORIGINAL_TITLE_PAGE":
        raise ValueError("title equivalence promoted without primary source")
    if "HTML response only" not in p.get("hashed_object", ""):
        raise ValueError("catalogue hash promoted to source checksum")
    h = data.get("holdings", [])
    if len(h) != len(COVERAGE) or {x.get("id") for x in h} != set(COVERAGE):
        raise ValueError("institution coverage differs")
    for item in h:
        coverage, expected_issues = COVERAGE[item["id"]]
        if item.get("coverage") != coverage or item.get("issues_1963") != list(expected_issues):
            raise ValueError("holdings modified: " + item["id"])
        if not item.get("native") or not item.get("library"):
            raise ValueError("lost library provenance")
    derived = {str(n): sum(n in x["issues_1963"] for x in h) for n in range(32, 38)}
    if data.get("by_issue_reported_holder_count") != derived:
        raise ValueError("per-issue holdings count does not reconcile")
    req = data.get("ready_but_not_sent_request", {})
    if req.get("contact_sent") is not False or req.get("target_issues") != list(range(32, 38)):
        raise ValueError("request status or scope promoted")
    b = data.get("boundaries", {})
    for k in ("scan_or_issue_contents_accessed", "article_original_verified",
              "author_or_pages_from_original_verified"):
        if b.get(k) is not False:
            raise ValueError("unread source promoted: " + k)
    if b.get("independent_observations_norad_527_528_529") != [] or b.get("new_orbital_constraints") != 0:
        raise ValueError("no observed 527–529 data in catalogue")
    return True


def check_html(raw, data):
    p = data["provenance"]
    if len(raw) != p["retrieved_html_bytes"] or hashlib.sha256(raw).hexdigest() != p["html_sha256"]:
        raise ValueError("catalogue snapshot digest mismatch")
    parser = PlainText()
    parser.feed(raw.decode("utf-8"))
    plain = re.sub(r"\s+", " ", " ".join(parser.parts))
    if p["exact_title_nii"] not in plain:
        raise ValueError("CiNii serial title absent")
    for item in data["holdings"]:
        pos = plain.find(item["native"])
        if pos < 0 or item["coverage"] not in plain[pos:pos + 180]:
            raise ValueError("reported holding not in the named library context: " + item["id"])
    return True


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    validate(data)
    if "--live" in sys.argv[1:]:
        request = urllib.request.Request(URL, headers={"User-Agent": "Lontra-archival-custody/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise ValueError("catalogue HTTP status not 200")
            check_html(response.read(), data)
    print("C241-LONTRA-R62 PASS: five aggregated holdings, 1963 issues 32–37; zero observations")


if __name__ == "__main__":
    main()
