"""Confirm ADS historical scanning index without claiming an article or an observation."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/ads_soviet_astronomy_scan_locator_C241_LONTRA_R59.json"

def validate(data):
    if data.get("id") != "C241-LONTRA-R59" or data.get("evidence_class") != "INSTITUTIONAL_DIGITIZED_SERIAL_RUN_INDEX":
        raise ValueError("Wrong evidence identity or class")
    source = data.get("catalogue", {})
    expected = {
        "institution": "Smithsonian Astrophysical Observatory / NASA Astrophysics Data System",
        "url": "https://adsabs.harvard.edu/abs_doc/fulltext_abbr.html",
        "serial": "Soviet Astronomy",
        "bibstem": "SvA..",
        "scanned_range": "v.1-37: 2/1957-12/1993",
        "http_status": 200,
        "html_bytes": 129845,
        "html_sha256": "74801612d982bec60b87af20512adcfb2906e3403d98058fd3eab5ecdc86ed37",
    }
    if any(source.get(k) != v for k,v in expected.items()):
        raise ValueError("Source identity or verified HTML changed")
    if "not scans of any volume" not in source.get("hash_scope", ""):
        raise ValueError("HTML hash scope was promoted to article")
    limits = data.get("inference_limits",{})
    if limits.get("english_volume_7_within_index_range") is not True:
        raise ValueError("Missing serial-range locator")
    for key in ("individual_1963_article_link_found","volume_7_issue_3_opened",
                "volume_7_issue_5_opened","original_russian_article_opened",
                "english_translation_article_opened","issue_month_crosswalk_verified",
                "report_1521678463_opened","independent_soviet_tracking_sensor",
                "contacted_institution"):
        if limits.get(key) is not False:
            raise ValueError("Unverified article, crosswalk, or observation promoted: "+key)
    if any(limits.get(k) is not None for k in ("original_article_author","original_article_pages","pdf_sha256")):
        raise ValueError("Unknown article metadata/hash invented")
    if limits.get("observations_norad_527_528_529") != [] or limits.get("new_orbital_constraints") != 0:
        raise ValueError("No orbital observations can be inferred from serial index")
    return True

if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("R59 ADS serial index: PASS (bibliographic route only)")
