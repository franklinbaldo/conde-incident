#!/usr/bin/env python3
"""C241-L36: audit printed UN Jan31 versus NASA Apr30 values; no physical rate."""
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
try:
    from tools.tle_un_1963_registration_audit import validate as validate_un_1963
    from tools.tle_nasa_ssr_apr_oct_audit import validate as validate_nasa_apr
except ModuleNotFoundError:  # Direct execution: python3 tools/tle_un_nasa_crosscutoff_audit.py
    from tle_un_1963_registration_audit import validate as validate_un_1963
    from tle_nasa_ssr_apr_oct_audit import validate as validate_nasa_apr

ROOT = Path(__file__).resolve().parents[1]
MODEL = "research/tle_custody/un_nasa_crosscutoff_print_deltas_C241-L36.json"
UN = "research/tle_custody/un_1963_registration_C241-L33.json"
NASA = "research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json"
IDENTITY = "research/tle_custody/nasa_ssr_dec1977_528_identity_C241-L32.json"
NASA_1963_LINEAGE = "research/tle_custody/nasa_ssr_1963_incremental_lineage_C241-L11.json"
NASA_OCTOBER = "research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json"
FIELDS = (
    ("nodal_period_min", "nodal_period_min_printed", "nodal_period_min"),
    ("inclination_deg", "inclination_deg_printed", "inclination_deg"),
    ("apogee_km", "apogee_km_printed", "apogee_km"),
    ("perigee_km", "perigee_km_printed", "perigee_km"),
)
EXPECTED = (
    ("1963-003A", 527),
    ("1963-003B", 528),
    ("1963-003C", 529),
)

