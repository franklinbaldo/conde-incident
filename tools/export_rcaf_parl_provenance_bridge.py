#!/usr/bin/env python3
"""RCAF Cold Lake and PARL: two facilities, system-level reports, zero named 528 returns."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "C241-L55": ("research/tle_custody/rcaf_roundel_spadats_1963_C241-L55.json",
                  "7e7a1fdc831924f8ce4e012e0d293bfa71fc861d"),
    "C241-L56": ("research/tle_custody/norad_parl_cold_lake_addendum_C241-L56.json",
                  "ce1dcef9a8469362a72e1d7ceb7d68e26cc88fdb"),
}
OUT = ROOT / "public/data/conde-rcaf-parl-provenance-bridge.json"
NORAD_PDF_SHA = "eb8682425a393b016642165a9c00b6be8868a27954ddd0e55c40c1e14da425b4"
RCAF_PDF_SHA = "830a7707f3ce611172ff6b6942794654b1fc30d564f97e2b7bf78f2c981657b3"

def require(ok, msg):
    if not ok:
        raise ValueError("RCAF-PARL bridge: " + msg)

def unique_keys(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, "duplicate JSON key " + k)
        obj[k] = v
    return obj

def load(root=ROOT):
    found, digests = {}, {}
    for ident, (name, blob_sha) in SOURCES.items():
        raw = (root / name).read_bytes()
        git_blob = hashlib.sha1(("blob %d\0" % len(raw)).encode() + raw).hexdigest()
        require(git_blob == blob_sha, "source blob drift " + ident)
        found[ident] = json.loads(raw, object_pairs_hook=unique_keys)
        digests[ident] = hashlib.sha256(raw).hexdigest()
    return found, digests

def build(sources, digests):
    rcaf, norad = sources["C241-L55"], sources["C241-L56"]
    require(rcaf["schema"] == "conde.c241-l55-rcaf-spadats-custody/v1"
            and rcaf["evidence_id"] == "C241-L55", "RCAF identity")
    s = rcaf["source"]
    require(s["sha256"] == RCAF_PDF_SHA and s["bytes"] == 36226444
            and s["periodical"] == "Roundel" and s["issue"] == "September 1963"
            and s["publication_date_precision"] == "MONTH_ONLY"
            and s["printed_page"] == 5 and s["pdf_page_index_zero_based"] == 6
            and s["source_class"] == "CONTEMPORARY_RCAF_EDITORIAL_ACCOUNT_NOT_RAW_SENSOR_DATA",
            "RCAF PDF and page scope")
    ra = {a["id"]: a for a in rcaf["anchors"]}
    require(len(rcaf["anchors"]) == len(ra) == 3 and set(ra) ==
            {"RCAF_COLD_LAKE_SPADATS", "DRB_PRINCE_ALBERT", "RCAF_CAMERA_PHOTO"},
            "RCAF anchors")
    require("Baker-Nunn camera installation at RCAF Station Cold Lake"
            in ra["RCAF_COLD_LAKE_SPADATS"]["text"], "Cold Lake camera quote")
    require("Prince Albert" in ra["DRB_PRINCE_ALBERT"]["text"], "Prince Albert quote")
    require("work with a satellite tracking camera" in ra["RCAF_CAMERA_PHOTO"]["text"],
            "photo quote does not locate instrument")
    require(rcaf["independence"]["independent_instrumental_observations_recovered"] == 0
            and rcaf["independence"]["duplicate_528_measurement_with_other_ledgers"] is None
            and rcaf["cold_lake_named_observations_recovered"] == 0
            and rcaf["physical_constraint_active"] is False
            and rcaf["orbit_parameters"] == "THETA_UNCHANGED"
            and rcaf["impact_at_conde"] == "NOT_ESTABLISHED", "RCAF epistemic guard")
    require(all(rcaf[k] is None for k in (
        "norad_528_observation_utc", "norad_528_observation_station",
        "norad_528_sensor_sigma", "norad_528_transmission_receipt",
        "norad_528_frame")), "RCAF no 528 observables")
    require(norad["schema"] == "conde.c241-l56-parl-feed/v1"
            and norad["id"] == "C241-L56" and norad["parent_id"] == "C241-L52"
            and norad["parent_sha256"] == "59de53b50a29c23c5d286b59b72591ee51efb055081f9fd57c29fe3aea8154eb",
            "NORAD L56 parent identity")
    require(norad["source_sha256"] == NORAD_PDF_SHA
            and norad["source_bytes"] == 7111330
            and norad["source_pages"] == 122
            and norad["source_independence"] == "SAME_BINARY_AS_C241-L52_NOT_NEW_SOURCE_OR_SENSOR",
            "NORAD binary must not be double counted")
    na = {a["id"]: a for a in norad["anchors"]}
    require(len(norad["anchors"]) == len(na) == 3 and set(na) ==
            {"COLD_LAKE_CONTROL", "PRINCE_ALBERT_PART_TIME", "PRINCE_ALBERT_JAN1964"},
            "NORAD anchor IDs")
    require((na["COLD_LAKE_CONTROL"]["pdf_page_zero_based"],
             na["COLD_LAKE_CONTROL"]["printed_page"]) == (70,55)
            and "operational control of CINCNORAD" in na["COLD_LAKE_CONTROL"]["phrase"],
            "Cold Lake page/control")
    for ident in ("PRINCE_ALBERT_PART_TIME", "PRINCE_ALBERT_JAN1964"):
        require((na[ident]["pdf_page_zero_based"], na[ident]["printed_page"]) == (72,57),
                "PARL locator " + ident)
    require("part-time basis" in na["PRINCE_ALBERT_PART_TIME"]["phrase"]
            and "still providing information" in na["PRINCE_ALBERT_JAN1964"]["phrase"],
            "PARL historical scope")
    require("PARL" in norad["distinction"] and "Baker-Nunn" in norad["distinction"],
            "radar and optical separation")
    scope = norad["scope"]
    require(all(scope[k] is None for k in (
        "named_527", "named_528", "named_529", "utc_528", "station_of_528",
        "frame_528", "sigma_528", "data_receipt_528",
        "independent_sensors_528", "decay_hour_528", "fall_location_528")),
            "NORAD cannot be promoted to target data")
    require(scope["physical_constraint_active"] is False
            and scope["theta"] == "THETA_UNCHANGED", "NORAD physical guard")
    require(set(digests) == set(SOURCES)
            and all(len(v) == 64 for v in digests.values()), "manifest sha256")

    def edge(a, b, relation):
        return {"source": a, "target": b, "relation": relation,
                "active": False, "instrumental_528_measurement": False}
    graph = [
        edge("C241-L55", "PDF:RCAF_ROUNDEL_1963_09", "CONTEMPORARY_EDITORIAL_PDF"),
        edge("C241-L56", "PDF:NORAD1963_JUL_DEC", "SAME_BINARY_AS_C241_L52"),
        edge("C241-L52", "PDF:NORAD1963_JUL_DEC", "PARENT_SOURCE_NOT_NEW_SENSOR"),
        edge("PDF:RCAF_ROUNDEL_1963_09", "CLAIM:RCAF_COLD_LAKE_SPADATS", "PAGE_5_SYSTEM_LEVEL"),
        edge("PDF:RCAF_ROUNDEL_1963_09", "CLAIM:DRB_PRINCE_ALBERT", "PAGE_5_NETWORK_DESCRIPTION"),
        edge("PDF:RCAF_ROUNDEL_1963_09", "CLAIM:RCAF_CAMERA_PHOTO", "CAPTION_WITHOUT_TIME_SITE"),
        edge("PDF:NORAD1963_JUL_DEC", "CLAIM:COLD_LAKE_CONTROL", "PAGE_55_INSTITUTIONAL_CONTROL"),
        edge("PDF:NORAD1963_JUL_DEC", "CLAIM:PRINCE_ALBERT_PART_TIME", "PAGE_57_SPADATS_GENERAL_FEED"),
        edge("PDF:NORAD1963_JUL_DEC", "CLAIM:PRINCE_ALBERT_JAN1964", "PAGE_57_LATER_ADMINISTRATIVE_STATUS"),
        edge("CLAIM:RCAF_COLD_LAKE_SPADATS", "SITE:COLD_LAKE_OPTICAL_CAMERA", "RCAF_INPUT_AT_NETWORK_LEVEL"),
        edge("CLAIM:COLD_LAKE_CONTROL", "SITE:COLD_LAKE_OPTICAL_CAMERA", "OPERATIONAL_CONTROL_NOT_528_DATA"),
        edge("CLAIM:DRB_PRINCE_ALBERT", "SITE:PRINCE_ALBERT_RADAR", "DIFFERENT_SITE_SENSOR_TYPE"),
        edge("CLAIM:PRINCE_ALBERT_PART_TIME", "SITE:PRINCE_ALBERT_RADAR", "PART_TIME_FEED_UNSPECIFIED_TARGET"),
        edge("CLAIM:PRINCE_ALBERT_JAN1964", "H:PARL_528_RETURN", "POST_1963_STATUS_NOT_MEASUREMENT"),
        edge("CLAIM:RCAF_CAMERA_PHOTO", "H:COLD_LAKE_528_ANGLES", "PHOTO_NOT_OBJECT_OR_SITE_PROOF"),
        edge("SITE:COLD_LAKE_OPTICAL_CAMERA", "H:COLD_LAKE_528_ANGLES", "NAMED_528_EXPOSURE_REQUIRED"),
        edge("SITE:PRINCE_ALBERT_RADAR", "H:PARL_528_RETURN", "NAMED_528_RADAR_RETURN_REQUIRED"),
        edge("H:COLD_LAKE_528_ANGLES", "LEAN:opticalObservationConstraint", "PREMISES_PENDING"),
        edge("H:PARL_528_RETURN", "LEAN:radarObservationConstraintCandidate", "PREMISES_PENDING"),
        edge("LEAN:opticalObservationConstraint", "PARAM:528_optical_direction", "INACTIVE_NO_ANGLES"),
        edge("LEAN:radarObservationConstraintCandidate", "PARAM:528_radar_range", "INACTIVE_NO_RANGE"),
        edge("H:COLD_LAKE_528_ANGLES", "LATENT:528:spadats_receipt", "RECEIPT_REQUIRED"),
        edge("H:PARL_528_RETURN", "LATENT:528:spadats_receipt", "RECEIPT_REQUIRED"),
    ]
    latent_units = {
        "target_id": "NORAD_catalogue_id",
        "epoch_utc": "UTC",
        "station": "station_identifier",
        "observable": "angle_or_range",
        "reference_frame": "frame_id",
        "clock_calibration": "time_bias_distribution",
        "covariance": "instrument_covariance",
        "spadats_receipt": "message_or_log_id",
        "family_independence": "sensor_genealogy",
    }
    latents = [
        {"id": "LATENT:528:" + ident, "unit": unit, "value": None,
         "activation": False, "status": "MISSING_OBJECT_SPECIFIC_PRIMARY_RECORD"}
        for ident, unit in latent_units.items()
    ]
    params = [
        {"id": x, "value": None, "activation": False}
        for x in ("PARAM:528_optical_direction", "PARAM:528_radar_range",
                  "PARAM:528_station_link", "PARAM:528_clock_bias")
    ]
    return {
        "schema": "conde.rcaf-parl-provenance-bridge/v1",
        "id": "ABELHA-C241-L55-L56-01",
        "sources": [
            {"occurrence_id": k, "manifest_path": SOURCES[k][0],
             "manifest_sha256": digests[k], "manifest_git_blob_sha1": SOURCES[k][1],
             "pdf_sha256": RCAF_PDF_SHA if k == "C241-L55" else NORAD_PDF_SHA,
             "pdf_url": s["url"] if k == "C241-L55" else norad["source_url"],
             "class": "CONTEMPORARY_EDITORIAL_NOT_SENSOR" if k == "C241-L55"
                     else "NORAD_REPORT_DUPLICATE_OF_C241-L52"}
            for k, s in (("C241-L55", rcaf["source"]), ("C241-L56", norad))
        ],
        "existing_parent": {"occurrence_id": "C241-L52", "pdf_sha256": NORAD_PDF_SHA,
                            "duplicate_new_measurement": False},
        "document_anchors": [
            {"occurrence_id": "C241-L55", "anchor_id": a["id"],
             "printed_page": 5, "pdf_page_zero_based": 6,
             "epistemic_status": "NETWORK_DESCRIPTION_NOT_528_OBSERVATION"}
            for a in rcaf["anchors"]
        ] + [
            {"occurrence_id": "C241-L56", "anchor_id": a["id"],
             "printed_page": a["printed_page"],
             "pdf_page_zero_based": a["pdf_page_zero_based"],
             "epistemic_status": "ADMINISTRATIVE_HISTORY_NOT_528_OBSERVATION"}
            for a in norad["anchors"]
        ],
        "stations": [
            {"id": "SITE:COLD_LAKE_OPTICAL_CAMERA", "instrument": "Baker-Nunn optical",
             "confirmed_528_measurements_in_sources": 0},
            {"id": "SITE:PRINCE_ALBERT_RADAR", "instrument": "DRB radar",
             "confirmed_528_measurements_in_sources": 0},
        ],
        "graph": graph,
        "hypotheses": ["H:COLD_LAKE_528_ANGLES", "H:PARL_528_RETURN"],
        "lean_candidates": ["opticalObservationConstraint", "radarObservationConstraintCandidate"],
        "lean_status": "CONDITIONAL_UNCOMPILED_NO_EMPIRICAL_PREMISES",
        "simulator_parameters": params,
        "latents": latents,
        "named_527_528_529_observations_recovered": 0,
        "independent_instrumental_families_established_for_528": None,
        "physical_constraint_active": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_acquisition": "Recover 528-specific Cold Lake exposure or PARL radar return with UTC, instrument, station geodesy, calibration, frame, uncertainties and SPADATS receipt; do not infer two independent 528 sensors from network descriptions.",
    }

def render(root=ROOT):
    data, digests = load(root)
    return (json.dumps(build(data, digests), ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode()

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write-site", action="store_true")
    mode.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    raw = render()
    if args.write_site:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(raw)
    elif args.check_site:
        require(OUT.read_bytes() == raw, "published JSON drift")
    else:
        print(raw.decode(), end="")

if __name__ == "__main__":
    main()
