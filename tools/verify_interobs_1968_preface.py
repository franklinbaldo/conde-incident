"""Audit a three-page primary INTEROBS preface without promoting it to target observation."""
import argparse
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/tle_custody/interobs_1968_closure_preface_C241-LONTRA-R40.json"
SHA = "997ff8bed4924b9cfcba7a018ebeed176ac9602e0484e41c899235b2515e110c"
SIZE = 725023
URL = "https://real.mtak.hu/143828/1/vorwort_interobs_programs.pdf"


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def validate(data, pdf_bytes=None):
    require(data["schema"] == "conde.contemporary_satellite_tracking_bibliography/v1", "schema")
    require(data["id"] == "C241-LONTRA-R40", "id")
    require(data["status"] == "CONTEMPORARY_1968_PREFACE_IDENTIFIES_INTEROBS_SERIES_CLOSURE_AND_SUCCESSOR_NOT_TARGET_MEASUREMENT", "status")
    source = data["source"]
    for k, v in {
        "repository_record": "https://real.mtak.hu/143828/", "pdf_url": URL,
        "document_date": "1968-07-01", "publication_year": 1968,
        "covered_observation_year": 1966, "series_issue": 7,
        "http_status": 200, "tls_validated": True, "bytes": SIZE,
        "sha256": SHA, "pdf_page_count": 3, "preface_pdf_page_zero_based": 0,
        "preface_printed_page": 3, "page_visually_inspected": True,
        "complete_volume_retrieved": False, "excerpt_facsimile_retrieved": True,
    }.items():
        require(source[k] == v, "source." + k)
    p = data["preface"]
    for k in ("reports_issue_7_as_final_issue_of_series", "describes_satellite_grouped_summary_list_1",
              "describes_satellite_grouped_observation_material_list_2", "future_series_supported_by_astronomical_council_ussr"):
        require(p[k] is True, "preface." + k)
    for k in ("actual_list_1_or_list_2_retrieved", "satellite_ids_proven_equivalent_to_527_528_529",
              "successor_volume_retrieved", "earlier_folge_1_2_volumes_retrieved", "november_1963_campaign_confirmed"):
        require(p[k] is False, "preface." + k)
    require(p["satellite_ids_in_issue_7"] == ["65-106-01", "65-106-02", "65-112-01"], "issue 7 objects")
    require(p["future_publication_series_romanized_as_printed"] == "Resultati Nabljudenij Sowjetskich Iskustwennich Sputnikow Semli", "successor title")
    require("1963-11-07" in data["follow_up"] and "1963-11-09" in data["follow_up"], "date scope")
    limits = data["limits"]
    for k in ("target_observations_identified", "raw_instrumental_observations_retrieved", "outreach_sent"):
        require(limits[k] is False, "limits." + k)
    require(limits["orbital_constraints_activated"] == 0, "false orbital constraint")
    require(limits["new_target_orbital_measurements"] == 0, "false target measurement")
    if pdf_bytes is not None:
        require(len(pdf_bytes) == SIZE, "source byte length")
        require(hashlib.sha256(pdf_bytes).hexdigest() == SHA, "source SHA256")
        require(pdf_bytes.startswith(b"%PDF-"), "PDF signature")
        require(b"%%EOF" in pdf_bytes[-256:], "PDF EOF")
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("pypdf required for PDF replay") from exc
        reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
        require(len(reader.pages) == 3, "PDF must be 3-page excerpt, not full volume")
        first = reader.pages[0].extract_text() or ""
        # Anchors survive OCR quirks and soft-hyphenated line wrapping.
        for token in ("V O R W O R T", "Heft Nr. 7", "1966", "beenden wir die Ausgabe",
                      "eigentliche Beobachtungsmaterial", "Nabljudenij", "Sputnikow Semli",
                      "65-106-01", "65-112=01", "1968"):
            require(token in first, "preface anchor missing: " + token)
        cover = reader.pages[1].extract_text() or ""
        require("INTEROBS" in cover and "1968" in cover, "title page missing")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-original", type=Path)
    opts = parser.parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate(data, opts.pdf_original.read_bytes() if opts.pdf_original else None)
    print("C241-LONTRA-R40 archival custody and scientific limits PASS")


if __name__ == "__main__":
    main()
