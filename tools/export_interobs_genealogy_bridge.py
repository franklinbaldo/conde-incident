#!/usr/bin/env python3
"""Source-locked INTEROBS genealogy and conditional optical observable contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "C241-LONTRA-R38": ("research/tle_custody/konkoly_interobs_1963_C241-LONTRA-R38.json", "d0c2dbc9e661eaa8fcb8fd1e8155d62709e604e2eb2c6bfdad1f2a806cb6bb76"),
    "C241-LONTRA-R39": ("research/tle_custody/baja_1966_yearbook_interobs_C241-LONTRA-R39.json", "630167657fabebb51243ebb411a62c21bcada307da76c86203246c7f0f352ffc"),
    "C241-LONTRA-R40": ("research/tle_custody/interobs_1968_closure_preface_C241-LONTRA-R40.json", "d4ebdfddcad5e36927067b344a794b9b9756f205f222fff625ae4bb5147702db"),
    "C241-LONTRA-R41": ("research/tle_custody/interobs_ftd_translation_C241-LONTRA-R41.json", "d8a99d9b41ee1e11fa23c043535f8e8c313ae49a0ac8f9e2b1157c0a93471889"),
}
OUTPUT = ROOT / "public/data/conde-interobs-genealogy-bridge.json"


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("INTEROBS: " + msg)


def build(s: dict) -> dict:
    require(set(s) == set(SOURCES), "unexpected sources")
    r38, r39, r40, r41 = (s[k] for k in SOURCES)
    require(all(s[k]["id"] == k for k in SOURCES), "source ID changed")
    require(r38["study"]["object_is_1963_003_abc"] is False
            and r38["study"]["campaign_includes_1963_nov_07_to_09"] is False
            and r38["study"]["object_designation"] == "1960 epsilon 3 (Sputnik 4 cabin)"
            and r38["study"]["fixes_total_in_table_2"] == 793
            and r38["limits"]["target_observations_identified"] is False,
            "different-object observations were promoted")
    require(r39["report"]["reported_observation_years"] == [1963, 1964]
            and r39["report"]["cited_publication_volumes"] == ["Folge I", "Folge II"]
            and r39["report"]["campaign_coverage_1963_11_07_to_09"] is None
            and r39["report"]["listed_satellite_codes_proven_to_be_527_528_529"] is False
            and r39["source"]["publication_year"] == 1965
            and r39["source"]["cover_year"] == 1966
            and r39["source"]["original_interobs_campaign_volumes_retrieved"] is False,
            "Baja yearbook scope changed")
    require(r40["source"]["publication_year"] == 1968
            and r40["source"]["covered_observation_year"] == 1966
            and r40["preface"]["describes_satellite_grouped_summary_list_1"] is True
            and r40["preface"]["describes_satellite_grouped_observation_material_list_2"] is True
            and r40["preface"]["actual_list_1_or_list_2_retrieved"] is False
            and r40["preface"]["november_1963_campaign_confirmed"] is False
            and r40["source"]["complete_volume_retrieved"] is False,
            "1968 preface scope changed")
    doc, access, report, scope = (r41[k] for k in ("document", "access", "report", "scope"))
    require(doc["report_number"] == "FTD-HT-23-856-68" and doc["accession"] == "AD 684833"
            and doc["original_year"] == 1967 and doc["translation_date"] == "1968-09-20"
            and doc["original_copy_retrieved"] is False
            and access["critical_printed_pages"] == [18, 19]
            and access["cover_and_critical_pages_visually_inspected"] is True
            and access["full_pdf_sha256"] is None
            and access["full_pdf_bytes"] is None
            and access["downloaded_pdf_replay"] == "NOT_RUN"
            and report["positions_approximate_by_year"] == {"1963": 600, "1964": 6400, "1965": 12200, "1966": 40000}
            and report["positions_are_approximate"] is True
            and report["first_detailed_observation_month"] == "August"
            and report["original_station_logs_retrieved"] is False
            and scope["target_norad_ids"] == [527, 528, 529]
            and scope["target_observations_identified"] is False
            and scope["target_specific_1963_11_07_to_09_campaign_confirmed"] is False,
            "USAF translation claimed unsupported instrumental measurements")
    for k in SOURCES:
        limits = s[k].get("limits", s[k].get("scope"))
        require(limits["orbital_constraints_activated"] == 0, "physical activation in " + k)
        if k != "C241-LONTRA-R41":
            require(limits["new_target_orbital_measurements"] == 0, "target observations added in " + k)
    require(r38["source"]["sha256"] == "70a0e99bf61528d28b48f583295a4984ae2b9056595d1bb9d7a626a61a47ebe5"
            and r39["source"]["sha256"] == "8061e6c164836e6b6e0e465be801fcb891002204bd3a523b4eda43a81d8d459a"
            and r40["source"]["sha256"] == "997ff8bed4924b9cfcba7a018ebeed176ac9602e0484e41c899235b2515e110c",
            "source custody changed")

    def edge(a: str, b: str, relation: str, independence: str = "NOT_ESTABLISHED") -> dict:
        return {"from": a, "to": b, "relation": relation,
                "physical_measurement_independence": independence, "activation": False}
    graph = [
        edge("SOVIET_INTEROBS_COMPILATION_1967", "USAF_FTD_TRANSLATION_1968_AD684833", "TRANSLATION_OF_SAME_WORK", "SAME_WORK_NOT_NEW_SENSOR"),
        edge("USAF_FTD_TRANSLATION_1968_AD684833", "C241-LONTRA-R41", "VIEWER_COPY_UNHASHED", "SAME_WORK_NOT_NEW_SENSOR"),
        edge("C241-LONTRA-R38", "INTEROBS_FOLGE_I_II", "BIBLIOGRAPHIC_REFERENCE_UNREAD"),
        edge("C241-LONTRA-R39", "INTEROBS_FOLGE_I_II", "YEARBOOK_REPORTS_PUBLICATION_UNREAD"),
        edge("C241-LONTRA-R40", "INTEROBS_LIST_1_2", "ISSUE_7_STRUCTURE_ONLY_NOT_1963_CONTENT"),
        edge("C241-LONTRA-R41", "INTEROBS_FOLGE_I_II", "REPORT_CITES_SERIES_NOT_PRIMARY_DATA"),
        edge("INTEROBS_FOLGE_I_II", "H_INTEROBS_528_NOV1963_OBS", "SEARCH_CANDIDATE_NOT_OBSERVATION"),
        edge("H_INTEROBS_528_NOV1963_OBS", "OPTICAL_DIRECTION_RA_DEC_528", "REQUIRES_TARGET_STATION_TIME_FRAME_CALIBRATION"),
        edge("OPTICAL_DIRECTION_RA_DEC_528", "SIMULATOR_528_OPTICAL_LIKELIHOOD", "CONDITIONAL_OPERATOR_NOT_EVALUATED"),
    ]
    latents = ("target_identifier", "station_geodetic_position_1963", "epoch_utc_and_clock_sigma",
               "optical_ra_dec_observable", "reference_frame_and_reduction", "angular_covariance")
    return {
        "schema": "conde.interobs-genealogy-scientific-bridge/v1",
        "id": "ABELHA-INTEROBS-R38-R41-01",
        "input_sha256": {k: {"path": p, "sha256": h} for k, (p, h) in SOURCES.items()},
        "source_occurrences": list(SOURCES),
        "matrix_occurrence": None,
        "dependency_graph": graph,
        "source_custody": [
            {"source_occurrence": "C241-LONTRA-R38", "source_url": r38["source"]["url"],
             "representation": "TRANSCRIBED_HTML_NOT_ORIGINAL_PRINT_FACSIMILE", "source_sha256": r38["source"]["sha256"],
             "observed_target": "1960 epsilon 3 / Sputnik 4", "target_527_529": False},
            {"source_occurrence": "C241-LONTRA-R39", "source_url": r39["source"]["url"],
             "representation": "1965_YEARBOOK_ORIGINAL_PAGE_PDF", "source_sha256": r39["source"]["sha256"],
             "printed_page": r39["source"]["printed_page"], "target_527_529": None},
            {"source_occurrence": "C241-LONTRA-R40", "source_url": r40["source"]["pdf_url"],
             "representation": "1968_PREFACE_EXCERPT_ONLY", "source_sha256": r40["source"]["sha256"],
             "printed_page": r40["source"]["preface_printed_page"], "target_527_529": None},
            {"source_occurrence": "C241-LONTRA-R41", "source_url": doc["facsimile_viewer"],
             "representation": "USAF_1968_TRANSLATION_VIEWED_NOT_DOWNLOADED", "source_sha256": None,
             "printed_pages": access["critical_printed_pages"], "target_527_529": None},
        ],
        "approximate_interobs_positions_1963_all_objects": 600,
        "approximate_position_count_is_not_target_count": True,
        "hypotheses": [
            {"id": "H_INTEROBS_528_NOV1963_OBS", "status": "OPEN_UNVERIFIED", "target": 528,
             "required": "Folge I-II List 1 target identifiers and List 2 dated station records"},
            {"id": "H_SPUTNIK4_1963_ROWS_ARE_528", "status": "REJECTED_DIFFERENT_OBJECT"},
            {"id": "H_600_POSITIONS_IMPLY_528_TRACK", "status": "UNSUPPORTED_AGGREGATE_TO_TARGET_TRANSFER"},
        ],
        "lean_candidate": "Conde1963.interobsDocumentarySourceDependency",
        "lean_status": "DOCUMENTARY_CANDIDATE_NOT_COMPILED_AS_ORBITAL_RESTRICTION",
        "simulator_operator": "CONDITIONAL_TOPOCENTRIC_OPTICAL_RA_DEC_RESIDUAL",
        "simulator_latent_parameters": [
            {"id": f"INTEROBS:{norad}:{parameter}", "value": None, "uncertainty": "UNQUANTIFIED",
             "activation": False, "source_candidates": list(SOURCES)}
            for norad in (527, 528, 529) for parameter in latents
        ],
        "independent_target_observations_added": 0,
        "activation": False, "physical_domain_effect": "THETA_UNCHANGED",
        "follow_up": "Recover full Folge I-II Lists 1/2 and original station logs; verify 1963-11-07/09 target aliases, station, time, frame, instrument uncertainty, and source independence before activating optical residual.",
    }


def render(root: Path = ROOT) -> bytes:
    ledgers = {}
    for source_id, (path, digest) in SOURCES.items():
        raw = (root / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "manifest SHA drift: " + source_id)
        ledgers[source_id] = json.loads(raw)
    return (json.dumps(build(ledgers), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--write-site", action="store_true")
    p.add_argument("--check-site", action="store_true")
    a = p.parse_args()
    output = render()
    if a.write_site:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(output)
    elif a.check_site:
        require(OUTPUT.read_bytes() == output, "published JSON differs from source")
    else:
        print(output.decode(), end="")


if __name__ == "__main__":
    main()
