#!/usr/bin/env python3
"""Verify memoir custody without promoting AFU negatives to 1963 observations."""
import argparse
import hashlib
from html import unescape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/zvenigorod_afu_memoir_route_C241-LONTRA-R35.json"
DIGEST = "3eef0389a2c752cf52803965a4e4a13e2ea12699b7f2129fbe98f6aa841a057d"
PHRASES = ("С мая 2007 г.", "негативов АФУ", "Международной виртуальной обсерватории", "1963 г")

def validate(doc, raw=None):
    assert doc["schema"] == "conde.archival_retro_memoir_route/v1"
    assert doc["id"] == "C241-LONTRA-R35"
    s = doc["source"]
    assert s["url"] == "https://www.sai.msu.ru/EAAS/rus/doc/MEM-12.htm"
    assert s["http_status"] == 200 and s["tls_certificate_validated"] is True
    assert (s["byte_length"], s["sha256"]) == (613158, DIGEST)
    assert (s["server_charset"], s["html_meta_charset"], s["effective_decoding"]) == ("koi8-r", "windows-1251", "koi8-r")
    assert s["source_form"] == "retrospective_first_person_memoir_on_university_site"
    assert len(s["historical_claims"]) == 3
    assert s["historical_claims"][0]["date"] == "1963"
    assert s["historical_claims"][1]["date"] == "2007-05"
    assert all(v["independent_target_measurement"] is False for v in s["historical_claims"])
    questions = doc["open_questions"]
    assert set(questions) == {"survival_as_of_2026", "negative_inventory_identifier",
        "dates_of_original_photographs", "covers_november_1963",
        "covers_norad_527_528_529", "modern_custodian"}
    assert all(v is None for v in questions.values())
    assert doc["status"] == "VERIFIED_MEMOIR_BYTES_ARCHIVE_REFERENCE_NOT_ORIGINAL_1963_OBSERVATION"
    assert doc["observables"] == {"target_ids":[527,528,529],
        "independent_measurements":0, "orbital_constraints_activated":0}
    assert doc["outreach_sent"] is False
    if raw is not None:
        assert len(raw) == 613158 and hashlib.sha256(raw).hexdigest() == DIGEST, "raw source bytes differ"
        assert b"charset=windows-1251" in raw.lower(), "HTML charset metadata missing"
        page = unescape(re.sub(r"<[^>]*>", " ", raw.decode("koi8-r")))
        page = re.sub(r"\s+", " ", page)
        assert all(p in page for p in PHRASES), "historical text missing"
    return True

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--html", type=Path)
    args = p.parse_args()
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")),
             args.html.read_bytes() if args.html else None)
    print("PASS: memoir bytes / 2007 AFU archive reference; no 1963 satellite observation")

