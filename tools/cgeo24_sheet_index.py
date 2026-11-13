"""Conservative MI sheet lookup from two acquired official PDFs."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/geo/cgeo24_esplanada_sheet_index.json"

def load():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))

def sheet_for(lon, lat, sheets):
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        raise ValueError("invalid geographic coordinate")
    matches, boundary = [], False
    for sheet in sheets:
        west, south, east, north = sheet["bbox"]
        if west <= lon <= east and south <= lat <= north:
            if lon in (west, east) or lat in (south, north):
                boundary = True
            else:
                matches.append(sheet["mi"])
    if boundary or len(matches) > 1:
        return "BOUNDARY_UNRESOLVED"
    return matches[0] if matches else None

def validate(data):
    assert data["id"] == "CGEO-24"
    assert data["schema"] == "conde.gis.sheet-catalog-locator/v1"
    assert data["sources"]["sudene"]["entry"]["mi"] == 1850
    assert data["sources"]["sudene"]["entry"]["name"] == "Esplanada - BA / SE"
    assert data["sources"]["sudene"]["entry"]["inventory_quantity"] == 4
    assert data["sources"]["sudene"]["edition_year_of_underlying_map"] is None
    for source in data["sources"].values():
        assert source["url"].startswith("https://")
        assert source["byte_size"] > 0
        assert len(source["sha256"]) == 64
    grid = data["nominal_graticule"]
    assert grid["horizontal_datum"] is None and grid["positional_accuracy_m"] is None
    assert {item["mi"] for item in grid["sheets"]} == {1850, 1851, 1906}
    assert grid["sheets"][0]["bbox"] == [-38, -12, -37.5, -11.5]
    for camera in data["camera_observations"]:
        assert camera["epoch"] == "2022-09-15"
        assert sheet_for(camera["lon"], camera["lat"], grid["sheets"]) == camera["mi_expected"] == 1850
    assert data["false_friends"][0]["name"] == "Conde - PB"
    assert data["false_friends"][0]["is_conde_bahia"] is False
    hist = data["historical"]
    for name in ("center_point_1963", "center_polygon_1963", "fall_location_1963", "horizontal_error_m"):
        assert hist[name] is None
    assert hist["authenticated_pre_1963_sheet"] is False
    assert hist["can_constrain_orbital_reentry"] is False

def verify_pdf(source, path):
    contents = Path(path).read_bytes()
    return (contents.startswith(b"%PDF-") and len(contents) == source["byte_size"] and hashlib.sha256(contents).hexdigest() == source["sha256"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ibge-pdf", type=Path)
    parser.add_argument("--sudene-pdf", type=Path)
    args = parser.parse_args()
    data = load()
    validate(data)
    for path, name in ((args.ibge_pdf, "ibge"), (args.sudene_pdf, "sudene")):
        if path is not None and not verify_pdf(data["sources"][name], path):
            parser.error(f"source SHA/size/signature mismatch: {name}")
    print("CGEO-24: index contract OK" + ("; source PDF replay OK" if args.ibge_pdf and args.sudene_pdf else "; source replay NOT_RUN unless PDFs supplied"))

if __name__ == "__main__":
    main()
