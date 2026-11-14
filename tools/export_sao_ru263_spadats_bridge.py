#!/usr/bin/env python3
"""C241-L53/L52/L45: archive holdings and plans are not NORAD 528 measurements."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "C241-L53": ("research/tle_custody/sao_ru263_station_files_C241-L53.json",
                  "40bbfda2f2440bae8344f9b42177622e1c3d7eee6aed34560f69e203b01cc473"),
    "C241-L52": ("research/tle_custody/norad_1963_spadats_operational_C241-L52.json",
                  "59de53b50a29c23c5d286b59b72591ee51efb055081f9fd57c29fe3aea8154eb"),
    "C241-L45": ("research/tle_custody/sao_ru478_finding_aid_C241-L45.json",
                  "f51192f1e1776c0c4d35ea4c4bc5ee33182a44823a53fa024139c378423d5812"),
}
OUT = ROOT / "public/data/conde-ru263-spadats-dependency-bridge.json"


def require(value, message):
    if not value:
        raise ValueError("RU263-SPADATS: " + message)


def unique_keys(items):
    result = {}
    for k, v in items:
        require(k not in result, "duplicate key " + k)
        result[k] = v
    return result


def load(root=ROOT):
    loaded, hashes = {}, {}
    for identifier, (path, expected) in SOURCES.items():
        raw = (root / path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if expected is not None:
            require(digest == expected, "source bytes drift " + identifier)
        loaded[identifier] = json.loads(raw, object_pairs_hook=unique_keys)
        hashes[identifier] = digest
    return loaded, hashes


def build(sources, hashes):
    ru, norad, old = (sources[x] for x in ("C241-L53", "C241-L52", "C241-L45"))
    require(ru["schema"] == "conde.sao-ru263-station-records-custody/v1"
            and ru["id"] == "C241-L53", "RU263 identity")
    source = ru["source"]
    require(source["url"] == "https://sirismm.si.edu/EADpdfs/SIA.FARU0263.pdf"
            and source["sha256"] == "0648a4807160099c1c5146f9a90e8ab291af8cb7a0eff1f5a9ca0bc53e074603"
            and source["bytes"] == 192142 and source["pdf_pages"] == 58
            and source["source_class"] == "OFFICIAL_FINDING_AID_NOT_INSTRUMENTAL_OBSERVATIONS",
            "RU263 document custody")
    require(ru["related_conde_evidence"] == ["C241-L43", "C241-L45", "C241-L52"]
            and ru["cross_collection_independent_observations"] == "UNKNOWN"
            and ru["individual_observations_recovered_from_this_finding_aid"] == 0
            and ru["physical_constraints_activated"] == 0
            and ru["impact_at_conde"] == "NOT_ESTABLISHED", "RU263 scope")
    require(all(ru[k] is None for k in (
        "norad_527_observation", "norad_528_observation",
        "norad_529_observation", "norad_528_station",
        "norad_528_utc", "norad_528_sensor_sigma")), "RU263 cannot identify measurements")
    require(ru["norad_528_data_received_by_spadats"] == "UNKNOWN", "RU263 receipt is unknown")
    anchors = ru["anchors"]
    expected_anchors = {
        "RU263-COLD-LAKE-OPERATIONS": (2, 36, 14, 15, "Cold Lake, Canada, 1963-1965"),
        "RU263-COLD-LAKE-ENGINEERING": (8, 67, 43, 44, "Cold Lake, Canada, 1961-1963"),
        "RU263-IRAN-ENGINEERING": (8, 69, 43, 44, "Iran, 1959-1963"),
        "RU263-CURACAO-ENGINEERING": (8, 68, 43, 44, "Curacao, 1959-1963"),
    }
    require(len(anchors) == 4 and {a["id"] for a in anchors} == set(expected_anchors),
            "RU263 box anchors")
    for a in anchors:
        require(tuple(a[k] for k in ("series", "box", "printed_page",
                                      "pdf_page_index_zero_based", "phrase"))
                == expected_anchors[a["id"]], "RU263 page/box/phrase " + a["id"])
        require("not " in a["scope"].lower() or "no " in a["scope"].lower(),
                "RU263 anchor must disclose its inference limit")

    require(norad["schema"] == "c241-l52-norad-spadats-operational/v1"
            and norad["evidence_id"] == "C241-L52"
            and norad["source_kind"] == "CONTEMPORARY_INSTITUTIONAL_SUMMARY_NOT_RAW_TRACKING",
            "NORAD identity/status")
    ns = norad["source"]
    require(ns["url"].endswith("1963%20NORAD%20CONAD%20History%20Jul-Dec.pdf")
            and ns["sha256"] == "eb8682425a393b016642165a9c00b6be8868a27954ddd0e55c40c1e14da425b4"
            and ns["bytes"] == 7111330 and ns["report_date"] == "1964-05-01",
            "NORAD custody/report not observation time")
    expected_events = {
        "JCS_1963_07_17": ("1963-07-17", 70, 55, "administrative-plan-decision"),
        "JCS_NASA_DATA_REQUEST": ("1963-07-17", 70, 55, "data-sharing-request"),
        "NORAD_REPLAN_1963_09": ("1963-09", 71, 56, "planned-system-integration"),
        "NAVY_CALIBRATION_1963_10": ("1963-10", 71, 56, "calibration-plan-change"),
        "COLD_LAKE_COMMS_1963_12": ("1963-12", 71, 56, "communications-availability-context"),
    }
    events = norad["events"]
    require(len(events) == 5 and {x["id"] for x in events} == set(expected_events),
            "NORAD event IDs")
    for event in events:
        require(tuple(event[k] for k in ("date", "pdf_page_index", "printed_page", "kind"))
                == expected_events[event["id"]], "NORAD chronology/locator " + event["id"])
        require(bool(event["finding"]), "NORAD finding text")
    scope = norad["scope"]
    require(all(scope[k] is None for k in (
        "instrumental_observation_527", "instrumental_observation_528",
        "instrumental_observation_529", "station_of_528", "epoch_528_utc",
        "frame_528", "sigma_528", "actual_1963_sao_to_spadats_528_transfer",
        "independent_instrumental_family_count", "physical_piece_528",
        "decay_hour_528", "impact_location_528")), "NORAD scope cannot fill measurements")
    require(scope["physical_constraint_active"] is False
            and scope["orbit_parameters"] == "THETA_UNCHANGED"
            and scope["graph_state"] == "CONTEXT_ONLY_NOT_ACTIVATED", "NORAD activation")
    require(old["schema"] == "conde.sao-ru478-finding-aid-custody/v1"
            and old["id"] == "C241-L45"
            and old["source"]["sha256"] == "e4f2b29b9882cdfac1812b41251b087354e311822d7302e4655a89bc4a06c07e"
            and old["derived_from_same_sao_program"] is True
            and old["individual_observation_utc"] is None
            and old["physical_constraints_activated"] == 0, "RU478 dependency")
    require({a["id"] for a in old["anchors"]} == {
        "RU478-WEATHER-1963", "RU478-AF-NORAD",
        "RU478-MONTHLY-REPORTS", "RU478-TAPE-12546"}, "RU478 anchor IDs")

    def edge(a, b, relation):
        return {"source": a, "target": b, "relation": relation,
                "independent_instrumental_observation": False, "active": False}

    edges = [
        edge("C241-L53", "PDF:RU263", "FINDING_AID_CUSTODIED"),
        edge("C241-L52", "PDF:NORAD1963", "CONTEMPORARY_SUMMARY_CUSTODIED"),
        edge("C241-L45", "PDF:RU478", "EARLIER_SAO_FINDING_AID"),
        edge("PDF:RU263", "PROGRAM:SAO", "COLLECTION_CREATOR_NOT_SENSOR"),
        edge("PDF:RU478", "PROGRAM:SAO", "SAME_PROGRAM_POSSIBLE_OVERLAP"),
        edge("PDF:NORAD1963", "PROGRAM:SPADATS", "PLANNING_HISTORY_NOT_DATA_RECEIPT"),
        edge("EVENT:JCS_NASA_DATA_REQUEST", "H:SAO_TO_SPADATS_528", "REQUEST_NOT_ACTUAL_TRANSFER"),
        edge("EVENT:NORAD_REPLAN_1963_09", "H:NETWORK_INTEGRATION", "PLAN_NOT_COMPLETION"),
        edge("EVENT:COLD_LAKE_COMMS_1963_12", "H:COLD_LAKE_REALTIME", "LATER_COMMUNICATIONS_CONTEXT"),
        edge("H:SAO_TO_SPADATS_528", "LATENT:528:receipt", "RECEIPT_LOG_REQUIRED"),
        edge("H:NETWORK_INTEGRATION", "LATENT:network:independent_instruments", "GENEALOGY_REQUIRED"),
        edge("H:COLD_LAKE_REALTIME", "LATENT:528:station", "NOT_EVIDENCE_OF_528_STATION"),
        edge("H:528_OBSERVATION", "OBS:optical_direction", "RAW_CALIBRATED_ANGLES_REQUIRED"),
        edge("OBS:optical_direction", "MODEL:topocentric_direction_residual", "CONDITIONAL_FORWARD_MODEL"),
        edge("MODEL:topocentric_direction_residual", "LEAN:opticalObservationConstraint", "PENDING_PREMISES_NOT_COMPILED"),
    ]
    edges.extend(edge("PDF:RU263", "FILE:" + a["id"], "BOX_PAGE_LOCATOR_NOT_CONTENTS")
                 for a in anchors)
    edges.extend(edge("PDF:NORAD1963", "EVENT:" + e["id"], "DATE_RECORDED_IN_1964_REPORT")
                 for e in events)
    edges.extend(edge("FILE:" + a["id"], "H:528_OBSERVATION",
                      "SUGGESTED_ARCHIVAL_SEARCH_NOT_DETECTION") for a in anchors)
    latents = [{"id": "LATENT:528:" + name, "value": None, "unit": unit,
                "activation": False, "source_status": "PENDING_PRIMARY_OBSERVATION"}
               for name, unit in (
                   ("receipt", "document_identifier"), ("station", "station_identifier"),
                   ("epoch", "UTC"), ("ra", "radians"), ("dec", "radians"),
                   ("frame", "reference_frame"), ("covariance", "radians_squared"))]
    latents.append({"id": "LATENT:network:independent_instruments", "value": None,
                    "unit": "count_unknown", "activation": False,
                    "source_status": "PENDING_INSTRUMENT_GENEALOGY"})
    return {
        "schema": "conde.ru263-spadats-dependency-bridge/v1",
        "id": "ABELHA-C241-L53-L52-01",
        "sources": [{"occurrence_id": ident, "manifest_path": SOURCES[ident][0],
                     "manifest_sha256": hashes[ident], "pdf_url": src["source"]["url"],
                     "pdf_sha256": src["source"]["sha256"],
                     "document_class": src["source"].get("source_class",
                          sources[ident].get("source_kind"))}
                    for ident, src in (("C241-L53", ru), ("C241-L52", norad), ("C241-L45", old))],
        "related_matrix_occurrence": None,
        "catalogue_target_candidates": [
            {"norad_id": t, "measured_by_these_manifests": False,
             "observation_utc": None, "station": None,
             "instrumental_independence": None, "activation": False}
            for t in (527, 528, 529)],
        "anchors": [{"id": a["id"], "box": a["box"], "series": a["series"],
                     "printed_page": a["printed_page"],
                     "pdf_page_index_zero_based": a["pdf_page_index_zero_based"],
                     "classification": "INVENTORY_LOCATOR_NOT_OBSERVATION"}
                    for a in anchors],
        "events": [{"id": e["id"], "date_as_documented": e["date"],
                    "printed_page": e["printed_page"],
                    "pdf_page_index_zero_based": e["pdf_page_index"],
                    "classification": e["kind"], "observation_epoch_528_utc": None}
                   for e in events],
        "graph": edges,
        "hypotheses": ["H:SAO_TO_SPADATS_528", "H:NETWORK_INTEGRATION",
                       "H:COLD_LAKE_REALTIME", "H:528_OBSERVATION"],
        "observable_operator": {"name": "topocentric_direction_residual",
                                 "inputs_required": ["target_528_identity", "raw_angles",
                                     "station_geodesy", "epoch_utc", "frame",
                                     "clock_calibration", "instrument_covariance"],
                                 "status": "CONDITIONAL_NOT_EVALUABLE"},
        "lean_candidate": "opticalObservationConstraint",
        "lean_status": "PENDING_PREMISES_NO_COMPILED_EMPIRICAL_PROOF",
        "latents": latents,
        "independent_instrumental_families": None,
        "confirmed_norad_528_observations_from_manifests": 0,
        "unknown_observations_in_unopened_archive": None,
        "actual_1963_sao_to_spadats_528_transfer": None,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Read original RU263 boxes 36/67 and RU478 boxes 59/65 plus SPADATS intake logs; identify NORAD 528, station, UTC, calibration, RA/Dec, frame, covariance before activating physics.",
    }


def render(root=ROOT):
    sources, hashes = load(root)
    return (json.dumps(build(sources, hashes), ensure_ascii=False,
                       sort_keys=True, indent=2) + "\n").encode()


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write-site", action="store_true")
    mode.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    output = render()
    if args.write_site:
        OUT.write_bytes(output)
    elif args.check_site:
        require(OUT.read_bytes() == output, "site bytes diverged")
    else:
        print(output.decode(), end="")


if __name__ == "__main__":
    main()
