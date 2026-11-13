#!/usr/bin/env python3
"""Distinguish verifiable institution contact information from archival custody."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/sfu_station1078_custodian_route_C241-L39.json"
EXPECTED = [
    ("https://lpi.sfu-kras.ru/contact", 110177,
     "2adb4e614387eaed3b194b271ccf57db20322cdb5b0ee1f3cec2d69c54013971",
     ("lpikrgu@wood.krasnet.ru", "Приёмная директора")),
    ("https://lpi.sfu-kras.ru/node/922", 112263,
     "67c96d4cb12b5f026ae4f7f0cb95754120423ef139d2c8a98fd64de55e1c2213",
     ("15 декабря 2008", "более 10 000 экспонатов")),
]

def validate(doc, copies=None):
    assert doc["schema"] == "conde.archival_custodian_route/v1"
    assert doc["id"] == "C241-L39" and doc["predecessor"] == "C241-L38"
    assert len(doc["sources"]) == len(EXPECTED)
    for i, (url, size, digest, phrases) in enumerate(EXPECTED):
        s = doc["sources"][i]
        assert (s["url"], s["bytes"], s["sha256"]) == (url, size, digest)
        assert s["http_status"] == 200
        assert s["tls_certificate_validated"] is False
        assert s["downloaded_with_insecure_tls"] is True
        if copies is not None:
            raw = copies[i]
            assert len(raw) == size, "source length mismatch"
            assert hashlib.sha256(raw).hexdigest() == digest, "source hash mismatch"
            page = raw.decode("utf-8")
            assert all(phrase in page for phrase in phrases), "source phrase missing"
    contact, museum = doc["sources"]
    assert contact["kind"] == "INSTITUTIONAL_CONTACT_PAGE"
    assert contact["contact_address"] == "lpikrgu@wood.krasnet.ru"
    assert "not archival curator" in contact["contact_role"]
    assert museum["kind"] == "INSTITUTIONAL_MUSEUM_DESCRIPTION"
    assert museum["museum_focus"] == "history of education"
    assert museum["museum_founded_date"] == "2008-12-15"
    assert museum["museum_reports_more_than_10000_items"] is True
    assert museum["museum_station1078_journals_listed"] is False
    e = doc["evidence_boundary"]
    assert e["source_html_is_not_original_1963_journal"] is True
    for field in ("institution_contact_is_verified_current_custodian",
                  "museum_holds_station1078_journals",
                  "detailed_inventory_or_call_number_known",
                  "institutional_outreach_sent",
                  "pages_or_facsimiles_retrieved"):
        assert e[field] is False, field
    assert e["target_norad_ids"] == [527, 528, 529]
    assert e["dates_to_request"] == ["1963-11-07", "1963-11-08", "1963-11-09"]
    for field in ("independent_target_measurements", "new_numeric_observables",
                  "orbital_constraints_activated"):
        assert e[field] == 0, field
    assert doc["proposed_request"]["status"] == "NOT_SENT"
    assert doc["epistemic_status"] == "VERIFIED_PUBLIC_CONTACT_AND_MUSEUM_LEADS_NOT_ARCHIVE_HOLDINGS"
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--contact-html", type=Path)
    parser.add_argument("--museum-html", type=Path)
    args = parser.parse_args()
    assert (args.contact_html is None) == (args.museum_html is None), "supply both copies"
    raw = None if args.contact_html is None else [args.contact_html.read_bytes(), args.museum_html.read_bytes()]
    validate(json.loads(MANIFEST.read_text(encoding="utf-8")), raw)
    print("PASS: L39 contact-only archival lead, no simulated custody or orbital observation")
