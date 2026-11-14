#!/usr/bin/env python3
"""Link R60 bibliography and R61 holdings to an inactive scientific contract.

A library holdings page is not a satellite observation or proof that an
article cited in 1969 appears in the catalogued 1963 fascicle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R60 = "research/tle_custody/polish_nafa_soviet_refs_C241_LONTRA_R60.json"
R61 = "research/tle_custody/ukraine_bulletin32_holdings_C241_LONTRA_R61.json"
SHA60 = "03c1c49e0a9c1ed28bd5afb21902563f635a9fd066db8dfa47033d5fca837b02"
SHA61 = "d0a981fe6aae55d4d222f2848e309c895ea7c87a86836b0efc13948141f84643"
OUTPUT = ROOT / "public/data/conde-bulletin32-genealogy-bridge.json"


def require(condition, message):
    if not condition:
        raise ValueError("Bulletin 32 scientific bridge: " + message)


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate source JSON key: " + key)
        result[key] = value
    return result


def load_source(root, name, sha256):
    raw = (root / name).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == sha256, "source SHA-256 drift: " + name)
    return json.loads(raw, object_pairs_hook=reject_duplicate_keys)


def load(root=ROOT):
    return load_source(root, R60, SHA60), load_source(root, R61, SHA61)


def edge(source, target, relation):
    return {"source": source, "target": target, "relation": relation,
            "documentary_only": True, "activation": False}


def build(r60, r61):
    require(r60.get("id") == "C241-LONTRA-R60", "R60 identity")
    require(r60.get("evidence_class") == "VERIFIED_1969_TECHNICAL_BIBLIOGRAPHY_AND_1963_PRIMARY_LOCATOR", "R60 class")
    require(r61.get("id") == "C241-LONTRA-R61", "R61 identity")
    require(r61.get("evidence_class") == "INSTITUTIONAL_SERIAL_HOLDINGS_NOT_PRIMARY_FACSIMILE", "R61 class")
    require("C241-LONTRA-R60" in r61.get("upstream", []), "R61 provenance relationship")
    source = r60.get("source", {})
    catalog = r61.get("catalog", {})
    cross = r61.get("cross_catalog", {})
    target = r61.get("target", {})
    b60, b61 = r60.get("boundaries", {}), r61.get("boundaries", {})
    ref13 = next((r for r in r60.get("source_references", [])
                  if r.get("reference") == 13), None)
    require(source.get("year") == 1969 and source.get("sha256") ==
            "f83992fecb15d01fbba0a9e8e3b94bdc81d6620f89ed4790dc4c5ee940bed0c4",
            "1969 source year / PDF identity")
    require(source.get("printed_pages") == "61-71" and
            source.get("pdf_page_indices_zero_based_verified_visually") == [62, 72],
            "1969 source pagination")
    require(ref13 is not None and ref13.get("bulletin_issue") == 32 and
            ref13.get("year") == 1963 and
            ref13.get("authors") == ["L. I. Medvedeva", "B. A. Firago"] and
            ref13.get("status") == "CITED_NOT_RETRIEVED", "reference 13 is only a locator")
    require(catalog.get("1963_holding") == "N32-37" and
            catalog.get("html_sha256") ==
            "5ec7eeef7492fb0c4d135f6d5ae5f0378c7290fffd86d49d633da4e1f53e0480",
            "Kyiv catalog identity")
    require(cross.get("japan_nii_ncid") == "AA00566856" and
            cross.get("verified_issue_32_held") is True, "Japan secondary holdings")
    require(target.get("soviet_bulletin_issue") == 32 and
            target.get("soviet_bulletin_year") == 1963 and
            target.get("link_to_target_article_status") ==
            "BIBLIOGRAPHIC_CITATION_ONLY_NOT_IN_HOLDINGS_TEXT" and
            target.get("primary_article_pages_known") is False,
            "holdings do not establish article text or pagination")
    for key in ("original_1963_bulletin_32_retrieved", "original_1963_azh_article_retrieved"):
        require(b60.get(key) is False, "R60 primary source not retrieved: " + key)
    for key in ("issue_32_facsimile_retrieved", "original_article_retrieved",
                "original_page_read", "station_identified_for_527_529"):
        require(b61.get(key) is False, "R61 unverified original/station: " + key)
    require(b60.get("observations_norad_527_528_529") == [] and
            b61.get("independent_observations_norad_527_528_529") == [] and
            b60.get("new_orbital_constraints") == 0 and
            b61.get("new_orbital_constraints") == 0,
            "bibliography/holdings are not tracking data")

    relations = [
        ("SOURCE:OSZCZAK-1969-PDF", "DOC:C241-LONTRA-R60", "CUSTODIED_1969_BIBLIOGRAPHY"),
        ("DOC:C241-LONTRA-R60", "REF:OSZCZAK-1969-13", "PRINTS_REFERENCE_13"),
        ("REF:OSZCZAK-1969-13", "WORK:SOVIET-BULLETIN-32-1963", "CITES_UNRETRIEVED_1963_WORK"),
        ("CATALOG:KYIV-2026-HTML", "DOC:C241-LONTRA-R61", "CUSTODIED_INSTITUTIONAL_HOLDINGS"),
        ("CATALOG:NII-AA00566856", "DOC:C241-LONTRA-R61", "CROSS_CATALOG_HOLDINGS_ONLY"),
        ("DOC:C241-LONTRA-R61", "HOLDING:SOVIET-BULLETIN-32", "LISTS_FASCICLE_NOT_ARTICLE"),
        ("HOLDING:SOVIET-BULLETIN-32", "H:ARTICLE_IDENTITY_UNVERIFIED", "NO_ARTICLE_LEVEL_INVENTORY"),
        ("WORK:SOVIET-BULLETIN-32-1963", "H:ARTICLE_IDENTITY_UNVERIFIED", "ORIGINAL_NOT_RETRIEVED"),
        ("H:ARTICLE_IDENTITY_UNVERIFIED", "LATENT:BULLETIN32:original_pages", "REQUIRES_PRIMARY_FACSIMILE"),
        ("WORK:SOVIET-BULLETIN-32-1963", "H:OPTICAL_METHOD_MAY_BE_RELEVANT", "BIBLIOGRAPHIC_METHOD_ONLY"),
        ("H:OPTICAL_METHOD_MAY_BE_RELEVANT", "LATENT:BULLETIN32:norad_identity", "TARGET_ID_NOT_PRINTED"),
        ("H:OPTICAL_METHOD_MAY_BE_RELEVANT", "LATENT:BULLETIN32:station_utc_frame", "NO_INSTRUMENTAL_RECORD"),
        ("LATENT:BULLETIN32:station_utc_frame", "LEAN:candidateBulletin32OpticalTiming", "PREMISES_NOT_ESTABLISHED"),
        ("LATENT:BULLETIN32:norad_identity", "LEAN:candidateBulletin32OpticalTiming", "TARGET_MAPPING_MISSING"),
        ("LEAN:candidateBulletin32OpticalTiming", "PARAM:optical_timing_offset_528", "CANDIDATE_ONLY"),
        ("LEAN:candidateBulletin32OpticalTiming", "PARAM:optical_range_sigma_528", "CANDIDATE_ONLY"),
    ]
    graph = [edge(*item) for item in relations]
    return {
        "schema": "conde-documentary-to-science-v1",
        "id": "C241-ABELHA-R57-BULLETIN32",
        "sources": [
            {"id": r60["id"], "path": R60, "manifest_sha256": SHA60,
             "pdf_sha256": source["sha256"], "evidence_class": r60["evidence_class"],
             "year": 1969, "printed_pages": source["printed_pages"]},
            {"id": r61["id"], "path": R61, "manifest_sha256": SHA61,
             "html_sha256": catalog["html_sha256"], "evidence_class": r61["evidence_class"],
             "year": 2026, "issue_held": 32},
        ],
        "occurrence_ids": ["C241-LONTRA-R60", "C241-LONTRA-R61"],
        "work_id": "SOVIET-BULLETIN-32-1963",
        "not_a_new_matrix_occurrence": True,
        "source_family": "SOVIET_BULLETIN_32_BIBLIOGRAPHIC_LOCATOR",
        "independent_observations_from_these_sources": 0,
        "independence_of_underlying_1963_observations": None,
        "graph": graph,
        "delta_links": len(graph),
        "delta_orbital_constraints": 0,
        "lean_candidate": {
            "id": "candidateBulletin32OpticalTiming", "status": "NOT_PROMOTED",
            "compiled_theorem_claimed": False,
            "missing_premises": ["original_fascicle_scan", "article_page_identity",
                                 "norad_target_identity", "instrument_station",
                                 "utc_or_calibrated_clock", "reference_frame",
                                 "measurement_uncertainty_and_dependencies"],
        },
        "simulator_parameters": [
            {"id": "optical_timing_offset_528", "value": None, "activation": False},
            {"id": "optical_range_sigma_528", "value": None, "activation": False},
        ],
        "physical_domain_effect": "THETA_UNCHANGED",
        "limitations": [
            "R60 is a 1969 secondary citation; it does not supply a 1963 observation.",
            "R61 is a 2026 institutional holdings HTML; it does not inventory the referenced article.",
            "Kyiv and Japanese holdings are not two independent satellite measurements.",
            "No instrument, NORAD 528 measurement, UTC calibration, frame, or covariance is supplied.",
        ],
    }


def render(root=ROOT):
    data = build(*load(root))
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def validate(payload, root=ROOT):
    require(payload == build(*load(root)), "scientific bridge output mutated or stale")
    edges = payload["graph"]
    require(len({(e["source"], e["target"], e["relation"]) for e in edges}) == len(edges),
            "duplicate edges")
    require(all(e["documentary_only"] is True and e["activation"] is False
                for e in edges), "activated evidence edges")
    require(payload["delta_orbital_constraints"] == 0 and
            payload["physical_domain_effect"] == "THETA_UNCHANGED", "physical activation")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-site", action="store_true")
    parser.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    raw = render()
    if args.write_site:
        OUTPUT.write_bytes(raw)
    if args.check_site:
        require(OUTPUT.read_bytes() == raw, "published bytes differ")
    validate(json.loads(raw))
    print("Bulletin 32 documentary bridge PASS; physical constraints 0; links 16")


if __name__ == "__main__":
    main()
