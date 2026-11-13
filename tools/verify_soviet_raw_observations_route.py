#!/usr/bin/env python3
"""Verify original IKI 2007 PDF custody without promoting catalogues to observations."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/soviet_raw_observations_route_C241-L37.json"


def validate(data, pdf_bytes=None):
    assert data["schema"] == "conde.archival_source_route/v1"
    assert data["id"] == "C241-L37"
    s = data["retrospective_author_source"]
    assert s["publisher"] == "Институт космических исследований РАН (IKI RAS)"
    assert s["publication_year"] == 2007
    assert s["source_role"] == "RETROSPECTIVE_AUTHOR_DESCRIPTION_NOT_INSTRUMENT"
    assert s["retrieved_pdf"] and s["page_visually_inspected"]
    assert s["pdf_page_index_zero_based"] == 52
    assert s["printed_pages_on_spread"] == [104, 105]
    assert s["bytes"] == 7317076
    assert s["sha256"] == "8dc0d5b54985ab53d394babbad36da03ae02cef17f5ad897ad94e05acf9005f5"
    d = data["source_distinction"]
    assert d["methods_series"] == "Бюллетень станций оптического наблюдения искусственных спутников Земли"
    assert d["raw_data_series"] == "Результаты наблюдений ИСЗ"
    assert d["same_serial_title_proven"] is False
    assert d["raw_series_target_measurements_read"] is False
    c = data["bibliographic_followups"]
    assert len(c) == 2
    assert c[0]["catalogue_year_of_publication"] == 1964
    assert c[0]["period_described_in_catalogue"] == "June 1963"
    assert c[0]["target_527_528_529_explicitly_named"] is False
    assert c[0]["executor_direct_http_status"] == 403
    assert c[1]["digitized_day"] == "2008-09-23"
    assert all(x["source_status"] == "CATALOGUE_METADATA_ONLY" for x in c)
    assert all(x["original_pages_retrieved"] is False for x in c)
    assert all(x["source_bytes_sha256"] is None for x in c)
    assert data["requested_norad_ids"] == [527, 528, 529]
    assert data["independent_target_observations"] == 0
    assert data["new_numeric_observables"] == 0
    assert data["orbital_constraints_activated"] == 0
    assert data["original_1963_instrument_read"] is False
    assert data["archive_contacted"] is False
    assert data["epistemic_status"] == "RETROSPECTIVE_SOURCE_SERIES_REDIRECT_NO_ORBITAL_DATA"
    if pdf_bytes is not None:
        assert len(pdf_bytes) == s["bytes"], "PDF source length changed"
        assert pdf_bytes.startswith(b"%PDF-"), "PDF magic missing"
        assert b"%%EOF" in pdf_bytes[-1024:], "PDF trailer missing"
        assert hashlib.sha256(pdf_bytes).hexdigest() == s["sha256"], "PDF source hash mismatch"
    return True


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path, help="complete original PDF file, not stored in Git")
    args = p.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, args.pdf.read_bytes() if args.pdf else None)
    print("PASS: retrospective series locator without orbital promotion" + ("; PDF byte replay" if args.pdf else ""))