def require(ok, why):
    if not ok:
        raise ValueError(why)

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def validate(m, un, nasa, identity):
    # Arithmetic agreement alone is not document custody: changing both a
    # ledger cell and its published delta would otherwise pass unchanged PDF
    # hashes. Reuse the independently source-pinned L33 and L16 validators,
    # rather than maintaining another table of 12+12 printed cells here.
    validate_un_1963(un, identity, load(NASA_1963_LINEAGE))
    validate_nasa_apr(nasa, load(NASA_OCTOBER))
    require(m["schema"] == "conde.c241-l36-un-nasa-editorial-crosscutoff/v1"
            and m["id"] == "C241-L36"
            and m["epistemic_status"] == "DOCUMENTARY_PRINTED_DIFFERENCES_NO_PHYSICAL_RATE",
            "schema/status")
    s0, s1 = m["source_earlier"], m["source_later"]
    un0, nasa0 = un["docs"][0], nasa["april"]
    require(s0["ledger"] == UN and s1["ledger"] == NASA
            and m["identity_bridge"] == IDENTITY, "source paths")
    require(un0["number"] == "30"
            and un0["kind"] == "JAN31_FULL_NEW_REGISTRATION"
            and s0["document_id"] == "UN A/AC.105/INF.30"
            and s0["url"] == un0["url"]
            and s0["sha256"] == un0["sha256"]
            and s0["pdf_page_index_zero_based"] == un0["relevant_pdf_page_index"] == 1
            and s0["cutoff_printed"] == un0["report_cutoff_printed"]
            == "2400Z 31 JANUARY 1963"
            and s0["published_day"] == un0["document_day"] == "1963-03-13"
            and s0["source_role"] == "US_TO_UN_REGISTER_AS_OF_CUTOFF_NOT_SENSOR",
            "UN source hash, page or date differs")
    require(nasa0["ntrs"] == "19630012128"
            and s1["document_id"] == "NASA NTRS 19630012128"
            and s1["url"] == nasa0["url"]
            and s1["sha256"] == nasa0["sha256"]
            and s1["pdf_page_index_zero_based"] == nasa0["pdf_page_index_zero_based"] == 6
            and s1["cutoff_printed"] == nasa0["data_as_of"] == "1430Z APR 30 1963"
            and s1["published_day"] == nasa0["publication"] == "1963-04-30"
            and s1["source_role"] == "NASA_SSR_COMPILED_CATALOG_NOT_SENSOR",
            "NASA source hash, page or date differs")
    require(identity["row"]["international_designator_printed"] == "1963 003B"
            and identity["row"]["catalog_number_printed"] == 528
            and identity["row"]["identity_match"] == "DIRECT_VISUAL_VERIFIED"
            and [(x["international_designator_printed"], x["catalog_number_printed"])
                 for x in identity["control_rows"]]
            == [("1963 003A",527), ("1963 003C",529)],
            "NASA 1977 original crosswalk changed")
    require(m["comparison_rule"] ==
            "Decimal(later NASA printed value) - Decimal(earlier UN printed value); nominal arithmetic only",
            "comparison operator")
    require(m["quantities"] == [field for field, _, _ in FIELDS],
            "quantity or unit changed")
    rows = m["objects"]
    require(len(rows) == len(EXPECTED)
            and len(un0["printed_rows"]) == len(EXPECTED)
            and len(nasa["april_rows"]) == len(EXPECTED), "missing object rows")
    report = []
    for i, (designator, norad) in enumerate(EXPECTED):
        u, n, out = un0["printed_rows"][i], nasa["april_rows"][i], rows[i]
        require(u["printed_designator"] == f"1963-3-{designator[-1]}"
                and u["norad_from_nasa_1977"] == norad
                and n["designator"] == designator
                and out["designator"] == designator and out["norad"] == norad,
                f"identity order mismatch for {norad}")
        require(set(out["nominal_deltas"]) == {field for field, _, _ in FIELDS},
                f"expected four fields for {norad}")
        differences = {}
        for field, uk, nk in FIELDS:
            try:
                old, new = Decimal(u[uk]), Decimal(str(n[nk]))
            except (InvalidOperation, TypeError):
                raise ValueError(f"invalid printed number {norad}/{field}")
            observed = str(new-old)
            require(out["nominal_deltas"][field] == observed,
                    f"printed delta changed {norad}/{field}: {observed}")
            differences[field] = observed
        report.append({"norad": norad, "designator": designator,
                       "published_print_differences": differences})
    require(set(m["unknowns"]) ==
            {"observation_epochs_for_each_printed_cell_utc",
             "sensor_station_for_each_cell", "tracking_arc_and_state_fit_method",
             "measurement_covariance", "cross_publication_error_covariance",
             "reporting_latency_model", "common_upstream_lineage_fully_resolved"}
            and all(x is None for x in m["unknowns"].values()),
            "invented observation, sigma or causal lineage")
    ind = m["independence"]
    require(ind["same_us_source_family_possible"] is True
            and ind["new_independent_tracking_sensor_evidences"] == 0
            and all(ind[k] is False for k in
                    ("un_to_nasa_publications_count_as_two_independent_observations",
                     "nominal_change_is_derivative",
                     "nominal_change_is_physical_bound",
                     "nominal_change_is_calibrated_uncertainty")),
            "published cells wrongly elevated to independent physical measurements")
    g = m["graph"]
    require(g["parent"] == "research/constraints/ssr_1963_observable_graph.json"
            and g["dependencies"] == [UN, NASA, IDENTITY]
            and g["printed_pair_connections"] == len(EXPECTED)*len(FIELDS) == 12
            and g["documentation_only"] is True
            and g["physical_constraints_activated"] == 0
            and g["lean_promoted"] is False
            and g["simulation_parameters_changed"] is False
            and g["inferred_terminal_time_or_place"] is False,
            "graph mistakenly activates constraint")
    return {
        "record_id": m["id"],
        "compared_editorial_rows": 3,
        "new_documentary_links": 12,
        "nominal_print_deltas": report,
        "source_family": "US_NASA_NORAD_POSSIBLY_SHARED_NOT_INDEPENDENT_SENSORS",
        "observed_times_per_cell": None,
        "inferred_rates": None,
        "added_instrumental_observations": 0,
        "active_physical_constraints": 0,
        "conclusion": "DOCUMENTARY_PRINT_CHANGE_ONLY",
    }

def check_original_pdfs(m, directory):
    for source, name in ((m["source_earlier"], "inf030E.pdf"),
                         (m["source_later"], "19630012128.pdf")):
        raw = (Path(directory) / name).read_bytes()
        require(raw.startswith(b"%PDF-"), f"not a PDF: {name}")
        require(hashlib.sha256(raw).hexdigest() == source["sha256"],
                f"original PDF bytes changed: {name}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf-dir")
    parser.add_argument("--output")
    args = parser.parse_args()
    m = load(MODEL)
    result = validate(m, load(UN), load(NASA), load(IDENTITY))
    if args.pdf_dir:
        check_original_pdfs(m, args.pdf_dir)
        result["archival_pdf_bytes_verified"] = 2
    report = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    print(report, end="")

if __name__ == "__main__":
    main()
