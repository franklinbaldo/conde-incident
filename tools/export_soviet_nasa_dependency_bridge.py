#!/usr/bin/env python3
"""Documentary numerical crosswalk R49 -> candidate observables, never a new 528 sensor."""
import argparse
import hashlib
import json
from pathlib import Path
if __package__:
    from .audit_soviet_nasa_crosswalk_r49 import audit
else:
    from audit_soviet_nasa_crosswalk_r49 import audit

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "C241-LONTRA-R49": ("research/tle_custody/soviet_nasa_crosswalk_C241_LONTRA_R49.json", "17f9095ae14630cc881c6ace9f9709a4e41a41bdeca3a6e5ed3ff806493dfca3"),
    "C241-LONTRA-R48": ("research/tle_custody/soviet_bse1964_1963_003_C241_LONTRA_R48.json", "1901a3cc28c12a50507791c64eb940ce999c579f20984cd42485fde4cdf4a4f3"),
    "C241-L18": ("research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json", "6cc3b54429deca2e43ccb7ddc7f2ae6ebaa80955b4f142c258cbb6e7ac82a435"),
}
OUT = ROOT / "public/data/conde-soviet-nasa-dependency-bridge.json"


def need(ok, message):
    if not ok:
        raise ValueError("R49 scientific link: " + message)


def no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def load(root=ROOT):
    data, hashes = {}, {}
    for identifier, (filename, pin) in SOURCES.items():
        raw = (root / filename).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == pin, "source hash drift " + identifier)
        data[identifier] = json.loads(raw, object_pairs_hook=no_duplicate_keys)
        hashes[identifier] = digest
    return data, hashes


