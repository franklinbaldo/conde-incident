"""Audit a Kyiv scientific-library holdings record without promoting it to a satellite measurement."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import urllib.request

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/ukraine_bulletin32_holdings_C241_LONTRA_R61.json"
URL = "https://mao.kiev.ua/index.php/ua/gao-biblio-periodyka/sciencefilds-a-b"
SHA256 = "5ec7eeef7492fb0c4d135f6d5ae5f0378c7290fffd86d49d633da4e1f53e0480"

class _PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, text):
        self.parts.append(text)

def catalog_text(html_bytes):
    parser = _PlainText()
    parser.feed(html_bytes.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(parser.parts))

def check_holding_context(html_bytes):
    text = catalog_text(html_bytes)
    pattern = (r"Бюллетень станций оптического наблюдения ИСЗ"
               r".{0,320}?1962 N25-31\s+1963 N32-37\s+1964 N38-43")
    if not re.search(pattern, text):
        raise ValueError("Issue 32 is not confirmed in the 1963 holdings for the right serial")
    return True

def validate(data):
    if data.get("id") != "C241-LONTRA-R61" or data.get("evidence_class") != "INSTITUTIONAL_SERIAL_HOLDINGS_NOT_PRIMARY_FACSIMILE":
        raise ValueError("Wrong evidence identity or classification")
    c = data.get("catalog", {})
    expected = {"source_url":URL, "serial_title":"Бюллетень станций оптического наблюдения ИСЗ",
                "1962_holding":"N25-31", "1963_holding":"N32-37", "1964_holding":"N38-43",
                "verified_http_status":200, "verified_html_bytes":63640, "html_sha256":SHA256}
    if any(c.get(k) != v for k,v in expected.items()):
        raise ValueError("Institutional catalog locator or custody modified")
    if "Hash belongs only" not in c.get("custody_scope", "") or "not a scan" not in c.get("verification", ""):
        raise ValueError("Catalogue promoted to primary source")
    x = data.get("cross_catalog",{})
    if x.get("japan_nii_ncid") != "AA00566856" or x.get("verified_issue_32_held") is not True:
        raise ValueError("Japanese cross-catalog identity modified")
    if "not independent technical observations" not in x.get("interpretation",""):
        raise ValueError("Holdings conflated with observations")
    target = data.get("target",{})
    if target.get("soviet_bulletin_issue") != 32 or target.get("soviet_bulletin_year") != 1963:
        raise ValueError("Target bulletin identity altered")
    if target.get("link_to_target_article_status") != "BIBLIOGRAPHIC_CITATION_ONLY_NOT_IN_HOLDINGS_TEXT":
        raise ValueError("Article presence inferred from holdings")
    if target.get("primary_article_pages_known") is not False:
        raise ValueError("Original pagination not established")
    b = data.get("boundaries",{})
    for k in ("issue_32_facsimile_retrieved", "original_article_retrieved", "original_page_read",
              "station_identified_for_527_529", "institutional_contact_sent"):
        if b.get(k) is not False:
            raise ValueError("Unverified fact promoted: " + k)
    if b.get("independent_observations_norad_527_528_529") != [] or type(b.get("new_orbital_constraints")) is not int or b["new_orbital_constraints"] != 0:
        raise ValueError("A holdings catalog cannot add observational constraints")
    return True

def replay():
    req = urllib.request.Request(URL, headers={"User-Agent":"Mozilla/5.0 (Conde archival research)"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        status, raw = resp.status, resp.read(750_001)
    if status != 200 or len(raw) > 750_000:
        raise ValueError("Unexpected HTTP status or excessive response")
    check_holding_context(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(json.dumps({"http":status,"bytes":len(raw),"sha256":digest,
                      "snapshot_sha256_matches":digest == SHA256,"1963_issue_32_holding_confirmed":True}))
    return True

if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    if "--live" in sys.argv:
        replay()
    else:
        print("C241-LONTRA-R61: catalogue-only audit PASS (no sensor data)")
