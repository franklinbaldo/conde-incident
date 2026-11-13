"""CGEO-20: temporal controls for Centro and Vila do Conde."""
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "research/geo/cgeo20_centro_vila_2020.json"


def validate(d):
    def need(ok, message):
        if not ok:
            raise ValueError(message)
    need(d["id"] == "CGEO-20", "contract id")
    need(d["municipality"]["ibge_code"] == "2908606", "wrong place")
    sources = d["sources"]
    need([x["id"] for x in sources] == ["MUNI20", "BLOG14"],
         "changed source families")
    official = sources[0]
    need(official["url"].startswith("https://www.conde.ba.gov.br/"),
         "not an official municipal source")
    need(official["pages_visually_inspected"] == [1, 2],
         "pages not inspected")
    need(official["pdf_sha256"] is None and official["binary_acquired"] is False,
         "fabricated binary authentication")
    expected = [
        ("MUNI20", 1, "CENTRO DA CIDADE, VILA DO CONDE"),
        ("MUNI20", 2, "Praça Severino Vieira (centro), Praça Vila do Conde (Vila)"),
        ("BLOG14", None, "Passarela que liga o Conde a Vila do Conde"),
        ("BLOG14", None, "Passarela sobre o rio Itapicuru"),
    ]
    need(len(d["observations"]) == 4, "missing occurrence")
    for item, triplet in zip(d["observations"], expected):
        need((item["source"], item["page"], item["verbatim"]) == triplet,
             "changed source text")
        need(item["applies_in_1963"] is None, "backdated source")
    units = d["named_localities"]
    need([(u["id"], u["name"]) for u in units] ==
         [("CENTRO20", "Centro da cidade"), ("VILA20", "Vila do Conde")],
         "conflated named localities")
    for unit in units:
        need(unit["point"] is None and unit["polygon"] is None,
             "no coordinate or polygon in source")
    interp = d["interpretation"]
    need(interp["distinction_of_locality_names_in_2020"] is True,
         "lost modern distinction")
    for k in ("2020_source_proves_1963_urban_extent",
              "2014_bridge_proves_1963_bridge",
              "same_2020_process_multiple_independent_observers",
              "senhor_do_bonfim_is_nossa_senhora_do_monte"):
        need(interp[k] is False, "unsupported historical conclusion: " + k)
    for k in ("1958_severiano_lima_is_2020_severino_vieira",
              "1963_center_is_2020_centro", "1963_center_is_2020_vila"):
        need(interp[k] is None, "unproven 1963 identity: " + k)
    need(interp["status"] == "CONNECTED_PENDING_HISTORICAL_SPATIAL_BRIDGE",
         "unearned historical bridge")
    links = d["dependency_edges"]
    need(len(links) == 4 and
         {x["from"] for x in links} == {"CGEO-17", "CGEO-18", "CGEO-19"},
         "lost dependency edge")
    need({x["to"] for x in links} == {"CENTRO20", "VILA20"},
         "premature exclusion of a locality")
    exp = d["castor_export"]
    need(exp["event_date"] == "1963-11-08", "wrong event date")
    for k in ("center_1963_point", "center_1963_polygon",
              "centro_vila_boundary_1963", "bridge_present_1963",
              "impact_point_1963", "crs", "accuracy_m"):
        need(exp[k] is None, "invented 1963 position: " + k)
    need(exp["can_constrain_orbital_reentry"] is False,
         "no orbital constraint from modern labels")
    return d


if __name__ == "__main__":
    validate(json.loads(CONTRACT.read_text(encoding="utf-8")))
    print("CGEO-20 PASS: distinct 2020 names; 1963 still unresolved")
