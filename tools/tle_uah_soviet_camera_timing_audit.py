#!/usr/bin/env python3
"""C241-L47: replay UAH scans while blocking transfer of generic Soviet shutter delays to NORAD 528."""
import argparse
import hashlib
import json
import pathlib
import urllib.request

LEDGER = pathlib.Path(__file__).resolve().parents[1] / "research/tle_custody/uah_soviet_camera_timing_C241-L47.json"
EXPECTED = (
    (3371, "19631000", 9678172, "41a7ecbf20ecbb799709905ad52d1c4e900c5c348c0273e7314506670e7c3509", 28),
    (3372, "19631100", 10004789, "f953ffe533a7f6e0a3430c6381903be57dd98521523622e4b6e90c7830080318", 28),
    (3373, "19631200", 3761647, "e5552268a1ec86ab1823a409bb7e2b994a11b42eed9890affc9ae7a0a73d57ea", 9),
)


def reject_duplicate_keys(pairs):
    d = {}
    for key, value in pairs:
        if key in d:
            raise ValueError("duplicate key: " + key)
        d[key] = value
    return d


def load(path=LEDGER):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def audit(d):
    if set(d) != {"schema", "evidence_id", "epistemic_status", "source_lineage", "family_count", "orbital_constraint_active", "target", "source_copies", "inspected_context", "next_test"}:
        raise ValueError("ledger schema drift")
    if d["schema"] != "c241-l47-uah-soviet-camera-context-v1" or d["evidence_id"] != "C241-L47":
        raise ValueError("identity")
    if d["epistemic_status"] != "CONTEMPORARY_SECONDHAND_INSTRUMENT_CONTEXT_ONLY" or d["orbital_constraint_active"] is not False or d["family_count"] != 1:
        raise ValueError("scientific status")
    if "May 1963" not in d["source_lineage"] or "not retrieved" not in d["source_lineage"]:
        raise ValueError("chain of custody")
    t = d["target"]
    nulls = {"raw_observation", "observation_utc", "station", "sensor_identity_for_528", "frame", "instrument_sigma_for_528", "orbital_covariance", "decay_hour_utc", "reentry_location"}
    if set(t) != nulls | {"norad", "designator", "specific_object_mentioned_on_inspected_page"}:
        raise ValueError("target schema")
    if t["norad"] != 528 or t["designator"] != "1963-003B" or t["specific_object_mentioned_on_inspected_page"] is not False or any(t[k] is not None for k in nulls):
        raise ValueError("unproven physical observation or timing")
    sources = d["source_copies"]
    if len(sources) != len(EXPECTED):
        raise ValueError("source count")
    for i, (item_id, stamp, nbytes, digest, pages) in enumerate(EXPECTED):
        s = sources[i]
        if set(s) != {"id", "month", "issue", "item", "pdf", "sha256", "bytes", "pdf_pages", "text_layer_chars_pypdf", "specific_page_reviewed"}:
            raise ValueError("source schema")
        if s["id"] != ("C241-L47-UAH-" + ("OCT", "NOV", "DEC")[i]) or s["month"] != ("1963-10", "1963-11", "1963-12")[i]:
            raise ValueError("month mismatch")
        if s["issue"] != ("vol. 4, no. 10", "vol. 4, no. 11", "vol. 4, no. 12")[i]:
            raise ValueError("issue mismatch")
        if s["item"] != f"https://digitalprojects.uah.edu/items/show/{item_id}":
            raise ValueError("item URL")
        if s["pdf"] != f"https://digitalprojects.uah.edu/files/original/195/{item_id}/spaceintelligencenotes_{stamp}.pdf":
            raise ValueError("PDF URL")
        if s["sha256"] != digest or s["bytes"] != nbytes or s["pdf_pages"] != pages:
            raise ValueError("binary provenance")
        if s["text_layer_chars_pypdf"] != 0 or s["specific_page_reviewed"] is not (i == 1):
            raise ValueError("visual versus text inspection")
    c = d["inspected_context"]
    expected_context = {
        "source_id": "C241-L47-UAH-NOV", "page_printed": 24, "page_pdf_index_zero_based": 23,
        "heading": "STUDY OF STANDARD EQUIPMENT FOR PHOTOGRAPHIC OBSERVATION OF ARTIFICIAL EARTH SATELLITES",
        "camera": "NAFA-3S/25-S", "report_reference": "Dept. of Defense Intelligence Info., Report No. 1521678463, 19 June 1963",
        "earlier_publication_reference": "Astronomicheskiy Zhurnal, Moskva, No. 5, May 1963",
        "original_russian_page_recovered": False, "underlying_dod_report_recovered": False,
        "opening_shutter_delay_seconds_printed": "0.0022", "opening_shutter_plusminus_seconds_printed": "0.0002",
        "closing_shutter_lag_seconds_printed": "0.0002", "closing_shutter_plusminus_seconds_printed": "0.0002",
        "chronograph_delay_at_210_volts_seconds_printed": "0.0268",
        "chronograph_delay_at_230_volts_seconds_printed": "0.0254",
    }
    for key, value in expected_context.items():
        if c.get(key) != value:
            raise ValueError("unverified transcription: " + key)
    if set(c) != set(expected_context) | {"interpretation", "visual_check"}:
        raise ValueError("context schema")
    if "not a tracking record" not in c["interpretation"] or "No OCR" not in c["visual_check"]:
        raise ValueError("physical overclaim")
    return True


def verify_pdf(s, data, use_pdf_reader=False):
    if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-128:]:
        raise ValueError("malformed facsimile")
    if len(data) != s["bytes"] or hashlib.sha256(data).hexdigest() != s["sha256"]:
        raise ValueError("source drift")
    if use_pdf_reader:
        from io import BytesIO
        from pypdf import PdfReader
        doc = PdfReader(BytesIO(data))
        if len(doc.pages) != s["pdf_pages"]:
            raise ValueError("page count drift")
        if sum(len(page.extract_text() or "") for page in doc.pages) != s["text_layer_chars_pypdf"]:
            raise ValueError("text layer drift")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-remote", action="store_true")
    parser.add_argument("--source-dir", type=pathlib.Path)
    opts = parser.parse_args()
    ledger = load()
    audit(ledger)
    if opts.verify_remote or opts.source_dir:
        for s in ledger["source_copies"]:
            if opts.source_dir:
                data = (opts.source_dir / (s["month"].replace("-", "") + "00.pdf")).read_bytes()
            else:
                req = urllib.request.Request(s["pdf"], headers={"User-Agent": "Conde-C241-L47/1.0"})
                with urllib.request.urlopen(req, timeout=60) as response:
                    data = response.read()
            verify_pdf(s, data, use_pdf_reader=True)
            print(s["id"], "binary and scanned pages PASS")
    print("C241-L47 scope PASS: historic equipment only; NORAD 528 observation not recovered")


if __name__ == "__main__":
    main()
