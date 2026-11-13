"""Trace variable-specific retrospective station coverage, not a 1963 sounding."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/meteorology/apac_recife_2004_variable_rows.txt"
OUTPUT = ROOT / "research/meteorology/apac_recife_2004_periods.json"
PDF = "https://www.apac.pe.gov.br/images/media/1642199099_Tomo%20I%20-%20Completo.pdf"
TABLES = {"temperature_min": "1.4", "relative_humidity": "1.7",
          "wind_speed": "1.8", "surface_pressure": "1.9"}
COLUMNS = ["variable", "table", "wmo_id", "latitude_catalogue",
           "longitude_catalogue", "period_mean", "unit", "start_month",
           "start_year", "end_month", "end_year", "reported_total_months",
           "reported_months_with_data"]


def build(raw):
    items = []
    for line in raw.decode("utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != len(COLUMNS):
            raise ValueError("bad column count")
        row = dict(zip(COLUMNS, parts))
        for key in ("wmo_id", "start_month", "start_year", "end_month",
                    "end_year", "reported_total_months", "reported_months_with_data"):
            row[key] = int(row[key])
        for key in ("latitude_catalogue", "longitude_catalogue", "period_mean"):
            row[key] = float(row[key])
        if TABLES.get(row["variable"]) != row["table"] or row["wmo_id"] != 82900:
            raise ValueError("unknown station or variable/table")
        start = row["start_year"], row["start_month"]
        end = row["end_year"], row["end_month"]
        if not (1 <= start[1] <= 12 and 1 <= end[1] <= 12 and start <= end):
            raise ValueError("bad date")
        if row["reported_months_with_data"] > row["reported_total_months"]:
            raise ValueError("invalid missingness")
        row["period_overlaps_1963_11"] = start <= (1963, 11) <= end
        row["observed_at_1963_11_08"] = None
        row["verified_november_1963_monthly_value"] = None
        row["calibrated_uncertainty"] = None
        items.append(row)
    if len(items) != 4 or {r["variable"] for r in items} != set(TABLES):
        raise ValueError("missing/duplicate variable")
    pressure = next(r for r in items if r["variable"] == "surface_pressure")
    if pressure["period_overlaps_1963_11"]:
        raise ValueError("surface pressure catalogue starts in 1966, not 1963")
    return {
        "schema": "conde.apac-recife-variable-coverage/v1",
        "source": {
            "url": PDF, "institution": "Government of Pernambuco / APAC archive",
            "publication_month": "2004-11", "read_on": "2026-11-13",
            "pdf_sha256": None, "visual_pdf_verified": False,
            "acquisition": "indexed PDF text; binary/screenshot timed out",
            "transcription_sha256": hashlib.sha256(raw).hexdigest(),
        },
        "station": {"wmo_id": 82900, "label": "CURADO (RECIFE) - INMET",
                    "sonde_launch_coordinates_1963": None},
        "records": items,
        "uncertainty": {"1963_surface_measurement": None,
                        "independent_igra_observation": None,
                        "sonde_instrument_1963": None,
                        "recife_to_conde_transfer_error": None},
        "dependencies": ["C149", "C150", "C151", "C193"],
        "edges": [
            {"from": "APAC-PE-2004-tables-1.4-1.7-1.8-1.9",
             "to": "C149-C151", "relation": "retrospective_surface_coverage"},
            {"from": "C149-C151", "to": "Castor_drag_and_drift",
             "relation": "PENDING_observation_and_transfer"},
        ],
        "status": "CONNECTED_PENDING_CALIBRATION",
        "admissible_domain_reduction": False,
    }


def check(data, raw):
    if data != build(raw):
        raise ValueError("manifest differs from checked transcription")
    return True


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    raw = SOURCE.read_bytes()
    result = build(raw)
    if args.check:
        check(json.loads(OUTPUT.read_text()), raw)
        print("PASS variable-specific periods")
    else:
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
