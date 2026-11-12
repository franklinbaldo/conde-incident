"""Fail-closed export of what a UWM 1954/1961 sheet does NOT establish about 1963."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from datetime import date

RECORD = Path(__file__).resolve().parents[1] / "research/geo/uwm_aracaju_se_1954_1961_legend_review.json"
PARENT = Path(__file__).resolve().parents[1] / "research/geo/uwm_aracaju_se_1954_1961_cartographic_custody.json"
CROP_IDS = {
    "legend_limits": ("ef3c6754e39ed0364bb14f405f6da93d4a55b8bba61aaebf67a96ba7a72cdb33", 308989),
    "marginal_imprint": ("e114640d9aed9544e06eac11ba5fbe6108c7c0b322bb001185812240ba2cc617", 48662),
    "conde_and_coast": ("9ebbb45431e445ea1304d25d285b5aff8ed1272b544d424f35f8fe28d47af927", 532998),
}
PROJECTED_CAPTION = "Projeção policônica da Carta Internacional ao milionésimo"
CLASS_LABELS = ["Internacional", "Interestadual", "Marco de fronteira"]

def read_record(path: Path = RECORD, parent: Path = PARENT) -> dict:
    rec = json.loads(path.read_text(encoding="utf-8"))
    par = json.loads(parent.read_text(encoding="utf-8"))
    if rec["schema"] != "conde.historical-cartographic-legend-review/v1":
        raise ValueError("unsupported cartographic review schema")
    if rec["record_id"] != "CGEO-08" or rec["parent_occurrence_id"] != par["occurrence_id"]:
        raise ValueError("source occurrence mismatch")
    if par["object"]["contentdm_item_id"] != "10814" or rec["source"]["catalogue_item_id"] != "10814":
        raise ValueError("unexpected map item")
    if rec["same_underlying_source_not_new_independent_survey"] is not True:
        raise ValueError("provenance cannot be independent")
    if len(rec["visually_inspected_iiif_derivatives"]) != len(CROP_IDS):
        raise ValueError("unexpected IIIF crop count")
    if {c["role"] for c in rec["visually_inspected_iiif_derivatives"]} != set(CROP_IDS):
        raise ValueError("missing or duplicate crop role")
    for crop in rec["visually_inspected_iiif_derivatives"]:
        expected = CROP_IDS[crop["role"]]
        if expected != (crop["sha256"], crop["bytes"]) or crop["http_status"] != 200:
            raise ValueError("unexpected crop digest or size")
        if not crop["url"].startswith("https://collections.lib.uwm.edu/digital/iiif/agdm/10814/"):
            raise ValueError("unexpected crop endpoint")
    literal = rec["literal_readings"]
    if literal["projection_caption"] != PROJECTED_CAPTION:
        raise ValueError("altered projection caption")
    if literal["legend_boundary_classes_observed"] != CLASS_LABELS:
        raise ValueError("altered legend categories")
    if literal["municipal_boundary_class_in_inspected_legend"] is not False:
        raise ValueError("municipal legend class was not observed")
    if literal["toponym_conde_visible"] is not True:
        raise ValueError("toponym reading altered")
    geo = rec["cartographic_interpretation"]
    for key in ("projection_full_parameters", "crs_authority", "datum",
                "georeferencing_control_points", "positional_accuracy_m",
                "municipal_boundary_1963", "source_publishing_impression_date_verified"):
        if geo[key] is not None:
            raise ValueError(f"unproven cartographic metadata: {key}")
    if geo["projection_family_printed"] != "POLYCONIC":
        raise ValueError("projection family mismatch")
    if geo["historical_boundary_year_1963_proven"] is not False:
        raise ValueError("unproven historical boundary")
    if geo["city_label_conde_is_municipal_perimeter"] is not False:
        raise ValueError("toponym is not a polygon")
    if geo["municipal_boundary_graphically_identifiable_by_legend"] is not False:
        raise ValueError("legend does not identify municipal limits")
    for key in ("historical_municipal_boundary_polygon", "observed_reentry_coordinates",
                "event_spatial_membership", "datum"):
        if rec["castor_contract"][key] is not None:
            raise ValueError(f"fabricated historical geometry or event: {key}")
    if rec["castor_contract"]["can_constrain_reentry_1963"] is not False:
        raise ValueError("unproven 1963 spatial constraint")
    if rec["castor_contract"]["forward_operator_active"] is not False:
        raise ValueError("unproven forward operator")
    return rec

def check_derivative(record: dict, role: str, image_file: Path) -> None:
    crop = next((c for c in record["visually_inspected_iiif_derivatives"] if c["role"] == role), None)
    if crop is None:
        raise ValueError(f"unknown IIIF derivative: {role}")
    image = image_file.read_bytes()
    if hashlib.sha256(image).hexdigest() != crop["sha256"] or len(image) != crop["bytes"]:
        raise ValueError("IIIF derivative checksum/size mismatch")

def export(date_iso: str, record: dict) -> dict:
    date.fromisoformat(date_iso)
    if record["castor_contract"]["target_date"] != "1963-11-08":
        raise ValueError("unexpected historical target date")
    return {
        "date": date_iso,
        "source_record": record["record_id"],
        "same_underlying_cartographic_source": record["parent_occurrence_id"],
        "sheet_projection_family": record["cartographic_interpretation"]["projection_family_printed"],
        "sheet_projection_crs": None,
        "sheet_datum": None,
        "historical_municipal_boundary_polygon": None,
        "event_spatial_membership": None,
        "can_constrain_reentry_1963": False,
        "status": "CONNECTED_PENDING_CALIBRATION",
        "missing_bridges": record["castor_contract"]["missing_bridges"],
    }

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", default="1963-11-08", help="Requested observation date, ISO YYYY-MM-DD")
    p.add_argument("--verify-derivative", type=Path, help="Locally downloaded IIIF JPEG")
    p.add_argument("--role", choices=list(CROP_IDS), help="Crop role for checksum verification")
    args = p.parse_args()
    if (args.verify_derivative is None) != (args.role is None):
        p.error("--role and --verify-derivative must be provided together")
    record = read_record()
    if args.verify_derivative is not None:
        check_derivative(record, args.role, args.verify_derivative)
    print(json.dumps(export(args.date, record), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
