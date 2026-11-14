"""CGEO-63: deterministic editorial-toponym audit, optional HTTP re-acquisition."""
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

MANIFEST = Path(__file__).resolve().parents[1] / "research/geo/cgeo63_praca_editorial_variants.json"
SHA2018 = "45a86bade93889c5bdf734acb96453f7973e81a81882879b2440087ac308dfeb"
URL2018 = "https://jornalgrandebahia.com.br/2018/02/conde-apresenta-o-1o-festival-do-coco/"
HIST2025 = "https://conde.portaldacidade.com/noticias/cidade/historia-de-conde-parte-iv-curiosidades-do-municipio-entre-os-seculos-xix-e-xx-2248"
COUNTS = {"Severiano Vieira": 2, "Severino Vieira": 7}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    require(data["id"] == "CGEO-63", "wrong study ID")
    require(data["schema"] == "conde.gis.historical-plaza-editorial-variants/v1", "schema")
    require(data["municipality"] == {"name": "Conde", "uf": "BA", "ibge_code": "2908606"}, "wrong municipality")
    require(len(data["sources"]) == 5, "five linked source records expected")
    src = {x["id"]: x for x in data["sources"]}
    require(set(src) == {"JGB2018", "HIST2025", "MUNI2020", "IBGE1958", "OSM2026"}, "source IDs")
    event = src["JGB2018"]
    require(event["kind"] == "contemporary_secondary_event_schedule", "source class")
    require(event["url"] == URL2018 and event["http_status"] == 200, "event source")
    require(event["published_date"] == "2018-02-22", "publication date")
    require(event["event_period"] == "2018-01-22/2018-01-28", "event period")
    require(event["raw_sha256"] == SHA2018 and event["raw_bytes"] == 379832, "bytes not pinned")
    require(event["raw_bytes_versioned"] is False, "do not pretend full bytes are in Git")
    require(event["literal_utf8_counts"] == COUNTS, "literal counts")
    require(event["visible_text_provenance"] == "same HTML article; not independent witnesses", "witness duplication")
    history = src["HIST2025"]
    require(history["url"] == HIST2025 and history["kind"] == "retrospective_secondary_local_history", "history link/class")
    require(history["published_date"] == "2025-08-04" and history["updated_date"] == "2025-08-09", "history date")
    require(history["retrieval_status"] == "WEB_TEXT_VISIBLE_BINARY_NOT_ACQUIRED_HTTP_403_IFRO", "history custody")
    require(history["raw_bytes"] is None and history["raw_sha256"] is None, "false source hash")
    require(history["attributed_researcher"] == "Walber Luide Andrade da Silva", "lineage")
    require(src["MUNI2020"]["reference"] == "research/geo/cgeo20_centro_vila_2020.json", "municipal dependency")
    require(src["MUNI2020"]["survey_geometry_1963"] is None, "invented 1963 survey")
    require(src["IBGE1958"]["reference"] == "research/geo/cgeo17_1958_urban_toponym_crosswalk.json", "IBGE dependency")
    require(src["IBGE1958"]["place_name"] == "Praça Severiano Lima", "1958 transcription")
    require(src["IBGE1958"]["equivalence_to_severino_vieira"] is None, "premature 1958 identification")
    require(src["OSM2026"]["reference"] == "research/geo/cgeo62_praca_severino_vieira.json", "OSM dependency")
    require(src["OSM2026"]["count_named_ways"] == 4, "OSM feature cardinality")
    readings = data["readings"]
    require(len(readings) == 5, "readings")
    require([(x["source"], x["literal"], x["count_in_original_html"]) for x in readings[:2]]
            == [("JGB2018", "Praça Severiano Vieira", 2),
                ("JGB2018", "Praça Severino Vieira", 7)], "2018 textual variants")
    require([(x["source"], x["claimed_event"], x.get("event_year"), x.get("event_date"))
             for x in readings[2:]] == [
                ("HIST2025", "inauguration_of_square_named_for_Severino_Vieira", 1904, None),
                ("HIST2025", "bust_of_Severino_Vieira_in_square", None, "1949-07-08"),
                ("HIST2025", "new_church_of_Senhor_do_Bonfim", 1960, None),
            ], "retrospective dates")
    for x in readings[2:]:
        require(x["primary_contemporary_record"] is None
                and x["verification"] == "secondary_retrospective_claim", "false primary authentication")
    i = data["interpretation"]
    require(i["same_2018_event_venue_named_using_two_spellings_in_one_article"] is True, "2018 editorial link")
    require(i["independent_2018_venue_witnesses"] == 1, "one article is one lineage")
    require(i["historical_place_may_preexist_1963"] == "secondary_retrospective_hypothesis_only", "overclaim")
    for k in ("identity_with_1958_praca_severiano_lima", "identity_with_2020_severino_vieira_geometry",
              "identity_with_modern_osm_ways", "street_or_plaza_rename_document",
              "historical_center_polygon_1963", "event_location_1963", "positional_uncertainty_m"):
        require(i[k] is None, "unsupported geometry/identity: " + k)
    require(i["can_constrain_orbital_reentry"] is False and i["active_constraint"] is False, "false orbital gate")
    return {"source_families": 5, "historical_contemporary_records": 0,
            "distinct_2018_editorial_venues": 1, "orbital_constraint": False}


def verify_live_2018(event):
    req = urllib.request.Request(event["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        require(response.status == 200, "2018 HTTP")
        raw = response.read(1000000)
    require(len(raw) == event["raw_bytes"], "original HTML length changed")
    require(hashlib.sha256(raw).hexdigest() == event["raw_sha256"], "original HTML changed")
    for token, expected in COUNTS.items():
        require(raw.lower().count(token.lower().encode("utf-8")) == expected,
                "2018 raw literal occurrence changed: " + token)
    return {"live_source": "MATCHED_PINNED_2018_HTML", "bytes": len(raw)}


if __name__ == "__main__":
    d = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = validate(d)
    if "--live" in sys.argv:
        result.update(verify_live_2018(d["sources"][0]))
    else:
        result["live_source"] = "NOT_RUN_REMOTE_SOURCE"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
