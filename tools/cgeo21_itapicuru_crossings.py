"""CGEO-21: keep modern crossing chronology out of 1963 reentry location."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo21_itapicuru_crossings_2014_2025.json"
PARENT = ROOT / "research/geo/cgeo20_centro_vila_2020.json"


def validate(d):
    def require(predicate, why):
        if not predicate:
            raise ValueError(why)

    require(d["id"] == "CGEO-21" and d["municipality"] ==
            {"ibge_code": "2908606", "name": "Conde", "uf": "BA"}, "wrong project or source")
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    require(parent["id"] == "CGEO-20" and parent["castor_export"]["bridge_present_1963"] is None,
            "parent no longer unresolved")
    sources = d["sources"]
    require([x["id"] for x in sources] ==
            ["BLOG14", "ALBA15", "PNCP24", "NEWS24", "NEWS25"], "source ID/order altered")
    expected = {
        "BLOG14": ("2014-03-26", "condebahia.wordpress.com", "local_blog"),
        "ALBA15": ("2015-02-06", "www.al.ba.gov.br", "official_legislative_proposal_index"),
        "PNCP24": ("2024-05-29", "pncp.gov.br", "official_procurement_record"),
        "NEWS24": ("2024-12-29", "www.politicalivre.com.br", "press_announced_future_inauguration"),
        "NEWS25": ("2025-07-16", "conde.portaldacidade.com", "local_press_report"),
    }
    from urllib.parse import urlparse
    for s in sources:
        date, domain, kind = expected[s["id"]]
        require(s["source_date"] == date and urlparse(s["url"]).netloc == domain and
                s["kind"] == kind, "source/date/authority mismatch")
        require(s["file_acquired"] is False and s["sha256"] is None, "invented original hash")
    require(sources[1]["identifier"] == "IND/20.904/2015", "incorrect legislature identifier")
    require(sources[2]["identifier"] == "14126692000123-1-000022/2024", "wrong PNCP record")
    require(sources[3]["announced_event_date"] == "2024-12-30", "announcement date changed")
    assets = d["candidate_assets"]
    require([(x["id"], x["type"], x["documented_in"]) for x in assets] == [
        ("PEDESTRIAN_PASSARELA14", "passarela", ["BLOG14"]),
        ("CONCRETE_BRIDGE24", "concrete_bridge", ["PNCP24", "NEWS24", "NEWS25"])
    ], "crossing types or source lineage conflated")
    for a in assets:
        require(a["geometry"] is None and a["construction_date"] is None and
                a["exists_in_1963"] is None, "unearned bridge reconstruction")
    require(assets[1]["inauguration_verified"] is None, "press announcement treated as act")
    observations = d["observations"]
    require([o["source"] for o in observations] == [s["id"] for s in sources],
            "orphan/missing source observations")
    require(observations[0]["supports_1963"] is None, "passarela backdated")
    for o, key in zip(observations[1:], [
            "supports_bridge_absence_before_2015", "proves_actual_completion",
            "proves_event_occurred_on_2024_12_30", "proves_bridge_presence_in_1963"]):
        require(o[key] is False, "overstated source inference: " + key)
    require({(x["from"], x["to"]) for x in d["links"]} == {
        ("CGEO-20", "PEDESTRIAN_PASSARELA14"), ("CGEO-20", "CONCRETE_BRIDGE24"),
        ("CGEO-18", "CGEO-21"), ("CGEO-17", "CGEO-21"), ("CGEO-19", "CGEO-21")
    }, "lost cumulative dependency")
    interp = d["interpretation"]
    require(interp["same_passarela_and_concrete_bridge"] is None and
            interp["confirmed_2024_inauguration_date"] is None and
            interp["historical_1963_side_of_river_from_tupi"] is None,
            "unproved identity/event/1963 riverbank")
    require(interp["proven_absence_of_bridge_in_1963"] is False and
            interp["spatial_separation_in_2024_2025_reported"] is True,
            "wrong interpretation")
    require(interp["status"] == "CONNECTED_PENDING_HISTORICAL_SPATIAL_BRIDGE", "status too strong")
    exp = d["castor_export"]
    require(exp["event_date"] == "1963-11-08", "wrong incident date")
    for k in ("city_center_polygon_1963", "crossing_point_1963", "crossing_present_1963",
              "river_bank_of_reported_event_1963", "impact_point_1963", "crs", "accuracy_m"):
        require(exp[k] is None, "invented spatial variable: " + k)
    require(exp["can_constrain_orbital_reentry"] is False, "not a physical constraint")
    return d


if __name__ == "__main__":
    validate(json.loads(CONTRACT.read_text(encoding="utf-8")))
    print("CGEO-21 PASS: bridge chronology indexed; 1963 unknown")
