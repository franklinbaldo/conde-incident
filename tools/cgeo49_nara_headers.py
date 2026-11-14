#!/usr/bin/env python3
"""CGEO-49: fail closed on unverified spot number, film can and historical geometry."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/geo/cgeo49_nara_header_crosssheet.json"
PARENT = ROOT / "research/geo/cgeo47_nara_m1765_conde_pre1963.json"
EXPECTED = {
    "m1765-317-00247.jpg": ("125370", "27 SEP 42"),
    "m1765-317-00248.jpg": ("125374", "7,11,18,20 SEP 42"),
    "m1765-317-00249.jpg": ("133002", "21 AUG 43"),
    "m1765-317-00250.jpg": ("133002", "21 AUG 43"),
}

def require(ok, msg):
    if not ok:
        raise ValueError(msg)

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(d, parent):
    require((d.get("schema"), d.get("id")) ==
            ("conde.cgeo.nara-overlay-headers/v1", "CGEO-49"), "contract id")
    require(d.get("parent_evidence") == ["CGEO-47", "CGEO-48"], "lineage")
    require((d.get("record_group"), d.get("nara_series"), d.get("nara_unit"),
             d.get("degree_square"), d.get("microfilm"), d.get("roll")) ==
            ("373", "306062", "46716637", "11S037W", "M1765", "317"), "wrong unit")
    require("Human visual" in d.get("reading_method", ""), "method not recorded")
    require(d.get("archival_method_url", "").startswith(
            "https://unwritten-record.blogs.archives.gov/"), "missing archival method")
    require(parent.get("id") == "CGEO-47", "missing source parent")
    unit = next(u for u in parent["units"] if u["degree_square"] == "11S037W")
    listed = {img["filename"]: img for img in unit["images"]}
    require(len(d.get("sheets", [])) == len(EXPECTED), "sheet cardinality")
    require({x["filename"] for x in d["sheets"]} == set(EXPECTED), "sheet set")
    for s in d["sheets"]:
        filename = s["filename"]
        original = listed[filename]
        number, date = EXPECTED[filename]
        require(s.get("sha256") == original["sha256"], "source hash mismatch")
        require((s.get("handwritten_number"), s.get("header_date_reading")) ==
                (number, date), "visual transcription drift")
        require(s.get("header_date_status") == "provisional_visual_transcription", "date promoted")
        require(s.get("number_position") ==
                "above printed O.P. FILE NO. field; classification unverified", "misidentified heading")
        require(s.get("verified_spot_number") is None and
                s.get("verified_negative_can") is None, "unverified physical locator promoted")
    c = d["cross_sheet_inferences"]
    require(c["number_repeated_on"] == [
            "m1765-317-00249.jpg", "m1765-317-00250.jpg"], "cross-sheet pair")
    require(c["repeated_number"] == "133002", "cross-sheet number")
    require("not independently established" in c["conclusion"], "false identification")
    for key in ("number_125374_is_confirmed_spot", "number_133002_is_confirmed_spot"):
        require(c[key] is None, "spot number assumed")
    require(c["images_of_conde_confirmed"] is False, "aerial exposure falsely claimed")
    limits = d["limitations"]
    require(limits["source_sha_references_are_parent_CGEO47"] is True, "lineage lost")
    for key in ("archival_locator_crosswalk_done", "original_aerial_negative_acquired",
                "ground_footprint_georeferenced", "orbital_constraints_activated"):
        require(limits[key] is False, "unverified inference promoted")
    for key in ("historical_center_geometry_1963", "verified_aerial_exposure_date_at_conde",
                "reentry_location"):
        require(limits[key] is None, "historical geometry/date invented")
    require(limits["final_status"] == "CROSS_SHEET_HEADER_CANDIDATES_ONLY", "status promoted")
    return len(d["sheets"])

def verify_bytes(d, parent, cached_directory=None):
    unit = next(u for u in parent["units"] if u["degree_square"] == "11S037W")
    by_name = {s["filename"]: s for s in unit["images"]}
    for s in d["sheets"]:
        record = by_name[s["filename"]]
        if cached_directory:
            payload = (Path(cached_directory) / ("11S037W_" + s["filename"])).read_bytes()
        else:
            req = Request(record["url"], headers={"User-Agent": "Conde-CGEO49/1.0"})
            with urlopen(req, timeout=50) as response:
                require(response.status == 200, "source HTTP non-200")
                payload = response.read()
        require(len(payload) == record["bytes"], "source size drift")
        require(hashlib.sha256(payload).hexdigest() == s["sha256"], "source hash drift")
        require(payload.startswith(bytes.fromhex("ffd8ff")) and
                payload.endswith(bytes.fromhex("ffd9")), "JPEG incomplete")
    return len(d["sheets"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--cached-directory")
    args = parser.parse_args()
    d, parent = load(DATA), load(PARENT)
    print("CGEO49_HEADER_CONTRACT_PASS", validate(d, parent))
    if args.live or args.cached_directory:
        print("CGEO49_SOURCE_BYTES_PASS", verify_bytes(d, parent, args.cached_directory))

if __name__ == "__main__":
    main()
