#!/usr/bin/env python3
"""C241-L45: source-locked SAO RU478 archive routes -> pending scientific operands."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .tle_sao_ru478_finding_aid_c241_l45 import audit
else:
    from tle_sao_ru478_finding_aid_c241_l45 import audit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "research/tle_custody/sao_ru478_finding_aid_C241-L45.json"
CROSSWALK = "research/constraints/morcego_sao_ru478_1963_crosswalk.json"
P17 = "public/data/conde-sao-p17-scope-bridge.json"
OUT = ROOT / "public/data/conde-sao-ru478-scientific-bridge.json"
PINNED = {
    MANIFEST: "f51192f1e1776c0c4d35ea4c4bc5ee33182a44823a53fa024139c378423d5812",
    CROSSWALK: "c67e9019f179683b7304f52a2de6a41fef0e2df8792ac1977bb2aa3b703a4201",
    P17: "4f8d9621693c91c09383058e040a6a3f73282e45c9a471db49f3582fa973ca25",
}
ANCHOR_TO_OCCURRENCE = {
    "RU478-WEATHER-1963": "MOR-RU478-03",
    "RU478-AF-NORAD": None,
    "RU478-MONTHLY-REPORTS": "MOR-RU478-01",
    "RU478-TAPE-12546": "MOR-RU478-02",
}
SOURCE_FAMILY = "SMITHSONIAN_SAO_PROGRAM"


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("SAO RU478 scientific bridge: " + msg)


def build(manifest: dict, crosswalk: dict, p17: dict) -> dict:
    audit(manifest, crosswalk)
    require(crosswalk["schema"] == "conde.sao-archive-crosswalk/v1"
            and crosswalk["status"] == "ARCHIVAL_AND_SITE_METADATA_CONNECTED_NO_PHYSICAL_OBSERVATION",
            "crosswalk epistemic scope changed")
    source = next(s for s in crosswalk["sources"] if s["id"] == "RU478")
    require(source["source_sha256"] is None
            and source["grade"] == "primary_for_archive_holdings_only",
            "earlier crosswalk custody history altered")
    require(crosswalk["source_independence"] ==
            "SAO RU301, RU478 and SAO SR353 are different documents from one tracking program, not three independent observations.",
            "same-program dependence changed")
    require(p17["schema"] == "conde.sao-p17-selected-catalogue-bridge/v1"
            and p17["source_occurrence"] == "C241-L44"
            and p17["independent_instrumental_observations_added"] == 0
            and p17["activation"] is False,
            "SAO P17 source independence or scope changed")
    occurrences = {o["id"]: o for o in crosswalk["occurrences"]}
    variables = crosswalk["variables"]
    require(len(variables) == 12 and len({v["id"] for v in variables}) == 12,
            "crosswalk variable set changed")
    require(len(crosswalk["edges"]) == 6, "crosswalk dependencies changed")
    require(all(not e["hard_physical_constraint"] for e in crosswalk["edges"]),
            "hard constraint fabricated")
    require(all(o["independence_family"] == SOURCE_FAMILY
                and not o["original_instrument_measurement"]
                and not o["hard_physical_constraint"]
                for o in occurrences.values()), "archive entry promoted to measurement")
    require(all(v["value"] is None for v in variables if v["uncertainty"] == "UNKNOWN_NOT_ZERO"),
            "unknown observation parameter filled without a new source")
    require(all(v["kind"] in ("categorical", "code") for v in variables
                if v["value"] is not None), "metadata mistaken for observation")
    require(all(h["id"] != "H_OPTICAL_528_OBSERVED" or h["status"] == "OPEN"
                for h in crosswalk["hypotheses"]), "unverified observation asserted")
    require({o["id"] for o in crosswalk["occurrences"]} >=
            {o for o in ANCHOR_TO_OCCURRENCE.values() if o is not None}
            | {"MOR-RU478-04"}, "original Morcego occurrence missing")

    pdf_node = "SAO:RU478:ORIGINAL_FINDING_AID"
    graph = [{"from": "C241-L45", "to": pdf_node,
              "relation": "ORIGINAL_OFFICIAL_PDF_HOLDINGS_ONLY",
              "independent_observation": False},
             {"from": pdf_node, "to": "C241-L44",
              "relation": "RELATED_SAO_PROGRAM_NOT_PROVEN_SHARED_TARGET_DATA",
              "independent_observation": False}]
    archive_routes = []
    for anchor in manifest["anchors"]:
        locator = anchor["id"]
        occurrence = ANCHOR_TO_OCCURRENCE[locator]
        graph.append({"from": pdf_node, "to": locator,
                      "relation": "PRINTED_PAGE_BOX_LOCATOR",
                      "independent_observation": False})
        if occurrence:
            item = occurrences[occurrence]
            require(item["source_id"] == "RU478", "crosswalk occurrence wrong source")
            graph.append({"from": locator, "to": occurrence,
                          "relation": "PREVIOUSLY_CATALOGUED_ARCHIVE_ROUTE_NOT_NEW_SENSOR",
                          "independent_observation": False})
        archive_routes.append({
            "id": locator, "box": anchor["box"],
            "printed_page": anchor["printed_page"],
            "pdf_page_index_zero_based": anchor["pdf_page_index_zero_based"],
            "phrase": anchor["phrase"], "finding": anchor["fact"],
            "upstream_occurrence": occurrence,
            "source_class": "ARCHIVAL_LOCATOR_ONLY",
            "activation": False,
        })

    for norad, suffix in ((527, "A"), (528, "B"), (529, "C")):
        graph.append({
            "from": "RU478-TAPE-12546",
            "to": f"SAO-RU478:TRACK_SEARCH:{norad}",
            "relation": "SEARCH_CANDIDATE_NOT_PRINTED_TARGET_IDENTIFICATION",
            "independent_observation": False,
        })
    latent = [
        {"id": v["id"], "kind": v["kind"], "value": v["value"],
         "source_occurrence": v["source_occurrence"],
         "uncertainty": v["uncertainty"],
         "metadata_only": v["value"] is not None,
         "physical_activation": False}
        for v in variables
    ]
    return {
        "schema": "conde.sao-ru478-scientific-bridge/v1",
        "id": "ABELHA-C241-L45-RU478-01",
        "source_occurrence": "C241-L45",
        "source": {"url": manifest["source"]["url"],
                   "original_pdf_sha256": manifest["source"]["sha256"],
                   "original_pdf_bytes": manifest["source"]["bytes"],
                   "pdf_pages": manifest["source"]["pdf_pages"],
                   "source_class": manifest["source"]["source_class"],
                   "hash_scope": "COMPLETE_FINDING_AID_PDF_NOT_INSTRUMENTAL_LOG",
                   "independence_family": SOURCE_FAMILY},
        "inputs": [{"path": p, "sha256": h} for p, h in PINNED.items()],
        "archive_routes": archive_routes,
        "dependency_graph": graph,
        "upstream_variable_dependencies": crosswalk["edges"],
        "upstream_hypotheses": crosswalk["hypotheses"],
        "simulator_latent_parameters": latent,
        "object_search_candidates": [
            {"norad_id": n, "intldes": f"1963-003{s}",
             "target_observation_id": None,
             "epoch_utc": None, "station": None, "ra_dec_radians": None,
             "reference_frame": None, "angle_sigma_radians": None,
             "clock_correction_seconds": None, "activation": False}
            for n, s in ((527, "A"), (528, "B"), (529, "C"))
        ],
        "conditional_forward_operator": "RADEC_from_orbit_station_epoch",
        "candidate_restriction": "IF_TARGET_ID_STATION_TIME_FRAME_ANGLE_SIGMA_AND_CLOCK_CALIBRATED_THEN_ANGULAR_RESIDUAL",
        "lean_candidate": "Conde1963.saoRU478FindingAidRoutes",
        "lean_status": "DOCUMENTARY_PREDICATE_CANDIDATE_NOT_COMPILED_PHYSICAL_THEOREM",
        "not_covered_by_new_pdf_locators": ["MOR-RU478-04"],
        "negative_scope": "NO_TARGET_527_528_529_IDENTIFIED_IN_FOUR_INVENTORY_ANCHORS",
        "global_nonobservation_proved": False,
        "independent_instrumental_observations_added": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Acquire box59 November 1963 observation report, box65 tape12546 contents and box51-52 station/clock cards; verify target, date, station, angular error and WWV correction.",
    }


def render(root: Path = ROOT) -> bytes:
    documents = {}
    for path, expected in PINNED.items():
        raw = (root / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected,
                "pinned input byte drift: " + path)
        documents[path] = json.loads(raw)
    model = build(documents[MANIFEST], documents[CROSSWALK], documents[P17])
    return (json.dumps(model, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--write-site", action="store_true")
    p.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    data = render()
    if args.write_site:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(data)
    elif args.check_site:
        require(OUT.read_bytes() == data, "published JSON differs")
    else:
        print(data.decode(), end="")


if __name__ == "__main__":
    main()