def build(data, hashes):
    cross, sov, nasa = [data[x] for x in SOURCES]
    need(audit(cross, sov, nasa) == "PAIR_MATCH_BUT_PROVENANCE_UNRESOLVED", "upstream audit")
    need(cross["interpretation"]["relation"] == "PRINT_NUMERIC_PAIR_MATCH_SOURCE_DEPENDENCE_UNRESOLVED", "relation")
    need(cross["sources"]["soviet"]["printed_object"] == "Секретный", "anonymous row")
    need(cross["sources"]["nasa"]["row_designator"] == "1963-003A", "NASA target is A, not B")
    need(sov["printed_table_row"]["rocket_printed"] == "Тор — Аджена D", "launch vehicle text")
    need(sov["document_custody"]["pdf_sha256"] == "d2372fe5b073c95366681bf550a0688ee47a6d2b6c4c612125e006a79fcdc613", "Soviet PDF custody")
    nasa_row = [s for s in nasa["sources"] if s["ntrs_id"] == "19640002493"]
    need(len(nasa_row) == 1 and nasa_row[0]["sha256"] == "9f2b6973117bb709bd26893a90e42b170e58f245c0fa11370ab26cfda3b0d94d", "NASA PDF custody")
    need(cross["interpretation"]["independent_soviet_sensor_or_time_utc_proven"] is False, "sensor status")
    need(cross["interpretation"]["same_1963_003A_identity_confirmed_by_soviet_table"] is False, "identity status")
    need(cross["interpretation"]["new_physical_constraints_activated"] == 0, "constraints")
    need(sov["target"]["measured_NORAD_527_528_529_in_retrieved_document"] is False, "target misidentified")

    def edge(a, b, label):
        return {"source": a, "target": b, "relation": label,
                "new_instrumental_observation": False, "activation": False}

    edges = [
        edge("C241-LONTRA-R48", "DOC:BSE1964:p503:r3", "PRINT_ROW_CUSTODIED_NOT_RAW_OBSERVATION"),
        edge("C241-L18", "DOC:NASA1963:19640002493:p5:A", "SSR_COMPILATION_NOT_RAW_OBSERVATION"),
        edge("C241-LONTRA-R49", "DOC:BSE1964:p503:r3", "CROSSWALK_INPUT"),
        edge("C241-LONTRA-R49", "DOC:NASA1963:19640002493:p5:A", "CROSSWALK_INPUT"),
        edge("DOC:BSE1964:p503:r3", "DATUM:PRINTED_ALTITUDE_PAIR", "459_533_KM_PRINTED"),
        edge("DOC:NASA1963:19640002493:p5:A", "DATUM:PRINTED_ALTITUDE_PAIR", "459_533_KM_PRINTED"),
        edge("DATUM:PRINTED_ALTITUDE_PAIR", "H:COMMON_UPSTREAM", "POSSIBLE_SHARED_SOURCE_NOT_PROVEN"),
        edge("DATUM:PRINTED_ALTITUDE_PAIR", "H:INDEPENDENT_SOVIET_SENSOR", "NO_INSTRUMENTAL_EVIDENCE"),
        edge("DATUM:PRINTED_ALTITUDE_PAIR", "H:ROW_IS_1963_003A", "NUMERIC_SIMILARITY_NOT_IDENTIFIER"),
        edge("H:COMMON_UPSTREAM", "LATENT:source_lineage", "WESTERN_PERIODICALS_UNTRACED"),
        edge("H:INDEPENDENT_SOVIET_SENSOR", "LATENT:instrumental_independence", "UNKNOWN_NOT_ZERO"),
        edge("H:ROW_IS_1963_003A", "LATENT:soviet_row_identity", "ROW_HAS_NO_NORAD_COSPAR"),
        edge("H:ROW_IS_1963_003A", "MODEL:orbital_element_comparison", "CONDITIONAL_IDENTITY_AND_EPOCH"),
        edge("MODEL:orbital_element_comparison", "LEAN:candidatePrintedElementConsistency", "PREMISES_MISSING_NOT_COMPILED"),
    ]
    latents = [{"id": k, "unit": unit, "value": None, "activation": False}
               for k, unit in (
                   ("LATENT:source_lineage", "upstream_document_id"),
                   ("LATENT:instrumental_independence", "instrument_family_id"),
                   ("LATENT:soviet_row_identity", "NORAD_or_COSPAR_id"),
                   ("LATENT:sensor", "instrument_id"),
                   ("LATENT:observation_epoch", "UTC"),
                   ("LATENT:reference_frame", "frame_identifier"),
                   ("LATENT:instrument_sigma", "angular_or_element_uncertainty"),
                   ("LATENT:time_calibration", "seconds"))]
    return {
        "schema": "conde.soviet-nasa-documentary-dependency/v1",
        "id": "ABELHA-C241-LONTRA-R49-01",
        "sources": [{"occurrence_id": k, "path": SOURCES[k][0], "ledger_sha256": hashes[k]}
                    for k in SOURCES],
        "source_custody": {"soviet_scan_url": sov["work"]["section_pdf"],
                           "soviet_pdf_sha256": sov["document_custody"]["pdf_sha256"],
                           "soviet_print_page": 503,
                           "nasa_pdf_url": nasa_row[0]["pdf_url"],
                           "nasa_pdf_sha256": nasa_row[0]["sha256"],
                           "nasa_print_page": 5},
        "source_classes": {"soviet": "CONTEMPORARY_PRINT_RETROSPECTIVE",
                           "nasa": "NASA_SSR_COMPILED_ELEMENTS"},
        "printed_orbital_comparison": cross["comparison"],
        "publication_years": {"soviet": 1964, "nasa": 1963},
        "instrumental_observation_epoch_utc": None,
        "soviet_row_explicit_norad_id": None,
        "nasa_print_row": "1963-003A",
        "other_target_candidates": [
            {"norad_id": k, "row_identified_as_target": False,
             "new_orbital_measurement": None, "activation": False}
            for k in (527, 528, 529)],
        "graph": edges,
        "hypotheses": ["H:COMMON_UPSTREAM", "H:INDEPENDENT_SOVIET_SENSOR", "H:ROW_IS_1963_003A"],
        "model_observable": {"name": "orbital_element_comparison", "status": "CONDITIONAL_NOT_EVALUABLE",
                             "required": ["identified_object", "measurement_epoch_utc",
                                          "reference_frame", "instrumental_covariance", "upstream_genealogy"]},
        "lean_candidate": "candidatePrintedElementConsistency",
        "lean_status": "CANDIDATE_ONLY_NO_COMPILED_EMPIRICAL_PROOF",
        "latents": latents,
        "independent_instrumental_families": None,
        "new_confirmed_norad_528_observations": 0,
        "new_activated_physical_constraints": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Retrieve cited Western periodical 1963 tables and row-level upstream; demand historical object identity, UTC, measurement basis, frame and uncertainty before any 527/528/529 orbital constraint.",
    }


def render(root=ROOT):
    data, hashes = load(root)
    return (json.dumps(build(data, hashes), indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write-site", action="store_true")
    mode.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.write_site:
        OUT.write_bytes(content)
    elif args.check_site:
        need(content == OUT.read_bytes(), "published output drift")
    else:
        print(content.decode(), end="")


if __name__ == "__main__":
    main()
