"""CGEO-32: validate cross-project archival locator without inventing flights."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "research" / "geo"
DNOCS = ROOT / "cgeo32_dnocs213_1961_mi1850.json"
PETROBRAS = ROOT / "cgeo26_pet53d_1961_aerial_locator.json"
USAF = ROOT / "cgeo29_usaf_63_32_photoindex_node.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(d, p, u):
    def require(ok, why):
        if not ok:
            raise ValueError(why)

    require(d["id"] == "CGEO-32" and d["schema"] == "conde.gis.archival-cross-project-leads/v1", "contract")
    require(d["municipality"] == p["municipality"] == u["municipality"], "municipality")
    require(d["evidence_status"] == "SECONDARY_SEARCH_INDEX_TRANSCRIPTION_NOT_PRIMARY_DOCUMENT", "grade")
    source = d["catalogue_family"]
    require(source["nominal_catalogue_date"] == p["catalogue_occurrence"]["catalogue_date"], "catalogue date")
    require(source["original_catalogue_pdf_acquired"] is False and source["printed_page_verified"] is False, "original not inspected")
    require(source["original_pdf_sha256"] is None and source["index_text_usable_as_verified_facsimile"] is False, "no false provenance")
    require(source["independent_catalogue_witnesses"] == 1, "duplicate web mirrors not independent")
    require(set(source["source_urls"]) <= set(p["catalogue_occurrence"]["web_mirrors"]), "same source family")
    lead = d["new_locator"]
    expected = {"project_label": "DNOCS - Projeto 213", "region": "Nordeste", "project_nominal_year": 1961,
                "aerial_photo_nominal_scale_denominator": 40000, "photo_index_nominal_scale_denominator": 250000,
                "sheet_mi": 1850, "sheet_cim": "SC-24-Z-C-VI", "sheet_name": "Esplanada", "sheet_states": ["BA", "SE"]}
    require(all(lead[k] == v for k, v in expected.items()), "misread archival index")
    pet = p["catalogue_occurrence"]["observed_entry"]
    usa = u["crosswalk"]
    require(pet["sheet_mi"] == usa["sheet_mi"] == lead["sheet_mi"], "sheet linkage")
    require(pet["sheet_cim"] == lead["sheet_cim"], "sheet code")
    require(pet["aerial_photo_nominal_scale_denominator"] == 25000 and pet["photo_index_nominal_scale_denominator"] == 100000, "PETROBRAS scale")
    require(usa["usaf_project_literal"] == "USAF 63-32", "USAF record")
    require(lead["project_label"] not in (pet["project"], usa["usaf_project_literal"]), "distinct project labels")
    for k in ("individual_flight_date", "strip_id", "frame_id", "frame_footprint", "center_of_conde_covered"):
        require(lead[k] is None, "unacquired detail: " + k)
    for k in ("original_photoindex_acquired", "original_frame_acquired", "modern_holding_verified"):
        require(lead[k] is False, "false custody: " + k)
    cross = d["cross_project_comparison"]
    require(cross["existing_pet53d_parent"] == p["id"] and cross["existing_usaf632_parent"] == u["id"], "parents")
    require(cross["common_sheet_index"] == 1850 and cross["distinct_nominal_project_labels"] == 3, "labels")
    require(cross["independent_aerial_acquisitions_verified"] == 0, "no verified flight")
    for k in ("dnocs_same_flight_as_pet53d", "dnocs_same_flight_as_usaf632"):
        require(cross[k] is None, "independence unresolved")
    require(cross["same_catalogue_family_as_pet53d"] is True, "catalogue lineage")
    for k in ("usaf_63_32_is_exposure_date", "nominal_year_dates_every_frame", "full_sheet_coverage_verified"):
        require(cross[k] is False, "unsupported dating/footprint")
    science = d["scientific_link"]
    require(science["status"] == "CONNECTED_PENDING_PRIMARY_CATALOGUE_AND_PHOTOINDEX", "status")
    require(science["incident_date"] == "1963-11-08", "incident")
    require(set(science["activation_requirements"]) == {"original_catalogue_entry", "individual_flight_date", "frame_footprint", "image_bytes_and_sha256", "historical_georeference_controls"}, "requirements")
    for k in ("historical_center_point", "historical_center_polygon", "fall_location"):
        require(science[k] is None, "invented geometry")
    require(science["can_constrain_orbital_reentry"] is False, "unjustified orbital restriction")
    require({x["to"] for x in d["graph_edges"]} == {"CGEO-24", "CGEO-26", "CGEO-29", "CGEO-17", "CGEO-18"}, "graph connectivity")
    return "CGEO-32 CONTRACT_ONLY_PASS: new DNOCS 213 1961 MI-1850 archival lead; no original frames"


if __name__ == "__main__":
    print(check(load(DNOCS), load(PETROBRAS), load(USAF)))
