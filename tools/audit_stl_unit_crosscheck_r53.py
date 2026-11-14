"""NASA's reproduced STL table: Kepler dimensional crosscheck, not a new sensor."""
import json
import math
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "research/tle_custody/stl_unit_crosscheck_C241_LONTRA_R53.json"
PDF_SHA = "f77b0e8998d467dd457d0ab8e8012e6e9d69c60fb6180aa3d68f1e8422b32786"
# Independently transcribed from previously visually inspected PDF page B-12.
ROWS = (
    ("1963 3A first", "1963 3A", 94.7, 298, 322),
    ("1963 3A second", "1963 3A", 94.6, 286, 334),
    ("Cosmos 13", "1963 6A", 89.8, 127, 209),
    ("Syncom 1 first", "1963 4A", 1426.5, 21268, 22974),
    ("Syncom 1 second", "1963 4A", 1426.5, 21242, 23004),
)
R = 6371.0
MU = 398600.4418
MI = 1.609344


def minutes(perigee, apogee, scale):
    semimajor = R + (perigee + apogee) / 2 * scale
    return 2 * math.pi * math.sqrt(semimajor ** 3 / MU) / 60


def audit(doc):
    if not isinstance(doc, dict) or doc.get("id") != "C241-LONTRA-R53":
        raise ValueError("wrong audit record")
    for k, v in {
        "url": "https://ntrs.nasa.gov/api/citations/19670008638/downloads/19670008638.pdf",
        "pdf_sha256": PDF_SHA,
        "pdf_page_one_based": 105,
        "printed_page": "B-12",
        "upstream": "STL SPACE LOG, Vol. 3, No. 4",
        "upstream_original_retrieved": False,
    }.items():
        if doc.get("source", {}).get(k) != v:
            raise ValueError("invalid source: " + k)
    if doc.get("physics") != {
        "earth_radius_km": R, "earth_mu_km3_s2": MU, "statute_mile_km": MI
    }:
        raise ValueError("model assumptions changed")
    if doc.get("rows") != [list(row) for row in ROWS]:
        raise ValueError("printed observations changed")
    for k, v in {
        "classification": "NUMERICAL_UNIT_CROSSCHECK_NOT_ORIGINAL_LEGEND",
        "favoured_by_internal_consistency": "statute_miles",
        "unit_printed_on_B12_directly_certified": False,
        "unit_in_original_STL_issue_certified": False,
        "independent_from_R51": False,
        "new_instrumental_sensors": 0,
        "new_observations_527_528_529_november": 0,
        "new_orbital_constraints_activated": 0,
    }.items():
        if doc.get("conclusion", {}).get(k) != v:
            raise ValueError("evidence wrongly promoted: " + k)
    computed = []
    for name, designation, printed, perigee, apogee in ROWS:
        km = minutes(perigee, apogee, 1)
        miles = minutes(perigee, apogee, MI)
        if not abs(printed - miles) < abs(printed - km):
            raise ValueError("unit consistency failed: " + name)
        computed.append({
            "name": name, "designation": designation, "printed_period_minutes": printed,
            "if_km_minutes": round(km, 3),
            "if_miles_minutes": round(miles, 3),
            "km_residual_minutes": round(abs(printed - km), 3),
            "miles_residual_minutes": round(abs(printed - miles), 3)
        })
    return computed


if __name__ == "__main__":
    print(json.dumps({"rows": audit(json.loads(SOURCE.read_text(encoding="utf-8"))),
                      "status": "QUANTITATIVE_INFERENCE_ONLY"}, indent=2))
